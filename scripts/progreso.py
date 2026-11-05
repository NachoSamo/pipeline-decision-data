"""Muestra el avance de una descarga y cuántas notas mencionan residuos."""

import time
import unicodedata
from datetime import datetime

from keywords import RAICES_RESIDUOS


def normalizar(texto):
    sin_tildes = unicodedata.normalize("NFD", texto or "")
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower()


def relevante(fila, raices=RAICES_RESIDUOS):
    texto = normalizar(f"{fila.get('titulo')} {fila.get('bajada')} {fila.get('body')}")
    return any(raiz in texto for raiz in raices)


def _duracion(segundos):
    minutos = int(segundos // 60)
    return f"{minutos // 60} h {minutos % 60:02d} min" if minutos >= 60 else f"{minutos} min"


class Avance:
    def __init__(self, etiqueta, total=None, inicio=0, cada=15, mide_residuos=True):
        self.etiqueta = etiqueta
        self.mide_residuos = mide_residuos
        self.total = total
        self.hecho = inicio
        self.nuevas = 0
        self.utiles = 0
        self.cada = cada
        self.comienzo = time.monotonic()
        self.ultimo = 0

    def linea(self):
        partes = [f"[{datetime.now():%H:%M:%S}] {self.etiqueta}: {self.hecho}"]
        if self.total:
            partes[0] += f" de {self.total} ({min(self.hecho / self.total, 1):.0%})"
        if self.nuevas and self.mide_residuos:
            partes.append(f"mencionan residuos {self.utiles} ({self.utiles / self.nuevas:.0%})")
        transcurrido = time.monotonic() - self.comienzo
        if self.nuevas and transcurrido > 0:
            ritmo = self.nuevas / transcurrido
            partes.append(f"{ritmo * 60:.0f}/min")
            if self.total and self.total > self.hecho:
                partes.append(f"faltan {_duracion((self.total - self.hecho) / ritmo)}")
        return " | ".join(partes)

    def paso(self, cantidad=1, utiles=0, total=None):
        self.hecho += cantidad
        self.nuevas += cantidad
        self.utiles += utiles
        if total:
            self.total = total
        ahora = time.monotonic()
        if ahora - self.ultimo >= self.cada or (self.total and self.hecho >= self.total):
            print(self.linea(), flush=True)
            self.ultimo = ahora


if __name__ == "__main__":
    avance = Avance("Prueba", total=10, cada=0)
    avance.paso(2, utiles=1)
    assert "2 de 10 (20%)" in avance.linea() and "mencionan residuos 1 (50%)" in avance.linea()
    assert relevante({"titulo": "El BASURAL", "bajada": None, "body": ""})
    assert not relevante({"titulo": "Economía", "bajada": "", "body": "Dólar"})
    assert normalizar("Plásticos") == "plasticos"
    assert _duracion(3900) == "1 h 05 min"
    print("selfcheck ok")
