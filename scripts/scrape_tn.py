"""Descarga notas de TN con la API de su buscador.

Es la misma API que usa la página de resultados y trae las notas completas.
Se puede cortar y retomar.

Uso:
    python scripts/scrape_tn.py --selfcheck
    python scripts/scrape_tn.py
    python scripts/scrape_tn.py --terminos "residuos sustentables"
"""

import argparse
import json
import time

import requests

from keywords import BUSQUEDAS_PRECISAS_RESIDUOS
from progreso import Avance, relevante
from scrape_eldoce import DATA, a_fila, consolidar, resumir

SITE = "https://tn.com.ar"
API = SITE + "/pf/api/v3/content/fetch/search-api"
TAM_PAGINA = 20
PAUSA = 4
# El buscador ordena por relevancia: tras tantas páginas sin aporte, sigue el próximo término.
PAGINAS_SIN_APORTE = 10

CRUDO = DATA / "tn_residuos.jsonl"
PROGRESO = DATA / "tn_residuos.progreso.json"
SALIDA = DATA / "tn_residuos.parquet"


def a_fila_tn(nota, termino):
    return {**a_fila(nota, termino), "fuente": "TN", "url": SITE + (nota.get("website_url") or nota.get("canonical_url") or "")}


def pedir(sesion, termino, pagina):
    consulta = {"applyFilter": True, "feed_size": TAM_PAGINA, "page": pagina, "query": termino, "size": TAM_PAGINA}
    parametros = {"query": json.dumps(consulta, separators=(",", ":")), "_website": "tn"}
    errores_del_servidor = 0
    for intento in range(3):
        try:
            respuesta = sesion.get(API, params=parametros, timeout=60)
            if respuesta.status_code in (403, 429):
                raise SystemExit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
            errores_del_servidor += respuesta.status_code >= 500
            respuesta.raise_for_status()
            return respuesta.json()
        except (requests.RequestException, ValueError) as error:
            print(f"  error en {termino} p{pagina}: {error}", flush=True)
            time.sleep(PAUSA * 5 * (intento + 1))
    if errores_del_servidor == 3:
        return None
    raise SystemExit(f"Fallaron 3 intentos en {termino} p{pagina}; el avance quedó guardado.")


def siguiente_pagina(pagina, filas, total, sin_aporte):
    if not filas or pagina * TAM_PAGINA >= total or sin_aporte >= PAGINAS_SIN_APORTE:
        return None
    return pagina + 1


def descargar(terminos):
    DATA.mkdir(exist_ok=True)
    progreso = json.loads(PROGRESO.read_text(encoding="utf-8")) if PROGRESO.exists() else {}
    sesion = requests.Session()
    sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
    for numero, termino in enumerate(terminos, 1):
        pagina = progreso.get(termino, 1)
        if pagina is None:
            print(f"TN [{numero}/{len(terminos)}] {termino}: ya estaba descargado", flush=True)
            continue
        avance = Avance(f"TN [{numero}/{len(terminos)}] {termino}", inicio=(pagina - 1) * TAM_PAGINA)
        sin_aporte = 0
        while pagina is not None:
            datos = pedir(sesion, termino, pagina)
            if datos is None:
                print(f"TN {termino}: el servidor falla en la página {pagina}; sigo con el próximo término.", flush=True)
                progreso[termino] = None
                PROGRESO.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
                break
            filas = [a_fila_tn(nota, termino) for nota in datos.get("content_elements") or []]
            with CRUDO.open("a", encoding="utf-8") as archivo:
                for fila in filas:
                    archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
            total = datos.get("count") or 0
            aportes = sum(map(relevante, filas))
            avance.paso(len(filas), aportes, total)
            sin_aporte = 0 if aportes else sin_aporte + 1
            siguiente = siguiente_pagina(pagina, filas, total, sin_aporte)
            if sin_aporte >= PAGINAS_SIN_APORTE and siguiente is None:
                print(f"TN {termino}: {sin_aporte} páginas sin aporte; sigo con el próximo término.", flush=True)
            pagina = siguiente
            progreso[termino] = pagina
            PROGRESO.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
            time.sleep(PAUSA)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS_PRECISAS_RESIDUOS)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        fila = a_fila_tn({"_id": "A", "website_url": "/campo/nota/", "headlines": {"basic": "Basura"}}, "basura")
        assert fila["fuente"] == "TN" and fila["url"] == "https://tn.com.ar/campo/nota/"
        assert relevante(fila)
        assert siguiente_pagina(1, [fila], 100, 0) == 2
        assert siguiente_pagina(5, [fila], 100, 0) is None
        assert siguiente_pagina(1, [], 100, 0) is None
        assert siguiente_pagina(1, [fila], 100, PAGINAS_SIN_APORTE) is None
        print("selfcheck ok")
    else:
        descargar(args.terminos)
        if CRUDO.exists():
            resumir(consolidar(CRUDO, SALIDA))
