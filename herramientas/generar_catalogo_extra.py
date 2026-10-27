"""Genera catalogo-extra.js: artículos que no vienen en la plantilla QC-F-002 (catalogo.js).

Uso:  python3 herramientas/generar_catalogo_extra.py   (desde la raíz del repositorio)

Filas con las mismas 16 columnas de tblCatalogo más una 17.ª (unidad de compra):
Categoria, Tipo, Designacion, A, B, e, Calc, NormaCS, NormaSS, Nota, PesoTabla, Area, PesoCS, PesoSS, UnidadPeso, Clave, Unidad
UnidadPeso "kg/und" = peso por unidad (accesorios); Calc "TUBO" = peso por metro (kg/m).
"""
import json, math, re

base = open("catalogo.js", encoding="utf-8").read()
cat = json.loads(base[base.index("{"):base.rindex("}") + 1])
TUB = [r for r in cat["tuberia"] if r[0].startswith("Tubería ASME")]   # Tipo, NPS, OD, Cedula, e, kg/m CS, kg/m SS, Clave
filas = []

def fila(categoria, tipo, desig, od, esp, calc, ncs, nss, nota, pcs, pss, upeso, unidad, clave=None):
    r = [categoria, tipo, desig, od if od is not None else "", "", esp if esp is not None else "", calc, ncs, nss, nota, "", "",
         "" if pcs in (None, "") else round(pcs, 3), "" if pss in (None, "") else round(pss, 3), upeso,
         clave or f"{tipo} · {desig}", unidad]
    filas.append(r)

fmt = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
tok = lambda ced: set(re.split(r"\s*/\s*", ced))

# ---------- 1. Stub ends 316L, ficha HECO 690 (ASME B16.9 patrón corto / MSS SP-43 tipo A) ----------
# (NPS, Sch, D, s, L, d4, r, kg, tipo) — seamless (nahtlos) y, donde no hay, soldado (geschw.). kg 0,000 = sin dato.
HECO = """1/2" 10S 21.3 2.11 50.8 34.9 3.18 0.070 S|1/2" 40S 21.3 2.77 50.8 34.9 3.18 0.098 S|3/4" 10S 26.7 2.11 50.8 42.9 3.18 0.100 S|3/4" 40S 26.7 2.87 50.8 42.9 3.18 0.120 S|1" 10S 33.4 2.77 50.8 50.8 3.18 0.151 S|1" 40S 33.4 3.38 50.8 50.8 3.18 0.170 S|1-1/4" 10S 42.2 2.77 50.8 63.5 4.76 0.220 S|1-1/4" 40S 42.2 3.56 50.8 63.5 4.76 0.250 S|1-1/2" 10S 48.3 2.77 50.8 73.0 6.35 0.250 S|1-1/2" 40S 48.3 3.68 50.8 73.0 6.35 0.310 S|2" 10S 60.3 2.77 63.5 92.1 7.94 0.430 S|2" 40S 60.3 3.91 63.5 92.1 7.94 0.610 S|2-1/2" 10S 73.0 3.05 63.5 104.8 7.94 0.570 S|2-1/2" 40S 73.0 5.16 63.5 104.8 7.94 0.800 S|3" 10S 88.9 3.05 63.5 127.0 9.53 0.730 S|3" 40S 88.9 5.49 63.5 127.0 9.53 1.130 S|4" 10S 114.3 3.05 76.2 157.2 11.11 1.090 S|4" 40S 114.3 6.02 76.2 157.2 11.11 1.870 S|5" 10S 141.3 3.40 76.2 185.7 11.11 1.470 S|5" 40S 141.3 6.55 76.2 185.7 11.11 2.280 S|6" 10S 168.3 3.40 88.9 215.9 12.70 2.150 S|6" 40S 168.3 7.11 88.9 215.9 12.70 3.570 S|8" 10S 219.1 3.76 101.6 269.9 12.70 3.220 S|8" 40S 219.1 8.18 101.6 269.9 12.70 9.480 W|10" 10S 273.1 4.19 127.0 323.9 12.70 5.130 S|10" 40S 273.1 9.27 127.0 323.9 12.70 0 W|12" 10S 323.9 4.57 152.4 381.0 12.70 8.160 S|12" 40S 323.9 9.53 152.4 381.0 12.70 0 W|14" 10S 355.6 4.78 152.4 412.8 12.70 9.000 W|16" 10S 406.4 4.78 152.4 469.9 12.70 10.820 W|18" 10S 457.2 4.78 152.4 533.4 12.70 10.500 W|20" 10S 508.0 5.54 152.4 584.2 12.70 0 W|24" 10S 609.6 6.35 152.4 692.2 12.70 19.000 W"""
for x in HECO.split("|"):
    nps, sch, D, s, L, d4, rr, kg, t = x.split()
    D, s, L, d4, kg = float(D), float(s), float(L), float(d4), float(kg)
    nota = f"Ficha HECO 690 · L {fmt(L)} mm · Ø reborde {fmt(d4)} mm" + (" · soldado" if t == "W" else " · sin costura")
    if nps == '8"' and sch == "40S": nota += " · ⚠ peso de la ficha a verificar (parece alto)"
    if not kg: nota += " · la ficha no trae el peso"
    fila("Accesorio tubería", "Stub end 316L corto (HECO)", f"{nps} · {sch}", D, s, "", "N/A", "ASTM A403 WP316L / MSS SP-43 tipo A / ASME B16.9",
         nota, None, kg or None, "kg/und", "und")

