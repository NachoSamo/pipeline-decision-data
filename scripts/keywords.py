"""Diccionario de palabras clave por track."""

BUSQUEDAS_RESIDUOS = [
    "residuos",
    "basura",
    "basural",
    "basurales",
    "reciclaje",
    "reciclado",
    "recicladores",
    "cartoneros",
    "Cormecor",
    "Piedras Blancas",
    "punto verde",
    "puntos verdes",
    "desechos",
    "enterramiento",
    "plásticos",
    "contaminación",
    "economía circular",
    "recolección diferenciada",
    "gestión de RSU",
    "valorización de residuos",
    "cooperativa de reciclaje",
    "reciclaje industrial",
    "RAEE",
    "residuos electrónicos",
    "compostaje urbano",
    "compostaje industrial",
    "ley de envases",
    "biodigestor",
    "trazabilidad de residuos",
]

# Sin los términos que en El Doce trajeron más ruido, como "desechos" o "RAEE".
BUSQUEDAS_PRECISAS_RESIDUOS = [
    "residuos",
    "basura",
    "basural",
    "basurales",
    "reciclaje",
    "reciclado",
    "recicladores",
    "cartoneros",
    "relleno sanitario",
    "punto verde",
    "puntos verdes",
    "compostaje",
    "economía circular",
    "recolección diferenciada",
    "cooperativa de reciclaje",
    "ley de envases",
    "residuos electrónicos",
    "residuos sustentables",
]

# "waste" solo queda afuera porque también significa "desperdiciar".
BUSQUEDAS_INGLES_RESIDUOS = [
    "waste management",
    "solid waste",
    "municipal waste",
    "plastic waste",
    "food waste",
    "electronic waste",
    "e-waste",
    "hazardous waste",
    "waste pickers",
    "recycling",
    "landfill",
    "open dump",
    "circular economy",
    "composting",
    "extended producer responsibility",
]

RAICES_INGLES_RESIDUOS = [
    "waste",
    "recycl",
    "landfill",
    "garbage",
    "trash",
    "compost",
    "circular economy",
    "open dump",
    "extended producer responsibility",
]

TAGS_INFOBAE_RESIDUOS = [
    "reciclaje",
    "basura",
    "residuos",
    "economia-circular",
    "plasticos",
    "desechos",
    "basural",
    "cartoneros",
    "puntos-verdes",
]

TAGS_INFOBAE_AMPLIOS = [
    "sustentabilidad",
    "ambiente",
    "contaminacion",
    "medio-ambiente",
]

TAGS_CLARIN_RESIDUOS = [
    "reciclaje",
    "basura",
    "ceamse",
    "residuos",
    "plasticos",
    "desechos",
    "basurales",
    "puntos-verdes",
    "basural",
    "cartoneros",
]

TAGS_CLARIN_AMPLIOS = [
    "ambiente",
    "sustentabilidad",
    "contaminacion",
    "medio-ambiente",
]

# Raíces sin tildes para filtrar URLs de sitemaps y priorizar notas.
RAICES_RESIDUOS = [
    "residu",
    "basur",
    "recicl",
    "desech",
    "cartoner",
    "compost",
    "relleno sanitario",
    "economia circular",
    "punto verde",
    "puntos verdes",
    "cormecor",
    "ceamse",
    "piedras blancas",
    "envases",
    "plastico",
    "biodigestor",
    "raee",
]

CORE_KEYWORDS_RESIDUOS = [
    r"\beconom[íi]a circular\b",
    r"\brecolecci[óo]n diferenciada\b",
    r"\bgesti[óo]n de rsu\b",
    r"\bvalorizaci[óo]n de residuos\b",
    r"\bcooperativa de reciclaje\b",
    r"\bpunto[s]? verde[s]?\b",
    r"\breciclaje industrial\b",
    r"\braee\b|\bresiduos electr[óo]nicos\b",
    r"\bcompostaje (urbano|industrial)\b",
    r"\bley de envases\b",
    r"\bbiodigestor\b",
    r"\btrazabilidad de residuos\b",
]
