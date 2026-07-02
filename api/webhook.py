"""
ADHDclearfocus — Stripe Webhook Handler (AI-Powered)
Flow: Stripe payment confirmed → Claude AI analyses results →
      generate_report.py builds personalised PDF → SendGrid delivers to customer
"""

import json
import os
import base64
import http.client
import hashlib
from http.server import BaseHTTPRequestHandler

import sys
sys.path.append(os.path.dirname(__file__))
from generate_report import build_report

SENDGRID_API_KEY  = os.environ.get("SENDGRID_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
FROM_EMAIL        = "hello@adhdclearfocus.com"
FROM_NAME         = "ADHDclearfocus"
ADMIN_EMAIL       = os.environ.get("ADMIN_EMAIL", "conalldonegan@outlook.com")

DOMAIN_LABELS = {
    "inattention":    "Attention Regulation",
    "hyperactivity":  "Hyperactivity & Impulse Control",
    "executive":      "Executive Function",
    "emotional":      "Emotional Regulation",
    "working_memory": "Working Memory",
    "time":           "Time Perception",
    "hyperfocus":     "Hyperfocus & Interest Drive",
    "rsd":            "Rejection Sensitivity (RSD)",
    "developmental":  "Developmental History",
    "impact":         "Life Impact",
}

def generate_loyalty_code(email):
    prefix = email.split("@")[0].upper().replace(".", "").replace("_", "")[:6]
    hash_suffix = hashlib.md5(email.lower().encode()).hexdigest()[:4].upper()
    return f"ACF-{prefix}-{hash_suffix}"

def get_ai_analysis(pcts, level, asrs_flag, asrs_count, age_group, total_pct):
    if not ANTHROPIC_API_KEY:
        return None
    domain_summary = "\n".join([
        f"- {DOMAIN_LABELS.get(k,k)}: {v}% ({'Elevated' if v>=65 else 'Moderate' if v>=40 else 'Low'})"
        for k,v in sorted(pcts.items(), key=lambda x: -x[1])
    ])
    prompt = f"""You are an expert ADHD clinical psychologist writing personalised report content for a client.

CLIENT PROFILE:
- Age group: {age_group}
- Overall level: {level} ({total_pct}%)
- WHO ASRS-v1.1: {'Positive' if asrs_flag else 'Below threshold'} ({asrs_count}/6)
- Domain scores (sorted highest to lowest):
{domain_summary}

Write personalised, warm, non-pathologising clinical narrative specific to THIS profile.
Focus on their specific pattern — not generic ADHD text.

Return ONLY valid JSON (no markdown fences):
{{
  "overall_narrative": "3-4 sentences describing this person's unique neurological pattern. Reference their specific highest and lowest domains.",
  "top_insight": "1-2 sentences on the single most clinically significant finding.",
  "domain_narratives": {{
    "inattention": "2 sentences specific to their {pcts.get('inattention',0)}% score",
    "hyperactivity": "2 sentences specific to their {pcts.get('hyperactivity',0)}% score",
    "executive": "2 sentences specific to their {pcts.get('executive',0)}% score",
    "emotional": "2 sentences specific to their {pcts.get('emotional',0)}% score",
    "working_memory": "2 sentences specific to their {pcts.get('working_memory',0)}% score",
    "time": "2 sentences specific to their {pcts.get('time',0)}% score",
    "hyperfocus": "2 sentences specific to their {pcts.get('hyperfocus',0)}% score",
    "rsd": "2 sentences specific to their {pcts.get('rsd',0)}% score",
    "developmental": "2 sentences specific to their {pcts.get('developmental',0)}% score",
    "impact": "2 sentences specific to their {pcts.get('impact',0)}% score"
  }},
  "priority_actions": [
    "Most important concrete action for this specific profile",
    "Second most important action",
    "Third most important action"
  ]
}}"""
    try:
        conn = http.client.HTTPSConnection("api.anthropic.com")
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        })
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        }
        conn.request("POST", "/v1/messages", payload, headers)
        resp = conn.getresponse()
        data = json.loads(resp.read())
        text = data.get("content", [{}])[0].get("text", "{}")
        text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI analysis error: {e}")
        return None

