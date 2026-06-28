"""Network analysis for the Social Transparency Group Analyzer."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.utils import percentile_rank, zscore

try:
    from community import community_louvain
except Exception:  # pragma: no cover
    community_louvain = None


def _positive_projection(G: nx.DiGraph) -> nx.Graph:
    """Create an undirected graph using only positive relational weight."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes(data=True))

    for u, v, data in G.edges(data=True):
        weight = float(data.get("positive_weight", data.get("total_weight", 1.0)))
        if weight <= 0:
            continue
        if H.has_edge(u, v):
            H[u][v]["weight"] += weight
        else:
            H.add_edge(u, v, weight=weight)
    return H


def _detect_communities(H: nx.Graph) -> tuple[dict, float]:
    """Detect communities with Louvain when available, otherwise greedy modularity."""
    if H.number_of_nodes() == 0 or H.number_of_edges() == 0:
        return {node: 0 for node in H.nodes()}, 0.0

    if community_louvain is not None:
        partition = community_louvain.best_partition(H, weight="weight")
        try:
            modularity = community_louvain.modularity(partition, H, weight="weight")
        except Exception:
            modularity = 0.0
        return partition, float(modularity)

    communities = list(nx.algorithms.community.greedy_modularity_communities(H, weight="weight"))
    partition = {}
    for index, community in enumerate(communities):
        for node in community:
            partition[node] = index
    modularity = nx.algorithms.community.modularity(H, communities, weight="weight") if communities else 0.0
    return partition, float(modularity)


def _assign_role(row: pd.Series) -> str:
    """Assign an interpretable sociological role based on relative metrics."""
    if row.get("degree", 0) == 0:
        return "isolated"
    if row.get("betweenness_percentile", 0) >= 0.85:
        return "broker"
    if row.get("in_degree_percentile", 0) >= 0.85:
        return "recognised_actor"
    if row.get("out_degree_percentile", 0) >= 0.85:
        return "relational_seeker"
    if row.get("core_number_percentile", 0) >= 0.75:
        return "cohesive_core"
    if row.get("degree_percentile", 0) <= 0.25:
        return "peripheral"
    return "ordinary_member"


def _interest_similarity(nodes_df: pd.DataFrame) -> pd.Series:
    """Average cosine similarity of each participant's interests to the group."""
    if "interests_list" not in nodes_df.columns or len(nodes_df) <= 1:
        return pd.Series([0.0] * len(nodes_df), index=nodes_df.index)

    text = nodes_df["interests_list"].apply(lambda values: " ".join(values) if isinstance(values, list) else "")
    if text.str.strip().eq("").all():
        return pd.Series([0.0] * len(nodes_df), index=nodes_df.index)

    try:
        matrix = TfidfVectorizer(max_features=200).fit_transform(text)
        sim = cosine_similarity(matrix)
        averages = []
        for i in range(len(nodes_df)):
            others = [sim[i][j] for j in range(len(nodes_df)) if i != j]
            averages.append(float(np.mean(others)) if others else 0.0)
        return pd.Series(averages, index=nodes_df.index)
    except Exception:
        return pd.Series([0.0] * len(nodes_df), index=nodes_df.index)


