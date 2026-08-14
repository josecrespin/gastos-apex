// Service worker de la app personal — NETWORK-FIRST para HTML/CSS:
// José ve siempre la última versión apenas hay señal; el cache queda
// como respaldo offline. Scope: /gastos-apex/personal/ (no toca obras).
const CACHE = 'gastos-jose-v8';
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

// Ultimo recurso. NUNCA devolver undefined a respondWith: eso es un network
// error y el telefono muestra una PANTALLA EN BLANCO. Pasaba cada vez que se
// caia la senal (o iOS vaciaba el cache del PWA) y la URL pedida no estaba
// exactamente igual en el cache (por ejemplo con ?utm_source de WhatsApp).
function sinRed(req){
  return caches.match(req, {ignoreSearch:true})
    .then(hit => hit || caches.match('index.html', {ignoreSearch:true}))
    .then(hit => hit || caches.match('./', {ignoreSearch:true}))
    .then(hit => hit || new Response(
      '<!doctype html><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<body style="margin:0;background:#0F272E;color:#E8E2D5;height:100vh;display:flex;' +
      'align-items:center;justify-content:center;text-align:center;padding:24px;' +
      'font:600 15px -apple-system,BlinkMacSystemFont,system-ui,sans-serif">' +
      '<div>Sin conexion y sin copia guardada.<br><br>' +
      '<a style="color:#C98F5F" href="./">Reintentar</a></div>',
      {status:200, headers:{'Content-Type':'text/html; charset=utf-8'}}))
    .catch(() => new Response('', {status:504}));
}

function guardar(req, r){
  if(!r || !r.ok) return;
  const copia = r.clone();
  caches.open(CACHE).then(c => c.put(req, copia)).catch(() => {});
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.location.origin)) return;
  const req = e.request;
  const esVivo = req.mode === 'navigate' || req.destination === 'document' ||
                 req.destination === 'style' || /\.(html|css)$/.test(new URL(req.url).pathname);
  if (esVivo) {
    // network-first: red -> se guarda copia -> si no hay senal, el cache.
    // cache:'no-cache' revalida SIEMPRE contra el server. Va envuelto en
    // Promise.resolve() porque en WebKit fetch(req,{cache:...}) sobre un
    // request de navegacion puede tirar SINCRONICO: si eso escapa del
    // handler, la navegacion muere y queda la pantalla en blanco.
    e.respondWith(
      Promise.resolve()
        .then(() => fetch(req, {cache:'no-cache'}))
        .then(r => { guardar(req, r); return r; })
        .catch(() => sinRed(req))
    );
  } else {
    // cache-first para estaticos que no cambian (iconos, manifest)
    e.respondWith(
      caches.match(req, {ignoreSearch:true})
        .then(hit => hit || fetch(req).then(r => { guardar(req, r); return r; }))
        .catch(() => new Response('', {status:504}))
    );
  }
});
