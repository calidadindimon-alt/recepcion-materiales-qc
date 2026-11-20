# Copia de respaldo del CAD en Supabase

Proyecto Supabase `indimon-cad-respaldo` (ref `nlbzhdqfiyrlhpiinbuh`). La app sigue usando Firebase; después de subir una
línea a Firestore avisa a la función `respaldo` con los identificadores. La función lee esas líneas **directo de Firestore
con el token del usuario** (las reglas de Firebase deciden qué puede copiar) y las guarda en:

- `respaldo_lineas`: la última versión de cada línea (incluye las borradas, marcadas con `borrada`).
- `respaldo_versiones`: las últimas 30 versiones de cada línea.

Las tablas tienen RLS sin políticas y sin permisos para `anon`/`authenticated`: nadie las lee ni escribe desde internet;
solo la función (llave de servicio, del lado del servidor) y el panel de Supabase.

`functions/respaldo/index.ts` y `migrations/` son copia de lo que está publicado, para referencia.
