"""Módulo Modular de Pre-limpieza y Filtrado Heurístico.

Corrige problemas de evaluación booleana de arrays de NumPy y optimiza
el procesamiento de grandes volúmenes con to_dict('records').
"""

import html
import re
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd


SECCIONES_DESCARTADAS = {
    "deportes", "futbol", "fútbol", "primera c", "primera división", "copa de la liga",
    "espectaculos", "espectáculos", "cuarteteando", "fama", "show", "musica", "música",
    "cine y series", "horoscopo", "horóscopo", "policiales"
}

RAICES_POR_TEMA = {
    "residuos": [
        "basur", "residu", "recicl", "verted", "lixiviad", "compost", "chatarra", "plástic", "plastic",
        "desecho", "relleno sanitar", "ecodiseñ", "ecodiseno", "economía circular", "economia circular",
        "recolecc", "cartoner", "desperdicio aliment", "durmiente", "envase", "acopl", "botell", "tarifa"
    ],
    "biodiversidad": [
        "fauna", "flora", "especie", "bosque", "deforestac", "humedal", "extinción", "extincion",
        "reserva natural", "caza furtiva", "invasora", "hábitat", "habitat", "biodiversid", "selva",
        "parque nacional", "yaguaret", "avifauna", "anfibio", "arrecife"
    ],
    "movilidad": [
        "tránsito", "transito", "transporte", "colectivo", "tren", "bicisenda", "ciclovía", "ciclovia",
        "movilidad eléctric", "movilidad electric", "subte", "congestión", "congestion", "peatonal",
        "electromovilidad", "flota", "autobús", "autobus", "estación"
    ],
    "soluciones": [
        "planta", "inaugur", "proyecto", "tecnolog", "startup", "inversión", "inversion", "biodigest",
        "prototipo", "alianza", "innovac", "patente", "desarrollo", "financiam", "solución", "solucion"
    ]
}

PALABRAS_CLAVE_DEPORTE = re.compile(
    r"\b(goles?|partidos?|dt|director técnico|primer tiempo|segundo tiempo|tiro al arco|penales?)\b",
    re.IGNORECASE
)

SHORTCODES_CMS = re.compile(r"\[/?et_pb_[^\]]*\]|\[/?caption[^\]]*\]|<[^>]+>", re.DOTALL)


def limpiar_texto(texto: Optional[str]) -> str:
    """Elimina etiquetas HTML, shortcodes de constructores web y espacios redundantes."""
    if not texto or not isinstance(texto, str):
        return ""
    texto_sin_html = SHORTCODES_CMS.sub(" ", texto)
    texto_decodificado = html.unescape(texto_sin_html)
    return " ".join(texto_decodificado.split()).strip()


def extraer_lista_tags_segura(tags_raw: Any) -> List[str]:
    """Extrae tags de forma segura sin disparar ambigüedad booleana en arrays de NumPy."""
    if tags_raw is None:
        return []
    if isinstance(tags_raw, float) and pd.isna(tags_raw):
        return []
    if hasattr(tags_raw, "__iter__") and not isinstance(tags_raw, (str, bytes)):
        return [str(t).strip().lower() for t in tags_raw if pd.notna(t) and t]
    if isinstance(tags_raw, str):
        return [tags_raw.strip().lower()]
    return []


def evaluar_descarte_heuristico(fila: Dict[str, Any], long_minima_cuerpo: int = 150) -> Tuple[bool, str]:
    """Determina si un registro debe descartarse antes del LLM.
    
    Retorna:
        (debe_descartar, motivo)
    """
    seccion_raw = fila.get("seccion")
    seccion = "" if pd.isna(seccion_raw) else str(seccion_raw).strip().lower()
    tags_lower = extraer_lista_tags_segura(fila.get("tags"))

    # 1. Filtro por sección o tag deportivo / farándula
    if seccion in SECCIONES_DESCARTADAS or any(t in SECCIONES_DESCARTADAS for t in tags_lower):
        return True, f"Sección o tag no ambiental: {seccion}"

    titulo = limpiar_texto(str(fila.get("titulo") or ""))
    bajada = limpiar_texto(str(fila.get("bajada") or ""))
    cuerpo = limpiar_texto(str(fila.get("body") or ""))

    # 2. Control de longitud mínima
    if len(cuerpo) < long_minima_cuerpo:
        return True, f"Cuerpo insuficiente ({len(cuerpo)} caracteres)"

    # 3. Detección de eventos deportivos
    encabezado = f"{titulo} {bajada}".lower()
    if PALABRAS_CLAVE_DEPORTE.search(encabezado):
        return True, "Falso positivo por léxico deportivo"

    return False, "Apto para LLM"


