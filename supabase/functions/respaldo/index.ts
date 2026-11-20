// Copia de respaldo del CAD INDIMON: la app manda los identificadores de las líneas que acaba de subir a Firebase
// y el token de Firebase del usuario. Esta función lee esas líneas DIRECTO de Firestore con el mismo token
// (así las reglas de Firebase deciden qué puede copiar cada usuario y nadie puede mandar datos inventados)
// y las guarda en Supabase con la llave de servicio. El público no puede leer ni escribir las tablas.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2.45.4";

const PROYECTO_FIREBASE = "indimon-cad";
const ORIGENES = ["https://calidadindimon-alt.github.io", "http://localhost:8792", "http://localhost:8793"];
const FS = `https://firestore.googleapis.com/v1/projects/${PROYECTO_FIREBASE}/databases/(default)/documents/lineas/`;
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const cors = (origen: string | null) => ({
  "Access-Control-Allow-Origin": origen && ORIGENES.includes(origen) ? origen : ORIGENES[0],
  "Access-Control-Allow-Headers": "authorization, content-type, x-client-info, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Vary": "Origin",
});
const valor = (f: any) => f == null ? null : ("stringValue" in f ? f.stringValue : "booleanValue" in f ? f.booleanValue : "timestampValue" in f ? f.timestampValue : "integerValue" in f ? f.integerValue : null);

Deno.serve(async (req) => {
  const h = cors(req.headers.get("origin"));
  if (req.method === "OPTIONS") return new Response("ok", { headers: h });
  const json = (o: unknown, status = 200) => new Response(JSON.stringify(o), { status, headers: { ...h, "Content-Type": "application/json" } });
  if (req.method !== "POST") return json({ error: "solo POST" }, 405);
  const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return json({ error: "falta el token de Firebase" }, 401);
  let ids: string[] = [];
  try { ids = (await req.json()).ids; } catch (_) { /* cuerpo inválido */ }
  if (!Array.isArray(ids) || !ids.length || ids.length > 50 || ids.some((x) => typeof x !== "string" || !/^[A-Za-z0-9_-]{1,80}$/.test(x))) return json({ error: "ids inválidos" }, 400);

  const copiadas: string[] = [], fallidas: Record<string, string> = {};
  for (const id of ids) {
    const r = await fetch(FS + encodeURIComponent(id), { headers: { Authorization: "Bearer " + token } });
    if (r.status === 401) return json({ error: "token de Firebase no válido o vencido" }, 401);
    if (!r.ok) { fallidas[id] = "firestore " + r.status; continue; }
    const f = (await r.json()).fields || {};
    const actualizado = valor(f.actualizado) || new Date().toISOString();
    let datos: unknown = null, bom: unknown = null;
    try { datos = valor(f.datos) ? JSON.parse(valor(f.datos)) : null; } catch (_) { datos = null; }
    try { bom = valor(f.bom) ? JSON.parse(valor(f.bom)) : null; } catch (_) { bom = null; }
    const fila = { id, obra: valor(f.obra) || "", obra_id: valor(f.obraId) || "", linea: valor(f.linea) || "", datos, bom, borrada: valor(f.borrada) === true,
      actualizado, por_email: valor(f.por), por_nombre: valor(f.porNombre), uid: valor(f.uid) };
    // no repite una versión que ya está guardada (salvo que ahora traiga el listado de materiales y la guardada no)
    const { data: hay } = await db.from("respaldo_lineas").select("actualizado, con_bom:bom->0").eq("id", id).maybeSingle();
    if (hay && new Date(hay.actualizado).getTime() === new Date(actualizado).getTime()) {
      if (!bom || hay.con_bom != null) { copiadas.push(id); continue; }
      const e = (await db.from("respaldo_lineas").update({ bom, recibido: new Date().toISOString() }).eq("id", id)).error;
      if (e) fallidas[id] = e.message; else copiadas.push(id);
      continue;
    }
    const e1 = (await db.from("respaldo_lineas").upsert({ ...fila, recibido: new Date().toISOString() })).error;
    const e2 = e1 ? null : (await db.from("respaldo_versiones").insert({ linea_id: id, obra: fila.obra, linea: fila.linea, datos, borrada: fila.borrada, actualizado, por_email: fila.por_email })).error;
    if (e1 || e2) fallidas[id] = (e1 || e2)!.message; else copiadas.push(id);
  }
  return json({ copiadas, fallidas });
});
