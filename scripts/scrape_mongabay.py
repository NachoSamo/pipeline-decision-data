"""Descarga notas de Mongabay Latam con su API de WordPress.

Su robots.txt pide 10 segundos entre pedidos.

Uso:
    python scripts/scrape_mongabay.py --selfcheck
    python scripts/scrape_mongabay.py
    python scripts/scrape_mongabay.py --terminos residuos
"""

import argparse

from diccionarios.keywords_residuos import BUSQUEDAS_PRECISAS
from scrape_wordpress import descargar, selfcheck

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS_PRECISAS)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        consultas = [(t, {"search": t}) for t in args.terminos]
        descargar("mongabay", "Mongabay", "https://es.mongabay.com", consultas, pausa=10)
