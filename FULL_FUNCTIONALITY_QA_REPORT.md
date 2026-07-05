# ADHDclearfocus Full Functionality QA Report

Generated locally. Passed 61/61 checks.

- [x] page:index.html — 2546 visible chars / 17850 html chars
- [x] js:index.html:0
- [x] page:assessment.html — dynamic static-JS assessment page; 363 visible fallback chars / 48463 html chars; full 39-question content present in embedded data
- [x] js:assessment.html:1
- [x] js:assessment.html:2
- [x] js:assessment.html:3
- [x] page:resources.html — 12719 visible chars / 31676 html chars
- [x] js:resources.html:1
- [x] js:resources.html:3
- [x] js:resources.html:4
- [x] page:strategies.html — 49348 visible chars / 99541 html chars
- [x] js:strategies.html:1
- [x] js:strategies.html:3
- [x] js:strategies.html:4
- [x] page:workplace.html — 2568 visible chars / 15942 html chars
- [x] js:workplace.html:1
- [x] js:workplace.html:2
- [x] page:pricing.html — 1658 visible chars / 6281 html chars
- [x] js:pricing.html:1
- [x] page:app.html — 3131 visible chars / 47798 html chars
- [x] js:app.html:1
- [x] js:app.html:4
- [x] page:community.html — 1527 visible chars / 31399 html chars
- [x] js:community.html:1
- [x] js:community.html:4
- [x] page:focus.html — 1812 visible chars / 35141 html chars
- [x] js:focus.html:1
- [x] js:focus.html:3
- [x] page:crisis.html — 3797 visible chars / 24305 html chars
- [x] js:crisis.html:1
- [x] js:crisis.html:3
- [x] page:legal.html — 2417 visible chars / 5515 html chars
- [x] js:legal.html:1
- [x] page:thank-you.html — 2242 visible chars / 13182 html chars
- [x] js:thank-you.html:1
- [x] js:thank-you.html:3
- [x] assessment:39_questions — id count 39
- [x] assessment:10_domains_present
- [x] assessment:gp_summary_present
- [x] assessment:workplace_present
- [x] assessment:paid_report_metadata_endpoint
- [x] assessment:no_generic_report_payment_link
- [x] assessment:checkout_failure_no_payment
- [x] checkout:metadata_source
- [x] checkout:uses_urlencode
- [x] checkout:cancel_assessment
- [x] webhook:signature_verification
- [x] webhook:metadata_gate
- [x] webhook:sendgrid_required_for_paid_delivery
- [x] webhook:pdf_generation
- [x] vercel:route:/api/create-checkout — /api/create-checkout.py
- [x] vercel:route:/api/webhook — /api/webhook.py
- [x] vercel:route:/api/employer-lead — /api/employer-lead.py
- [x] vercel:route:/api/health — /api/health.py
- [x] vercel:no_invalid_runtime
- [x] python:version_file — 3.12
- [x] requirements:reportlab
- [x] email:no_old_outlook
- [x] email:focusedcare_present
- [x] python:api_compile
- [x] pdf:report_generation_smoke — 59203 bytes

## What cannot be proven locally
- I can validate code paths, metadata flow, Python compilation, PDF generation, and static page integrity locally.
- I cannot run a live paid Stripe transaction or SendGrid delivery without your live/test Stripe keys, SendGrid sender verification, and Vercel environment variables being present in production.
- Use `/api/health` after deployment to check whether required variables are present. It does not expose secret values.

## Payment safety changes made
- The generic PDF report Stripe Payment Link fallback has been removed from the assessment. That fallback could take payment without assessment metadata.
- The PDF report button now only redirects after `/api/create-checkout` returns a Stripe Checkout Session containing all 10 domain scores.
- The webhook now fulfils only sessions with `metadata[source]=adhdclearfocus_screener` and ignores unrelated Stripe products such as review calls.
- SendGrid failure now makes the webhook fail, so Stripe can retry rather than silently accepting payment without delivery.