"""Descarga notas de CBA24N, el sitio de Canal 10, desde sus sitemaps mensuales.

Su robots.txt excluye /search y /api, así que no usa el buscador. Lista los
sitemaps y filtra las URLs por raíces del diccionario. Se puede cortar y retomar.

Uso:
    python scripts/scrape_cba24n.py --selfcheck
    python scripts/scrape_cba24n.py
    python scripts/scrape_cba24n.py --limite 3
"""

import argparse
import json
import re
import time

import requests

from dataset import DESDE_ANIO, NOMBRE
from html_texto import texto_de_bloque
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, resumir
from scrape_infobae import pedir
from scrape_ldjson import a_fila, articulo_ld, raices_en

SITE = "https://www.cba24n.com.ar"
# ponytail: el sitio respondió 429 con 4 s de pausa; subir si vuelve a pasar.
PAUSA = 12

LISTADO = DATA / f"cba24n_{NOMBRE}.listado.jsonl"
CRUDO = DATA / f"cba24n_{NOMBRE}.jsonl"
SALIDA = DATA / f"cba24n_{NOMBRE}.parquet"


def urls_de(xml):
    return re.findall(r"<loc>\s*([^<\s]+)", xml)


def seccion_de(url):
    return url.split("/")[3]


def desde_el_corte(sitemaps, anio=DESDE_ANIO):
    return [u for u in sitemaps if not anio or int(re.search(r"sitemap-(\d{4})", u).group(1)) >= anio]


def listar(sesion):
    if LISTADO.exists():
        return
    DATA.mkdir(exist_ok=True)
    sitemaps = desde_el_corte(urls_de(pedir(sesion, f"{SITE}/sitemap.xml").text))
    avance = Avance("CBA24N sitemaps", total=len(sitemaps), mide_tema=False)
    filas = []
    for sitemap in sitemaps:
        time.sleep(PAUSA)
        respuesta = pedir(sesion, sitemap)
        for url in urls_de(respuesta.text if respuesta else ""):
            filas += [{"url": url, "termino": raiz} for raiz in raices_en(url)]
        avance.paso()
    LISTADO.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


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
    avance = Avance("CBA24N", total=len(notas), inicio=len(notas) - len(faltan))
    for url, terminos in faltan[:limite] if limite else faltan:
        time.sleep(PAUSA)
        respuesta = pedir(sesion, url)
        html = respuesta.text if respuesta else ""
        with CRUDO.open("a", encoding="utf-8") as archivo:
            for termino in sorted(terminos):
                fila = a_fila("CBA24N", url, termino, articulo_ld(html))
                fila["seccion"] = seccion_de(url)
                fila["body"] = texto_de_bloque(html, "article-body-content")
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        url = "https://www.cba24n.com.ar/cordoba/recicladores-protestan_a6ae"
        assert urls_de(f"<loc>{url}</loc>") == [url]
        assert seccion_de(url) == "cordoba"
        assert desde_el_corte(["https://x/sitemap-2026-11.xml", "https://x/sitemap-1900-01.xml"], 2024) == ["https://x/sitemap-2026-11.xml"]
        assert raices_en(url) == ["recicl"]
        assert texto_de_bloque("<div class=article-body-content><p>Hola</p></div>", "article-body-content") == "Hola"
        print("selfcheck ok")
    else:
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        listar(sesion)
        descargar(sesion, args.limite)
        if CRUDO.exists():
            resumir(consolidar(CRUDO, SALIDA))
