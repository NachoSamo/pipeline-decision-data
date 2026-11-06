"""Descarga 19 fuentes especializadas en residuos con la API de WordPress.

Cada fuente se busca con los términos de su idioma, desde 2024. Sin argumentos
baja todas, una después de otra. Si una falla, sigue con la próxima. Se puede
cortar y retomar volviendo a ejecutar el mismo comando.

Uso:
    python scripts/scrape_especializadas.py --selfcheck
    python scripts/scrape_especializadas.py
    python scripts/scrape_especializadas.py zerowasteeurope globalrec
"""

import argparse

from dataset import NOMBRE
from diccionarios.keywords_residuos import (
    POR_IDIOMA,
    RAICES_ALEMAN_RESIDUOS,
    RAICES_ITALIANO_RESIDUOS,
    RAICES_POLACO_RESIDUOS,
    RAICES_PORTUGUES_RESIDUOS,
)
from progreso import relevante
from scrape_wordpress import descargar

DESDE = "2024-01-01T00:00:00"
PAUSA = 4

# clave: (nombre, sitio, idioma, segundos entre pedidos)
FUENTES = {
    "residuosprofesional": ("Residuos Profesional", "https://www.residuosprofesional.com", "es", PAUSA),
    "ecodallecitta": ("Eco dalle Città", "https://www.ecodallecitta.it", "it", 20),
    "insidewaste": ("Inside Waste", "https://www.insidewaste.com.au", "en", PAUSA),
    "portalkomunalny": ("Portal Komunalny", "https://portalkomunalny.pl", "pl", PAUSA),
    "bioplasticsnews": ("Bioplastics News", "https://bioplasticsnews.com", "en", PAUSA),
    "320grad": ("320°", "https://www.320grad.de", "de", PAUSA),
    "ciclovivo": ("CicloVivo", "https://ciclovivo.com.br", "pt", PAUSA),
    "infrastructurenews": ("Infrastructure News", "https://www.infrastructurenews.co.za", "en", PAUSA),
    "envirotec": ("Envirotec", "https://www.envirotecmagazine.com", "en", PAUSA),
    "abrema": ("Abrema", "https://www.abrema.org.br", "pt", PAUSA),
    "recoverweb": ("Recover Web", "https://www.recoverweb.it", "it", PAUSA),
    "recyclinginternational": ("Recycling International", "https://recyclinginternational.com", "en", PAUSA),
    "biocycle": ("BioCycle", "https://www.biocycle.net", "en", PAUSA),
    "ecoticias": ("Ecoticias", "https://www.ecoticias.com", "es", PAUSA),
    "recyclingportal": ("Recycling Portal", "https://www.recyclingportal.eu", "en", PAUSA),
    "gaia": ("GAIA", "https://www.no-burn.org", "en", PAUSA),
    "iswa": ("ISWA", "https://www.iswa.org", "en", PAUSA),
    "zerowasteeurope": ("Zero Waste Europe", "https://zerowasteeurope.eu", "en", PAUSA),
    "globalrec": ("Global Rec", "https://globalrec.org", "en", PAUSA),
}

