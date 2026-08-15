#!/usr/bin/env python3
"""
Genera las apps v5 de los hermanos (/agus/ y /facu/) desde UNA sola plantilla.
Fuente de verdad: _plantilla-hermano.html  →  agus/index.html + facu/index.html

Correr:  python3 build_hermanos.py
No toca la app de Obras (raiz) ni la de Jose (personal/).
"""
import os, shutil, json, re

RAIZ = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(RAIZ, '_plantilla-hermano.html')
SW_CACHE_V = 5          # subir cuando cambie el shell (v5 = fixes v10)

HERMANOS = {
    'agus': {
        'NOMBRE': 'Agus',
        'NOMBRE_UP': 'AGUS',
        'TABLA_PERSONAL': 'gastos_agus',
        'RPC_PERSONAL': 'gastos_agus_lista',
        'CLAVE_PERSONAL': '2989913b7b',
        'CLAVE_OBRAS': '66db2f50ca',
        # identidad pearl (--p-agus del design system)
        'ACCENT': '#E8E2D5', 'ACCENT_HI': '#F5F0E4', 'ACCENT_DEEP': '#CBBFA4',
        'ACCENT_SOFT': 'rgba(232,226,213,.14)', 'ON_ACCENT': '#20261F',
        'GLOW': '0 10px 28px -10px rgba(232,226,213,.28)',
        'LOGO_TRI': '#E8E2D5', 'LOGO_ONDA': '#C98F5F',
        'ICONOS_DE': 'personal-agus',
        'VIEJA': 'personal-agus',
    },
    'facu': {
        'NOMBRE': 'Facu',
        'NOMBRE_UP': 'FACU',
        'TABLA_PERSONAL': 'gastos_facu',
        'RPC_PERSONAL': 'gastos_facu_lista',
        'CLAVE_PERSONAL': '56a2863905',
        'CLAVE_OBRAS': '66db2f50ca',
        # identidad teal claro (--p-facu del design system)
        'ACCENT': '#4FB0C8', 'ACCENT_HI': '#6FC2D6', 'ACCENT_DEEP': '#3A8CA0',
        'ACCENT_SOFT': 'rgba(79,176,200,.15)', 'ON_ACCENT': '#062229',
        'GLOW': '0 10px 28px -10px rgba(79,176,200,.40)',
        'LOGO_TRI': '#E8E2D5', 'LOGO_ONDA': '#4FB0C8',
        'ICONOS_DE': 'personal-facu',
        'VIEJA': 'personal-facu',
    },
}

SW = """// Service worker de Gastos {NOMBRE} v5 — NETWORK-FIRST para HTML/CSS:
// {NOMBRE} ve siempre la ultima version apenas hay senal; el cache queda
// como respaldo offline. Scope: /gastos-apex/{YO}/.
// Los POST a Supabase nunca pasan por aca (solo GET same-origin).
const CACHE = 'gastos-{YO}5-v{V}';
const SHELL = ['.', 'index.html', '../apex-sync.css', 'manifest.webmanifest',
               'icon-180.png', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
}});

self.addEventListener('activate', e => {{
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('gastos-{YO}') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});
// Ultimo recurso. NUNCA devolver undefined a respondWith: eso es un network
// error y el telefono muestra una PANTALLA EN BLANCO. Pasaba cada vez que se
// caia la senal (o iOS vaciaba el cache del PWA) y la URL pedida no estaba
// exactamente igual en el cache (por ejemplo con ?utm_source de WhatsApp).
function sinRed(req){{
  return caches.match(req, {{ignoreSearch:true}})
    .then(hit => hit || caches.match('index.html', {{ignoreSearch:true}}))
    .then(hit => hit || caches.match('./', {{ignoreSearch:true}}))
    .then(hit => hit || new Response(
      '<!doctype html><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<body style="margin:0;background:#0F272E;color:#E8E2D5;height:100vh;display:flex;' +
      'align-items:center;justify-content:center;text-align:center;padding:24px;' +
      'font:600 15px -apple-system,BlinkMacSystemFont,system-ui,sans-serif">' +
      '<div>Sin conexion y sin copia guardada.<br><br>' +
      '<a style="color:#C98F5F" href="./">Reintentar</a></div>',
      {{status:200, headers:{{'Content-Type':'text/html; charset=utf-8'}}}}))
    .catch(() => new Response('', {{status:504}}));
}}

function guardar(req, r){{
  if(!r || !r.ok) return;
  const copia = r.clone();
  caches.open(CACHE).then(c => c.put(req, copia)).catch(() => {{}});
}}

self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.location.origin)) return;
  const req = e.request;
  const esVivo = req.mode === 'navigate' || req.destination === 'document' ||
                 req.destination === 'style' || /\.(html|css)$/.test(new URL(req.url).pathname);
  if (esVivo) {{
    // network-first: red -> se guarda copia -> si no hay senal, el cache.
    // cache:'no-cache' revalida SIEMPRE contra el server. Va envuelto en
    // Promise.resolve() porque en WebKit fetch(req,{{cache:...}}) sobre un
    // request de navegacion puede tirar SINCRONICO: si eso escapa del
    // handler, la navegacion muere y queda la pantalla en blanco.
    e.respondWith(
      Promise.resolve()
        .then(() => fetch(req, {{cache:'no-cache'}}))
        .then(r => {{ guardar(req, r); return r; }})
        .catch(() => sinRed(req))
    );
  }} else {{
    // cache-first para estaticos que no cambian (iconos, manifest)
    e.respondWith(
      caches.match(req, {{ignoreSearch:true}})
        .then(hit => hit || fetch(req).then(r => {{ guardar(req, r); return r; }}))
        .catch(() => new Response('', {{status:504}}))
    );
  }}
}});
"""

