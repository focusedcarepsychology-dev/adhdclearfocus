"""
ADHDclearfocus — Stripe Webhook Handler
Flow: verified Stripe payment → optional AI analysis → PDF generation →
verified transactional-email provider → customer delivery.

Resend is preferred when RESEND_API_KEY is present. SendGrid remains a fallback
only when both SENDGRID_API_KEY and an explicit verified sender are configured.
"""

import json
import hmac
import time
import os
import base64
import http.client
import hashlib
from http.server import BaseHTTPRequestHandler

import sys
sys.path.append(os.path.dirname(__file__))
from generate_report import build_report


def env(*names, default=""):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            v = os.environ.get(k)
            if v:
                return v
    return default


RESEND_API_KEY = env("RESEND_API_KEY")
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")
RESEND_FROM_EMAIL = env("RESEND_FROM_EMAIL", default="clearfocus@mail.focusedcarepsychology.ie")
SENDGRID_FROM_EMAIL = env("SENDGRID_FROM_EMAIL", "FROM_EMAIL")
FROM_NAME = "ADHDclearfocus"
ADMIN_EMAIL = env("ADMIN_EMAIL", default="focusedcarepsychology@gmail.com")

DOMAIN_LABELS = {
    "inattention": "Attention Regulation",
    "hyperactivity": "Hyperactivity & Impulse Control",
    "executive": "Executive Function",
    "emotional": "Emotional Regulation",
    "working_memory": "Working Memory",
    "time": "Time Perception",
    "hyperfocus": "Hyperfocus & Interest Drive",
    "rsd": "Rejection Sensitivity (RSD)",
    "developmental": "Developmental History",
    "impact": "Life Impact",
}


def delivery_provider():
    if RESEND_API_KEY:
        return "resend"
    if SENDGRID_API_KEY and SENDGRID_FROM_EMAIL:
        return "sendgrid"
    return ""


def generate_loyalty_code(email):
    prefix = email.split("@")[0].upper().replace(".", "").replace("_", "")[:6]
    hash_suffix = hashlib.md5(email.lower().encode()).hexdigest()[:4].upper()
    return f"ACF-{prefix}-{hash_suffix}"


def get_ai_analysis(pcts, level, asrs_flag, asrs_count, age_group, total_pct):
    if not ANTHROPIC_API_KEY:
        return None
    domain_summary = "\n".join([
        f"- {DOMAIN_LABELS.get(k, k)}: {v}% ({'Elevated' if v >= 65 else 'Moderate' if v >= 40 else 'Low'})"
        for k, v in sorted(pcts.items(), key=lambda x: -x[1])
    ])
    prompt = f"""Write warm, non-pathologising, evidence-informed educational narrative for a personalised ADHD self-reflection report.
This is not a diagnosis and must not imply that a clinician has assessed the person.

PROFILE:
- Age group: {age_group}
- Overall level: {level} ({total_pct}%)
- WHO ASRS-v1.1 screening items: {'positive screening pattern' if asrs_flag else 'below screening threshold'} ({asrs_count}/6)
- Domain scores:
{domain_summary}

Return ONLY valid JSON:
{{
  "overall_narrative": "3-4 sentences describing the pattern without diagnosing",
  "top_insight": "1-2 sentences on the most useful self-reflection finding",
  "domain_narratives": {{
    "inattention": "2 sentences",
    "hyperactivity": "2 sentences",
    "executive": "2 sentences",
    "emotional": "2 sentences",
    "working_memory": "2 sentences",
    "time": "2 sentences",
    "hyperfocus": "2 sentences",
    "rsd": "2 sentences",
    "developmental": "2 sentences",
    "impact": "2 sentences"
  }},
  "priority_actions": ["action 1", "action 2", "action 3"]
}}"""
    try:
        conn = http.client.HTTPSConnection("api.anthropic.com", timeout=25)
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        })
        conn.request("POST", "/v1/messages", payload, {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        })
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8", errors="replace")
        conn.close()
        if resp.status >= 400:
            raise RuntimeError(f"anthropic_{resp.status}:{raw[:160]}")
        data = json.loads(raw or "{}")
        text = data.get("content", [{}])[0].get("text", "{}")
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as exc:
        print(f"AI analysis error: {exc}")
        return None


def _send_resend(to_email, subject, html, attachments=None):
    payload = {
        "from": f"{FROM_NAME} <{RESEND_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
        "reply_to": ADMIN_EMAIL,
    }
    if attachments:
        payload["attachments"] = attachments
    conn = http.client.HTTPSConnection("api.resend.com", timeout=25)
    conn.request("POST", "/emails", json.dumps(payload), {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    })
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8", errors="replace")
    conn.close()
    if resp.status not in (200, 201, 202):
        raise RuntimeError(f"resend_email_{resp.status}:{raw[:180]}")
    return resp.status


