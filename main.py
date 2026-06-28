"""Main pipeline for the Social Transparency Group Analyzer.

The script loads a questionnaire export, builds a multilayer sociogram,
computes sociological network metrics and exports research-ready outputs.
"""

from __future__ import annotations

from pathlib import Path

from src.analyze_graph import analyze_graph, export_summary
from src.build_graph import build_graph, export_nodes_edges
from src.clean_data import clean_data
from src.export_html import export_html
from src.load_data import load_data


def find_input_file(data_dir: Path) -> Path | None:
    """Return the first available questionnaire file in the data directory."""
    files = sorted(list(data_dir.glob("*.csv")) + list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls")))
    if not files:
        return None

    # Prefer the Social Transparency example or a user-provided file with a clear name.
    priority = [file for file in files if "social_transparency" in file.name.lower()]
    return priority[0] if priority else files[0]


def main() -> None:
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    input_file = find_input_file(data_dir)
    if input_file is None:
        print(f"No input file found in {data_dir}")
        print("Add a CSV/XLSX questionnaire export to the data folder and run again.")
        return

    print("Social Transparency Group Analyzer")
    print("==================================")
    print(f"Input file: {input_file}")

    print("\n[1/5] Loading questionnaire data...")
    raw_df = load_data(input_file)
    print(f"Loaded rows: {len(raw_df)}")

    print("\n[2/5] Cleaning participant data...")
    clean_df = clean_data(raw_df)
    print(f"Unique participants: {len(clean_df)}")

    print("\n[3/5] Building multilayer sociogram...")
    graph, nodes_df, edges_df = build_graph(clean_df)
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} aggregated edges")
    print(f"Nominations: {len(edges_df)} relational nominations")

    print("\n[4/5] Computing network and transparency metrics...")
    enriched_nodes_df, summary = analyze_graph(graph, nodes_df, edges_df)
    print(f"Detected communities: {summary.get('n_communities', 0)}")
    print(f"Density: {summary.get('density', 0):.3f}")
    print(f"Reciprocity: {summary.get('reciprocity', 0):.3f}")

    print("\n[5/5] Exporting results...")
    export_nodes_edges(enriched_nodes_df, edges_df, output_dir)
    export_summary(summary, output_dir)
    export_html(graph, enriched_nodes_df, edges_df, output_dir, summary)

    print("\nDone. Generated files:")
    print(f"- {output_dir / 'nodes.csv'}")
    print(f"- {output_dir / 'edges.csv'}")
    print(f"- {output_dir / 'summary.json'}")
    print(f"- {output_dir / 'report.html'}")


if __name__ == "__main__":
    main()
