"""Limpia, deduplica y consolida los datasets en un Parquet por track, con un solo esquema.

Salidas (zstd nivel 19, para quedar debajo de los 100 MB de GitHub):
    data/biodiversidad.parquet   <- data/biodiversidad/*.parquet
    data/movilidad.parquet       <- data/movilidad/*.parquet
    data/residuos.parquet        <- data/residuos/*.parquet
    data/soluciones.parquet      <- data/soluciones/{residuos,agro,movilidad,biodiversidad}/*.parquet

Por cada salida: recorta el pie de suscripción del cuerpo; descarta títulos cortos, notas sin
cuerpo, sin fecha y de títulos seriados; deduplica por id, título normalizado y cuerpo (se queda
con el cuerpo más largo y, a igualdad, la nota más vieja); une los tracks de las duplicadas y
recalcula tipo_voz. Al terminar de escribir las 4 salidas, borra los Parquet por fuente.

Orden del flujo de soluciones: crudo -> separar_por_track.py -> limpiar.py. Si se vuelve a correr
separar_por_track.py, hay que volver a correr este script.

Uso:
    python scripts/limpiar.py --selfcheck
    python scripts/limpiar.py --simular
    python scripts/limpiar.py
"""

import argparse
import os
import re
from pathlib import Path

os.environ["DATASET"] = "soluciones"  # evita que dataset.py recree data/residuos al importar

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from diccionarios.keywords_soluciones import RAICES_TRACK
from progreso import normalizar
from scrape_problematicas import PATRON_SECCION

DATA = Path(__file__).resolve().parent.parent / "data"
LIMITE_MB = 100
ORDEN_TRACKS = list(RAICES_TRACK)
SALIDAS = {
    "biodiversidad": ["biodiversidad"],
    "movilidad": ["movilidad"],
    "residuos": ["residuos"],
    "soluciones": [f"soluciones/{t}" for t in ORDEN_TRACKS],
}
DIARIOS = {"CBA24N", "Clarín", "El Doce", "Infobae", "La Nación", "TN"}

LISTA = pa.list_(pa.string())
ESQUEMA = pa.schema([
    ("id", pa.string()),
    ("url", pa.string()),
    ("fuente", pa.string()),
    ("titulo", pa.string()),
    ("bajada", pa.string()),
    ("fecha", pa.timestamp("us", tz="UTC")),
    ("seccion", pa.string()),
    ("tags", LISTA),
    ("tipo", pa.string()),
    ("body", pa.string()),
    ("acceso_libre", pa.bool_()),
    ("terminos_busqueda", LISTA),
    ("terminos_en_texto", LISTA),
    ("diccionario_en_texto", LISTA),
    ("keywords_core", LISTA),
    ("tipo_voz", pa.string()),
    ("tracks", LISTA),
])
COLUMNAS = ESQUEMA.names
LISTAS = [c.name for c in ESQUEMA if c.type == LISTA]

# Texto fijo de suscripción o de código que algunas fuentes pegan al cuerpo. Cada patrón borra
# solo ese bloque, no el resto de la nota.
PIES = [
    # Mongabay Latam
    re.compile(r"^[ \t]*(?:Y )?[Ss]i quieres (?:estar al tanto de las mejores historias de Mongabay"
               r"|conocer m[áa]s sobre la situaci[óo]n ambiental)[^\n]*$", re.M),
    # Muro de pago de Bioplastics News
    re.compile(r"Subscribe to get access\s*Read more of this content when you subscribe today\.?\s*"
               r"Subscribe\s*Submitting form\s*Log in"),
    # Formulario de newsletter de 320°
    re.compile(r"Am Abend das Wichtigste vom Tag!.*?Infos zum Datenschutz finden Sie hier\.", re.S),
    # Bloque de newsletters de Inside Climate News
    re.compile(r"Newsletters\s*We deliver climate news to your inbox.*?I agree to the terms of service and privacy policy\.", re.S),
    # Glosario en JavaScript de Grist
    re.compile(r"^[ \t]*toolTips\(.*$", re.M),
    # Líneas cortas de invitación a newsletters (Grist y otros en inglés)
    re.compile(r"^[^\n]{0,120}\b(?:Sign up for|subscribe to) the\b[^\n]{0,80}\bnewsletters?\b[^\n]{0,60}$", re.M),
]

# Títulos de servicio o de serie diaria, sobre el título normalizado. Salen de los prefijos que más
# se repiten; se evitan patrones amplios como "agenda" o "dia mundial".
SERIADOS = re.compile("|".join([
    r"^cronogramas? de pagos?\b",
    r"^dolar (?:blue|hoy|oficial|solidario|tarjeta|mep)\b",
    r"^cortes de luz\b",
    r"^los cortes de calles\b",
    r"^lo mas leido\b",
    r"^colectivo imaginario\b",
    r"^que significa (?:la|esta) senal\b",
    r"^trenes hoy\b",
    r"^pocos lo saben\b",
    r"^la psicologia dice\b",
    r"^\W*cual es el signo\b",
    r"\bhoroscopo\b",
    r"\bquiniela\b",
    r"\bminuto a minuto\b",
    r"^agenda vida digital\b",
    r"^tn ecologia$",
]))
LARGO_MINIMO_TITULO = 15


