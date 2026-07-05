# ADHDclearfocus v2 — Legacy Feature Audit & Final Merge Notes

Generated: 2026-07-05 12:09 UTC

## Result

The latest old backend files were checked against the v2 reconciled package. No working legacy feature was missing from the new package. The old features are preserved, but the v2 versions are safer and cleaner.

## What was preserved from the old working site

| Feature | Status in this package |
|---|---|
| Stripe checkout session creation | Preserved and improved in `api/create-checkout.py`. Still attaches the screener metadata used by the webhook. Also adds URL encoding, validation, promotion-code support, `.ie` domain defaults and safe failure handling. |
| 10-dimension metadata transfer | Preserved. All 10 percentages are still sent: inattention, hyperactivity, executive, emotional, working memory, time, hyperfocus, RSD, developmental and impact. |
| 14-page PDF report generation | Preserved exactly in `api/generate_report.py`. The uploaded old `generate_report(3).py` and packaged version match in size and content. |
| Evidence-based clinical content | Preserved in the report generator and public strategy/resource pages. |
| Stripe webhook payment flow | Preserved and improved in `api/webhook.py`. It still generates the report, requests AI narrative, sends the PDF by SendGrid, creates the loyalty code, and notifies admin. |
| AI report analysis | Preserved. Anthropic call retained with JSON narrative output. |
| SendGrid PDF delivery | Preserved. Email includes profile summary, 10-domain bars, PDF attachment and loyalty-code section. |
| Admin notification | Preserved. |
| Mailchimp email capture | Preserved and improved in `api/mailchimp-subscribe.py`. It now uses upsert-style subscription and degrades gracefully if Mailchimp is not configured. |
| ReportLab dependency | Preserved in `requirements.txt`. |
| Python 3.12 runtime | Preserved via `.python-version` and Vercel config. |

## Old files checked

- `create-checkout(3).py` — Stripe checkout metadata; 3,701 bytes; sha256 prefix `54bd018bd216`.
- `generate_report(3).py` — 14-page ReportLab PDF report; 92,602 bytes; sha256 prefix `0dad4dd3d78d`.
- `mailchimp-subscribe(2).py` — Mailchimp subscribe proxy; 2,553 bytes; sha256 prefix `c18fa29bd9ac`.
- `webhook(1).py` — Stripe webhook + AI analysis + SendGrid report delivery; 13,648 bytes; sha256 prefix `a8dbf095b1ee`.
- `requirements(2).txt` — ReportLab dependency; 17 bytes; sha256 prefix `bae2b1046a11`.


## Packaged backend files

- `api/create-checkout.py` — 4,465 bytes; sha256 prefix `91a48323a5a7`.
- `api/generate_report.py` — 92,602 bytes; sha256 prefix `0dad4dd3d78d`.
- `api/mailchimp-subscribe.py` — 3,617 bytes; sha256 prefix `23a19a6eda3c`.
- `api/webhook.py` — 15,274 bytes; sha256 prefix `ff3c14bcd502`.
- `requirements.txt` — 17 bytes; sha256 prefix `bae2b1046a11`.

## Files deliberately not included

The uploaded `.pyc` files were not included. They are compiled local cache files and should not be uploaded to Vercel or GitHub.

## Important deployment notes

1. Upload the contents of this folder to the GitHub repository root, not the folder itself.
2. Make sure hidden files are visible so `.python-version` uploads.
3. In Vercel, set the environment variables listed in `DEPLOYMENT_CHECKLIST.md`.
4. Rotate any old JSONBin master key that was previously exposed in browser code.
5. Use `STRIPE_WEBHOOK_SECRET` once the Stripe webhook endpoint is configured. The webhook will still accept events without it, but production should use the secret.
