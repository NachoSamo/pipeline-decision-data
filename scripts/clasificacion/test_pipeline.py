"""Test de integración end-to-end de la tubería modular en scripts/clasificacion/."""

import json
import sys
from pathlib import Path

# Permitir ejecución directa del script
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import pytest
from prelimpieza import evaluar_descarte_heuristico, preparar_registro_para_llm
from clasificador_llm import ClasificadorLLM, MockLLMBackend
from transformacion import consolidar_resultados

# La muestra vive fuera del repo (máquina local). En CI no existe y el test se omite.
RUTA_MUESTRA = Path(r"C:\Users\Lautaro\.gemini\antigravity\brain\59fdb650-9d36-4235-814e-334e91d7b56e\scratch\sample_20_residuos.json")


@pytest.mark.skipif(not RUTA_MUESTRA.exists(), reason="requiere la muestra local sample_20_residuos.json (fuera del repo)")
def test_tubería_modular():
    raiz = Path(__file__).resolve().parent.parent.parent
    ruta_muestra = RUTA_MUESTRA

    with open(ruta_muestra, "r", encoding="utf-8") as f:
        registros = json.load(f)

    clasificador = ClasificadorLLM(backend=MockLLMBackend(), tema="residuos")
    analizados = []

    for item in registros:
        fila = {
            "id": f"reg_{item['idx']:02d}",
            "fuente": item["fuente"],
            "url": item["url"],
            "fecha": item["fecha"],
            "titulo": item["titulo"],
            "bajada": item["bajada"],
            "body": item["snippet_cuerpo"],
            "seccion": "Deportes" if "fútbol" in item["titulo"].lower() or "primera c" in item["titulo"].lower() else "General",
            "tags": ["reciclaje", "residuos"]  # prueba con lista de tags
        }

        descarte, _ = evaluar_descarte_heuristico(fila)
        if descarte:
            continue

        reg_listo = preparar_registro_para_llm(fila, max_chars_cuerpo=2500)
        resultado = clasificador.procesar_registro(reg_listo)
        if resultado:
            analizados.append(resultado)

    # Consolidar en data/resultados/test/
    ruta_salida = consolidar_resultados(analizados, tema="test", directorio_base=raiz / "data" / "resultados" / "test")

    # Validar Parquet
    df = pd.read_parquet(ruta_salida)
    assert len(df) > 0
    assert "texto_embedding_problema" in df.columns
    print(f"Test de integración modular superado exitosamente ({len(df)} registros validados).")


if __name__ == "__main__":
    test_tubería_modular()
