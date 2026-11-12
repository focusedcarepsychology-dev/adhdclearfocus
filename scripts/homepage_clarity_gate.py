#!/usr/bin/env python3
"""Zero-dependency accessibility, copy, funnel and SEO regression gate for the public homepage."""
from html.parser import HTMLParser
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"index.html").read_text(encoding="utf-8")
errors=[]

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.start={}
        self.links=set()
        self.meta={}
        self.forms=0
        self.inputs=[]
        self.scripts=[]
        self.ids=set()
    def handle_starttag(self,tag,attrs):
        d=dict(attrs); self.start[tag]=self.start.get(tag,0)+1
        if tag=="a" and "href" in d: self.links.add(d["href"])
        if tag=="meta": self.meta[d.get("name") or d.get("property")]=d.get("content","")
        if tag=="input":self.inputs.append(d)
        if tag=="form":self.forms+=1
        if tag=="script":self.scripts.append(d.get("src",""))
        if "id" in d:
            if d["id"] in self.ids:errors.append("duplicate HTML id: "+d["id"])
            self.ids.add(d["id"])

p=Tags()
try: p.feed(html)
except Exception as e:errors.append("HTML parse failed: "+str(e))

def require(ok,message):
    if not ok:errors.append(message)
require(p.start.get("h1")==1,"exactly one visible H1 is required")
require(p.start.get("main")==1,"exactly one main landmark is required")
require(p.start.get("nav",0)>=2,"desktop and accessible mobile navigation required")
require(p.start.get("details",0)>=1 and p.start.get("summary",0)>=1,"keyboard accessible mobile menu required")
require(p.meta.get("description","").startswith("Free ADHD education"),"clear meta description missing")
require("ADHDclearfocus | Free ADHD Tools" in html,"homepage SEO title mismatch")
require("ADHDclearfocus is a free ADHD education and self-help platform" in html,"explicit platform explanation missing")
require("not a validated diagnostic assessment" in html,"non-diagnostic limits missing")
require("39-question self-reflection" in html,"free self-reflection description missing")
require("no diagnosis claims" in html.lower(),"non-diagnostic CTA context missing")
for route in ("/assessment","/strategies","/guides","/adhd-focus-timer","/methodology","/resources","/about","/ie","/uk","/crisis","/editorial-policy"):
    require(route in p.links,"missing key user pathway: "+route)
require("https://focusedcarepsychology.org/" in p.links,"clinical / educational separation link missing")
require("https://www.adhdclearfocus.com/" in html,"homepage canonical missing")
require("name=\"consent\" required" in html and "data-seo-newsletter" in html,"explicit newsletter opt-in missing")
require(any(x.get("type")=="email" and "required" in x for x in p.inputs),"required email input missing")
require(any(x.get("name")=="consent" and "required" in x for x in p.inputs),"required opt-in missing")
require("/assets/seo.js" in p.scripts,"newsletter handler missing")
require("@media(max-width:800px)" in html and "@media(max-width:560px)" in html,"mobile breakpoints missing")
require("prefers-reduced-motion:reduce" in html and ":focus-visible" in html,"basic motion / focus accessibility missing")
require('href="#main-content"' in html and "main-content" in p.ids,"skip navigation missing")
require("116 123" in html,"crisis signpost missing")
require("74%" not in html and "82%" not in html,"unsupported illustrative risk-score percentages remain")
require("fonts.googleapis.com" not in html,"unnecessary external font dependency")
require("https://www.adhdclearfocus.com/" in (ROOT/"sitemap.xml").read_text(encoding="utf-8"),"homepage absent from sitemap")
for path in ("assessment.html","strategies.html","guides.html","adhd-focus-timer.html","methodology.html","about.html","ie.html","uk.html","crisis.html","editorial-policy.html"):
    require((ROOT/path).exists(),"linked public feature source missing: "+path)
if errors:
    print("HOMEPAGE QUALITY GATE FAILED")
    for item in errors:print(" -",item)
    sys.exit(1)
print("HOMEPAGE QUALITY GATE PASSED: content, SEO, navigation, consent, routes and accessibility markers verified")
