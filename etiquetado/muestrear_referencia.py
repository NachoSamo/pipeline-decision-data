"""Arma la muestra de movilidad que etiqueta un LLM grande como referencia.

300 notas al azar de los Parquet filtrados: 240 de problemáticas y 60 de soluciones,
en proporción a sus tamaños, sin las 25 del gold del equipo. Se reparten en 3 partes
de 100 y a cada parte se le suman, mezcladas, las 25 del gold: sirven para medir
cuánto coincide cada etiquetador con el equipo. Además escribe la calibración, que
son solo las 25 del gold. Es determinística (semilla 42).

    python etiquetado/muestrear_referencia.py
"""

import json
import random
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
FILTRADOS = DATA / "v1-samo-movilidad"
SALIDA = RAIZ / "etiquetado" / "referencia"
GOLD = RAIZ / "etiquetado" / "reconciliacion" / "movilidad-gold.json"
SEMILLA = 42
N_PROBLEMATICAS, N_SOLUCIONES, PARTES = 240, 60, 3
MAX_BODY = 6000
CAMPOS = ["id", "dataset", "fuente", "alcance", "url", "fecha", "titulo", "bajada", "body"]


def texto(valor):
    return "" if pd.isna(valor) else str(valor)


def notas(df):
    """Lista de dicts con los campos que ve el etiquetador."""
    salida = []
    for fila in df.to_dict("records"):
        nota = {c: texto(fila.get(c)) for c in CAMPOS}
        nota["fecha"] = nota["fecha"][:10]
        nota["body"] = nota["body"][:MAX_BODY]
        salida.append(nota)
    return salida


def armar():
    """Devuelve (partes, calibracion) sin escribir nada."""
    import sys

    sys.path.insert(0, str(RAIZ / "scripts"))
    from diccionarios.alcance_fuentes import alcance

    ids_gold = [e["id"] for e in json.loads(GOLD.read_text(encoding="utf-8"))["etiquetas"]]

    prob = pd.read_parquet(FILTRADOS / "movilidad_filtrado.parquet").assign(dataset="problematicas")
    sol = pd.read_parquet(FILTRADOS / "movilidad_soluciones_filtrado.parquet").assign(dataset="soluciones")
    prob = prob[~prob["id"].isin(ids_gold)]
    sol = sol[~sol["id"].isin(ids_gold) & ~sol["id"].isin(prob["id"])]  # sin notas repetidas entre datasets
    muestra = pd.concat([
        prob.sample(N_PROBLEMATICAS, random_state=SEMILLA),
        sol.sample(N_SOLUCIONES, random_state=SEMILLA),
    ]).sample(frac=1, random_state=SEMILLA)

    gold = pd.read_parquet(DATA / "movilidad.parquet")
    gold = gold[gold["id"].isin(ids_gold)].assign(dataset="gold")
    gold["alcance"] = gold["fuente"].map(alcance)
    calibracion = notas(gold)

    todas = notas(muestra)
    tam = len(todas) // PARTES
    partes = []
    for n in range(PARTES):
        parte = todas[n * tam:(n + 1) * tam] + calibracion
        random.Random(SEMILLA + n).shuffle(parte)
        partes.append(parte)
    return partes, calibracion


def escribir(nombre, lista):
    ruta = SALIDA / nombre
    ruta.write_text(json.dumps({"track": "movilidad", "notas": lista}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{ruta.relative_to(RAIZ)}: {len(lista)} notas")


def main():
    partes, calibracion = armar()
    ids_gold = {n["id"] for n in calibracion}
    assert len(calibracion) == 25
    for parte in partes:
        ids = [n["id"] for n in parte]
        assert len(ids) == 125 and len(set(ids)) == 125 and ids_gold <= set(ids)
    sin_gold = [n["id"] for p in partes for n in p if n["id"] not in ids_gold]
    assert len(sin_gold) == len(set(sin_gold)) == 300, "las partes comparten notas"

    SALIDA.mkdir(parents=True, exist_ok=True)
    for n, parte in enumerate(partes, 1):
        escribir(f"movilidad-parte{n}.json", parte)
    escribir("movilidad-calibracion.json", calibracion)


if __name__ == "__main__":
    main()
