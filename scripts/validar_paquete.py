# -*- coding: utf-8 -*-
"""Validación de integridad del paquete del tablero RUFE.

Ejecutar con VALIDAR.bat o:  python scripts/validar_paquete.py
No requiere librerías externas.
"""
import json, os, sys, csv, io

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok, avisos, errores = [], [], []


def ruta(*p):
    return os.path.join(RAIZ, *p)


def leer_json(rel):
    with io.open(ruta(rel), encoding="utf-8-sig") as f:
        return json.load(f)


# ---- 1. archivos obligatorios -------------------------------------------
OBLIG = ["index.html", "MANIFIESTO.json", "INICIAR_TABLERO.bat",
         "data/municipios_valle.geojson", "data/centros_poblados.json",
         "data/datos_rufe.csv", "data/config.json"]
for r in OBLIG:
    if os.path.isfile(ruta(*r.split("/"))):
        ok.append("existe %s (%d KB)" % (r, round(os.path.getsize(ruta(*r.split("/"))) / 1024)))
    else:
        errores.append("FALTA el archivo %s" % r)
if errores:
    print("\n".join("  [ERROR] " + e for e in errores))
    sys.exit(1)

# ---- 2. geometrías -------------------------------------------------------
gj = leer_json("data/municipios_valle.geojson")
muni = {f["properties"]["code"]: f["properties"] for f in gj["features"]}
if len(muni) == 42:
    ok.append("42 municipios en el GeoJSON, sin códigos DIVIPOLA repetidos"
              if len(muni) == len(gj["features"]) else "42 municipios")
else:
    errores.append("el GeoJSON tiene %d municipios y deberían ser 42" % len(muni))

sin_geom = [c for c, p in muni.items() if not c.isdigit() or len(c) != 5]
if sin_geom:
    errores.append("códigos DIVIPOLA con formato inválido: %s" % ", ".join(sin_geom))

sin_aro = [p["name"] for p in muni.values() if p.get("aro") in (None, "", "SIN_ASIGNAR")]
if sin_aro:
    avisos.append("municipios sin ARO asignada: %s" % ", ".join(sin_aro))
else:
    reparto = {}
    for p in muni.values():
        reparto[p["aro"]] = reparto.get(p["aro"], 0) + 1
    ok.append("ARO asignada a los 42 municipios (%s)" %
              ", ".join("%s %d" % (k, v) for k, v in sorted(reparto.items())))

# ---- 3. centros poblados -------------------------------------------------
pts = leer_json("data/centros_poblados.json")
ok.append("%d centros poblados con coordenadas" % len(pts))

por_muni = {}
for p in pts:
    por_muni.setdefault(p["code"], []).append(p)

huerfanos = sorted(set(p["code"] for p in pts) - set(muni))
if huerfanos:
    avisos.append("centros poblados cuyo municipio no está en el GeoJSON: %s" % ", ".join(huerfanos))

sin_pts = [muni[c]["name"] for c in muni if c not in por_muni]
if sin_pts:
    errores.append("municipios sin ningún centro poblado (no aparecerían en el mapa de calor): %s"
                   % ", ".join(sin_pts))
else:
    ok.append("los 42 municipios tienen al menos un centro poblado")

sin_cab = [muni[c]["name"] for c, ps in por_muni.items()
           if c in muni and not any(p["cm"] for p in ps)]
if sin_cab:
    errores.append("municipios sin cabecera marcada (cm=1), el reparto 80/20 fallaría: %s"
                   % ", ".join(sin_cab))
else:
    ok.append("los 42 municipios tienen cabecera marcada para el reparto 80/20")

fuera = [p["nombre"] for p in pts
         if not (-78.0 < p["lon"] < -75.0 and 3.0 < p["lat"] < 5.3)]
if fuera:
    avisos.append("puntos fuera del recuadro del Valle: %s" % ", ".join(fuera[:5]))

# ---- 4. datos RUFE -------------------------------------------------------
with io.open(ruta("data", "datos_rufe.csv"), encoding="utf-8-sig") as f:
    filas = list(csv.DictReader(f))

req = {"codigo_divipola", "municipio", "registros_rufe"}
faltan_col = req - set(filas[0].keys() if filas else [])
if faltan_col:
    errores.append("al CSV le faltan columnas: %s" % ", ".join(sorted(faltan_col)))
else:
    total = 0
    malos, no_cruzan = [], []
    for r in filas:
        try:
            v = int(float(r["registros_rufe"]))
            if v < 0:
                malos.append(r["municipio"])
            total += v
        except (ValueError, TypeError):
            malos.append(r["municipio"])
        if r["codigo_divipola"].strip() not in muni:
            no_cruzan.append(r["municipio"])
    if malos:
        errores.append("valores no numéricos o negativos: %s" % ", ".join(malos))
    if no_cruzan:
        errores.append("filas que no cruzan por DIVIPOLA: %s" % ", ".join(no_cruzan))
    else:
        ok.append("las %d filas del CSV cruzan por DIVIPOLA con la cartografía" % len(filas))

    aros_ok = {"NORTE", "CENTRO", "SUR"}
    raras = sorted(set(r.get("aro", "").strip().upper() for r in filas) - aros_ok - {""})
    if raras:
        errores.append("valores de ARO no reconocidos en el CSV (esos municipios podrían "
                       "quedar fuera de los filtros): %s" % ", ".join(raras))
    else:
        ok.append("todas las filas del CSV tienen ARO válida")

    sin_dato = [muni[c]["name"] for c in muni
                if c not in set(r["codigo_divipola"].strip() for r in filas)]
    if sin_dato:
        avisos.append("municipios sin dato RUFE (se dibujan en gris): %s" % ", ".join(sin_dato))
    ok.append("total de registros RUFE en el CSV: %s" % format(total, ",d").replace(",", "."))

# ---- 5. configuración ----------------------------------------------------
cfg = leer_json("data/config.json")
for k in ("titulo", "corte", "fuente", "reparto_cabecera", "nota_metodologica"):
    if not cfg.get(k):
        avisos.append("config.json sin '%s'" % k)
w = cfg.get("reparto_cabecera")
if not isinstance(w, (int, float)) or not 0 < w <= 1:
    errores.append("reparto_cabecera debe ser un número entre 0 y 1 (actual: %r)" % w)
else:
    ok.append("reparto cabecera/resto: %d%% / %d%%" % (round(w * 100), round((1 - w) * 100)))

# ---- informe -------------------------------------------------------------
print("")
print("  VALIDACION DEL PAQUETE - Tablero RUFE Valle del Cauca")
print("  " + "-" * 56)
for o in ok:
    print("  [OK]     " + o)
for a in avisos:
    print("  [AVISO]  " + a)
for e in errores:
    print("  [ERROR]  " + e)
print("  " + "-" * 56)
if errores:
    print("  Resultado: %d error(es). El tablero puede no funcionar bien." % len(errores))
    sys.exit(1)
print("  Resultado: paquete integro. %d avisos." % len(avisos))
print("  Abre el tablero con INICIAR_TABLERO.bat")
