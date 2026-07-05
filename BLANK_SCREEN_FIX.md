# Blank Screen Fix — ADHDclearfocus

The homepage previously depended on in-browser Babel (`type="text/babel"`). If Babel fails to load, is blocked, or errors during transformation, React never mounts and the user sees a blank page because the original `#root` was empty.

## Fix applied

- Precompiled the homepage JSX into normal browser JavaScript.
- Removed the Babel CDN dependency from `index.html`.
- Kept React and ReactDOM CDN links only.
- Added a static fallback inside `#root`, so the page no longer appears blank even if JavaScript fails.
- Added a React error boundary around the assessment app.
- Bumped the service worker cache name to force browsers to replace stale cached files.
- Added `/`, `/index.html`, `strategies.html`, and `resources.html` to offline cache.

## Upload note

Upload the contents of this package to GitHub, replacing all existing files. After deploy, test in an incognito/private browser first. If your normal browser still shows blank, clear site data or unregister the old service worker once.
