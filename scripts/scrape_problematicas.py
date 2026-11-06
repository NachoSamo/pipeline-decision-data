"""Descarga notas de problemáticas por vertical desde portales con API de WordPress.

Guarda en data/<vertical>/<fuente>.parquet. No toca los Parquet de residuos.
Busca con el tema de la vertical (BUSQUEDAS_*_<VERTICAL>) y después marca cada nota con las
señales de problema y de opinión, sin descartar ninguna. Si no se indica --vertical, usa
biodiversidad. El circuito está en docs/circuito-problematicas.md.

Para correr en paralelo, una terminal por fuente. Nunca dos terminales con la misma fuente.
Se puede cortar y retomar volviendo a ejecutar el mismo comando.

Uso:
    python scripts/scrape_problematicas.py --selfcheck
    python scripts/scrape_problematicas.py --listar
    python scripts/scrape_problematicas.py mongabay
    python scripts/scrape_problematicas.py grist --terminos wetlands
    python scripts/scrape_problematicas.py mongabay --desde 2024-01-01
    python scripts/scrape_problematicas.py grist --vertical movilidad
"""

import argparse
import re
from pathlib import Path

import pandas as pd

import progreso
from diccionarios.keywords_biodiversidad import (
    BUSQUEDAS_BIODIVERSIDAD,
    BUSQUEDAS_INGLES_BIODIVERSIDAD,
    BUSQUEDAS_PORTUGUES_BIODIVERSIDAD,
)
from diccionarios.keywords_movilidad import BUSQUEDAS_INGLES_MOVILIDAD, BUSQUEDAS_MOVILIDAD, BUSQUEDAS_PORTUGUES_MOVILIDAD
from diccionarios.keywords_senales import SENALES_OPINION, SENALES_PROBLEMA
from progreso import normalizar
from scrape_wordpress import descargar

# No usa dataset.DATA, que apunta a data/residuos o data/soluciones.
DATA = Path(__file__).resolve().parent.parent / "data"

VERTICAL = "biodiversidad"  # la vertical por defecto
DESDE = "2021-01-01"

# Términos por idioma y fuentes que aplican a cada vertical.
VERTICALES = {
    "biodiversidad": {
        "es": BUSQUEDAS_BIODIVERSIDAD,
        "en": BUSQUEDAS_INGLES_BIODIVERSIDAD,
        "pt": BUSQUEDAS_PORTUGUES_BIODIVERSIDAD,
        "fuentes": ["mongabay", "mongabayen", "grist", "ecoticias", "ciclovivo", "visionsustentable", "ecomundo"],
    },
    "movilidad": {
        "es": BUSQUEDAS_MOVILIDAD,
        "en": BUSQUEDAS_INGLES_MOVILIDAD,
        "pt": BUSQUEDAS_PORTUGUES_MOVILIDAD,
        # Mongabay se deja afuera: es de biodiversidad y bosques.
        "fuentes": ["grist", "ecoticias", "ciclovivo", "visionsustentable", "ecomundo"],
    },
}

# clave: (nombre, sitio, idioma, segundos entre pedidos, tipo de voz)
# Las pausas son las mismas que usan los scripts de residuos para cada sitio.
FUENTES = {
    "mongabay": ("Mongabay", "https://es.mongabay.com", "es", 10, "medio_especializado"),
    "mongabayen": ("Mongabay en inglés", "https://news.mongabay.com", "en", 10, "medio_especializado"),
    "grist": ("Grist", "https://grist.org", "en", 4, "medio_especializado"),
    "ecoticias": ("Ecoticias", "https://www.ecoticias.com", "es", 4, "medio_especializado"),
    "ciclovivo": ("CicloVivo", "https://ciclovivo.com.br", "pt", 4, "medio_especializado"),
    "visionsustentable": ("Visión Sustentable", "https://www.visionsustentable.com", "es", 4, "medio_especializado"),
    "ecomundo": ("Ecomundo", "https://www.ecomundo.com.ar", "es", 4, "medio_especializado"),
}

# Secciones o etiquetas que indican una columna de opinión.
SECCIONES_OPINION = ["opinion", "columna", "commentary", "op-ed", "editorial", "analisis", "artigo", "perspective"]


def carpeta(vertical=VERTICAL):
    return DATA / vertical


CARPETA = carpeta()


def patron(palabras):
    # Palabra completa con hasta 3 letras de más, para plurales y femeninos.
    # Así "ong" no coincide con "ongoing" y "loss" sí coincide con "losses".
    return re.compile(r"\b(" + "|".join(re.escape(normalizar(p)) for p in palabras) + r")\w{0,3}\b")


PATRON_PROBLEMA = patron(SENALES_PROBLEMA)
PATRON_OPINION = patron(SENALES_OPINION)
PATRON_SECCION = patron(SECCIONES_OPINION)


def encontradas(patron_, texto):
    return sorted({m.group(1) for m in patron_.finditer(texto)})


