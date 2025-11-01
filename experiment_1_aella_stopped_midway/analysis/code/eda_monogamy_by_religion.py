#!/usr/bin/env python3
"""Generate exploratory cross-tab for monogamy preference by religion practice."""

from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

SEED = 20251016
random.seed(SEED)
np.random.seed(SEED)

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
OUTPUT_DIR = Path("tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MONOGAMY_LABEL_COL = "Your current monogamy/nonmonogamy preference? (27iua3o)"
RELIGION_LABEL_COL = "Do you *currently* actively practice a religion? (902tbll)"

SMALL_CELL_THRESHOLD = 10
MISSING_STRINGS: List[str] = [
    "",
    "NA",
    "NaN",
    "nan",
    "N/A",
    "Prefer not to answer",
    "Prefer Not to Answer",
]

ORDER_MONOGAMY = [
    "Full monogamy",
    "Leaning monogamy",
    "Leaning nonmonogamy",
    "Full nonmonogamy",
]
ORDER_RELIGION = [
    "No",
    "Yes, slightly",
    "Yes, moderately",
    "Yes, very seriously",
]

TIMESTAMP = datetime.now(timezone.utc).isoformat()
COMMAND = "python analysis/code/eda_monogamy_by_religion.py"


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path, usecols=[MONOGAMY_LABEL_COL, RELIGION_LABEL_COL], low_memory=False)


def clean_string(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip()
    cleaned = cleaned.replace({val: pd.NA for val in MISSING_STRINGS})
    cleaned = cleaned.replace({"nan": pd.NA, "None": pd.NA})
    cleaned = cleaned.mask(cleaned == "")
    return cleaned


def summarise(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    analytic = df.dropna(subset=[MONOGAMY_LABEL_COL, RELIGION_LABEL_COL]).copy()
    analytic[MONOGAMY_LABEL_COL] = pd.Categorical(analytic[MONOGAMY_LABEL_COL], categories=ORDER_MONOGAMY, ordered=True)
    analytic[RELIGION_LABEL_COL] = pd.Categorical(analytic[RELIGION_LABEL_COL], categories=ORDER_RELIGION, ordered=True)
    grouped = (
        analytic.groupby([RELIGION_LABEL_COL, MONOGAMY_LABEL_COL], observed=True)
        .size()
        .reset_index(name="n")
    )
    total_n = float(len(analytic))
    grouped["share_overall"] = grouped["n"] / total_n if total_n > 0 else np.nan
    grouped["share_within_religion"] = grouped["n"] / grouped.groupby(RELIGION_LABEL_COL, observed=True)["n"].transform("sum")
    grouped["share_within_monogamy"] = grouped["n"] / grouped.groupby(MONOGAMY_LABEL_COL, observed=True)["n"].transform("sum")
    grouped["suppressed"] = grouped["n"] < SMALL_CELL_THRESHOLD
    suppress_cols = ["n", "share_overall", "share_within_religion", "share_within_monogamy"]
    grouped.loc[grouped["suppressed"], suppress_cols] = np.nan
    return grouped.sort_values([RELIGION_LABEL_COL, MONOGAMY_LABEL_COL]).reset_index(drop=True), int(total_n)


def format_float(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.4f}" if value < 1 else f"{value:.0f}"


def write_markdown(df: pd.DataFrame, path: Path) -> None:
    headers = list(df.columns)
    lines = [
        "# Monogamy Preference by Religion Practice (Exploratory)",
        "",
        "> Exploratory (SRS assumption; seed 20251016)",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values = [
            str(row["religion_practice"]),
            str(row["monogamy_preference"]),
            "" if pd.isna(row["n"]) else f"{int(row['n'])}",
            format_float(row["share_overall"]),
            format_float(row["share_within_religion"]),
            format_float(row["share_within_monogamy"]),
            "Y" if row["suppressed"] else "N",
        ]
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "_Notes_: Shares computed under equal weighting; cells with n < 10 suppressed.",
            "",
            f"Regenerate: `{COMMAND}`",
            "",
            f"Generated: {TIMESTAMP}",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(df: pd.DataFrame, analytic_n: int) -> None:
    csv_path = OUTPUT_DIR / "exploratory_monogamy_by_religion.csv"
    md_path = OUTPUT_DIR / "exploratory_monogamy_by_religion.md"
    metadata_path = OUTPUT_DIR / "exploratory_monogamy_by_religion_metadata.json"

    df_out = df.rename(
        columns={
            RELIGION_LABEL_COL: "religion_practice",
            MONOGAMY_LABEL_COL: "monogamy_preference",
        }
    )
    df_out.to_csv(csv_path, index=False)
    write_markdown(df_out, md_path)

    metadata = {
        "generated": TIMESTAMP,
        "seed": SEED,
        "command": COMMAND,
        "dataset": str(DATA_PATH),
        "rows_analyzed": analytic_n,
        "small_cell_threshold": SMALL_CELL_THRESHOLD,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    df = load_data(DATA_PATH)
    df[MONOGAMY_LABEL_COL] = clean_string(df[MONOGAMY_LABEL_COL])
    df[RELIGION_LABEL_COL] = clean_string(df[RELIGION_LABEL_COL])
    summary, analytic_n = summarise(df)
    write_outputs(summary, analytic_n)


if __name__ == "__main__":
    main()
