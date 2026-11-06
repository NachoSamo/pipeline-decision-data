"""Descarga notas de Visión Sustentable con su API de WordPress.

Uso:
    python scripts/scrape_visionsustentable.py --selfcheck
    python scripts/scrape_visionsustentable.py
    python scripts/scrape_visionsustentable.py --terminos residuos
"""

import argparse

from diccionarios.keywords_residuos import BUSQUEDAS
from scrape_wordpress import descargar, selfcheck

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+", default=BUSQUEDAS)
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        consultas = [(t, {"search": t}) for t in args.terminos]
        descargar("visionsustentable", "Visión Sustentable", "https://www.visionsustentable.com", consultas)
