"""
Módulo para construir el grafo dirigido de relaciones
"""

import pandas as pd
import networkx as nx
from pathlib import Path
from src.utils import normalize_text, fuzzy_match_name, parse_relations


def build_graph(df):
    """
    Construye un grafo dirigido a partir de las relaciones
    
    Args:
        df: DataFrame con datos limpios
        
    Returns:
        Tupla (G, nodes_df, edges_df) donde:
        - G: Grafo dirigido de NetworkX
        - nodes_df: DataFrame con información de nodos
        - edges_df: DataFrame con información de aristas
    """
    G = nx.DiGraph()
    
    # Crear diccionario de nombres normalizados a IDs
    name_to_id = {}
    name_list = []
    
    for _, row in df.iterrows():
        name = row['name']
        person_id = row['id']
        name_normalized = normalize_text(name)
        
        name_to_id[name_normalized] = person_id
        name_list.append(name)
        
        # Agregar nodo al grafo
        G.add_node(person_id, **row.to_dict())
    
    # Procesar relaciones
    edges_data = []
    
    for _, row in df.iterrows():
        source_id = row['id']
        source_name = row['name']
        relations_raw = row.get('relations_raw', '')
        
        if pd.isna(relations_raw) or not relations_raw:
            continue
        
        # Parsear relaciones
        relations = parse_relations(relations_raw)
        
        if not relations:
            continue
        
        # Asignar pesos según orden
        for idx, relation_name in enumerate(relations):
            if idx == 0:
                weight = 3
            elif idx == 1:
                weight = 2
            else:
                weight = 1
            
            # Buscar el ID correspondiente usando fuzzy matching
            matched_name, score = fuzzy_match_name(relation_name, name_list, threshold=70)
            
            if matched_name:
                matched_normalized = normalize_text(matched_name)
                target_id = name_to_id.get(matched_normalized)
                
                if target_id and target_id != source_id:  # Evitar auto-referencias
                    # Agregar arista al grafo (sumar pesos si ya existe)
                    if G.has_edge(source_id, target_id):
                        G[source_id][target_id]['weight'] += weight
                    else:
                        G.add_edge(source_id, target_id, weight=weight)
                    
                    # Agregar a edges_data (se agrupará después)
                    edges_data.append({
                        'source': source_id,
                        'target': target_id,
                        'weight': weight,
                        'source_name': source_name,
                        'target_name': matched_name,
                        'match_score': score
                    })
    
    # Crear DataFrame de nodos
    nodes_data = []
    for node_id in G.nodes():
        node_attrs = G.nodes[node_id]
        nodes_data.append(node_attrs)
    
    nodes_df = pd.DataFrame(nodes_data)
    
    # Crear DataFrame de aristas
    if edges_data:
        edges_df = pd.DataFrame(edges_data)
        # Agrupar por source-target y sumar pesos
        edges_df = edges_df.groupby(['source', 'target', 'source_name', 'target_name']).agg({
            'weight': 'sum',
            'match_score': 'mean'
        }).reset_index()
    else:
        edges_df = pd.DataFrame(columns=['source', 'target', 'weight', 'source_name', 'target_name', 'match_score'])
    
    return G, nodes_df, edges_df


def export_nodes_edges(nodes_df, edges_df, output_dir):
    """
    Exporta los DataFrames de nodos y aristas a CSV
    
    Args:
        nodes_df: DataFrame con información de nodos
        edges_df: DataFrame con información de aristas
        output_dir: Directorio de salida
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Exportar nodos
    nodes_export = nodes_df.copy()
    # Eliminar columnas que no son necesarias en el CSV
    if 'interests_list' in nodes_export.columns:
        nodes_export = nodes_export.drop(columns=['interests_list'])
    nodes_export.to_csv(output_dir / 'nodes.csv', index=False, encoding='utf-8-sig')
    
    # Exportar aristas
    edges_df.to_csv(output_dir / 'edges.csv', index=False, encoding='utf-8-sig')

