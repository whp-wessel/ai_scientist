# Data Quality Checklist — Loop 048
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
- [x] `artifacts/session_info.txt` regenerated 2025-11-08T23:15:06Z via `python - <<'PY' ... import runner; runner.update_reproducibility()` (see decision log entry `repro_checkpoint_loop049`), capturing the current Python stack, git HEAD, and seed 20251016 ahead of Loop 049 edits.
- [x] `artifacts/checksums.json` (raw + imputed files) re-hashed at 2025-11-08T23:15:06Z; hashes match prior values, and the refreshed timestamp confirms deterministic inputs were revalidated before literature/PAP updates.

## Risks / TODOs
1. Dtype warning (mixed types) for column 68 — inspect before modeling.
2. Sensitive columns (abuse, assault) flagged for disclosure control; `qc/disclosure_check_loop_006.md` documents the latest automation run (violations = 0).
3. Semantic Scholar credential still failing (403). Loop 049 logged `lit/queries/loop_049/query_001.json`, and the waiver memo now spans loops 008–049 with both Glenn 2014 (DOI `10.1080/19349637.2014.864543`, CrossRef payload `lit/queries/loop_048/crossref_query_001.json`) and the Journal of Adolescent Health mentor report (DOI `10.1016/S1054-139X(97)87629-X`, CrossRef payload `lit/queries/loop_049/crossref_query_002.json`) plus earlier sources (Berson & Baggerly 2009, Zhang 2025, Mandelli 2015, Kuhar 2024, Ashton 2021, Bauldry 2006, Luecken 2000). PAP freeze remains on hold until ops restores the key or grants a waiver; the 2025-11-09 ops memo (`lit/semantic_scholar_ops_memo_2025-11-09.md`) will be dispatched on schedule with logged proof, and the 2025-11-10 support-ticket draft (`lit/semantic_scholar_support_ticket_draft_2025-11-10.md`) is queued if ops has not restored access by that deadline.
4. Liu & Yin (2025), Talmon (2023), and Oh & Han (2019) jointly motivate explicit coding for maternal/paternal warmth and the short-form DERS items (`e3y0vab`–`e3y0vah`). Draft transformation script before PAP freeze so the mediator specification is reproducible once the waiver/API issue is resolved.
5. Ensure every new derivation is appended to `analysis/data_processing.md` so QC history stays reproducible.
6. Kennedy et al. (2017; `10.1016/j.aogh.2017.03.265`) adds a mentorship/support mechanism for H2; document which survey fields proxy mentorship or adult guidance before PAP freeze to keep the new literature aligned with modeling plans.

## Regeneration Notes
- All deterministic QC steps (DP1–DP8) are listed in `analysis/data_processing.md` with copy/paste-ready commands.
- Any interim manual calculation must be replaced by a scripted step and logged in the ledger before PAP freeze.
