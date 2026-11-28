"""Módulo de Visualización: proyección UMAP 2D.

El grafo web ya no se genera acá: lo exporta Frontend/exportar_web.py y lo dibuja Frontend/web/.

Genera visualizaciones para la toma de decisiones y presentación del Hackatón.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import umap


def generar_mapa_umap_2d(
    emb_problemas: np.ndarray,
    emb_soluciones: np.ndarray,
    df_problemas: pd.DataFrame,
    df_soluciones: pd.DataFrame,
    df_gaps: pd.DataFrame,
    ruta_salida: Path
) -> None:
    """Genera un mapa 2D de alta resolución (UMAP) visualizando desiertos de soluciones."""
    print("🗺️ Calculando proyección UMAP 2D del espacio latente...")
    
    todos_emb = np.vstack([emb_problemas, emb_soluciones])
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.15, metric="cosine", random_state=42)
    coords_2d = reducer.fit_transform(todos_emb)
    
    n_p = len(df_problemas)
    coords_p = coords_2d[:n_p]
    coords_s = coords_2d[n_p:]
    
    plt.figure(figsize=(14, 10), facecolor="#0f172a")
    ax = plt.gca()
    ax.set_facecolor("#0f172a")
    
    # 1. Graficar Problemas (Puntos Rojos / Coral)
    plt.scatter(
        coords_p[:, 0], coords_p[:, 1],
        c="#f87171", label=f"Problemas ({n_p})",
        alpha=0.6, s=55, edgecolors="#ef4444", linewidths=0.5
    )
    
    # 2. Graficar Soluciones (Puntos Verdes / Esmeralda)
    plt.scatter(
        coords_s[:, 0], coords_s[:, 1],
        c="#34d399", label=f"Soluciones ({len(df_soluciones)})",
        alpha=0.9, s=90, edgecolors="#10b981", marker="^", linewidths=1.2
    )
    
    # 3. Resaltar los Top 10 Vacíos Críticos de Solución (No-Patrones)
    top_gap_ids = set(df_gaps.head(10)["nodo_id"])
    indices_top_gap = [i for i in range(n_p) if f"P_{i}" in top_gap_ids]
    
    if indices_top_gap:
        plt.scatter(
            coords_p[indices_top_gap, 0], coords_p[indices_top_gap, 1],
            facecolors="none", edgecolors="#fbbf24", s=280,
            linewidths=2.5, label="Top 10 Vacíos Críticos (Desiertos)", linestyle="--"
        )
        for idx_g in indices_top_gap:
            titulo_resumido = str(df_problemas.iloc[idx_g].get("titulo_problema") or "")[:28]
            plt.annotate(
                f"⚠️ {titulo_resumido}...",
                (coords_p[idx_g, 0], coords_p[idx_g, 1]),
                color="#fde047", fontsize=8.5, weight="bold",
                xytext=(8, 8), textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.2", fc="#1e293b", ec="#fbbf24", alpha=0.85)
            )

    # Estilos del Gráfico
    plt.title(
        "Mapa de Densidad Semántica: Detección de Vacíos de Solución (NO-PATRONES)\n"
        "Córdoba Tech Week · Hack to the Future 2026",
        color="#f8fafc", fontsize=15, weight="bold", pad=20
    )
    plt.xlabel("Dimensión UMAP 1", color="#94a3b8", fontsize=11)
    plt.ylabel("Dimensión UMAP 2", color="#94a3b8", fontsize=11)
    ax.tick_params(colors="#94a3b8")
    for spine in ax.spines.values():
        spine.set_color("#334155")
        
    leg = plt.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="#f8fafc", fontsize=11, loc="upper right")
    plt.grid(True, color="#1e293b", linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ruta_salida, dpi=300, facecolor="#0f172a")
    plt.close()
    print(f"✅ Mapa UMAP 2D guardado en: {ruta_salida}")