def _send_sendgrid(to_email, subject, html, attachments=None):
    payload = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": SENDGRID_FROM_EMAIL, "name": FROM_NAME},
        "reply_to": {"email": ADMIN_EMAIL, "name": FROM_NAME},
        "content": [{"type": "text/html", "value": html}],
    }
    if attachments:
        payload["attachments"] = [
            {
                "content": item["content"],
                "type": item.get("content_type", "application/octet-stream"),
                "filename": item["filename"],
                "disposition": "attachment",
            }
            for item in attachments
        ]
    conn = http.client.HTTPSConnection("api.sendgrid.com", timeout=25)
    conn.request("POST", "/v3/mail/send", json.dumps(payload), {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    })
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8", errors="replace")
    conn.close()
    if resp.status not in (200, 201, 202):
        raise RuntimeError(f"sendgrid_email_{resp.status}:{raw[:180]}")
    return resp.status


def send_transactional_email(to_email, subject, html, attachments=None):
    provider = delivery_provider()
    if provider == "resend":
        return _send_resend(to_email, subject, html, attachments)
    if provider == "sendgrid":
        return _send_sendgrid(to_email, subject, html, attachments)
    raise RuntimeError("transactional_email_not_configured")


def _domain_rows_html(pcts):
    rows = []
    for key, label in DOMAIN_LABELS.items():
        pct = pcts.get(key, 0)
        descriptor = "higher" if pct >= 65 else "moderate" if pct >= 40 else "lower"
        rows.append(
            f'<tr><td style="padding:7px 8px;color:#516174;font-size:13px;">{label}</td>'
            f'<td style="padding:7px 8px;color:#122033;font-size:13px;font-weight:700;">{pct}% · {descriptor}</td></tr>'
        )
    return "".join(rows)


def send_report_email(to_email, pdf_bytes, level, total_pct, pcts, ai_analysis, loyalty_code, age_group):
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    insight = ""
    actions_html = ""
    if ai_analysis:
        narrative = ai_analysis.get("overall_narrative", "")
        top = ai_analysis.get("top_insight", "")
        if narrative or top:
            insight = f'<h2 style="font-size:18px;color:#122033;">Your profile insight</h2><p style="font-size:14px;line-height:1.65;color:#445268;">{narrative}</p><p style="font-size:14px;line-height:1.65;color:#445268;"><strong>{top}</strong></p>'
        actions = ai_analysis.get("priority_actions", []) or []
        if actions:
            actions_html = "<h2 style='font-size:18px;color:#122033;'>Priority actions</h2><ol>" + "".join(
                f"<li style='font-size:14px;line-height:1.6;color:#445268;margin-bottom:6px;'>{a}</li>" for a in actions
            ) + "</ol>"

    html = f"""<!doctype html><html><body style="margin:0;background:#f3f6f8;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="padding:28px 14px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:620px;background:#ffffff;border-radius:14px;">
<tr><td style="padding:28px;">
<div style="font-size:22px;font-weight:800;color:#122033;">ADHD<span style="color:#087f8c;">clearfocus</span></div>
<h1 style="font-size:24px;color:#122033;margin-top:24px;">Your personalised report is attached</h1>
<p style="font-size:14px;line-height:1.65;color:#445268;">Your completed self-reflection profile was used to generate the attached planning report. Your overall profile level is <strong>{level}</strong> ({total_pct}%).</p>
{insight}
<h2 style="font-size:18px;color:#122033;">Your 10-dimension profile</h2>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">{_domain_rows_html(pcts)}</table>
{actions_html}
<p style="font-size:13px;line-height:1.6;color:#445268;margin-top:22px;">Your reference code is <strong>{loyalty_code}</strong>. Keep it for future ClearFocus account or product offers.</p>
<p style="font-size:11px;line-height:1.6;color:#68778a;margin-top:24px;border-top:1px solid #e4e9ee;padding-top:16px;">This report is for education, self-reflection and planning only. It is not a diagnosis or clinical assessment. If you are in immediate danger or crisis, use local emergency services; Samaritans can be reached on 116 123 in Ireland and the UK.</p>
</td></tr></table></td></tr></table></body></html>"""

    return send_transactional_email(
        to_email,
        "Your ADHDclearfocus report",
        html,
        attachments=[{
            "filename": f"ADHDclearfocus_Report_{level}.pdf",
            "content": pdf_b64,
            "content_type": "application/pdf",
        }],
    )


