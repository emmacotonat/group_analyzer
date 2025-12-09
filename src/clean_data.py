"""
Módulo para limpiar y normalizar datos
"""

import pandas as pd
from src.utils import normalize_text, fuzzy_match_name, parse_interests


def clean_data(df):
    """
    Limpia y normaliza los datos del DataFrame
    
    Args:
        df: DataFrame con datos crudos
        
    Returns:
        DataFrame limpio y normalizado con ID único para cada persona
    """
    df_clean = df.copy()
    
    # Normalizar nombres
    print("   - Normalizando nombres...")
    df_clean['name'] = df_clean['name'].apply(normalize_text)
    df_clean['nickname'] = df_clean['nickname'].apply(normalize_text)
    
    # Limpiar otros campos de texto
    df_clean['location'] = df_clean['location'].apply(normalize_text)
    
    # Procesar intereses
    print("   - Procesando intereses...")
    df_clean['interests_list'] = df_clean['interests'].apply(parse_interests)
    
    # Convertir tipos numéricos
    df_clean['birth_year'] = pd.to_numeric(df_clean['birth_year'], errors='coerce')
    df_clean['integration_score'] = pd.to_numeric(df_clean['integration_score'], errors='coerce')
    
    # Aplicar fuzzy matching para unificar nombres duplicados
    print("   - Aplicando fuzzy matching para unificar nombres...")
    unique_names = df_clean['name'].unique()
    name_mapping = {}
    
    for name in unique_names:
        if not name:  # Saltar nombres vacíos
            continue
        
        # Buscar si hay un nombre similar ya procesado
        matched_name = None
        for existing_name in name_mapping.values():
            matched, score = fuzzy_match_name(name, [existing_name], threshold=85)
            if matched:
                matched_name = existing_name
                break
        
        if matched_name:
            name_mapping[name] = matched_name
        else:
            name_mapping[name] = name
    
    # Aplicar mapeo de nombres
    df_clean['name'] = df_clean['name'].map(name_mapping).fillna(df_clean['name'])
    
    # Eliminar duplicados basados en nombre normalizado
    print("   - Eliminando duplicados...")
    df_clean = df_clean.drop_duplicates(subset=['name'], keep='first')
    
    # Generar ID único para cada persona
    print("   - Generando IDs únicos...")
    df_clean = df_clean.reset_index(drop=True)
    df_clean['id'] = df_clean.index + 1
    df_clean['id'] = 'P' + df_clean['id'].astype(str).str.zfill(4)
    
    # Reordenar columnas
    columns_order = ['id', 'name', 'nickname', 'gender', 'birth_year',
                     'integration_score', 'location', 'interests', 'interests_list', 'relations_raw']
    df_clean = df_clean[[col for col in columns_order if col in df_clean.columns]]
    
    return df_clean

