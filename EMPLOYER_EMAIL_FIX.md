# Employer page email fix

## What was wrong

The workplace/employers page previously used a browser `mailto:` link only. That means the enquiry was not sent by the website itself. It depended on the visitor having an email app configured on their device.

## What is fixed now

- The form now posts to `/api/employer-lead`.
- `/api/employer-lead` sends the enquiry through SendGrid.
- Enquiries go to `focusedcarepsychology@gmail.com` by default.
- The page still has a backup `mailto:` fallback if SendGrid is not configured yet.
- The page also attempts to tag the lead in Mailchimp as `employer-lead` if Mailchimp is configured.

## Required Vercel variables for this to work

Minimum:

- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL=focusedcarepsychology@gmail.com`
- `EMPLOYER_LEADS_EMAIL=focusedcarepsychology@gmail.com`

Recommended:

- `ADMIN_EMAIL=focusedcarepsychology@gmail.com`

Important: `focusedcarepsychology@gmail.com` must be verified in SendGrid as a sender, or SendGrid may reject the email.
