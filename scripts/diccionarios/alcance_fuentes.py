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
    "Infocampo": ARGENTINA,
    "TodoAgro": ARGENTINA,
    # América Latina
    "CicloVivo": LATAM,       # Brasil
    "Abrema": LATAM,          # Brasil
    "Mongabay": LATAM,        # Mongabay Latam (es.mongabay.com)
    "Mobilidade Sampa": LATAM,     # Brasil
    "O Eco": LATAM,                # Brasil
    "InfoAmazonia": LATAM,         # Brasil
    "AgFeed": LATAM,               # Brasil
    "Actualidad Ambiental": LATAM,  # Perú
    "Climate Tracker": LATAM,      # Climate Tracker América Latina
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
    "Ambientum": INTERNACIONAL,              # España
    "Movilidad Eléctrica": INTERNACIONAL,    # origen sin confirmar
    "Ecoportal": INTERNACIONAL,              # origen sin confirmar
    "Green Savers": INTERNACIONAL,           # Portugal
    "Rinnovabili": INTERNACIONAL,            # Italia
    "HDmotori": INTERNACIONAL,               # Italia
    "EconomyUp": INTERNACIONAL,              # Italia
    "MamStartup": INTERNACIONAL,             # Polonia
    "Agrofakt": INTERNACIONAL,               # Polonia
    "Naturschutz.ch": INTERNACIONAL,         # Suiza
    "Carbon Brief": INTERNACIONAL,           # Reino Unido
    "Bus and Coach Buyer": INTERNACIONAL,    # Reino Unido
    "African Leadership Magazine": INTERNACIONAL,  # África, editada en Reino Unido
    "Africa Sustainability Matters": INTERNACIONAL,  # África
    "Inside Climate News": INTERNACIONAL,    # Estados Unidos
    "AgFunderNews": INTERNACIONAL,           # Estados Unidos
    "The Driven": INTERNACIONAL,             # Australia
    "Mongabay India": INTERNACIONAL,         # India
    "Dialogue Earth": INTERNACIONAL,         # Sur global
    "IPS Noticias": INTERNACIONAL,           # agencia del Sur global
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
    # Soluciones: solo las del track de movilidad, que se clasifican en la v2.
    sol = pd.read_parquet(data / "soluciones.parquet", columns=["fuente", "tracks"])
    fuentes = set(sol.loc[sol["tracks"].map(lambda t: "movilidad" in list(t)), "fuente"])
    faltan = fuentes - ALCANCE_POR_FUENTE.keys()
    assert not faltan, f"soluciones de movilidad: fuentes sin alcance: {sorted(faltan)}"
    assert alcance("El Doce") == CORDOBA and alcance("Grist") == INTERNACIONAL
    print("alcance_fuentes OK")