# Fuentes aprobadas solo para el dataset de soluciones.
_NUEVAS = {
    "economyup": ("EconomyUp", "https://www.economyup.it", "it", PAUSA),
    "mamstartup": ("MamStartup", "https://mamstartup.pl", "pl", PAUSA),
    "infocampo": ("Infocampo", "https://www.infocampo.com.ar", "es", PAUSA),
    "todoagro": ("TodoAgro", "https://www.todoagro.com.ar", "es", PAUSA),
    "agrotendencia": ("AgroTendencia", "https://www.agrotendencia.tv", "es", PAUSA),
    "agfundernews": ("AgFunderNews", "https://agfundernews.com", "en", PAUSA),
    "agfeed": ("AgFeed", "https://agfeed.com.br", "pt", PAUSA),
    "agrofakt": ("Agrofakt", "https://agrofakt.pl", "pl", PAUSA),
    "mobilidadesampa": ("Mobilidade Sampa", "https://mobilidadesampa.com.br", "pt", PAUSA),
    "movilidadelectrica": ("Movilidad Eléctrica", "https://www.movilidadelectrica.com", "es", PAUSA),
    "thedriven": ("The Driven", "https://thedriven.io", "en", PAUSA),
    "busandcoachbuyer": ("Bus and Coach Buyer", "https://www.busandcoachbuyer.com", "en", PAUSA),
    "hdmotori": ("HDmotori", "https://www.hdmotori.it", "it", PAUSA),
    "carbonbrief": ("Carbon Brief", "https://www.carbonbrief.org", "en", PAUSA),
    "infoamazonia": ("InfoAmazonia", "https://infoamazonia.org", "pt", PAUSA),
    "naturschutz": ("Naturschutz.ch", "https://www.naturschutz.ch", "de", PAUSA),
    "greensavers": ("Green Savers", "https://greensavers.sapo.pt", "pt", PAUSA),
    "rinnovabili": ("Rinnovabili", "https://www.rinnovabili.it", "it", PAUSA),
    "insideclimatenews": ("Inside Climate News", "https://insideclimatenews.org", "en", PAUSA),
    "ecoportal": ("Ecoportal", "https://www.ecoportal.net", "es", PAUSA),
    "ambientum": ("Ambientum", "https://www.ambientum.com", "es", PAUSA),
    "africasustainability": ("Africa Sustainability Matters", "https://africasustainabilitymatters.com", "en", PAUSA),
    "mongabayindia": ("Mongabay India", "https://india.mongabay.com", "en", PAUSA),
    "ipsnoticias": ("IPS Noticias", "https://www.ipsnoticias.net", "es", 4),
    "oeco": ("O Eco", "https://oeco.org.br", "pt", PAUSA),
    "africanleadership": ("African Leadership Magazine", "https://www.africanleadershipmagazine.co.uk", "en", PAUSA),
    "dialogueearth": ("Dialogue Earth", "https://dialogue.earth", "en", PAUSA),
    "actualidadambiental": ("Actualidad Ambiental", "https://www.actualidadambiental.pe", "es", PAUSA),
    "climatetracker": ("Climate Tracker", "https://climatetrackerlatam.org", "es", PAUSA),
}
if NOMBRE == "soluciones":
    FUENTES = {**FUENTES, **_NUEVAS}


def bajar(clave):
    nombre, sitio, idioma, pausa = FUENTES[clave]
    terminos, raices, diccionario = POR_IDIOMA[idioma]
    consultas = [(t, {"search": t, "after": DESDE}) for t in terminos]
    descargar(clave, nombre, sitio, consultas, pausa=pausa, raices=raices, diccionario=diccionario)


def selfcheck():
    assert len(_NUEVAS) == 29 and len(FUENTES) == 19
    assert all(idioma in POR_IDIOMA for _, _, idioma, _ in FUENTES.values())
    assert relevante({"titulo": "La raccolta dei RIFIUTI"}, RAICES_ITALIANO_RESIDUOS)
    assert relevante({"titulo": "Gestão de resíduos"}, RAICES_PORTUGUES_RESIDUOS)
    assert relevante({"titulo": "Nowe składowisko i śmieci"}, RAICES_POLACO_RESIDUOS)
    assert relevante({"titulo": "Müll und Abfälle"}, RAICES_ALEMAN_RESIDUOS)
    assert not relevante({"titulo": "Elezioni oggi"}, RAICES_ITALIANO_RESIDUOS)
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuentes", nargs="*", help=", ".join(FUENTES))
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    desconocidas = set(args.fuentes) - set(FUENTES)
    if desconocidas:
        parser.error(f"fuentes desconocidas: {', '.join(sorted(desconocidas))}")
    if args.selfcheck:
        selfcheck()
    else:
        claves = args.fuentes or list(FUENTES)
        incompletas = []
        for numero, clave in enumerate(claves, 1):
            print(f"\n=== Fuente {numero} de {len(claves)}: {FUENTES[clave][0]} ===", flush=True)
            try:
                bajar(clave)
            except (SystemExit, ValueError, KeyError, TypeError) as motivo:
                print(f"{FUENTES[clave][0]}: quedó incompleta. {motivo} Sigo con la próxima fuente.", flush=True)
                incompletas.append(clave)
        print(f"\nTerminaron {len(claves) - len(incompletas)} de {len(claves)} fuentes.")
        if incompletas:
            print("Incompletas: " + " ".join(incompletas))
            print("Para retomarlas: python scripts/scrape_especializadas.py " + " ".join(incompletas))
