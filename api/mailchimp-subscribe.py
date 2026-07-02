"""
ADHDclearfocus — Mailchimp Subscribe Proxy
Serverless function to handle Mailchimp subscriptions server-side,
avoiding CORS restrictions that block direct browser API calls.
"""
import json
import os
import http.client
import base64
from http.server import BaseHTTPRequestHandler

MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
MAILCHIMP_LIST_ID = os.environ.get("MAILCHIMP_LIST_ID", "3f6c1e163c")
MAILCHIMP_SERVER = "us13"

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            email = data.get("email", "")
            tags = data.get("tags", [])
            merge_fields = data.get("merge_fields", {})

            if not email or "@" not in email:
                self._respond(400, {"error": "Invalid email"})
                return

            payload = json.dumps({
                "email_address": email,
                "status": "subscribed",
                "tags": tags,
                "merge_fields": merge_fields,
            })

            auth = base64.b64encode(f"anystring:{MAILCHIMP_API_KEY}".encode()).decode()
            conn = http.client.HTTPSConnection(f"{MAILCHIMP_SERVER}.api.mailchimp.com")
            conn.request("POST",
                f"/3.0/lists/{MAILCHIMP_LIST_ID}/members",
                payload,
                {"Content-Type": "application/json", "Authorization": f"Basic {auth}"})
            resp = conn.getresponse()
            resp_body = resp.read()

            # 200 or 400 (member exists) are both acceptable
            if resp.status in (200, 201, 400):
                self._respond(200, {"success": True})
            else:
                self._respond(500, {"error": f"Mailchimp error {resp.status}"})

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
