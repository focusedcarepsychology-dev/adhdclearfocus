# ADHDclearfocus commercial model refresh — September 2026

Status: commercial/measurement design only. This branch is not a production release.

## Why this refresh exists

The product has multiple possible revenue paths but the live/source-of-truth commercial model still contains a time-limited founding offer that closed on 31 July 2026 and records two different historical subscription-price models. Traffic, feature usage and email capture therefore cannot be treated as evidence that the current subscription positioning is commercially optimal.

The next phase should optimise **attributable contribution**, not page views or feature count.

## Funnel to measure

1. content / search / referral source;
2. screener start and completion;
3. consented email capture;
4. €49 personalised report checkout;
5. settled €49 payment;
6. optional €79 review-call purchase;
7. Pro trial / waitlist / paid subscription once a current offer is selected;
8. employer enquiry where relevant.

The September attribution branch stores first- and last-touch categorical source data and carries it into the existing Stripe Checkout Session metadata. This permits future reports such as “which landing page/campaign produced settled report purchases?” without sending raw referrers or health information into attribution metadata.

## Offer rules

### €49 personalised report

Keep as the clearest existing low-friction paid product while measuring:
- screener-completion → checkout-start rate;
- checkout-start → paid rate;
- refund/support burden;
- paid purchases by first source/landing and last campaign;
- downstream €79 or future subscription conversion.

Do not optimise only for report checkout volume if refunds, fulfilment/API cost or downstream quality deteriorate.

### €79 review call

Treat as an optional expansion offer, not an automatic clinical pathway. Track attach rate and realised contribution separately from the report. Any regulated clinical service must retain its own suitability/governance boundary.

### Pro subscription

Do not extend an expired “founding deadline” by inventing a new urgency date. Replace deadline-based messaging only after choosing and testing a current offer.

The historical €5/month billed yearly (€60/year) versus €10 regular model and the earlier €9/€19 monthly model should be treated as **price hypotheses**, not truths.

Recommended evidence sequence:
1. identify the minimum product actually available/usable now;
2. offer one transparent control price to a defined cohort;
3. test at most one meaningfully different challenger price/packaging variant;
4. measure trial activation, week-4 retention, paid conversion, cancellations and support cost;
5. prefer the offer producing higher retained contribution, not merely higher signup rate.

Do not use paid acquisition until retention and paid conversion are measurable.

## Education → clinical-service boundary

ADHDclearfocus remains an educational platform. Where a user wants professional assessment/support, the scalable model is a company-owned, clearly labelled next-step/referral pathway in which clinical suitability remains with an appropriately qualified clinician. Attribution should record the educational source that generated a qualified enquiry, but screening scores must not be used by the commercial system to promise diagnosis, suitability or clinical outcome.

## Employer route

The employer/certification concept is a separate B2B experiment. Before building a large programme, validate:
- 10–15 employer/HR conversations;
- the specific buying problem;
- budget owner;
- one paid pilot or strong written commercial commitment.

No €2,500 programme should be treated as revenue potential until this evidence exists.

## Scale / kill rules

- Organic traffic rises but qualified email/report/service conversion does not: change content intent/CTA and funnel, not publishing volume.
- >=100 meaningful screener completions but weak €49 paid conversion: diagnose trust, offer, price, delivery promise and checkout friction.
- Subscription trial signups with <25% week-4 retained use: change product/positioning before acquisition.
- Scale a content family only when it produces attributable qualified leads or positive paid contribution.
- Keep first-touch and last-touch attribution separate so a discovery page is not incorrectly credited only to the final CTA page.
