"""Utility functions for the Social Transparency Group Analyzer."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

import pandas as pd
from rapidfuzz import fuzz, process


RELATION_LAYERS = {
    "close_contacts": {"label": "closeness", "base_weight": 3.0, "valence": 1},
    "support_contacts": {"label": "support", "base_weight": 2.7, "valence": 1},
    "trust_contacts": {"label": "trust", "base_weight": 2.7, "valence": 1},
    "collaboration_contacts": {"label": "collaboration", "base_weight": 2.2, "valence": 1},
    "influence_contacts": {"label": "influence", "base_weight": 2.0, "valence": 1},
    "information_contacts": {"label": "information", "base_weight": 1.7, "valence": 1},
    "conflict_contacts": {"label": "conflict", "base_weight": 1.5, "valence": -1},
    "avoid_contacts": {"label": "avoidance", "base_weight": 1.2, "valence": -1},
    "relations_raw": {"label": "generic_relation", "base_weight": 1.0, "valence": 1},
}

SCORE_COLUMNS = [
    "belonging_score",
    "perceived_transparency",
    "relational_clarity",
    "psychological_safety",
    "integration_score",
    "isolation_score",
]


def normalize_text(text: object) -> str:
    """Normalize text for matching while preserving privacy-safe processing."""
    if pd.isna(text) or text is None:
        return ""

    text = str(text)
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def display_text(text: object) -> str:
    """Return a readable string without converting it to lowercase."""
    if pd.isna(text) or text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def parse_list(value: object) -> list[str]:
    """Parse comma, semicolon or newline separated questionnaire answers."""
    if pd.isna(value) or value is None:
        return []

    raw = str(value).strip()
    if not raw:
        return []

    parts = re.split(r"[,;\n]+", raw)
    return [display_text(part) for part in parts if display_text(part)]


def parse_interests(value: object) -> list[str]:
    """Parse interests or tags as normalised strings."""
    return [normalize_text(item) for item in parse_list(value)]


def parse_relations(value: object) -> list[str]:
    """Parse relational nominations."""
    return parse_list(value)


def fuzzy_match_name(name: str, name_list: Iterable[str], threshold: int = 80) -> tuple[str | None, int]:
    """Find the closest participant name using fuzzy matching."""
    name_list = list(name_list)
    if not name or not name_list:
        return None, 0

    normalized_candidates = [normalize_text(candidate) for candidate in name_list]
    result = process.extractOne(normalize_text(name), normalized_candidates, scorer=fuzz.ratio)

    if not result or result[1] < threshold:
        return None, 0

    matched_normalized = result[0]
    for original_name in name_list:
        if normalize_text(original_name) == matched_normalized:
            return original_name, int(result[1])

    return None, 0


def ranked_weight(base_weight: float, position: int) -> float:
    """Give more weight to earlier nominations in a list."""
    if position == 0:
        multiplier = 1.0
    elif position == 1:
        multiplier = 0.75
    elif position == 2:
        multiplier = 0.55
    else:
        multiplier = 0.35
    return round(base_weight * multiplier, 3)


def safe_numeric(series: pd.Series) -> pd.Series:
    """Convert a column to numeric values and keep missing values as NaN."""
    return pd.to_numeric(series, errors="coerce")


def zscore(series: pd.Series) -> pd.Series:
    """Return z-scores with safe handling of constant or empty series."""
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    std = numeric.std(ddof=0)
    if std == 0:
        return pd.Series([0.0] * len(numeric), index=series.index)
    return (numeric - numeric.mean()) / std


def percentile_rank(series: pd.Series) -> pd.Series:
    """Return percentile rank from 0 to 1."""
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    return numeric.rank(pct=True)
