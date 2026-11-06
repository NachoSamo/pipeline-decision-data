"""Diccionario de problemáticas de biodiversidad. Borrador sin revisar con el equipo.

Se busca con el tema. Las señales de problema y de opinión están en keywords_senales.py.
Lo usan scrape_problematicas.py y scrape_diarios_problematicas.py.
"""

# --- Biodiversidad: scraping de problemáticas (borrador del 5/11/2026, falta revisar) ---
# Se busca con el tema.

BUSQUEDAS_BIODIVERSIDAD = [
    "biodiversidad",
    "especies amenazadas",
    "especies en peligro",
    "extinción",
    "fauna silvestre",
    "flora nativa",
    "bosque nativo",
    "monte nativo",
    "desmonte",
    "deforestación",
    "ley de bosques",
    "humedales",
    "ley de humedales",
    "incendios forestales",
    "áreas protegidas",
    "reserva natural",
    "parque nacional",
    "especies invasoras",
    "tráfico de fauna",
    "caza furtiva",
    "polinizadores",
    "pérdida de hábitat",
    "Chaco seco",
    "Sierras de Córdoba",
    "Ansenuza",
    "Mar Chiquita",
]

BUSQUEDAS_INGLES_BIODIVERSIDAD = [
    "biodiversity",
    "endangered species",
    "extinction",
    "wildlife",
    "deforestation",
    "native forest",
    "wetlands",
    "wildfires",
    "protected areas",
    "invasive species",
    "wildlife trafficking",
    "poaching",
    "pollinators",
    "habitat loss",
]

BUSQUEDAS_PORTUGUES_BIODIVERSIDAD = [
    "biodiversidade",
    "espécies ameaçadas",
    "extinção",
    "fauna silvestre",
    "desmatamento",
    "floresta nativa",
    "áreas úmidas",
    "queimadas",
    "áreas protegidas",
    "espécies invasoras",
    "tráfico de animais",
    "polinizadores",
    "perda de habitat",
]

# Etiquetas probadas el 5/11/2026: todas devolvieron notas.
TAGS_INFOBAE_BIODIVERSIDAD = [
    "biodiversidad", "deforestacion", "incendios-forestales", "humedales", "especies-en-peligro-de-extincion",
    "animales-en-peligro-de-extincion", "fauna", "flora-y-fauna", "bosques", "bosques-nativos",
    "parques-nacionales", "desmonte", "ley-de-humedales", "ley-de-bosques", "extincion", "trafico-de-animales",
    "conservacion", "areas-protegidas", "fauna-silvestre", "especies-invasoras", "yaguarete",
]

# Muy amplias (animales tiene 9.265 notas, muchas de mascotas): solo con el tema en título o bajada.
TAGS_INFOBAE_AMPLIOS_BIODIVERSIDAD = ["naturaleza", "cambio-climatico", "animales"]

TAGS_CLARIN_BIODIVERSIDAD = [
    "biodiversidad", "deforestacion", "incendios-forestales", "humedales", "especies-en-peligro-de-extincion",
    "animales-en-peligro-de-extincion", "flora-y-fauna", "bosques", "bosques-nativos", "parques-nacionales",
    "desmonte", "ley-de-bosques", "extincion", "trafico-de-animales", "conservacion", "fauna-silvestre",
    "yaguarete",
]

TAGS_CLARIN_AMPLIOS_BIODIVERSIDAD = ["naturaleza", "cambio-climatico", "animales"]

# Raíces sin tildes. Filtran las URLs de los sitemaps (La Nación, CBA24N) y cuentan menciones.
RAICES_BIODIVERSIDAD = [
    "biodiversidad", "humedal", "desmonte", "deforest", "bosque", "fauna", "flora", "extincion",
    "incendio forestal", "incendios forestales", "especie", "yaguarete", "parque nacional", "parques nacionales",
    "reserva natural", "areas protegidas", "area protegida", "ansenuza", "mar chiquita", "trafico de animales",
    "trafico de fauna", "caza furtiva", "polinizador", "monte nativo", "chaco seco", "habitat",
]
