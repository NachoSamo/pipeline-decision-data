"""Arma una muestra fija de notas para etiquetado manual.

Genera etiquetado/muestra.js con 25 notas por track (movilidad y residuos),
repartidas entre fuentes en round-robin. Es determinística: la semilla fija
hace que las dos personas que etiquetan vean exactamente las mismas notas.
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SEMILLA = 42
N = 25
MIN_BODY = 300
MAX_BODY = 15000
VERSION = "2026-11-25-s42"
TRACKS = ("movilidad", "residuos")


def texto(valor):
    """Convierte un valor a str, con nulos como cadena vacia."""
    return "" if pd.isna(valor) else str(valor)


def fecha_iso(valor):
    """Devuelve la fecha como YYYY-MM-DD, o cadena vacia si es nula."""
    return "" if pd.isna(valor) else valor.strftime("%Y-%m-%d")


def muestrear_track(track):
    """Devuelve la lista de N notas de un track."""
    df = pd.read_parquet(RAIZ / "data" / f"{track}.parquet")
    df = df[df["body"].notna() & (df["body"].str.strip().str.len() >= MIN_BODY)]

    # Round-robin entre fuentes: se mezcla, se numera dentro de cada fuente
    # y se toman las primeras N filas por numero de orden.
    df = df.sample(frac=1, random_state=SEMILLA)
    df["_orden"] = df.groupby("fuente").cumcount()
    df = df.sort_values("_orden", kind="stable").head(N)

    return [
        {
            "id": texto(fila["id"]),
            "fuente": texto(fila["fuente"]),
            "url": texto(fila["url"]),
            "fecha": fecha_iso(fila["fecha"]),
            "titulo": texto(fila["titulo"]),
            "bajada": texto(fila["bajada"]),
            "body": texto(fila["body"])[:MAX_BODY],
        }
        for _, fila in df.iterrows()
    ]


def main():
    """Arma la muestra, escribe muestra.js y devuelve el dict."""
    obj = {"version": VERSION}
    for track in TRACKS:
        obj[track] = muestrear_track(track)

    salida = RAIZ / "etiquetado" / "muestra.js"
    contenido = "window.MUESTRA = " + json.dumps(obj, ensure_ascii=False, indent=1) + ";\n"
    salida.write_text(contenido, encoding="utf-8")

    for track in TRACKS:
        notas = obj[track]
        conteo = pd.Series([n["fuente"] for n in notas]).value_counts()
        print(f"{track}: {len(notas)} notas")
        for fuente, cantidad in conteo.items():
            print(f"  {fuente}: {cantidad}")
    return obj


if __name__ == "__main__":
    muestra = main()
    for track in TRACKS:
        notas = muestra[track]
        assert len(notas) == N, f"{track}: {len(notas)} notas"
        ids = [n["id"] for n in notas]
        assert len(set(ids)) == len(ids), f"{track}: ids repetidos"
        assert all(n["body"].strip() for n in notas), f"{track}: body vacio"
        fuentes = {n["fuente"] for n in notas}
        assert len(fuentes) > 3, f"{track}: solo {len(fuentes)} fuentes"
    print("Asserts OK")
