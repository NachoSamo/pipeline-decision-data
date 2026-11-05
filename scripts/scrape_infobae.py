"""Descarga notas de Infobae a partir de sus páginas de tags.

Infobae excluye /buscador en robots.txt, así que no se usa ese buscador.
El listado por tag no trae el cuerpo: cada nota se pide por separado.
Primero van los tags de residuos y las notas de tags amplios que mencionan
el diccionario en título o bajada. Se puede cortar y retomar.

Uso:
    python scripts/scrape_infobae.py --selfcheck
    python scripts/scrape_infobae.py --limite 3
    python scripts/scrape_infobae.py --solo-prioritarias
    python scripts/scrape_infobae.py
"""

import argparse
import json
import re
import sys
import time

import requests

from keywords import BUSQUEDAS_RESIDUOS, TAGS_INFOBAE_AMPLIOS, TAGS_INFOBAE_RESIDUOS
from progreso import Avance, relevante
from scrape_eldoce import DATA, a_fila, consolidar, normalizar, resumir

SITE = "https://www.infobae.com"
API = SITE + "/pf/api/v3/content/fetch/content-feed"
TAM_LISTADO = 100
# ponytail: un solo hilo y una pausa fija; no paralelizar contra un medio.
PAUSA_LISTADO = 4
PAUSA_NOTA = 2

LISTADO = DATA / "infobae_residuos.listado.jsonl"
CRUDO = DATA / "infobae_residuos.jsonl"
SALIDA = DATA / "infobae_residuos.parquet"


def pedir(sesion, url, **kwargs):
    for intento in range(3):
        try:
            respuesta = sesion.get(url, timeout=60, **kwargs)
            if respuesta.status_code in (403, 429):
                sys.exit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
            if respuesta.status_code in (404, 410):
                return None
            respuesta.raise_for_status()
            return respuesta
        except requests.RequestException as error:
            print(f"  error en {url}: {error}", flush=True)
            time.sleep(PAUSA_LISTADO * 5 * (intento + 1))
    sys.exit(f"Fallaron 3 intentos en {url}; el avance quedó guardado.")


def listar(sesion):
    if LISTADO.exists():
        return
    temporal = LISTADO.with_suffix(".tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        for tag in TAGS_INFOBAE_RESIDUOS + TAGS_INFOBAE_AMPLIOS:
            offset = 0
            while offset is not None:
                consulta = {
                    "feedLimit": str(TAM_LISTADO),
                    "feedOffset": str(offset),
                    "feedOrder": "display_date:desc",
                    "feedQuery": "",
                    "feedSections": "",
                    "feedSectionsToExclude": "/arc-support",
                    "feedSlugAuthor": "",
                    "feedSlugAuthorToExclude": "",
                    "feedTags": tag,
                    "feedTagsToExclude": "arc-support, efe",
                }
                parametros = {"query": json.dumps(consulta, separators=(",", ":")), "_website": "infobae"}
                datos = pedir(sesion, API, params=parametros).json()
                for nota in datos.get("content_elements") or []:
                    fila = {
                        "id": nota.get("_id"),
                        "url": nota.get("website_url"),
                        "titulo": (nota.get("headlines") or {}).get("basic"),
                        "bajada": (nota.get("subheadlines") or {}).get("basic"),
                        "tag": tag,
                    }
                    archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
                print(f"{tag}: offset {offset} de {datos.get('count')}", flush=True)
                offset = datos.get("next")
                time.sleep(PAUSA_LISTADO)
    temporal.replace(LISTADO)


def contenido_global(pagina):
    coincidencia = re.search(r"Fusion\.globalContent=(\{.*?\});Fusion\.", pagina, re.S)
    return json.loads(coincidencia.group(1)) if coincidencia else None


def edicion(url):
    return url.strip("/").split("/")[0]


def prioridad(nota, diccionario):
    if nota["tags"] & set(TAGS_INFOBAE_RESIDUOS):
        return 0
    texto = normalizar(f"{nota['titulo']} {nota['bajada']}")
    return 1 if any(t in texto for t in diccionario) else 2


def pendientes():
    notas = {}
    with LISTADO.open(encoding="utf-8") as archivo:
        for linea in archivo:
            fila = json.loads(linea)
            if fila["url"]:
                nota = notas.setdefault(fila["url"], {**fila, "tags": set()})
                nota["tags"].add(fila["tag"])
    hechas = set()
    if CRUDO.exists():
        with CRUDO.open(encoding="utf-8") as archivo:
            hechas = {json.loads(linea)["ruta"] for linea in archivo}
    diccionario = [normalizar(t) for t in BUSQUEDAS_RESIDUOS]
    faltan = [n for url, n in notas.items() if url not in hechas]
    return sorted(faltan, key=lambda n: prioridad(n, diccionario)), len(notas)


def descargar_notas(sesion, limite, solo_prioritarias=False):
    faltan, total = pendientes()
    if solo_prioritarias:
        diccionario = [normalizar(t) for t in BUSQUEDAS_RESIDUOS]
        total -= sum(prioridad(n, diccionario) == 2 for n in faltan)
        faltan = [n for n in faltan if prioridad(n, diccionario) < 2]
    print(f"Notas únicas: {total}. Faltan: {len(faltan)}", flush=True)
    lote = faltan[:limite] if limite else faltan
    avance = Avance("Infobae", total=total, inicio=total - len(faltan))
    for nota in lote:
        respuesta = pedir(sesion, SITE + nota["url"])
        contenido = contenido_global(respuesta.text) if respuesta else None
        with CRUDO.open("a", encoding="utf-8") as archivo:
            base = contenido or {"_id": nota["id"], "website_url": nota["url"]}
            for tag in sorted(nota["tags"]):
                fila = a_fila(base, tag)
                fila.update(
                    fuente="Infobae",
                    tipo=base.get("type"),
                    id=fila["id"] or nota["id"],
                    url=SITE + nota["url"],
                    ruta=nota["url"],
                    edicion=edicion(nota["url"]),
                    titulo=fila["titulo"] or nota["titulo"],
                    bajada=fila["bajada"] or nota["bajada"],
                )
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))
        time.sleep(PAUSA_NOTA)


def selfcheck():
    pagina = 'x;Fusion.globalContent={"_id":"A","content_elements":[{"type":"text","content":"Hola"}]};Fusion.y=1'
    assert contenido_global(pagina)["_id"] == "A"
    assert contenido_global("sin datos") is None
    assert edicion("/mexico/2026/11/04/nota/") == "mexico"
    dic = [normalizar(t) for t in BUSQUEDAS_RESIDUOS]
    assert prioridad({"tags": {"basura"}, "titulo": "", "bajada": ""}, dic) == 0
    assert prioridad({"tags": {"ambiente"}, "titulo": "Un basural", "bajada": ""}, dic) == 1
    assert prioridad({"tags": {"ambiente"}, "titulo": "Bosques", "bajada": None}, dic) == 2
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--solo-prioritarias", action="store_true", help="Saltea notas de tags amplios sin el diccionario en título o bajada.")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        listar(sesion)
        descargar_notas(sesion, args.limite, args.solo_prioritarias)
        resumir(consolidar(CRUDO, SALIDA))
