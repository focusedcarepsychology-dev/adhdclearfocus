"""ADHDclearfocus dynamic Open Graph image generator.
GET /api/og?slug=adult-adhd
Returns a lightweight 1200x630 PNG using only the Python standard library.
"""
import struct
import zlib
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

W, H = 1200, 630
BG = (10, 22, 40)
BG2 = (15, 40, 71)
TEAL = (0, 212, 221)
WHITE = (255, 255, 255)
MUTED = (177, 201, 220)
AMBER = (255, 179, 71)

TITLES = {
    "home": ("FREE ADHD SELF-ASSESSMENT", "EVIDENCE-LED TOOLS AND GUIDES"),
    "guides": ("EVIDENCE-LED ADHD GUIDES", "CLEAR ANSWERS. SOURCES INCLUDED."),
    "adhd-screening-test": ("ADHD SCREENING TESTS", "WHAT A SCREENER CAN AND CANNOT TELL YOU"),
    "adhd-assessment-ireland": ("ADHD ASSESSMENT IRELAND", "WHAT A PROPER ASSESSMENT LOOKS FOR"),
    "adhd-assessment-uk": ("ADHD ASSESSMENT UK", "WHAT NICE SAYS DIAGNOSIS REQUIRES"),
    "adhd-in-women": ("ADHD IN WOMEN", "WHY RECOGNITION CAN COME LATER"),
    "adhd-at-work": ("ADHD AT WORK", "PERFORMANCE, SAFETY AND PRACTICAL SUPPORT"),
    "workplace": ("ADHD WORKPLACE SUPPORT", "TRAINING FOR IRELAND AND THE UK"),
    "adhd-paralysis": ("ADHD PARALYSIS", "WHEN KNOWING WHAT TO DO IS NOT ENOUGH"),
    "adhd-time-blindness": ("ADHD TIME BLINDNESS", "MAKE INVISIBLE TIME MORE VISIBLE"),
    "adhd-procrastination": ("ADHD PROCRASTINATION", "DELAY IS NOT ALWAYS A MOTIVATION PROBLEM"),
    "adhd-executive-dysfunction": ("ADHD EXECUTIVE DYSFUNCTION", "WHEN THE PLAN EXISTS BUT ACTION STALLS"),
    "adhd-emotional-dysregulation": ("ADHD & EMOTIONAL REGULATION", "INTENSE FEELINGS, CLEARER EVIDENCE"),
    "adhd-rejection-sensitivity": ("ADHD & REJECTION SENSITIVITY", "VALIDATE THE EXPERIENCE WITHOUT OVERSTATING RSD"),
    "adhd-autism-overlap": ("ADHD & AUTISM OVERLAP", "WHEN BOTH PATTERNS MAY BE PRESENT"),
    "adhd-relationships": ("ADHD & RELATIONSHIPS", "UNDERSTAND THE PATTERN BEFORE BLAME"),
    "late-adhd-diagnosis": ("LATE ADHD DIAGNOSIS", "LATE RECOGNITION DOES NOT MEAN LATE ONSET"),
    "adhd-hyperfocus": ("ADHD HYPERFOCUS", "REAL EXPERIENCE, COMPLICATED EVIDENCE"),
    "adhd-and-sleep": ("ADHD & SLEEP", "WHEN THE DAY DOES NOT SWITCH OFF CLEANLY"),
    "adhd-medication-evidence": ("ADHD MEDICATION", "WHAT THE EVIDENCE SAYS"),
    "cbt-for-adhd": ("CBT FOR ADHD", "SKILLS FOR ORGANISATION AND FOLLOW-THROUGH"),
    "exercise-and-adhd": ("EXERCISE & ADHD", "USEFUL ADJUNCT, NOT A MIRACLE TREATMENT"),
    "adhd-body-doubling": ("ADHD BODY DOUBLING", "BORROWED STRUCTURE FOR DIFFICULT STARTS"),
    "adhd-focus-timer": ("FREE ADHD FOCUS TIMER", "START, FOCUS AND RESTART"),
    "adhd-workplace-adjustments": ("ADHD WORKPLACE ADJUSTMENTS", "CHANGE THE SYSTEM, NOT THE PERSON"),
    "adult-adhd": ("ADULT ADHD", "LOOK FOR THE PATTERN, NOT A STEREOTYPE"),
    "adhd-or-anxiety": ("ADHD OR ANXIETY?", "HOW THE PATTERNS CAN OVERLAP"),
    "assessment": ("FREE ADHD SELF-ASSESSMENT", "39 QUESTIONS ACROSS 10 ADHD-RELATED AREAS"),
    "strategies": ("ADHD COPING STRATEGIES", "PRACTICAL EVIDENCE-INFORMED TOOLS"),
    "resources": ("ADHD RESEARCH EXPLAINED", "PLAIN ENGLISH. ORIGINAL SOURCES. CLEAR CAVEATS."),
    "insights": ("ADHD QUESTIONS ANSWERED", "EVIDENCE-LED EXPLANATIONS WITHOUT HYPE"),
    "ie": ("ADHDCLEARFOCUS IRELAND", "ADHD TOOLS, GUIDES AND WORKPLACE SUPPORT"),
    "uk": ("ADHDCLEARFOCUS UK", "ADHD TOOLS, GUIDES AND WORKPLACE SUPPORT"),
    "about": ("ABOUT ADHDCLEARFOCUS", "EDUCATIONAL ADHD TOOLS WITH CLEAR CLINICAL BOUNDARIES"),
    "methodology": ("HOW THE SELF-ASSESSMENT WORKS", "WHAT IT CAN AND CANNOT TELL YOU"),
    "editorial-policy": ("EDITORIAL POLICY", "EVIDENCE, REVIEW, CORRECTIONS AND TRANSPARENCY"),
    "pricing": ("ADHDCLEARFOCUS PRICING", "FREE TOOLS WITH OPTIONAL REPORTS AND SUPPORT"),
    "community": ("ADHD COMMUNITY", "QUESTIONS, EXPERIENCES AND PEER SUPPORT"),
    "crisis": ("ADHD CRISIS MODE", "GROUNDING TOOLS AND SUPPORT SIGNPOSTING"),
    "employers-adhd-awareness-training": ("ADHD AWARENESS TRAINING", "PRACTICAL EDUCATION FOR WORKPLACES"),
    "employers-adhd-manager-training": ("ADHD MANAGER TRAINING", "CLEARER PRIORITIES, FEEDBACK AND SUPPORT"),
    "employers-adhd-workplace-adjustments": ("ADHD WORKPLACE ADJUSTMENTS", "PRACTICAL CHANGES FOR EMPLOYERS"),
    "employers-neurodiversity-training-ireland": ("NEURODIVERSITY TRAINING IRELAND", "ADHD-AWARE EDUCATION FOR EMPLOYERS"),
    "employers-neurodiversity-training-uk": ("NEURODIVERSITY TRAINING UK", "ADHD-AWARE EDUCATION FOR EMPLOYERS"),
}

