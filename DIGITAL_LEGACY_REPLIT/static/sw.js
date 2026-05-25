const CACHE_VERSION = 'v1';
const STATIC_CACHE = `digital-legacy-static-${CACHE_VERSION}`;
const API_CACHE = `digital-legacy-api-${CACHE_VERSION}`;

const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
];

// Install: pre-cache the app shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: remove old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== API_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // API calls: network-first, brief cache fallback (read-only endpoints)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstApi(request));
    return;
  }

  // Static assets (/assets/*): cache-first
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(cacheFirstStatic(request));
    return;
  }

  // Navigation (HTML): network-first, fall back to cached index.html
  if (request.mode === 'navigate') {
    event.respondWith(networkFirstNav(request));
    return;
  }

  // Everything else: network-first
  event.respondWith(fetch(request).catch(() => caches.match(request)));
});

async function networkFirstApi(request) {
  const url = new URL(request.url);
  // Only cache safe read-only mobile endpoints to avoid stale auth state
  const cacheable = [
    '/api/mobile/dashboard',
    '/api/digital-assets/types',
    '/api/beneficiaries/relationships',
  ].some((path) => url.pathname === path);

  try {
    const response = await fetch(request);
    if (cacheable && response.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    if (cacheable) {
      const cached = await caches.match(request, { cacheName: API_CACHE });
      if (cached) return cached;
    }
    return new Response(JSON.stringify({ error: 'Offline', offline: true }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

async function cacheFirstStatic(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Asset non disponibile offline', { status: 503 });
  }
}

async function networkFirstNav(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match('/') || await caches.match(request);
    if (cached) return cached;
    return new Response('<h1>Offline</h1><p>Connettiti a Internet per usare Digital Legacy.</p>', {
      headers: { 'Content-Type': 'text/html' },
    });
  }
}

// Push notification handler
self.addEventListener('push', (event) => {
  if (!event.data) return;

  let payload;
  try {
    payload = event.data.json();
  } catch {
    payload = { title: 'Digital Legacy', body: event.data.text() };
  }

  const options = {
    body: payload.body || '',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    tag: payload.tag || 'digital-legacy',
    data: payload.data || {},
    requireInteraction: payload.requireInteraction || false,
    actions: payload.actions || [],
  };

  event.waitUntil(self.registration.showNotification(payload.title, options));
});

// Notification click: focus or open the app
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || '/';

  event.waitUntil(
    clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        const existing = windowClients.find((c) => c.url === targetUrl && 'focus' in c);
        if (existing) return existing.focus();
        return clients.openWindow(targetUrl);
      })
  );
});
