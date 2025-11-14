#!/usr/bin/env python3
"""Produce reproducible descriptive statistics for the literature phase."""

from pathlib import Path

import pandas as pd


def describe_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> None:
    for column in columns:
        if column not in df.columns:
            continue
        col_series = df[column]
        numeric = pd.to_numeric(col_series, errors="coerce")
        print(f"\n{column} summary:")
        if numeric.notna().sum() > 0:
            print(numeric.describe())
            if numeric.isna().any():
                missing = col_series.isna().sum()
                print(f"Non-numeric/missing responses: {missing}")
        else:
            counts = col_series.value_counts(dropna=False).head(10)
            print("Top categories (non-numeric):")
            print(counts.to_string())


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "childhoodbalancedpublic_original.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset missing: {data_path}")

    df = pd.read_csv(data_path, low_memory=False)
    print(f"Rows: {len(df)}")
    top_countries = df["What country do you live in? (4bxk14u)"].value_counts().head(5)
    print("\nTop countries:")
    print(top_countries.to_string())

    print("\nReligion (top categories):")
    print(df["religion"].value_counts().head(5).to_string())

    describe_columns(
        df,
        (
            "classchild",
            "classteen",
            "classcurrent",
            "I love myself (2l8994l)",
            "I am not happy (ix5iyv3)-neg",
            "I am satisfied with my work/career life (or lack thereof) (z0mhd63)",
            "I am satisfied with my romantic relationships (hp9qz6f)",
            "during ages *0-12*: Your parents gave useful guidance (pqo6jmj)",
            "during ages *0-12*:  taught a purity culture that encouraged abstinance/waiting until marriage (wgbq7hv)",
            "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",
            "during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)",
            "In general, people in my *current* social circles tend treat me really well (tmt46e6)",
            "In general, people in my *current* social circles tend to treat me really well (71mn55g)",
            "Do you *currently* actively practice a religion? (902tbll)",
            "I tend to suffer from depression (wz901dj)",
            "I tend to suffer from anxiety (npvfh98)-neg",
            "Your CURRENT net worth is closest to (nhoz8ia)",
        ),
    )


if __name__ == "__main__":
    main()
