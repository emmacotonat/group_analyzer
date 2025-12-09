"""
Proyecto Group Analyzer
Analiza relaciones y comunidades en grupos a partir de datos de Google Forms
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.load_data import load_data
from src.clean_data import clean_data
from src.build_graph import build_graph, export_nodes_edges
from src.analyze_graph import analyze_graph
from src.export_html import export_html


def main():
    """Función principal que orquesta todo el proceso"""
    
    # Configurar rutas
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"
    
    # Crear directorio de salida si no existe
    output_dir.mkdir(exist_ok=True)
    
    # Buscar archivo de entrada
    input_files = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls")) + list(data_dir.glob("*.csv"))
    
    if not input_files:
        print(f"Error: No se encontró ningún archivo de entrada en {data_dir}")
        print("Por favor, coloca un archivo .xlsx, .xls o .csv en la carpeta 'data/'")
        return
    
    input_file = input_files[0]
    print(f"Cargando datos desde: {input_file}")
    
    # 1. Cargar datos
    print("\n[1/5] Cargando datos...")
    df = load_data(input_file)
    print(f"   ✓ Cargados {len(df)} registros")
    
    # 2. Limpiar y normalizar datos
    print("\n[2/5] Limpiando y normalizando datos...")
    df_clean = clean_data(df)
    print(f"   ✓ Datos normalizados: {len(df_clean)} personas únicas")
    
    # 3. Construir grafo
    print("\n[3/5] Construyendo grafo dirigido...")
    G, nodes_df, edges_df = build_graph(df_clean)
    print(f"   ✓ Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    
    # 4. Analizar grafo
    print("\n[4/5] Analizando grafo...")
    nodes_df_enriched = analyze_graph(G, nodes_df)
    print(f"   ✓ Análisis completado: métricas calculadas")
    
    # 5. Exportar resultados
    print("\n[5/5] Exportando resultados...")
    export_nodes_edges(nodes_df_enriched, edges_df, output_dir)
    export_html(G, nodes_df_enriched, edges_df, output_dir)
    print(f"   ✓ Archivos guardados en: {output_dir}")
    
    print("\n" + "="*50)
    print("¡Proceso completado exitosamente!")
    print("="*50)
    print(f"\nArchivos generados:")
    print(f"  - {output_dir / 'nodes.csv'}")
    print(f"  - {output_dir / 'edges.csv'}")
    print(f"  - {output_dir / 'report.html'}")


if __name__ == "__main__":
    main()