def send_report_email(to_email, pdf_bytes, level, total_pct, pcts, ai_analysis, loyalty_code, age_group):
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    subject = f"Your ADHDclearfocus Report — {level} Profile ({total_pct}%)"

    domain_rows = ""
    for key, label in DOMAIN_LABELS.items():
        pct = pcts.get(key, 0)
        color = "#FFB347" if pct >= 65 else "#00D4DD" if pct >= 40 else "#00E676"
        bar_px = int(pct * 1.8)
        domain_rows += f'<tr><td style="padding:5px 0;font-size:12px;color:#7B93B4;width:160px;">{label}</td><td style="padding:5px 8px;"><div style="background:#1A2E4A;border-radius:4px;height:8px;width:180px;overflow:hidden;"><div style="background:{color};width:{bar_px}px;height:100%;border-radius:4px;"></div></div></td><td style="padding:5px 0;font-size:12px;font-weight:700;color:{color};">{pct}%</td></tr>'

    ai_section = ""
    if ai_analysis:
        overall = ai_analysis.get("overall_narrative","")
        top = ai_analysis.get("top_insight","")
        actions = ai_analysis.get("priority_actions",[])
        acts_html = "".join([f'<li style="margin-bottom:6px;color:#A8C4D8;font-size:13px;">{a}</li>' for a in actions])
        ai_section = f'<div style="background:#0F2040;border:1px solid #00D4DD30;border-radius:10px;padding:16px;margin:16px 0;"><div style="font-size:11px;color:#00D4DD;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Your Profile Insight</div><p style="font-size:13px;color:#E0EAF4;line-height:1.65;margin:0 0 8px;">{overall}</p>{f"""<p style="font-size:13px;color:#FFB347;font-weight:600;margin:0 0 8px;"><strong>Key finding:</strong> {top}</p>""" if top else ""}{f"""<div><div style="font-size:11px;color:#7B93B4;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Your Priority Actions</div><ul style="margin:0;padding-left:18px;">{acts_html}</ul></div>""" if actions else ""}</div>'

    html = f"""<div style="background:#0A1628;padding:0;margin:0;font-family:Arial,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:32px 24px;">
<div style="margin-bottom:20px;"><span style="font-size:22px;font-weight:900;color:#fff;">ADHD<span style="color:#00D4DD;">clearfocus</span></span></div>
<div style="background:#112240;border:2px solid #FFB34750;border-radius:14px;padding:20px;margin-bottom:20px;text-align:center;">
<div style="display:inline-block;background:#FFB34720;border:1px solid #FFB347;border-radius:20px;padding:4px 16px;font-size:11px;font-weight:700;color:#FFB347;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">{level} Profile · {total_pct}%</div>
<h1 style="font-size:20px;font-weight:900;color:#fff;margin:0 0 8px;">Your report is attached</h1>
<p style="color:#7B93B4;font-size:13px;line-height:1.6;margin:0;">Your personalised 14-page ADHDclearfocus report covering all 10 neurological dimensions is attached. Open it to see your complete profile, evidence-based strategies, and next steps.</p>
</div>
{ai_section}
<div style="background:#112240;border:1px solid #1E3A5F;border-radius:12px;padding:18px;margin-bottom:20px;">
<div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:14px;">Your 10-Dimension Profile</div>
<table style="width:100%;border-collapse:collapse;">{domain_rows}</table>
<div style="font-size:10px;color:#7B93B4;margin-top:10px;">Amber (65%+) = Clinically significant · Teal (40-64%) = Moderate · Green (&lt;40%) = Lower priority</div>
</div>
<div style="background:linear-gradient(135deg,#0A2010,#0A1628);border:1px solid #00E67650;border-radius:12px;padding:18px;margin-bottom:20px;text-align:center;">
<div style="font-size:11px;color:#00E676;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Your Lifetime Discount Code</div>
<div style="font-size:24px;font-weight:900;color:#00E676;letter-spacing:5px;font-family:monospace;margin:8px 0;">{loyalty_code}</div>
<p style="font-size:12px;color:#7B93B4;line-height:1.6;margin:0;">When ADHDclearfocus Pro launches, use this code to lock in your <strong style="color:#fff;">€5/month for life</strong> rate (regular price €10/month). Tied to your email. If you cancel and rejoin without it, rate rises to €10/month.</p>
</div>
<div style="border-top:1px solid #1E3A5F;padding-top:16px;margin-top:16px;">
<p style="font-size:10px;color:#7B93B4;line-height:1.6;margin:0;">This report is for educational and self-awareness purposes only. It does not constitute a clinical diagnosis. If in crisis contact Samaritans free on <strong style="color:#fff;">116 123</strong> (Ireland and UK, 24/7).</p>
<p style="font-size:10px;color:#7B93B4;margin:8px 0 0;">ADHDclearfocus · Focused Care Psychology Limited · Waterford, Ireland · <a href="https://adhdclearfocus.com" style="color:#00D4DD;">adhdclearfocus.com</a></p>
</div>
</div></div>"""

    payload = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "reply_to": {"email": ADMIN_EMAIL, "name": FROM_NAME},
        "content": [{"type": "text/html", "value": html}],
        "attachments": [{"content": pdf_b64, "type": "application/pdf",
            "filename": f"ADHDclearfocus_Report_{level}.pdf", "disposition": "attachment"}],
    }
    conn = http.client.HTTPSConnection("api.sendgrid.com")
    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    conn.request("POST", "/v3/mail/send", json.dumps(payload), headers)
    return conn.getresponse().status

