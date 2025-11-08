#!/usr/bin/env python3
"""Shared helpers for handling Likert-scale recodes/alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import pandas as pd


@dataclass(frozen=True)
class LikertSpec:
    """Specification for a Likert item that may require sign flipping."""

    name: str
    column: str
    variable_id: str
    concept: str
    flip_sign: bool = True

    @property
    def aligned_column(self) -> str:
        return f"{self.name}_aligned"

    @property
    def z_column(self) -> str:
        return f"{self.name}_z"


def get_likert_specs() -> List[LikertSpec]:
    """Return the ordered list of Likert specs used across scripts."""

    return [
        LikertSpec(
            name="abuse_child",
            column="during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
            variable_id="mds78zu",
            concept="Childhood emotional abuse (0-12)",
            flip_sign=True,
        ),
        LikertSpec(
            name="abuse_teen",
            column="during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
            variable_id="v1k988q",
            concept="Teen emotional abuse (13-18)",
            flip_sign=True,
        ),
        LikertSpec(
            name="guidance_child",
            column="during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
            variable_id="pqo6jmj",
            concept="Childhood parental guidance (0-12)",
            flip_sign=True,
        ),
        LikertSpec(
            name="guidance_teen",
            column="during ages *13-18*: Your parents gave useful guidance (dcrx5ab)",
            variable_id="dcrx5ab",
            concept="Teen parental guidance (13-18)",
            flip_sign=True,
        ),
        LikertSpec(
            name="depression",
            column="I tend to suffer from depression (wz901dj)",
            variable_id="wz901dj",
            concept="Adult depression self-report",
            flip_sign=True,
        ),
        LikertSpec(
            name="selflove",
            column="I love myself (2l8994l)",
            variable_id="2l8994l",
            concept="Adult self-love self-report",
            flip_sign=True,
        ),
        LikertSpec(
            name="selfwar",
            column="you felt as though you were 'at war' with yourself in trying to be a good person",
            variable_id="selfwar",
            concept="Adult intrapersonal conflict (current)",
            flip_sign=True,
        ),
        LikertSpec(
            name="anxiety",
            column="I tend to suffer from anxiety (npvfh98)-neg",
            variable_id="npvfh98_neg",
            concept="Adult anxiety self-report",
            flip_sign=True,
        ),
    ]


def ensure_columns(df: pd.DataFrame, specs: Iterable[LikertSpec]) -> None:
    """Raise if the dataframe is missing any Likert columns."""

    missing = [spec.column for spec in specs if spec.column not in df.columns]
    if missing:
        raise KeyError(f"Missing expected Likert columns: {missing}")


def align_likert(df: pd.DataFrame, specs: Iterable[LikertSpec]) -> Dict[str, pd.Series]:
    """Return aligned series (sign-flipped if specified) for each spec."""

    aligned: Dict[str, pd.Series] = {}
    for spec in specs:
        series = df[spec.column]
        factor = -1 if spec.flip_sign else 1
        aligned[spec.aligned_column] = series * factor
    return aligned


def zscore(series: pd.Series) -> pd.Series:
    """Return a z-scored copy of the provided series."""

    centered = series - series.mean()
    std = series.std(ddof=0)
    if std == 0:
        return centered
    return centered / std
