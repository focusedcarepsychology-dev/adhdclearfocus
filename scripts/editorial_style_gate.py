#!/usr/bin/env python3
"""Regression check for the shared ADHDclearfocus educational editorial design."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
errors = []
css = (ROOT/'assets/seo.css').read_text(encoding='utf-8')

for marker in ('--bg:#f8faf8', '--text:#172a3c', '.hero{', '.answer{',
               '.newsletter-consent{', ':focus-visible', 'prefers-reduced-motion',
               '@media(max-width:700px)', '.related-guides'):
    if marker not in css:
        errors.append('Missing editorial style or accessibility rule: ' + marker)

# The shared CSS must only affect evidence/guide pages: don't override the
# independent questionnaire, timer, crisis-mode or employer app CSS.
for page in ('guides.html','about.html','methodology.html','editorial-policy.html',
             'ie.html','uk.html','adhd-paralysis.html','adhd-in-women.html'):
    body = (ROOT/page).read_text(encoding='utf-8')
    if '/assets/seo.css' not in body:
        errors.append(page + ': missing shared editorial stylesheet')
    if 'rel="canonical"' not in body:
        errors.append(page + ': missing canonical')
    if '<h1' not in body:
        errors.append(page + ': missing H1')

for page in ('assessment.html','adhd-focus-timer.html','crisis.html'):
    body = (ROOT/page).read_text(encoding='utf-8')
    if '/assets/seo.css' in body:
        errors.append(page + ': unintended new dependence on editorial CSS')

if errors:
    print('EDITORIAL STYLESHEET QUALITY GATE FAILED')
    print('\n'.join(' - '+msg for msg in errors))
    sys.exit(1)
print('EDITORIAL STYLESHEET QUALITY GATE PASSED')
