"""Diccionario de problemáticas de movilidad sustentable. Borrador sin revisar con el equipo.

Se busca con el tema. Las señales de problema y de opinión están en keywords_senales.py.
Lo usan scrape_problematicas.py y scrape_diarios_problematicas.py.
"""

# --- Movilidad sustentable: scraping de problemáticas (borrador del 6/11/2026, falta revisar) ---
# Las señales de problema y de opinión están en keywords_senales.py.

BUSQUEDAS_MOVILIDAD = [
    "movilidad sustentable",
    "movilidad sostenible",
    "movilidad urbana",
    "transporte público",
    "transporte urbano",
    "transporte interurbano",
    "colectivos",
    "paro de colectivos",
    "frecuencia de colectivos",
    "boleto",
    "ciclovías",
    "bicisendas",
    "bicicletas",
    "peatones",
    "veredas",
    "accesibilidad",
    "siniestros viales",
    "seguridad vial",
    "accidentes de tránsito",
    "congestión",
    "tránsito",
    "vehículos eléctricos",
    "autos eléctricos",
    "electromovilidad",
    "emisiones del transporte",
    "calidad del aire",
    "trenes",
    "tren metropolitano",
    "trolebuses",
    "SiBus",
    "TAMSE",
    "Coniferal",
    "Circunvalación",
]

BUSQUEDAS_INGLES_MOVILIDAD = [
    "sustainable mobility",
    "urban mobility",
    "public transport",
    "public transit",
    "bus service",
    "bike lanes",
    "cycling infrastructure",
    "pedestrian safety",
    "road safety",
    "traffic deaths",
    "traffic congestion",
    "electric vehicles",
    "e-mobility",
    "micromobility",
    "transport emissions",
    "rail transit",
]

BUSQUEDAS_PORTUGUES_MOVILIDAD = [
    "mobilidade urbana",
    "mobilidade sustentável",
    "transporte público",
    "ônibus",
    "ciclovias",
    "bicicleta",
    "pedestres",
    "segurança viária",
    "trânsito",
    "congestionamento",
    "veículos elétricos",
    "carros elétricos",
    "micromobilidade",
    "emissões do transporte",
]

# Raíces sin tildes para URLs de sitemaps y menciones. Se evita "tren" solo porque coincide con "entrenador".
RAICES_MOVILIDAD = [
    "movilidad", "transporte", "colectivo", "omnibus", "ciclovia", "bicisenda", "bicicleta", "peaton",
    "transito", "siniestro vial", "siniestros viales", "seguridad vial", "accidente de transito",
    "accidentes de transito", "congestion", "electromovilidad", "auto electrico", "autos electricos",
    "vehiculo electrico", "vehiculos electricos", "trenes", "ferrocarril", "tren metropolitano", "trolebus",
    "subte", "boleto", "sibus", "tamse", "coniferal", "circunvalacion", "calidad del aire",
]

# Etiquetas de Infobae probadas el 6/11/2026: todas devolvieron notas.
TAGS_INFOBAE_MOVILIDAD = [
    "transporte-publico", "colectivos", "movilidad-sustentable", "movilidad-urbana", "autos-electricos",
    "vehiculos-electricos", "electromovilidad", "bicicletas", "ciclovias", "bicisendas", "transito",
    "accidentes-de-transito", "seguridad-vial", "siniestros-viales", "trenes", "subte",
    "contaminacion-del-aire", "paro-de-colectivos", "boleto", "uta", "peatones",
]

# Muy amplias: "calidad-del-aire" devolvió 10.000 (el máximo de la API) y "autos" trae reseñas de modelos.
TAGS_INFOBAE_AMPLIOS_MOVILIDAD = ["movilidad", "transporte", "autos", "calidad-del-aire"]

# Etiquetas de Clarín probadas el 6/11/2026. Sin las que devolvieron 404 (vehiculos-electricos,
# electromovilidad, tarifas-de-colectivos, peatones) ni las que traen una sola nota (movilidad, transporte).
TAGS_CLARIN_MOVILIDAD = [
    "transporte-publico", "colectivos", "movilidad-sustentable", "movilidad-urbana", "autos-electricos",
    "bicicletas", "ciclovias", "bicisendas", "transito", "accidentes-de-transito", "seguridad-vial",
    "siniestros-viales", "trenes", "subte", "contaminacion-del-aire", "calidad-del-aire",
    "paro-de-colectivos", "boleto", "uta",
]

TAGS_CLARIN_AMPLIOS_MOVILIDAD = ["autos"]

# Movilidad compartida y bicis públicas, sumadas el 6/11/2026 a pedido de Gina.
BUSQUEDAS_MOVILIDAD += [
    "Ecobici",
    "bicicletas públicas",
    "bici pública",
    "bicicletas compartidas",
    "Mi Bici Tu Bici",
    "monopatines eléctricos",
    "monopatines",
    "micromovilidad",
    "movilidad compartida",
    "autos compartidos",
    "carpooling",
]
BUSQUEDAS_INGLES_MOVILIDAD += ["bike share", "bike sharing", "e-scooters", "shared mobility", "car sharing"]
BUSQUEDAS_PORTUGUES_MOVILIDAD += ["bicicletas compartilhadas", "patinetes elétricos", "mobilidade compartilhada"]
RAICES_MOVILIDAD += [
    "ecobici", "bici publica", "bicicletas publicas", "bicicletas compartidas", "mi bici tu bici", "monopatin",
    "micromovilidad", "movilidad compartida", "autos compartidos", "carpooling",
]
# Etiquetas probadas el 6/11/2026.
TAGS_INFOBAE_MOVILIDAD += [
    "ecobici", "bicicletas-publicas", "bicicletas-compartidas", "monopatines-electricos", "monopatines",
    "micromovilidad", "movilidad-compartida", "autos-compartidos",
]
TAGS_CLARIN_MOVILIDAD += ["ecobici", "bicicletas-publicas", "carpooling"]
