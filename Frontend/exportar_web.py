"""Exporta el grafo de no-patrones al contrato JSON que lee la web (Frontend/web/data/).

Lee el .gexf y el reporte_no_patrones.json que ya genera scripts/grafo/ejecutar_analisis.py.
No recalcula nada y solo usa la biblioteca estándar.

Uso:
    python Frontend/exportar_web.py --dir-resultados data/resultados/v1-residuos/no_patrones --version v1 --tema residuos
    Agregar --vigente solo si esa versión es la vigente, y --advertencia "texto" (repetible) para los límites conocidos.
"""

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

DIR_DATA = Path(__file__).resolve().parent / "web" / "data"
DIR_RECORRIDOS = Path(__file__).resolve().parent / "recorridos"  # embudo medido por versión, opcional

TIPOS_NODO = {"Problema", "Solucion", "CausaRaiz", "Actor", "Categoria", "Ubicacion"}
TIPOS_ARISTA = {
    "PERTENECE_A", "CAUSADO_POR", "AFECTA_A", "UBICADO_EN",
    "IMPULSADA_POR", "APUNTA_A_CATEGORIA", "MITIGA_POTENCIALMENTE",
}
CAMPOS_META = {"version", "tema", "vigente", "fecha_analisis", "fecha_exportacion", "totales", "advertencias"}
TOP_DESTACADOS = 15  # cuántos vacíos, gemas y cuellos se marcan en el grafo

# (clave del ranking en el reporte, valor de "destacado", campo del score)
RANKINGS = [
    ("vacios_solucion", "vacio", "gap_score"),
    ("gemas_ocultas", "gema", "score_gema_oculta"),
    ("causas_cuello_botella", "cuello", "indice_desatencion"),
]


def leer_gexf(ruta: Path) -> tuple[list[dict], list[dict], str]:
    """Devuelve (nodos, aristas, fecha) leyendo el GEXF 1.2 que escribe NetworkX."""
    ns = {"g": "http://www.gexf.net/1.2draft"}
    raiz = ET.parse(ruta).getroot()
    fecha = (raiz.find("g:meta", ns).get("lastmodifieddate") or "") if raiz.find("g:meta", ns) is not None else ""
    grafo = raiz.find("g:graph", ns)

    titulos = {}  # (clase, id) -> nombre del atributo
    for bloque in grafo.findall("g:attributes", ns):
        for a in bloque.findall("g:attribute", ns):
            titulos[(bloque.get("class"), a.get("id"))] = a.get("title")

    def atributos(elem, clase):
        return {
            titulos[(clase, av.get("for"))]: av.get("value")
            for av in elem.findall("g:attvalues/g:attvalue", ns)
        }

    nodos = [{"id": n.get("id"), **atributos(n, "node")} for n in grafo.findall("g:nodes/g:node", ns)]
    aristas = [
        {"origen": e.get("source"), "destino": e.get("target"), **atributos(e, "edge")}
        for e in grafo.findall("g:edges/g:edge", ns)
    ]
    return nodos, aristas, fecha


def construir_contrato(nodos_gexf, aristas_gexf, reporte, *, version, tema, vigente, advertencias, fecha_analisis):
    destacados = {}  # id -> (tipo de destacado, score, puesto)
    for clave, marca, campo in RANKINGS:
        for puesto, fila in enumerate(reporte.get(clave, [])[:TOP_DESTACADOS], 1):
            destacados.setdefault(fila["nodo_id"], (marca, fila.get(campo), puesto))

    nodos = []
    for n in nodos_gexf:
        url = n.get("id_original") or ""
        marca, score, puesto = destacados.get(n["id"], (None, None, None))
        nodos.append({
            "id": n["id"],
            "tipo": n.get("tipo"),
            "etiqueta": n.get("titulo") or n.get("nombre") or n["id"],
            "descripcion": n.get("descripcion") or "",
            "categoria": n.get("categoria") or "",
            "ubicacion": n.get("ubicacion") or "",
            "fuente": n.get("fuente") or "",
            "fecha": (n.get("fecha") or "")[:10],
            "url_fuente": url if url.startswith("http") else "",
            "destacado": marca,
            "puesto": puesto,
            "score": score,
        })

    aristas = [
        {
            "origen": a["origen"],
            "destino": a["destino"],
            "tipo": a.get("tipo"),
            "peso": float(a["similitud"]) if a.get("similitud") else None,
        }
        for a in aristas_gexf
    ]

    return {
        "meta": {
            "version": version,
            "tema": tema,
            "vigente": vigente,
            "fecha_analisis": fecha_analisis,
            "fecha_exportacion": date.today().isoformat(),
            "totales": reporte.get("resumen", {}),
            "advertencias": advertencias,
        },
        "nodos": nodos,
        "aristas": aristas,
        "rankings": {clave: reporte.get(clave, []) for clave, _, _ in RANKINGS},
    }


