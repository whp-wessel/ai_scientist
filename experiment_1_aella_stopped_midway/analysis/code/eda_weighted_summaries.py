#!/usr/bin/env python3
"""Generate exploratory SRS-weighted summaries for wellbeing and socioeconomic outcomes."""

from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20251016
random.seed(SEED)
np.random.seed(SEED)

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
OUTPUT_TABLE_DIR = Path("tables")
OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

NOTEBOOK_COMMAND = "python analysis/code/eda_weighted_summaries.py"
TIMESTAMP = datetime.now(timezone.utc).isoformat()
SMALL_CELL_THRESHOLD = 10

SELFLOVE_VAR = "I love myself (2l8994l)"
ABUSE_VAR = "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"
CLASSCHILD_VAR = "classchild"
NETWORTH_VAR = "networth"

KEY_VARS = [SELFLOVE_VAR, ABUSE_VAR, CLASSCHILD_VAR, NETWORTH_VAR, "selfage"]


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return pd.read_csv(path, low_memory=False)


def apply_missing_codes(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    return series.mask(series < 0)


def summarize_selflove_by_abuse(df: pd.DataFrame) -> pd.DataFrame:
    temp = df[[SELFLOVE_VAR, ABUSE_VAR]].copy()
    temp[SELFLOVE_VAR] = apply_missing_codes(temp[SELFLOVE_VAR])
    temp[ABUSE_VAR] = apply_missing_codes(temp[ABUSE_VAR])
    temp = temp.dropna(subset=[SELFLOVE_VAR, ABUSE_VAR])
    if temp.empty:
        raise ValueError("No analytic rows for self-love by abuse summary.")
    grouped = temp.groupby(ABUSE_VAR)
    total_n = len(temp)
    rows = []
    for level, g in grouped:
        n = len(g)
        mean_val = g[SELFLOVE_VAR].mean()
        std_val = g[SELFLOVE_VAR].std(ddof=1)
        se = std_val / math.sqrt(n) if n > 0 else float("nan")
        ci_low = mean_val - 1.96 * se
        ci_high = mean_val + 1.96 * se
        rows.append(
            {
                "abuse_code": level,
                "n": n,
                "share": n / total_n,
                "mean_selflove": mean_val,
                "se": se,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    result = pd.DataFrame(rows).sort_values("abuse_code").reset_index(drop=True)
    result["suppressed"] = result["n"] < SMALL_CELL_THRESHOLD
    result.loc[result["suppressed"], ["n", "share", "mean_selflove", "se", "ci_low", "ci_high"]] = np.nan
    return result


def recode_classchild(val: float) -> str | pd.NA:
    if pd.isna(val):
        return pd.NA
    if val == 0:
        return "0 = unsure/other"
    if val in (1, 2):
        return "1-2 lower"
    if val in (3, 4):
        return "3-4 middle"
    if val in (5, 6):
        return "5-6 upper"
    return pd.NA


def recode_networth(val: float) -> str | pd.NA:
    if pd.isna(val):
        return pd.NA
    if val in (0, 1):
        return "0-1 low"
    if val in (2, 3):
        return "2-3 moderate"
    if val in (4, 5, 6):
        return "4-6 high"
    return pd.NA


def summarize_networth_by_class(df: pd.DataFrame) -> pd.DataFrame:
    temp = df[[CLASSCHILD_VAR, NETWORTH_VAR]].copy()
    temp[CLASSCHILD_VAR] = apply_missing_codes(temp[CLASSCHILD_VAR])
    temp[NETWORTH_VAR] = apply_missing_codes(temp[NETWORTH_VAR])
    temp = temp.dropna(subset=[CLASSCHILD_VAR, NETWORTH_VAR])
    if temp.empty:
        raise ValueError("No analytic rows for net worth by class summary.")
    temp["classchild_group"] = temp[CLASSCHILD_VAR].map(recode_classchild)
    temp["networth_group"] = temp[NETWORTH_VAR].map(recode_networth)
    temp = temp.dropna(subset=["classchild_group", "networth_group"])
    total_n = len(temp)
    grouped = (
        temp.groupby(["classchild_group", "networth_group"], sort=True)
        .size()
        .reset_index(name="n")
    )
    grouped["share_overall"] = grouped["n"] / total_n
    grouped["share_within_class"] = grouped.groupby("classchild_group")["n"].transform(lambda x: x / x.sum())
    grouped["suppressed"] = grouped["n"] < SMALL_CELL_THRESHOLD
    grouped.loc[grouped["suppressed"], ["n", "share_overall", "share_within_class"]] = np.nan
    return grouped.sort_values(["classchild_group", "networth_group"]).reset_index(drop=True)


def summarize_missingness(df: pd.DataFrame) -> pd.DataFrame:
    summaries = []
    total = len(df)
    for col in KEY_VARS:
        raw = pd.to_numeric(df[col], errors="coerce")
        negative_codes = int(raw[raw < 0].shape[0]) if raw.notna().any() else 0
        cleaned = raw.mask(raw < 0)
        missing = cleaned.isna().sum()
        summaries.append(
            {
                "variable": col,
                "non_missing_n": int(total - missing),
                "missing_n": missing,
                "missing_pct": missing / total,
                "negative_code_count": negative_codes,
            }
        )
    return pd.DataFrame(summaries)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def write_markdown(df: pd.DataFrame, path: Path, title: str, note: str) -> None:
    headers = list(df.columns)
    lines = [f"# {title}", "", "> Exploratory (SRS assumption; seed 20251016)", ""]
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines.extend([header_line, separator_line])
    for _, row in df.iterrows():
        formatted = []
        for item in row:
            if isinstance(item, float):
                if math.isnan(item):
                    formatted.append("")
                else:
                    formatted.append(f"{item:.4g}")
            else:
                formatted.append(str(item) if item is not None else "")
        lines.append("| " + " | ".join(formatted) + " |")
    lines.extend(["", f"_Notes_: {note}", "", f"Regenerate: `{NOTEBOOK_COMMAND}`", "", f"Generated: {TIMESTAMP}"])
    path.write_text("\n".join(lines))


def write_metadata(path: Path, metadata: dict) -> None:
    path.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    df = load_data(DATA_PATH)

    selflove_summary = summarize_selflove_by_abuse(df)
    networth_summary = summarize_networth_by_class(df)
    missing_summary = summarize_missingness(df)

    write_csv(selflove_summary, OUTPUT_TABLE_DIR / "exploratory_selflove_by_abuse.csv")
    write_csv(networth_summary, OUTPUT_TABLE_DIR / "exploratory_networth_by_classchild.csv")
    write_csv(missing_summary, OUTPUT_TABLE_DIR / "exploratory_missingness_key_vars.csv")

    write_markdown(
        selflove_summary,
        OUTPUT_TABLE_DIR / "exploratory_selflove_by_abuse.md",
        title="Self-love by Childhood Emotional Abuse (Exploratory)",
        note="Values <0 treated as non-response; suppression applied when n < 10 (none observed).",
    )
    write_markdown(
        networth_summary,
        OUTPUT_TABLE_DIR / "exploratory_networth_by_classchild.md",
        title="Net Worth by Childhood Class (Aggregated Categories; Exploratory)",
        note="Classchild recoded to grouped categories to avoid small cells; n < 10 suppressed.",
    )
    write_markdown(
        missing_summary,
        OUTPUT_TABLE_DIR / "exploratory_missingness_key_vars.md",
        title="Missingness Summary for Key Variables",
        note="Missingness counts calculated after treating numeric values < 0 as non-response.",
    )

    metadata = {
        "seed": SEED,
        "generated": TIMESTAMP,
        "dataset": str(DATA_PATH),
        "outputs": [
            "tables/exploratory_selflove_by_abuse.csv",
            "tables/exploratory_networth_by_classchild.csv",
            "tables/exploratory_missingness_key_vars.csv",
        ],
        "command": NOTEBOOK_COMMAND,
    }
    write_metadata(Path("artifacts/eda_weighted_summaries_metadata.json"), metadata)


if __name__ == "__main__":
    main()
