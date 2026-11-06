"""Descarga notas de problemáticas de los diarios, reusando sus scripts de residuos.

Los scripts de cada diario tienen fijos el diccionario, las etiquetas y las rutas de residuos.
Este script reemplaza esos valores por los de la vertical antes de llamar a sus funciones,
así no hace falta tocarlos. Guarda en data/<vertical>/<fuente>.parquet.
Si no se indica --vertical, usa biodiversidad.

Cada diario usa una vía distinta, la misma que en residuos:
    eldoce, tn    buscador del sitio, con BUSQUEDAS_<VERTICAL>
    infobae       páginas de etiquetas; de las amplias, solo notas con el tema en título o bajada
    clarin        páginas de etiquetas; ídem
    lanacion      sitemap histórico, filtrando URLs por RAICES_<VERTICAL>
    cba24n        sitemaps mensuales, ídem

Una terminal por diario, y nunca el mismo diario en dos verticales a la vez.
Se puede cortar y retomar volviendo a ejecutar el mismo comando.

Uso:
    python scripts/scrape_diarios_problematicas.py --selfcheck
    python scripts/scrape_diarios_problematicas.py infobae
    python scripts/scrape_diarios_problematicas.py clarin --limite 5
    python scripts/scrape_diarios_problematicas.py tn --terminos humedales
    python scripts/scrape_diarios_problematicas.py tn --vertical movilidad
"""

import argparse
import functools

import requests

import progreso
from diccionarios import keywords_biodiversidad, keywords_movilidad
import scrape_cba24n
import scrape_eldoce
import scrape_infobae
import scrape_ldjson
import scrape_tn
from scrape_eldoce import consolidar, resumir
from scrape_problematicas import VERTICAL, carpeta, marcar

FUENTES = ["eldoce", "tn", "infobae", "clarin", "lanacion", "cba24n"]
MODULOS = [scrape_eldoce, scrape_tn, scrape_infobae, scrape_ldjson, scrape_cba24n]
VERTICALES = ["biodiversidad", "movilidad"]
DICCIONARIOS = {"biodiversidad": keywords_biodiversidad, "movilidad": keywords_movilidad}


def vocabulario(vertical):
    """Listas de keywords_<vertical>.py, por ejemplo BUSQUEDAS_MOVILIDAD."""
    keywords = DICCIONARIOS[vertical]
    sufijo = vertical.upper()
    return {
        "busquedas": getattr(keywords, f"BUSQUEDAS_{sufijo}"),
        "raices": getattr(keywords, f"RAICES_{sufijo}"),
        "tags_infobae": getattr(keywords, f"TAGS_INFOBAE_{sufijo}"),
        "tags_infobae_amplios": getattr(keywords, f"TAGS_INFOBAE_AMPLIOS_{sufijo}"),
        "tags_clarin": getattr(keywords, f"TAGS_CLARIN_{sufijo}"),
        "tags_clarin_amplios": getattr(keywords, f"TAGS_CLARIN_AMPLIOS_{sufijo}"),
    }


PEDIR_ELDOCE = scrape_eldoce.pedir
# El buscador de El Doce falla en páginas profundas: 502 en la 111 de "colectivos", 504 en la 81 de
# "veredas". Pasada esta página, un error del servidor da el término por terminado. Un bloqueo
# (403 o 429) corta siempre.
TOPE_PAGINAS_ELDOCE = 20
PAUSA_CBA24N = 20


def pedir_eldoce_con_tope(sesion, termino, pagina):
    try:
        return PEDIR_ELDOCE(sesion, termino, pagina)
    except SystemExit as motivo:
        if pagina <= TOPE_PAGINAS_ELDOCE or "respondió" in str(motivo):
            raise
        print(f"El Doce {termino}: el buscador no deja pasar de la página {pagina - 1}; sigo con el próximo término.",
              flush=True)
        return {"content_elements": [], "count": 0}


