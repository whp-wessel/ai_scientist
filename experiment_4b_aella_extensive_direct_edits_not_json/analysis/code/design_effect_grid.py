#!/usr/bin/env python3
"""Generate a design-effect grid showing how inflated uncertainties affect the confirmatory estimates."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Design-effect uncertainty grid")
    parser.add_argument(
        "--input",
        default="analysis/results.csv",
        help="BH-adjusted results CSV.",
    )
    parser.add_argument(
        "--deffs",
        nargs="+",
        type=float,
        default=[1.0, 1.25, 1.5, 2.0],
        help="Design-effect multipliers to apply to the standard errors.",
    )
    parser.add_argument(
        "--output-csv",
        default="outputs/sensitivity_design_effect_grid.csv",
        help="CSV table with adjusted SEs/CI.",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/sensitivity_design_effect_grid.md",
        help="Markdown summary of the design-effect scenarios.",
    )
    return parser.parse_args()


def norm_cdf(x: float) -> float:
    return (1 + math.erf(x / math.sqrt(2))) / 2


def two_sided_pvalue(estimate: float, se: float) -> float:
    if se == 0 or math.isnan(estimate) or math.isnan(se):
        return float("nan")
    z = estimate / se
    return 2 * (1 - norm_cdf(abs(z)))


def build_rows(df: pd.DataFrame, deffs: list[float]) -> pd.DataFrame:
    targeted = df[df["targeted"].astype(str).str.upper() == "Y"].copy()
    rows: list[dict[str, float | str]] = []
    for deff in deffs:
        sqrt_deff = math.sqrt(deff)
        for _, row in targeted.iterrows():
            estimate = float(row["estimate"])
            se_orig = float(row["se"])
            se_adj = se_orig * sqrt_deff
            ci_low = estimate - 1.96 * se_adj
            ci_high = estimate + 1.96 * se_adj
            p_value = two_sided_pvalue(estimate, se_adj)
            n_unweighted = int(row["n_unweighted"])
            n_eff = n_unweighted / deff if deff else 0.0
            rows.append(
                {
                    "hypothesis_id": row["hypothesis_id"],
                    "deff": deff,
                    "estimate": estimate,
                    "se_adj": se_adj,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p_value": p_value,
                    "n_unweighted": n_unweighted,
                    "n_effective": n_eff,
                    "q_value": row.get("q_value", ""),
                }
            )
    return pd.DataFrame(rows)


def to_markdown(df: pd.DataFrame) -> str:
    header = "| Hypothesis | DEFF | Estimate | SE_adj | 95% CI | p-value | n_unweighted | n_effective | q-value |"
    sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    lines = [header, sep]
    for _, row in df.iterrows():
        ci_range = f"[{row['ci_low']:.3f}, {row['ci_high']:.3f}]"
        lines.append(
            "| "
            f"{row['hypothesis_id']} | {row['deff']:.2f} | {row['estimate']:.3f} | {row['se_adj']:.3f} | "
            f"{ci_range} | {row['p_value']:.2g} | {int(row['n_unweighted'])} | "
            f"{row['n_effective']:.1f} | {row['q_value']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)
    grid = build_rows(df, args.deffs)
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(output_csv, index=False)

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(to_markdown(grid))
    print(f"Wrote design-effect grid to {output_csv} and {output_md}")


if __name__ == "__main__":
    main()
