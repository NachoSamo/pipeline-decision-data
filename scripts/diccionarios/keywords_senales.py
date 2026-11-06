"""Señales de problema y de opinión, comunes a biodiversidad y movilidad.

No filtran: solo marcan cada nota en el Parquet (senal_problema y senal_opinion).
"""

SENALES_PROBLEMA = [
    # español
    "crisis", "conflicto", "denuncia", "reclamo", "reclaman", "amenaza", "perdida", "riesgo",
    "alerta", "advierte", "emergencia", "falta de", "deficit", "deterioro", "retroceso",
    "incumplimiento", "impacto", "afectados", "desaparicion",
    # inglés
    "threat", "decline", "loss", "conflict", "warn", "risk", "emergency", "illegal", "lack of",
    # portugués
    "ameaca", "denuncia", "perda", "risco", "alerta", "conflito", "falta de",
]

SENALES_OPINION = [
    # español
    "opinion", "columna", "analisis", "entrevista", "especialista", "investigador", "investigadora",
    "experto", "experta", "cientific", "biolog", "conicet", "universidad", "ong", "legislador",
    "legisladora", "proyecto de ley",
    # inglés
    "commentary", "op-ed", "opinion", "interview", "researcher", "scientist", "expert", "professor",
    "lawmaker", "legislation",
    # portugués
    "artigo", "entrevista", "pesquisador", "pesquisadora", "especialista", "cientista", "projeto de lei",
]