PEDIR_TN = scrape_tn.pedir


def pedir_tn_con_tope(sesion, termino, pagina):
    # El buscador de TN responde 400 a partir de la página 501 (10.000 resultados), como en "trenes".
    try:
        return PEDIR_TN(sesion, termino, pagina)
    except SystemExit as motivo:
        if pagina <= TOPE_PAGINAS_ELDOCE or "respondió" in str(motivo):
            raise
        print(f"TN {termino}: el buscador no deja pasar de la página {pagina - 1}; sigo con el próximo término.",
              flush=True)
        return {"content_elements": [], "count": 0}


PEDIR_NOTA = scrape_infobae.pedir

# raices_en recibe las raíces como valor por defecto, fijado al importar con las de residuos.
# Por eso no alcanza con cambiar la lista: se reemplaza la función.
RAICES_EN = scrape_ldjson.raices_en
RAICES = []


def raices_en_vertical(url, raices=None):
    return RAICES_EN(url, RAICES if raices is None else raices)


def redirige_en_circulo(sesion, url):
    try:
        sesion.get(url, timeout=60)
    except requests.TooManyRedirects:
        return True
    except requests.RequestException:
        return False
    return False


def pedir_nota_salteando_redirecciones(sesion, url, **kwargs):
    # Una nota de Clarín redirigía en círculo y cortaba toda la descarga. Solo se saltea ese caso:
    # si falla por otra causa, como un corte de internet, se sigue cortando.
    try:
        return PEDIR_NOTA(sesion, url, **kwargs)
    except SystemExit:
        if not redirige_en_circulo(sesion, url):
            raise
        print(f"  salteo {url}: redirige en círculo", flush=True)
        return None


def aplicar(vertical=VERTICAL):
    """Cambia residuos por la vertical en los módulos de los diarios."""
    v = vocabulario(vertical)
    destino = carpeta(vertical)
    destino.mkdir(parents=True, exist_ok=True)
    ruta = lambda fuente, extension: destino / f"{fuente}.{extension}"
    relevante = functools.partial(progreso.relevante, raices=v["raices"])
    progreso.ETIQUETA = vertical  # el log dice "mencionan <vertical>"
    for modulo in MODULOS:
        modulo.relevante = relevante
    for modulo, fuente in ((scrape_eldoce, "eldoce"), (scrape_tn, "tn")):
        modulo.CRUDO = ruta(fuente, "jsonl")
        modulo.PROGRESO = ruta(fuente, "progreso.json")
    scrape_infobae.LISTADO = ruta("infobae", "listado.jsonl")
    scrape_infobae.CRUDO = ruta("infobae", "jsonl")
    scrape_infobae.TAGS_INFOBAE_PRINCIPALES = v["tags_infobae"]
    scrape_infobae.TAGS_INFOBAE_AMPLIOS = v["tags_infobae_amplios"]
    scrape_infobae.PRIORITARIAS_TEXTO = v["busquedas"]
    scrape_ldjson.rutas = lambda fuente: (ruta(fuente, "listado.jsonl"), ruta(fuente, "jsonl"), ruta(fuente, "parquet"))
    RAICES[:] = v["raices"]
    scrape_ldjson.raices_en = scrape_cba24n.raices_en = raices_en_vertical
    scrape_ldjson.PRIORITARIAS_URL = v["raices"]
    scrape_ldjson.TAGS_CLARIN_PRINCIPALES = v["tags_clarin"]
    scrape_ldjson.TAGS_CLARIN_AMPLIOS = v["tags_clarin_amplios"]
    scrape_cba24n.LISTADO = ruta("cba24n", "listado.jsonl")
    scrape_cba24n.CRUDO = ruta("cba24n", "jsonl")
    # CBA24N respondió 429 con 12 s de pausa en movilidad (6/11/2026), después de unas 70 notas.
    scrape_cba24n.PAUSA = max(scrape_cba24n.PAUSA, PAUSA_CBA24N)
    scrape_eldoce.pedir = pedir_eldoce_con_tope
    scrape_tn.pedir = pedir_tn_con_tope
    for modulo in (scrape_infobae, scrape_ldjson, scrape_cba24n):
        modulo.pedir = pedir_nota_salteando_redirecciones
    return v


