"""
ADHDclearfocus — Accounts (free-tier auth + tracker sync)
POST /api/auth

Actions (JSON body):
  {"action":"signup", "email","password","name"}          -> {token, name}
  {"action":"login",  "email","password"}                 -> {token, name, data}
  {"action":"get_data","token"}                           -> {data}
  {"action":"set_data","token","data":{...}}              -> {ok}

Storage: a JSONBin record — SEPARATE account/key from the public forum key.
Env vars (Vercel → Settings → Environment Variables):
  AUTH_BIN_ID   — bin id of a bin created with body {"users": {}}
  AUTH_BIN_KEY  — that account's master key (NEVER shipped to the client)
  AUTH_SECRET   — any long random string (signs session tokens)

Security model (honest scope): PBKDF2-HMAC-SHA256 (200k iterations) password
hashing; HMAC-signed expiring tokens (30 days); the bin key never leaves the
server. Suitable for a community forum + wellness tracker. NOT suitable for
clinical records or payments — those stay with Stripe/SendGrid as before.
Free-tier limits: JSONBin free plan has monthly request caps; at forum scale
this is fine, and the client caches aggressively. Python stdlib only.
"""
import json
import os
import time
import base64
import hashlib
import hmac as hmac_mod
import http.client
from http.server import BaseHTTPRequestHandler

def _env(*names):
    for n in names:
        for k in (n, n.upper(), n.lower()):
            v = os.environ.get(k)
            if v:
                return v
    return ""


BIN_ID = _env("AUTH_BIN_ID")
BIN_KEY = _env("AUTH_BIN_KEY")
SECRET = _env("AUTH_SECRET")

TOKEN_TTL = 30 * 24 * 3600  # 30 days
MAX_DATA_BYTES = 20_000     # per-user tracker blob cap
MAX_USERS = 5000            # free-tier sanity cap


def _b64e(b): return base64.urlsafe_b64encode(b).decode().rstrip("=")
def _b64d(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return _b64e(salt), _b64e(dk)


def verify_password(password, salt_b64, hash_b64):
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), _b64d(salt_b64), 200_000)
    return hmac_mod.compare_digest(_b64e(dk), hash_b64)


def make_token(email):
    exp = str(int(time.time()) + TOKEN_TTL)
    payload = email + "|" + exp
    sig = hmac_mod.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return _b64e((payload + "|" + sig).encode())


def check_token(token):
    try:
        email, exp, sig = _b64d(token).decode().split("|")
        payload = email + "|" + exp
        good = hmac_mod.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac_mod.compare_digest(sig, good):
            return None
        if int(exp) < time.time():
            return None
        return email
    except Exception:
        return None


def bin_read():
    conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
    conn.request("GET", f"/v3/b/{BIN_ID}/latest",
                 headers={"X-Master-Key": BIN_KEY, "X-Bin-Meta": "false"})
    r = conn.getresponse()
    raw = r.read().decode()
    conn.close()
    if r.status != 200:
        raise RuntimeError("bin read failed")
    d = json.loads(raw)
    if not isinstance(d, dict):
        d = {}
    d.setdefault("users", {})
    return d