def validar(contrato: dict) -> None:
    """Falla si el JSON no cumple el contrato que espera la web."""
    faltan = CAMPOS_META - contrato["meta"].keys()
    assert not faltan, f"Faltan campos en meta: {faltan}"
    ids = {n["id"] for n in contrato["nodos"]}
    assert len(ids) == len(contrato["nodos"]), "Hay ids de nodo repetidos"
    for n in contrato["nodos"]:
        assert n["tipo"] in TIPOS_NODO, f"Tipo de nodo desconocido: {n['tipo']} ({n['id']})"
    for a in contrato["aristas"]:
        assert a["tipo"] in TIPOS_ARISTA, f"Tipo de arista desconocido: {a['tipo']}"
        assert a["origen"] in ids and a["destino"] in ids, f"Arista a un nodo inexistente: {a}"


def actualizar_indice(contrato: dict, archivo: str, dir_data: Path) -> None:
    ruta = dir_data / "index.json"
    indice = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []
    meta = contrato["meta"]
    entrada = {
        "id": archivo.removesuffix(".json"),
        "version": meta["version"],
        "tema": meta["tema"],
        "vigente": meta["vigente"],
        "fecha": meta["fecha_analisis"],
        "archivo": archivo,
    }
    indice = [e for e in indice if e["id"] != entrada["id"]] + [entrada]
    indice.sort(key=lambda e: (not e["vigente"], e["tema"], e["version"]))
    ruta.write_text(json.dumps(indice, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def exportar(dir_resultados: Path, version: str, tema: str, vigente: bool = False,
             advertencias: list[str] | None = None, dir_data: Path = DIR_DATA) -> Path:
    gexf = next(dir_resultados.glob("*.gexf"))
    reporte = json.loads((dir_resultados / "reporte_no_patrones.json").read_text(encoding="utf-8"))
    nodos, aristas, fecha = leer_gexf(gexf)
    contrato = construir_contrato(
        nodos, aristas, reporte, version=version, tema=tema, vigente=vigente,
        advertencias=advertencias or [], fecha_analisis=fecha,
    )
    recorrido = DIR_RECORRIDOS / f"{version}-{tema}.json"
    contrato["meta"]["recorrido"] = json.loads(recorrido.read_text(encoding="utf-8")) if recorrido.exists() else None
    validar(contrato)

    dir_data.mkdir(parents=True, exist_ok=True)
    archivo = f"{version}-{tema}.json"
    salida = dir_data / archivo
    salida.write_text(json.dumps(contrato, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    actualizar_indice(contrato, archivo, dir_data)
    print(f"✅ {salida} ({len(contrato['nodos'])} nodos, {len(contrato['aristas'])} aristas)")
    return salida


def main():
    p = argparse.ArgumentParser(description="Exporta el grafo de no-patrones al JSON de la web")
    p.add_argument("--dir-resultados", required=True, help="Carpeta con el .gexf y reporte_no_patrones.json")
    p.add_argument("--version", required=True)
    p.add_argument("--tema", required=True)
    p.add_argument("--vigente", action="store_true", help="Marcar esta versión como vigente")
    p.add_argument("--advertencia", action="append", default=[], help="Límite conocido que la web muestra (repetible)")
    a = p.parse_args()
    exportar(Path(a.dir_resultados), a.version, a.tema, a.vigente, a.advertencia)


if __name__ == "__main__":
    main()