def sesion_nueva():
    sesion = requests.Session()
    sesion.headers["User-Agent"] = "pipeline-decision-data/0.1"
    return sesion


def bajar(fuente, vertical=VERTICAL, limite=None, terminos=None):
    v = aplicar(vertical)
    if fuente == "eldoce":
        scrape_eldoce.descargar(terminos or v["busquedas"])
    elif fuente == "tn":
        scrape_tn.descargar(terminos or v["busquedas"])
    elif fuente == "infobae":
        sesion = sesion_nueva()
        scrape_infobae.listar(sesion)
        scrape_infobae.descargar_notas(sesion, limite, solo_prioritarias=True)
    elif fuente in ("clarin", "lanacion"):
        sesion = sesion_nueva()
        scrape_ldjson.listar(fuente, sesion)
        scrape_ldjson.descargar(fuente, sesion, limite, solo_prioritarias=fuente == "clarin")
    elif fuente == "cba24n":
        sesion = sesion_nueva()
        scrape_cba24n.listar(sesion)
        scrape_cba24n.descargar(sesion, limite)
    crudo, salida = carpeta(vertical) / f"{fuente}.jsonl", carpeta(vertical) / f"{fuente}.parquet"
    if not crudo.exists():
        print("No se encontraron notas.")
        return
    notas = marcar(consolidar(crudo, salida, v["busquedas"]), "diario", vertical)
    notas.to_parquet(salida, index=False)
    resumir(notas)
    print(f"Con señal de problema: {(notas['senal_problema'].str.len() > 0).sum()}")
    print(f"Con señal de opinión o voz especializada: {(notas['senal_opinion'].str.len() > 0).sum()}")
    print("Por tipo de voz:\n" + notas["tipo_voz"].value_counts().to_string())


def mencionan(clase_avance):
    avance = clase_avance("x")
    avance.nuevas = avance.utiles = 1
    return avance.linea().split(" | ")[1].split(" 1 ")[0]