def notify_admin(customer_email, level, total_pct, pcts, loyalty_code, ai_analysis):
    domain_text = "<br>".join(
        f"{DOMAIN_LABELS.get(k, k)}: {v}%" for k, v in pcts.items()
    )
    insight = ai_analysis.get("top_insight", "N/A") if ai_analysis else "AI narrative unavailable"
    html = (
        "<html><body style='font-family:Arial,Helvetica,sans-serif;'>"
        "<h2>New ClearFocus report purchase</h2>"
        f"<p><b>Customer:</b> {customer_email}</p>"
        f"<p><b>Profile:</b> {level} ({total_pct}%)</p>"
        f"<p><b>Reference code:</b> {loyalty_code}</p>"
        f"<p><b>Key insight:</b> {insight}</p>"
        f"<p>{domain_text}</p>"
        "</body></html>"
    )
    return send_transactional_email(
        ADMIN_EMAIL,
        "New ClearFocus report purchase",
        html,
    )


class handler(BaseHTTPRequestHandler):
    def _verify_stripe_signature(self, body):
        if not STRIPE_WEBHOOK_SECRET:
            return False
        sig_header = self.headers.get("Stripe-Signature", "")
        try:
            timestamp = ""
            signatures = []
            for part in sig_header.split(","):
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                if key == "t":
                    timestamp = value
                elif key == "v1":
                    signatures.append(value)
            if not timestamp or not signatures:
                return False
            if abs(time.time() - int(timestamp)) > 300:
                return False
            signed = f"{timestamp}.".encode() + body
            expected = hmac.new(
                STRIPE_WEBHOOK_SECRET.encode(), signed, hashlib.sha256
            ).hexdigest()
            return any(hmac.compare_digest(expected, sig) for sig in signatures)
        except Exception:
            return False

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            content_length = min(int(self.headers.get("Content-Length", 0)), 1_000_000)
            body = self.rfile.read(content_length)
            if not self._verify_stripe_signature(body):
                self._send_json(400, {"error": "invalid_signature"})
                return

            data = json.loads(body or b"{}")
            if data.get("type", "") != "checkout.session.completed":
                self._send_json(200, {"received": True, "ignored": "event_type"})
                return

            session = data.get("data", {}).get("object", {})
            metadata = session.get("metadata", {}) or {}
            if metadata.get("source") != "adhdclearfocus_screener":
                self._send_json(200, {"received": True, "ignored": "not_report_checkout"})
                return
            if session.get("payment_status") and session.get("payment_status") != "paid":
                self._send_json(200, {"received": True, "ignored": "not_paid"})
                return
            if not delivery_provider():
                raise RuntimeError("transactional_email_not_configured")

            customer_email = (
                (session.get("customer_details", {}) or {}).get("email", "")
                or session.get("customer_email", "")
            ).strip().lower()
            if not customer_email or "@" not in customer_email:
                raise RuntimeError("customer_email_missing")

            level = metadata.get("level", "Elevated")
            total_pct = int(metadata.get("total_pct", 0))
            asrs_flag = metadata.get("asrs_flag", "false") == "true"
            asrs_count = int(metadata.get("asrs_count", 0))
            age_group = metadata.get("age_group", "Adult")
            keys = [
                "inattention", "hyperactivity", "executive", "emotional",
                "working_memory", "time", "hyperfocus", "rsd",
                "developmental", "impact",
            ]
            pcts = {k: int(metadata.get(f"pct_{k}", 0)) for k in keys}
            loyalty_code = generate_loyalty_code(customer_email)
            ai_analysis = get_ai_analysis(
                pcts, level, asrs_flag, asrs_count, age_group, total_pct
            )

            pdf_buf = build_report(
                name="Your ADHDclearfocus Profile",
                age_group=age_group,
                level=level,
                total_pct=total_pct,
                asrs_flag=asrs_flag,
                asrs_count=asrs_count,
                pcts=pcts,
                ai_analysis=ai_analysis,
                loyalty_code=loyalty_code,
            )
            pdf_bytes = pdf_buf.read()
            send_report_email(
                customer_email,
                pdf_bytes,
                level,
                total_pct,
                pcts,
                ai_analysis,
                loyalty_code,
                age_group,
            )
            try:
                notify_admin(
                    customer_email, level, total_pct, pcts, loyalty_code, ai_analysis
                )
            except Exception as admin_exc:
                print(f"Admin notification failed: {admin_exc}")

            self._send_json(200, {
                "received": True,
                "fulfilled": True,
                "delivery_provider": delivery_provider(),
            })
        except Exception as exc:
            print(f"Webhook fulfilment error: {exc}")
            self._send_json(500, {"error": "fulfilment_failed"})

    def do_GET(self):
        self._send_json(200, {
            "status": "ADHDclearfocus webhook active",
            "delivery_provider": delivery_provider() or "none",
        })
