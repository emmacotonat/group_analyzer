# Questionnaire Design

This questionnaire is designed for a TFG on **social transparency**. It collects two kinds of information:

1. **Relational nominations**: who is connected to whom, and through which type of relation.
2. **Subjective perception**: how participants experience belonging, clarity, safety and visibility inside the group.

The goal is not to expose private relations. The goal is to make the relational architecture of a group analytically observable.

---

## Recommended introduction for participants

> This questionnaire asks about group relations in order to build an anonymised sociogram for academic research. The objective is to understand patterns of recognition, support, trust, collaboration, influence and possible disconnection inside the group. Your answers will be treated confidentially and interpreted sociologically, not as personal judgements.

---

## Consent

Recommended column: `consent`

Question:

> Do you consent to participate in this research questionnaire?

Accepted values in the code: `yes`, `true`, `1`, `sí`, `si`, `y`.

---

## Identification

Recommended columns:

- `name`
- `display_name`
- `participant_id`

For real research, use pseudonyms or participant codes whenever possible.

Example questions:

- Write your name or agreed pseudonym.
- Write the name you want to appear in the sociogram.

---

## Basic attributes

Optional columns:

- `gender`
- `age_band`
- `role`
- `location`
- `group_context`
- `interests`

These attributes are not mandatory. Only collect them if they are theoretically relevant and ethically justified.

---

## Subjective perception scales

Use a 0 to 10 scale.

### `belonging_score`

> From 0 to 10, how much do you feel you belong to this group?

### `perceived_transparency`

> From 0 to 10, how clearly do you understand the informal relations and dynamics of this group?

### `relational_clarity`

> From 0 to 10, how clear is your own position inside this group?

### `psychological_safety`

> From 0 to 10, how safe do you feel expressing yourself in this group?

### `isolation_score`

> From 0 to 10, how isolated do you feel inside this group?

---

## Relational nomination questions

Participants can nominate several people separated by commas.

### `close_contacts`

> Which people in the group do you feel closest to?

### `support_contacts`

> Which people would you ask for emotional, practical or academic support?

### `trust_contacts`

> Which people do you trust most inside the group?

### `collaboration_contacts`

> Which people would you choose to work with?

### `influence_contacts`

> Which people do you perceive as influential in the group?

### `information_contacts`

> Which people help you understand what is happening in the group?

### `conflict_contacts`

> Are there people with whom you perceive tension or conflict? Only answer if you feel comfortable.

### `avoid_contacts`

> Are there people you tend to avoid? Only answer if you feel comfortable.

---

## Open-ended questions

Recommended column: `open_notes`

Possible question:

> Is there anything about the group dynamics that is not visible from the outside but you think is important?

Other possible questions:

- What makes someone visible in this group?
- Are there people whose work or presence is important but not recognised?
- Are there informal subgroups?
- Are there hidden tensions or silences?
- What would make the group more transparent, safe or inclusive?

---

## Google Forms structure

Use short answer questions for names and nomination fields. Use linear scale questions for perception scores. Export the form as CSV or XLSX and place it inside the `data/` folder.

Recommended file name:

```text
social_transparency_questionnaire.csv
```

---

## Ethical cautions

- Do not force participants to answer conflict or avoidance questions.
- Do not publish identifiable sociograms without consent.
- Avoid presenting centrality as a ranking of personal worth.
- Explain that network metrics are analytical indicators, not moral judgements.
- Consider anonymising names before sharing results.
