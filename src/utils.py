"""
Funciones auxiliares para el proyecto
"""

import re
import unicodedata
import pandas as pd
from rapidfuzz import fuzz, process


def normalize_text(text):
    """
    Normaliza texto: elimina tildes, convierte a minúsculas y limpia espacios
    
    Args:
        text: Texto a normalizar (puede ser str, float, NaN)
        
    Returns:
        Texto normalizado o string vacío si es NaN
    """
    if pd.isna(text) or text is None:
        return ""
    
    # Convertir a string
    text = str(text)
    
    # Eliminar tildes
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def fuzzy_match_name(name, name_list, threshold=80):
    """
    Encuentra el mejor match para un nombre usando fuzzy matching
    
    Args:
        name: Nombre a buscar
        name_list: Lista de nombres disponibles
        threshold: Umbral mínimo de similitud (0-100)
        
    Returns:
        Tupla (nombre_match, score) o (None, 0) si no hay match
    """
    if not name or not name_list:
        return None, 0
    
    name_normalized = normalize_text(name)
    
    # Buscar mejor match
    result = process.extractOne(
        name_normalized,
        [normalize_text(n) for n in name_list],
        scorer=fuzz.ratio
    )
    
    if result and result[1] >= threshold:
        # Encontrar el nombre original correspondiente
        matched_normalized = result[0]
        for original_name in name_list:
            if normalize_text(original_name) == matched_normalized:
                return original_name, result[1]
    
    return None, 0


def parse_interests(interests_str):
    """
    Parsea una cadena de intereses separados por comas
    
    Args:
        interests_str: String con intereses separados por comas
        
    Returns:
        Lista de intereses normalizados
    """
    if pd.isna(interests_str) or not interests_str:
        return []
    
    interests = [normalize_text(i.strip()) for i in str(interests_str).split(',')]
    interests = [i for i in interests if i]  # Eliminar vacíos
    
    return interests


def parse_relations(relations_str):
    """
    Parsea una cadena de relaciones separadas por comas
    
    Args:
        relations_str: String con nombres separados por comas
        
    Returns:
        Lista de nombres normalizados
    """
    if pd.isna(relations_str) or not relations_str:
        return []
    
    relations = [normalize_text(r.strip()) for r in str(relations_str).split(',')]
    relations = [r for r in relations if r]  # Eliminar vacíos
    
    return relations