def selfcheck():
    for vertical in VERTICALES:
        vocabulario(vertical)  # falla si falta alguna lista en keywords_<vertical>.py
    aplicar("biodiversidad")
    bio = carpeta("biodiversidad")
    assert scrape_eldoce.CRUDO == bio / "eldoce.jsonl" and scrape_tn.PROGRESO == bio / "tn.progreso.json"
    assert scrape_ldjson.rutas("clarin")[2] == bio / "clarin.parquet"
    assert scrape_ldjson.raices_en("https://x/sociedad/peligra-el-humedal-nid1/") == ["humedal"]
    assert scrape_ldjson.raices_en("https://x/sociedad/el-basural-nid1/") == []
    assert scrape_cba24n.raices_en("https://x/cordoba/desmonte-en-las-sierras_a1") == ["desmonte"]
    assert scrape_tn.relevante({"titulo": "Incendios forestales en Córdoba"})
    assert not scrape_tn.relevante({"titulo": "Un basural en la ciudad"})
    dic = [progreso.normalizar(t) for t in keywords_biodiversidad.BUSQUEDAS_BIODIVERSIDAD]
    assert scrape_infobae.prioridad({"tags": {"humedales"}, "titulo": "", "bajada": ""}, dic) == 0
    assert scrape_infobae.prioridad({"tags": {"animales"}, "titulo": "Polinizadores en riesgo", "bajada": ""}, dic) == 1
    assert scrape_infobae.prioridad({"tags": {"animales"}, "titulo": "Tu perro", "bajada": None}, dic) == 2
    assert not scrape_ldjson.es_prioritaria({"animales"}, "https://x/sociedad/tu-perro-nid1/")
    assert scrape_ldjson.es_prioritaria({"humedales"}, "https://x/sociedad/ley-nid1/")
    assert scrape_ldjson.es_prioritaria({"animales"}, "https://x/sociedad/peligra-el-humedal-nid1/")
    assert mencionan(scrape_tn.Avance) == "mencionan biodiversidad"

    aplicar("movilidad")
    mov = carpeta("movilidad")
    assert scrape_tn.CRUDO == mov / "tn.jsonl" and scrape_ldjson.rutas("lanacion")[1] == mov / "lanacion.jsonl"
    assert scrape_ldjson.raices_en("https://x/sociedad/paro-de-colectivos-en-cordoba-nid1/") == ["colectivo"]
    assert scrape_ldjson.raices_en("https://x/deportes/el-entrenador-del-club-nid1/") == []
    assert scrape_tn.relevante({"titulo": "Nueva ciclovía en el centro"})
    assert scrape_infobae.prioridad({"tags": {"colectivos"}, "titulo": "", "bajada": ""}, []) == 0
    assert scrape_cba24n.raices_en("https://x/cordoba/nueva-ciclovia-en-el-centro_a1") == ["ciclovia"]
    assert mencionan(scrape_tn.Avance) == "mencionan movilidad"

    global PEDIR_ELDOCE
    original, PEDIR_ELDOCE = PEDIR_ELDOCE, lambda *_: (_ for _ in ()).throw(SystemExit("502"))
    try:
        assert scrape_eldoce.pedir(None, "colectivos", 111) == {"content_elements": [], "count": 0}
        try:
            scrape_eldoce.pedir(None, "colectivos", 5)
            raise AssertionError("una falla antes del tope tiene que cortar")
        except SystemExit:
            pass
        PEDIR_ELDOCE = lambda *_: (_ for _ in ()).throw(SystemExit("El sitio respondió 429: corto para no insistir."))
        try:
            scrape_eldoce.pedir(None, "colectivos", 111)
            raise AssertionError("un bloqueo tiene que cortar aunque la página sea profunda")
        except SystemExit:
            pass
    finally:
        PEDIR_ELDOCE = original

    global PEDIR_TN, PEDIR_NOTA
    original_tn, PEDIR_TN = PEDIR_TN, lambda *_: (_ for _ in ()).throw(SystemExit("Fallaron 3 intentos"))
    original_nota, PEDIR_NOTA = PEDIR_NOTA, lambda *_, **__: (_ for _ in ()).throw(SystemExit("Fallaron 3 intentos"))

    class SesionFalsa:
        def __init__(self, error):
            self.error = error

        def get(self, *_, **__):
            raise self.error

    try:
        assert scrape_tn.pedir(None, "trenes", 501) == {"content_elements": [], "count": 0}
        assert scrape_ldjson.pedir(SesionFalsa(requests.TooManyRedirects()), "https://x/nota") is None
        try:
            scrape_ldjson.pedir(SesionFalsa(requests.ConnectionError()), "https://x/nota")
            raise AssertionError("un corte de conexión tiene que cortar")
        except SystemExit:
            pass
    finally:
        PEDIR_TN, PEDIR_NOTA = original_tn, original_nota
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fuente", nargs="?", choices=FUENTES)
    parser.add_argument("--vertical", default=VERTICAL, choices=VERTICALES)
    parser.add_argument("--limite", type=int, help="Infobae, Clarín, La Nación y CBA24N: cuántas notas bajar.")
    parser.add_argument("--terminos", nargs="+", help="El Doce y TN: reemplaza el diccionario.")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    elif not args.fuente:
        parser.error("indicá un diario: " + ", ".join(FUENTES))
    else:
        print(f"\n=== {args.fuente} ({args.vertical}) ===", flush=True)
        bajar(args.fuente, args.vertical, args.limite, args.terminos)
