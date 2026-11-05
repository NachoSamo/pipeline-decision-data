"""Descarga notas de Clarín y La Nación leyendo el JSON-LD de cada página.

Clarín se lista desde sus páginas de tags. La Nación excluye /buscador y
/pf/api/ en robots.txt, así que se lista desde su sitemap histórico y solo se
guardan las URLs que contienen una raíz del diccionario. Se puede retomar.

Uso:
    python scripts/scrape_ldjson.py --selfcheck
    python scripts/scrape_ldjson.py clarin
    python scripts/scrape_ldjson.py clarin --solo-prioritarias
    python scripts/scrape_ldjson.py lanacion --limite 3
"""

import argparse
import json
import re
import time

import requests

from keywords import RAICES_RESIDUOS, TAGS_CLARIN_AMPLIOS, TAGS_CLARIN_RESIDUOS
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, limpiar, resumir
from scrape_infobae import PAUSA_LISTADO, PAUSA_NOTA, pedir

CLARIN = "https://www.clarin.com"
LANACION = "https://www.lanacion.com.ar"
NOMBRES = {"clarin": "Clarín", "lanacion": "La Nación"}


def rutas(fuente):
    return (
        DATA / f"{fuente}_residuos.listado.jsonl",
        DATA / f"{fuente}_residuos.jsonl",
        DATA / f"{fuente}_residuos.parquet",
    )


def raices_en(url):
    texto = url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ").lower()
    return [r for r in RAICES_RESIDUOS if r in texto]


def listar_clarin(sesion, archivo):
    for tag in TAGS_CLARIN_RESIDUOS + TAGS_CLARIN_AMPLIOS:
        vistas, pagina = set(), 1
        while True:
            sufijo = f"{tag}.html" if pagina == 1 else f"{tag}/page/{pagina}"
            respuesta = pedir(sesion, f"{CLARIN}/tema/{sufijo}")
            hallazgos = re.findall(r'href="(/[a-z0-9-]+/[^"]+_0_[^"]+\.html)"', respuesta.text) if respuesta else []
            nuevas = set(hallazgos) - vistas
            if not nuevas:
                break
            for url in sorted(nuevas):
                archivo.write(json.dumps({"url": CLARIN + url, "termino": tag}, ensure_ascii=False) + "\n")
            vistas |= nuevas
            print(f"{tag}: página {pagina}, {len(vistas)} notas", flush=True)
            pagina += 1
            time.sleep(PAUSA_LISTADO)


def listar_lanacion(sesion, archivo):
    indice = pedir(sesion, f"{LANACION}/sitemap-index-historico.xml").text
    sitemaps = re.findall(r"<loc>([^<]+)</loc>", indice)
    for numero, sitemap in enumerate(sitemaps, 1):
        respuesta = pedir(sesion, sitemap)
        for url in re.findall(r"<loc>([^<]+)</loc>", respuesta.text if respuesta else ""):
            for raiz in raices_en(url):
                archivo.write(json.dumps({"url": url, "termino": raiz}, ensure_ascii=False) + "\n")
        if numero % 25 == 0:
            print(f"sitemap {numero} de {len(sitemaps)}", flush=True)
        time.sleep(PAUSA_NOTA)


