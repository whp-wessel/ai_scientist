# Data Quality Checklist — Loop 038
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
- [x] `artifacts/session_info.txt` regenerated 2025-11-08T21:16:03Z with the latest Python/pip snapshot and git HEAD so reviewer R1 stays satisfied ahead of PAP edits.
- [x] `artifacts/checksums.json` (raw + imputed files) re-hashed at 2025-11-08T21:16Z; contents remain unchanged, and the refreshed timestamp documents that deterministic inputs were revalidated this loop.

## Risks / TODOs
1. Dtype warning (mixed types) for column 68 — inspect before modeling.
2. Sensitive columns (abuse, assault) flagged for disclosure control; `qc/disclosure_check_loop_006.md` documents the latest automation run (violations = 0).
3. Semantic Scholar credential still failing (403). Loop 038 logged `lit/queries/loop_038/query_001.json`; the waiver memo now spans loops 008–038 and incorporates Musliner & Singer 2014 (`10.1016/j.chiabu.2014.01.016`) alongside Bellis et al. 2017, Hintikka et al. 1998, Gasper 2020, Renjilian et al. 2021, Xu & Zheng 2025, Moran et al. 2018, and Kennedy et al. 2017, so PAP freeze remains on hold until approval or credential restoration.
4. Liu & Yin (2025), Talmon (2023), and Oh & Han (2019) jointly motivate explicit coding for maternal/paternal warmth and the short-form DERS items (`e3y0vab`–`e3y0vah`). Draft transformation script before PAP freeze so the mediator specification is reproducible once the waiver/API issue is resolved.
5. Ensure every new derivation is appended to `analysis/data_processing.md` so QC history stays reproducible.
6. Kennedy et al. (2017; `10.1016/j.aogh.2017.03.265`) adds a mentorship/support mechanism for H2; document which survey fields proxy mentorship or adult guidance before PAP freeze to keep the new literature aligned with modeling plans.

## Regeneration Notes
- All deterministic QC steps (DP1–DP8) are listed in `analysis/data_processing.md` with copy/paste-ready commands.
- Any interim manual calculation must be replaced by a scripted step and logged in the ledger before PAP freeze.
