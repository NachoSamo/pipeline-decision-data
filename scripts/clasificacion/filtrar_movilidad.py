"""Filtra el ruido de data/movilidad.parquet con reglas determinísticas.

Las reglas solo se aplican a diarios. Las fuentes especializadas (Grist, CicloVivo,
Ecoticias, Visión Sustentable, Ecomundo) pasan siempre. No hay corte por longitud del cuerpo.
Las notas descartadas no se guardan en ningún archivo.

Uso, desde la raíz del repo:
    python scripts/clasificacion/filtrar_movilidad.py               filtra y escribe el Parquet
    python scripts/clasificacion/filtrar_movilidad.py --selfcheck   casos sintéticos y gold
    python scripts/clasificacion/filtrar_movilidad.py --muestra 20  auditoría, sin escribir el Parquet
"""

import argparse
import contextlib
import json
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

from diccionarios.keywords_movilidad import RAICES_MOVILIDAD  # noqa: E402
from progreso import Avance, normalizar  # noqa: E402

ENTRADA = RAIZ / "data" / "movilidad.parquet"
SALIDA = RAIZ / "data" / "movilidad_filtrado.parquet"
LOG = RAIZ / "data" / "logs" / "filtrar_movilidad.log"
GOLD = RAIZ / "etiquetado" / "reconciliacion" / "movilidad-gold.json"

DIARIOS = {"TN", "El Doce", "Clarín", "La Nación", "CBA24N"}
SECCIONES_FUERA = {
    "deportes", "futbol", "polideportivo", "boxeo", "toda pasion", "famosos", "show",
    "el show del lagarto", "celebridades", "cuarteteando", "hollywood", "television",
    "espectaculos", "policiales", "redes sociales", "viste", "increible", "contenido patrocinado",
}
SEGURIDAD_VIAL = re.compile(
    r"\b(?:choc\w*|choque\w*|accidente\w*|atropell\w*|vuelc\w*|volc\w*|siniestro\w*|tragedia|alcoholemia|picadas?)\b"
)
MOTIVOS = ["seccion_fuera_de_track", "seguridad_vial", "sin_raiz_movilidad"]


