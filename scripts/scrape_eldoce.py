"""Descarga notas de El Doce por palabra clave y arma un Parquet.

Uso:
    python scripts/scrape_eldoce.py --selfcheck
    python scripts/scrape_eldoce.py
    python scripts/scrape_eldoce.py --terminos RAEE biodigestor

Si se corta, volver a ejecutarlo retoma desde la última página guardada.
"""

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

from keywords import BUSQUEDAS_RESIDUOS, CORE_KEYWORDS_RESIDUOS
from progreso import Avance, normalizar, relevante

API = "https://eldoce.tv/pf/api/v3/content/fetch/search-api"
SITE = "https://eldoce.tv"
TAM_PAGINA = 20
# ponytail: un solo hilo y 4 s entre pedidos por sus términos de uso; no paralelizar.
PAUSA = 4

DATA = Path(__file__).resolve().parent.parent / "data"
CRUDO = DATA / "eldoce_residuos.jsonl"
PROGRESO = DATA / "eldoce_residuos.progreso.json"
SALIDA = DATA / "eldoce_residuos.parquet"


def limpiar(texto):
    return html.unescape(re.sub(r"<[^>]+>", "", texto or "")).strip()


def cuerpo(elementos):
    partes = []
    for e in elementos or []:
        if e.get("type") in ("text", "header"):
            partes.append(limpiar(e.get("content")))
        elif e.get("type") == "list":
            partes += [limpiar(i.get("content")) for i in e.get("items", [])]
    return "\n".join(p for p in partes if p)


def a_fila(nota, termino):
    taxonomia = nota.get("taxonomy") or {}
    return {
        "id": nota.get("_id"),
        "fuente": "El Doce",
        "url": SITE + (nota.get("website_url") or nota.get("canonical_url") or ""),
        "titulo": limpiar((nota.get("headlines") or {}).get("basic")),
        "bajada": limpiar((nota.get("subheadlines") or {}).get("basic")),
        "fecha": nota.get("display_date"),
        "seccion": (taxonomia.get("primary_section") or {}).get("name"),
        "tags": [t.get("text") for t in taxonomia.get("tags") or []],
        "tipo": nota.get("subtype") or nota.get("type"),
        "body": cuerpo(nota.get("content_elements")),
        "termino": termino,
    }


def pedir(sesion, termino, pagina):
    consulta = {"feed_size": TAM_PAGINA, "page": pagina, "query": termino, "size": TAM_PAGINA}
    parametros = {"query": json.dumps(consulta, separators=(",", ":")), "_website": "eldoce"}
    for intento in range(3):
        try:
            respuesta = sesion.get(API, params=parametros, timeout=60)
            if respuesta.status_code in (403, 429):
                sys.exit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
            respuesta.raise_for_status()
            return respuesta.json()
        except (requests.RequestException, ValueError) as error:
            print(f"  error en {termino} p{pagina}: {error}", flush=True)
            time.sleep(PAUSA * 5 * (intento + 1))
    sys.exit(f"Fallaron 3 intentos en {termino} p{pagina}; el avance quedó guardado.")


def descargar(terminos):
    DATA.mkdir(exist_ok=True)
    progreso = json.loads(PROGRESO.read_text(encoding="utf-8")) if PROGRESO.exists() else {}
    sesion = requests.Session()
    sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
    for numero, termino in enumerate(terminos, 1):
        pagina = progreso.get(termino, 1)
        if pagina is None:
            print(f"El Doce [{numero}/{len(terminos)}] {termino}: ya estaba descargado", flush=True)
            continue
        avance = Avance(f"El Doce [{numero}/{len(terminos)}] {termino}", inicio=(pagina - 1) * TAM_PAGINA)
        while pagina is not None:
            datos = pedir(sesion, termino, pagina)
            filas = [a_fila(nota, termino) for nota in datos.get("content_elements") or []]
            with CRUDO.open("a", encoding="utf-8") as archivo:
                for fila in filas:
                    archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
            total = datos.get("count") or 0
            avance.paso(len(filas), sum(map(relevante, filas)), total)
            pagina = pagina + 1 if filas and pagina * TAM_PAGINA < total else None
            progreso[termino] = pagina
            PROGRESO.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
            time.sleep(PAUSA)


def consolidar(crudo=CRUDO, salida=SALIDA, diccionario=BUSQUEDAS_RESIDUOS):
    filas = pd.read_json(crudo, lines=True, dtype={"id": str}, convert_dates=False)
    terminos = filas.groupby("id")["termino"].agg(lambda t: sorted(set(t)))
    notas = filas.drop_duplicates("id").drop(columns="termino").set_index("id")
    notas["terminos_busqueda"] = terminos
    texto = (notas["titulo"].fillna("") + "\n" + notas["bajada"].fillna("") + "\n" + notas["body"].fillna(""))
    normalizado = texto.map(normalizar)
    notas["terminos_en_texto"] = [
        [t for t in ts if normalizar(t) in n] for ts, n in zip(notas["terminos_busqueda"], normalizado)
    ]
    notas["diccionario_en_texto"] = [
        [t for t in diccionario if normalizar(t) in n] for n in normalizado
    ]
    notas["keywords_core"] = [
        [k for k in CORE_KEYWORDS_RESIDUOS if re.search(k, t, re.I)] for t in texto
    ]
    notas["fecha"] = pd.to_datetime(notas["fecha"], utc=True, format="ISO8601")
    notas = notas.reset_index().sort_values("fecha", ascending=False)
    notas.to_parquet(salida, index=False)
    return notas


def resumir(notas):
    print(f"\nNotas únicas: {len(notas)}")
    print(f"Con cuerpo: {(notas['body'].str.len() > 0).sum()}")
    print(f"Con su término de búsqueda en el texto: {(notas['terminos_en_texto'].str.len() > 0).sum()}")
    print(f"Con algún término del diccionario: {(notas['diccionario_en_texto'].str.len() > 0).sum()}")
    print(f"Con alguna keyword core: {(notas['keywords_core'].str.len() > 0).sum()}")
    print("\nPor tipo:\n" + notas["tipo"].value_counts(dropna=False).to_string())
    print("\nPor año:\n" + notas["fecha"].dt.year.value_counts().sort_index().to_string())


def selfcheck():
    nota = {
        "_id": "A1",
        "website_url": "/actualidad/nota/",
        "headlines": {"basic": "Basural &amp; multa"},
        "subheadlines": {"basic": "Bajada"},
        "display_date": "2026-01-02T00:00:00Z",
        "taxonomy": {"primary_section": {"name": "Actualidad"}, "tags": [{"text": "basura"}]},
        "subtype": "article",
        "content_elements": [
            {"type": "text", "content": "Uno <b>dos</b>"},
            {"type": "image", "content": "no"},
            {"type": "list", "items": [{"content": "tres"}]},
        ],
    }
    fila = a_fila(nota, "basural")
    assert fila["url"] == "https://eldoce.tv/actualidad/nota/"
    assert fila["titulo"] == "Basural & multa"
    assert fila["body"] == "Uno dos\ntres"
    assert fila["tags"] == ["basura"]
    assert normalizar("Plásticos") == "plasticos"
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS_RESIDUOS)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        descargar(args.terminos)
        resumir(consolidar())
