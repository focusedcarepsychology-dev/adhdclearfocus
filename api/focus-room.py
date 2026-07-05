"""
ADHDclearfocus — Focus Room proxy
POST /api/focus-room
Actions:
  {"action":"create"} -> {room_id}
  {"action":"heartbeat","room_id","peer_id","peer":{...}} -> {peers}
  {"action":"leave","room_id","peer_id"} -> {ok}

Uses JSONBin as a low-cost relay while keeping the master key server-side.
Env vars: FOCUS_BIN_KEY or JSONBIN_MASTER_KEY.
"""
import json
import os
import re
import time
import http.client
from http.server import BaseHTTPRequestHandler


def env(*names, default=""):
    for name in names:
        for key in (name, name.upper(), name.lower()):
            val = os.environ.get(key)
            if val:
                return val
    return default


BIN_KEY = env("FOCUS_BIN_KEY", "COMMUNITY_BIN_KEY", "JSONBIN_MASTER_KEY", "JSONBIN_API_KEY")
ROOM_RE = re.compile(r"^[a-f0-9]{24}$", re.I)
PEER_RE = re.compile(r"^[A-Za-z0-9_-]{3,80}$")
MAX_PEERS = 40
TTL_MS = 45_000


def clean_text(value, limit=120):
    return str(value or "").replace("\x00", "").strip()[:limit]


def clean_peer(peer):
    peer = peer or {}
    return {
        "name": clean_text(peer.get("name"), 80) or "Focus partner",
        "task": clean_text(peer.get("task"), 160) or "Working silently",
        "struggle": int(peer.get("struggle") or 0),
        "ts": int(peer.get("ts") or time.time()*1000),
    }


def jsonbin_request(method, path, body=None, extra_headers=None):
    if not BIN_KEY:
        raise RuntimeError("focus_storage_not_configured")
    conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
    headers = {"X-Master-Key": BIN_KEY}
    if extra_headers:
        headers.update(extra_headers)
    if body is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(body, separators=(",", ":"))
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"jsonbin_{method}_{resp.status}")
    return json.loads(raw or "{}")


def get_room(room_id):
    data = jsonbin_request("GET", f"/v3/b/{room_id}/latest", extra_headers={"X-Bin-Meta": "false"})
    return data if isinstance(data, dict) else {"type": "acf_focus_room", "peers": {}}


def put_room(room_id, data):
    jsonbin_request("PUT", f"/v3/b/{room_id}", body=data)


class handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

    def do_POST(self):
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 50_000)
            payload = json.loads(self.rfile.read(length) or b"{}")
            action = payload.get("action")
            now = int(time.time()*1000)

            if action == "create":
                data = jsonbin_request("POST", "/v3/b", body={"type": "acf_focus_room", "created": now, "peers": {}}, extra_headers={"X-Bin-Name": "acf_focus_room"})
                room_id = (((data or {}).get("metadata") or {}).get("id"))
                if not room_id:
                    raise RuntimeError("no_room_id")
                self.send_json(200, {"room_id": room_id})
                return

            room_id = clean_text(payload.get("room_id"), 32)
            if not ROOM_RE.match(room_id):
                self.send_json(400, {"error": "invalid_room_id"})
                return
            peer_id = clean_text(payload.get("peer_id"), 90)
            if not PEER_RE.match(peer_id):
                self.send_json(400, {"error": "invalid_peer_id"})
                return

            room = get_room(room_id)
            peers = room.get("peers") if isinstance(room.get("peers"), dict) else {}
            peers = {k: v for k, v in peers.items() if isinstance(v, dict) and now - int(v.get("ts") or 0) <= TTL_MS}

            if action == "heartbeat":
                peers[peer_id] = clean_peer(payload.get("peer"))
                # Keep only freshest peers to protect free-tier storage.
                peers = dict(sorted(peers.items(), key=lambda kv: int(kv[1].get("ts") or 0), reverse=True)[:MAX_PEERS])
                put_room(room_id, {"type": "acf_focus_room", "updated": now, "peers": peers})
                self.send_json(200, {"peers": peers})
                return

            if action == "leave":
                peers.pop(peer_id, None)
                put_room(room_id, {"type": "acf_focus_room", "updated": now, "peers": peers})
                self.send_json(200, {"ok": True})
                return

            self.send_json(400, {"error": "unknown_action"})
        except Exception as exc:
            self.send_json(503, {"error": "focus_room_unavailable", "detail": str(exc)[:160]})
