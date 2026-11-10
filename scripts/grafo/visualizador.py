"""Módulo de Visualización: Proyección UMAP 2D y Grafo Web Interactivo HTML.

Genera visualizaciones para la toma de decisiones y presentación del Hackatón.
"""

import json
import numpy as np
import pandas as pd
import networkx as nx
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


def generar_grafo_html_interactivo(
    G: nx.MultiDiGraph,
    df_gaps: pd.DataFrame,
    df_gemas: pd.DataFrame,
    ruta_salida: Path
) -> None:
    """Genera una interfaz web interactiva HTML autónoma utilizando Vis.js."""
    print("🌐 Generando visualizador web interactivo autónomo HTML...")
    
    top_gaps_set = set(df_gaps.head(15)["nodo_id"])
    top_gemas_set = set(df_gemas.head(15)["nodo_id"])
    
    # Formatear nodos para Vis.js
    nodos_vis = []
    colores_tipo = {
        "Problema": "#ef4444",      # Rojo
        "Solucion": "#10b981",      # Verde
        "CausaRaiz": "#f59e0b",     # Ámbar
        "Actor": "#3b82f6",         # Azul
        "Categoria": "#8b5cf6",     # Violeta
        "Ubicacion": "#06b6d4"      # Cyan
    }
    
    # Para mantener el rendimiento fluido en el navegador, mostramos el núcleo semántico:
    # Todos los problemas con gap_score alto, todas las soluciones, sus causas y categorías
    nodos_relevantes = set()
    for n in G.nodes():
        if n in top_gaps_set or n in top_gemas_set:
            nodos_relevantes.add(n)
            for neighbor in G.neighbors(n):
                nodos_relevantes.add(neighbor)
            for predecessor in G.predecessors(n):
                nodos_relevantes.add(predecessor)
                
    # Si el subgrafo es muy pequeño, incluimos más problemas y soluciones
    for n, d in G.nodes(data=True):
        if d.get("tipo") in ("Solucion", "Categoria") or len(nodos_relevantes) < 250:
            nodos_relevantes.add(n)

    for n in nodos_relevantes:
        d = G.nodes[n]
        tipo = d.get("tipo", "Entidad")
        label = d.get("titulo") or d.get("nombre") or n
        color = colores_tipo.get(tipo, "#64748b")
        size = 18
        border_width = 1
        border_color = color
        
        if n in top_gaps_set:
            color = "#f43f5e"
            border_width = 4
            border_color = "#fde047"
            size = 28
            label = f"⚠️ [VACÍO] {label[:30]}..."
        elif n in top_gemas_set:
            color = "#059669"
            border_width = 4
            border_color = "#38bdf8"
            size = 28
            label = f"💎 [GEMA] {label[:30]}..."
        elif tipo == "Categoria":
            size = 22
        elif tipo == "CausaRaiz":
            size = 16
            
        nodos_vis.append({
            "id": n,
            "label": str(label)[:45],
            "title": f"<b>{tipo}:</b> {label}<br><i>{d.get('descripcion', '')[:120]}</i>",
            "group": tipo,
            "color": {"background": color, "border": border_color},
            "borderWidth": border_width,
            "size": size,
            "font": {"color": "#ffffff", "size": 11}
        })
        
    aristas_vis = []
    for u, v, k, d in G.edges(keys=True, data=True):
        if u in nodos_relevantes and v in nodos_relevantes:
            rel = d.get("tipo", "RELACIONADO")
            color_edge = "#475569"
            dashes = False
            width = 1
            if rel == "MITIGA_POTENCIALMENTE":
                color_edge = "#34d399"
                dashes = True
                width = 2
            elif rel == "CAUSADO_POR":
                color_edge = "#f59e0b"
                width = 1.5
                
            aristas_vis.append({
                "from": u,
                "to": v,
                "label": rel if rel == "MITIGA_POTENCIALMENTE" else "",
                "color": {"color": color_edge, "highlight": "#38bdf8"},
                "arrows": "to",
                "dashes": dashes,
                "width": width
            })
            
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Grafo de Conocimiento y NO-PATRONES · Decision Data</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0b1120;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
        }}
        #header {{
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 56px;
            background: rgba(15, 23, 42, 0.95);
            border-bottom: 1px solid #1e293b;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 100;
        }}
        #header h1 {{
            font-size: 16px;
            font-weight: 700;
            color: #38bdf8;
            margin: 0;
        }}
        #legend {{
            display: flex;
            gap: 16px;
            font-size: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        #network {{
            position: absolute;
            top: 56px; bottom: 0; left: 0; right: 380px;
            background: #0f172a;
        }}
        #sidebar {{
            position: absolute;
            top: 56px; bottom: 0; right: 0;
            width: 380px;
            background: #1e293b;
            border-left: 1px solid #334155;
            padding: 20px;
            overflow-y: auto;
            box-sizing: border-box;
        }}
        .card {{
            background: #0f172a;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 14px;
            border: 1px solid #334155;
        }}
        .card h3 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #f8fafc;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .badge-gap {{ background: #991b1b; color: #fecaca; }}
        .badge-gema {{ background: #065f46; color: #a7f3d0; }}
        .prop {{ font-size: 12px; color: #94a3b8; margin: 4px 0; }}
        .prop strong {{ color: #cbd5e1; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🕸️ Grafo de Conocimiento & Detección de NO-PATRONES (Hack to the Future 2026)</h1>
        <div id="legend">
            <div class="legend-item"><div class="dot" style="background:#ef4444; border: 2px solid #fde047;"></div> Vacío (Gap)</div>
            <div class="legend-item"><div class="dot" style="background:#10b981; border: 2px solid #38bdf8;"></div> Gema Oculta</div>
            <div class="legend-item"><div class="dot" style="background:#f59e0b;"></div> Causa Raíz</div>
            <div class="legend-item"><div class="dot" style="background:#8b5cf6;"></div> Categoría</div>
            <div class="legend-item"><div class="dot" style="background:#3b82f6;"></div> Actor</div>
        </div>
    </div>
    
    <div id="network"></div>
    
    <div id="sidebar">
        <h2 style="font-size: 15px; color: #38bdf8; margin-top: 0;">Panel de Inspección de No-Patrones</h2>
        <p style="font-size: 12px; color: #94a3b8;">Haz clic en cualquier nodo para explorar sus causas, actores y nivel de desatención semántica.</p>
        
        <div id="node-details" class="card">
            <h3>Información del Nodo</h3>
            <p class="prop">Selecciona un elemento en el grafo central.</p>
        </div>

        <h3 style="font-size: 13px; color: #fde047; margin-top: 20px;">Top 3 Vacíos Críticos (Solution Gaps)</h3>
        {''.join([f'''
        <div class="card">
            <span class="badge badge-gap">Gap Score: {r["gap_score"]}</span>
            <h3>{r["titulo"]}</h3>
            <p class="prop"><strong>Categoría:</strong> {r["categoria"]}</p>
            <p class="prop"><strong>Causas:</strong> {r["causas_raiz"] or "No informadas"}</p>
            <p class="prop" style="color: #fca5a5;">⚠️ Distancia a solución más próxima: {r["distancia_solucion_mas_cercana"]}</p>
        </div>
        ''' for _, r in df_gaps.head(3).iterrows()])}

        <h3 style="font-size: 13px; color: #34d399; margin-top: 20px;">Top 2 Gemas Ocultas (Innovaciones Raras)</h3>
        {''.join([f'''
        <div class="card">
            <span class="badge badge-gema">Singularidad: {r["score_gema_oculta"]}</span>
            <h3>{r["nombre"]}</h3>
            <p class="prop"><strong>Impulsa:</strong> {r["quien_impulsa"]}</p>
            <p class="prop"><strong>Categoría:</strong> {r["categoria"]}</p>
            <p class="prop" style="color: #6ee7b7;">💡 Enfoque tecnológico atípico en el dataset</p>
        </div>
        ''' for _, r in df_gemas.head(2).iterrows()])}
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodos_vis, ensure_ascii=False)});
        var edges = new vis.DataSet({json.dumps(aristas_vis, ensure_ascii=False)});
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            physics: {{
                stabilization: false,
                barnesHut: {{
                    gravitationalConstant: -3500,
                    springLength: 95,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                navigationButtons: true,
                keyboard: true
            }}
        }};
        var network = new vis.Network(container, data, options);

        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var nodeData = nodes.get(nodeId);
                var html = '<h3>' + nodeData.label + '</h3>';
                html += '<p class="prop"><strong>ID:</strong> ' + nodeData.id + '</p>';
                html += '<p class="prop"><strong>Tipo:</strong> ' + nodeData.group + '</p>';
                html += '<p class="prop" style="margin-top:10px;">' + nodeData.title + '</p>';
                document.getElementById('node-details').innerHTML = html;
            }}
        }});
    </script>
</body>
</html>
"""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Grafo interactivo guardado en: {ruta_salida}")
