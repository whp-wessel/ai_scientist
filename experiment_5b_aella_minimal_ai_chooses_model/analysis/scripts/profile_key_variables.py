"""
Generate descriptive summaries for the focal childhood/adult wellbeing variables.

Usage:
    python analysis/scripts/profile_key_variables.py

Outputs two CSV files under `analysis/profiling/`:
    - loop001_key_vars_summary.csv
    - loop001_key_vars_value_counts.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
PROFILE_DIR = Path("analysis/profiling")

# Map shorthand codes to the exact column headers present in the dataset.
VARIABLES: Dict[str, str] = {
    "mds78zu": "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
    "ix5iyv3": "I am not happy (ix5iyv3)-neg",
    "pqo6jmj": "during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
    "z0mhd63": "I am satisfied with my work/career life (or lack thereof) (z0mhd63)",
    "4tuoqly": "during ages *0-12*:  you spent time on the internet or computers (4tuoqly)",
    "classcurrent": "classcurrent",
    "dfqbzi5": "during ages *0-12*:  you were depressed (dfqbzi5)",
    "wz901dj": "I tend to suffer from depression (wz901dj)",
}


def main() -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    summary_rows = []
    counts_rows = []
    for code, column in VARIABLES.items():
        series = df[column]
        summary_rows.append(
            {
                "variable_code": code,
                "column_name": column,
                "non_missing_n": int(series.count()),
                "missing_n": int(series.isna().sum()),
                "mean": float(series.mean()) if pd.api.types.is_numeric_dtype(series) else None,
                "std": float(series.std()) if pd.api.types.is_numeric_dtype(series) else None,
                "min": float(series.min()) if pd.api.types.is_numeric_dtype(series) else None,
                "max": float(series.max()) if pd.api.types.is_numeric_dtype(series) else None,
                "unique_values": int(series.nunique(dropna=True)),
            }
        )

        value_counts = series.value_counts(dropna=False).sort_index()
        counts_rows.extend(
            {
                "variable_code": code,
                "value": value if pd.notna(value) else "NA",
                "count": int(count),
            }
            for value, count in value_counts.items()
        )

    summary_path = PROFILE_DIR / "loop001_key_vars_summary.csv"
    counts_path = PROFILE_DIR / "loop001_key_vars_value_counts.csv"
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
    pd.DataFrame(counts_rows).to_csv(counts_path, index=False)
    print(f"Wrote {summary_path} and {counts_path}")


if __name__ == "__main__":
    main()
