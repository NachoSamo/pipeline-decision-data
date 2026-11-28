"""Comprueba que el exportador respeta el contrato. Corre con pytest o directo con python."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exportar_web import exportar, validar

RAIZ = Path(__file__).resolve().parent.parent
V1 = RAIZ / "data" / "resultados" / "v1-residuos" / "no_patrones"


def test_exporta_v1_y_cumple_contrato():
    with tempfile.TemporaryDirectory() as tmp:
        salida = exportar(V1, "v1", "residuos", advertencias=["prueba"], dir_data=Path(tmp))
        contrato = json.loads(salida.read_text(encoding="utf-8"))
        validar(contrato)
        assert contrato["meta"]["vigente"] is False
        assert any(n["destacado"] == "vacio" for n in contrato["nodos"])
        indice = json.loads((Path(tmp) / "index.json").read_text(encoding="utf-8"))
        assert [e["id"] for e in indice] == ["v1-residuos"]


def test_validar_rechaza_arista_huerfana():
    malo = {
        "meta": {k: None for k in ("version", "tema", "vigente", "fecha_analisis",
                                   "fecha_exportacion", "totales", "advertencias")},
        "nodos": [{"id": "P_0", "tipo": "Problema"}],
        "aristas": [{"origen": "P_0", "destino": "NO_EXISTE", "tipo": "CAUSADO_POR"}],
    }
    try:
        validar(malo)
    except AssertionError:
        return
    raise AssertionError("validar() aceptó una arista a un nodo inexistente")


if __name__ == "__main__":
    test_exporta_v1_y_cumple_contrato()
    test_validar_rechaza_arista_huerfana()
    print("OK")
