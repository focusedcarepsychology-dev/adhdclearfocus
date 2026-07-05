"""
ADHDclearfocus — configuration health check
GET /api/health
Returns only present/missing status for required environment variables. Does not expose secrets.
"""
import json
import os
from http.server import BaseHTTPRequestHandler

CHECKS = {
    "paid_report_checkout": ["STRIPE_SECRET_KEY", "STRIPE_PRICE_ID", "DOMAIN"],
    "paid_report_fulfilment": ["STRIPE_WEBHOOK_SECRET", "SENDGRID_API_KEY", "SENDGRID_FROM_EMAIL"],
    "ai_personalisation_optional": ["ANTHROPIC_API_KEY"],
    "employer_leads": ["SENDGRID_API_KEY", "EMPLOYER_LEADS_EMAIL"],
    "accounts_optional": ["AUTH_BIN_ID", "AUTH_BIN_KEY", "AUTH_SECRET"],
    "community_optional": ["COMMUNITY_BIN_ID", "COMMUNITY_BIN_KEY"],
    "focus_rooms_optional": ["FOCUS_BIN_KEY"],
    "mailchimp_optional": ["MAILCHIMP_API_KEY", "MAILCHIMP_LIST_ID"],
}

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
        payload = {group: {name: ("present" if has(name) else "missing") for name in names} for group, names in CHECKS.items()}
        payload["ok_for_paid_report"] = all(v == "present" for section in ("paid_report_checkout", "paid_report_fulfilment") for v in payload[section].values())
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
