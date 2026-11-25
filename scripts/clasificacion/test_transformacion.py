"""Tests unitarios del score ponderado (Fuente x Recencia) de transformacion.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from transformacion import PESO_DEFAULT, PESOS_FUENTE, calcular_factor_recencia, calcular_score_ponderado


def test_factor_recencia_por_anio():
    assert calcular_factor_recencia("2026-03-01") == 1.0
    assert calcular_factor_recencia("2025-07-10") == 0.9
    assert calcular_factor_recencia("2024-01-01") == 0.8
    assert calcular_factor_recencia("2019-05-05") == 0.7
    assert calcular_factor_recencia(None) == 0.7
    assert calcular_factor_recencia("xx") == 0.7


def test_score_fuente_conocida_y_desconocida():
    assert calcular_score_ponderado("La Voz", "2026-01-01") == round(1.3 * 1.0, 3)
    assert calcular_score_ponderado("Fuente Inventada", "2026-01-01") == PESO_DEFAULT


def test_nota_mas_reciente_no_puntua_menos():
    for fuente in PESOS_FUENTE:
        assert calcular_score_ponderado(fuente, "2026-01-01") >= calcular_score_ponderado(fuente, "2024-01-01")


if __name__ == "__main__":
    test_factor_recencia_por_anio()
    test_score_fuente_conocida_y_desconocida()
    test_nota_mas_reciente_no_puntua_menos()
    print("test_transformacion: OK")
