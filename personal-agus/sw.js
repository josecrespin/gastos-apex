// Gastos Agus se mudo a /agus/. Este worker solo se despide:
// borra sus caches, se desregistra y deja pasar todo a la red.
// OJO: 'gastos-agus' tambien es prefijo de 'gastos-agus5-vN', que es el cache
// de la app NUEVA. Por eso se excluye — si no, el puente le borra el shell.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter(k => k.indexOf('gastos-agus') === 0 && k.indexOf('gastos-agus5') !== 0)
      .map(k => caches.delete(k)));
    await self.registration.unregister();
    const cs = await self.clients.matchAll({type:'window'});
    cs.forEach(c => c.navigate(c.url));
  })());
});
