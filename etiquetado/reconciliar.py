"""Guía la sesión de reconciliación entre las dos personas que etiquetaron.

Lee etiquetado/etiquetas/<persona>-<track>.json, mide cuánto coinciden y
recorre una por una las notas en desacuerdo para elegir la etiqueta final.
Guarda después de cada decisión, así se puede cortar y retomar.

    python etiquetado/reconciliar.py movilidad            # sesión + informe
    python etiquetado/reconciliar.py movilidad --informe  # solo el informe
    python etiquetado/reconciliar.py --selfcheck

Salida en etiquetado/reconciliacion/: <track>-gold.json y <track>-informe.md.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
SALIDA = DIR / "reconciliacion"
# El alcance ya no se etiqueta: sale de la fuente (scripts/diccionarios/alcance_fuentes.py).
CAMPOS = ("relevante", "tipo", "categorias_problema", "categorias_solucion", "categoria_otra")
TIPOS = {"p": "problema", "s": "solucion", "a": "ambas"}
# Categorías renombradas después de etiquetar: los JSON viejos se leen con el nombre nuevo.
RENOMBRADAS = {"GESTION_DEFICIENTE_RESIDUOS_ESPECIALES_RAEE": "GESTION_DEFICIENTE_RESIDUOS"}


# ---------- carga ----------

def leer_js(ruta, claves_sin_comillas=False):
    """Lee un `window.X = {...};` como dict. config.js tiene claves sin comillas."""
    txt = ruta.read_text(encoding="utf-8")
    txt = re.sub(r"^\s*//.*$", "", txt, flags=re.M)
    txt = txt.split("=", 1)[1].strip().rstrip(";")
    if claves_sin_comillas:
        txt = re.sub(r"([{,]\s*)(\w+)\s*:", r'\1"\2":', txt)
    return json.loads(txt)


def cargar(track):
    archivos = sorted((DIR / "etiquetas").glob(f"*-{track}.json"))
    if len(archivos) != 2:
        sys.exit(f"Se esperaban 2 archivos *-{track}.json y hay {len(archivos)}.")
    personas, etiquetas = [], []
    muestra = leer_js(DIR / "muestra.js")
    for a in archivos:
        d = json.loads(a.read_text(encoding="utf-8"))
        if d["muestra_version"] != muestra["version"]:
            sys.exit(f"{a.name} es de la muestra {d['muestra_version']}, no de {muestra['version']}.")
        personas.append(d["persona"].capitalize())
        for e in d["etiquetas"]:
            e["categorias_problema"] = [RENOMBRADAS.get(c, c) for c in e.get("categorias_problema") or []]
        etiquetas.append({e["id"]: e for e in d["etiquetas"]})
    config = leer_js(DIR / "config.js", claves_sin_comillas=True)
    return muestra, config, personas, etiquetas


# ---------- comparación y métricas ----------

def normalizar(e):
    e = e or {}
    otra = (e.get("categoria_otra") or "").strip().lower() or None
    return {
        "relevante": e.get("relevante"),
        "tipo": e.get("tipo"),
        "categorias_problema": sorted(e.get("categorias_problema") or []),
        "categorias_solucion": sorted(e.get("categorias_solucion") or []),
        "categoria_otra": otra,
    }


def diferencias(a, b):
    na, nb = normalizar(a), normalizar(b)
    return [c for c in CAMPOS if na[c] != nb[c]]


def kappa(a, b):
    """Kappa de Cohen entre dos listas de etiquetas. None si no se puede calcular."""
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    if pe == 1:
        return 1.0 if po == 1 else None
    return (po - pe) / (1 - pe)


def jaccard(a, b):
    sa = {"P:" + c for c in a.get("categorias_problema") or []} | {"S:" + c for c in a.get("categorias_solucion") or []}
    sb = {"P:" + c for c in b.get("categorias_problema") or []} | {"S:" + c for c in b.get("categorias_solucion") or []}
    return 1.0 if not (sa | sb) else len(sa & sb) / len(sa | sb)


def es_otra(cat):
    return bool(re.match(r"OTR[OA]_", cat or ""))


# ---------- informe ----------

def pct(x, n):
    return f"{x} de {n} ({100 * x / n:.0f} %)" if n else "—"


def num(v):
    return "—" if v is None else f"{v:.2f}".replace(".", ",")


def informe(track, muestra, config, personas, etiquetas, gold):
    A, B = etiquetas
    p1, p2 = personas
    notas = muestra[track]
    ids = [n["id"] for n in notas]
    titulo = {n["id"]: n["titulo"] for n in notas}
    n = len(ids)

    acuerdo_total = sum(not diferencias(A.get(i), B.get(i)) for i in ids)
    rel_a = [A.get(i, {}).get("relevante") for i in ids]
    rel_b = [B.get(i, {}).get("relevante") for i in ids]
    ambos = [i for i in ids if A.get(i, {}).get("relevante") and B.get(i, {}).get("relevante")]
    tipo_a = [A[i]["tipo"] for i in ambos]
    tipo_b = [B[i]["tipo"] for i in ambos]
    jac = sum(jaccard(A[i], B[i]) for i in ambos) / len(ambos) if ambos else None

    L = [
        f"# Reconciliación · {track}",
        "",
        f"Muestra `{muestra['version']}` · {p1} y {p2} · generado el {datetime.now():%d/%m/%Y %H:%M}.",
        "",
        "## Acuerdo antes de reconciliar",
        "",
        "Con 25 notas, el kappa es orientativo. Mide el acuerdo descontando el azar:",
        "menos de 0,4 es bajo, de 0,4 a 0,6 moderado, y más de 0,6 bueno.",
        "",
        "| Medida | Valor |",
        "|---|---|",
        f"| Notas con acuerdo en todos los campos | {pct(acuerdo_total, n)} |",
        f"| Relevancia: acuerdo | {pct(sum(x == y for x, y in zip(rel_a, rel_b)), n)} |",
        f"| Relevancia: kappa | {num(kappa(rel_a, rel_b))} |",
        f"| Relevantes para {p1} / para {p2} | {sum(x is True for x in rel_a)} / {sum(x is True for x in rel_b)} |",
        f"| Tipo, en las {len(ambos)} relevantes para los dos: acuerdo | {pct(sum(x == y for x, y in zip(tipo_a, tipo_b)), len(ambos))} |",
        f"| Tipo: kappa | {num(kappa(tipo_a, tipo_b))} |",
        f"| Categorías: superposición media (Jaccard, 1 = idénticas) | {num(jac)} |",
        "",
        "## Uso de categorías",
        "",
        "Las que usó una sola persona, o las dos pero en notas distintas, son candidatas a definir mejor.",
        "",
        f"| Categoría | {p1} | {p2} | Los dos en la misma nota |",
        "|---|---:|---:|---:|",
    ]
    for lado, clave in (("problemas", "categorias_problema"), ("soluciones", "categorias_solucion")):
        for cat in config["tracks"][track][lado]:
            ua = sum(cat in (A.get(i, {}).get(clave) or []) for i in ids)
            ub = sum(cat in (B.get(i, {}).get(clave) or []) for i in ids)
            both = sum(cat in (A.get(i, {}).get(clave) or []) and cat in (B.get(i, {}).get(clave) or []) for i in ids)
            L.append(f"| `{cat}` | {ua} | {ub} | {both} |")

    otras = [(p, e["categoria_otra"], titulo[i]) for p, E in zip(personas, etiquetas)
             for i, e in E.items() if e.get("categoria_otra") and i in titulo]
    L += ["", "## Texto libre en las categorías \"otro\"", "",
          "Lo que se repite acá puede pasar a ser una categoría nueva.", ""]
    L += [f"- **{p}:** {t} — _{ti}_" for p, t, ti in otras] or ["- Nadie usó texto libre."]

    desac = [(i, diferencias(A.get(i), B.get(i))) for i in ids]
    desac = [(i, d) for i, d in desac if d]
    L += ["", f"## Desacuerdos ({len(desac)})", "", "| Nota | Campos que difieren |", "|---|---|"]
    L += [f"| {titulo[i][:90]} | {', '.join(d)} |" for i, d in desac]

    if gold["etiquetas"]:
        decididas = [g for g in gold["etiquetas"] if g["origen"] != "acuerdo"]
        L += ["", f"## Decisiones de la reconciliación ({len(decididas)} de {len(desac)})", "",
              "Las notas de esta tabla son la base de la guía de etiquetado.", "",
              "| Nota | Se quedó con | Por qué / regla |", "|---|---|---|"]
        L += [f"| {titulo[g['id']][:90]} | {g['origen']} | {g['nota_reconciliacion'] or ''} |" for g in decididas]

    ruta = SALIDA / f"{track}-informe.md"
    ruta.write_text("\n".join(L) + "\n", encoding="utf-8")
    return ruta


# ---------- sesión interactiva ----------

def preguntar(texto, validas):
    while True:
        r = input(texto).strip().lower()
        if r in validas:
            return r
        print(f"  Opción no válida. Opciones: {', '.join(sorted(validas))}")


def elegir(titulo, opciones, varias):
    print(f"  {titulo}:")
    for k, o in enumerate(opciones, 1):
        print(f"    {k:>2}. {o}")
    while True:
        r = input("  Números separados por coma: " if varias else "  Número: ").strip()
        try:
            idx = [int(x) for x in r.split(",") if x.strip()]
        except ValueError:
            idx = []
        if idx and all(1 <= k <= len(opciones) for k in idx) and (varias or len(idx) == 1):
            elegidas = list(dict.fromkeys(opciones[k - 1] for k in idx))
            return elegidas if varias else elegidas[0]
        print("  Respuesta no válida.")


def etiqueta_nueva(cfg):
    if preguntar("  ¿Relevante? [s/n]: ", {"s", "n"}) == "n":
        return {"relevante": False, "tipo": None, "categorias_problema": [], "categorias_solucion": [],
                "categoria_otra": None}
    tipo = TIPOS[preguntar("  Tipo [p]roblema [s]olución [a]mbas: ", set(TIPOS))]
    cp = elegir("Categorías de problema", cfg["problemas"], True) if tipo in ("problema", "ambas") else []
    cs = elegir("Categorías de solución", cfg["soluciones"], True) if tipo in ("solucion", "ambas") else []
    otra = (input("  ¿Cuál es el \"otro\"? (texto libre): ").strip() or None) if any(map(es_otra, cp + cs)) else None
    return {"relevante": True, "tipo": tipo, "categorias_problema": cp, "categorias_solucion": cs,
            "categoria_otra": otra}


def mostrar(valor):
    if isinstance(valor, list):
        return ", ".join(valor) or "—"
    return {True: "sí", False: "no", None: "—"}.get(valor, valor)


def mostrar_nota(k, total, nota, personas, a, b, difs):
    print("\n" + "=" * 78)
    print(f"Desacuerdo {k} de {total}")
    print(f"{nota['titulo']}\n{nota['fuente']} · {nota['fecha']} · {nota['url']}")
    if nota["bajada"]:
        print(f"\n{nota['bajada']}")
    cuerpo = nota["body"]
    print("\n" + cuerpo[:900] + (" […]" if len(cuerpo) > 900 else ""))
    print("\n" + "-" * 78)
    ancho = max(map(len, personas)) + 1
    for c in CAMPOS:
        if c in difs:
            print(f"* {c}")
            for p, e in zip(personas, (a, b)):
                print(f"    {p + ':':<{ancho}} {mostrar((e or {}).get(c))}")
        else:
            print(f"  {c}: {mostrar((a or {}).get(c))}")
    for p, e in zip(personas, (a, b)):
        if (e or {}).get("comentario"):
            print(f"  Comentario de {p}: {e['comentario']}")
    print("  (* = difieren)")


def registro(id_, etiqueta, origen, nota, comentarios):
    r = {"id": id_}
    r.update({c: etiqueta.get(c) for c in CAMPOS})
    r["categorias_problema"] = r["categorias_problema"] or []
    r["categorias_solucion"] = r["categorias_solucion"] or []
    r.update({"origen": origen, "nota_reconciliacion": nota, "comentarios": comentarios})
    return r


def guardar(ruta, gold, ids):
    orden = {i: k for k, i in enumerate(ids)}
    gold["etiquetas"].sort(key=lambda g: orden[g["id"]])
    gold["actualizado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ruta.write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sesion(track, muestra, config, personas, etiquetas, gold, ruta_gold):
    A, B = etiquetas
    notas = muestra[track]
    ids = [n["id"] for n in notas]
    hechas = {g["id"] for g in gold["etiquetas"]}

    def comentarios(i):
        return {p.lower(): E.get(i, {}).get("comentario") or "" for p, E in zip(personas, etiquetas)}

    # Las notas en las que coinciden pasan directo al gold.
    for i in ids:
        if i not in hechas and not diferencias(A.get(i), B.get(i)):
            gold["etiquetas"].append(registro(i, A.get(i, {}), "acuerdo", "", comentarios(i)))
    guardar(ruta_gold, gold, ids)
    hechas = {g["id"] for g in gold["etiquetas"]}

    # Primero las que difieren en relevancia, después en tipo, después el resto.
    pend = [(n, diferencias(A.get(n["id"]), B.get(n["id"]))) for n in notas if n["id"] not in hechas]
    pend.sort(key=lambda x: 0 if "relevante" in x[1] else 1 if "tipo" in x[1] else 2)
    print(f"\n{track}: {len(hechas)} notas ya en el gold, {len(pend)} desacuerdos por resolver.")

    p1, p2 = personas
    for k, (nota, difs) in enumerate(pend, 1):
        i = nota["id"]
        mostrar_nota(k, len(pend), nota, personas, A.get(i), B.get(i), difs)
        op = preguntar(f"\n[1] {p1}  [2] {p2}  [n] nueva  [s] saltar  [q] salir y guardar: ", {"1", "2", "n", "s", "q"})
        if op == "q":
            break
        if op == "s":
            continue
        if op == "n":
            etiqueta, origen = etiqueta_nueva(config["tracks"][track]), "nueva"
        else:
            etiqueta, origen = (A if op == "1" else B).get(i, {}), personas[int(op) - 1].lower()
        nota_rec = input("  ¿Por qué? Regla para la guía (opcional): ").strip()
        gold["etiquetas"].append(registro(i, etiqueta, origen, nota_rec, comentarios(i)))
        guardar(ruta_gold, gold, ids)

    faltan = len(ids) - len(gold["etiquetas"])
    print(f"\nGold: {len(gold['etiquetas'])} de {len(ids)} notas en {ruta_gold}" + (f" (faltan {faltan})." if faltan else "."))


# ---------- entrada ----------

def selfcheck():
    assert kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1.0
    assert kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == 0.0
    assert kappa([True] * 4, [True] * 4) == 1.0
    assert kappa([], []) is None
    assert jaccard({"categorias_problema": ["X", "Y"]}, {"categorias_problema": ["X"]}) == 0.5
    assert jaccard({}, {}) == 1.0
    assert diferencias({"categorias_problema": ["B", "A"], "categoria_otra": " Ruido "},
                       {"categorias_problema": ["A", "B"], "categoria_otra": "ruido"}) == []
    assert diferencias({"relevante": True}, None) == ["relevante"]
    assert es_otra("OTRO_PROBLEMA_MOVILIDAD") and es_otra("OTRA_SOLUCION_RESIDUOS") and not es_otra("CONGESTION_Y_DEMORAS")
    cfg = leer_js(DIR / "config.js", claves_sin_comillas=True)
    assert {"movilidad", "residuos"} <= set(cfg["tracks"])
    print("selfcheck OK")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("track", nargs="?", choices=["movilidad", "residuos"])
    ap.add_argument("--informe", action="store_true", help="solo genera el informe, sin sesión")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()
    if args.selfcheck:
        return selfcheck()
    if not args.track:
        ap.error("falta el track: movilidad o residuos")

    muestra, config, personas, etiquetas = cargar(args.track)
    SALIDA.mkdir(exist_ok=True)
    ruta_gold = SALIDA / f"{args.track}-gold.json"
    gold = (json.loads(ruta_gold.read_text(encoding="utf-8")) if ruta_gold.exists() else
            {"track": args.track, "muestra_version": muestra["version"], "personas": personas, "etiquetas": []})

    if not args.informe:
        try:
            sesion(args.track, muestra, config, personas, etiquetas, gold, ruta_gold)
        except (KeyboardInterrupt, EOFError):
            print("\nCortado. Lo decidido hasta acá quedó guardado.")
    print(f"Informe: {informe(args.track, muestra, config, personas, etiquetas, gold)}")


if __name__ == "__main__":
    main()
