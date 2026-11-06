"""Corre las descargas del dataset de soluciones, una o todas en paralelo.

Con `todas`, cada fuente corre en su propio proceso y deja su log en
data/soluciones/crudo/logs/. Relanza una fuente solo si falló la red. Nunca
insiste si el sitio respondió 403 o 429.

Uso:
    python scripts/soluciones.py --selfcheck
    python scripts/soluciones.py tn
    python scripts/soluciones.py tn eldoce
    python scripts/soluciones.py todas
"""

import argparse
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ["DATASET"] = "soluciones"

from dataset import DATA
from scrape_especializadas import FUENTES as ESPECIALIZADAS
from scrape_internacional import FUENTES as INTERNACIONALES

SCRIPTS = Path(__file__).resolve().parent
INTENTOS = 6
ESPERA = 300

COMANDOS = {
    "eldoce": ["scrape_eldoce.py"],
    "tn": ["scrape_tn.py"],
    "infobae": ["scrape_infobae.py", "--solo-prioritarias"],
    "clarin": ["scrape_ldjson.py", "clarin", "--solo-prioritarias"],
    "lanacion": ["scrape_ldjson.py", "lanacion"],
    "cba24n": ["scrape_cba24n.py"],
    "ecobiz": ["scrape_ecobiz.py"],
    "visionsustentable": ["scrape_visionsustentable.py"],
    "ecomundo": ["scrape_ecomundo.py"],
    "mongabay": ["scrape_mongabay.py"],
    **{clave: ["scrape_internacional.py", clave] for clave in INTERNACIONALES},
    **{clave: ["scrape_especializadas.py", clave] for clave in ESPECIALIZADAS},
}


def decidir(salida, codigo):
    if codigo == 0 and "quedó incompleta" not in salida:
        return "terminó"
    if re.search(r"respondió (403|429)", salida):
        return "frenada por el sitio"
    if re.search(r"Fallaron \d+ intentos|ConnectionError|ConnectTimeout|ReadTimeout", salida):
        return "reintentar"
    return "falló"


def correr(clave, log=None, intentos=INTENTOS, espera=ESPERA):
    escribir = log.write if log else sys.stdout.write
    entorno = {**os.environ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    for intento in range(1, intentos + 1):
        proceso = subprocess.Popen(
            [sys.executable, str(SCRIPTS / COMANDOS[clave][0]), *COMANDOS[clave][1:]],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=entorno,
        )
        lineas = []
        for linea in proceso.stdout:
            lineas.append(linea)
            escribir(linea)
            (log or sys.stdout).flush()
        estado = decidir("".join(lineas), proceso.wait())
        if estado != "reintentar":
            return estado
        escribir(f"\nFalló la red. Intento {intento} de {intentos}; reintento en {espera // 60} min.\n")
        (log or sys.stdout).flush()
        time.sleep(espera)
    return "sin red"


def correr_con_log(clave):
    carpeta = DATA / "logs"
    carpeta.mkdir(exist_ok=True)
    print(f"Empieza {clave}", flush=True)
    with (carpeta / f"{clave}.log").open("a", encoding="utf-8") as log:
        estado = correr(clave, log)
    print(f"{clave}: {estado}", flush=True)
    return clave, estado


def selfcheck():
    assert decidir("listo", 0) == "terminó"
    assert decidir("error en x: ConnectionError\nlisto", 0) == "terminó"
    assert decidir("El sitio respondió 429: corto", 1) == "frenada por el sitio"
    assert decidir("X: quedó incompleta. El sitio respondió 403", 0) == "frenada por el sitio"
    assert decidir("Fallaron 3 intentos en x", 1) == "reintentar"
    assert decidir("X: quedó incompleta. Fallaron 3 intentos", 0) == "reintentar"
    assert decidir("requests.exceptions.ConnectionError", 1) == "reintentar"
    assert decidir("ValueError", 1) == "falló"
    assert "infobae" in COMANDOS and "residuosprofesional" in COMANDOS and "grist" in COMANDOS
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuentes", nargs="*", help="todas, o alguna de: " + ", ".join(COMANDOS))
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    claves = list(COMANDOS) if args.fuentes == ["todas"] else args.fuentes
    desconocidas = set(claves) - set(COMANDOS)
    if desconocidas:
        parser.error(f"fuentes desconocidas: {', '.join(sorted(desconocidas))}")
    if args.selfcheck:
        selfcheck()
    elif len(claves) == 1:
        print(f"{claves[0]}: {correr(claves[0])}")
    elif claves:
        with ThreadPoolExecutor(len(claves)) as grupo:
            resultados = list(grupo.map(correr_con_log, claves))
        print("\nResumen:")
        for clave, estado in resultados:
            print(f"  {clave}: {estado}")
    else:
        parser.error("indicá una fuente o `todas`")
