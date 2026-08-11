// Service worker Obras — NETWORK-FIRST para HTML y CSS: los teléfonos
// ven siempre la última versión apenas hay señal; el cache queda solo
// como respaldo offline. Íconos/manifest siguen cache-first (no cambian).
// Los POST a Supabase nunca pasan por acá (solo GET same-origin).
const CACHE = 'gastos-obras-v7';
const SHELL = ['.', 'index.html', 'dashboard.html', 'apex-sync.css',
               'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => (k.startsWith('gastos-obras-') || k === 'gastos-as-v1') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.location.origin)) return;
  const req = e.request;
  const esVivo = req.mode === 'navigate' || req.destination === 'document' ||
                 req.destination === 'style' || /\.(html|css)$/.test(new URL(req.url).pathname);
  if (esVivo) {
    // network-first: red → cachear copia → si no hay señal, cache.
    // cache:'no-cache' revalida SIEMPRE contra el server (evita que el
    // HTTP cache del navegador devuelva un HTML viejo "fresco").
    e.respondWith(
      fetch(req, {cache:'no-cache'}).then(r => {
        const copia = r.clone();
        caches.open(CACHE).then(c => c.put(req, copia));
        return r;
      }).catch(() => caches.match(req))
    );
  } else {
    // cache-first para estáticos que no cambian (íconos, manifest)
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(r => {
        const copia = r.clone();
        caches.open(CACHE).then(c => c.put(req, copia));
        return r;
      }))
    );
  }
});
