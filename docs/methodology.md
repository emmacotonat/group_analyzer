# Methodology

This project operationalises **social transparency** as the analytical visibility of relational structures inside a group.

The tool is not meant to reveal private life or rank individuals. It is a research instrument for observing how relations, recognition, cohesion, brokerage and invisibility are distributed.

---

## 1. Theoretical framing

The TFG can define social transparency as:

> The degree to which the relational architecture of a group can be made observable, interpretable and discussable without reducing people to metrics.

This means that transparency is not only an individual perception. It is also a structural condition: some relations are visible, some are hidden, some actors are recognised, and others remain peripheral or invisible.

---

## 2. Data model

### Nodes

Nodes represent participants in the group.

Each participant can have attributes such as gender, role, age band, location, interests and subjective scores.

### Edges

Edges represent nominations made by one participant toward another.

The graph is:

- **directed**: A can nominate B even if B does not nominate A.
- **weighted**: earlier nominations receive more weight.
- **multilayer**: each relation type is preserved.
- **signed**: conflict and avoidance are treated as negative layers.

---

## 3. Relational layers

| Column | Layer | Interpretation |
|---|---|---|
| `close_contacts` | closeness | affective proximity |
| `support_contacts` | support | care, support and reliance |
| `trust_contacts` | trust | confidence and perceived reliability |
| `collaboration_contacts` | collaboration | practical or academic work preference |
| `influence_contacts` | influence | perceived capacity to shape the group |
| `information_contacts` | information | orientation and informal knowledge |
| `conflict_contacts` | conflict | tension or disagreement |
| `avoid_contacts` | avoidance | distance, discomfort or disconnection |

---

## 4. Metrics and sociological meaning

| Metric | Meaning in the TFG |
|---|---|
| In-degree | Recognition received from others |
| Out-degree | Relational orientation toward others |
| Weighted in-degree | Intensity of received recognition |
| Betweenness | Brokerage between subgroups |
| PageRank | Recursive visibility or prestige |
| Eigenvector centrality | Connection to already well-connected actors |
| k-core | Embeddedness in the cohesive centre |
| Community | Meso-level subgroup structure |
| Reciprocity | Mutual recognition |
| Isolation flag | Structural disconnection in observed data |
| Recognition gap | Misalignment between belonging and received nominations |
| Transparency tension | Misalignment between subjective transparency and structural recognition |

---

## 5. Interpretation strategy

The analysis should move through four levels:

1. **Descriptive level**: number of participants, ties, communities, density and reciprocity.
2. **Positional level**: who appears central, peripheral, brokered or isolated.
3. **Perceptual level**: how subjective scores align or misalign with network position.
4. **Critical level**: what remains invisible, biased, missing or ethically sensitive.

---

## 6. Suggested research questions

- How does the sociogram make visible the relational architecture of the group?
- Which actors are recognised, central, peripheral or structurally invisible?
- Are subjective perceptions of belonging aligned with relational position?
- Do informal communities correspond to visible subgroups?
- Which actors mediate between otherwise separated clusters?
- What are the ethical limits of making group relations visible?

---

## 7. Limitations

- Questionnaire nominations depend on memory, trust and willingness to answer.
- Non-response can distort the graph.
- Centrality is not the same as power in every context.
- Communities are algorithmic partitions, not automatically real social groups.
- Conflict and avoidance data are sensitive and should be optional.
- Network data should be complemented with qualitative interpretation.

---

## 8. Suggested TFG chapter structure

1. Introduction: why social transparency matters.
2. Theoretical framework: relational sociology, sociograms, visibility and power.
3. Methodology: questionnaire, graph construction and metrics.
4. Results: sociogram, centralities, communities and perception scores.
5. Discussion: what the graph reveals and what it cannot reveal.
6. Ethical reflection: anonymity, consent and algorithmic interpretation.
7. Conclusions: social transparency as a methodological and sociological concept.
