# ADHDclearfocus — Vercel environment variables, step by step

This guide assumes you know nothing about Vercel environment variables.

## What environment variables are

Environment variables are private settings stored inside Vercel. They let your site use Stripe, SendGrid, Anthropic, Mailchimp and JSONBin without putting secret API keys inside public website files.

Never paste secret keys into HTML, JavaScript, GitHub README text, or browser code.

---

## Step 1 — Open the right Vercel project

1. Go to your Vercel dashboard.
2. Click the ADHDclearfocus project.
3. Click **Settings**.
4. Click **Environment Variables**.

---

## Step 2 — Add each variable

For each variable below:

1. In **Key**, paste the variable name exactly.
2. In **Value**, paste the value.
3. Select **Production**, **Preview**, and **Development** unless you intentionally want a different test value.
4. Click **Save** or **Add**.

---

## Step 3 — Minimum variables for the paid report flow

These are needed for: assessment → Stripe checkout → payment webhook → AI analysis → PDF report → customer email → admin notification.

| Key | What to put in Value | Where to get it |
|---|---|---|
| `DOMAIN` | `https://www.adhdclearfocus.com` | Your live website domain |
| `STRIPE_SECRET_KEY` | Starts with `sk_live_` for live mode, or `sk_test_` for testing | Stripe Dashboard → Developers → API keys |
| `STRIPE_PRICE_ID` | Starts with `price_` | Stripe Dashboard → Product catalogue → your €49 report price |
| `STRIPE_WEBHOOK_SECRET` | Starts with `whsec_` | Stripe Dashboard → Developers → Webhooks → your endpoint signing secret |
| `SENDGRID_API_KEY` | Starts with `SG.` | SendGrid → Settings → API Keys |
| `SENDGRID_FROM_EMAIL` | `focusedcarepsychology@gmail.com` | Must be verified in SendGrid first |
| `ADMIN_EMAIL` | `focusedcarepsychology@gmail.com` | Where admin/payment notifications go |
| `EMPLOYER_LEADS_EMAIL` | `focusedcarepsychology@gmail.com` | Where workplace/employer enquiries go |
| `ANTHROPIC_API_KEY` | Starts with `sk-ant-` | Anthropic Console → API Keys |

Important: if `SENDGRID_FROM_EMAIL` is not verified in SendGrid, SendGrid may reject outgoing emails. Verify `focusedcarepsychology@gmail.com` as a Single Sender in SendGrid, or use a verified domain email.

---

## Step 4 — Optional variables for Mailchimp

These are needed for newsletter/waitlist/employer-lead list capture.

| Key | Value |
|---|---|
| `MAILCHIMP_API_KEY` | Your Mailchimp API key, usually ending in a server code like `-us13` |
| `MAILCHIMP_LIST_ID` | Your audience/list ID, for example `3f6c1e163c` |
| `MAILCHIMP_SERVER` | Usually `us13`; optional because the code tries to derive this from the API key |

The website still works without Mailchimp; it just will not reliably add people to the mailing list.

---

## Step 5 — Optional variables for accounts and tracker sync

These are needed only if you want login/accounts and synced tracker data.

| Key | Value |
|---|---|
| `AUTH_BIN_ID` | JSONBin bin ID containing `{ "users": {} }` |
| `AUTH_BIN_KEY` | JSONBin master/access key for that private auth bin |
| `AUTH_SECRET` | Any long random string, at least 32 characters |

Example `AUTH_SECRET`: use a password generator and create a long random value. Do not use a normal password you use elsewhere.

---

## Step 6 — Optional variables for community and focus rooms

These are needed for community posts/replies and focus-room session storage.

| Key | Value |
|---|---|
| `COMMUNITY_BIN_ID` | JSONBin bin ID for community posts |
| `COMMUNITY_BIN_KEY` | JSONBin master/access key |
| `FOCUS_BIN_KEY` | JSONBin master/access key for focus room storage, or reuse `COMMUNITY_BIN_KEY` short-term |

For best security later, use separate JSONBin keys/bins for auth, community and focus rooms.

---

## Step 7 — Redeploy after adding variables

Environment variables do not automatically change an already-built deployment.

1. In Vercel, open the ADHDclearfocus project.
2. Click **Deployments**.
3. Click the three dots beside the latest production deployment.
4. Click **Redeploy**.
5. Wait until Vercel says the deployment is complete.

---

## Step 8 — Test the important routes

Open these in your browser:

- `https://www.adhdclearfocus.com/`
- `https://www.adhdclearfocus.com/assessment.html`
- `https://www.adhdclearfocus.com/workplace.html`
- `https://www.adhdclearfocus.com/api/health`
- `https://www.adhdclearfocus.com/api/webhook`

The `/api/health` route should return JSON showing which environment variables are present or missing. It does **not** show the secret values. For the paid report to be ready, `ok_for_paid_report` should be `true`.

The webhook route should show a simple JSON status message.

For the workplace page, submit a test enquiry using your own email. If SendGrid is configured correctly, the enquiry should arrive at `focusedcarepsychology@gmail.com`. If SendGrid is not configured, the page opens a pre-filled email as a backup.

For the paid PDF report, complete the assessment, enter your email, and click **Open secure checkout**. The button should only redirect to Stripe after the site creates a personalised Checkout Session. If Stripe or Vercel variables are missing, it should show an error and no payment should be taken.

---

## Step 9 — Stripe webhook setup

In Stripe:

1. Go to **Developers**.
2. Go to **Webhooks**.
3. Click **Add endpoint**.
4. Endpoint URL: `https://www.adhdclearfocus.com/api/webhook`.
5. Select event: `checkout.session.completed`.
6. Save.
7. Copy the signing secret beginning with `whsec_`.
8. Add it to Vercel as `STRIPE_WEBHOOK_SECRET`.
9. Redeploy in Vercel.

---

## Step 10 — SendGrid sender setup

In SendGrid:

1. Go to **Settings**.
2. Go to **Sender Authentication**.
3. Use **Single Sender Verification** first because it is easiest.
4. Verify `focusedcarepsychology@gmail.com`.
5. Create an API key with Mail Send permission.
6. Add it to Vercel as `SENDGRID_API_KEY`.
7. Add `SENDGRID_FROM_EMAIL=focusedcarepsychology@gmail.com`.
8. Redeploy in Vercel.

Later, for better deliverability, authenticate the domain and use a domain email address.

---

## Step 11 — Safest way to test paid report delivery

Use Stripe **test mode** before switching to live mode.

1. In Stripe, create a test Product called `ADHDclearfocus Clarity Report`.
2. Create a test Price for €49.
3. Copy the test `price_...` ID into Vercel as `STRIPE_PRICE_ID`.
4. Copy your `sk_test_...` secret key into Vercel as `STRIPE_SECRET_KEY`.
5. Create a test webhook endpoint pointing to `https://www.adhdclearfocus.com/api/webhook`.
6. Copy the test webhook signing secret into Vercel as `STRIPE_WEBHOOK_SECRET`.
7. Redeploy.
8. Complete the assessment and buy the report with Stripe test card `4242 4242 4242 4242`, any future expiry, any CVC.
9. Confirm the customer email receives the PDF attachment.
10. Confirm `focusedcarepsychology@gmail.com` receives the admin notification.

Only after the test PDF arrives should you replace the Vercel variables with live `sk_live_...`, live `price_...`, and live `whsec_...` values.

## Important safety rule

Do not use a generic Stripe Payment Link for the personalised PDF report unless it collects and passes all 10 domain scores as metadata. The current package intentionally blocks payment if the personalised Checkout Session cannot be created. This prevents a customer paying without enough information to generate the report.
