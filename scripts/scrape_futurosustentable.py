"""Descarga notas de Futuro Sustentable desde sus sitemaps.

Su robots.txt excluye /?s= y cualquier URL con "?", y pide 60 segundos entre
pedidos. Por eso no usa el buscador ni la API: lista los sitemaps, filtra las
URLs por raíces del diccionario y lee cada nota. Se puede cortar y retomar.

Uso:
    python scripts/scrape_futurosustentable.py --selfcheck
    python scripts/scrape_futurosustentable.py
    python scripts/scrape_futurosustentable.py --limite 1
"""

import argparse
import json
import re
import time

import requests

from html_texto import texto_de_bloque
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, resumir
from scrape_ldjson import a_fila, articulo_ld, raices_en

SITE = "https://futurosustentable.com.ar"
PAUSA = 60

LISTADO = DATA / "futurosustentable_residuos.listado.jsonl"
CRUDO = DATA / "futurosustentable_residuos.jsonl"
SALIDA = DATA / "futurosustentable_residuos.parquet"


def pedir(sesion, url):
    time.sleep(PAUSA)
    respuesta = sesion.get(url, timeout=120)
    if respuesta.status_code in (403, 429):
        raise SystemExit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
    if respuesta.status_code in (404, 410):
        return None
    respuesta.raise_for_status()
    return respuesta.text


def urls_de(xml):
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    return [u for u in urls if not re.search(r"\.(jpe?g|png|webp|gif)$", u, re.I)]


def listar(sesion):
    if LISTADO.exists():
        return
    DATA.mkdir(exist_ok=True)
    indice = pedir(sesion, f"{SITE}/sitemap_index.xml")
    sitemaps = [u for u in urls_de(indice) if "/post-sitemap" in u]
    filas = []
    for sitemap in sitemaps:
        xml = pedir(sesion, sitemap)
        for url in urls_de(xml or ""):
            filas += [{"url": url, "termino": raiz} for raiz in raices_en(url)]
        print(f"{sitemap}: {len(filas)} filas", flush=True)
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
    print(f"Notas únicas: {len(notas)}. Faltan: {len(faltan)}. Tarda 1 minuto por nota.", flush=True)
    avance = Avance("Futuro Sustentable", total=len(notas), inicio=len(notas) - len(faltan), cada=0)
    for url, terminos in faltan[:limite] if limite else faltan:
        pagina = pedir(sesion, url) or ""
        with CRUDO.open("a", encoding="utf-8") as archivo:
            for termino in sorted(terminos):
                fila = a_fila("Futuro Sustentable", url, termino, articulo_ld(pagina))
                fila["body"] = texto_de_bloque(pagina, "entry-content")
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        xml = "<loc>https://x/a-residuos/</loc><loc>https://x/f.jpg</loc>"
        assert urls_de(xml) == ["https://x/a-residuos/"]
        assert raices_en(urls_de(xml)[0]) == ["residu"]
        print("selfcheck ok")
    else:
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        listar(sesion)
        descargar(sesion, args.limite)
        if CRUDO.exists():
            resumir(consolidar(CRUDO, SALIDA))
