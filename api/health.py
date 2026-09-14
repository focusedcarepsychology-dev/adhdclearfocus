"""
ADHDclearfocus — configuration health check
GET /api/health
Returns only present/missing status for required environment variables. Does not expose secrets.
"""
import json
import os
from http.server import BaseHTTPRequestHandler

ALIASES = {
    "SENDGRID_FROM_EMAIL": ["SENDGRID_FROM_EMAIL", "FROM_EMAIL"],
    "EMPLOYER_LEADS_EMAIL": ["EMPLOYER_LEADS_EMAIL", "ADMIN_EMAIL"],
    "COMMUNITY_BIN_KEY": ["COMMUNITY_BIN_KEY", "JSONBIN_MASTER_KEY", "JSONBIN_API_KEY"],
    "FOCUS_BIN_KEY": ["FOCUS_BIN_KEY", "JSONBIN_MASTER_KEY", "JSONBIN_API_KEY"],
}


def has(name):
    names = ALIASES.get(name, [name])
    return any(os.environ.get(n) or os.environ.get(n.lower()) for n in names)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        checkout = {
            "STRIPE_SECRET_KEY": "present" if has("STRIPE_SECRET_KEY") else "missing",
        }
        fulfilment = {
            "STRIPE_WEBHOOK_SECRET": "present" if has("STRIPE_WEBHOOK_SECRET") else "missing",
            "RESEND_API_KEY": "present" if has("RESEND_API_KEY") else "missing",
            "SENDGRID_API_KEY": "present" if has("SENDGRID_API_KEY") else "missing",
            "SENDGRID_FROM_EMAIL": "present" if has("SENDGRID_FROM_EMAIL") else "missing",
        }
        resend_ready = has("RESEND_API_KEY")
        sendgrid_ready = has("SENDGRID_API_KEY") and has("SENDGRID_FROM_EMAIL")
        email_ready = resend_ready or sendgrid_ready

        payload = {
            "paid_report_checkout": checkout,
            "paid_report_fulfilment": fulfilment,
            "delivery_provider": "resend" if resend_ready else ("sendgrid" if sendgrid_ready else "none"),
            "ai_personalisation_optional": {
                "ANTHROPIC_API_KEY": "present" if has("ANTHROPIC_API_KEY") else "missing",
            },
            "employer_leads": {
                "SENDGRID_API_KEY": "present" if has("SENDGRID_API_KEY") else "missing",
                "EMPLOYER_LEADS_EMAIL": "present" if has("EMPLOYER_LEADS_EMAIL") else "missing",
            },
            "accounts_optional": {
                name: ("present" if has(name) else "missing")
                for name in ("AUTH_BIN_ID", "AUTH_BIN_KEY", "AUTH_SECRET")
            },
            "community_optional": {
                name: ("present" if has(name) else "missing")
                for name in ("COMMUNITY_BIN_ID", "COMMUNITY_BIN_KEY")
            },
            "focus_rooms_optional": {
                "FOCUS_BIN_KEY": "present" if has("FOCUS_BIN_KEY") else "missing",
            },
            "mailchimp_optional": {
                name: ("present" if has(name) else "missing")
                for name in ("MAILCHIMP_API_KEY", "MAILCHIMP_LIST_ID")
            },
            "pricing_mode": "inline_eur_49",
            "ok_for_paid_report": bool(
                has("STRIPE_SECRET_KEY")
                and has("STRIPE_WEBHOOK_SECRET")
                and email_ready
            ),
        }
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
