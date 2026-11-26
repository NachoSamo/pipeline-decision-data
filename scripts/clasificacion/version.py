"""Versión vigente de la clasificación. Única fuente para las rutas de resultados.

Cada versión escribe en data/resultados/<VERSION>-<tema>/, así una versión nueva
no pisa la anterior. Para la v2: cambiar VERSION a "v2" y, en el Kaggle
(kaggle_pipeline.py y pipeline_clasificacion_kaggle.ipynb), la misma constante.
Versiones anteriores: v1 (data/resultados/v1-residuos/, docs/v1-residuos/).
"""

from pathlib import Path

VERSION = "v1"
RAIZ = Path(__file__).resolve().parent.parent.parent


def carpeta_resultados(tema: str = "residuos") -> Path:
    return RAIZ / "data" / "resultados" / f"{VERSION}-{tema}"
