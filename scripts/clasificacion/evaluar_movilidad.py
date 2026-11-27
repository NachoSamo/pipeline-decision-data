"""Evalúa la salida del clasificador v2 de movilidad contra la referencia de Haiku.

Compara movilidad_clasificado.parquet (la corrida del gate en Kaggle, solo las 300 notas de
la referencia) con etiquetado/referencia/movilidad-referencia.json y escribe gate-informe.md:
relevancia (precisión, recall y kappa, en total y por dataset), tipo, categorías (Jaccard),
JSON inválidos, motivos cruzados y la lista de desacuerdos para leer a mano.

    python scripts/clasificacion/evaluar_movilidad.py --selfcheck
    python scripts/clasificacion/evaluar_movilidad.py [--salida data/resultados/v2-movilidad/gate]
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "etiquetado"))
from reconciliar import jaccard, kappa, num, pct  # noqa: E402

REFERENCIA = RAIZ / "etiquetado" / "referencia" / "movilidad-referencia.json"
NOTAS = [RAIZ / "etiquetado" / "referencia" / f"movilidad-parte{n}.json" for n in (1, 2, 3)]
SALIDA = RAIZ / "data" / "resultados" / "v2-movilidad" / "gate"


def lista(v):
    """Las listas llegan del Parquet como arrays de numpy, o nulas."""
    return [] if v is None or (isinstance(v, float) and pd.isna(v)) else list(v)


def metricas(ref, pred):
    """ref y pred: dict id -> etiqueta. Evalúa sobre los id de ref."""
    ids = list(ref)
    r = [bool(ref[i]["relevante"]) for i in ids]
    p = [bool(pred.get(i, {}).get("relevante")) for i in ids]
    vp = sum(a and b for a, b in zip(r, p))
    ambos = [i for i in ids if ref[i]["relevante"] and pred.get(i, {}).get("relevante")]
    return {
        "n": len(ids), "vp": vp, "ref_rel": sum(r), "pred_rel": sum(p),
        "precision": vp / sum(p) if sum(p) else None,
        "recall": vp / sum(r) if sum(r) else None,
        "kappa": kappa(r, p),
        "ambos": len(ambos),
        "tipo": sum(ref[i].get("tipo") == pred[i].get("tipo") for i in ambos),
        "jaccard": sum(jaccard(ref[i], pred[i]) for i in ambos) / len(ambos) if ambos else None,
    }


def cargar_pred(ruta):
    df = pd.read_parquet(ruta)
    pred = {}
    for f in df.to_dict("records"):
        pred[f["id"]] = {
            "relevante": f.get("relevante") is True,
            "motivo": f.get("motivo"),
            "tipo": f.get("tipo"),
            "categorias_problema": lista(f.get("categorias_problema")),
            "categorias_solucion": lista(f.get("categorias_solucion")),
            "problema": f.get("problema"),
            "error": f.get("error_1") or f.get("error_2"),
        }
    return pred


def informe(ref, pred, notas):
    m = metricas(ref, pred)
    faltan = [i for i in ref if i not in pred]
    errores = [i for i in ref if pred.get(i, {}).get("error")]
    lineas = [
        "# Gate de la clasificación v2 de movilidad", "",
        f"Generado el {datetime.now():%d/%m/%Y %H:%M} con `scripts/clasificacion/evaluar_movilidad.py`. Compara la salida "
        "de Qwen2.5-7B (vLLM, Kaggle) con la referencia de Haiku (300 notas). La referencia tiene criterios dispares en "
        "tarifas, paros, anuncios, aviación y proyectos sin aprobar: parte de los desacuerdos viene de ahí.", "",
        "## Resumen", "",
        "| Medida | Valor | Umbral |", "|---|---|---|",
        f"| Relevancia: recall | {num(m['recall'])} ({m['vp']} de {m['ref_rel']}) | ≥ 0,85 |",
        f"| Relevancia: precisión | {num(m['precision'])} ({m['vp']} de {m['pred_rel']}) | ≥ 0,70 |",
        f"| Relevancia: kappa | {num(m['kappa'])} | |",
        f"| Tipo, en relevantes para los dos | {pct(m['tipo'], m['ambos'])} | |",
        f"| Categorías (Jaccard) | {num(m['jaccard'])} | |",
        f"| Notas sin respuesta | {len(faltan)} de {m['n']} | 0 |",
        f"| JSON inválidos | {len(errores)} de {m['n']} | 0 |", "",
        "## Por dataset", "",
        "| Dataset | Recall | Precisión | Kappa | Relevantes en la referencia | Relevantes para Qwen |",
        "|---|---|---|---|---|---|",
    ]
    for ds in sorted({notas[i]["dataset"] for i in ref}):
        sub = {i: e for i, e in ref.items() if notas[i]["dataset"] == ds}
        d = metricas(sub, pred)
        lineas.append(f"| {ds} | {num(d['recall'])} | {num(d['precision'])} | {num(d['kappa'])} | {d['ref_rel']} | {d['pred_rel']} |")

    cruce = Counter((ref[i]["motivo"], pred.get(i, {}).get("motivo")) for i in ref)
    lineas += ["", "## Motivos: referencia contra Qwen", "", "| Referencia | Qwen | Notas |", "|---|---|---:|"]
    lineas += [f"| `{a}` | `{b}` | {n} |" for (a, b), n in cruce.most_common() if a != b]

    lineas += ["", "## Desacuerdos en relevancia", "",
               "| Nota | Fuente | Referencia | Qwen | Comentario de Haiku |", "|---|---|---|---|---|"]
    for i in ref:
        r, p = ref[i], pred.get(i, {})
        if bool(r["relevante"]) != bool(p.get("relevante")):
            com = str(r.get("comentario") or "").replace("|", "/")[:120]
            lineas.append(f"| {notas[i]['titulo'][:80]} | {notas[i]['fuente']} | {r['motivo']} | {p.get('motivo')} | {com} |")
    return "\n".join(lineas) + "\n", m


def main(salida):
    ref = {e["id"]: e for e in json.loads(REFERENCIA.read_text(encoding="utf-8"))["etiquetas"]}
    notas = {n["id"]: n for ruta in NOTAS for n in json.loads(ruta.read_text(encoding="utf-8"))["notas"]}
    pred = cargar_pred(Path(salida) / "movilidad_clasificado.parquet")
    texto, m = informe(ref, pred, notas)
    ruta = Path(salida) / "gate-informe.md"
    ruta.write_text(texto, encoding="utf-8")
    print(f"Recall {num(m['recall'])}, precisión {num(m['precision'])}, kappa {num(m['kappa'])}. Informe en {ruta}")


def selfcheck():
    ref = {"a": {"relevante": True, "tipo": "solucion", "categorias_solucion": ["X"], "motivo": "problema_o_solucion_concreta"},
           "b": {"relevante": False, "motivo": "otro_tema"},
           "c": {"relevante": True, "tipo": "ambas", "categorias_problema": ["P"], "motivo": "problema_o_solucion_concreta"}}
    m = metricas(ref, ref)
    assert m["recall"] == m["precision"] == m["kappa"] == 1.0 and m["tipo"] == 2 and m["jaccard"] == 1.0
    pred = {"a": {"relevante": True, "tipo": "ambas", "categorias_solucion": ["X", "Y"]},
            "b": {"relevante": True}, "c": {"relevante": False}}
    m = metricas(ref, pred)
    assert m["recall"] == 0.5 and m["precision"] == 0.5 and m["tipo"] == 0 and m["jaccard"] == 0.5
    assert lista(None) == [] and lista(float("nan")) == [] and lista(("A",)) == ["A"]

    # Con la referencia real: una predicción perfecta da 1 en todo.
    referencia = {e["id"]: e for e in json.loads(REFERENCIA.read_text(encoding="utf-8"))["etiquetas"]}
    notas = {n["id"]: n for ruta in NOTAS for n in json.loads(ruta.read_text(encoding="utf-8"))["notas"]}
    texto, m = informe(referencia, {i: dict(e) for i, e in referencia.items()}, notas)
    assert m["n"] == 300 and m["recall"] == m["precision"] == 1.0 and "Desacuerdos" in texto
    print("selfcheck ok")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--salida", default=str(SALIDA), help="carpeta con movilidad_clasificado.parquet del gate")
    args = ap.parse_args()
    selfcheck() if args.selfcheck else main(args.salida)
