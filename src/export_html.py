"""Export an interactive HTML report for the Social Transparency Group Analyzer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pyvis.network import Network


ROLE_DESCRIPTIONS = {
    "broker": "connects otherwise separated parts of the group",
    "recognised_actor": "receives many nominations and is highly visible",
    "relational_seeker": "actively nominates others and orients toward the group",
    "cohesive_core": "belongs to the dense relational centre",
    "peripheral": "has a relatively low number of ties",
    "isolated": "has no observed ties in the questionnaire data",
    "ordinary_member": "does not occupy an extreme network position",
}


def _fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def export_html(G, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, output_dir: str | Path, summary: dict | None = None) -> None:
    """Generate the interactive report."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    summary = summary or {}

    if G.number_of_nodes() == 0:
        (output_dir / "report.html").write_text("<h1>No data available</h1>", encoding="utf-8")
        return

    net = Network(height="760px", width="100%", directed=True, notebook=False, bgcolor="#ffffff")
    net.set_options(
        """
        {
          "nodes": {
            "font": {"size": 14, "face": "Inter"},
            "scaling": {"min": 12, "max": 42}
          },
          "edges": {
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.5}},
            "smooth": {"type": "dynamic"}
          },
          "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -55,
              "centralGravity": 0.01,
              "springLength": 120,
              "springConstant": 0.08
            },
            "stabilization": {"iterations": 250}
          }
        }
        """
    )

    palette = [
        "#7c3aed",
        "#db2777",
        "#2563eb",
        "#059669",
        "#ea580c",
        "#0891b2",
        "#9333ea",
        "#be123c",
    ]

    node_lookup = nodes_df.set_index("id").to_dict("index")

    for _, row in nodes_df.iterrows():
        node_id = row["id"]
        label = row.get("display_name", node_id)
        community = int(row.get("community", 0)) if pd.notna(row.get("community", 0)) else 0
        role = row.get("sociological_role", "ordinary_member")
        size = 12 + float(row.get("degree_percentile", 0.2)) * 30
        border_width = 4 if role in {"broker", "recognised_actor", "cohesive_core"} else 1

        title = f"""
        <strong>{label}</strong><br>
        ID: {node_id}<br>
        Community: {community}<br>
        Role: {role}<br>
        In-degree: {_fmt(row.get('in_degree'))}<br>
        Out-degree: {_fmt(row.get('out_degree'))}<br>
        Betweenness: {_fmt(row.get('betweenness_centrality'))}<br>
        PageRank: {_fmt(row.get('pagerank'))}<br>
        Recognition gap: {_fmt(row.get('recognition_gap'))}<br>
        Transparency tension: {_fmt(row.get('transparency_tension'))}
        """

        net.add_node(
            node_id,
            label=label,
            size=size,
            color={"background": palette[community % len(palette)], "border": "#111827"},
            borderWidth=border_width,
            title=title,
        )

    for u, v, data in G.edges(data=True):
        total_weight = float(data.get("total_weight", 1.0))
        negative_weight = float(data.get("negative_weight", 0.0))
        edge_color = "#ef4444" if negative_weight > 0 and negative_weight >= total_weight / 2 else "#64748b"
        relation_types = ", ".join(data.get("relation_types", []))
        net.add_edge(
            u,
            v,
            value=max(1.0, total_weight),
            width=max(1.0, min(6.0, total_weight)),
            color=edge_color,
            title=f"Relations: {relation_types}<br>Total weight: {_fmt(total_weight)}",
        )

    graph_html = net.generate_html()
    body_start = graph_html.find("<body>") + len("<body>")
    body_end = graph_html.find("</body>")
    graph_body = graph_html[body_start:body_end] if body_start > -1 and body_end > -1 else graph_html

    top_recognised = nodes_df.sort_values("weighted_in_degree", ascending=False).head(8)
    top_brokers = nodes_df.sort_values("betweenness_centrality", ascending=False).head(8)
    top_tension = nodes_df.sort_values("transparency_tension", ascending=False).head(8)

    def table(df: pd.DataFrame, columns: list[str]) -> str:
        rows = []
        for _, item in df.iterrows():
            rows.append("<tr>" + "".join(f"<td>{_fmt(item.get(col))}</td>" for col in columns) + "</tr>")
        header = "<tr>" + "".join(f"<th>{col}</th>" for col in columns) + "</tr>"
        return f"<table>{header}{''.join(rows)}</table>"

    role_rows = []
    for role, description in ROLE_DESCRIPTIONS.items():
        count = int((nodes_df["sociological_role"] == role).sum()) if "sociological_role" in nodes_df else 0
        role_rows.append(f"<tr><td>{role}</td><td>{count}</td><td>{description}</td></tr>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Transparency Group Analyzer</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --ink: #111827;
            --muted: #64748b;
            --card: #ffffff;
            --line: #e5e7eb;
            --accent: #7c3aed;
            --accent2: #db2777;
        }}
        body {{
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg);
            color: var(--ink);
        }}
        .hero {{
            padding: 48px 6vw;
            background: radial-gradient(circle at top left, #fce7f3, transparent 32%), linear-gradient(135deg, #111827, #312e81 55%, #831843);
            color: white;
        }}
        .hero h1 {{ margin: 0; font-size: clamp(2rem, 4vw, 4rem); letter-spacing: -0.04em; }}
        .hero p {{ max-width: 850px; color: #e5e7eb; font-size: 1.1rem; line-height: 1.7; }}
        .wrap {{ padding: 32px 6vw 64px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin: 24px 0; }}
        .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 20px; box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06); }}
        .metric {{ font-size: 2rem; font-weight: 750; color: var(--accent); }}
        .label {{ color: var(--muted); margin-top: 6px; }}
        h2 {{ margin-top: 42px; font-size: 1.6rem; }}
        .graph {{ background: white; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 16px; overflow: hidden; margin: 14px 0 28px; }}
        th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--line); text-align: left; font-size: 0.92rem; }}
        th {{ background: #f1f5f9; color: #334155; }}
        .note {{ color: var(--muted); line-height: 1.7; max-width: 980px; }}
        .pill {{ display: inline-block; background: #ede9fe; color: #5b21b6; border-radius: 999px; padding: 6px 10px; margin: 4px; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <section class="hero">
        <h1>Social Transparency Group Analyzer</h1>
        <p>An interactive sociogram and analytical report for studying recognition, visibility, brokerage, cohesion and invisibility inside a group.</p>
    </section>

    <main class="wrap">
        <div class="grid">
            <div class="card"><div class="metric">{summary.get('n_nodes', len(nodes_df))}</div><div class="label">participants</div></div>
            <div class="card"><div class="metric">{summary.get('n_edge_nominations', len(edges_df))}</div><div class="label">relational nominations</div></div>
            <div class="card"><div class="metric">{_fmt(summary.get('density'), 3)}</div><div class="label">network density</div></div>
            <div class="card"><div class="metric">{_fmt(summary.get('reciprocity'), 3)}</div><div class="label">reciprocity</div></div>
            <div class="card"><div class="metric">{summary.get('n_communities', 0)}</div><div class="label">communities</div></div>
            <div class="card"><div class="metric">{summary.get('isolated_nodes', 0)}</div><div class="label">isolated nodes</div></div>
        </div>

        <h2>Interactive sociogram</h2>
        <p class="note">Node colour represents detected community. Node size reflects relational connectedness. Darker borders mark especially relevant positions such as brokers, recognised actors or cohesive-core members.</p>
        <div class="graph">{graph_body}</div>

        <h2>Interpretive roles</h2>
        <table><tr><th>Role</th><th>Count</th><th>Interpretation</th></tr>{''.join(role_rows)}</table>

        <h2>Most recognised actors</h2>
        <p class="note">High received nominations indicate visibility or recognition. This should not be interpreted as moral superiority or objective importance.</p>
        {table(top_recognised, ['display_name', 'weighted_in_degree', 'in_degree', 'community', 'sociological_role'])}

        <h2>Potential brokers</h2>
        <p class="note">High betweenness suggests actors who may connect otherwise separated subgroups. In the TFG, this is useful for discussing mediation, hidden coordination and relational power.</p>
        {table(top_brokers, ['display_name', 'betweenness_centrality', 'degree', 'community', 'sociological_role'])}

        <h2>Transparency tension</h2>
        <p class="note">This indicator compares received recognition with subjective perceived transparency. High positive values may indicate actors who are structurally visible but whose position is not necessarily perceived as clear or transparent.</p>
        {table(top_tension, ['display_name', 'transparency_tension', 'recognition_gap', 'perceived_transparency', 'belonging_score'])}

        <h2>Relation layers</h2>
        <p>{''.join(f'<span class="pill">{key}: {value}</span>' for key, value in summary.get('relation_counts', {}).items())}</p>

        <h2>Research caution</h2>
        <p class="note">This report should be read as a sociological instrument, not as a ranking of people. The graph depends on questionnaire design, participation, memory, trust and willingness to disclose relations. Missing ties are also social data, but they must be interpreted carefully.</p>
    </main>
</body>
</html>"""

    (output_dir / "report.html").write_text(html, encoding="utf-8")
