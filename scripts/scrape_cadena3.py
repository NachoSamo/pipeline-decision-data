"""Descarga notas de Cadena 3 desde su sitemap de noticias y una lista propia.

Su robots.txt excluye el buscador, y sus páginas de tags dependen de una
verificación anti-bots. Por eso el script solo usa el sitemap de noticias, que
trae notas recientes, y las URLs que agregues a data/cadena3_urls.txt.

Uso:
    python scripts/scrape_cadena3.py --selfcheck
    python scripts/scrape_cadena3.py
    python scripts/scrape_cadena3.py --limite 3
"""

import argparse
import json
import re
import time

import requests

from html_texto import texto_de_bloque
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, resumir
from scrape_infobae import pedir
from scrape_ldjson import a_fila, articulo_ld, raices_en

SITEMAP = "https://www.cadena3.com/feed/sitemap-news.xml"
PAUSA = 4

URLS = DATA / "cadena3_urls.txt"
CRUDO = DATA / "cadena3_residuos.jsonl"
SALIDA = DATA / "cadena3_residuos.parquet"


def urls_de(xml):
    return list(dict.fromkeys(re.findall(r"<loc>\s*([^<\s]+)", xml)))


def es_nota(url):
    return "/noticia/" in url


def sin_embebidos(texto):
    return re.sub(r"/Inicio Código Embebido/.*?/Fin Código Embebido/", "", texto, flags=re.S).strip()


def pendientes(sesion):
    notas = {}
    respuesta = pedir(sesion, SITEMAP)
    for url in urls_de(respuesta.text if respuesta else ""):
        if es_nota(url) and raices_en(url):
            notas[url] = set(raices_en(url))
    if URLS.exists():
        for url in URLS.read_text(encoding="utf-8").split():
            if es_nota(url):
                notas.setdefault(url, set()).add("lista manual")
    hechas = set()
    if CRUDO.exists():
        hechas = {json.loads(l)["url"] for l in CRUDO.read_text(encoding="utf-8").splitlines()}
    return [(u, t) for u, t in notas.items() if u not in hechas], len(notas)


def descargar(sesion, limite):
    faltan, total = pendientes(sesion)
    print(f"Notas únicas: {total}. Faltan: {len(faltan)}", flush=True)
    avance = Avance("Cadena 3", total=total, inicio=total - len(faltan))
    for url, terminos in faltan[:limite] if limite else faltan:
        time.sleep(PAUSA)
        respuesta = pedir(sesion, url)
        if respuesta:
            respuesta.encoding = "utf-8"
        html = respuesta.text if respuesta else ""
        with CRUDO.open("a", encoding="utf-8") as archivo:
            for termino in sorted(terminos):
                fila = a_fila("Cadena 3", url, termino, articulo_ld(html))
                fila["body"] = sin_embebidos(texto_de_bloque(html, "cuerpo-nota"))
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        xml = "<loc>https://x/noticia/a/basural_1</loc><loc>https://x/noticia/a/basural_1</loc>"
        assert urls_de(xml) == ["https://x/noticia/a/basural_1"]
        assert es_nota(urls_de(xml)[0]) and not es_nota("https://x/seccion/a")
        assert raices_en("https://x/noticia/a/el-basural_1") == ["basur"]
        assert sin_embebidos("Uno\n/Inicio Código Embebido/\nOtra nota\n/Fin Código Embebido/") == "Uno"
        print("selfcheck ok")
    else:
        DATA.mkdir(exist_ok=True)
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        descargar(sesion, args.limite)
        if CRUDO.exists():
            resumir(consolidar(CRUDO, SALIDA))