def analyze_graph(G: nx.DiGraph, nodes_df: pd.DataFrame, edges_df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    """Compute node-level and group-level metrics.

    Metrics are designed for sociological interpretation, especially visibility,
    recognition, brokerage, cohesion, fragmentation and subjective transparency.
    """
    nodes_df = nodes_df.copy()
    if G.number_of_nodes() == 0:
        return nodes_df, {}

    H = _positive_projection(G)

    nodes_df["degree"] = [G.degree(node_id) for node_id in nodes_df["id"]]
    nodes_df["in_degree"] = [G.in_degree(node_id) for node_id in nodes_df["id"]]
    nodes_df["out_degree"] = [G.out_degree(node_id) for node_id in nodes_df["id"]]
    nodes_df["weighted_in_degree"] = [G.in_degree(node_id, weight="total_weight") for node_id in nodes_df["id"]]
    nodes_df["weighted_out_degree"] = [G.out_degree(node_id, weight="total_weight") for node_id in nodes_df["id"]]
    nodes_df["positive_received"] = [sum(data.get("positive_weight", 0) for _, _, data in G.in_edges(node_id, data=True)) for node_id in nodes_df["id"]]
    nodes_df["negative_received"] = [sum(data.get("negative_weight", 0) for _, _, data in G.in_edges(node_id, data=True)) for node_id in nodes_df["id"]]

    try:
        nodes_df["pagerank"] = nodes_df["id"].map(nx.pagerank(G, weight="total_weight", max_iter=1000)).fillna(0.0)
    except Exception:
        nodes_df["pagerank"] = 0.0

    try:
        nodes_df["betweenness_centrality"] = nodes_df["id"].map(nx.betweenness_centrality(H, weight="weight")).fillna(0.0)
    except Exception:
        nodes_df["betweenness_centrality"] = 0.0

    try:
        nodes_df["closeness_centrality"] = nodes_df["id"].map(nx.closeness_centrality(H)).fillna(0.0)
    except Exception:
        nodes_df["closeness_centrality"] = 0.0

    try:
        nodes_df["eigenvector_centrality"] = nodes_df["id"].map(nx.eigenvector_centrality(H, weight="weight", max_iter=1000)).fillna(0.0)
    except Exception:
        nodes_df["eigenvector_centrality"] = 0.0

    try:
        nodes_df["core_number"] = nodes_df["id"].map(nx.core_number(H)).fillna(0).astype(int)
    except Exception:
        nodes_df["core_number"] = 0

    partition, modularity = _detect_communities(H)
    nodes_df["community"] = nodes_df["id"].map(partition).fillna(0).astype(int)

    # Mutual recognition: how many of a participant's ties are reciprocated.
    mutual_counts = {}
    for node in G.nodes:
        count = 0
        for neighbour in set(G.successors(node)).union(set(G.predecessors(node))):
            if G.has_edge(node, neighbour) and G.has_edge(neighbour, node):
                count += 1
        mutual_counts[node] = count
    nodes_df["mutual_ties"] = nodes_df["id"].map(mutual_counts).fillna(0).astype(int)
    nodes_df["is_isolated"] = nodes_df["degree"] == 0

    # Relative positions.
    for column in ["degree", "in_degree", "out_degree", "weighted_in_degree", "betweenness_centrality", "core_number"]:
        nodes_df[f"{column}_percentile"] = percentile_rank(nodes_df[column])

    nodes_df["interest_similarity_avg"] = _interest_similarity(nodes_df)

    # TFG-specific interpretive indicators.
    nodes_df["recognition_z"] = zscore(nodes_df["weighted_in_degree"])
    if "perceived_transparency" in nodes_df.columns:
        nodes_df["perceived_transparency_z"] = zscore(nodes_df["perceived_transparency"])
        nodes_df["transparency_tension"] = nodes_df["recognition_z"] - nodes_df["perceived_transparency_z"]
    else:
        nodes_df["perceived_transparency_z"] = 0.0
        nodes_df["transparency_tension"] = nodes_df["recognition_z"]

    if "belonging_score" in nodes_df.columns:
        nodes_df["belonging_z"] = zscore(nodes_df["belonging_score"])
        nodes_df["recognition_gap"] = nodes_df["recognition_z"] - nodes_df["belonging_z"]
    else:
        nodes_df["belonging_z"] = 0.0
        nodes_df["recognition_gap"] = nodes_df["recognition_z"]

    nodes_df["sociological_role"] = nodes_df.apply(_assign_role, axis=1)

    density = nx.density(G)
    reciprocity = nx.reciprocity(G) if G.number_of_edges() else 0.0
    components = list(nx.connected_components(H)) if H.number_of_nodes() else []
    largest_component_share = max((len(component) for component in components), default=0) / max(G.number_of_nodes(), 1)

    relation_counts = {}
    unmatched_nominations = 0
    if edges_df is not None and not edges_df.empty:
        relation_counts = edges_df[edges_df["matched"] == True]["relation_type"].value_counts().to_dict()
        unmatched_nominations = int((edges_df["matched"] == False).sum())

    summary = {
        "n_nodes": int(G.number_of_nodes()),
        "n_edges_aggregated": int(G.number_of_edges()),
        "n_edge_nominations": int(len(edges_df)) if edges_df is not None else int(G.number_of_edges()),
        "density": float(density),
        "reciprocity": float(reciprocity) if reciprocity is not None else 0.0,
        "n_communities": int(nodes_df["community"].nunique()),
        "modularity": float(modularity),
        "largest_component_share": float(largest_component_share),
        "isolated_nodes": int(nodes_df["is_isolated"].sum()),
        "average_belonging": float(nodes_df["belonging_score"].mean()) if "belonging_score" in nodes_df.columns else None,
        "average_perceived_transparency": float(nodes_df["perceived_transparency"].mean()) if "perceived_transparency" in nodes_df.columns else None,
        "average_relational_clarity": float(nodes_df["relational_clarity"].mean()) if "relational_clarity" in nodes_df.columns else None,
        "average_psychological_safety": float(nodes_df["psychological_safety"].mean()) if "psychological_safety" in nodes_df.columns else None,
        "relation_counts": relation_counts,
        "unmatched_nominations": unmatched_nominations,
        "top_brokers": nodes_df.sort_values("betweenness_centrality", ascending=False)[["id", "display_name", "betweenness_centrality"]].head(5).to_dict("records"),
        "top_recognised": nodes_df.sort_values("weighted_in_degree", ascending=False)[["id", "display_name", "weighted_in_degree"]].head(5).to_dict("records"),
    }

    return nodes_df, summary


def export_summary(summary: dict, output_dir: str | Path) -> None:
    """Export group-level results as JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "summary.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
