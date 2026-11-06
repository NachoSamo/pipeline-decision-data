"""Diccionario del dataset de soluciones tecnológicas. Borrador sin aprobar."""

IDIOMAS = ["es", "en", "pt", "it", "de", "pl"]
TRACKS = ["residuos", "agro", "movilidad", "biodiversidad"]

TERMINOS_AMPLIOS = {
    "es": ["startup", "solución tecnológica", "innovación tecnológica", "inteligencia artificial", "plataforma digital", "aplicación móvil", "sensores", "drones", "biotecnología", "robótica", "emprendimiento tecnológico", "desarrollaron tecnología"],
    "en": ["startup", "technology solution", "technological innovation", "artificial intelligence", "digital platform", "mobile app", "sensors", "drones", "biotechnology", "robotics", "cleantech", "climate tech"],
    "pt": ["startup", "solução tecnológica", "inovação tecnológica", "inteligência artificial", "plataforma digital", "aplicativo", "sensores", "drones", "biotecnologia", "robótica", "empreendedorismo tecnológico", "desenvolveram tecnologia"],
    "it": ["startup", "soluzione tecnologica", "innovazione tecnologica", "intelligenza artificiale", "piattaforma digitale", "app mobile", "sensori", "droni", "biotecnologie", "robotica", "cleantech", "tecnologia sviluppata"],
    "de": ["Startup", "technologische Lösung", "technologische Innovation", "künstliche Intelligenz", "digitale Plattform", "mobile App", "Sensoren", "Drohnen", "Biotechnologie", "Robotik", "Cleantech", "neue Technologie"],
    "pl": ["startup", "rozwiązanie technologiczne", "innowacja technologiczna", "sztuczna inteligencja", "platforma cyfrowa", "aplikacja mobilna", "czujniki", "drony", "biotechnologia", "robotyka", "cleantech", "nowa technologia"],
}

PALABRAS_TECNOLOGIA = {
    "es": ["tecnología", "startup", "innovación"],
    "en": ["technology", "startup", "innovation"],
    "pt": ["tecnologia", "startup", "inovação"],
    "it": ["tecnologia", "startup", "innovazione"],
    "de": ["Technologie", "Startup", "Innovation"],
    "pl": ["technologia", "startup", "innowacja"],
}

PALABRAS_TRACK = {
    "es": {"residuos": ["reciclaje", "residuos", "basura"], "agro": ["agricultura", "cultivos", "ganadería"], "movilidad": ["movilidad", "transporte", "vehículos eléctricos"], "biodiversidad": ["biodiversidad", "conservación", "reforestación"]},
    "en": {"residuos": ["recycling", "waste", "landfill"], "agro": ["agriculture", "crops", "livestock"], "movilidad": ["mobility", "transport", "electric vehicles"], "biodiversidad": ["biodiversity", "conservation", "reforestation"]},
    "pt": {"residuos": ["reciclagem", "resíduos", "lixo"], "agro": ["agricultura", "lavoura", "pecuária"], "movilidad": ["mobilidade", "transporte", "veículos elétricos"], "biodiversidad": ["biodiversidade", "conservação", "reflorestamento"]},
    "it": {"residuos": ["riciclo", "rifiuti", "discarica"], "agro": ["agricoltura", "colture", "allevamento"], "movilidad": ["mobilità", "trasporti", "veicoli elettrici"], "biodiversidad": ["biodiversità", "conservazione", "riforestazione"]},
    "de": {"residuos": ["Recycling", "Abfall", "Deponie"], "agro": ["Landwirtschaft", "Anbau", "Viehzucht"], "movilidad": ["Mobilität", "Verkehr", "Elektrofahrzeuge"], "biodiversidad": ["Biodiversität", "Naturschutz", "Aufforstung"]},
    "pl": {"residuos": ["recykling", "odpady", "składowisko"], "agro": ["rolnictwo", "uprawy", "hodowla"], "movilidad": ["mobilność", "transport", "pojazdy elektryczne"], "biodiversidad": ["bioróżnorodność", "ochrona przyrody", "zalesianie"]},
}


