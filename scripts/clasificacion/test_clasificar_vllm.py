"""Chequeos sin GPU del clasificador v2 de movilidad."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clasificar_vllm  # noqa: E402
import evaluar_movilidad  # noqa: E402


def test_selfcheck():
    clasificar_vllm.selfcheck()


def test_evaluar_selfcheck():
    evaluar_movilidad.selfcheck()
