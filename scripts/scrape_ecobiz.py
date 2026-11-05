"""Descarga notas de ECOBIZ desde su buscador.

La URL del buscador lleva el término en base64 y pagina con /pg-N. El listado no
trae el cuerpo, así que cada nota se pide por separado. Se puede cortar y retomar.

Uso:
    python scripts/scrape_ecobiz.py --selfcheck
    python scripts/scrape_ecobiz.py
    python scripts/scrape_ecobiz.py --terminos residuos
    python scripts/scrape_ecobiz.py --limite 3
"""

import argparse
import base64
import json
import re
import time

import requests

from html_texto import texto_de_bloque
from keywords import BUSQUEDAS_RESIDUOS
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, limpiar, resumir

SITE = "https://ecobiz.com.ar"
PAUSA = 4

LISTADO = DATA / "ecobiz_residuos.listado.jsonl"
PROGRESO = DATA / "ecobiz_residuos.progreso.json"
CRUDO = DATA / "ecobiz_residuos.jsonl"
SALIDA = DATA / "ecobiz_residuos.parquet"


def pedir(sesion, url):
    time.sleep(PAUSA)
    respuesta = sesion.get(url, timeout=60)
    if respuesta.status_code in (403, 429):
        raise SystemExit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
    if respuesta.status_code in (404, 410):
        return None
    respuesta.raise_for_status()
    return respuesta.text


def url_busqueda(termino, pagina):
    codigo = base64.b64encode(termino.encode("utf-8")).decode("ascii")
    sufijo = f"/pg-{pagina}" if pagina > 1 else ""
    return f"{SITE}/resultados-busqueda/{codigo}{sufijo}"


def notas_en(pagina):
    return list(dict.fromkeys(re.findall(r'href="(/nota/\d+-[^"]+)"', pagina)))


def ultima_pagina(pagina):
    paginas = re.findall(r"/pg-(\d+)\"", pagina)
    return max(map(int, paginas), default=1)


def listar(sesion, terminos):
    DATA.mkdir(exist_ok=True)
    progreso = json.loads(PROGRESO.read_text(encoding="utf-8")) if PROGRESO.exists() else {}
    for termino in terminos:
        pagina = progreso.get(termino, 1)
        while pagina is not None:
            html = pedir(sesion, url_busqueda(termino, pagina)) or ""
            notas = notas_en(html)
            with LISTADO.open("a", encoding="utf-8") as archivo:
                for ruta in notas:
                    archivo.write(json.dumps({"url": SITE + ruta, "termino": termino}, ensure_ascii=False) + "\n")
            print(f"{termino}: página {pagina} de {ultima_pagina(html)}, {len(notas)} notas", flush=True)
            pagina = pagina + 1 if notas and pagina < ultima_pagina(html) else None
            progreso[termino] = pagina
            PROGRESO.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")


def fila_de(url, termino, html):
    titulo = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    fecha = re.search(r"<small[^>]*>\s*(\d{2})\.(\d{2})\.(\d{4})\s*</small>", html)
    seccion = re.search(r'<header class="post-header.*?<a [^>]*>(.*?)</a>', html, re.S)
    return {
        "id": url,
        "fuente": "ECOBIZ",
        "url": url,
        "titulo": limpiar(titulo.group(1)) if titulo else "",
        "bajada": texto_de_bloque(html, "post-copete"),
        "fecha": f"{fecha.group(3)}-{fecha.group(2)}-{fecha.group(1)}" if fecha else None,
        "seccion": limpiar(seccion.group(1)) if seccion else None,
        "tags": [],
        "tipo": "nota",
        "body": texto_de_bloque(html, "post-desarrollo"),
        "termino": termino,
    }


def descargar(sesion, limite):
    notas = {}
    for linea in LISTADO.read_text(encoding="utf-8").splitlines():
        fila = json.loads(linea)
        notas.setdefault(fila["url"], set()).add(fila["termino"])
    hechas = set()
    if CRUDO.exists():
        hechas = {json.loads(l)["url"] for l in CRUDO.read_text(encoding="utf-8").splitlines()}
    faltan = [(u, t) for u, t in notas.items() if u not in hechas]
    print(f"Notas únicas: {len(notas)}. Faltan: {len(faltan)}", flush=True)
    avance = Avance("ECOBIZ", total=len(notas), inicio=len(notas) - len(faltan))
    for url, terminos in faltan[:limite] if limite else faltan:
        html = pedir(sesion, url) or ""
        with CRUDO.open("a", encoding="utf-8") as archivo:
            for termino in sorted(terminos):
                fila = fila_de(url, termino, html)
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))


def selfcheck():
    assert url_busqueda("residuos", 1).endswith("/resultados-busqueda/cmVzaWR1b3M=")
    assert url_busqueda("residuos", 2).endswith("/cmVzaWR1b3M=/pg-2")
    html = (
        '<header class="post-header"><a href="/131-Negocios">Negocios</a><small class="x">26.10.2026</small></header>'
        '<h1 class="y">Título &amp; más</h1><div class="post-copete z"><p>Bajada</p></div>'
        '<div class="post-desarrollo"><p>Cuerpo</p></div><a href="/nota/12-Una-nota">a</a>'
        '<a href="/resultados-busqueda/x/pg-11"></a>'
    )
    fila = fila_de("https://x/n", "residuos", html)
    assert fila["titulo"] == "Título & más" and fila["bajada"] == "Bajada"
    assert fila["fecha"] == "2026-10-26" and fila["seccion"] == "Negocios"
    assert fila["body"] == "Cuerpo"
    assert notas_en(html) == ["/nota/12-Una-nota"] and ultima_pagina(html) == 11
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS_RESIDUOS)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        listar(sesion, args.terminos)
        descargar(sesion, args.limite)
        if CRUDO.exists():
            resumir(consolidar(CRUDO, SALIDA))
