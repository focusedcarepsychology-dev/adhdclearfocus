"""
ADHDclearfocus — AI Diary Coach
POST /api/coach  body: {"text": "<diary entry>"}
Returns: {"reply": "<coaching response>"} 

Uses the same ANTHROPIC_API_KEY already required by webhook.py.
Python stdlib only (no pip SDKs) — consistent with platform architecture.
Falls back gracefully: if the key is missing or the call fails, returns 503
and the client uses its built-in offline responder.
"""
import json
import os
import hmac as _h  # noqa
import http.client
from http.server import BaseHTTPRequestHandler

SYSTEM_PROMPT = (
    "You are the ADHDclearfocus diary coach. The user has ADHD traits and has "
    "written a short diary entry. Respond in 60-110 words, warm but concrete. "
    "Rules: (1) Reflect ONE specific thing they said. (2) Offer ONE small, "
    "evidence-informed next step (implementation intentions, task chunking, "
    "body doubling, a 20-minute walk, or affect labelling). (3) Never diagnose, "
    "never mention medication, never give clinical advice. (4) If the entry "
    "suggests self-harm or crisis, respond ONLY with: telling them you're "
    "concerned, to use the Crisis Mode page, and to call Samaritans 116 123 "
    "(free, 24/7). (5) Plain text, no lists, no headings."
)


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
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
        api_key = (os.environ.get("ANTHROPIC_API_KEY")
                   or os.environ.get("anthropic_api_key") or "")
        if not api_key:
            self._send(503, {"error": "coach_unavailable"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            text = str(data.get("text", ""))[:2000].strip()
            if len(text) < 3:
                self._send(400, {"error": "empty"})
                return

            payload = json.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": text}],
            })
            conn = http.client.HTTPSConnection("api.anthropic.com", timeout=25)
            conn.request("POST", "/v1/messages", body=payload, headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            })
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8")
            conn.close()
            if resp.status != 200:
                self._send(503, {"error": "coach_unavailable"})
                return
            out = json.loads(raw)
            reply = "".join(
                b.get("text", "") for b in out.get("content", [])
                if b.get("type") == "text"
            ).strip()
            if not reply:
                self._send(503, {"error": "coach_unavailable"})
                return
            self._send(200, {"reply": reply})
        except Exception:
            self._send(503, {"error": "coach_unavailable"})
