# ADHDclearfocus — Paid PDF Report Delivery Fix

## Problem found

The assessment previously had a generic Stripe Payment Link fallback for the PDF report. That is unsafe for a personalised report because a generic link can take payment without the 10-domain assessment metadata needed by the webhook to generate the correct PDF.

## Fix made

The PDF report purchase path now works only like this:

1. User completes the 39-question assessment.
2. User enters email after the results.
3. Browser sends email, total score, ASRS flag and all 10 domain percentages to `/api/create-checkout`.
4. `/api/create-checkout` creates a Stripe Checkout Session with the metadata attached.
5. User pays on Stripe.
6. Stripe sends `checkout.session.completed` to `/api/webhook`.
7. `/api/webhook` verifies the Stripe signature, checks `metadata[source]=adhdclearfocus_screener`, builds the PDF, emails it to the customer via SendGrid, and sends an admin notification.

## What happens if checkout is not configured

No payment is taken. The page shows an error telling the user to email `focusedcarepsychology@gmail.com`.

## What happens if SendGrid fails after payment

The webhook now returns an error instead of silently succeeding. Stripe will retry the webhook. This is safer because a delivery failure is visible and recoverable.

## What is still separate

The optional review call remains a separate Stripe Payment Link. The report webhook ignores that payment because it does not have `metadata[source]=adhdclearfocus_screener`.

## Required environment variables

For paid PDF delivery:

- `DOMAIN=https://www.adhdclearfocus.com`
- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL=focusedcarepsychology@gmail.com`
- `ADMIN_EMAIL=focusedcarepsychology@gmail.com`

Optional:

- `ANTHROPIC_API_KEY` for AI-personalised narrative. If missing, the report still generates using built-in evidence-based content.

## Post-deploy checks

1. Visit `/api/health`.
2. Confirm `ok_for_paid_report` is `true`.
3. Complete the assessment.
4. Use Stripe test mode first.
5. Confirm the customer receives the PDF attachment.
6. Confirm the admin notification arrives.
