"""
Módulo para analizar el grafo y calcular métricas
"""

import pandas as pd
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from community import community_louvain


def analyze_graph(G, nodes_df):
    """
    Analiza el grafo y enriquece el DataFrame de nodos con métricas
    
    Args:
        G: Grafo dirigido de NetworkX
        nodes_df: DataFrame con información de nodos
        
    Returns:
        DataFrame enriquecido con métricas de red
    """
    if G.number_of_nodes() == 0:
        return nodes_df
    
    nodes_df = nodes_df.copy()
    
    # Convertir a grafo no dirigido para algunas métricas
    G_undirected = G.to_undirected()
    
    # 1. Grado, in-degree, out-degree
    print("   - Calculando grados...")
    nodes_df['degree'] = [G.degree(node_id) for node_id in nodes_df['id']]
    nodes_df['in_degree'] = [G.in_degree(node_id) for node_id in nodes_df['id']]
    nodes_df['out_degree'] = [G.out_degree(node_id) for node_id in nodes_df['id']]
    
    # 2. Centralidad eigenvector (en grafo no dirigido)
    print("   - Calculando centralidad eigenvector...")
    try:
        eigenvector = nx.eigenvector_centrality(G_undirected, max_iter=1000)
        nodes_df['eigenvector_centrality'] = nodes_df['id'].map(eigenvector).fillna(0)
    except:
        nodes_df['eigenvector_centrality'] = 0
    
    # 3. Comunidades mediante Louvain
    print("   - Detectando comunidades (Louvain)...")
    try:
        # Convertir a grafo no dirigido con pesos
        G_undirected_weighted = G_undirected.copy()
        for u, v in G_undirected_weighted.edges():
            if G.has_edge(u, v):
                G_undirected_weighted[u][v]['weight'] = G[u][v].get('weight', 1)
            elif G.has_edge(v, u):
                G_undirected_weighted[u][v]['weight'] = G[v][u].get('weight', 1)
            else:
                G_undirected_weighted[u][v]['weight'] = 1
        
        partition = community_louvain.best_partition(G_undirected_weighted, weight='weight')
        nodes_df['community'] = nodes_df['id'].map(partition).fillna(-1)
    except Exception as e:
        print(f"     ⚠ Error en detección de comunidades: {e}")
        nodes_df['community'] = 0
    
    # 4. Similitud entre intereses (cosine similarity)
    print("   - Calculando similitud de intereses...")
    try:
        # Preparar intereses como texto
        interests_text = nodes_df['interests_list'].apply(
            lambda x: ' '.join(x) if isinstance(x, list) else ''
        )
        
        # Vectorizar intereses
        vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
        interests_matrix = vectorizer.fit_transform(interests_text)
        
        # Calcular similitud coseno promedio con todos los demás
        similarity_matrix = cosine_similarity(interests_matrix)
        
        # Para cada nodo, calcular similitud promedio con otros nodos
        nodes_df['interests_similarity_avg'] = [
            np.mean([similarity_matrix[i][j] for j in range(len(nodes_df)) if i != j])
            if len(nodes_df) > 1 else 0
            for i in range(len(nodes_df))
        ]
    except Exception as e:
        print(f"     ⚠ Error en similitud de intereses: {e}")
        nodes_df['interests_similarity_avg'] = 0
    
    # 5. Métricas adicionales
    print("   - Calculando métricas adicionales...")
    
    # PageRank (en grafo dirigido)
    try:
        pagerank = nx.pagerank(G, max_iter=1000)
        nodes_df['pagerank'] = nodes_df['id'].map(pagerank).fillna(0)
    except:
        nodes_df['pagerank'] = 0
    
    # Betweenness centrality
    try:
        betweenness = nx.betweenness_centrality(G_undirected)
        nodes_df['betweenness_centrality'] = nodes_df['id'].map(betweenness).fillna(0)
    except:
        nodes_df['betweenness_centrality'] = 0
    
    # Closeness centrality
    try:
        closeness = nx.closeness_centrality(G_undirected)
        nodes_df['closeness_centrality'] = nodes_df['id'].map(closeness).fillna(0)
    except:
        nodes_df['closeness_centrality'] = 0
    
    return nodes_df