def _texto(valor):
    """Devuelve el valor como texto. Los nulos (None o NaN) pasan a cadena vacía."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    return str(valor)


def motivo(fila):
    """Devuelve el primer motivo de descarte de la nota, o None si pasa."""
    if fila.get("fuente") not in DIARIOS:
        return None
    seccion = normalizar(_texto(fila.get("seccion"))).strip()
    if seccion in SECCIONES_FUERA:
        return "seccion_fuera_de_track"
    titulo_bajada = f"{_texto(fila.get('titulo'))} {_texto(fila.get('bajada'))}"
    if SEGURIDAD_VIAL.search(normalizar(titulo_bajada)):
        return "seguridad_vial"
    tags = fila.get("tags")
    tags_txt = "" if tags is None or isinstance(tags, float) else " ".join(_texto(t) for t in tags)
    completo = normalizar(f"{titulo_bajada} {tags_txt}")
    if not any(raiz in completo for raiz in RAICES_MOVILIDAD):
        return "sin_raiz_movilidad"
    return None


def imprimir(texto=""):
    """Imprime cada línea con la hora al inicio."""
    for linea in str(texto).split("\n"):
        print(f"[{datetime.now():%H:%M:%S}] {linea}", flush=True)


def tee(consola, archivo):
    """Objeto con write y flush que escribe en la consola y en el log."""

    def write(texto):
        consola.write(texto)
        archivo.write(texto)
        return len(texto)

    def flush():
        consola.flush()
        archivo.flush()

    return SimpleNamespace(write=write, flush=flush)


def clasificar(filas, avance):
    motivos = []
    for fila in filas:
        motivos.append(motivo(fila))
        avance.paso(1)
    return motivos


def resumen(filas, motivos, comienzo, ruta=None):
    total = len(filas)
    cuenta = Counter(m for m in motivos if m)
    imprimir("-" * 60)
    imprimir("Descartes por motivo")
    imprimir(f"  {'motivo':<24}{'notas':>8}{'% total':>9}")
    for m in MOTIVOS:
        imprimir(f"  {m:<24}{cuenta[m]:>8}{cuenta[m] / total:>9.1%}")
    imprimir("Resumen por fuente")
    imprimir(f"  {'fuente':<20}{'iniciales':>10}{'descartadas':>13}{'quedan':>9}{'% queda':>9}")
    iniciales = Counter(f["fuente"] for f in filas)
    descartadas = Counter(f["fuente"] for f, m in zip(filas, motivos) if m)
    for fuente in sorted(iniciales, key=lambda f: -iniciales[f]):
        quedan = iniciales[fuente] - descartadas[fuente]
        imprimir(
            f"  {fuente:<20}{iniciales[fuente]:>10}{descartadas[fuente]:>13}"
            f"{quedan:>9}{quedan / iniciales[fuente]:>9.1%}"
        )
    quedan_total = total - sum(cuenta.values())
    imprimir(f"Total que queda: {quedan_total} de {total} ({quedan_total / total:.1%})")
    imprimir(f"Tiempo total: {(time.monotonic() - comienzo) / 60:.1f} min")
    if ruta:
        imprimir(f"Parquet de salida: {ruta}")
        imprimir(f"Tamaño: {ruta.stat().st_size / 1024 ** 2:.1f} MB")


def mostrar_muestra(filas, motivos, n):
    rng = random.Random(42)
    for m in MOTIVOS:
        candidatos = [i for i, x in enumerate(motivos) if x == m]
        imprimir(f"Muestra de {m} ({len(candidatos)} notas)")
        for i in rng.sample(candidatos, min(n, len(candidatos))):
            fila = filas[i]
            imprimir(f"  [{fila['fuente']}] ({_texto(fila.get('seccion'))}) {_texto(fila.get('titulo'))}")


def correr(muestra=None):
    comienzo = time.monotonic()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    consola = sys.stdout
    with open(LOG, "a", encoding="utf-8") as archivo:
        with contextlib.redirect_stdout(tee(consola, archivo)):
            imprimir("=" * 60)
            imprimir(f"Inicio: {datetime.now():%d/%m/%Y %H:%M:%S}")
            imprimir(f"Entrada: {ENTRADA}")
            df = pd.read_parquet(ENTRADA)
            filas = df.to_dict("records")
            imprimir(f"Total de notas: {len(filas)}")
            avance = Avance("Movilidad", total=len(filas), mide_tema=False)
            motivos = clasificar(filas, avance)
            if muestra is not None:
                resumen(filas, motivos, comienzo)
                mostrar_muestra(filas, motivos, muestra)
            else:
                mascara = [m is None for m in motivos]
                df[mascara].to_parquet(SALIDA, index=False, compression="zstd", compression_level=19)
                resumen(filas, motivos, comienzo, SALIDA)


def selfcheck():
    casos = [
        ({"fuente": "TN", "seccion": "Deportes", "titulo": "Lo que pasó"}, "seccion_fuera_de_track"),
        ({"fuente": "El Doce", "titulo": "Choque en Circunvalación", "bajada": ""}, "seguridad_vial"),
        ({"fuente": "Clarín", "titulo": "El dólar hoy", "tags": None}, "sin_raiz_movilidad"),
        ({"fuente": "TN", "titulo": "Nuevas líneas de colectivo"}, None),
        ({"fuente": "Grist", "seccion": "Deportes", "titulo": "Choque"}, None),
    ]
    for fila, esperado in casos:
        assert motivo(fila) == esperado, (fila, motivo(fila))

    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    ids = {e["id"] for e in gold["etiquetas"] if e["relevante"] is True}
    df = pd.read_parquet(ENTRADA)
    filas = df[df["id"].isin(ids)].to_dict("records")
    assert len(filas) == len(ids), "faltan ids del gold en movilidad.parquet"
    for fila in filas:
        assert motivo(fila) is None, (fila["id"], motivo(fila))
    imprimir("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filtro de ruido para movilidad.parquet.")
    parser.add_argument("--selfcheck", action="store_true", help="casos sintéticos y gold, sin escribir")
    parser.add_argument("--muestra", type=int, metavar="N", help="imprime N títulos por motivo, sin escribir")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        correr(args.muestra)
