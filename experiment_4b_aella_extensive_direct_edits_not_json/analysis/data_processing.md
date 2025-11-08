# Data Processing Ledger — Childhood Resilience Study
Updated: 2025-11-08
Seed: 20251016 (global, see `config/agent_config.yaml`)

This ledger enumerates every dataset transformation executed so far, the exact command to regenerate it, and the resulting artifacts. Steps are listed in execution order and will be appended whenever new derivations are added. All commands must be run from the repository root.

## DP1 — Structural QC Snapshot (Loop 002)
- **Purpose:** Record canonical row/column counts and detect dtype anomalies before modeling.
- **Inputs:** `data/raw/childhoodbalancedpublic_original.csv`
- **Command:**
  ```bash
  python analysis/code/describe_dataset.py \
    --input data/raw/childhoodbalancedpublic_original.csv \
    --seed 20251016 \
    --output-json artifacts/describe_dataset_loop002.json \
    --output-md qc/data_overview_loop002.md
  ```
- **Outputs:** `artifacts/describe_dataset_loop002.json`, `qc/data_overview_loop002.md`
- **Notes:** Reports row=14,443, col=718; min disclosed cell n=187 so far.

## DP2 — Codebook & Survey Design Validation (Loop 002)
- **Purpose:** Confirm that every PAP variable is present in the raw file and the survey metadata describes weights/strata (currently none provided → SRS assumption).
- **Inputs:** `data/raw/childhoodbalancedpublic_original.csv`, `docs/codebook.json`, `docs/survey_design.yaml`
- **Command:**
  ```bash
  python analysis/code/validate_metadata.py \
    --dataset data/raw/childhoodbalancedpublic_original.csv \
    --codebook docs/codebook.json \
    --survey-design docs/survey_design.yaml \
    --report-json artifacts/metadata_validation_loop002.json \
    --report-md qc/metadata_validation.md
  ```
- **Outputs:** `artifacts/metadata_validation_loop002.json`, `qc/metadata_validation.md`
- **Notes:** Flags missing survey weights; PAP remains descriptive until weights arrive.

## DP3 — Missingness Profile (Loop 003)
- **Purpose:** Quantify per-variable missingness and highlight variables needing imputation.
- **Inputs:** `data/raw/childhoodbalancedpublic_original.csv`
- **Command:**
  ```bash
  python analysis/code/missingness_profile.py \
    --input data/raw/childhoodbalancedpublic_original.csv \
    --output-csv outputs/missingness_loop003.csv \
    --output-md qc/missingness_loop003.md \
    --seed 20251016
  ```
- **Outputs:** `outputs/missingness_loop003.csv`, `qc/missingness_loop003.md`
- **Notes:** Mean missingness ≈ 44.6%; guidance variable has 0.8% missing.

## DP4 — Measurement Validity & DIF Checks (Loop 003)
- **Purpose:** Document wording/coding/reliability for every PAP variable and screen for DIF by sex assigned at birth.
- **Inputs:** `config/agent_config.yaml`, `docs/codebook.json`
- **Command:**
  ```bash
  python analysis/code/measure_validity_checks.py \
    --config config/agent_config.yaml \
    --output-md qc/measures_validity.md \
    --output-json artifacts/measurement_validity_loop003.json
  ```
- **Outputs:** `qc/measures_validity.md`, `artifacts/measurement_validity_loop003.json`
- **Notes:** All H1–H3 constructs now log reliability (`single_item`) plus DIF stats.

## DP5 — Exploratory Model Runs (Loop 003)
- **Purpose:** Exercise `analysis/code/run_models.py` for H1–H3 to confirm script determinism before PAP freeze (exploratory only, labeled as such in notebooks).
- **Inputs:** `config/agent_config.yaml`, `data/raw/childhoodbalancedpublic_original.csv`
- **Command:**
  ```bash
  python analysis/code/run_models.py \
    --hypothesis all \
    --seed 20251016 \
    --config config/agent_config.yaml \
    --draws 300 \
    --output-prefix outputs/run_models_loop003
  ```
- **Outputs:** `outputs/run_models_loop003_H1.json`, `outputs/run_models_loop003_H2.json`, `outputs/run_models_loop003_H3.json`
- **Notes:** Results remain exploratory; PAP still draft so no confirmatory tables produced.

## DP6 — Multiple Imputation Stack (Loops 005–006)
- **Purpose:** Generate deterministic hot-deck MI stack + diagnostics for use once PAP is frozen.
- **Inputs:** `data/raw/childhoodbalancedpublic_original.csv`, optional parquet deps (falls back to CSV)
- **Command:**
  ```bash
  python analysis/code/impute_and_stack.py \
    --m 5 \
    --stacked-output data/clean/childhood_imputed_stack_loop005.parquet \
    --summary-output artifacts/imputation_summary_loop005.json \
    --seed 20251016
  ```
- **Outputs:** `data/clean/childhood_imputed_stack_loop005.csv` (CSV fallback recorded in summary), `artifacts/imputation_summary_loop005.json`
- **Notes:** Summary JSON logs engine fallback + checksum; rerun Loop 006 to address reviewer STOP.

## DP7 — DAG + Identification Artifacts (Loops 005–006)
- **Purpose:** Maintain conceptual graph + memo describing descriptive stance and covariates.
- **Inputs:** none beyond repo scripts.
- **Command:**
  ```bash
  python analysis/code/plot_dag.py \
    --output-png figures/dag_design.png \
    --output-json figures/dag_design.json
  ```
- **Outputs:** `figures/dag_design.png`, `figures/dag_design.json`, referenced by `reports/identification.md`
- **Notes:** Memo includes command + seed; rerun Loop 006 to close reviewer STOP.

## DP8 — Disclosure Automation (Loop 006)
- **Purpose:** Enforce n ≥ 10 before releasing figures/tables.
- **Inputs:** `tables/` (if any), `figures/`
- **Command:**
  ```bash
  python analysis/code/disclosure_check.py \
    --tables-dir tables \
    --figures-dir figures \
    --min-n 10 \
    --output-md qc/disclosure_check_loop_006.md \
    --seed 20251016
  ```
- **Outputs:** `qc/disclosure_check_loop_006.md`
- **Notes:** Currently only structural DAG tracked; violations = 0.

## Pending Entries
- Add Scenario-specific sensitivity analyses once PAP freezes and confirmatory runs begin.
- Update this ledger when additional derived datasets, tables, or figures are produced.
