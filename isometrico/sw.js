/* Service worker de INDIMON CAD: guarda la app en el equipo para trabajar sin internet.
   Al publicar cambios, suba el número de VERSION para que los equipos descarguen la nueva copia. */
const VERSION = 'indimon-cad-v14';
const ARCHIVOS = [
  './', './index.html', './manifest.webmanifest', './vendor/xlsx.bundle.js',
  './vendor/exceljs.min.js', './plantillas/QC-F-004.xlsx', './plantillas/QC-F-015.xlsx',
  './icons/icon.svg', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(claves => Promise.all(claves.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    /* páginas: primero la red (para recibir actualizaciones); sin conexión, la copia guardada */
    e.respondWith(fetch(req).then(r => {
      const copia = r.clone(); caches.open(VERSION).then(c => c.put('./index.html', copia)); return r;
    }).catch(() => caches.match('./index.html')));
    return;
  }
  /* recursos: copia guardada al instante y actualización en segundo plano */
  e.respondWith(caches.match(req).then(guardada => {
    const red = fetch(req).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(VERSION).then(c => c.put(req, copia)); }
      return r;
    }).catch(() => guardada);
    return guardada || red;
  }));
});
