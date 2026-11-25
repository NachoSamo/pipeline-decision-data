"""Alcance geográfico de cada nota según el origen del medio que la publica.

Decisión del 25/11/2026: el alcance no lo elige el LLM ni la persona que
etiqueta; sale de la fuente. Medio cordobés → Córdoba; resto de Argentina →
nacional; resto de América Latina → regional; el resto → internacional.

    python scripts/diccionarios/alcance_fuentes.py   # verifica que cubra todas las fuentes
"""

CORDOBA = "CORDOBA_LOCAL"
ARGENTINA = "ARGENTINA_NACIONAL"
LATAM = "LATAM_REGIONAL"
INTERNACIONAL = "INTERNACIONAL_GLOBAL"

ALCANCE_POR_FUENTE = {
    # Córdoba
    "El Doce": CORDOBA,
    "CBA24N": CORDOBA,
    # Argentina
    "TN": ARGENTINA,
    "Clarín": ARGENTINA,
    "La Nación": ARGENTINA,
    "Infobae": ARGENTINA,
    "Visión Sustentable": ARGENTINA,
    "Ecomundo": ARGENTINA,
    "ECOBIZ": ARGENTINA,
    # América Latina
    "CicloVivo": LATAM,       # Brasil
    "Abrema": LATAM,          # Brasil
    "Mongabay": LATAM,        # Mongabay Latam (es.mongabay.com)
    # Resto del mundo
    "Grist": INTERNACIONAL,                  # Estados Unidos
    "Ecoticias": INTERNACIONAL,              # España
    "Residuos Profesional": INTERNACIONAL,   # España
    "Mongabay en inglés": INTERNACIONAL,
    "Resource Recycling": INTERNACIONAL,     # Estados Unidos
    "BioCycle": INTERNACIONAL,               # Estados Unidos
    "Circular Online": INTERNACIONAL,        # Reino Unido
    "Envirotec": INTERNACIONAL,              # Reino Unido
    "Eco dalle Città": INTERNACIONAL,        # Italia
    "Recover Web": INTERNACIONAL,            # Italia
    "320°": INTERNACIONAL,                   # Alemania
    "Portal Komunalny": INTERNACIONAL,       # Polonia
    "Recycling International": INTERNACIONAL,  # Países Bajos
    "Recycling Portal": INTERNACIONAL,       # Europa
    "Zero Waste Europe": INTERNACIONAL,
    "Inside Waste": INTERNACIONAL,           # Australia
    "Infrastructure News": INTERNACIONAL,    # Sudáfrica
    "Bioplastics News": INTERNACIONAL,       # origen sin confirmar
    "GAIA": INTERNACIONAL,                   # red global
    "ISWA": INTERNACIONAL,                   # asociación global
    "Global Rec": INTERNACIONAL,             # red global de recicladores
}


def alcance(fuente):
    """Alcance de una fuente. Falla si la fuente no está en el diccionario."""
    return ALCANCE_POR_FUENTE[fuente]


if __name__ == "__main__":
    from pathlib import Path

    import pandas as pd

    data = Path(__file__).resolve().parents[2] / "data"
    for track in ("movilidad", "residuos"):
        fuentes = set(pd.read_parquet(data / f"{track}.parquet", columns=["fuente"])["fuente"])
        faltan = fuentes - ALCANCE_POR_FUENTE.keys()
        assert not faltan, f"{track}: fuentes sin alcance: {sorted(faltan)}"
    assert alcance("El Doce") == CORDOBA and alcance("Grist") == INTERNACIONAL
    print("alcance_fuentes OK")
