#!/usr/bin/env python3
"""Loop 021 helper: verify DG-4827 replicate-weight drop and stage H3 weighting inputs.

The script plays two roles:
1. Audit the DG-4827 delivery described in the Markdown manifest by computing
   file checksums/sizes and writing a reproducible status table.
2. When all required pieces (PSU IDs, base weights, and BRR replicates) exist,
   merge them with the H3 analytic variables so downstream scripts (e.g.,
   `loop016_h3_power_check.py --use-weights`) can recompute design effects.

Run with `PYTHONHASHSEED=20251016 python scripts/loop021_h3_weighted_checks.py
--manifest docs/h3_replicate_weights_manifest/manifest_loop021.md`.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

DATA_PATH = Path("childhoodbalancedpublic_original.csv")
STATUS_OUTPUT = Path("tables/loop021_h3_weight_delivery_status.csv")
SUMMARY_OUTPUT = Path("tables/loop021_h3_weighted_summary.csv")
EFFECT_OUTPUT = Path("tables/loop021_h3_weighted_effect.csv")
PANEL_OUTPUT = Path("outputs/loop021_h3_weighted_panel.parquet")

# Column names used in the base dataset for H3 analyses.
NETWORTH_COL = "networth"
CLASSCHILD_COL = "classchild"
COUNTRY_COL = "What country do you live in? (4bxk14u)"


@dataclass
class ManifestRow:
    """Represent a single line from the Markdown manifest."""

    file_name: str
    description: str
    checksum_placeholder: str
    notes: str

    def role(self) -> str | None:
        """Infer the semantic role of the file based on its name."""

        lower = self.file_name.lower()
        if "psu" in lower or "stratum" in lower:
            return "psu"
        if "weight" in lower and "brr" not in lower and "fay" not in lower:
            return "weights"
        if "brr" in lower:
            return "brr"
        if "fay" in lower:
            return "fay"
        if lower.endswith(".json"):
            return "metadata"
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to docs/h3_replicate_weights_manifest/manifest_loop021.md",
    )
    parser.add_argument(
        "--delivery-root",
        type=Path,
        default=None,
        help=(
            "Directory containing the delivered files. Defaults to the manifest "
            "directory so files live alongside the Markdown record."
        ),
    )
    parser.add_argument(
        "--status-output",
        type=Path,
        default=STATUS_OUTPUT,
        help="CSV destination for the per-file audit table.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=SUMMARY_OUTPUT,
        help="CSV destination for the ingestion/coverage summary.",
    )
    parser.add_argument(
        "--effect-output",
        type=Path,
        default=EFFECT_OUTPUT,
        help=(
            "CSV destination for weighted effect overrides consumed by "
            "loop016_h3_power_check.py --use-weights. Only written when all "
            "required files exist."
        ),
    )
    parser.add_argument(
        "--panel-output",
        type=Path,
        default=PANEL_OUTPUT,
        help=(
            "Optional parquet file storing the merged analytic variables + "
            "weights/replicates for downstream diagnostics."
        ),
    )
    parser.add_argument(
        "--row-index-column",
        default="row_index",
        help=(
            "Column used to join the replicate files back to the public dataset. "
            "If absent, the script will create this column by using the original "
            "row order in the CSV."
        ),
    )
    return parser.parse_args()


def parse_manifest(manifest_path: Path) -> List[ManifestRow]:
    """Parse the Markdown table that lists the requested files."""

    rows: List[ManifestRow] = []
    in_table = False
    with manifest_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                if in_table:
                    break
                continue
            if line.startswith("| File") and "Description" in line:
                in_table = True
                continue
            if not in_table:
                continue
            if line.startswith("| ---"):
                continue
            if not line.startswith("|"):
                break
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 4:
                continue
            file_cell, desc_cell, checksum_cell, notes_cell = parts[:4]
            file_name = file_cell.strip("` ")
            rows.append(
                ManifestRow(
                    file_name=file_name,
                    description=desc_cell,
                    checksum_placeholder=checksum_cell,
                    notes=notes_cell,
                )
            )
    return rows


def sha256sum(path: Path) -> str:
    """Compute the SHA-256 checksum for a file."""

    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_parent(path: Path) -> None:
    """Create the parent directory for a path if needed."""

    path.parent.mkdir(parents=True, exist_ok=True)


def write_status_table(
    rows: Iterable[Dict[str, object]], destination: Path
) -> None:
    """Persist the per-file audit table."""

    ensure_parent(destination)
    pd.DataFrame(list(rows)).to_csv(destination, index=False)


def load_parquet_or_csv(path: Path) -> pd.DataFrame:
    """Load parquet if possible; fall back to CSV for development stubs."""

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_parquet(path)


def merge_weights(
    row_index_col: str,
    base_df: pd.DataFrame,
    weights_df: pd.DataFrame,
    psu_df: pd.DataFrame,
    brr_df: pd.DataFrame,
    fay_df: pd.DataFrame | None,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Merge the replicate delivery pieces with the analytic columns."""

    panel = base_df.copy()
    if row_index_col not in panel.columns:
        panel = panel.reset_index().rename(columns={"index": row_index_col})

    def rename_single_value(df: pd.DataFrame, target_name: str) -> pd.DataFrame:
        cols = [c for c in df.columns if c != row_index_col]
        if len(cols) != 1:
            raise ValueError(
                f"Expected exactly one value column in {target_name} file; "
                f"found {cols}"
            )
        return df.rename(columns={cols[0]: target_name})

    weights_df = rename_single_value(weights_df, "weight")

    psu_cols = [c for c in psu_df.columns if c != row_index_col]
    if len(psu_cols) < 1:
        raise ValueError("PSU file must contain at least one identifier column.")
    rename_map = {}
    if len(psu_cols) >= 1:
        rename_map[psu_cols[0]] = "psu_id"
    if len(psu_cols) >= 2:
        rename_map[psu_cols[1]] = "stratum_id"
    psu_df = psu_df.rename(columns=rename_map)

    brr_cols = [c for c in brr_df.columns if c != row_index_col]
    if not brr_cols:
        raise ValueError("BRR file must contain replicate columns.")

    panel = panel.merge(weights_df, on=row_index_col, how="left")
    panel = panel.merge(psu_df, on=row_index_col, how="left")
    panel = panel.merge(brr_df, on=row_index_col, how="left")
    coverage = {
        "n_panel": int(panel.shape[0]),
        "n_weights": int(weights_df.shape[0]),
        "n_psu": int(psu_df.shape[0]),
        "n_brr": int(brr_df.shape[0]),
        "brr_cols": len(brr_cols),
    }

    if fay_df is not None:
        panel = panel.merge(fay_df, on=row_index_col, how="left")
        fay_cols = [c for c in fay_df.columns if c != row_index_col]
        coverage["n_fay"] = int(fay_df.shape[0])
        coverage["fay_cols"] = len(fay_cols)
    return panel, coverage


