"""
Módulo para cargar datos desde archivos CSV/XLSX
"""

import pandas as pd
from pathlib import Path


def load_data(file_path):
    """
    Carga datos desde un archivo CSV o XLSX
    
    Args:
        file_path: Ruta al archivo de entrada
        
    Returns:
        DataFrame con los datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no tiene el formato esperado
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    
    # Determinar extensión y cargar
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")
    
    # Validar columnas requeridas
    required_columns = [
        'name', 'nickname', 'gender', 'birth_year',
        'integration_score', 'location', 'interests', 'relations_raw'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Faltan las siguientes columnas requeridas: {', '.join(missing_columns)}"
        )
    
    return df

