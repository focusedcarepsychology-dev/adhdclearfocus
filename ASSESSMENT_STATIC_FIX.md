# ADHDclearfocus — Assessment Static Fix

This build fixes the blank screen on the full assessment by replacing the React-based `/assessment.html` with a dependency-free plain JavaScript version.

## What changed

- `/index.html` remains the static public homepage.
- `/assessment.html` is now a reliable static assessment app with no React, ReactDOM, Babel, JSX, or CDN dependency.
- The 39-question / 10-domain screener has been preserved.
- Scores are calculated locally across the same 10 domains:
  - Attention Regulation
  - Hyperactivity & Impulse Control
  - Executive Function
  - Emotional Regulation
  - Working Memory
  - Time Perception
  - Hyperfocus & Interest Drive
  - Rejection Sensitivity
  - Developmental History
  - Life Impact
- ASRS Part A threshold logic is preserved.
- Local progress saving is preserved.
- Stripe checkout metadata is preserved via `/api/create-checkout`.
- Mailchimp capture is preserved via `/api/mailchimp-subscribe`.
- If the API checkout fails, it falls back to the direct Stripe payment link.
- `sw.js` cache version bumped to `adhdclearfocus-safe-v101` and continues to avoid caching `/`, `/index.html`, and `/assessment.html`.

## Content changes

- Neurofeedback has been moved into an “Emerging Evidence & Contested Interventions” frame rather than being presented as new evidence.
- Neurofeedback content has been expanded with a clearer journal trail and more balanced wording.
- RSD content has been simplified so it explains the lived experience more plainly and avoids over-medicalised wording.

## Why this is safer

The assessment blank was likely caused by the previous large React app failing or replacing the fallback root. This new assessment page renders without any framework dependency, so it should remain visible even if external CDN scripts fail.
