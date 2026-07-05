# ADHDclearfocus — Project Brief (Single Source of Truth)

**Version:** 2 July 2026 · **Owner:** Focused Care Psychology Limited (FCP Ltd), Waterford, Ireland
**Purpose of this document:** Upload this to the Claude Project so every new conversation starts with full context. If any future build contradicts this document, this document wins unless the owner explicitly changes it.

---

## 1. What ADHDclearfocus is

An **educational** ADHD self-awareness and productivity platform at **adhdclearfocus.com**. It is explicitly **not** a clinical service, does not diagnose, and does not create a clinical relationship (this keeps it outside EU MDR classification). All public copy must preserve this framing.

**Attribution rules (non-negotiable):**
- **No personal name appears anywhere as the creator/author of the platform.** Reports say "Prepared by the ADHDclearfocus clinical team". Site copy says "developed by the ADHDclearfocus clinical team" / "Built by experts".
- The **only** permitted personal surfaces are: (a) the Psychology Today profile link (https://www.psychologytoday.com/ie/counselling/conall-donegan-waterford-wd/1437075), framed as *"if your results raise concerns, speak to a chartered psychologist — free 15-minute consultation"*, shown **after** the screener and on support sections — never as "the person who built this site"; and (b) the legal/privacy contact email focusedcarepsychology@gmail.com on legal.html and support copy.
- The book **The Gratitude Prescription** is advertised as "written by a DPsych psychologist with 17 years of clinical experience" — no name, links to Amazon: https://www.amazon.co.uk/Gratitude-Prescription-Doctors-Program-Seconds/dp/B0GPBYKYYL

## 2. Architecture (DO NOT CHANGE — this has been rebuilt wrongly multiple times)

- **Flat HTML, one file per page. No build step. No Vite, no Next, no TypeScript, no Supabase.** Any AI that proposes a framework rebuild is wrong — reject it.
- React 18 **via CDN** + Babel standalone, used only inside index.html (the screener app).
- Serverless functions in **/api** as **Python using stdlib only** (urllib, json — **no pip SDKs**). `.python-version` file must be present (it is hidden — enable "show hidden files" before uploading).
- `vercel.json` present and valid. Deployed on **Vercel**, repo: focusedcarepsychology-dev/adhdclearfocus, project adhdclearfocus-g7cu, domain adhdclearfocus.com.
- Integrations: Stripe Payment Links, SendGrid (email), Anthropic API (claude-haiku-4-5-20251001) for report generation, Mailchimp (list capture), JSONBin.io (community forum storage, BIN_ID 6a38525eda38895dfee84b8a), GA4 (G-R8CLJRBNM0) + Vercel Analytics via script tag on **all pages**.
- **Known deployment failure mode:** changes "not showing" has always been caused by incomplete GitHub uploads (files not fully replacing old ones, or hidden `.python-version` not copied) — never by Vercel itself. Follow UPLOAD_INSTRUCTIONS.txt in the zip exactly.

## 3. Page inventory (12 pages)

| Page | What it does |
|---|---|
| index.html | Landing + full **39-question screener** (10 neurological dimensions; ASRS-v1.1, Brown, DIVA-5, Barkley frameworks; adult/teen branching), consent flow, paywall, email capture, Pro founding CTA, Psychology Today card, book card |
| app.html | Member dashboard: greeting, **7-day free trial banner**, streak, mood check-in with evidence-based responses, quick links (Crisis, Focus, Strategies, **Insights**) |
| insights.html | **Blog — "ADHD Insights"**: 4 fully-cited articles (prevalence/Song 2021; ASRS-v1.1 vs ASRS-5; exercise; late diagnosis), each with screener CTA + analytics events, plus book promo, Pro promo, Psychology Today support card |
| strategies.html | 47 evidence-based strategies incl. gratitude journaling section advertising the book |
| resources.html | Research library; includes book card and Psychology Today link |
| community.html | Forum (JSONBin cloud + localStorage fallback, seed posts, tags, likes, replies) |
| focus.html | Real body-doubling focus room (BroadcastChannel) + Pomodoro |
| crisis.html | Crisis mode: breathing, grounding, binaural tones; Samaritans 116 123 everywhere |
| pricing.html | Plans, comparison table, FAQ |
| thank-you.html | Post-purchase, €79 review-call upsell |
| welcome.html / legal.html | Onboarding / GDPR (Art. 9 consent), terms, Consumer Rights Act 2022 withdrawal terms |

## 4. Business model & pricing (current, live copy)

- **€49 Clarity Report** (one-off personalised PDF, delivered by Stripe Checkout Session → webhook → SendGrid). Important: do not use a generic Stripe Payment Link for this report, because the checkout session must include the assessment metadata needed to generate the PDF. Use `STRIPE_PRICE_ID` with `/api/create-checkout`.
- **€79 30-minute review call** upsell. Stripe link: https://buy.stripe.com/14A7sL8wM0xcbzpgg9fYY00.
- **Pro — Founding Member (waitlist until launch):** **€5/month billed yearly (€60/year), regular price €10/month**, founding rate locked for life, founding window closes **31 July 2026** (JS countdown and pricing.html now aligned). **7-day free trial on launch — no credit card required** (changed from 14 days on 2 July 2026 at owner instruction; consistent across index, app, pricing, insights).
- 15% discount on formal ADHD/ASD assessments via registered clinical partners (codes generated on subscription).
- Future: €2,500 employer certification programme.
- ⚠️ **Open decision for owner:** an earlier model was €9/month founding vs €19/month regular (monthly billing). The live build uses €5/mo-yearly / €10 regular. These are different revenue models — pick one deliberately. The build is currently internally consistent on €5/€60/€10.

## 5. Pro feature set (what the 7-day trial unlocks — all evidence-linked)

Body-doubling focus rooms (BroadcastChannel, real not simulated) · evidence-led audio engine (moderate background noise leads per Söderlund 2007; binaural labelled experimental per Garcia-Argibay 2019) · crisis mode offline · 47 cited strategies · 7-day focus challenge (one cited micro-task/day) · monthly re-assessments · voice diary & AI coach · community & research library · live Q&A with clinical psychologist · 15% assessment discount.

## 6. Evidence base (verified citations used in-app)

ASRS-v1.1: Kessler et al. 2005 (Part A 68.7% sens / 99.5% spec at 4/6); Brevik et al. 2020 (AUC 0.90); ASRS-5: Ustun et al. 2017, JAMA Psychiatry (91.4% sens / 96% spec); Kessler 2023 (prefer unweighted scoring). Prevalence: Song et al. 2021, J Glob Health (6.76% symptomatic adult ADHD ≈ 366M). Faraone et al. 2021 International Consensus. Exercise: Hoza 2015; Pontifex 2013; Kooij 2019 guidelines. Also: Safren 2010, Gollwitzer 1999, Lieberman 2007, Young 2011, Alloway & Alloway 2011.

## 7. Fixed on 2 July 2026 (this build — "MERGED_FINAL")

1. **Merged the blog back in** as insights.html (it existed only in the abandoned single-file React v4/v5 track — the "back to just the screener" confusion came from two parallel builds; the flat-HTML build is the only track going forward. The v5.jsx single-file React repo is retired).
2. Trial changed **14 → 7 days**, "**no credit card required**" added everywhere the trial is mentioned.
3. Psychology Today card added to the post-screener paywall; book card added to the paywall.
4. "Developed by Dr. …" removed from the PDF report generator (both occurrences).
5. **Four pre-existing crash bugs fixed** that would have broken the site had the previous zip been deployed:
   - index.html: duplicate `daysLeft` declaration → **entire screener page rendered blank**;
   - index.html: broken ternary (`:` instead of `?`) in the results comparison text;
   - app.html: two mangled greeting ternaries → whole dashboard script died;
   - app.html: Unicode minus signs (−) in mood-score comparisons → script parse failure;
   - api/generate_report.py: `},,` syntax error → **every €49 report purchase would have failed**.
6. Copy corrected 35 → **39 questions** (meta tags, intro, consent); stray €9/month waitlist line aligned to €5/mo-yearly; founding deadline unified to 31 July 2026; sitemap unified to adhdclearfocus.com and now includes /insights.html and /app.html.
7. All 12 pages pass JS/JSX parse validation; all 4 Python functions compile; all referenced DOM ids exist.

## 8. Standing instructions for any future Claude conversation

- Improve the existing flat build; never replace the architecture.
- Verify every clinical/statistical claim against the primary source before adding it; mark anything unverified as UNVERIFIED.
- Run a hostile-reviewer pass (parse-validate every page's JS, compile every Python file, check DOM ids) **before** delivering any zip — three of the five crash bugs above shipped in a previous "ready to upload" zip.
- Keep the educational (non-clinical) framing and the no-personal-attribution rule in every new page or feature.
- Deliverables: full-site zip + updated copy of this brief whenever anything material changes.

## 9. Deployment checklist (every release)

1. Extract zip → enable hidden files → confirm `.python-version` visible.
2. Select **all** files inside flat_deploy → copy into repo root, replacing everything → commit.
3. Vercel auto-deploys; hard-refresh (Ctrl+Shift+R) and confirm: intro says **39 questions**, trial pill says **7-day / no credit card**, /insights.html loads.
4. Test one full screener run and confirm the paywall shows the Psychology Today and book cards.
