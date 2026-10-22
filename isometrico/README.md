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
- **Unidades**: las cotas, la longitud de cada tramo y el paso de grilla se muestran en **milímetros** por defecto (500 mm por paso). En *1. Control y trazado → Unidad de cotas* puede cambiar a metros. El BOM mantiene la tubería en metros lineales (ML).
- **Tubería a cualquier ángulo (45°, 56°…)**: en *Ángulo de trazado* elija *Libre* (cada 15°, 5° o 1°) y el plano: *Horizontal* (ángulo desde el Norte), *Vertical N-S* o *Vertical E-O*. El tramo se dibuja en su plano con el triángulo de desvío sombreado y el ángulo rotulado; la longitud es la real. El ángulo exacto se puede escribir al confirmar la longitud o en el panel del tramo. Botón rápido **ISO / ∠** en la barra inferior (tecla A; tecla P cambia el plano).
- **Catálogo**: más de 60 símbolos en grupos (accesorios BW, roscados/SW/olets, bridas, 16 válvulas, especiales, instrumentos, soportes) con buscador. *Agregar ítem al catálogo* crea ítems propios; *Importar catálogo (.csv)* carga muchos a la vez (columnas `NOMBRE;CATEGORIA;SIMBOLO;DESCRIPCION;UNIDAD`, descargue la plantilla). Hay 20 especificaciones de material (acero al carbono, inox, Cr-Mo, baja temperatura, galvanizado, PVC/CPVC, HDPE, cobre).
- **Accesorios y válvulas**: elija el símbolo y toque sobre la tubería; se alinea solo con el eje del tramo. Codos, tees y cruces orientan sus brazos con las tuberías conectadas. No se permite repetir la misma pieza en el mismo punto.
- **Juntas soldadas**: *Generar juntas soldadas automáticas* las coloca en uniones tubo-tubo, codos, tees, reducciones, bridas, caps y olets (solo especificaciones soldadas a tope). Se numeran W1, W2… siguiendo el recorrido de la línea. Cotas, marcas de juntas y ángulos se acomodan solos para no montarse.
- **Tocar**: seleccione un componente para cambiar diámetro, especificación, longitud real, rotarlo o borrarlo.
- **Zoom**: pellizco con dos dedos, Ctrl+rueda o botones. *Lienzo* acerca al área de dibujo.
- **BOM**: se recalcula solo. La cantidad se puede ajustar a mano (deje vacío para volver al cálculo). *Añadir consumible* agrega soldadura, tintas, discos, etc.
- **Exportar**: *Excel* (.xlsx con formato: rótulo, BOM, totales de ML y juntas, y hoja de componentes con marcas W#/T#) y *PDF A3* (imprimir → Guardar como PDF, A3 horizontal).
- **Guardar**: el borrador se guarda solo en el equipo; *Guardar proyecto (.json)* para compartir o archivar.

Atajos PC: Ctrl+Z / Ctrl+Y, Supr, Esc, R (rotar), T (tubería), V (tocar), H (mover), +/−, 0 (ajustar).

## Archivos

- `index.html` – aplicación completa (HTML + CSS + JS, sin dependencias de CDN).
- `vendor/xlsx.bundle.js` – xlsx-js-style 1.2.0 (SheetJS 0.18.5 con estilos, Apache-2.0) para exportar .xlsx con formato sin internet.
- `manifest.webmanifest`, `sw.js`, `icons/` – instalación y funcionamiento sin conexión. Al publicar cambios suba `VERSION` en `sw.js`.
