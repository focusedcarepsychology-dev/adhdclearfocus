# Blank screen fix — cookie overlay issue

## What happened
The homepage was not fully crashing. It flashed the fallback homepage, then React loaded and replaced it with the app. The app's initial state was `step = "cookie"`, which displayed only the sticky header and the cookie banner at the bottom. The main content area had no intro screen, so it looked like the page had gone blank.

## Fix applied
- Changed the initial app step from `cookie` to `intro`.
- Converted the cookie notice into an overlay banner shown on top of the intro screen.
- Added `acf_cookie_ok` localStorage persistence so the banner does not reappear after acceptance.
- Kept the no-Babel homepage fix.
- Bumped the service worker cache to `adhdclearfocus-v5-cookiefix` so browsers refresh cached homepage assets.

## After deployment
Open the site in an incognito window first. If your normal browser still shows the old version, clear site data for `adhdclearfocus.com` and `www.adhdclearfocus.com`, or open DevTools > Application > Service Workers > Unregister.
