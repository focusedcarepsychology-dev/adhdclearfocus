"""
ADHDclearfocus — Employer Lead Email
POST /api/employer-lead
Sends workplace programme enquiries to EMPLOYER_LEADS_EMAIL / ADMIN_EMAIL using SendGrid.
Falls back gracefully on the frontend if SendGrid is not configured.
"""
import json
import os
import html
import http.client
from http.server import BaseHTTPRequestHandler


def env(*names, default=""):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            v = os.environ.get(k)
            if v:
                return v
    return default


SENDGRID_API_KEY = env("SENDGRID_API_KEY")
FROM_EMAIL = env("SENDGRID_FROM_EMAIL", "FROM_EMAIL", default="focusedcarepsychology@gmail.com")
FROM_NAME = env("SENDGRID_FROM_NAME", "FROM_NAME", default="ADHDclearfocus")
LEADS_EMAIL = env("EMPLOYER_LEADS_EMAIL", "ADMIN_EMAIL", default="focusedcarepsychology@gmail.com")


def clean(value, limit=1000):
    value = str(value or "").replace("\r", " ").replace("\x00", " ").strip()
    return value[:limit]


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 20_000)
            data = json.loads(self.rfile.read(length) or b"{}")
            email = clean(data.get("email"), 180).lower()
            company = clean(data.get("company"), 240)
            message = clean(data.get("message"), 4000)
            page = clean(data.get("page"), 240) or "/workplace.html"

            if "@" not in email or "." not in email:
                self._send(400, {"ok": False, "error": "invalid_email"})
                return

            if not SENDGRID_API_KEY:
                self._send(503, {"ok": False, "error": "sendgrid_not_configured"})
                return

            subject = f"Workplace programme enquiry — {company or 'new lead'}"
            safe_email = html.escape(email)
            safe_company = html.escape(company or "Not provided")
            safe_message = html.escape(message or "No message provided").replace("\n", "<br>")
            safe_page = html.escape(page)

            html_body = f"""
            <div style="font-family:Arial,sans-serif;background:#0A1628;color:#fff;padding:24px">
              <div style="max-width:640px;margin:auto;background:#112240;border:1px solid #1E3A5F;border-radius:14px;padding:22px">
                <h1 style="font-size:20px;margin:0 0 12px;color:#00D4DD">New ADHDclearfocus workplace enquiry</h1>
                <p style="color:#A8C4D8;margin:0 0 18px">A visitor submitted the employer enquiry form.</p>
                <table style="width:100%;border-collapse:collapse;color:#E0EAF4;font-size:14px">
                  <tr><td style="padding:8px 0;color:#7B93B4;width:120px">Email</td><td style="padding:8px 0"><a href="mailto:{safe_email}" style="color:#00D4DD">{safe_email}</a></td></tr>
                  <tr><td style="padding:8px 0;color:#7B93B4">Company</td><td style="padding:8px 0">{safe_company}</td></tr>
                  <tr><td style="padding:8px 0;color:#7B93B4;vertical-align:top">Message</td><td style="padding:8px 0;line-height:1.6">{safe_message}</td></tr>
                  <tr><td style="padding:8px 0;color:#7B93B4">Page</td><td style="padding:8px 0">{safe_page}</td></tr>
                </table>
              </div>
            </div>
            """

            text_body = (
                "New ADHDclearfocus workplace enquiry\n\n"
                f"Email: {email}\n"
                f"Company: {company or 'Not provided'}\n"
                f"Message: {message or 'No message provided'}\n"
                f"Page: {page}\n"
            )

            payload = {
                "personalizations": [{"to": [{"email": LEADS_EMAIL}], "subject": subject}],
                "from": {"email": FROM_EMAIL, "name": FROM_NAME},
                "reply_to": {"email": email},
                "content": [
                    {"type": "text/plain", "value": text_body},
                    {"type": "text/html", "value": html_body},
                ],
            }
            conn = http.client.HTTPSConnection("api.sendgrid.com", timeout=20)
            headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
            conn.request("POST", "/v3/mail/send", json.dumps(payload), headers)
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8", errors="replace")
            conn.close()

            if 200 <= resp.status < 300:
                self._send(200, {"ok": True, "sent_to": LEADS_EMAIL})
            else:
                self._send(502, {"ok": False, "error": f"sendgrid_{resp.status}", "detail": raw[:200]})
        except Exception as exc:
            self._send(500, {"ok": False, "error": str(exc)[:200]})
