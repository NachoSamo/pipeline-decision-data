"""Descarga notas de Ecomundo con su API de WordPress.

Baja la categoría Reciclado completa y después busca el diccionario de residuos.

Uso:
    python scripts/scrape_ecomundo.py --selfcheck
    python scripts/scrape_ecomundo.py
    python scripts/scrape_ecomundo.py --terminos residuos
"""

import argparse

from dataset import NOMBRE
from diccionarios.keywords_residuos import BUSQUEDAS
from scrape_wordpress import descargar, selfcheck

CATEGORIA_RECICLADO = 36

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminos", nargs="+")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        consultas = [(t, {"search": t}) for t in args.terminos or BUSQUEDAS]
        if not args.terminos and NOMBRE == "residuos":
            consultas.insert(0, ("categoría Reciclado", {"categories": CATEGORIA_RECICLADO}))
        descargar("ecomundo", "Ecomundo", "https://www.ecomundo.com.ar", consultas)
