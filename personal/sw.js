// Service worker de la app personal — NETWORK-FIRST para HTML/CSS:
// José ve siempre la última versión apenas hay señal; el cache queda
// como respaldo offline. Scope: /gastos-apex/personal/ (no toca obras).
const CACHE = 'gastos-jose-v4';
const SHELL = ['.', 'index.html', 'apex-sync.css', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('gastos-jose-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.location.origin)) return;
  const req = e.request;
  const esVivo = req.mode === 'navigate' || req.destination === 'document' ||
                 req.destination === 'style' || /\.(html|css)$/.test(new URL(req.url).pathname);
  if (esVivo) {
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
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(r => {
        const copia = r.clone();
        caches.open(CACHE).then(c => c.put(req, copia));
        return r;
      }))
    );
  }
});
