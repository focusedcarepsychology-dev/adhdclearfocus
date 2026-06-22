// ADHDclearfocus Service Worker v1
// Caches crisis tools for offline use — critical for mental health emergencies

const CACHE_NAME = 'adhdclearfocus-v1';
const OFFLINE_PAGES = [
  '/',
  '/app.html',
  '/crisis.html',
  '/focus.html',
  '/strategies.html',
  '/manifest.json',
  '/favicon.png',
  '/logo.png',
  '/logo_sm.png',
];

// Install: cache critical pages
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_PAGES);
    }).catch((err) => {
      console.log('Cache install error:', err);
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: cache-first for pages, network-first for API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API calls: always network
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({ error: 'offline', message: 'Crisis tools are still available offline.' }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })
    );
    return;
  }

  // Pages: cache-first (ensures offline crisis tools always work)
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        // Cache successful responses
        if (response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback
        return caches.match('/crisis.html');
      });
    })
  );
});

// Background sync for diary entries
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-diary') {
    event.waitUntil(syncDiaryEntries());
  }
});

async function syncDiaryEntries() {
  // Sync pending diary entries when back online
  const db = await openDB();
  const pending = await db.getAll('diary-sync-queue');
  for (const entry of pending) {
    try {
      await fetch('/api/sync-diary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry)
      });
      await db.delete('diary-sync-queue', entry.id);
    } catch (e) {
      console.log('Sync failed, will retry:', e);
    }
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(data.title || 'ADHDclearfocus', {
      body: data.body || 'Time for your daily check-in',
      icon: '/logo.png',
      badge: '/favicon.png',
      tag: data.tag || 'checkin',
      data: { url: data.url || '/app.html' }
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/app.html')
  );
});
