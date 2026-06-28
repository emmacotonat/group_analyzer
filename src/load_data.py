"""Load questionnaire data from CSV or Excel files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_data(file_path: str | Path) -> pd.DataFrame:
    """Load a questionnaire export from CSV/XLSX.

    The only strictly required identity column is either `name` or `display_name`.
    All relational and perceptual columns are optional so the tool can be used
    progressively during the TFG design.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {file_path}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path, encoding="utf-8")
    else:
        df = pd.read_excel(file_path)

    df.columns = [str(col).strip() for col in df.columns]

    if "name" not in df.columns and "display_name" not in df.columns:
        raise ValueError("The dataset must contain at least `name` or `display_name`.")

    if "name" not in df.columns and "display_name" in df.columns:
        df["name"] = df["display_name"]

    if "display_name" not in df.columns and "name" in df.columns:
        df["display_name"] = df["name"]

    if "consent" in df.columns:
        consent = df["consent"].astype(str).str.lower().str.strip()
        df = df[consent.isin(["yes", "true", "1", "sí", "si", "y"])]

    if df.empty:
        raise ValueError("No valid rows were found after loading the questionnaire data.")

    return df.reset_index(drop=True)
