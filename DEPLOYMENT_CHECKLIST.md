# ADHDclearfocus deployment checklist

## Before upload

- [ ] Rotate the exposed JSONBin key that was previously in client HTML.
- [ ] Confirm `.python-version` exists and contains `3.12`.
- [ ] Confirm `generate_report.py` is inside `/api` and is the large ReportLab file.
- [ ] Confirm `create-checkout.py` is the Stripe file, not the old Mailchimp duplicate.
- [ ] Confirm `vercel.json` is at the root.
- [ ] Confirm no secrets are present in `.html`, `.js`, or committed docs.

## Vercel environment variables

- [ ] `DOMAIN=https://adhdclearfocus.ie`
- [ ] `STRIPE_SECRET_KEY`
- [ ] `STRIPE_PRICE_ID`
- [ ] `STRIPE_WEBHOOK_SECRET`
- [ ] `SENDGRID_API_KEY`
- [ ] `SENDGRID_FROM_EMAIL`
- [ ] `ADMIN_EMAIL`
- [ ] `ANTHROPIC_API_KEY`
- [ ] `MAILCHIMP_API_KEY`
- [ ] `MAILCHIMP_LIST_ID`
- [ ] `AUTH_BIN_ID`
- [ ] `AUTH_BIN_KEY`
- [ ] `AUTH_SECRET`
- [ ] `COMMUNITY_BIN_ID`
- [ ] `COMMUNITY_BIN_KEY`
- [ ] `FOCUS_BIN_KEY`

## Stripe

- [ ] Webhook endpoint points to `https://adhdclearfocus.ie/api/webhook`.
- [ ] Event enabled: `checkout.session.completed`.
- [ ] Test mode works before live mode.
- [ ] Price ID matches the €49 report product.
- [ ] Static Payment Link fallback still works.

## Email

- [ ] SendGrid sender identity verified.
- [ ] SPF/DKIM configured for the sending domain.
- [ ] Test report email is received.
- [ ] Spam/promotions folder checked.

## Final browser checks

- [ ] Mobile homepage.
- [ ] Desktop homepage.
- [ ] Assessment completion.
- [ ] Checkout flow.
- [ ] Thank-you page.
- [ ] Dashboard/app page.
- [ ] Crisis Mode.
- [ ] Focus Room.
- [ ] Community post/reply.
- [ ] Strategies page.
- [ ] Resources page.
- [ ] Pricing page.
- [ ] Workplace page.
- [ ] Legal page.
- [ ] Offline page after first load.



## Vercel runtime fix

If Vercel says `Function Runtimes must have a valid version`, make sure `vercel.json` does **not** contain `"runtime": "python3.12"`. This package has already removed it; Vercel will auto-detect Python from the `.py` files and `.python-version`.
