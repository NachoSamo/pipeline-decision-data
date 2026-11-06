"""Define en qué dataset trabajan los scripts. Por defecto, residuos."""

import os
from pathlib import Path

NOMBRE = os.environ.get("DATASET", "residuos")
_RAIZ = Path(__file__).resolve().parent.parent / "data"
_CARPETAS = {"residuos": _RAIZ / "residuos", "soluciones": _RAIZ / "soluciones" / "crudo"}
# DATASET_DATA permite probar en una carpeta temporal.
DATA = Path(os.environ.get("DATASET_DATA") or _CARPETAS[NOMBRE])
DATA.mkdir(parents=True, exist_ok=True)

ETIQUETA = {"residuos": "residuos", "soluciones": "tecnología"}[NOMBRE]
DESDE_ANIO = 2024 if NOMBRE == "soluciones" else None
