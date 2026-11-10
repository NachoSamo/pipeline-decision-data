"""Módulo de Construcción del Grafo de Conocimiento Heterogéneo.

Construye un nx.MultiDiGraph a partir del Parquet clasificado, generando entidades,
relaciones explícitas y aristas semánticas continuas calculadas por proximidad vectorial.
"""

import re
import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, Any, Tuple, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
import faiss


def limpiar_texto_entidad(texto: Optional[str]) -> str:
    """Limpia y estandariza nombres de entidades para evitar duplicados sintácticos."""
    if not texto or not isinstance(texto, str):
        return ""
    limpio = re.sub(r"\s+", " ", texto).strip()
    return limpio


def parsear_lista_elementos(cadena_raw: Optional[str]) -> List[str]:
    """Separa cadenas delimitadas por ';' o comas en lista de entidades limpias."""
    if not cadena_raw or not isinstance(cadena_raw, str):
        return []
    partes = re.split(r"[;,]\s*", cadena_raw)
    elementos = []
    for p in partes:
        p_clean = limpiar_texto_entidad(p)
        if len(p_clean) >= 3 and p_clean.lower() not in ("none", "null", "nan", "no aplica", "n/a"):
            elementos.append(p_clean)
    return elementos


def generar_embeddings_textos(
    textos: List[str],
    n_componentes: int = 64
) -> Tuple[np.ndarray, Any]:
    """Genera representaciones semánticas densas L2-normalizadas con TF-IDF + SVD (LSA)."""
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=4000,
        sublinear_tf=True,
        strip_accents="unicode"
    )
    matriz_tfidf = vectorizer.fit_transform(textos)
    
    n_comp = min(n_componentes, matriz_tfidf.shape[1] - 1, len(textos) - 1)
    if n_comp > 4:
        svd = TruncatedSVD(n_components=n_comp, random_state=42)
        embeddings = svd.fit_transform(matriz_tfidf)
    else:
        embeddings = matriz_tfidf.toarray()
        
    embeddings_norm = normalize(embeddings, norm="l2")
    return embeddings_norm, vectorizer


PATRON_RUIDO_POLICIAL = re.compile(
    r"\b(asesinato|homicidio|femicidio|crimen|cuerpo calcinado|cad[aá]ver|feto|autopsia|balead[oa]|detenid[oa]|prisi[oó]n|imputad[oa]|forense|disparos?|robo|abuso)\b",
    re.IGNORECASE
)


def es_ruido_no_ambiental(fila: pd.Series) -> bool:
    """Detecta si un registro clasificado es crónica policial, judicial o forense accidental."""
    texto = (
        f"{fila.get('titulo_problema', '')} "
        f"{fila.get('descripcion_problema', '')} "
        f"{fila.get('nombre_solucion', '')} "
        f"{fila.get('descripcion_solucion', '')}"
    )
    return bool(PATRON_RUIDO_POLICIAL.search(texto))