def bin_write(d):
    conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
    conn.request("PUT", f"/v3/b/{BIN_ID}",
                 body=json.dumps(d),
                 headers={"Content-Type": "application/json",
                          "X-Master-Key": BIN_KEY})
    r = conn.getresponse()
    r.read()
    conn.close()
    if r.status != 200:
        raise RuntimeError("bin write failed")


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
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

    def do_GET(self):
        """One-time setup: with AUTH_BIN_KEY + AUTH_SECRET set (AUTH_BIN_ID not yet),
        visiting /api/auth?setup=1 creates the users bin and shows the id to paste
        into Vercel as AUTH_BIN_ID. Idempotent-safe: refuses if AUTH_BIN_ID exists."""
        if "setup=1" not in (self.path or ""):
            self._send(200, {"service": "adhdclearfocus-auth",
                             "configured": bool(BIN_ID and BIN_KEY and SECRET)})
            return
        if BIN_ID:
            self._send(200, {"status": "already_configured",
                             "message": "AUTH_BIN_ID is already set — nothing to do."})
            return
        if not BIN_KEY:
            self._send(400, {"status": "missing_key",
                             "message": "Set AUTH_BIN_KEY (a NEW JSONBin account's master key) "
                                        "in Vercel first, then visit this URL again."})
            return
        try:
            conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
            conn.request("POST", "/v3/b",
                         body=json.dumps({"users": {}}),
                         headers={"Content-Type": "application/json",
                                  "X-Master-Key": BIN_KEY,
                                  "X-Bin-Name": "acf_users",
                                  "X-Bin-Private": "true"})
            r = conn.getresponse()
            raw = r.read().decode()
            conn.close()
            d = json.loads(raw)
            new_id = (d.get("metadata") or {}).get("id", "")
            if r.status in (200, 201) and new_id:
                self._send(200, {"status": "created",
                                 "AUTH_BIN_ID": new_id,
                                 "next_step": "Copy the AUTH_BIN_ID value above into "
                                              "Vercel -> Settings -> Environment Variables, "
                                              "then redeploy. Accounts will then be live."})
            else:
                self._send(502, {"status": "jsonbin_error", "detail": raw[:300]})
        except Exception as e:
            self._send(502, {"status": "error", "detail": str(e)[:200]})

    def do_POST(self):
        if not (BIN_ID and BIN_KEY and SECRET):
            self._send(503, {"error": "auth_not_configured"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._send(400, {"error": "bad_json"})
            return

        action = data.get("action", "")

        if action == "signup":
            email = str(data.get("email", "")).strip().lower()[:120]
            password = str(data.get("password", ""))
            name = str(data.get("name", "")).strip()[:40] or email.split("@")[0]
            if "@" not in email or "." not in email:
                self._send(400, {"error": "invalid_email"}); return
            if len(password) < 8:
                self._send(400, {"error": "password_too_short",
                                 "message": "Password must be at least 8 characters"}); return
            try:
                db = bin_read()
                if email in db["users"]:
                    self._send(409, {"error": "exists",
                                     "message": "An account with this email already exists — log in instead"}); return
                if len(db["users"]) >= MAX_USERS:
                    self._send(503, {"error": "capacity"}); return
                salt, pw = hash_password(password)
                db["users"][email] = {"salt": salt, "pw": pw, "name": name,
                                      "created": int(time.time()), "data": {}}
                bin_write(db)
                self._send(200, {"token": make_token(email), "name": name})
            except Exception:
                self._send(503, {"error": "storage_unavailable"})
            return

        if action == "login":
            email = str(data.get("email", "")).strip().lower()
            password = str(data.get("password", ""))
            try:
                db = bin_read()
                u = db["users"].get(email)
                if not u or not verify_password(password, u["salt"], u["pw"]):
                    self._send(401, {"error": "bad_credentials",
                                     "message": "Email or password incorrect"}); return
                self._send(200, {"token": make_token(email), "name": u.get("name", ""),
                                 "data": u.get("data", {})})
            except Exception:
                self._send(503, {"error": "storage_unavailable"})
            return

        if action in ("get_data", "set_data"):
            email = check_token(str(data.get("token", "")))
            if not email:
                self._send(401, {"error": "invalid_token"}); return
            try:
                db = bin_read()
                u = db["users"].get(email)
                if not u:
                    self._send(401, {"error": "no_account"}); return
                if action == "get_data":
                    self._send(200, {"data": u.get("data", {}), "name": u.get("name", "")})
                    return
                blob = data.get("data", {})
                if not isinstance(blob, dict) or len(json.dumps(blob)) > MAX_DATA_BYTES:
                    self._send(400, {"error": "data_too_large"}); return
                u["data"] = blob
                bin_write(db)
                self._send(200, {"ok": True})
            except Exception:
                self._send(503, {"error": "storage_unavailable"})
            return

        self._send(400, {"error": "unknown_action"})
