# ADHDclearfocus — homepage brain animation fix

This package restores a lightweight moving brain / neural-heart visual on the opening page without bringing back React, Babel, or CDN dependencies.

## What changed

- Added a CSS-only animated brain/neural-heart illustration to `index.html`.
- Kept the homepage static so it should not reintroduce the previous blank-screen issue.
- Animation uses inline SVG and CSS only: no external image, no JavaScript, no React.
- Respects `prefers-reduced-motion`; users who prefer reduced motion will see a still version.
- Bumped the service-worker cache name from `safe-v101` to `safe-v102`.
- Bumped the homepage cache-repair key so browsers refresh the latest homepage.

## Test

After uploading all files and redeploying, open:

- https://www.adhdclearfocus.com/
- https://www.adhdclearfocus.com/assessment.html

The homepage should show the animated brain/profile card, and the assessment should remain separate and static.