# --- Pagina puente en la ruta vieja: limpia el service worker viejo, borra
#     sus caches y manda a la ruta nueva. Asi el icono ya instalado en el
#     telefono sigue funcionando y termina abriendo la app v5.
REDIR = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Gastos {NOMBRE} · Apex Sync</title>
<meta name="theme-color" content="#0F272E">
<link rel="canonical" href="../{YO}/">
<style>
  html,body{{height:100%}}
  body{{margin:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
       gap:18px;background:#0F272E;color:#A9BDBA;text-align:center;padding:24px;
       font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,system-ui,sans-serif}}
  b{{color:#E8E2D5;font-size:16px}}
  a{{color:{ACCENT};font-weight:700}}
</style>
</head>
<body>
  <b>Gastos {NOMBRE} se mudó</b>
  <p>Te estamos llevando a la app nueva…<br>Ahora la obra y lo personal están juntos.</p>
  <p><a href="../{YO}/">Abrir Gastos {NOMBRE}</a></p>
<script>
// Baja el service worker viejo y sus caches antes de saltar, para que el
// telefono no se quede sirviendo la app anterior desde el cache.
(async function(){{
  try{{
    if('serviceWorker' in navigator){{
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.filter(r => r.scope.indexOf('/{VIEJA}/') !== -1).map(r => r.unregister()));
    }}
    if(window.caches){{
      const keys = await caches.keys();
      await Promise.all(keys.filter(k => k.indexOf('gastos-{YO}') === 0 && k.indexOf('gastos-{YO}5') !== 0).map(k => caches.delete(k)));
    }}
  }}catch(e){{}}
  location.replace('../{YO}/');
}})();
</script>
</body>
</html>
"""

# El sw.js viejo se reemplaza por uno que se auto-desinstala: al navegar,
# el navegador busca actualizacion de sw.js, instala este y se va solo.
SW_ADIOS = """// Gastos {NOMBRE} se mudo a /{YO}/. Este worker solo se despide:
// borra sus caches, se desregistra y deja pasar todo a la red.
// OJO: 'gastos-{YO}' tambien es prefijo de 'gastos-{YO}5-vN', que es el cache
// de la app NUEVA. Por eso se excluye — si no, el puente le borra el shell.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => {{
  e.waitUntil((async () => {{
    const keys = await caches.keys();
    await Promise.all(keys
      .filter(k => k.indexOf('gastos-{YO}') === 0 && k.indexOf('gastos-{YO}5') !== 0)
      .map(k => caches.delete(k)));
    await self.registration.unregister();
    const cs = await self.clients.matchAll({{type:'window'}});
    cs.forEach(c => c.navigate(c.url));
  }})());
}});
"""


def build():
    with open(PLANTILLA, encoding='utf-8') as f:
        plantilla = f.read()

    for yo, cfg in HERMANOS.items():
        dest = os.path.join(RAIZ, yo)
        os.makedirs(dest, exist_ok=True)

        # --- index.html ---
        html = plantilla.replace('@@YO@@', yo)
        for k, v in cfg.items():
            html = html.replace('@@%s@@' % k, v)
        sobran = re.findall(r'@@[A-Z_]+@@', html)
        if sobran:
            raise SystemExit('Quedaron placeholders sin reemplazar: %s' % set(sobran))
        with open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)

        # --- manifest ---
        manifest = {
            "name": "Gastos %s · Apex Sync" % cfg['NOMBRE'],
            "short_name": "Gastos %s" % cfg['NOMBRE'],
            "description": "Obra FAGU + gastos personales de %s — Apex Sync" % cfg['NOMBRE'],
            "start_url": ".", "scope": ".", "display": "standalone",
            "background_color": "#0F272E", "theme_color": "#0F272E",
            "icons": [
                {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        }
        with open(os.path.join(dest, 'manifest.webmanifest'), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # --- service worker ---
        with open(os.path.join(dest, 'sw.js'), 'w', encoding='utf-8') as f:
            f.write(SW.format(NOMBRE=cfg['NOMBRE'], YO=yo, V=SW_CACHE_V))

        # --- iconos propios de cada hermano (los mismos que ya tienen) ---
        for n in (180, 192, 512):
            shutil.copyfile(os.path.join(RAIZ, cfg['ICONOS_DE'], 'icon-%d.png' % n),
                            os.path.join(dest, 'icon-%d.png' % n))

        # --- ruta vieja: puente ---
        vieja = os.path.join(RAIZ, cfg['VIEJA'])
        with open(os.path.join(vieja, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(REDIR.format(NOMBRE=cfg['NOMBRE'], YO=yo, VIEJA=cfg['VIEJA'], ACCENT=cfg['ACCENT']))
        with open(os.path.join(vieja, 'sw.js'), 'w', encoding='utf-8') as f:
            f.write(SW_ADIOS.format(NOMBRE=cfg['NOMBRE'], YO=yo))

        print('OK  /%s/  (+ puente en /%s/)' % (yo, cfg['VIEJA']))


if __name__ == '__main__':
    build()
