"""
Create centered and standardized (z) variants of the −3..3 Likert variables that
feed hypotheses H1–H4.

Usage:
    python analysis/scripts/derive_likert_scales.py

Outputs:
    - analysis/derived/loop002_likert_scales.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
OUTPUT_PATH = Path("analysis/derived/loop002_likert_scales.csv")


@dataclass(frozen=True)
class LikertVariable:
    code: str
    column: str


LIKERT_VARIABLES: List[LikertVariable] = [
    LikertVariable(
        code="mds78zu",
        column="during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
    ),
    LikertVariable(
        code="ix5iyv3",
        column="I am not happy (ix5iyv3)-neg",
    ),
    LikertVariable(
        code="pqo6jmj",
        column="during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
    ),
    LikertVariable(
        code="z0mhd63",
        column="I am satisfied with my work/career life (or lack thereof) (z0mhd63)",
    ),
    LikertVariable(
        code="4tuoqly",
        column="during ages *0-12*:  you spent time on the internet or computers (4tuoqly)",
    ),
    LikertVariable(
        code="dfqbzi5",
        column="during ages *0-12*:  you were depressed (dfqbzi5)",
    ),
    LikertVariable(
        code="wz901dj",
        column="I tend to suffer from depression (wz901dj)",
    ),
]

ADDITIONAL_COLUMNS = [
    "selfage",
    "gendermale",
    "education",
    "classchild",
    "classteen",
    "classcurrent",
]


def main() -> None:
    cols_to_read = [spec.column for spec in LIKERT_VARIABLES] + ADDITIONAL_COLUMNS
    df = pd.read_csv(DATA_PATH, usecols=cols_to_read)
    df.insert(0, "respondent_id", range(len(df)))

    for spec in LIKERT_VARIABLES:
        series = df[spec.column]
        scaled_col = f"{spec.code}_scaled"
        z_col = f"{spec.code}_z"
        df[scaled_col] = series / 3.0
        centered = series - series.mean()
        std = series.std(ddof=0)
        df[z_col] = centered / std if std != 0 else pd.NA

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {OUTPUT_PATH} (n={len(df)})")


if __name__ == "__main__":
    main()
