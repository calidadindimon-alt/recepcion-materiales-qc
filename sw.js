/* Service worker de Recepción de Materiales (QC-F-002): guarda la app en el equipo para trabajar sin internet.
   Al publicar cambios, suba el número de VERSION para que los equipos descarguen la nueva copia.
   No atiende la carpeta isometrico/ (INDIMON CAD tiene su propio service worker) y solo borra sus propias copias. */
const PREFIJO = 'recepcion-qc-';
const VERSION = PREFIJO + 'v2';
const ARCHIVOS = [
  './', './index.html', './manifest.webmanifest', './catalogo.js', './catalogo-extra.js', './vendor/msal-browser.min.js', './vendor/exceljs.min.js',
  './plantilla/QC-F-002.xlsx', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png'
];
const guardarTodo = () => caches.open(VERSION).then(c => c.addAll(ARCHIVOS));

self.addEventListener('install', e => {
  e.waitUntil(guardarTodo().then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(claves => Promise.all(claves.filter(k => k.startsWith(PREFIJO) && k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

/* la página lo pide al abrir con internet: si la copia guardada desapareció, se vuelve a bajar */
self.addEventListener('message', e => {
  if (e.data === 'asegurar') e.waitUntil(caches.open(VERSION).then(c => c.match('./index.html'))
    .then(hay => hay ? null : guardarTodo()).catch(() => {}));
});

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  if (url.pathname.includes('/isometrico/')) return;
  if (req.mode === 'navigate') {
    /* página: primero la red (para recibir actualizaciones); sin conexión, la copia guardada */
    e.respondWith(fetch(req).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(VERSION).then(c => c.put('./index.html', copia)); }
      return r;
    }).catch(() => caches.open(VERSION).then(c => c.match('./index.html'))));
    return;
  }
  /* recursos: copia guardada al instante y actualización en segundo plano */
  e.respondWith(caches.open(VERSION).then(c => c.match(req, { ignoreSearch: true }).then(guardada => {
    const red = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => guardada);
    return guardada || red;
  })));
});