# 5x7 uppercase pixel font.
FONT = {
"A":["01110","10001","10001","11111","10001","10001","10001"],"B":["11110","10001","10001","11110","10001","10001","11110"],
"C":["01111","10000","10000","10000","10000","10000","01111"],"D":["11110","10001","10001","10001","10001","10001","11110"],
"E":["11111","10000","10000","11110","10000","10000","11111"],"F":["11111","10000","10000","11110","10000","10000","10000"],
"G":["01111","10000","10000","10111","10001","10001","01111"],"H":["10001","10001","10001","11111","10001","10001","10001"],
"I":["11111","00100","00100","00100","00100","00100","11111"],"J":["00111","00010","00010","00010","10010","10010","01100"],
"K":["10001","10010","10100","11000","10100","10010","10001"],"L":["10000","10000","10000","10000","10000","10000","11111"],
"M":["10001","11011","10101","10101","10001","10001","10001"],"N":["10001","11001","10101","10011","10001","10001","10001"],
"O":["01110","10001","10001","10001","10001","10001","01110"],"P":["11110","10001","10001","11110","10000","10000","10000"],
"Q":["01110","10001","10001","10001","10101","10010","01101"],"R":["11110","10001","10001","11110","10100","10010","10001"],
"S":["01111","10000","10000","01110","00001","00001","11110"],"T":["11111","00100","00100","00100","00100","00100","00100"],
"U":["10001","10001","10001","10001","10001","10001","01110"],"V":["10001","10001","10001","10001","10001","01010","00100"],
"W":["10001","10001","10001","10101","10101","11011","10001"],"X":["10001","10001","01010","00100","01010","10001","10001"],
"Y":["10001","10001","01010","00100","00100","00100","00100"],"Z":["11111","00001","00010","00100","01000","10000","11111"],
"0":["01110","10001","10011","10101","11001","10001","01110"],"1":["00100","01100","00100","00100","00100","00100","01110"],
"2":["01110","10001","00001","00010","00100","01000","11111"],"3":["11110","00001","00001","01110","00001","00001","11110"],
"4":["00010","00110","01010","10010","11111","00010","00010"],"5":["11111","10000","10000","11110","00001","00001","11110"],
"6":["01110","10000","10000","11110","10001","10001","01110"],"7":["11111","00001","00010","00100","01000","01000","01000"],
"8":["01110","10001","10001","01110","10001","10001","01110"],"9":["01110","10001","10001","01111","00001","00001","01110"],
" ":["00000"]*7,"-":["00000","00000","00000","11111","00000","00000","00000"],"&":["01100","10010","10100","01000","10101","10010","01101"],
".":["00000","00000","00000","00000","00000","01100","01100"],",":["00000","00000","00000","00000","00110","00110","00100"],"'":["00100","00100","00000","00000","00000","00000","00000"],
"?":["01110","10001","00001","00010","00100","00000","00100"],":":["00000","01100","01100","00000","01100","01100","00000"],
}

