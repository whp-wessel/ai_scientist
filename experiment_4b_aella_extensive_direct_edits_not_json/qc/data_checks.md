# Data Quality Checklist — Loop 000
Date: 2025-11-07
Seed: 20251016
Dataset: `data/raw/childhoodbalancedpublic_original.csv`

## Structural Checks
- [x] File exists and is readable (CSV, UTF-8).
- [x] Row count = 14,443; column count = 718 (verified via pandas).
- [ ] Schema: mixed dtypes detected (see warnings below) — requires recoding script.

Command to reproduce counts:
```bash
python analysis/code/describe_dataset.py --input data/raw/childhoodbalancedpublic_original.csv --seed 20251016
```
_Status:_ script not yet implemented; counts obtained via ad-hoc pandas snippet logged in research notebook.

## Missingness Snapshot
- Mean missingness across variables: 44.6% (needs variable-level table).
- Action: build `analysis/code/missingness_profile.py` to export `tables/missingness_summary_loop000.csv`.

## Survey Design Metadata
- No explicit weight/strata variables found. Confirm with data provider; if supplied later, update `docs/survey_design.yaml` and re-run all EDA.

## Risks / TODOs
1. Dtype warning (mixed types) for column 68 — inspect before modeling.
2. Sensitive columns (abuse, assault) flagged for disclosure control; mark in `qc/disclosure_check_loop_000.md` before any public summary.

## Regeneration Notes
- Manual calculations performed interactively (documented command: see Research Notebook). Replace with deterministic scripts before PAP freeze.
