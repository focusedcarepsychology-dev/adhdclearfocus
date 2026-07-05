# GP summary + workplace support restored

This update restores and improves the post-assessment actions that were missing from the static assessment rebuild.

## Added to `/assessment.html`

- A clear **GP / clinician summary** option after assessment completion.
- A printable/free summary that includes:
  - overall level
  - ASRS-v1.1 Part A flag
  - 10-domain percentages
  - top domains
  - suggested GP/referral discussion points
  - educational/non-diagnostic disclaimer
- A **copy GP summary** button.
- A **workplace support suggestions** section matched to the user's highest domains.
- A printable workplace summary.
- A copy workplace suggestions button.
- A link to `/workplace.html` for employer programmes.
- The optional paid PDF report now clearly says it is the fuller report to keep/share with a GP.

## Stability

- Homepage remains static.
- Assessment remains dependency-free plain JavaScript.
- No React/Babel/CDN dependency has been reintroduced.
- Service worker cache bumped to v105.