def marcar(notas, tipo_voz, vertical=VERTICAL):
    texto = (notas["titulo"].fillna("") + "\n" + notas["bajada"].fillna("") + "\n" + notas["body"].fillna(""))
    normalizado = texto.map(normalizar)
    # Algunas fuentes, como La Nación, traen etiquetas vacías (None) dentro de la lista.
    etiquetas = notas["seccion"].fillna("").astype(str) + " " + notas["tags"].map(
        lambda t: " ".join(str(x) for x in t if x) if t is not None else "")
    es_opinion = etiquetas.map(lambda e: bool(PATRON_SECCION.search(normalizar(e))))
    notas = notas.copy()
    notas["vertical"] = vertical
    notas["tipo_voz"] = es_opinion.map({True: "opinion", False: tipo_voz})
    notas["senal_problema"] = normalizado.map(lambda n: encontradas(PATRON_PROBLEMA, n))
    notas["senal_opinion"] = normalizado.map(lambda n: encontradas(PATRON_OPINION, n))
    return notas


def raices(terminos):
    return [normalizar(t) for t in terminos]


def bajar(clave, terminos=None, desde=DESDE, vertical=VERTICAL):
    nombre, sitio, idioma, pausa, tipo_voz = FUENTES[clave]
    diccionario = VERTICALES[vertical][idioma]
    terminos = terminos or diccionario
    consultas = [(t, {"search": t, "after": f"{desde}T00:00:00"}) for t in terminos]
    progreso.ETIQUETA = vertical  # el log dice "mencionan <vertical>"
    descargar(
        clave,
        nombre,
        sitio,
        consultas,
        pausa=pausa,
        raices=raices(diccionario),
        diccionario=diccionario,
        carpeta=carpeta(vertical),
        sufijo="",
        al_terminar=lambda notas: marcar(notas, tipo_voz, vertical),
    )
    salida = carpeta(vertical) / f"{clave}.parquet"
    if salida.exists():
        notas = pd.read_parquet(salida, columns=["tipo_voz", "senal_problema", "senal_opinion"])
        print(f"Con señal de problema: {(notas['senal_problema'].str.len() > 0).sum()}")
        print(f"Con señal de opinión o voz especializada: {(notas['senal_opinion'].str.len() > 0).sum()}")
        print("Por tipo de voz:\n" + notas["tipo_voz"].value_counts().to_string())


def selfcheck():
    for config in VERTICALES.values():
        assert set(config["fuentes"]) <= set(FUENTES)
        assert all(FUENTES[f][2] in config for f in config["fuentes"])
    assert encontradas(PATRON_PROBLEMA, normalizar("Advierten una CRISIS por la pérdida de humedales")) == [
        "advierte", "crisis", "perdida"]
    assert encontradas(PATRON_OPINION, normalizar("An ongoing project")) == []
    assert encontradas(PATRON_OPINION, normalizar("Según las ONGs y una bióloga del CONICET")) == [
        "biolog", "conicet", "ong"]
    assert encontradas(PATRON_PROBLEMA, normalizar("Habitat losses")) == ["loss"]
    notas = pd.DataFrame({
        "titulo": ["Alerta por el desmonte", "Inauguran un parque"],
        "bajada": ["", None],
        "body": ["Una investigadora advierte", "Fiesta"],
        "seccion": ["Opinión", "Noticias"],
        "tags": [["Bosques", None], None],
    })
    marcadas = marcar(notas, "medio_especializado")
    assert list(marcadas["tipo_voz"]) == ["opinion", "medio_especializado"]
    assert marcadas["senal_problema"][0] == ["advierte", "alerta"]
    assert marcadas["senal_problema"][1] == [] and marcadas["senal_opinion"][0] == ["investigador"]
    assert marcadas["vertical"].tolist() == ["biodiversidad", "biodiversidad"]
    assert marcar(notas, "diario", "movilidad")["vertical"].tolist() == ["movilidad", "movilidad"]
    assert CARPETA.parts[-2:] == ("data", "biodiversidad")
    assert carpeta("movilidad").parts[-2:] == ("data", "movilidad")
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fuentes", nargs="*", help=", ".join(FUENTES))
    parser.add_argument("--vertical", default=VERTICAL, choices=sorted(VERTICALES))
    parser.add_argument("--terminos", nargs="+", help="Reemplaza el diccionario del idioma de la fuente.")
    parser.add_argument("--desde", default=DESDE, help=f"Fecha mínima AAAA-MM-DD (por defecto {DESDE}).")
    parser.add_argument("--listar", action="store_true", help="Muestra las fuentes de la vertical.")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    disponibles = VERTICALES[args.vertical]["fuentes"]
    desconocidas = set(args.fuentes) - set(disponibles)
    if desconocidas:
        parser.error(f"fuentes que no aplican a {args.vertical}: {', '.join(sorted(desconocidas))}")
    if args.selfcheck:
        selfcheck()
    elif args.listar or not args.fuentes:
        print(f"Fuentes para {args.vertical}:")
        for clave in disponibles:
            nombre, sitio, idioma, pausa, _ = FUENTES[clave]
            print(f"{clave:<18} {nombre:<20} {idioma}  {pausa:>2} s  {sitio}")
        if not args.fuentes:
            print("\nIndicá una o más fuentes. Para paralelo: una terminal por fuente.")
    else:
        for clave in args.fuentes:
            print(f"\n=== {FUENTES[clave][0]} ({args.vertical}) ===", flush=True)
            try:
                bajar(clave, args.terminos, args.desde, args.vertical)
            except SystemExit as motivo:
                print(f"{FUENTES[clave][0]}: quedó incompleta. {motivo}", flush=True)
