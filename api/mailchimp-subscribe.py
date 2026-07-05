"""
ADHDclearfocus — Mailchimp Subscribe Proxy
POST /api/mailchimp-subscribe
Server-side list capture to avoid CORS and keep the API key private.
If Mailchimp is not configured, returns 202 so the site experience does not break.
"""
import json
import os
import http.client
import base64
import hashlib
from http.server import BaseHTTPRequestHandler


def env(*names, default=""):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            v = os.environ.get(k)
            if v:
                return v
    return default


MAILCHIMP_API_KEY = env("MAILCHIMP_API_KEY")
MAILCHIMP_LIST_ID = env("MAILCHIMP_LIST_ID", default="3f6c1e163c")
MAILCHIMP_SERVER = env("MAILCHIMP_SERVER", default=(MAILCHIMP_API_KEY.split("-")[-1] if "-" in MAILCHIMP_API_KEY else "us13"))


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, payload):
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
            email = str(data.get("email", "")).strip().lower()[:180]
            tags = data.get("tags", [])
            merge_fields = data.get("merge_fields", {})
            if not email or "@" not in email or "." not in email:
                self._respond(400, {"error": "invalid_email"})
                return
            if not MAILCHIMP_API_KEY or not MAILCHIMP_LIST_ID:
                self._respond(202, {"success": True, "configured": False})
                return
            tags = [str(t)[:80] for t in tags[:12]] if isinstance(tags, list) else []
            if not isinstance(merge_fields, dict):
                merge_fields = {}
            payload = json.dumps({
                "email_address": email,
                "status_if_new": "subscribed",
                "status": "subscribed",
                "tags": tags,
                "merge_fields": {str(k)[:10]: str(v)[:255] for k, v in merge_fields.items()},
            })
            subscriber_hash = hashlib.md5(email.encode()).hexdigest()
            auth = base64.b64encode(f"anystring:{MAILCHIMP_API_KEY}".encode()).decode()
            conn = http.client.HTTPSConnection(f"{MAILCHIMP_SERVER}.api.mailchimp.com", timeout=20)
            conn.request("PUT", f"/3.0/lists/{MAILCHIMP_LIST_ID}/members/{subscriber_hash}", payload,
                         {"Content-Type": "application/json", "Authorization": f"Basic {auth}"})
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8")
            conn.close()
            if resp.status in (200, 201):
                self._respond(200, {"success": True, "configured": True})
            else:
                self._respond(202, {"success": True, "warning": f"mailchimp_{resp.status}", "detail": raw[:160]})
        except Exception:
            self._respond(202, {"success": True, "warning": "subscribe_deferred"})
