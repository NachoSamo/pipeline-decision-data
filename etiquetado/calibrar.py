"""Compara etiquetadores LLM con el gold del equipo y arma la referencia de movilidad.

Calibración: lee etiquetado/referencia/movilidad-calibracion-<modelo>.json (las 25 notas
del gold etiquetadas por cada modelo) y escribe calibracion-informe.md con el acuerdo de
cada modelo con el equipo. Sirve para elegir qué modelo etiqueta las 300 notas.

Unión: lee movilidad-referencia-parte{1,2,3}.json (125 notas cada una, 25 del gold),
mide el acuerdo de cada parte con el gold y escribe movilidad-referencia.json (las 300
notas que no son del gold) y movilidad-referencia-informe.md.

    python etiquetado/calibrar.py --selfcheck
    python etiquetado/calibrar.py
    python etiquetado/calibrar.py --unir
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))
from reconciliar import jaccard, kappa, leer_js, num, pct  # noqa: E402

REF = DIR / "referencia"
GOLD = DIR / "reconciliacion" / "movilidad-gold.json"
MOTIVOS = [
    "problema_o_solucion_concreta", "movilidad_de_pasada", "seguridad_vial", "politica_o_economia_sin_medida",
    "otro_track_ambiental", "otro_tema", "nota_de_color", "gestion_sin_problema_ni_solucion",
]
TIPOS = {"problema", "solucion", "ambas"}


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def categorias():
    cfg = leer_js(DIR / "config.js", claves_sin_comillas=True)["tracks"]["movilidad"]
    return set(cfg["problemas"]), set(cfg["soluciones"])


def validar(etiquetas, ids_esperados, cats):
    """Lista de problemas de formato. Vacía si todo está bien."""
    probs, sols = cats
    errores = []
    ids = [e.get("id") for e in etiquetas]
    if len(ids) != len(set(ids)):
        errores.append("hay id repetidos")
    if set(ids) != set(ids_esperados):
        errores.append(f"faltan {len(set(ids_esperados) - set(ids))} y sobran {len(set(ids) - set(ids_esperados))} id")
    for e in etiquetas:
        donde = str(e.get("id"))[:60]
        if not isinstance(e.get("relevante"), bool):
            errores.append(f"{donde}: relevante no es bool")
        if e.get("motivo") not in MOTIVOS:
            errores.append(f"{donde}: motivo inválido {e.get('motivo')!r}")
        if e.get("relevante") and e.get("tipo") not in TIPOS:
            errores.append(f"{donde}: tipo inválido {e.get('tipo')!r}")
        malas = set(e.get("categorias_problema") or []) - probs | set(e.get("categorias_solucion") or []) - sols
        if malas:
            errores.append(f"{donde}: categorías inválidas {sorted(malas)}")
    return errores


def acuerdo(etiquetas, gold):
    """Métricas de un etiquetador contra el gold, sobre los id del gold."""
    por_id = {e["id"]: e for e in etiquetas}
    ids = [i for i in gold if i in por_id]
    rel_g = [gold[i]["relevante"] for i in ids]
    rel_m = [bool(por_id[i].get("relevante")) for i in ids]
    ambos = [i for i in ids if gold[i]["relevante"] and por_id[i].get("relevante")]
    return {
        "n": len(ids),
        "acuerdo_rel": sum(a == b for a, b in zip(rel_g, rel_m)),
        "kappa_rel": kappa(rel_g, rel_m),
        "rel_gold": sum(rel_g),
        "rel_modelo": sum(rel_m),
        "ambos_rel": len(ambos),
        "acuerdo_tipo": sum(gold[i]["tipo"] == por_id[i].get("tipo") for i in ambos),
        "jaccard": sum(jaccard(gold[i], por_id[i]) for i in ambos) / len(ambos) if ambos else None,
        "difieren": [i for i in ids if gold[i]["relevante"] != bool(por_id[i].get("relevante"))],
    }


def filas_acuerdo(nombre, m):
    return (
        f"| {nombre} | {pct(m['acuerdo_rel'], m['n'])} | {num(m['kappa_rel'])} | {m['rel_modelo']} de {m['n']} "
        f"| {pct(m['acuerdo_tipo'], m['ambos_rel'])} | {num(m['jaccard'])} |"
    )


ENCABEZADO_ACUERDO = [
    "| Etiquetador | Relevancia: acuerdo | Relevancia: kappa | Marcó relevantes | Tipo, en relevantes para los dos "
    "| Categorías (Jaccard) |",
    "|---|---|---|---|---|---|",
]


def cargar_gold():
    return {e["id"]: e for e in leer(GOLD)["etiquetas"]}


def titulos():
    return {n["id"]: n["titulo"] for n in leer(REF / "movilidad-calibracion.json")["notas"]}


def fecha():
    return f"{datetime.now():%d/%m/%Y %H:%M}"


def calibracion():
    gold, cats, tit = cargar_gold(), categorias(), titulos()
    archivos = sorted(REF.glob("movilidad-calibracion-*.json"))
    if not archivos:
        sys.exit("No hay archivos movilidad-calibracion-<modelo>.json en etiquetado/referencia/.")
    lineas = [
        "# Calibración de etiquetadores · movilidad", "",
        f"Generado el {fecha()} con `etiquetado/calibrar.py`. Cada modelo etiquetó las 25 notas del gold del equipo "
        "(`reconciliacion/movilidad-gold.json`) con la guía, sin ver las etiquetas.", "",
        "**Medición débil:** 25 notas con 4 relevantes. Un solo acierto o error mueve mucho las cifras. "
        "Sirve para descartar modelos que se apartan claramente del criterio del equipo, no para afinar.", "",
        "Kappa mide el acuerdo descontando el azar: menos de 0,4 es bajo, de 0,4 a 0,6 moderado y más de 0,6 bueno.", "",
        "## Acuerdo con el gold", "", *ENCABEZADO_ACUERDO,
    ]
    detalle = []
    for ruta in archivos:
        d = leer(ruta)
        nombre = d.get("etiquetador") or ruta.stem.removeprefix("movilidad-calibracion-")
        errores = validar(d["etiquetas"], gold.keys(), cats)
        m = acuerdo(d["etiquetas"], gold)
        lineas.append(filas_acuerdo(nombre, m))
        detalle += ["", f"### {nombre}", ""]
        detalle.append(f"- **Formato:** {'válido' if not errores else f'{len(errores)} problemas'}.")
        detalle += [f"  - {e}" for e in errores[:10]]
        por_id = {e["id"]: e for e in d["etiquetas"]}
        for i in m["difieren"]:
            e = por_id[i]
            detalle.append(
                f"- Difiere en relevancia: _{tit.get(i, i)[:90]}_. Gold: {gold[i]['relevante']}; "
                f"modelo: {e.get('relevante')} ({e.get('motivo')}). {e.get('comentario') or ''}".rstrip()
            )
    lineas += ["", "## Detalle por etiquetador", *detalle, ""]
    salida = REF / "calibracion-informe.md"
    salida.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Escrito {salida.relative_to(DIR.parent)}")


def contar(etiquetas, clave):
    c = Counter()
    for e in etiquetas:
        valor = e.get(clave)
        for v in valor if isinstance(valor, list) else [valor]:
            if v:
                c[v] += 1
    return c


def tabla(titulo, conteo, total):
    filas = [f"## {titulo}", "", "| Valor | Notas |", "|---|---:|"]
    filas += [f"| `{k}` | {pct(v, total)} |" for k, v in conteo.most_common()]
    return filas + [""]


def normalizar_sugerencia(s):
    """Agrupa sugerencias que difieren solo en mayúsculas, espacios o la descripción después de ':'."""
    return re.sub(r"[\s_]+", "_", str(s).split(":")[0].strip()).upper()


def unir():
    gold, cats = cargar_gold(), categorias()
    notas, etiquetas, lineas_acuerdo, errores = {}, [], [], []
    for n in (1, 2, 3):
        entrada = {x["id"]: x for x in leer(REF / f"movilidad-parte{n}.json")["notas"]}
        d = leer(REF / f"movilidad-referencia-parte{n}.json")
        errores += [f"parte {n}: {e}" for e in validar(d["etiquetas"], entrada.keys(), cats)]
        lineas_acuerdo.append(filas_acuerdo(f"parte {n} ({d.get('etiquetador', '?')})", acuerdo(d["etiquetas"], gold)))
        for e in d["etiquetas"]:
            if e["id"] not in gold:
                etiquetas.append(e)
                notas[e["id"]] = entrada[e["id"]]
    if errores:
        sys.exit("Formato inválido:\n" + "\n".join(errores[:30]))
    assert len(etiquetas) == len({e["id"] for e in etiquetas}) == 300

    (REF / "movilidad-referencia.json").write_text(
        json.dumps({"track": "movilidad", "generado": fecha(), "etiquetas": etiquetas}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    rel = [e for e in etiquetas if e["relevante"]]
    por_dataset = Counter(notas[e["id"]]["dataset"] for e in etiquetas)
    rel_dataset = Counter(notas[e["id"]]["dataset"] for e in rel)
    rel_fuente = Counter(notas[e["id"]]["fuente"] for e in rel)
    tot_fuente = Counter(notas[e["id"]]["fuente"] for e in etiquetas)
    sugerencias = Counter(normalizar_sugerencia(e["categoria_sugerida"]) for e in etiquetas if e.get("categoria_sugerida"))
    ejemplos = {}
    for e in etiquetas:
        if e.get("categoria_sugerida"):
            ejemplos.setdefault(normalizar_sugerencia(e["categoria_sugerida"]), []).append(notas[e["id"]]["titulo"][:80])

    lineas = [
        "# Referencia de movilidad · 300 notas", "",
        f"Generado el {fecha()} con `etiquetado/calibrar.py --unir`. Etiquetas de un LLM con la guía de movilidad, "
        "sobre una muestra al azar de los Parquet filtrados. No reemplaza al gold del equipo.", "",
        "## Acuerdo de cada parte con el gold (25 notas)", "", *ENCABEZADO_ACUERDO, *lineas_acuerdo, "",
        "## Relevantes", "",
        f"- **Total:** {pct(len(rel), len(etiquetas))}.",
        *[f"- **{ds}:** {pct(rel_dataset[ds], por_dataset[ds])}." for ds in sorted(por_dataset)], "",
        "| Fuente | Relevantes |", "|---|---:|",
        *[f"| {f} | {pct(rel_fuente[f], t)} |" for f, t in tot_fuente.most_common()], "",
        *tabla("Motivos", contar(etiquetas, "motivo"), len(etiquetas)),
        *tabla("Tipos (relevantes)", contar(rel, "tipo"), len(rel)),
        *tabla("Categorías de problema", contar(rel, "categorias_problema"), len(rel)),
        *tabla("Categorías de solución", contar(rel, "categorias_solucion"), len(rel)),
        "## Categorías sugeridas", "",
        "Para que el equipo decida si alguna entra a la taxonomía antes de clasificar en Kaggle.", "",
        "| Sugerencia | Notas | Ejemplos |", "|---|---:|---|",
        *[f"| `{s}` | {n} | {'; '.join(ejemplos[s][:3])} |" for s, n in sugerencias.most_common()], "",
    ]
    (REF / "movilidad-referencia-informe.md").write_text("\n".join(lineas), encoding="utf-8")
    print(f"Referencia: {len(etiquetas)} notas, {len(rel)} relevantes. Informe en etiquetado/referencia/.")


def selfcheck():
    cats = ({"CONGESTION_Y_DEMORAS"}, {"REDES_FERROVIARIAS_Y_SUBTE"})
    buena = {"id": "a", "relevante": True, "motivo": "problema_o_solucion_concreta", "tipo": "ambas",
             "categorias_problema": ["CONGESTION_Y_DEMORAS"], "categorias_solucion": ["REDES_FERROVIARIAS_Y_SUBTE"]}
    mala = {"id": "b", "relevante": "si", "motivo": "x", "tipo": None, "categorias_problema": ["INVENTADA"]}
    assert validar([buena], ["a"], cats) == []
    assert len(validar([mala], ["a"], cats)) == 5
    gold = {"a": {"relevante": True, "tipo": "ambas", "categorias_problema": ["CONGESTION_Y_DEMORAS"]},
            "b": {"relevante": False, "tipo": None}}
    m = acuerdo([buena, {"id": "b", "relevante": True}], gold)
    assert m["acuerdo_rel"] == 1 and m["acuerdo_tipo"] == 1 and m["jaccard"] == 0.5 and m["difieren"] == ["b"]
    assert normalizar_sugerencia("transporte de carga: camiones") == normalizar_sugerencia(" Transporte de  CARGA")
    assert {"CONGESTION_Y_DEMORAS"} <= categorias()[0]
    print("selfcheck ok")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--unir", action="store_true", help="une las 3 partes de la referencia")
    args = ap.parse_args()
    selfcheck() if args.selfcheck else unir() if args.unir else calibracion()
