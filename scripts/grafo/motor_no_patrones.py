"""Motor de Detección de NO-PATRONES (Solution Gaps & Outliers).

Aplica análisis topológico sobre NetworkX y análisis de densidad vectorial con Scikit-learn
para cuantificar vacíos de mercado, soluciones infrecuentes y causas cuello de botella.
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, Any, List, Tuple
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN


def detectar_vacios_solucion(
    G: nx.MultiDiGraph,
    df_problemas: pd.DataFrame,
    matriz_similitud: np.ndarray,
    top_n: int = 15
) -> pd.DataFrame:
    """Calcula el 'Solution Gap Score' para cada problema del dataset.
    
    Identifica problemas graves o recurrentes que carecen de soluciones
    tanto topológicamente en el grafo como vectorialmente en el espacio semántico.
    """
    frecuencias_cat = df_problemas["tipo_problema"].value_counts(normalize=True).to_dict()
    max_similitudes = np.max(matriz_similitud, axis=1)  # Máxima afinidad con cualquier solución
    distancias_minimas = 1.0 - max_similitudes          # Distancia al vecino de solución más próximo
    
    resultados = []
    for idx, row in df_problemas.iterrows():
        node_id = f"P_{idx}"
        cat = row.get("tipo_problema") or "OTRO_PROBLEMA_RESIDUOS"
        frec_cat = frecuencias_cat.get(cat, 0.05)
        
        # Grado entrante de soluciones en el grafo
        aristas_entrantes_sol = [
            (u, v, data) for u, v, data in G.in_edges(node_id, data=True)
            if data.get("tipo") == "MITIGA_POTENCIALMENTE"
        ]
        in_degree_sol = len(aristas_entrantes_sol)
        sin_solucion_topologica = 1.0 if in_degree_sol == 0 else 0.0
        
        dist_vec = float(distancias_minimas[idx])
        sim_max = float(max_similitudes[idx])
        
        # Ponderación calibrada de Vacío (Gap Score de 0 a 100)
        # 50% distancia semántica + 30% orfandad topológica + 20% recurrencia de la categoría
        score_gap = (
            (dist_vec * 50.0) +
            (sin_solucion_topologica * 30.0) +
            (min(frec_cat * 5.0, 1.0) * 20.0)
        )
        
        # Solución más cercana
        idx_sol_cercana = int(np.argmax(matriz_similitud[idx]))
        nodo_sol_cercana = f"S_{idx_sol_cercana}"
        nom_sol_cercana = G.nodes[nodo_sol_cercana].get("nombre", "Ninguna") if nodo_sol_cercana in G else "Ninguna"
        
        resultados.append({
            "nodo_id": node_id,
            "titulo": row.get("titulo_problema") or "Sin título",
            "descripcion": row.get("descripcion_problema") or "",
            "categoria": cat,
            "ubicacion": row.get("ubicacion") or "No especificada",
            "causas_raiz": row.get("causas_raiz") or "",
            "afectados": row.get("afectados") or "",
            "gap_score": round(score_gap, 2),
            "distancia_solucion_mas_cercana": round(dist_vec, 4),
            "similitud_maxima": round(sim_max, 4),
            "soluciones_conectadas_grafo": in_degree_sol,
            "solucion_mas_proxima_nombre": nom_sol_cercana,
            "url_fuente": row.get("url") or ""
        })
        
    df_gaps = pd.DataFrame(resultados).sort_values(by="gap_score", ascending=False).reset_index(drop=True)
    return df_gaps.head(top_n)


def detectar_gemas_ocultas_soluciones(
    G: nx.MultiDiGraph,
    df_soluciones: pd.DataFrame,
    emb_soluciones: np.ndarray,
    matriz_similitud: np.ndarray,
    top_n: int = 15
) -> pd.DataFrame:
    """Detecta 'Gemas Ocultas' (Outliers de Innovación).
    
    Soluciones poco frecuentes, con enfoques tecnológicos atípicos
    que atienden nichos específicos de problemas que el resto del mercado ignora.
    """
    frecuencias_cat_sol = df_soluciones["tipo_solucion"].value_counts().to_dict()
    
    # Detección de densidad / outlierness con Local Outlier Factor
    n_vecinos = min(10, len(df_soluciones) - 1)
    lof = LocalOutlierFactor(n_neighbors=n_vecinos, metric="cosine")
    lof.fit(emb_soluciones)
    # Factor de anomalía negativo invertido: mayor valor = mayor singularidad
    singularidad = -lof.negative_outlier_factor_
    
    resultados = []
    for idx, row in df_soluciones.iterrows():
        node_id = f"S_{idx}"
        cat = row.get("tipo_solucion") or "OTRA_SOLUCION_RESIDUOS"
        frec_cat = frecuencias_cat_sol.get(cat, 1)
        
        # Problemas a los que esta solución conecta en el grafo
        aristas_salientes = [
            (u, v, data) for u, v, data in G.out_edges(node_id, data=True)
            if data.get("tipo") == "MITIGA_POTENCIALMENTE"
        ]
        num_problemas_conectados = len(aristas_salientes)
        
        # Promedio de similitud con los problemas que ataca
        sims_problemas = matriz_similitud[:, idx]
        sim_top_problemas = np.sort(sims_problemas)[-5:]  # Top 5 afinidades
        prom_afinidad_top = float(np.mean(sim_top_problemas))
        
        score_singularidad = float(singularidad[idx])
        # Ponderación: singularidad semántica + rareza de categoría + aplicabilidad
        es_rara = 1.0 if frec_cat <= 3 else (0.5 if frec_cat <= 10 else 0.1)
        score_gema = (score_singularidad * 40.0) + (es_rara * 35.0) + (prom_afinidad_top * 25.0)
        
        resultados.append({
            "nodo_id": node_id,
            "nombre": row.get("nombre_solucion") or "Sin nombre",
            "descripcion": row.get("descripcion_solucion") or "",
            "categoria": cat,
            "quien_impulsa": row.get("quien_impulsa") or "No especificado",
            "tipo_problema_objetivo": row.get("tipo_problema_objetivo") or "",
            "frecuencia_categoria": frec_cat,
            "score_gema_oculta": round(score_gema, 2),
            "singularidad_vectorial": round(score_singularidad, 3),
            "problemas_mitigables_en_grafo": num_problemas_conectados,
            "afinidad_semantica_promedio": round(prom_afinidad_top, 4),
            "url_fuente": row.get("url") or ""
        })
        
    df_gemas = pd.DataFrame(resultados).sort_values(by="score_gema_oculta", ascending=False).reset_index(drop=True)
    return df_gemas.head(top_n)


def detectar_causas_cuello_de_botella(
    G: nx.MultiDiGraph,
    top_n: int = 15
) -> pd.DataFrame:
    """Identifica Causas Raíz 'Cuello de Botella'.
    
    Causas con alta centralidad de problemas (muchos problemas las padecen),
    pero con nula o escasa oferta de soluciones vinculadas a ellos.
    """
    nodos_causas = [n for n, d in G.nodes(data=True) if d.get("tipo") == "CausaRaiz"]
    
    resultados = []
    for c_node in nodos_causas:
        nombre_causa = G.nodes[c_node].get("nombre", c_node)
        
        # Problemas que tienen esta causa raíz
        problemas_asociados = [u for u, v, d in G.in_edges(c_node, data=True) if d.get("tipo") == "CAUSADO_POR"]
        num_problemas = len(problemas_asociados)
        if num_problemas == 0:
            continue
            
        # Cuántas soluciones mitigan a alguno de estos problemas
        soluciones_cobertura = set()
        for p in problemas_asociados:
            for u, v, d in G.in_edges(p, data=True):
                if d.get("tipo") == "MITIGA_POTENCIALMENTE":
                    soluciones_cobertura.add(u)
                    
        num_soluciones = len(soluciones_cobertura)
        
        # Índice de desatención = problemas / (soluciones + 1)
        indice_desatencion = num_problemas / (num_soluciones + 1.0)
        
        # Tasa de cobertura de soluciones
        cobertura_pct = (num_soluciones / num_problemas) * 100.0 if num_problemas > 0 else 0.0
        
        resultados.append({
            "nodo_id": c_node,
            "causa_raiz": nombre_causa,
            "problemas_que_la_padecen": num_problemas,
            "soluciones_que_la_mitigan": num_soluciones,
            "indice_desatencion": round(indice_desatencion, 2),
            "cobertura_soluciones_pct": round(cobertura_pct, 1),
            "ejemplo_problema": G.nodes[problemas_asociados[0]].get("titulo", "") if problemas_asociados else ""
        })
        
    df_causas = pd.DataFrame(resultados).sort_values(by="indice_desatencion", ascending=False).reset_index(drop=True)
    return df_causas.head(top_n)


def ejecutar_analisis_no_patrones(
    G: nx.MultiDiGraph,
    df_problemas: pd.DataFrame,
    df_soluciones: pd.DataFrame,
    emb_soluciones: np.ndarray,
    matriz_similitud: np.ndarray
) -> Dict[str, pd.DataFrame]:
    """Orquesta la ejecución completa de los algoritmos de no-patrones."""
    print("🔍 Ejecutando análisis de NO-PATRONES...")
    
    df_gaps = detectar_vacios_solucion(G, df_problemas, matriz_similitud, top_n=20)
    print(f"   - {len(df_gaps)} Vacíos Críticos de Solución (Solution Gaps) identificados.")
    
    df_gemas = detectar_gemas_ocultas_soluciones(G, df_soluciones, emb_soluciones, matriz_similitud, top_n=20)
    print(f"   - {len(df_gemas)} Gemas Ocultas de Innovación detectadas.")
    
    df_cuellos = detectar_causas_cuello_de_botella(G, top_n=20)
    print(f"   - {len(df_cuellos)} Causas Raíz Cuello de Botella aisladas.")
    
    return {
        "vacios_solucion": df_gaps,
        "gemas_ocultas": df_gemas,
        "causas_cuello_botella": df_cuellos
    }
