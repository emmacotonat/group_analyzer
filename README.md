# Group Analyzer

Sistema de análisis de relaciones y comunidades en grupos a partir de datos exportados de Google Forms.

## 📋 Descripción

Este proyecto analiza las relaciones entre miembros de un grupo, construye un grafo dirigido de conexiones, detecta comunidades y genera visualizaciones interactivas.

## 🚀 Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
group_analyzer/
├── data/                    # Archivos de entrada (CSV/XLSX)
│   └── example_input.csv    # Archivo de ejemplo
├── src/                     # Código fuente
│   ├── load_data.py        # Carga de datos
│   ├── clean_data.py       # Limpieza y normalización
│   ├── build_graph.py      # Construcción del grafo
│   ├── analyze_graph.py    # Análisis y métricas
│   ├── export_html.py      # Exportación HTML
│   └── utils.py            # Utilidades
├── output/                  # Archivos de salida
│   ├── nodes.csv           # Nodos del grafo
│   ├── edges.csv           # Aristas del grafo
│   └── report.html         # Informe interactivo
├── requirements.txt
└── main.py                 # Script principal
```

## 📊 Formato de Datos de Entrada

El archivo de entrada (CSV o XLSX) debe contener las siguientes columnas:

- **name**: Nombre completo de la persona
- **nickname**: Apodo o nombre corto
- **gender**: Género (M/F)
- **birth_year**: Año de nacimiento
- **integration_score**: Puntuación de integración (0-10)
- **location**: Ubicación
- **interests**: Intereses separados por comas (ej: "Música,Deportes,Literatura")
- **relations_raw**: Nombres de personas relacionadas, separados por comas (ej: "Juan Pérez,Ana López")

## 🎯 Uso

1. Coloca tu archivo CSV o XLSX en la carpeta `data/`
2. Ejecuta el script principal:
```bash
python main.py
```

El sistema:
1. Cargará y limpiará los datos
2. Normalizará nombres usando fuzzy matching
3. Construirá el grafo dirigido de relaciones
4. Calculará métricas de red (grado, centralidad, comunidades)
5. Generará archivos de salida en `output/`

## 📈 Métricas Calculadas

- **Grado**: Número total de conexiones
- **In-degree**: Conexiones entrantes
- **Out-degree**: Conexiones salientes
- **Centralidad Eigenvector**: Importancia en la red
- **Comunidades (Louvain)**: Grupos detectados
- **Similitud de Intereses**: Similitud coseno basada en intereses
- **PageRank**: Importancia basada en enlaces
- **Betweenness Centrality**: Centralidad de intermediación
- **Closeness Centrality**: Centralidad de cercanía

## 📤 Archivos de Salida

- **nodes.csv**: Información completa de cada persona con métricas
- **edges.csv**: Relaciones dirigidas con pesos
- **report.html**: Visualización interactiva del grafo con PyVis

## 🔧 Dependencias

- pandas: Manipulación de datos
- networkx: Análisis de grafos
- pyvis: Visualización interactiva
- rapidfuzz: Fuzzy matching de nombres
- scikit-learn: Similitud de intereses
- python-louvain: Detección de comunidades
- openpyxl: Lectura de archivos Excel

## 📝 Notas

- Los nombres se normalizan automáticamente (sin tildes, minúsculas)
- El fuzzy matching une nombres similares (ej: "María" y "Maria")
- Los pesos de las relaciones se asignan según el orden: primero=3, segundo=2, resto=1
- El informe HTML es interactivo: puedes arrastrar nodos y hacer zoom