def construir_grafo_conocimiento(
    df: pd.DataFrame,
    umbral_similitud_arista: float = 0.30,
    top_k_vecinos: int = 3
) -> Tuple[nx.MultiDiGraph, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """Construye el grafo heterogéneo NetworkX y calcula las métricas semánticas.
    
    Retorna:
        (G, df_problemas, df_soluciones, emb_problemas, emb_soluciones, matriz_similitud)
    """
    G = nx.MultiDiGraph()
    
    # 0. Saneamiento temático: purga de crónica policial / judicial accidental
    mascara_ruido = df.apply(es_ruido_no_ambiental, axis=1)
    df_limpio = df[~mascara_ruido].copy()
    if mascara_ruido.sum() > 0:
        print(f"🧹 Saneamiento de dominio: {mascara_ruido.sum()} registros policiales/forenses purgados.")
    
    # 1. Separar problemas y soluciones
    df_problemas = df_limpio[df_limpio["es_problema"] == True].copy().reset_index(drop=True)
    df_soluciones = df_limpio[df_limpio["es_solucion"] == True].copy().reset_index(drop=True)
    
    print(f"📊 Dataset cargado: {len(df_problemas):,} Problemas | {len(df_soluciones):,} Soluciones")
    
    # 2. Generar embeddings semánticos
    textos_prob = [
        str(r.get("texto_embedding_problema") or f"{r.get('titulo_problema', '')}. {r.get('descripcion_problema', '')}")
        for _, r in df_problemas.iterrows()
    ]
    textos_sol = [
        str(r.get("texto_embedding_solucion") or f"{r.get('nombre_solucion', '')}. {r.get('descripcion_solucion', '')}")
        for _, r in df_soluciones.iterrows()
    ]
    
    todos_textos = textos_prob + textos_sol
    emb_todos, _ = generar_embeddings_textos(todos_textos, n_componentes=64)
    emb_problemas = emb_todos[:len(df_problemas)]
    emb_soluciones = emb_todos[len(df_problemas):]
    
    # Matriz de similitud coseno (N_problemas x N_soluciones)
    matriz_similitud = cosine_similarity(emb_problemas, emb_soluciones)
    
    # 3. Incorporar Nodos de Problemas
    for idx, row in df_problemas.iterrows():
        node_id = f"P_{idx}"
        cat = row.get("tipo_problema") or "OTRO_PROBLEMA_RESIDUOS"
        G.add_node(
            node_id,
            tipo="Problema",
            titulo=row.get("titulo_problema") or "Problema sin título",
            descripcion=row.get("descripcion_problema") or "",
            categoria=cat,
            ubicacion=row.get("ubicacion") or "No especificada",
            alcance=row.get("alcance_geo") or "No especificado",
            fuente=row.get("fuente") or "",
            fecha=row.get("fecha") or "",
            id_original=row.get("id_original") or ""
        )
        
        # Categoría
        nodo_cat = f"CAT_{cat}"
        G.add_node(nodo_cat, tipo="Categoria", nombre=cat)
        G.add_edge(node_id, nodo_cat, tipo="PERTENECE_A")
        
        # Causas Raíz
        causas = parsear_lista_elementos(row.get("causas_raiz"))
        for c in causas:
            nodo_causa = f"CR_{c.lower()}"
            G.add_node(nodo_causa, tipo="CausaRaiz", nombre=c)
            G.add_edge(node_id, nodo_causa, tipo="CAUSADO_POR")
            
        # Actores / Afectados
        actores = parsear_lista_elementos(row.get("afectados"))
        for a in actores:
            nodo_actor = f"ACT_{a.lower()}"
            G.add_node(nodo_actor, tipo="Actor", nombre=a)
            G.add_edge(node_id, nodo_actor, tipo="AFECTA_A")
            
        # Ubicación
        if row.get("ubicacion") and str(row.get("ubicacion")).strip().lower() not in ("none", "nan", ""):
            loc = str(row.get("ubicacion")).strip()
            nodo_loc = f"LOC_{loc.lower()}"
            G.add_node(nodo_loc, tipo="Ubicacion", nombre=loc)
            G.add_edge(node_id, nodo_loc, tipo="UBICADO_EN")

    # 4. Incorporar Nodos de Soluciones
    for idx, row in df_soluciones.iterrows():
        node_id = f"S_{idx}"
        cat = row.get("tipo_solucion") or "OTRA_SOLUCION_RESIDUOS"
        G.add_node(
            node_id,
            tipo="Solucion",
            nombre=row.get("nombre_solucion") or "Solución sin nombre",
            descripcion=row.get("descripcion_solucion") or "",
            categoria=cat,
            quien_impulsa=row.get("quien_impulsa") or "",
            tipo_objetivo=row.get("tipo_problema_objetivo") or "",
            ubicacion=row.get("ubicacion") or "No especificada",
            alcance=row.get("alcance_geo") or "No especificado",
            fuente=row.get("fuente") or "",
            fecha=row.get("fecha") or "",
            id_original=row.get("id_original") or ""
        )
        
        # Categoría
        nodo_cat = f"CAT_{cat}"
        G.add_node(nodo_cat, tipo="Categoria", nombre=cat)
        G.add_edge(node_id, nodo_cat, tipo="PERTENECE_A")
        
        # Impulsor
        impulsores = parsear_lista_elementos(row.get("quien_impulsa"))
        for imp in impulsores:
            nodo_actor = f"ACT_{imp.lower()}"
            G.add_node(nodo_actor, tipo="Actor", nombre=imp)
            G.add_edge(node_id, nodo_actor, tipo="IMPULSADA_POR")
            
        # Categoría Objetivo que mitiga
        obj = row.get("tipo_problema_objetivo")
        if obj and str(obj).strip().lower() not in ("none", "nan", ""):
            nodo_cat_obj = f"CAT_{str(obj).strip()}"
            G.add_node(nodo_cat_obj, tipo="Categoria", nombre=str(obj).strip())
            G.add_edge(node_id, nodo_cat_obj, tipo="APUNTA_A_CATEGORIA")

    # 5. Aristas Semánticas de Mitigación (Indexación con FAISS)
    index_sol = faiss.IndexFlatIP(emb_soluciones.shape[1])
    index_sol.add(emb_soluciones.astype(np.float32))
    
    # Buscar top_k soluciones más afines para cada problema
    distancias, indices = index_sol.search(emb_problemas.astype(np.float32), top_k_vecinos)
    
    total_aristas_semanticas = 0
    for idx_prob in range(len(df_problemas)):
        id_p = f"P_{idx_prob}"
        for rank in range(top_k_vecinos):
            sim = float(distancias[idx_prob][rank])
            idx_sol = int(indices[idx_prob][rank])
            id_s = f"S_{idx_sol}"
            
            # Si supera el umbral de afinidad, se crea la arista semántica
            if sim >= umbral_similitud_arista:
                G.add_edge(
                    id_s,
                    id_p,
                    tipo="MITIGA_POTENCIALMENTE",
                    similitud=round(sim, 4),
                    distancia=round(1.0 - sim, 4)
                )
                total_aristas_semanticas += 1

    print(f"🕸️ Grafo construido:")
    print(f"   - Nodos totales: {G.number_of_nodes():,}")
    print(f"   - Aristas totales: {G.number_of_edges():,} (incluye {total_aristas_semanticas} aristas semánticas)")
    
    return G, df_problemas, df_soluciones, emb_problemas, emb_soluciones, matriz_similitud
