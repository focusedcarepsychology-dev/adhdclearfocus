# Home Blank Hard Fix

This build fixes the persistent "homepage flashes then goes blank" issue by removing React from the homepage entirely.

## What changed

- `index.html` is now a static, dependency-free homepage.
- The previous React assessment app has been moved to `assessment.html`.
- The homepage no longer loads React, ReactDOM, Babel or app state.
- The homepage clears old service-worker caches once.
- `sw.js` has been changed so it never caches `/`, `/index.html` or `/assessment.html`.
- The home CTA links to `/assessment.html`.

## Why this was necessary

The previous homepage rendered a fallback first, then React replaced it. On some browsers/deployments the React state/render step resulted in a blank root after the initial flash. This build makes the public homepage immune to that failure mode.

## Upload instruction

Upload/replace all files from this package into the repo root, including hidden files and the `/api` folder.
