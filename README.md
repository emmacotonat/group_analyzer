# Social Transparency Group Analyzer

A research-oriented group analyzer for a Sociology final degree project on **social transparency**.

This repository turns questionnaire data into a sociogram, network metrics, community detection, relational interpretation and research-ready outputs. It is inspired by classic sociograms, but designed as a more complete tool for studying how group relations become visible, invisible, central, peripheral, fragmented or mediated.

> Core idea: social transparency is not about exposing private life. It is about making the relational architecture of a group analytically observable, ethically and sociologically.

---

## What the project does

The pipeline takes a CSV/XLSX questionnaire export and produces:

1. A cleaned participant table.
2. A directed, weighted and multilayer relational graph.
3. A sociogram with interactive visualisation.
4. Node-level metrics: visibility, recognition, brokerage, embeddedness, isolation and community.
5. Group-level results: density, reciprocity, modularity, fragmentation, number of communities and centralisation proxies.
6. A research interpretation report in HTML.
7. Exportable `nodes.csv`, `edges.csv` and `summary.json` files for the TFG.

---

## Why this is useful for the TFG

For the TFG on **social transparency**, this tool can operationalise questions such as:

- Who is visible in the group and who remains structurally invisible?
- Which people connect otherwise separated subgroups?
- Are there cohesive communities or fragmented relational islands?
- Are perceived belonging and actual network position aligned?
- Where do conflict, avoidance or weak recognition appear?
- Which relations are central to the group but not obvious at first sight?
- How does the sociogram reveal the architecture of social perception?

The tool does not replace qualitative interpretation. It creates an analytical map that can be interpreted together with interviews, observation, field notes or open-ended questionnaire answers.

---

## Repository structure

```text
group_analyzer/
├── data/
│   ├── example_input.csv
│   └── social_transparency_example.csv
├── docs/
│   ├── questionnaire.md
│   ├── methodology.md
│   ├── outputs.md
│   └── ethics.md
├── output/
│   ├── nodes.csv
│   ├── edges.csv
│   ├── summary.json
│   └── report.html
├── src/
│   ├── load_data.py
│   ├── clean_data.py
│   ├── build_graph.py
│   ├── analyze_graph.py
│   ├── export_html.py
│   └── utils.py
├── main.py
└── requirements.txt
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

Place a questionnaire export in the `data/` folder and run:

```bash
python main.py
```

The script will automatically use the first `.csv`, `.xlsx` or `.xls` file found in `data/`.

For the TFG example dataset, keep `data/social_transparency_example.csv` as the only input file or replace it with the real Google Forms export.

---

## Recommended questionnaire columns

Minimum:

- `name`: participant name or pseudonym.
- `belonging_score`: perceived belonging from 0 to 10.
- `perceived_transparency`: how clearly the participant understands the group relations from 0 to 10.
- `relational_clarity`: how clear the participant feels their own position is from 0 to 10.
- `psychological_safety`: how safe the participant feels in the group from 0 to 10.

Relational nomination columns:

- `close_contacts`: people the participant feels closest to.
- `support_contacts`: people the participant would ask for support.
- `trust_contacts`: people the participant trusts.
- `collaboration_contacts`: people the participant would work with.
- `influence_contacts`: people the participant sees as influential.
- `information_contacts`: people who provide information or orientation.
- `conflict_contacts`: people with whom there is tension.
- `avoid_contacts`: people the participant tends to avoid.

Optional attributes:

- `gender`
- `age_band`
- `role`
- `location`
- `interests`
- `open_notes`

The old `relations_raw` column is still supported for compatibility.

---

## Main metrics

| Metric | Sociological interpretation |
|---|---|
| In-degree | Recognition received by others |
| Out-degree | Relational orientation toward others |
| Weighted in-degree | Intensity of received nominations |
| Betweenness | Brokerage and mediation between subgroups |
| PageRank | Recursive visibility or relational prestige |
| k-core | Embeddedness in the cohesive centre |
| Community | Meso-level relational cluster |
| Reciprocity | Mutual recognition |
| Isolation flag | Structural disconnection or missing recognition |
| Recognition gap | Difference between perceived position and received nominations |
| Transparency tension | Misalignment between subjective clarity and network position |

---

## Outputs

After running the pipeline:

```text
output/nodes.csv      # participant-level metrics
output/edges.csv      # relational nominations by layer
output/summary.json   # group-level results
output/report.html    # interactive sociological report
```

---

## TFG framing

Suggested methodological paragraph:

> This project operationalises social transparency as the analytical visibility of relational structures inside a group. Through a questionnaire based on relational nominations and perceived position, the tool builds a directed and weighted sociogram. Network metrics are then used not as neutral indicators of individual value, but as sociological traces of recognition, brokerage, cohesion, fragmentation and invisibility.

---

## Ethical note

This tool should be used with informed consent, anonymisation and careful interpretation. Network results can expose sensitive positions. The objective is not to rank people morally, but to understand relational structures and how they shape group experience.
