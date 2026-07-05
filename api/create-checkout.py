"""
ADHDclearfocus — Stripe Checkout Session Creator
POST /api/create-checkout
Creates a Stripe Checkout Session with screener metadata attached so the webhook
can generate and send the personalised PDF report.

Stdlib only. Env vars:
  STRIPE_SECRET_KEY
  STRIPE_PRICE_ID
  DOMAIN=https://www.adhdclearfocus.com
"""
import json
import os
import base64
import http.client
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode


def env(*names, default=""):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            v = os.environ.get(k)
            if v:
                return v
    return default


STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
PRICE_ID = env("STRIPE_PRICE_ID")
DOMAIN = env("DOMAIN", default="https://www.adhdclearfocus.com").rstrip("/")

DOMAIN_KEYS = [
    "inattention", "hyperactivity", "executive", "emotional", "working_memory",
    "time", "hyperfocus", "rsd", "developmental", "impact"
]


def clamp_pct(value):
    try:
        return max(0, min(100, int(round(float(value)))))
    except Exception:
        return 0


def create_stripe_session(email, metadata):
    if not STRIPE_SECRET_KEY or not PRICE_ID:
        raise RuntimeError("stripe_not_configured")
    params = {
        "mode": "payment",
        "customer_email": email,
        "success_url": f"{DOMAIN}/thank-you.html?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{DOMAIN}/#results",
        "line_items[0][price]": PRICE_ID,
        "line_items[0][quantity]": "1",
        "allow_promotion_codes": "true",
        "metadata[source]": "adhdclearfocus_screener",
    }
    for key, value in metadata.items():
        params[f"metadata[{key}]"] = str(value)[:480]
    body = urlencode(params)
    conn = http.client.HTTPSConnection("api.stripe.com", timeout=25)
    auth = base64.b64encode(f"{STRIPE_SECRET_KEY}:".encode()).decode()
    conn.request("POST", "/v1/checkout/sessions", body, {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Stripe-Version": "2024-06-20",
    })
    response = conn.getresponse()
    raw = response.read().decode("utf-8")
    conn.close()
    data = json.loads(raw or "{}")
    if response.status >= 400:
        raise RuntimeError(data.get("error", {}).get("message", "stripe_error"))
    return data.get("url", "")


class handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = min(int(self.headers.get("Content-Length", 0)), 25_000)
            data = json.loads(self.rfile.read(content_length) or b"{}")
            email = str(data.get("email", "")).strip().lower()[:180]
            if "@" not in email or "." not in email:
                self.send_json(400, {"error": "valid_email_required"})
                return
            pcts = data.get("pcts") or {}
            metadata = {
                "level": str(data.get("level", ""))[:80],
                "total_pct": clamp_pct(data.get("total_pct", 0)),
                "asrs_flag": str(bool(data.get("asrs_flag", False))).lower(),
                "asrs_count": clamp_pct(data.get("asrs_count", 0)),
                "age_group": str(data.get("age_group", "Adult"))[:40],
            }
            for key in DOMAIN_KEYS:
                metadata[f"pct_{key}"] = clamp_pct(pcts.get(key, 0))
            url = create_stripe_session(email, metadata)
            self.send_json(200, {"url": url})
        except Exception:
            # The client falls back to the static Stripe Payment Link.
            self.send_json(503, {"error": "checkout_unavailable"})
