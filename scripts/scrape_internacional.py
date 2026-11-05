"""Descarga notas internacionales en inglés desde 2024 con la API de WordPress.

Sin argumentos baja las cuatro fuentes, una después de otra. Se puede cortar y
retomar.

Uso:
    python scripts/scrape_internacional.py --selfcheck
    python scripts/scrape_internacional.py
    python scripts/scrape_internacional.py circularonline grist
    python scripts/scrape_internacional.py grist --terminos recycling
"""

import argparse

from keywords import BUSQUEDAS_INGLES_RESIDUOS, RAICES_INGLES_RESIDUOS
from progreso import relevante
from scrape_wordpress import descargar

DESDE = "2024-01-01T00:00:00"

# clave: (nombre, sitio, segundos entre pedidos)
FUENTES = {
    "resourcerecycling": ("Resource Recycling", "https://resource-recycling.com", 4),
    "circularonline": ("Circular Online", "https://www.circularonline.co.uk", 4),
    "mongabayen": ("Mongabay en inglés", "https://news.mongabay.com", 10),
    "grist": ("Grist", "https://grist.org", 4),
}


def consultas(terminos):
    return [(t, {"search": t, "after": DESDE}) for t in terminos]


def selfcheck():
    assert consultas(["recycling"]) == [("recycling", {"search": "recycling", "after": DESDE})]
    assert relevante({"titulo": "New Landfill rules"}, RAICES_INGLES_RESIDUOS)
    assert not relevante({"titulo": "Elections today"}, RAICES_INGLES_RESIDUOS)
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuentes", nargs="*", help=", ".join(FUENTES))
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS_INGLES_RESIDUOS)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    desconocidas = set(args.fuentes) - set(FUENTES)
    if desconocidas:
        parser.error(f"fuentes desconocidas: {', '.join(desconocidas)}")
    if args.selfcheck:
        selfcheck()
    else:
        for clave in args.fuentes or FUENTES:
            nombre, sitio, pausa = FUENTES[clave]
            try:
                descargar(
                    clave,
                    nombre,
                    sitio,
                    consultas(args.terminos),
                    pausa=pausa,
                    raices=RAICES_INGLES_RESIDUOS,
                    diccionario=BUSQUEDAS_INGLES_RESIDUOS,
                )
            except SystemExit as motivo:
                print(f"{nombre}: quedó incompleta. {motivo} Sigo con la próxima fuente.", flush=True)