# ---------- 2. Codos BW con peso calculado (teorema de Pappus): kg/m del tubo × largo del arco ----------
R_LR = {'1/2"': 38.1, '3/4"': 28.6, '1"': 38.1, '1-1/4"': 47.8, '1-1/2"': 57.2, '2"': 76.2, '2-1/2"': 95.3, '3"': 114.3, '3-1/2"': 133.4,
        '4"': 152.4, '5"': 190.5, '6"': 228.6, '8"': 304.8, '10"': 381.0, '12"': 457.2, '14"': 533.4, '16"': 609.6, '18"': 685.8,
        '20"': 762.0, '24"': 914.4}                     # ASME B16.9 radio largo (centro a cara del codo 90°)
NPS_IN = {'1"': 1, '1-1/4"': 1.25, '1-1/2"': 1.5, '2"': 2, '2-1/2"': 2.5, '3"': 3, '3-1/2"': 3.5, '4"': 4, '5"': 5, '6"': 6, '8"': 8,
          '10"': 10, '12"': 12, '14"': 14, '16"': 16, '18"': 18, '20"': 20, '24"': 24}
R_SR = {k: round(v * 25.4, 1) for k, v in NPS_IN.items()}   # radio corto = 1 × NPS (desde 1")
SCH_CODO = {"5S", "10S", "STD", "40", "40S", "XS", "80", "80S"}
CODOS = [("Codo 90° radio largo BW", R_LR, math.pi / 2), ("Codo 45° radio largo BW", R_LR, math.pi / 4),
         ("Codo 180° radio largo BW", R_LR, math.pi), ("Codo 90° radio corto BW", R_SR, math.pi / 2)]
for nombre, R, ang in CODOS:
    for t in TUB:
        nps, od, ced, e, pcs, pss = t[1], t[2], t[3], t[4], t[5], t[6]
        if nps not in R or not (tok(ced) & SCH_CODO): continue
        arco = R[nps] * ang / 1000
        fila("Accesorio tubería", nombre, f"{nps} · SCH {ced}", od, e, "", "ASTM A234 WPB / ASME B16.9", "ASTM A403 WP304/316 / ASME B16.9",
             f"Peso calculado: kg/m del tubo SCH {ced} × arco ({fmt(arco * 1000, 0)} mm, R {fmt(R[nps])} mm) · verificar con el certificado",
             pcs * arco, pss * arco, "kg/und", "und")

# ---------- 3. Tubería galvanizada ASTM A53 SCH 40 (peso del tubo negro, sin zinc) ----------
for t in TUB:
    if "40" in tok(t[3]) and t[1] in ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '6"']:
        fila("Tubería", "Tubería galvanizada ASTM A53 SCH 40", t[1], t[2], t[4], "TUBO", "ASTM A53 Gr. B galvanizado (ASTM A123/A153)", "N/A",
             "Peso del tubo negro (el zinc suma alrededor de 2-4 %) · roscado NPT o ranurado", t[5], None, "", "tramo")

# ---------- 4. Tubería PVC y CPVC (ASTM D1785 / F441): mismos diámetros y espesores que el acero SCH 40/80 ----------
PVC = [("Tubería PVC SCH 40", "40", 1.40, "ASTM D1785 PVC 1120", '12"'), ("Tubería PVC SCH 80", "80", 1.40, "ASTM D1785 PVC 1120", '12"'),
       ("Tubería CPVC SCH 80", "80", 1.55, "ASTM F441 CPVC 4120", '4"')]
ORDEN = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '6"', '8"', '10"', '12"']
for nombre, sch, dens, norma, hasta in PVC:
    for t in TUB:
        if t[1] in ORDEN[:ORDEN.index(hasta) + 1] and sch in tok(t[3]):
            kgm = math.pi * (t[2] - t[4]) * t[4] * dens / 1000
            fila("Tubería", nombre, t[1], t[2], t[4], "TUBO", norma, norma, f"Peso calculado con densidad {fmt(dens, 2)} g/cm³", kgm, kgm, "", "tramo")

# ---------- 5. Tubería de cobre ASTM B88 tipos K, L y M (OD = nominal + 1/8") ----------
B88 = {  # nominal: (OD pulg, K, L, M) espesores en pulgadas
    '1/4"': (0.375, 0.035, 0.030, None), '3/8"': (0.500, 0.049, 0.035, 0.025), '1/2"': (0.625, 0.049, 0.040, 0.028),
    '5/8"': (0.750, 0.049, 0.042, None), '3/4"': (0.875, 0.065, 0.045, 0.032), '1"': (1.125, 0.065, 0.050, 0.035),
    '1-1/4"': (1.375, 0.065, 0.055, 0.042), '1-1/2"': (1.625, 0.072, 0.060, 0.049), '2"': (2.125, 0.083, 0.070, 0.058),
    '2-1/2"': (2.625, 0.095, 0.080, 0.065), '3"': (3.125, 0.109, 0.090, 0.072), '4"': (4.125, 0.134, 0.110, 0.095)}
