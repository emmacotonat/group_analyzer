"""Clean and normalise questionnaire data for social transparency analysis."""

from __future__ import annotations

import pandas as pd

from src.utils import RELATION_LAYERS, SCORE_COLUMNS, display_text, normalize_text, parse_interests, safe_numeric


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned participant table with stable IDs and parsed attributes."""
    df_clean = df.copy()

    df_clean["display_name"] = df_clean["display_name"].apply(display_text)
    df_clean["name"] = df_clean["name"].apply(display_text)
    df_clean["name_normalized"] = df_clean["name"].apply(normalize_text)

    # Remove empty identities and duplicated questionnaire rows.
    df_clean = df_clean[df_clean["name_normalized"] != ""].copy()
    df_clean = df_clean.drop_duplicates(subset=["name_normalized"], keep="first")
    df_clean = df_clean.reset_index(drop=True)

    # Stable participant identifiers. The public output can use these IDs instead of names.
    if "participant_id" not in df_clean.columns:
        df_clean["participant_id"] = [f"P{i:04d}" for i in range(1, len(df_clean) + 1)]
    else:
        df_clean["participant_id"] = df_clean["participant_id"].fillna("").astype(str)
        missing = df_clean["participant_id"].str.strip() == ""
        df_clean.loc[missing, "participant_id"] = [f"P{i:04d}" for i in range(1, missing.sum() + 1)]

    df_clean["id"] = df_clean["participant_id"]

    # Normalise common optional attributes.
    for column in ["gender", "age_band", "role", "location", "group_context"]:
        if column in df_clean.columns:
            df_clean[column] = df_clean[column].apply(display_text)

    if "interests" in df_clean.columns:
        df_clean["interests_list"] = df_clean["interests"].apply(parse_interests)
    else:
        df_clean["interests"] = ""
        df_clean["interests_list"] = [[] for _ in range(len(df_clean))]

    for column in SCORE_COLUMNS:
        if column in df_clean.columns:
            df_clean[column] = safe_numeric(df_clean[column])

    # Ensure relation columns exist, so downstream code can rely on a stable schema.
    for column in RELATION_LAYERS:
        if column not in df_clean.columns:
            df_clean[column] = ""

    preferred_order = [
        "id",
        "participant_id",
        "display_name",
        "name",
        "name_normalized",
        "gender",
        "age_band",
        "role",
        "location",
        "group_context",
        "belonging_score",
        "perceived_transparency",
        "relational_clarity",
        "psychological_safety",
        "integration_score",
        "isolation_score",
        "interests",
        "interests_list",
        *RELATION_LAYERS.keys(),
        "open_notes",
    ]

    existing = [column for column in preferred_order if column in df_clean.columns]
    remaining = [column for column in df_clean.columns if column not in existing]
    return df_clean[existing + remaining]
