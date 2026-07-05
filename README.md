# ADHDclearfocus v2 upload package

This package keeps the required architecture: flat HTML pages, React 18 + Babel only inside `index.html`, and Python serverless functions in `/api` using stdlib except `reportlab` for PDF generation.

## What changed

- Normalised the Vercel project structure.
- Moved Python functions into `/api`.
- Removed duplicated/misnamed server files from the upload package.
- Added missing production pages: `strategies.html`, `resources.html`, `pricing.html`, `workplace.html`, `legal.html`, `thank-you.html`, `offline.html`.
- Added `manifest.json`, `sw.js`, `robots.txt`, `sitemap.xml`, `vercel.json`, app icons and shared brand assets.
- Added a shared no-build design layer: `/assets/brand.css`.
- Added shared no-build UX helpers: `/assets/ux.js`.
- Fixed the Stripe checkout function so it URL-encodes metadata properly and returns safe errors.
- Rebuilt Mailchimp proxy to fail gracefully if not configured.
- Added server-side community and focus-room proxies so JSONBin keys are not exposed in the browser.
- Updated public domain references to `adhdclearfocus.ie`.
- Added basic security headers and cache rules.

## Upload to Vercel

Upload the **contents** of this folder to the GitHub repository root, not the folder itself.

Required minimum files at the repository root:

- `.python-version`
- `vercel.json`
- `requirements.txt`
- `index.html`
- `/api/*.py`
- `/assets/*`
- `manifest.json`
- `sw.js`

## Required environment variables

Minimum for core paid report flow:

- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL` optional, defaults to `hello@adhdclearfocus.ie`
- `ADMIN_EMAIL` optional, defaults to the legal contact email
- `ANTHROPIC_API_KEY`
- `DOMAIN=https://adhdclearfocus.ie`

For accounts:

- `AUTH_BIN_ID`
- `AUTH_BIN_KEY`
- `AUTH_SECRET`

For community:

- `COMMUNITY_BIN_ID`
- `COMMUNITY_BIN_KEY`

For focus rooms:

- `FOCUS_BIN_KEY` or `JSONBIN_MASTER_KEY`

For Mailchimp:

- `MAILCHIMP_API_KEY`
- `MAILCHIMP_LIST_ID`
- `MAILCHIMP_SERVER` optional; auto-derived from the key where possible.

## Critical security action

A JSONBin master key was previously embedded in the client-side HTML. Rotate that key in JSONBin before deploying this version. Treat it as public.

## Testing after deployment

1. Open `/` and complete the screener.
2. Confirm fallback Stripe Payment Link opens if `/api/create-checkout` is not configured.
3. Configure Stripe env vars and confirm Checkout Session redirects.
4. In Stripe, send a test `checkout.session.completed` webhook to `/api/webhook`.
5. Confirm SendGrid delivers the PDF report.
6. Create an account from `/community.html` and check `/api/auth`.
7. Create a community post and confirm the browser does not contain JSONBin keys.
8. Open `/focus.html` on two devices and test room sync.
9. Check `/legal.html`, `/sitemap.xml`, `/manifest.json` and offline mode.



## Final full-feature locked package

This package has been checked against the old working backend files uploaded after the v2 reconciliation. The legacy Stripe checkout, webhook, AI report generation, SendGrid delivery, Mailchimp capture and ReportLab PDF generation are preserved. See `LEGACY_FEATURE_AUDIT.md` for details.
