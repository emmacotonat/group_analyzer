# Outputs

Running `python main.py` generates four main files in the `output/` folder.

---

## `nodes.csv`

Participant-level table with original questionnaire fields and computed metrics.

Important columns:

| Column | Meaning |
|---|---|
| `id` | Participant identifier |
| `display_name` | Name or pseudonym used in the report |
| `degree` | Total number of observed ties |
| `in_degree` | Number of incoming nominations |
| `out_degree` | Number of outgoing nominations |
| `weighted_in_degree` | Intensity of received nominations |
| `positive_received` | Positive relational weight received |
| `negative_received` | Conflict/avoidance weight received |
| `pagerank` | Recursive visibility |
| `betweenness_centrality` | Brokerage position |
| `closeness_centrality` | Reachability |
| `eigenvector_centrality` | Prestige by association |
| `core_number` | Cohesive embeddedness |
| `community` | Detected community |
| `mutual_ties` | Number of reciprocal relations |
| `is_isolated` | Whether the participant has no observed ties |
| `recognition_gap` | Difference between received recognition and belonging |
| `transparency_tension` | Difference between structural recognition and perceived transparency |
| `sociological_role` | Interpretable role assigned by the tool |

---

## `edges.csv`

Nomination-level table. Each row is one relational nomination from the questionnaire.

Important columns:

| Column | Meaning |
|---|---|
| `source` | Participant making the nomination |
| `target` | Participant receiving the nomination |
| `relation_type` | Layer: support, trust, conflict, etc. |
| `weight` | Weight of the nomination |
| `signed_weight` | Positive or negative weight |
| `valence` | Positive relation = 1; negative relation = -1 |
| `rank_position` | Order in which the person was nominated |
| `match_score` | Fuzzy matching confidence |
| `matched` | Whether the nomination matched an existing participant |

---

## `summary.json`

Group-level results.

Main fields:

- `n_nodes`
- `n_edges_aggregated`
- `n_edge_nominations`
- `density`
- `reciprocity`
- `n_communities`
- `modularity`
- `largest_component_share`
- `isolated_nodes`
- `average_belonging`
- `average_perceived_transparency`
- `average_relational_clarity`
- `average_psychological_safety`
- `relation_counts`
- `unmatched_nominations`
- `top_brokers`
- `top_recognised`

---

## `report.html`

Interactive report with:

- summary cards
- interactive sociogram
- role distribution
- most recognised actors
- potential brokers
- transparency tension table
- relation layer counts
- research caution section

Open it in a browser after running the pipeline.

---

## How to use the outputs in the TFG

Use `summary.json` for general descriptive results, `nodes.csv` for tables and selected cases, `edges.csv` for methodological transparency, and `report.html` for visual interpretation.

Suggested writing formula:

> The sociogram shows not only who is connected, but also how recognition, support, trust, influence and avoidance are distributed. These metrics are interpreted as traces of relational visibility rather than objective measures of personal value.
