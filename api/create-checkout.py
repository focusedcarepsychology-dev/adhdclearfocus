"""
ADHDclearfocus — Stripe Checkout Session Creator
POST /api/create-checkout
Creates a Stripe Checkout Session with screener metadata attached so the webhook
can generate and send the personalised PDF report.

Stdlib only. Required env vars before payment is enabled:
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SECRET
  SENDGRID_API_KEY
  SENDGRID_FROM_EMAIL (or FROM_EMAIL; sender must already be verified in SendGrid)

Optional:
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
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = env("SENDGRID_FROM_EMAIL", "FROM_EMAIL")
DOMAIN = env("DOMAIN", default="https://www.adhdclearfocus.com").rstrip("/")

REPORT_PRICE_EUR_CENTS = 4900
REPORT_PRODUCT_NAME = "ClearFocus personalised ADHD planning report"
REPORT_PRODUCT_DESCRIPTION = "One personalised digital planning report generated from the completed ClearFocus self-reflection assessment. Educational and planning support; not a diagnostic assessment."

DOMAIN_KEYS = [
    "inattention", "hyperactivity", "executive", "emotional", "working_memory",
    "time", "hyperfocus", "rsd", "developmental", "impact"
]


def clamp_pct(value):
    try:
        return max(0, min(100, int(round(float(value)))))
    except Exception:
        return 0


def payment_stack_ready():
    # Do not take money unless the Stripe webhook and explicit verified-email
    # configuration needed for automatic report fulfilment are present too.
    return all((
        STRIPE_SECRET_KEY,
        STRIPE_WEBHOOK_SECRET,
        SENDGRID_API_KEY,
        SENDGRID_FROM_EMAIL,
    ))


def create_stripe_session(email, metadata):
    if not payment_stack_ready():
        raise RuntimeError("paid_report_fulfilment_not_configured")

    params = {
        "mode": "payment",
        "customer_email": email,
        "success_url": f"{DOMAIN}/thank-you.html?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{DOMAIN}/assessment.html#results",
        # Use inline one-time pricing so deployment does not depend on a separate
        # STRIPE_PRICE_ID. Checkout still creates the charge in the configured
        # Stripe account and preserves the Session metadata used by the webhook.
        "line_items[0][price_data][currency]": "eur",
        "line_items[0][price_data][unit_amount]": str(REPORT_PRICE_EUR_CENTS),
        "line_items[0][price_data][product_data][name]": REPORT_PRODUCT_NAME,
        "line_items[0][price_data][product_data][description]": REPORT_PRODUCT_DESCRIPTION,
        "line_items[0][quantity]": "1",
        "allow_promotion_codes": "true",
        "metadata[source]": "adhdclearfocus_screener",
        "metadata[product]": "personalised_report_eur_49",
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
            if not url:
                raise RuntimeError("stripe_checkout_url_missing")
            self.send_json(200, {"url": url})
        except Exception:
            # Do not provide a generic Payment Link fallback; it would not contain
            # the assessment metadata needed to generate the personalised PDF.
            self.send_json(503, {"error": "checkout_unavailable"})
