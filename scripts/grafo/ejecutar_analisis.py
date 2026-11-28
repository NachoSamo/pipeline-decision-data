"""CLI Orquestador del Pipeline de Grafo de Conocimiento y No-Patrones.

Uso:
    python scripts/grafo/ejecutar_analisis.py --entrada data/resultados/v1-residuos/residuos_clasificado_final.parquet --dir-salida data/resultados/v1-residuos/no_patrones
    Para una versión nueva, cambiar VERSION en scripts/clasificacion/version.py o pasar las rutas de la nueva versión.
"""

import sys
import json
import argparse
import time
from pathlib import Path
import pandas as pd
import networkx as nx

from const_grafo import construir_grafo_conocimiento
from motor_no_patrones import ejecutar_analisis_no_patrones
from visualizador import generar_mapa_umap_2d

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "clasificacion"))
from version import VERSION

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Frontend"))
from exportar_web import exportar as exportar_web


def generar_reporte_markdown(
    resultados: dict,
    total_problemas: int,
    total_soluciones: int,
    total_nodos: int,
    total_aristas: int,
    ruta_reporte: Path
) -> None:
    """Genera un reporte analítico en Markdown con los No-Patrones detectados."""
    df_gaps = resultados["vacios_solucion"]
    df_gemas = resultados["gemas_ocultas"]
    df_cuellos = resultados["causas_cuello_botella"]
    
    md = []
    md.append("# 📊 Reporte Estratégico de NO-PATRONES y Vacíos de Solución")
    md.append("**Hack to the Future 2026 · Córdoba Tech Week · Decision Data**\n")
    md.append("---")
    md.append("## 1. Resumen Ejecutivo del Grafo de Conocimiento")
    md.append(f"- **Total Nodos en el Grafo:** {total_nodos:,}")
    md.append(f"- **Total Relaciones (Aristas):** {total_aristas:,}")
    md.append(f"- **Problemáticas Ambientales Analizadas:** {total_problemas:,}")
    md.append(f"- **Soluciones / Iniciativas Registradas:** {total_soluciones:,}")
    md.append(f"- **Ratio Problema / Solución:** {total_problemas / max(total_soluciones, 1):.2f} problemas por cada solución identificada en medios.\n")
    
    md.append("---")
    md.append("## 2. Top Vacíos Críticos de Mercado (Solution Gaps)")
    md.append("> [!WARNING]")
    md.append("> Estos problemas tienen alta recurrencia en el territorio pero carecen de soluciones vinculadas y presentan la máxima distancia en el espacio vectorial.")
    md.append("")
    md.append("| # | Problema | Categoría | Causas Raíz | Gap Score | Distancia a Solución más Próxima |")
    md.append("|---|---|---|---|:---:|:---:|")
    for i, (_, r) in enumerate(df_gaps.head(10).iterrows(), 1):
        causas = (r["causas_raiz"] or "No informadas")[:45]
        md.append(f"| {i} | **{r['titulo']}** | `{r['categoria']}` | {causas} | **{r['gap_score']}** | `{r['distancia_solucion_mas_cercana']}` |")
        
    md.append("\n---")
    md.append("## 3. Top Gemas Ocultas de Innovación (Outliers Tecnológicos)")
    md.append("> [!TIP]")
    md.append("> Iniciativas poco frecuentes (1 o 2 apariciones) con alto grado de singularidad técnica que abordan nichos desatendidos.")
    md.append("")
    md.append("| # | Nombre Solución | Quién Impulsa | Categoría | Score Gema | Singularidad Vectorial |")
    md.append("|---|---|---|---|:---:|:---:|")
    for i, (_, r) in enumerate(df_gemas.head(10).iterrows(), 1):
        md.append(f"| {i} | **{r['nombre']}** | {r['quien_impulsa']} | `{r['categoria']}` | **{r['score_gema_oculta']}** | `{r['singularidad_vectorial']}` |")
        
    md.append("\n---")
    md.append("## 4. Causas Raíz Cuello de Botella (Talón de Aquiles)")
    md.append("> [!IMPORTANT]")
    md.append("> Causas estructurales que provocan múltiples problemas pero prácticamente ninguna solución las mitiga.")
    md.append("")
    md.append("| # | Causa Raíz | Problemas que la Padecen | Soluciones que la Mitigan | Índice de Desatención |")
    md.append("|---|---|:---:|:---:|:---:|")
    for i, (_, r) in enumerate(df_cuellos.head(10).iterrows(), 1):
        md.append(f"| {i} | **{r['causa_raiz']}** | {r['problemas_que_la_padecen']} | {r['soluciones_que_la_mitigan']} | **{r['indice_desatencion']}** |")
        
    md.append("\n---")
    md.append("## 5. Archivos de Visualización Generados")
    carpeta_md = f"data/resultados/{VERSION}-residuos/no_patrones"
    md.append(f"- **Grafo web interactivo:** `Frontend/web/data/{VERSION}-residuos.json`, que dibuja la web de `Frontend/web/`.")
    md.append(f"- **Mapa 2D de Desiertos (UMAP):** `{carpeta_md}/mapa_desiertos_2d.png`.")
    md.append(f"- **Exportación estándar de Red:** `{carpeta_md}/grafo_residuos.gexf`.")
    md.append(f"- **Dataset de No-Patrones JSON:** `{carpeta_md}/reporte_no_patrones.json`.")

    with open(ruta_reporte, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"✅ Reporte en Markdown generado en: {ruta_reporte}")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Grafo y Detección de No-Patrones")
    parser.add_argument(
        "--entrada",
        type=str,
        default=f"data/resultados/{VERSION}-residuos/residuos_clasificado_final.parquet",
        help="Ruta al archivo Parquet clasificado"
    )
    parser.add_argument(
        "--dir-salida",
        type=str,
        default=f"data/resultados/{VERSION}-residuos/no_patrones",
        help="Directorio de destino para reportes y visualizaciones"
    )
    args = parser.parse_args()
    
    t0 = time.time()
    ruta_in = Path(args.entrada)
    dir_out = Path(args.dir_salida)
    dir_out.mkdir(parents=True, exist_ok=True)
    
    if not ruta_in.exists():
        print(f"❌ Error: No existe el archivo de entrada: {ruta_in}")
        sys.exit(1)
        
    print(f"\n{'='*75}")
    print(f"🚀 INICIANDO ANÁLISIS DE GRAFO Y NO-PATRONES (RESIDUOS)")
    print(f"📂 Entrada: {ruta_in}")
    print(f"📁 Salida:  {dir_out}")
    print(f"{'='*75}\n")
    
    # 1. Carga del dataset
    df = pd.read_parquet(ruta_in)
    
    # 2. Construcción del Grafo
    G, df_prob, df_sol, emb_prob, emb_sol, mat_sim = construir_grafo_conocimiento(
        df,
        umbral_similitud_arista=0.32,
        top_k_vecinos=3
    )
    
    # 3. Detección Cuantitativa de No-Patrones
    resultados = ejecutar_analisis_no_patrones(G, df_prob, df_sol, emb_sol, mat_sim)
    
    # 4. Generación de Visualizaciones
    ruta_umap = dir_out / "mapa_desiertos_2d.png"
    generar_mapa_umap_2d(emb_prob, emb_sol, df_prob, df_sol, resultados["vacios_solucion"], ruta_umap)
    
    # 5. Exportar Grafo GEXF
    ruta_gexf = dir_out / "grafo_residuos.gexf"
    # Limpiar atributos para compatibilidad estricta de GEXF
    G_clean = nx.MultiDiGraph()
    for n, d in G.nodes(data=True):
        G_clean.add_node(n, **{k: str(v) if v is not None else "" for k, v in d.items()})
    for u, v, k, d in G.edges(keys=True, data=True):
        G_clean.add_edge(u, v, key=k, **{k_: str(v_) if v_ is not None else "" for k_, v_ in d.items()})
    nx.write_gexf(G_clean, ruta_gexf)
    print(f"✅ Grafo en formato GEXF guardado en: {ruta_gexf}")
    
    # 6. Exportar Reportes (JSON y Markdown)
    reporte_json = {
        "resumen": {
            "total_problemas": len(df_prob),
            "total_soluciones": len(df_sol),
            "total_nodos": G.number_of_nodes(),
            "total_aristas": G.number_of_edges()
        },
        "vacios_solucion": resultados["vacios_solucion"].to_dict(orient="records"),
        "gemas_ocultas": resultados["gemas_ocultas"].to_dict(orient="records"),
        "causas_cuello_botella": resultados["causas_cuello_botella"].to_dict(orient="records")
    }
    ruta_json = dir_out / "reporte_no_patrones.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(reporte_json, f, indent=2, ensure_ascii=False)
    print(f"✅ Reporte en JSON guardado en: {ruta_json}")
    
    ruta_md = dir_out / "reporte_no_patrones.md"
    generar_reporte_markdown(
        resultados,
        len(df_prob),
        len(df_sol),
        G.number_of_nodes(),
        G.number_of_edges(),
        ruta_md
    )
    
    # 7. Exportar al contrato JSON de la web (Frontend/web/data/). Se marca no vigente:
    # para publicarla como vigente, volver a correr Frontend/exportar_web.py con --vigente.
    exportar_web(dir_out, VERSION, "residuos")
    
    t_tot = time.time() - t0
    print(f"\n{'='*75}")
    print(f"🎉 PIPELINE DE GRAFO Y NO-PATRONES FINALIZADO CON ÉXITO EN {t_tot:.2f} SEGUNDOS")
    print(f"{'='*75}\n")


if __name__ == "__main__":
    main()
