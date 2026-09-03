// ADHDclearfocus Service Worker v107 — SEO-safe navigation mode
// HTML navigations are always network-first and are never written to Cache Storage.
// Only a tiny set of static/offline assets are cached for resilience.
const CACHE_NAME = 'adhdclearfocus-safe-v107';
const STATIC_ASSETS = ['/offline','/crisis','/manifest.json','/favicon.png','/logo.png','/logo_sm.png'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({error:'offline',message:'You appear to be offline.'}), {
          status: 503,
          headers: {'Content-Type':'application/json','Cache-Control':'no-store'}
        })
      )
    );
    return;
  }

  // Never serve cached HTML to normal page navigations.
  if (event.request.mode === 'navigate' || event.request.destination === 'document') {
    event.respondWith(
      fetch(event.request, {cache:'no-store'})
        .catch(() => caches.match('/offline').then(r => r || caches.match('/crisis')))
    );
    return;
  }

  // Static assets: network first, with a cache fallback.
  event.respondWith(
    fetch(event.request).then(response => {
      if (response && response.ok && ['style','script','image','font','manifest'].includes(event.request.destination)) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone)).catch(() => {});
      }
      return response;
    }).catch(() => caches.match(event.request))
  );
});