def write_summary(
    destination: Path,
    status: str,
    notes: str,
    coverage: Dict[str, object] | None = None,
    weight_stats: Dict[str, object] | None = None,
) -> None:
    """Persist a tidy summary table describing the ingestion state."""

    ensure_parent(destination)
    rows = [
        {
            "metric": "status",
            "value": status,
            "units": "",
            "notes": notes,
        }
    ]
    if coverage:
        for key, value in coverage.items():
            rows.append(
                {
                    "metric": key,
                    "value": value,
                    "units": "count" if isinstance(value, int) else "",
                    "notes": "coverage diagnostic",
                }
            )
    if weight_stats:
        for key, (value, units) in weight_stats.items():
            rows.append(
                {
                    "metric": key,
                    "value": value,
                    "units": units,
                    "notes": "weight distribution",
                }
            )
    pd.DataFrame(rows).to_csv(destination, index=False)


def main() -> int:
    args = parse_args()
    manifest_rows = parse_manifest(args.manifest)
    if not manifest_rows:
        raise RuntimeError(
            f"Failed to parse file table from manifest {args.manifest}"
        )
    delivery_root = args.delivery_root or args.manifest.parent
    status_entries = []
    role_paths: Dict[str, Path] = {}
    for row in manifest_rows:
        file_path = delivery_root / row.file_name
        present = file_path.exists()
        size_bytes = file_path.stat().st_size if present else 0
        checksum = sha256sum(file_path) if present else ""
        role = row.role()
        status_entries.append(
            {
                "file": row.file_name,
                "role": role or "",
                "description": row.description,
                "expected_checksum": row.checksum_placeholder,
                "path": str(file_path),
                "present": present,
                "size_bytes": size_bytes,
                "sha256": checksum,
                "notes": row.notes,
            }
        )
        if present and role:
            role_paths[role] = file_path
    write_status_table(status_entries, args.status_output)

    required_roles = {"psu", "weights", "brr"}
    missing_roles = sorted(required_roles - role_paths.keys())
    if missing_roles:
        write_summary(
            destination=args.summary_output,
            status="blocked",
            notes=(
                "Cannot merge weighting inputs until files with roles "
                f"{', '.join(missing_roles)} are delivered under {delivery_root}."
            ),
        )
        print(
            "Replicate ingestion blocked; missing roles:",
            ", ".join(missing_roles),
            file=sys.stderr,
        )
        return 0

    base_cols = [NETWORTH_COL, CLASSCHILD_COL, COUNTRY_COL]
    base_df = pd.read_csv(DATA_PATH, usecols=base_cols, low_memory=False)
    base_df = base_df.reset_index().rename(columns={"index": args.row_index_column})

    weights_df = load_parquet_or_csv(role_paths["weights"])
    psu_df = load_parquet_or_csv(role_paths["psu"])
    brr_df = load_parquet_or_csv(role_paths["brr"])
    fay_df = (
        load_parquet_or_csv(role_paths["fay"])
        if "fay" in role_paths
        else None
    )

    panel, coverage = merge_weights(
        row_index_col=args.row_index_column,
        base_df=base_df,
        weights_df=weights_df,
        psu_df=psu_df,
        brr_df=brr_df,
        fay_df=fay_df,
    )

    ensure_parent(args.panel_output)
    panel.to_parquet(args.panel_output, index=False)

    weight_stats = {
        "weight_sum": (float(panel["weight"].sum()), "sum"),
        "weight_min": (float(panel["weight"].min()), "min"),
        "weight_median": (float(panel["weight"].median()), "median"),
        "weight_max": (float(panel["weight"].max()), "max"),
    }
    write_summary(
        destination=args.summary_output,
        status="ingested",
        notes="All required files loaded; panel written for downstream use.",
        coverage=coverage,
        weight_stats=weight_stats,
    )

    # Placeholder: once replicate SE calculations are finalized, populate the
    # weighted effect override table consumed by loop016.
    ensure_parent(args.effect_output)
    pd.DataFrame(
        [
            {
                "status": "todo",
                "notes": (
                    "Weighted effect calculations not yet implemented. "
                    "Use outputs/loop021_h3_weighted_panel.parquet to compute "
                    "replicate-based SEs before rerunning loop016 with "
                    "--use-weights."
                ),
            }
        ]
    ).to_csv(args.effect_output, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
