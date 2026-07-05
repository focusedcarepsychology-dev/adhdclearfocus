// ADHDclearfocus Service Worker v102 — safe mode
// This version intentionally does NOT cache index.html after the previous blank-screen issue.
const CACHE_NAME = 'adhdclearfocus-safe-v102';
const OFFLINE_PAGES = ['/crisis.html','/offline.html','/manifest.json','/favicon.png','/logo.png','/logo_sm.png'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_PAGES)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // Never cache the home page or assessment page; always take fresh files from Vercel.
  if (url.pathname === '/' || url.pathname === '/index.html' || url.pathname === '/assessment.html') {
    event.respondWith(fetch(event.request, { cache: 'no-store' }).catch(() => caches.match('/offline.html').then(r => r || caches.match('/crisis.html'))));
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request).catch(() => new Response(JSON.stringify({ error: 'offline', message: 'You appear to be offline. Crisis tools are still available.' }), { headers: { 'Content-Type': 'application/json' } })));
    return;
  }

  event.respondWith(fetch(event.request, { cache: 'no-store' }).then(response => {
    if (response && response.status === 200) {
      const clone = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone)).catch(() => {});
    }
    return response;
  }).catch(() => caches.match(event.request).then(cached => cached || caches.match('/offline.html') || caches.match('/crisis.html'))));
});