def preparar_registro_para_llm(fila: Dict[str, Any], max_chars_cuerpo: Optional[int] = 2500) -> Dict[str, Any]:
    """Sanitiza y prepara un registro individual para el LLM."""
    titulo = limpiar_texto(str(fila.get("titulo") or ""))
    bajada = limpiar_texto(str(fila.get("bajada") or ""))
    cuerpo = limpiar_texto(str(fila.get("body") or ""))

    if max_chars_cuerpo and len(cuerpo) > max_chars_cuerpo:
        cuerpo_procesado = cuerpo[:max_chars_cuerpo] + " ... [continúa]"
    else:
        cuerpo_procesado = cuerpo

    fecha_raw = fila.get("fecha")
    fecha_str = "" if pd.isna(fecha_raw) else str(fecha_raw)[:10]

    return {
        "id": fila.get("id") or fila.get("url"),
        "fuente": str(fila.get("fuente") or "Desconocida"),
        "url": str(fila.get("url") or ""),
        "fecha": fecha_str,
        "seccion": fila.get("seccion"),
        "titulo": titulo,
        "bajada": bajada,
        "cuerpo_limpio": cuerpo_procesado,
        "longitud_cuerpo_original": len(cuerpo),
        "longitud_cuerpo_procesado": len(cuerpo_procesado)
    }


def prefiltrar_dataframe(
    df: pd.DataFrame,
    max_chars_cuerpo: Optional[int] = 2500,
    long_minima_cuerpo: int = 150
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prefiltra de forma ultrarrápida un DataFrame usando to_dict('records').
    
    Retorna:
        (df_aptos, df_descartados)
    """
    aptos = []
    descartados = []

    # Iteración optimizada en memoria
    registros = df.to_dict(orient="records")

    for fila_dict in registros:
        debe_descartar, motivo = evaluar_descarte_heuristico(fila_dict, long_minima_cuerpo=long_minima_cuerpo)
        if debe_descartar:
            fila_dict["motivo_descarte"] = motivo
            descartados.append(fila_dict)
        else:
            registro_listo = preparar_registro_para_llm(fila_dict, max_chars_cuerpo=max_chars_cuerpo)
            aptos.append(registro_listo)

    df_aptos = pd.DataFrame(aptos)
    df_descartados = pd.DataFrame(descartados)
    return df_aptos, df_descartados


def filtrar_candidatos_tema(df: pd.DataFrame, tema: str = "residuos") -> pd.DataFrame:
    """Filtra rápidamente un DataFrame dejando solo notas con indicios reales del tema.
    
    1. Descarta secciones no ambientales (deportes, espectáculos, etc.)
    2. Descarta si el texto del cuerpo es menor a 150 caracteres o léxico deportivo
    3. Verifica presencia de raíces temáticas en título, bajada o primeros 400 caracteres del cuerpo
    """
    raices = RAICES_POR_TEMA.get(tema, RAICES_POR_TEMA.get("residuos", []))
    patron_tema = re.compile(r"\b(" + "|".join(re.escape(r) for r in raices) + ")", re.IGNORECASE) if raices else None

    candidatos = []
    registros = df.to_dict(orient="records")

    for fila in registros:
        debe_descartar, _ = evaluar_descarte_heuristico(fila, long_minima_cuerpo=150)
        if debe_descartar:
            continue

        if patron_tema:
            tit = str(fila.get("titulo") or "")
            baj = str(fila.get("bajada") or "")
            cue = str(fila.get("body") or fila.get("cuerpo_limpio") or fila.get("cuerpo") or "")[:400]
            texto_eval = f"{tit} {baj} {cue}".lower()
            if not patron_tema.search(texto_eval):
                continue

        candidatos.append(fila)

    return pd.DataFrame(candidatos)

