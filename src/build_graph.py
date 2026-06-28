"""Build directed and multilayer graphs from questionnaire nominations."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd

from src.utils import RELATION_LAYERS, fuzzy_match_name, parse_relations, ranked_weight


def build_graph(df: pd.DataFrame) -> tuple[nx.DiGraph, pd.DataFrame, pd.DataFrame]:
    """Build a directed weighted graph from relational questionnaire columns.

    The graph aggregates several relational layers, while `edges_df` preserves
    one row per nomination and relation type.
    """
    G = nx.DiGraph()

    name_to_id = dict(zip(df["display_name"], df["id"]))
    participant_names = list(name_to_id.keys())

    for _, row in df.iterrows():
        attrs = row.to_dict()
        G.add_node(row["id"], **attrs)

    edges_data: list[dict] = []

    for _, row in df.iterrows():
        source_id = row["id"]
        source_name = row["display_name"]

        for column, metadata in RELATION_LAYERS.items():
            raw_value = row.get(column, "")
            nominations = parse_relations(raw_value)

            for position, nomination in enumerate(nominations):
                matched_name, score = fuzzy_match_name(nomination, participant_names, threshold=70)
                if not matched_name:
                    edges_data.append(
                        {
                            "source": source_id,
                            "target": None,
                            "source_name": source_name,
                            "target_name": nomination,
                            "relation_type": metadata["label"],
                            "relation_column": column,
                            "weight": ranked_weight(metadata["base_weight"], position),
                            "signed_weight": ranked_weight(metadata["base_weight"], position) * metadata["valence"],
                            "valence": metadata["valence"],
                            "rank_position": position + 1,
                            "match_score": score,
                            "matched": False,
                        }
                    )
                    continue

                target_id = name_to_id.get(matched_name)
                if not target_id or target_id == source_id:
                    continue

                weight = ranked_weight(metadata["base_weight"], position)
                signed_weight = weight * metadata["valence"]

                if not G.has_edge(source_id, target_id):
                    G.add_edge(
                        source_id,
                        target_id,
                        total_weight=0.0,
                        positive_weight=0.0,
                        negative_weight=0.0,
                        signed_weight=0.0,
                        relation_types=[],
                    )

                edge = G[source_id][target_id]
                edge["total_weight"] += weight
                edge["signed_weight"] += signed_weight
                if metadata["valence"] > 0:
                    edge["positive_weight"] += weight
                else:
                    edge["negative_weight"] += weight
                if metadata["label"] not in edge["relation_types"]:
                    edge["relation_types"].append(metadata["label"])

                edges_data.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "source_name": source_name,
                        "target_name": matched_name,
                        "relation_type": metadata["label"],
                        "relation_column": column,
                        "weight": weight,
                        "signed_weight": signed_weight,
                        "valence": metadata["valence"],
                        "rank_position": position + 1,
                        "match_score": score,
                        "matched": True,
                    }
                )

    nodes_df = pd.DataFrame([G.nodes[node_id] for node_id in G.nodes])
    edges_df = pd.DataFrame(edges_data)

    if edges_df.empty:
        edges_df = pd.DataFrame(
            columns=[
                "source",
                "target",
                "source_name",
                "target_name",
                "relation_type",
                "relation_column",
                "weight",
                "signed_weight",
                "valence",
                "rank_position",
                "match_score",
                "matched",
            ]
        )

    return G, nodes_df, edges_df


def export_nodes_edges(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, output_dir: str | Path) -> None:
    """Export node and edge tables as CSV files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    nodes_export = nodes_df.copy()
    if "interests_list" in nodes_export.columns:
        nodes_export["interests_list"] = nodes_export["interests_list"].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")

    nodes_export.to_csv(output_dir / "nodes.csv", index=False, encoding="utf-8-sig")
    edges_df.to_csv(output_dir / "edges.csv", index=False, encoding="utf-8-sig")