for i, tipo in enumerate("KLM"):
    for nps, v in B88.items():
        if v[i + 1] is None: continue
        D, e = v[0] * 25.4, v[i + 1] * 25.4
        kgm = math.pi * (D - e) * e * 8.94 / 1000
        fila("Tubería", f"Tubería de cobre tipo {tipo}", nps, round(D, 2), round(e, 2), "TUBO", "ASTM B88", "ASTM B88",
             f"OD {fmt(D, 2)} mm · pared {fmt(e, 2)} mm · peso calculado (8,94 g/cm³)", kgm, kgm, "", "tramo")

# ---------- 6. Juegos de espárragos ASME B16.5 por clase (cantidad × diámetro) ----------
ESP = {150: {'1/2"': (4, '1/2"'), '3/4"': (4, '1/2"'), '1"': (4, '1/2"'), '1-1/4"': (4, '1/2"'), '1-1/2"': (4, '1/2"'), '2"': (4, '5/8"'),
             '2-1/2"': (4, '5/8"'), '3"': (4, '5/8"'), '3-1/2"': (8, '5/8"'), '4"': (8, '5/8"'), '5"': (8, '3/4"'), '6"': (8, '3/4"'),
             '8"': (8, '3/4"'), '10"': (12, '7/8"'), '12"': (12, '7/8"'), '14"': (12, '1"'), '16"': (16, '1"'), '18"': (16, '1-1/8"'),
             '20"': (20, '1-1/8"'), '24"': (20, '1-1/4"')},
       300: {'1/2"': (4, '1/2"'), '3/4"': (4, '5/8"'), '1"': (4, '5/8"'), '1-1/4"': (4, '5/8"'), '1-1/2"': (4, '3/4"'), '2"': (8, '5/8"'),
             '2-1/2"': (8, '3/4"'), '3"': (8, '3/4"'), '3-1/2"': (8, '3/4"'), '4"': (8, '3/4"'), '5"': (8, '3/4"'), '6"': (12, '3/4"'),
             '8"': (12, '7/8"'), '10"': (16, '1"'), '12"': (16, '1-1/8"'), '14"': (20, '1-1/8"'), '16"': (20, '1-1/4"'), '18"': (24, '1-1/4"'),
             '20"': (24, '1-1/4"'), '24"': (24, '1-1/2"')}}
for clase, tabla in ESP.items():
    for nps, (n, d) in tabla.items():
        fila("Empaque y tornillería", f"Juego de espárragos con tuercas clase {clase}", f"{nps} ({n} × {d})", None, None, "",
             "ASTM A193 B7 / A194 2H", "ASTM A193 B8/B8M / A194 8/8M", f"ASME B16.5 clase {clase}: {n} espárragos de {d} por brida (largo según cara RF/RTJ y empaque)",
             None, None, "", "juego")

# ---------- 7. Soldaduras (consumibles, se reciben en kg) ----------
SOLD = [("Electrodo E6010", "AWS A5.1", ['3/32"', '1/8"', '5/32"']), ("Electrodo E7018", "AWS A5.1", ['3/32"', '1/8"', '5/32"']),
        ("Electrodo E308L-16", "AWS A5.4", ['3/32"', '1/8"']), ("Electrodo E316L-16", "AWS A5.4", ['3/32"', '1/8"']),
        ("Varilla TIG ER70S-2", "AWS A5.18", ['1/16"', '3/32"', '1/8"']), ("Alambre MIG ER70S-6", "AWS A5.18", ['0,035" (0,9 mm)', '0,045" (1,2 mm)']),
        ("Varilla TIG ER308L", "AWS A5.9", ['1/16"', '3/32"', '1/8"']), ("Varilla TIG ER316L", "AWS A5.9", ['1/16"', '3/32"', '1/8"'])]
for tipo, norma, dias in SOLD:
    for d in dias:
        fila("Consumible", tipo, f"Ø {d}", None, None, "", norma, norma, "Se recibe por peso: la cantidad es en kg", 1, 1, "kg/und", "kg")

out = {"fuente": "herramientas/generar_catalogo_extra.py", "catalogo": filas}
with open("catalogo-extra.js", "w", encoding="utf-8") as f:
    f.write("/* Catálogo adicional (no viene en la plantilla QC-F-002): stub ends 316L HECO 690, codos BW con peso calculado,\n"
            "   tubería galvanizada, PVC/CPVC, cobre B88, espárragos B16.5 y soldaduras. Generado por\n"
            "   herramientas/generar_catalogo_extra.py; no editar a mano. */\n")
    f.write("window.CATALOGO_EXTRA = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
from collections import Counter
print(len(filas), "filas", Counter(r[1] for r in filas).most_common(40))