def clave_titulo(titulos):
    return titulos.fillna("").map(normalizar).str.replace(r"\s+", " ", regex=True).str.strip()


def como_lista(valor):
    if valor is None or isinstance(valor, (str, float)):
        return []
    return [str(x) for x in valor if x is not None]


def ordenar_tracks(tracks):
    return sorted(set(tracks), key=lambda t: ORDEN_TRACKS.index(t) if t in ORDEN_TRACKS else len(ORDEN_TRACKS))


def tipo_voz(notas):
    etiquetas = notas["seccion"].fillna("") + " " + notas["tags"].map(" ".join)
    opinion = etiquetas.map(lambda e: bool(PATRON_SECCION.search(normalizar(e))))
    voz = notas["fuente"].isin(DIARIOS).map({True: "diario", False: "medio_especializado"})
    return voz.where(~opinion, "opinion")


def unificar(notas):
    notas = notas.reindex(columns=COLUMNAS).copy()
    for columna in LISTAS:
        notas[columna] = notas[columna].map(como_lista)
    notas["acceso_libre"] = notas["acceso_libre"].map(lambda x: None if pd.isna(x) else bool(x)).astype(object)
    notas["fecha"] = pd.to_datetime(notas["fecha"], utc=True, errors="coerce").dt.as_unit("us")
    body = notas["body"].fillna("")
    for pie in PIES:
        body = body.str.replace(pie, "", regex=True)
    notas["body"] = body.str.replace(r"\n{3,}", "\n\n", regex=True).str.strip()
    return notas


def limpiar(notas):
    """Recibe las notas crudas de una salida, con su columna tracks. Devuelve (limpias, conteo)."""
    conteo = {"iniciales": len(notas)}
    notas = unificar(notas)
    titulo = clave_titulo(notas["titulo"])
    descartes = {
        "título corto": titulo.str.len() < LARGO_MINIMO_TITULO,
        "sin cuerpo": notas["body"] == "",
        "sin fecha": notas["fecha"].isna(),
        "seriado": titulo.str.contains(SERIADOS),
    }
    quedan = pd.Series(True, index=notas.index)
    for motivo, sale in descartes.items():
        conteo[motivo] = int((quedan & sale).sum())
        quedan &= ~sale
    notas = notas[quedan].assign(_titulo=titulo[quedan], _largo=notas["body"][quedan].str.len())
    notas = notas.sort_values(["_largo", "fecha"], ascending=[False, True], kind="stable")
    for motivo, clave in [("id repetido", "id"), ("título repetido", "_titulo"), ("cuerpo repetido", "body")]:
        unidos = notas.groupby(clave, dropna=False)["tracks"].agg(lambda grupo: ordenar_tracks(t for ts in grupo for t in ts))
        notas["tracks"] = notas[clave].map(unidos)
        antes = len(notas)
        notas = notas.drop_duplicates(clave)
        conteo[motivo] = antes - len(notas)
    notas["tipo_voz"] = tipo_voz(notas)
    notas = notas.sort_values("fecha", kind="stable")[COLUMNAS].reset_index(drop=True)
    conteo["finales"] = len(notas)
    return notas, conteo


def leer(nombre, carpetas):
    partes = []
    for carpeta in carpetas:
        for archivo in sorted(carpeta.glob("*.parquet")):
            parte = pd.read_parquet(archivo)
            if nombre != "soluciones":
                parte["tracks"] = [[nombre]] * len(parte)
            partes.append(parte)
    return pd.concat(partes, ignore_index=True)


def escribir(notas, destino):
    # El nivel por defecto dejaba biodiversidad en 109 MB; con 19 queda en 73 MB. Tarda unos minutos.
    pq.write_table(pa.Table.from_pandas(notas, schema=ESQUEMA, preserve_index=False), destino,
                   compression="zstd", compression_level=19)
    megas = destino.stat().st_size / 1024 / 1024
    if megas > LIMITE_MB:
        print(f"AVISO: {destino.name} pesa {megas:.0f} MB y supera los {LIMITE_MB} MB de GitHub.")
    return megas


