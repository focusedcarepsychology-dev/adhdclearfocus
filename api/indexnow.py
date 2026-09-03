"""Submit current public ADHDclearfocus URLs to IndexNow.
GET /api/indexnow
This endpoint submits only the fixed canonical URL list below; callers cannot inject URLs.
"""
import json
import http.client
from http.server import BaseHTTPRequestHandler

HOST = "www.adhdclearfocus.com"
KEY = "4f8b2d7a9c1e6f3a5b7d8e0c2a4f6b9d"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
URLS = [
  "https://www.adhdclearfocus.com/",
  "https://www.adhdclearfocus.com/assessment",
  "https://www.adhdclearfocus.com/guides",
  "https://www.adhdclearfocus.com/strategies",
  "https://www.adhdclearfocus.com/resources",
  "https://www.adhdclearfocus.com/insights",
  "https://www.adhdclearfocus.com/crisis",
  "https://www.adhdclearfocus.com/community",
  "https://www.adhdclearfocus.com/pricing",
  "https://www.adhdclearfocus.com/workplace",
  "https://www.adhdclearfocus.com/legal",
  "https://www.adhdclearfocus.com/about",
  "https://www.adhdclearfocus.com/methodology",
  "https://www.adhdclearfocus.com/editorial-policy",
  "https://www.adhdclearfocus.com/ie",
  "https://www.adhdclearfocus.com/uk",
  "https://www.adhdclearfocus.com/adult-adhd",
  "https://www.adhdclearfocus.com/adhd-screening-test",
  "https://www.adhdclearfocus.com/adhd-in-women",
  "https://www.adhdclearfocus.com/adhd-or-anxiety",
  "https://www.adhdclearfocus.com/adhd-paralysis",
  "https://www.adhdclearfocus.com/adhd-time-blindness",
  "https://www.adhdclearfocus.com/adhd-and-sleep",
  "https://www.adhdclearfocus.com/adhd-medication-evidence",
  "https://www.adhdclearfocus.com/cbt-for-adhd",
  "https://www.adhdclearfocus.com/exercise-and-adhd",
  "https://www.adhdclearfocus.com/adhd-body-doubling",
  "https://www.adhdclearfocus.com/adhd-focus-timer",
  "https://www.adhdclearfocus.com/adhd-workplace-adjustments",
  "https://www.adhdclearfocus.com/adhd-assessment-ireland",
  "https://www.adhdclearfocus.com/adhd-assessment-uk",
  "https://www.adhdclearfocus.com/employers/adhd-awareness-training",
  "https://www.adhdclearfocus.com/employers/adhd-manager-training",
  "https://www.adhdclearfocus.com/employers/adhd-workplace-adjustments",
  "https://www.adhdclearfocus.com/employers/neurodiversity-training-ireland",
  "https://www.adhdclearfocus.com/employers/neurodiversity-training-uk"
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = json.dumps({
            "host": HOST,
            "key": KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": URLS,
        })
        try:
            conn = http.client.HTTPSConnection("api.indexnow.org", timeout=20)
            conn.request("POST", "/indexnow", payload, {"Content-Type": "application/json; charset=utf-8"})
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8", errors="replace")
            conn.close()
            body = json.dumps({"ok": 200 <= resp.status < 300, "status": resp.status, "submitted": len(URLS), "detail": raw[:300]}).encode()
            self.send_response(200 if 200 <= resp.status < 300 else 502)
        except Exception as exc:
            body = json.dumps({"ok": False, "error": str(exc)[:300]}).encode()
            self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
