"""Funciones compartidas para portales de WordPress con API REST abierta."""

import json
import re
import time

import requests

from keywords import BUSQUEDAS_RESIDUOS, RAICES_RESIDUOS
from progreso import Avance, relevante
from scrape_eldoce import DATA, consolidar, limpiar, resumir

TAM_PAGINA = 100
PAUSA = 4


def html_a_texto(contenido):
    con_saltos = re.sub(r"</(p|h[1-6]|li)>", "\n", contenido or "", flags=re.I)
    lineas = (limpiar(linea) for linea in con_saltos.split("\n"))
    return "\n".join(linea for linea in lineas if linea)


def a_fila(nombre, post, termino):
    grupos = (post.get("_embedded") or {}).get("wp:term") or []
    # Algunos sitios devuelven objetos de error dentro de wp:term.
    nombres = [t["name"] for grupo in grupos if isinstance(grupo, list) for t in grupo if "name" in t]
    return {
        "id": post["link"],
        "fuente": nombre,
        "url": post["link"],
        "titulo": limpiar(post["title"]["rendered"]),
        "bajada": html_a_texto(post["excerpt"]["rendered"]),
        "fecha": post.get("date_gmt") or post.get("date"),
        "seccion": nombres[0] if nombres else None,
        "tags": nombres[1:],
        "tipo": post.get("type"),
        "body": html_a_texto(post["content"]["rendered"]),
        "termino": termino,
    }


def pedir(sesion, url, parametros, pausa, intentos=3):
    for intento in range(intentos):
        try:
            respuesta = sesion.get(url, params=parametros, timeout=120)
            if respuesta.status_code in (403, 429):
                raise SystemExit(f"El sitio respondió {respuesta.status_code}: corto para no insistir.")
            respuesta.raise_for_status()
            return respuesta
        except requests.RequestException as error:
            print(f"  error, reintento {intento + 1} de {intentos}: {error}", flush=True)
            time.sleep(pausa * 5 * (intento + 1))
    raise SystemExit(f"Fallaron {intentos} intentos en {url}; el avance quedó guardado.")


def descargar(clave, nombre, base, consultas, pausa=PAUSA, raices=RAICES_RESIDUOS, diccionario=BUSQUEDAS_RESIDUOS):
    DATA.mkdir(exist_ok=True)
    crudo = DATA / f"{clave}_residuos.jsonl"
    progreso_ruta = DATA / f"{clave}_residuos.progreso.json"
    progreso = json.loads(progreso_ruta.read_text(encoding="utf-8")) if progreso_ruta.exists() else {}
    sesion = requests.Session()
    sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
    campos = "id,date,date_gmt,link,title,excerpt,content,type,_links,_embedded"
    for numero, (termino, filtro) in enumerate(consultas, 1):
        pagina = progreso.get(termino, 1)
        if pagina is None:
            print(f"{nombre} [{numero}/{len(consultas)}] {termino}: ya estaba descargado", flush=True)
            continue
        avance = Avance(f"{nombre} [{numero}/{len(consultas)}] {termino}", inicio=(pagina - 1) * TAM_PAGINA)
        while pagina is not None:
            parametros = {**filtro, "per_page": TAM_PAGINA, "page": pagina, "_fields": campos, "_embed": "wp:term"}
            respuesta = pedir(sesion, f"{base}/wp-json/wp/v2/posts", parametros, pausa)
            filas = [a_fila(nombre, post, termino) for post in respuesta.json()]
            with crudo.open("a", encoding="utf-8") as archivo:
                for fila in filas:
                    archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
            paginas = int(respuesta.headers.get("X-WP-TotalPages", 0))
            total = int(respuesta.headers.get("X-WP-Total", 0))
            avance.paso(len(filas), sum(relevante(fila, raices) for fila in filas), total)
            pagina = pagina + 1 if pagina < paginas else None
            progreso[termino] = pagina
            progreso_ruta.write_text(json.dumps(progreso, ensure_ascii=False), encoding="utf-8")
            time.sleep(pausa)
    if crudo.exists():
        resumir(consolidar(crudo, DATA / f"{clave}_residuos.parquet", diccionario))
    else:
        print("No se encontraron notas.")


def selfcheck():
    post = {
        "link": "https://x/nota/",
        "title": {"rendered": "A &amp; B"},
        "excerpt": {"rendered": "<p>Bajada</p>"},
        "content": {"rendered": "<p>Uno <b>dos</b></p>\n<p>Tres</p>"},
        "date_gmt": "2026-01-01T00:00:00",
        "type": "post",
        "_embedded": {"wp:term": [[{"name": "Reciclado"}], [{"name": "PET"}]]},
    }
    fila = a_fila("Prueba", post, "residuos")
    assert fila["titulo"] == "A & B"
    assert fila["body"] == "Uno dos\nTres"
    assert fila["seccion"] == "Reciclado" and fila["tags"] == ["PET"]
    post["_embedded"]["wp:term"] = [{"code": "error"}, [{"name": "PET"}]]
    assert a_fila("Prueba", post, "residuos")["seccion"] == "PET"
    print("selfcheck ok")