def correr(simular=False, raiz=DATA):
    carpetas = {nombre: [raiz / c for c in rels] for nombre, rels in SALIDAS.items()}
    vacias = [str(c) for cs in carpetas.values() for c in cs if not any(c.glob("*.parquet"))]
    if vacias:
        # Sin esta guarda, una segunda corrida pisaría las salidas con archivos vacíos.
        raise SystemExit("No hay Parquet por fuente en: " + ", ".join(vacias) + ". ¿Ya se limpió? No se escribió nada.")
    filas = {}
    for nombre, cs in carpetas.items():
        print(f"Limpiando {nombre}...", flush=True)
        notas, conteo = limpiar(leer(nombre, cs))
        if not simular:
            conteo["MB"] = round(escribir(notas, raiz / f"{nombre}.parquet"))
        if nombre == "soluciones":
            por_track = pd.Series([t for ts in notas["tracks"] for t in ts]).value_counts()
            print("Soluciones por track (una nota puede estar en varios):\n" + por_track.to_string())
        filas[nombre] = conteo
        del notas
    print("\n" + pd.DataFrame(filas).T.fillna(0).astype(int).to_string())
    if simular:
        print("\nSimulación: no se escribió ni se borró nada.")
        return
    for cs in carpetas.values():
        for carpeta in cs:
            for archivo in carpeta.glob("*.parquet"):
                archivo.unlink()
            try:
                carpeta.rmdir()
            except OSError:
                pass  # quedan archivos que no son Parquet (por ejemplo, ignorados por git)
    print("\nListo. Se borraron los Parquet por fuente; la versión anterior queda en git.")


def selfcheck():
    import tempfile

    pie = "\nSi quieres estar al tanto de las mejores historias de Mongabay Latam, puedes suscribirte al boletín aquí."
    texto = "Un cuerpo con contenido real sobre el tema."
    crudo = pd.DataFrame([
        # id, fuente, titulo, fecha, body, seccion, tags, acceso_libre
        ("a1", "TN", "Basural a cielo abierto en Córdoba", "2024-01-02", "", "videos", None, None),            # video sin cuerpo
        ("a2", "TN", "Basural a cielo abierto en Córdoba", "2024-01-02", texto + " largo", "sociedad", None, 1.0),
        ("a3", "Clarín", "  BASURAL a cielo   abierto en Cordoba ", "2024-01-01", texto, "Opinión", None, 0.0),
        ("a4", "Mongabay", "Corto", "2024-01-03", texto, "", ["Bosques", None], True),
        ("a5", "Mongabay", "Una nota sin fecha válida", None, texto + " otra", "", [], None),
        ("a6", "El Doce", "Cortes de luz de Epec para este viernes en Córdoba", "2024-01-04", texto + " epec", "", [], None),
        ("a7", "Mongabay", "Deforestación en el Chaco seco avanza", "2024-01-05", "Texto del Chaco." + pie, "", ["Commentary"], None),
        ("a8", "Grist", "Otro título con el mismo cuerpo", "2024-01-06", "Texto del Chaco.", "", [], None),
    ], columns=["id", "fuente", "titulo", "fecha", "body", "seccion", "tags", "acceso_libre"])
    crudo["url"] = "https://x/" + crudo["id"]
    crudo["tracks"] = [["residuos"]] * len(crudo)
    limpias, conteo = limpiar(crudo)
    assert conteo == {"iniciales": 8, "título corto": 1, "sin cuerpo": 1, "sin fecha": 1, "seriado": 1,
                      "id repetido": 0, "título repetido": 1, "cuerpo repetido": 1, "finales": 2}, conteo
    assert limpias["id"].tolist() == ["a2", "a7"]  # texto más largo; el video y la copia de Grist salen
    assert limpias["body"].tolist()[1] == "Texto del Chaco."
    assert limpias["tipo_voz"].tolist() == ["diario", "opinion"]

    # Soluciones: la misma nota en dos tracks y una copia de título en un tercero.
    sol = pd.DataFrame({
        "id": ["s1", "s1", "s2"], "url": ["u1", "u1", "u2"], "fuente": ["Grist"] * 3,
        "titulo": ["Startup de compost para el agro"] * 2 + ["Startup de compost para el AGRO"],
        "fecha": ["2025-01-01"] * 3, "body": [texto] * 2 + [texto + "!"],
        "tracks": [["residuos", "agro"], ["residuos", "agro"], ["biodiversidad"]],
        "acceso_libre": [1.0, 1.0, False], "edicion": [None] * 3, "senal_problema": [[]] * 3,
    })
    limpias_sol, conteo_sol = limpiar(sol)
    assert conteo_sol["id repetido"] == 1 and conteo_sol["título repetido"] == 1 and len(limpias_sol) == 1
    assert list(limpias_sol["tracks"][0]) == ["residuos", "agro", "biodiversidad"]
    assert limpias_sol["acceso_libre"].tolist() == [False]

    with tempfile.TemporaryDirectory() as tmp:
        escribir(limpias, Path(tmp) / "a.parquet")
        escribir(limpias_sol, Path(tmp) / "b.parquet")
        assert pq.read_schema(Path(tmp) / "a.parquet").equals(ESQUEMA) and pq.read_schema(Path(tmp) / "b.parquet").equals(ESQUEMA)
        try:
            correr(simular=True, raiz=Path(tmp))
            raise AssertionError("debió frenar sin Parquet de entrada")
        except SystemExit as motivo:
            assert "No se escribió nada" in str(motivo)
    print("selfcheck ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--simular", action="store_true", help="Muestra la tabla sin escribir ni borrar nada.")
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
    else:
        correr(args.simular)
