"""
Módulo para exportar el informe HTML con visualización interactiva
"""

import pandas as pd
from pathlib import Path
from pyvis.network import Network
import networkx as nx


def export_html(G, nodes_df, edges_df, output_dir):
    """
    Genera un informe HTML con visualización interactiva del grafo
    
    Args:
        G: Grafo dirigido de NetworkX
        nodes_df: DataFrame con información de nodos enriquecida
        edges_df: DataFrame con información de aristas
        output_dir: Directorio de salida
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if G.number_of_nodes() == 0:
        # Generar HTML vacío
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Group Analyzer - Reporte</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Group Analyzer - Reporte</h1>
    <p class="error">No hay datos para visualizar.</p>
</body>
</html>
"""
        with open(output_dir / 'report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return
    
    # Crear red PyVis
    net = Network(
        height='800px',
        width='100%',
        directed=True,
        notebook=False
    )
    
    # Configurar opciones
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 12,
          "face": "Arial"
        },
        "scaling": {
          "min": 10,
          "max": 30
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "iterations": 200
        }
      }
    }
    """)
    
    # Obtener número de comunidades para colorear
    if 'community' in nodes_df.columns:
        num_communities = nodes_df['community'].nunique()
        # Generar colores para comunidades
        import colorsys
        colors = []
        for i in range(num_communities):
            hue = i / num_communities
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
            color = f"rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})"
            colors.append(color)
    else:
        colors = ['#97c2fc']
    
    # Agregar nodos
    for _, row in nodes_df.iterrows():
        node_id = str(row['id'])
        label = row.get('name', node_id)
        
        # Tamaño basado en grado
        size = max(10, min(30, row.get('degree', 5) * 2))
        
        # Color basado en comunidad
        if 'community' in row:
            community_id = int(row['community']) if pd.notna(row['community']) else 0
            color = colors[community_id % len(colors)]
        else:
            color = '#97c2fc'
        
        # Tooltip con información
        title = f"<b>{label}</b><br>"
        title += f"ID: {node_id}<br>"
        if 'degree' in row:
            title += f"Grado: {row['degree']}<br>"
        if 'community' in row:
            title += f"Comunidad: {row['community']}<br>"
        if 'eigenvector_centrality' in row:
            title += f"Centralidad: {row['eigenvector_centrality']:.3f}<br>"
        
        net.add_node(
            node_id,
            label=label,
            size=size,
            color=color,
            title=title
        )
    
    # Agregar aristas
    for _, row in edges_df.iterrows():
        source = str(row['source'])
        target = str(row['target'])
        weight = row.get('weight', 1)
        
        # Ancho de línea basado en peso
        width = max(1, min(5, weight))
        
        net.add_edge(
            source,
            target,
            value=weight,
            width=width,
            title=f"Peso: {weight}"
        )
    
    # Generar HTML
    html_file = output_dir / 'report.html'
    
    # Generar contenido HTML completo con tabla de resultados
    html_content = generate_html_report(net, nodes_df, edges_df)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_html_report(net, nodes_df, edges_df):
    """
    Genera el contenido HTML completo del reporte
    
    Args:
        net: Objeto Network de PyVis
        nodes_df: DataFrame con nodos
        edges_df: DataFrame con aristas
        
    Returns:
        String con el HTML completo
    """
    # Generar HTML del grafo
    net_html = net.generate_html()
    
    # Extraer solo el contenido del body del grafo
    import re
    graph_match = re.search(r'<body>(.*?)</body>', net_html, re.DOTALL)
    graph_content = graph_match.group(1) if graph_match else ""
    
    # Extraer scripts y estilos
    scripts_match = re.findall(r'<script[^>]*>.*?</script>', net_html, re.DOTALL)
    styles_match = re.findall(r'<style[^>]*>.*?</style>', net_html, re.DOTALL)
    
    # Preparar tabla de nodos
    table_rows = []
    nodes_sorted = nodes_df.sort_values('degree', ascending=False)
    
    for _, row in nodes_sorted.head(50).iterrows():  # Mostrar top 50
        name = row.get('name', 'N/A')
        degree = row.get('degree', 0)
        community = row.get('community', 'N/A')
        eigenvector = row.get('eigenvector_centrality', 0)
        
        table_rows.append(f"""
        <tr>
            <td>{name}</td>
            <td>{degree}</td>
            <td>{community}</td>
            <td>{eigenvector:.3f}</td>
        </tr>
        """)
    
    # HTML completo
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Group Analyzer - Reporte</title>
    {''.join(styles_match)}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .graph-container {{
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Group Analyzer</h1>
            <p>Análisis de Relaciones y Comunidades</p>
        </div>
        <div class="content">
            <div class="section">
                <h2>📈 Estadísticas Generales</h2>
                <div class="stats">
                    <div class="stat-card">
                        <h3>{len(nodes_df)}</h3>
                        <p>Personas</p>
                    </div>
                    <div class="stat-card">
                        <h3>{len(edges_df)}</h3>
                        <p>Relaciones</p>
                    </div>
                    <div class="stat-card">
                        <h3>{nodes_df['community'].nunique() if 'community' in nodes_df.columns else 0}</h3>
                        <p>Comunidades</p>
                    </div>
                    <div class="stat-card">
                        <h3>{nodes_df['degree'].mean():.1f if 'degree' in nodes_df.columns else 0}</h3>
                        <p>Grado Promedio</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🕸️ Grafo de Relaciones</h2>
                <p>Arrastra los nodos para interactuar. El color indica la comunidad y el tamaño el grado de conexión.</p>
                <div class="graph-container">
                    {graph_content}
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Tabla de Resultados</h2>
                <p>Top 50 personas ordenadas por grado de conexión:</p>
                <table>
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Grado</th>
                            <th>Comunidad</th>
                            <th>Centralidad Eigenvector</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {''.join(scripts_match)}
</body>
</html>"""
    
    return html

