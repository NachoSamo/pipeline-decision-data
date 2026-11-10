"""Módulo de Transformación y Consolidación de Resultados.

Aplana registros analizados, calcula el score ponderado (Fuente x Fecha)
y los almacena organizadamente en data/resultados/{tema}/{tema}_clasificado.parquet.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd


PESOS_FUENTE = {
    # Medios locales de Córdoba
    "El Doce": 1.3,
    "CBA24N": 1.3,
    "La Voz": 1.3,
    # Medios especializados y técnicos
    "Circular Online": 1.2,
    "Resource Recycling": 1.2,
    "Visión Sustentable": 1.2,
    "ECOBIZ": 1.2,
    "Mongabay": 1.2,
    "Mongabay en inglés": 1.2,
    "Grist": 1.2,
    "Residuos Profesional": 1.2,
    "Recycling International": 1.2,
    "320°": 1.2,
    # Medios nacionales generalistas
    "Clarín": 1.0,
    "La Nación": 1.0,
    "Infobae": 1.0,
    "TN": 0.95,
}

PESO_DEFAULT = 1.0


def calcular_factor_recencia(fecha_str: Optional[str]) -> float:
    """Calcula la frescura temporal (2026: 1.0, 2025: 0.9, 2024: 0.8, anterior: 0.7)."""
    if not fecha_str or len(fecha_str) < 4:
        return 0.7
    try:
        anio = int(fecha_str[:4])
        if anio >= 2026:
            return 1.0
        elif anio == 2025:
            return 0.9
        elif anio == 2024:
            return 0.8
        else:
            return 0.7
    except ValueError:
        return 0.7


def calcular_score_ponderado(fuente: str, fecha_str: Optional[str]) -> float:
    peso_fuente = PESOS_FUENTE.get(fuente, PESO_DEFAULT)
    factor_recencia = calcular_factor_recencia(fecha_str)
    return round(peso_fuente * factor_recencia, 3)


def transformar_registro_a_fila(registro: Dict[str, Any], tema: str = "residuos") -> Dict[str, Any]:
    """Convierte un registro analizado anidado en una fila tabular plana."""
    datos = registro.get("datos_estructurados", {})
    prob = datos.get("problematica") or {}
    sol = datos.get("solucion") or {}
    meta = datos.get("metadatos") or {}

    fuente = meta.get("fuente_medio") or registro.get("fuente_original") or "Desconocida"
    fecha = meta.get("fecha_publicacion") or registro.get("fecha_original")
    score = calcular_score_ponderado(fuente, fecha)

    causas = prob.get("causas_raiz") or []
    if isinstance(causas, list):
        causas_str = "; ".join(str(x) for x in causas if x)
    elif isinstance(causas, dict):
        causas_str = "; ".join(f"{k}: {v}" for k, v in causas.items())
    else:
        causas_str = str(causas)

    afectados = prob.get("afectados_o_actores") or []
    if isinstance(afectados, list):
        afectados_str = "; ".join(str(x) for x in afectados if x)
    elif isinstance(afectados, dict):
        afectados_str = "; ".join(f"{k}: {v}" for k, v in afectados.items())
    else:
        afectados_str = str(afectados)

    def a_str(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            import json
            return json.dumps(val, ensure_ascii=False)
        s = str(val).strip()
        return s if s else None

    return {
        "id_original": a_str(registro.get("id_original")),
        "tema": tema,
        "url": a_str(registro.get("url")),
        "fuente": fuente,
        "fecha": a_str(fecha),
        "score_ponderado": score,
        # Problemática
        "es_problema": bool(prob),
        "tipo_problema": a_str(prob.get("tipo_problema")),
        "titulo_problema": a_str(prob.get("titulo_sintetico")),
        "descripcion_problema": a_str(prob.get("descripcion")),
        "causas_raiz": causas_str,
        "afectados": afectados_str,
        "magnitud": a_str(prob.get("magnitud_o_cifras")),
        # Solución
        "es_solucion": bool(sol),
        "tipo_solucion": a_str(sol.get("tipo_solucion")),
        "nombre_solucion": a_str(sol.get("nombre_solucion_o_tecnologia")),
        "quien_impulsa": a_str(sol.get("quien_la_impulsa")),
        "descripcion_solucion": a_str(sol.get("descripcion")),
        "tipo_problema_objetivo": a_str(sol.get("tipo_problema_objetivo")),
        "detalle_problema_objetivo": a_str(sol.get("detalle_problema_objetivo")),
        "estado_madurez": a_str(sol.get("estado_madurez")),
        "evidencia": a_str(sol.get("evidencia_o_resultados")),
        # Metadatos
        "subcategoria": a_str(meta.get("subcategoria")),
        "alcance_geo": a_str(meta.get("alcance_geografico")),
        "ubicacion": a_str(meta.get("ubicacion_especifica")),
        # Embeddings
        "texto_embedding_problema": registro.get("texto_embedding_problema"),
        "texto_embedding_solucion": registro.get("texto_embedding_solucion"),
    }


def consolidar_resultados(
    registros_analizados: List[Dict[str, Any]],
    tema: str = "residuos",
    directorio_base: Optional[Path] = None
) -> Path:
    """Guarda los registros analizados en data/resultados/{tema}/{tema}_clasificado.parquet."""
    if directorio_base is None:
        raiz = Path(__file__).resolve().parent.parent.parent
        directorio_base = raiz / "data" / "resultados" / tema
    
    directorio_base.mkdir(parents=True, exist_ok=True)
    ruta_salida = directorio_base / f"{tema}_clasificado.parquet"

    filas = [
        transformar_registro_a_fila(r, tema=tema)
        for r in registros_analizados
        if r and "datos_estructurados" in r
    ]
    df = pd.DataFrame(filas)
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].apply(lambda x: None if x is None else str(x))
    df.to_parquet(ruta_salida, index=False)
    print(f"Resultados guardados exitosamente en:\n{ruta_salida} ({len(df)} registros)")
    return ruta_salida
