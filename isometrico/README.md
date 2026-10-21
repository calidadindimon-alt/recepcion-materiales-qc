# INDIMON CAD · DP-F-009 Bocetos Isométricos

App web instalable (PWA) para trazar isométricos de tubería en hoja A3 y calcular el listado de materiales (BOM).
Funciona con dedo, lápiz o ratón, en Android, iPhone/iPad y PC, también sin internet.

## Cómo obtener la app

| Opción | Pasos |
|---|---|
| **Instalar (recomendado)** | Publique el repositorio en GitHub Pages (Settings → Pages → rama `main`, carpeta `/root`). Abra `https://<usuario>.github.io/recepcion-materiales-qc/isometrico/` y pulse **Instalar** (Chrome/Edge en Android o PC) o **Compartir → Agregar a pantalla de inicio** en Safari (iOS). |
| **Archivo único .html** | Desde la app: menú *Simbología → 5. Archivo → Descargar app (.html)*. Genera un solo archivo con la librería Excel incluida; se abre con doble clic y no necesita internet. |
| **Local** | `python3 -m http.server` dentro de esta carpeta y abrir `http://localhost:8000`. |

## Uso rápido

- **Tubería**: arrastre desde un punto, o toque el inicio y luego cada vértice (cadena); toque el mismo punto o *Terminar* para cortar. El tramo se bloquea a los ejes 30°/90°/150°/210°/270°/330° y se imanta a nodos (círculo verde = nodo existente, naranja = grilla).
- **Accesorios y válvulas**: elija el símbolo y toque sobre la tubería; se alinea solo con el eje del tramo. Codos y tees orientan sus brazos con las tuberías conectadas.
- **Tocar**: seleccione un componente para cambiar diámetro, especificación, longitud real, rotarlo o borrarlo.
- **Zoom**: pellizco con dos dedos, Ctrl+rueda o botones. *Lienzo* acerca al área de dibujo.
- **BOM**: se recalcula solo. La cantidad se puede ajustar a mano (deje vacío para volver al cálculo). *Añadir consumible* agrega soldadura, tintas, discos, etc.
- **Exportar**: *Excel* (.xlsx con rótulo + BOM + detalle de componentes) y *PDF A3* (imprimir → Guardar como PDF, A3 horizontal).
- **Guardar**: el borrador se guarda solo en el equipo; *Guardar proyecto (.json)* para compartir o archivar.

Atajos PC: Ctrl+Z / Ctrl+Y, Supr, Esc, R (rotar), T (tubería), V (tocar), H (mover), +/−, 0 (ajustar).

## Archivos

- `index.html` – aplicación completa (HTML + CSS + JS, sin dependencias de CDN).
- `vendor/xlsx.full.min.js` – SheetJS 0.18.5 (Apache-2.0) para exportar .xlsx sin internet.
- `manifest.webmanifest`, `sw.js`, `icons/` – instalación y funcionamiento sin conexión. Al publicar cambios suba `VERSION` en `sw.js`.