def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i+3] = bytes(color)

def rect(buf, x0, y0, x1, y1, color):
    x0=max(0,x0); y0=max(0,y0); x1=min(W,x1); y1=min(H,y1)
    row=bytes(color) * max(0, x1-x0)
    for y in range(y0,y1):
        i=(y*W+x0)*3
        buf[i:i+len(row)]=row

def text(buf, s, x, y, scale, color, max_chars=None):
    s = s.upper()
    if max_chars and len(s) > max_chars: s=s[:max_chars]
    cx=x
    for ch in s:
        glyph=FONT.get(ch, FONT[" "])
        for gy,row in enumerate(glyph):
            for gx,v in enumerate(row):
                if v=="1": rect(buf,cx+gx*scale,y+gy*scale,cx+(gx+1)*scale,y+(gy+1)*scale,color)
        cx += 6*scale

def wrap_words(s, chars=28):
    words=s.split()
    lines=[]; cur=[]
    for w in words:
        if len(" ".join(cur+[w]))>chars and cur:
            lines.append(" ".join(cur)); cur=[w]
        else: cur.append(w)
    if cur: lines.append(" ".join(cur))
    return lines[:3]

def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag+data)&0xffffffff)

def png_bytes(slug):
    title, subtitle = TITLES.get(slug, TITLES["guides"])
    buf=bytearray(W*H*3)
    # subtle horizontal gradient
    for x in range(W):
        t=x/(W-1)
        col=(int(BG[0]*(1-t)+BG2[0]*t),int(BG[1]*(1-t)+BG2[1]*t),int(BG[2]*(1-t)+BG2[2]*t))
        rect(buf,x,0,x+1,H,col)
    rect(buf,0,0,18,H,TEAL)
    rect(buf,70,70,480,82,TEAL)
    # decorative blocks
    rect(buf,930,55,1130,255,(14,90,104))
    rect(buf,1010,330,1199,600,(43,37,94))
    text(buf,"ADHDCLEARFOCUS",70,105,6,TEAL)
    y=210
    for line in wrap_words(title,26):
        text(buf,line,70,y,10,WHITE); y+=92
    for line in wrap_words(subtitle,44):
        text(buf,line,72,500,4,MUTED); break
    text(buf,"ADHDCLEARFOCUS.COM",72,565,4,(6,16,31))
    rect(buf,65,555,470,608,TEAL)
    text(buf,"ADHDCLEARFOCUS.COM",85,568,4,(6,16,31))
    raw=b"".join(b"\x00"+bytes(buf[y*W*3:(y+1)*W*3]) for y in range(H))
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",W,H,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            q=parse_qs(urlparse(self.path).query)
            slug=(q.get("slug") or ["guides"])[0]
            if slug not in TITLES: slug="guides"
            body=png_bytes(slug)
            self.send_response(200)
            self.send_header("Content-Type","image/png")
            self.send_header("Cache-Control","public, max-age=86400, s-maxage=604800")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.send_response(500); self.end_headers()
