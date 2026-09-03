#!/usr/bin/env python3
"""Static SEO quality gate for ADHDclearfocus."""
from pathlib import Path
from urllib.parse import urlparse
import re, sys, json
from datetime import date, datetime

ROOT=Path(__file__).resolve().parents[1]
errors=[]
sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
locs=re.findall(r"<loc>(https://www\.adhdclearfocus\.com[^<]+)</loc>",sitemap)
if not locs:
    errors.append("sitemap.xml contains no canonical URLs")

def file_for(url):
    p=urlparse(url).path.strip("/")
    if not p: return ROOT/"index.html"
    return ROOT/(p+".html")

for url in locs:
    f=file_for(url)
    if not f.exists():
        errors.append(f"sitemap URL has no source file: {url} -> {f.relative_to(ROOT)}")
        continue
    c=f.read_text(encoding="utf-8",errors="replace")
    if re.search(r'<meta\s+name=["\']robots["\'][^>]+noindex',c,re.I):
        errors.append(f"indexable sitemap URL is noindex: {url}")
    m=re.search(r'<link\s+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',c,re.I)
    if not m:
        m=re.search(r'<link\s+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',c,re.I)
    if not m or m.group(1).rstrip("/") != url.rstrip("/"):
        errors.append(f"canonical mismatch: {url} -> {m.group(1) if m else 'missing'}")
    if not re.search(r"<title>.+?</title>",c,re.I|re.S):
        errors.append(f"missing title: {url}")
    if not re.search(r'<meta[^>]+name=["\']description["\']',c,re.I):
        errors.append(f"missing meta description: {url}")
    if ".html" in "\n".join(re.findall(r'href=["\']([^"\']+)',c,re.I)):
        errors.append(f"legacy .html internal link: {url}")
    if "application/ld+json" not in c:
        errors.append(f"missing structured data: {url}")
    if '"@type":"Article"' in c or '"@type": "Article"' in c:
        dm=re.findall(r'"dateModified"\s*:\s*"([0-9]{4}-[0-9]{2}-[0-9]{2})"',c)
        if not dm:
            errors.append(f"Article missing dateModified: {url}")
        else:
            try:
                age=(date.today()-date.fromisoformat(max(dm))).days
                if age>330:
                    errors.append(f"Article review older than 330 days ({age}): {url}")
            except ValueError:
                errors.append(f"Invalid dateModified: {url}")

# Utility routes should not enter the sitemap.
for p in ("focus","app","thank-you","offline","welcome"):
    if any(urlparse(u).path.rstrip("/")=="/"+p for u in locs):
        errors.append(f"utility route leaked into sitemap: /{p}")

if errors:
    print("SEO QUALITY GATE FAILED")
    for e in errors: print(" -",e)
    sys.exit(1)
print(f"SEO quality gate passed: {len(locs)} canonical sitemap URLs checked.")
