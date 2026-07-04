// ADHDclearfocus Service Worker v3
const CACHE_NAME = 'adhdclearfocus-v3';
const OFFLINE_PAGES = ['/crisis.html','/manifest.json','/favicon.png','/logo.png','/logo_sm.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_PAGES)).catch((err) => console.log('Cache install error:', err)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request).catch(() => new Response(JSON.stringify({ error: 'offline', message: 'You appear to be offline. Crisis tools are still available.' }), { headers: { 'Content-Type': 'application/json' } })));
    return;
  }

  event.respondWith(
    // cache:'no-store' forces a genuine network round-trip, bypassing the browser's own
    // HTTP cache layer -- without this, "network-first" can still silently serve a stale
    // cached response if the host's cache-control headers allow it.
    fetch(event.request, { cache: 'no-store' }).then((response) => {
      if (response && response.status === 200) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone)).catch(() => {});
      }
      return response;
    }).catch(() => caches.match(event.request).then((cached) => cached || caches.match('/crisis.html')))
  );
});
