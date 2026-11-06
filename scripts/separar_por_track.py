"""Separa el dataset de soluciones en un Parquet por track y fuente.

Deja notas desde 2024 y asigna tracks por raíces en título o bajada. Una nota
puede ir en varios tracks. Las notas sin track se descartan.

Uso:
    python scripts/separar_por_track.py --selfcheck
    python scripts/separar_por_track.py
"""

import argparse
import os
import re

os.environ["DATASET"] = "soluciones"

import pandas as pd

from dataset import DATA, DESDE_ANIO
from diccionarios.keywords_soluciones import RAICES_TRACK
from progreso import normalizar

LIMITE_MB = 100
PATRONES = {t: re.compile(r"\b(?:" + "|".join(map(re.escape, r)) + ")") for t, r in RAICES_TRACK.items()}


def tracks_de(titulo, bajada):
    encabezado = normalizar(f"{titulo or ''} {bajada or ''}")
    return [t for t, patron in PATRONES.items() if patron.search(encabezado)]


def separar_fuente(notas):
    fechas = pd.to_datetime(notas["fecha"], utc=True, errors="coerce")
    notas = notas[fechas.dt.year >= DESDE_ANIO].copy()
    notas["tracks"] = [tracks_de(a, b) for a, b in zip(notas["titulo"], notas["bajada"])]
    return {t: notas[notas["tracks"].map(lambda ts: t in ts)] for t in PATRONES}


def separar(entrada=DATA, salida=DATA.parent):
    filas = []
    for archivo in sorted(entrada.glob("*_soluciones.parquet")):
        fuente = archivo.name.removesuffix("_soluciones.parquet")
        fila = {"fuente": fuente}
        for track, notas in separar_fuente(pd.read_parquet(archivo)).items():
            fila[track] = len(notas)
            if len(notas):
                carpeta = salida / track
                carpeta.mkdir(parents=True, exist_ok=True)
                destino = carpeta / f"{fuente}.parquet"
                notas.to_parquet(destino, index=False)
                if destino.stat().st_size > LIMITE_MB * 1024 * 1024:
                    print(f"AVISO: {destino} supera {LIMITE_MB} MB; hay que dividirlo por año.")
        filas.append(fila)
    if filas:
        tabla = pd.DataFrame(filas).set_index("fuente")
        print(tabla.to_string())
        print("\nPor track, con repetidas entre tracks:\n" + tabla.sum().to_string())
    else:
        print("No hay Parquet consolidados.")


def selfcheck():
    assert tracks_de("Un milagro", "") == []
    assert tracks_de("Startup de reciclaje", "para el agro") == ["residuos", "agro"]
    notas = pd.DataFrame({
        "fecha": ["2023-12-31T00:00:00Z", "2024-01-01T00:00:00Z", "2025-01-01T00:00:00Z"],
        "titulo": ["Basura vieja", "Basura y cultivos", "Celular nuevo"],
        "bajada": ["", "", ""],
    })
    partes = separar_fuente(notas)
    assert len(partes["residuos"]) == 1 and len(partes["agro"]) == 1 and len(partes["movilidad"]) == 0
    assert list(partes["agro"]["tracks"].iloc[0]) == ["residuos", "agro"]
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        separar()
