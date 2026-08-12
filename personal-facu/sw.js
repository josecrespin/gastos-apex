// Gastos Facu se mudo a /facu/. Este worker solo se despide:
// borra sus caches, se desregistra y deja pasar todo a la red.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.indexOf('gastos-facu') === 0).map(k => caches.delete(k)));
    await self.registration.unregister();
    const cs = await self.clients.matchAll({type:'window'});
    cs.forEach(c => c.navigate(c.url));
  })());
});