def cruces(idioma):
    return [f"{t} {p}" for t in PALABRAS_TECNOLOGIA[idioma] for ps in PALABRAS_TRACK[idioma].values() for p in ps]


BUSQUEDAS_POR_IDIOMA = {i: TERMINOS_AMPLIOS[i] + cruces(i) for i in IDIOMAS}

RAICES_POR_IDIOMA = {
    "es": ["tecnolog", "startup", "inteligencia artificial", "innovac", "plataforma", "software", "sensor", "dron", "biotecn", "robot", "aplicacion", "digital", "algoritm", "cleantech", "agtech"],
    "en": ["technolog", "startup", "artificial intelligence", "innovat", "platform", "software", "sensor", "drone", "biotech", "robot", "digital", "algorithm", "cleantech", "climate tech", "agtech"],
    "pt": ["tecnolog", "startup", "inteligencia artificial", "inovac", "plataforma", "software", "sensor", "drone", "biotecn", "robot", "aplicativo", "digital", "algoritm", "cleantech", "agtech"],
    "it": ["tecnolog", "startup", "intelligenza artificiale", "innovazion", "piattaforma", "software", "sensor", "droni", "biotecn", "robot", "digitale", "algoritm", "cleantech", "agritech"],
    "de": ["technolog", "startup", "kunstliche intelligenz", "innovation", "plattform", "software", "sensor", "drohne", "biotech", "robot", "digital", "algorithm", "cleantech", "agrartech"],
    "pl": ["technolog", "startup", "sztuczna inteligencja", "innowac", "platform", "oprogramowan", "czujnik", "dron", "biotechnolog", "robot", "cyfrow", "algorytm", "cleantech"],
}

# Inicios de palabra, sin tildes. Se usan con \b en separar_por_track.py para que
# "agro" no encuentre "milagro". La ł del polaco no se descompone al normalizar.
RAICES_TRACK = {
    "residuos": ["residu", "basur", "recicl", "desech", "relleno sanitario", "compost", "economia circular", "waste", "recycl", "landfill", "garbage", "trash", "circular economy", "lixo", "aterro sanitario", "rifiut", "discaric", "abfall", "deponie", "kreislaufwirtschaft", "odpad", "recykl", "smieci", "składowisk"],
    "agro": ["agro", "agricol", "agricultur", "cultivo", "ganader", "cosecha", "semilla", "agtech", "crop", "farm", "livestock", "harvest", "lavoura", "pecuar", "colture", "allevament", "agritech", "landwirtschaft", "viehzucht", "rolnict", "uprawa", "uprawy", "hodowl"],
    "movilidad": ["movilidad", "transporte", "vehiculos electricos", "vehiculo electrico", "autos electricos", "colectivo", "micromovilidad", "mobility", "public transport", "electric vehicle", "mobilidade", "veiculos eletricos", "mobilita", "trasporti", "veicoli elettrici", "mobilitat", "verkehr", "elektrofahrzeug", "elektroauto", "mobilnosc", "pojazdy elektryczne", "komunikacj"],
    "biodiversidad": ["biodivers", "conservacion", "reforest", "deforest", "fauna", "especies", "humedal", "conservation", "wildlife", "species", "wetland", "reflorest", "conservacao", "riforest", "conservazione", "naturschutz", "aufforst", "artenschutz", "bioroznorodn", "ochrona przyrody", "zalesian"],
}

RAICES_TODOS_LOS_TRACKS = sorted({r for raices in RAICES_TRACK.values() for r in raices})

TAGS_INFOBAE_PRINCIPALES = []
TAGS_INFOBAE_AMPLIOS = ["tecnologia", "inteligencia-artificial", "startups", "innovacion"]
TAGS_CLARIN_PRINCIPALES = []
TAGS_CLARIN_AMPLIOS = ["tecnologia", "inteligencia-artificial", "startups", "innovacion"]


if __name__ == "__main__":
    assert all(len(BUSQUEDAS_POR_IDIOMA[i]) == 12 + 36 for i in IDIOMAS)
    assert cruces("es")[0] == "tecnología reciclaje"
    print("selfcheck ok")
