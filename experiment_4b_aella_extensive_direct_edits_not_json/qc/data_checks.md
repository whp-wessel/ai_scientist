# Data Quality Checklist — Loop 016
Date: 2025-11-08
Seed: 20251016
Dataset: `data/raw/childhoodbalancedpublic_original.csv`

## Structural Checks
- [x] File exists and is readable (CSV, UTF-8).
- [x] Row count = 14,443; column count = 718 (verified via pandas in DP1 scripts; no schema drift since Loop 002).
- [ ] Schema: mixed dtypes persist on select columns (see warnings below) — recoding remains on the backlog for the modeling scripts.

Command to reproduce counts:
```bash
python analysis/code/describe_dataset.py \
  --input data/raw/childhoodbalancedpublic_original.csv \
  --seed 20251016 \
  --output-json artifacts/describe_dataset_loop002.json \
  --output-md qc/data_overview_loop002.md
```
_Status:_ Automated summary generated in Loop 002; refer to `qc/data_overview_loop002.md` for the table output.

## Missingness Snapshot
- Mean missingness across variables: 44.6% (profile generated Loop 003; no new raw deliveries since).
- Command:
  ```bash
  python analysis/code/missingness_profile.py \
    --input data/raw/childhoodbalancedpublic_original.csv \
    --output-csv outputs/missingness_loop003.csv \
    --output-md qc/missingness_loop003.md \
    --seed 20251016
  ```
- Outputs: `outputs/missingness_loop003.csv` (full table) and `qc/missingness_loop003.md` (Exploratory top-k summary).

## Survey Design Metadata
- No explicit weight/strata variables found. Confirm with data provider; if supplied later, update `docs/survey_design.yaml` and re-run all EDA.
- Automated validation command:
  ```bash
  python analysis/code/validate_metadata.py \
    --dataset data/raw/childhoodbalancedpublic_original.csv \
    --codebook docs/codebook.json \
    --survey-design docs/survey_design.yaml \
    --report-json artifacts/metadata_validation_loop002.json \
    --report-md qc/metadata_validation.md
  ```
- Result: PAP variables documented with `source_column` mappings; `qc/metadata_validation.md` logs status (still assuming SRS).

## Reproducibility Checkpoint
- [x] `artifacts/session_info.txt` last updated 2025-11-08T15:34:50Z with Python/pip details and git HEAD; no package changes since, so references remain valid.
- [x] `artifacts/checksums.json` timestamp 2025-11-08T13:46:15Z covering raw + imputed files; raw dataset mtimes unchanged, so hashes remain current.

## Risks / TODOs
1. Dtype warning (mixed types) for column 68 — inspect before modeling.
2. Sensitive columns (abuse, assault) flagged for disclosure control; `qc/disclosure_check_loop_006.md` documents the latest automation run (violations = 0).
3. Semantic Scholar credential still failing (403). Loop 016 logged `lit/queries/loop_016/query_001.json`; waiver memo now covers loops 008-016 and cites the new CrossRef fallbacks (DOIs `10.2139/ssrn.4703219`, `10.1016/j.chiabu.2024.107020`, `10.21275/SR23621004642`, and `10.1093/med:psych/9780195332711.003.0004`), but PAP freeze remains on hold pending approval or credential fix.
4. Ensure every new derivation is appended to `analysis/data_processing.md` so QC history stays reproducible.

## Regeneration Notes
- All deterministic QC steps (DP1–DP8) are listed in `analysis/data_processing.md` with copy/paste-ready commands.
- Any interim manual calculation must be replaced by a scripted step and logged in the ledger before PAP freeze.
