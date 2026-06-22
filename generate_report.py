"""
ADHDclearfocus — Stripe Checkout Session Creator
Creates a Stripe checkout session with screener metadata attached,
so the webhook can generate a personalised PDF report.
"""

import json
import os
import http.client
from http.server import BaseHTTPRequestHandler

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")  # €49 report price ID
DOMAIN = os.environ.get("DOMAIN", "https://adhdclearfocus.com")


def create_stripe_session(email, metadata):
    """Create a Stripe checkout session with metadata."""
    params = {
        "mode": "payment",
        "customer_email": email,
        "success_url": f"{DOMAIN}/thank-you.html",
        "cancel_url": f"{DOMAIN}/",
        "line_items[0][price]": PRICE_ID,
        "line_items[0][quantity]": "1",
    }
    # Add metadata
    for key, value in metadata.items():
        params[f"metadata[{key}]"] = str(value)

    body = "&".join(f"{k}={v}" for k, v in params.items())

    conn = http.client.HTTPSConnection("api.stripe.com")
    import base64
    auth = base64.b64encode(f"{STRIPE_SECRET_KEY}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    conn.request("POST", "/v1/checkout/sessions", body, headers)
    response = conn.getresponse()
    data = json.loads(response.read())
    return data.get("url", "")


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            email = data.get("email", "")
            pcts_in = data.get("pcts", {})
            metadata = {
                "level":              data.get("level", ""),
                "total_pct":          data.get("total_pct", 0),
                "asrs_flag":          str(data.get("asrs_flag", False)).lower(),
                "asrs_count":         data.get("asrs_count", 0),
                "age_group":          data.get("age_group", "Adult"),
                "pct_inattention":    pcts_in.get("inattention",    0),
                "pct_hyperactivity":  pcts_in.get("hyperactivity",  0),
                "pct_executive":      pcts_in.get("executive",      0),
                "pct_emotional":      pcts_in.get("emotional",      0),
                "pct_working_memory": pcts_in.get("working_memory", 0),
                "pct_time":           pcts_in.get("time",           0),
                "pct_hyperfocus":     pcts_in.get("hyperfocus",     0),
                "pct_rsd":            pcts_in.get("rsd",            0),
                "pct_developmental":  pcts_in.get("developmental",  0),
                "pct_impact":         pcts_in.get("impact",         0),
            }

            url = create_stripe_session(email, metadata)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"url": url}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