def notify_admin(customer_email, level, total_pct, pcts, loyalty_code, ai_analysis):
    domain_text = "\n".join([f"  {DOMAIN_LABELS.get(k,k)}: {v}%" for k,v in pcts.items()])
    insight = ai_analysis.get("top_insight","N/A") if ai_analysis else "AI unavailable"
    html = f"<div style='font-family:Arial;padding:20px;'><h2>New Purchase</h2><p><b>Customer:</b> {customer_email}</p><p><b>Profile:</b> {level} ({total_pct}%)</p><p><b>Code:</b> {loyalty_code}</p><p><b>AI insight:</b> {insight}</p><pre>{domain_text}</pre></div>"
    payload = {
        "personalizations": [{"to": [{"email": ADMIN_EMAIL}],
            "subject": f"New Report Purchase — {customer_email} ({level})"}],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "content": [{"type": "text/html", "value": html}],
    }
    conn = http.client.HTTPSConnection("api.sendgrid.com")
    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    conn.request("POST", "/v3/mail/send", json.dumps(payload), headers)
    conn.getresponse()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            event_type = data.get("type", "")

            if event_type == "checkout.session.completed":
                session = data.get("data", {}).get("object", {})
                customer_email = session.get("customer_details", {}).get("email", "")
                metadata = session.get("metadata", {})
                level      = metadata.get("level", "Elevated")
                total_pct  = int(metadata.get("total_pct", 0))
                asrs_flag  = metadata.get("asrs_flag", "false") == "true"
                asrs_count = int(metadata.get("asrs_count", 0))
                age_group  = metadata.get("age_group", "Adult")
                pcts = {k: int(metadata.get(f"pct_{k}", 0)) for k in
                    ["inattention","hyperactivity","executive","emotional",
                     "working_memory","time","hyperfocus","rsd","developmental","impact"]}
                loyalty_code = generate_loyalty_code(customer_email)
                ai_analysis = get_ai_analysis(pcts, level, asrs_flag, asrs_count, age_group, total_pct)
                pdf_buf = build_report(
                    name="Your ADHDclearfocus Profile",
                    age_group=age_group, level=level, total_pct=total_pct,
                    asrs_flag=asrs_flag, asrs_count=asrs_count, pcts=pcts,
                    ai_analysis=ai_analysis, loyalty_code=loyalty_code,
                )
                pdf_bytes = pdf_buf.read()
                if customer_email:
                    send_report_email(customer_email, pdf_bytes, level, total_pct,
                        pcts, ai_analysis, loyalty_code, age_group)
                    notify_admin(customer_email, level, total_pct, pcts, loyalty_code, ai_analysis)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"received": True}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ADHDclearfocus webhook active"}).encode())