def listar(fuente, sesion):
    listado = rutas(fuente)[0]
    if listado.exists():
        return
    temporal = listado.with_suffix(".tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        (listar_clarin if fuente == "clarin" else listar_lanacion)(sesion, archivo)
    temporal.replace(listado)


def articulo_ld(pagina):
    bloques = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', pagina, re.S)
    for bloque in bloques:
        try:
            datos = json.loads(bloque)
        except ValueError:
            continue
        candidatos = datos if isinstance(datos, list) else datos.get("@graph", [datos])
        for candidato in candidatos:
            if isinstance(candidato, dict) and "Article" in str(candidato.get("@type")):
                return candidato
    return None


def como_lista(valor):
    if isinstance(valor, str):
        return [v.strip() for v in valor.split(",") if v.strip()]
    return valor or []


def a_fila(fuente, url, termino, ld):
    ld = ld or {}
    secciones = como_lista(ld.get("articleSection"))
    return {
        "id": url,
        "fuente": NOMBRES.get(fuente, fuente),
        "url": url,
        "titulo": limpiar(ld.get("headline")),
        "bajada": limpiar(ld.get("description")),
        "fecha": ld.get("datePublished"),
        "seccion": secciones[0] if secciones else None,
        "tags": como_lista(ld.get("keywords")),
        "tipo": (como_lista(ld.get("@type")) or [None])[0],
        "acceso_libre": ld.get("isAccessibleForFree"),
        "body": limpiar(ld.get("articleBody")),
        "termino": termino,
    }


def pendientes(fuente):
    listado, crudo, _ = rutas(fuente)
    notas = {}
    with listado.open(encoding="utf-8") as archivo:
        for linea in archivo:
            fila = json.loads(linea)
            notas.setdefault(fila["url"], set()).add(fila["termino"])
    hechas = set()
    if crudo.exists():
        with crudo.open(encoding="utf-8") as archivo:
            hechas = {json.loads(linea)["url"] for linea in archivo}
    faltan = [(url, ts) for url, ts in notas.items() if url not in hechas]
    amplios = set(TAGS_CLARIN_AMPLIOS)
    orden = lambda nota: (not (nota[1] - amplios), not raices_en(nota[0]))
    return sorted(faltan, key=orden), len(notas)


def es_prioritaria(terminos, url):
    return bool(terminos - set(TAGS_CLARIN_AMPLIOS)) or bool(raices_en(url))


def descargar(fuente, sesion, limite, solo_prioritarias=False):
    _, crudo, _ = rutas(fuente)
    faltan, total = pendientes(fuente)
    if solo_prioritarias:
        total -= sum(not es_prioritaria(t, u) for u, t in faltan)
        faltan = [(u, t) for u, t in faltan if es_prioritaria(t, u)]
    print(f"Notas únicas: {total}. Faltan: {len(faltan)}", flush=True)
    avance = Avance(NOMBRES[fuente], total=total, inicio=total - len(faltan))
    for url, terminos in faltan[:limite] if limite else faltan:
        respuesta = pedir(sesion, url)
        ld = articulo_ld(respuesta.text) if respuesta else None
        with crudo.open("a", encoding="utf-8") as archivo:
            for termino in sorted(terminos):
                fila = a_fila(fuente, url, termino, ld)
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        avance.paso(utiles=int(relevante(fila)))
        time.sleep(PAUSA_NOTA)


def selfcheck():
    pagina = '<script type="application/ld+json">{"@type":"NewsArticle","headline":"A &amp; B","articleBody":"<p>Uno</p>","keywords":"basura, ciudad","articleSection":["Ciudades"],"datePublished":"2026-01-01"}</script>'
    fila = a_fila("clarin", "https://x/y", "basura", articulo_ld(pagina))
    assert fila["titulo"] == "A & B" and fila["body"] == "Uno"
    assert fila["tags"] == ["basura", "ciudad"] and fila["seccion"] == "Ciudades"
    assert articulo_ld("<html></html>") is None
    assert a_fila("lanacion", "https://x/y", "basur", None)["body"] == ""
    assert raices_en("https://x/sociedad/el-basural-de-la-ciudad-nid1/") == ["basur"]
    assert raices_en("https://x/politica/la-economia-crece-nid1/") == []
    assert es_prioritaria({"basura"}, "https://x/politica/ley-nid1/")
    assert es_prioritaria({"ambiente"}, "https://x/politica/el-basural-nid1/")
    assert not es_prioritaria({"ambiente"}, "https://x/politica/ley-nid1/")
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuente", nargs="?", choices=sorted(NOMBRES))
    parser.add_argument("--limite", type=int)
    parser.add_argument("--solo-prioritarias", action="store_true", help="Saltea notas de tags amplios sin una raíz del diccionario en la URL.")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        sesion = requests.Session()
        sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
        listar(args.fuente, sesion)
        descargar(args.fuente, sesion, args.limite, args.solo_prioritarias)
        _, crudo, salida = rutas(args.fuente)
        resumir(consolidar(crudo, salida))
