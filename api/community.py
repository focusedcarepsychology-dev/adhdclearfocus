"""
ADHDclearfocus — Community storage proxy
POST /api/community
GET  /api/community?action=get_posts

Keeps JSONBin master keys server-side. Uses stdlib only for Vercel Python.
Env vars:
  COMMUNITY_BIN_ID   JSONBin bin holding {"posts": []}
  COMMUNITY_BIN_KEY  JSONBin master key for that bin
Optional fallbacks: JSONBIN_BIN_ID, JSONBIN_MASTER_KEY
"""
import json
import os
import re
import time
import http.client
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def env(*names, default=""):
    for name in names:
        for key in (name, name.upper(), name.lower()):
            val = os.environ.get(key)
            if val:
                return val
    return default


BIN_ID = env("COMMUNITY_BIN_ID", "JSONBIN_BIN_ID")
BIN_KEY = env("COMMUNITY_BIN_KEY", "JSONBIN_MASTER_KEY", "JSONBIN_API_KEY")
MAX_POSTS = 250
MAX_TITLE = 120
MAX_BODY = 2400
MAX_REPLY = 700
ALLOWED_TAGS = {"Attention", "Executive Function", "Emotional", "RSD", "Medication", "Relationships", "Work & Study", "Wins", "Question"}


def clean_text(value, limit):
    text = str(value or "").replace("\x00", "").strip()
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    return text[:limit]


def clean_post(raw):
    raw = raw or {}
    post_id = clean_text(raw.get("id"), 80) or f"u_{int(time.time()*1000)}"
    tag = clean_text(raw.get("tag"), 40)
    if tag not in ALLOWED_TAGS:
        tag = "Question"
    replies = []
    for r in raw.get("replies", [])[:80] if isinstance(raw.get("replies", []), list) else []:
        replies.append({
            "author": clean_text(r.get("author"), 80) or "community_member",
            "text": clean_text(r.get("text"), MAX_REPLY),
            "time": int(r.get("time") or time.time()*1000),
        })
    return {
        "id": post_id,
        "pinned": False,
        "tag": tag,
        "title": clean_text(raw.get("title"), MAX_TITLE),
        "body": clean_text(raw.get("body"), MAX_BODY),
        "displayName": clean_text(raw.get("displayName"), 80) or "community_member",
        "time": int(raw.get("time") or time.time()*1000),
        "likes": max(0, min(9999, int(raw.get("likes") or 0))),
        "replies": replies,
        "avatar": clean_text(raw.get("avatar"), 8) or "🧠",
    }


def jsonbin_get():
    if not BIN_ID or not BIN_KEY:
        raise RuntimeError("community_storage_not_configured")
    conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
    conn.request("GET", f"/v3/b/{BIN_ID}/latest", headers={"X-Master-Key": BIN_KEY, "X-Bin-Meta": "false"})
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"jsonbin_get_{resp.status}")
    data = json.loads(body or "{}")
    if isinstance(data, list):
        return {"posts": data}
    return data if isinstance(data, dict) else {"posts": []}


def jsonbin_put(data):
    conn = http.client.HTTPSConnection("api.jsonbin.io", timeout=20)
    body = json.dumps(data, separators=(",", ":"))
    conn.request("PUT", f"/v3/b/{BIN_ID}", body=body, headers={"Content-Type": "application/json", "X-Master-Key": BIN_KEY})
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"jsonbin_put_{resp.status}:{raw[:120]}")


class handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            if qs.get("action", ["get_posts"])[0] != "get_posts":
                self.send_json(400, {"error": "unknown_action"})
                return
            data = jsonbin_get()
            posts = data.get("posts", []) if isinstance(data, dict) else []
            if not isinstance(posts, list):
                posts = []
            self.send_json(200, {"posts": posts[:MAX_POSTS]})
        except Exception as exc:
            self.send_json(503, {"error": "community_storage_unavailable", "detail": str(exc)[:160]})

    def do_POST(self):
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 80_000)
            payload = json.loads(self.rfile.read(length) or b"{}")
            action = payload.get("action")
            post = clean_post(payload.get("post") or {})
            if not post["title"] or len(post["body"]) < 10:
                self.send_json(400, {"error": "post_too_short"})
                return
            data = jsonbin_get()
            posts = data.get("posts", []) if isinstance(data, dict) else []
            if not isinstance(posts, list):
                posts = []
            posts = [clean_post(p) for p in posts if isinstance(p, dict)]
            idx = next((i for i, p in enumerate(posts) if p.get("id") == post["id"]), -1)
            if action == "add_post":
                if idx >= 0:
                    posts[idx] = post
                else:
                    posts.insert(0, post)
            elif action == "update_post":
                if idx >= 0:
                    # Preserve original pinned status as false for user posts.
                    posts[idx] = post
                else:
                    posts.insert(0, post)
            else:
                self.send_json(400, {"error": "unknown_action"})
                return
            jsonbin_put({"posts": posts[:MAX_POSTS], "updated": int(time.time())})
            self.send_json(200, {"ok": True, "posts": posts[:MAX_POSTS]})
        except Exception as exc:
            self.send_json(503, {"error": "community_storage_unavailable", "detail": str(exc)[:160]})
