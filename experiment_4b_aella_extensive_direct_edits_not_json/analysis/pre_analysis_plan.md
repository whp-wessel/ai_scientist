status: draft
phase: pap
last_updated: 2025-11-08T14:05Z
freeze_commit: TBD
registry_url: TBD

# Pre-Analysis Plan — Draft
This draft documents priority hypotheses for the Childhood Resilience Study. The PAP will be frozen (status: frozen) only after:
1. Evidence map contains ≥3 DOI-backed sources supporting each targeted outcome.
2. Measurement validity dossier (`qc/measures_validity.md`) is populated for every referenced construct.
3. Reproducible code lives under `analysis/code/` with command lines captured below.

## Design Summary
- **Population:** Respondents in `data/raw/childhoodbalancedpublic_original.csv`, aged ≥18.
- **Survey design:** No weights currently available; treat as SRS while monitoring for forthcoming design info (see `docs/survey_design.yaml`). Any newly provided weights will trigger a PAP revision before freeze.
- **Seed discipline:** `20251016` (per `config/agent_config.yaml`) is passed explicitly to every script (`analysis/code/run_models.py`, `analysis/code/missingness_profile.py`, `analysis/code/measure_validity_checks.py`, `analysis/code/impute_and_stack.py`, `analysis/code/calc_bh.py`) to maintain determinism.
- **Disclosure threshold:** n ≥ 10 per `config/agent_config.yaml`; exploratory summaries in Loops 002–003 remained comfortably above this threshold (minimum reported cell n = 187 in `qc/data_overview_loop002.md`).
- **Outputs + manifests:** Every figure/table command will be recorded inside `papers/main/MANIFEST.md` and the relevant QC markdown before PAP freeze.

## Privacy & Disclosure Controls
- All confirmatory tables/figures will cite the n ≥ 10 rule and will be screened via loop-specific disclosure memos (`qc/disclosure_check_loop_{loop:03d}.md`). `analysis/code/disclosure_check.py` now automates this process (see `qc/disclosure_check_loop_006.md`).
- Sensitive predictors/outcomes (abuse, depression, self-love) are tagged in `analysis/hypotheses.csv` and `qc/measures_validity.md`; any subgroup slices yielding n < 10 will be suppressed or binned per `config/agent_config.yaml::small_cells`.
- For manuscript-ready numbers, we will store both machine-readable CSVs (`tables/*.csv`) and markdown tables with clear suppression notes, referencing the exact command string that generated them.
- `reports/identification.md` records the disclosure guardrails to ensure readers understand that all estimates exclude identifiable cells.
- Loop 006 regenerated `figures/dag_design.png` (see `papers/main/MANIFEST.md`) and refreshed the identification memo after the reviewer STOP.

## Hypotheses Under Consideration
### H1 — Childhood Religious Adherence & Adult Depression (Family: wellbeing)
- **Outcome:** Likert 1–5 `wz901dj` (“I tend to suffer from depression”).
- **Predictor:** Ordinal `externalreligion` (importance of childhood religious adherence).
- **Controls:** Age (`selfage`), gender indicators (`biomale`, `gendermale`, `cis`), childhood class (`classchild`).
- **Exploratory analytic N:** 14,438 observations after listwise deletion (`outputs/run_models_loop003_H1.json`).
- **Estimand:** Average marginal effect of moving from “not important” to “very important” on depression score (ordered logit).
- **Model:** Survey-weighted (currently SRS) ordered logistic regression using `statsmodels`. Robust SEs clustered at household not available; default to HC1.
- **Missing data:** Explore patterns; if MAR plausible, use multiple imputation via `miceforest` with seed 20251016.
- **Robustness (pre-specified):** (a) Treat predictor as binary high/low. (b) Replace outcome with binary indicator `wz901dj >=4` and run logit.
- **Regeneration command (planned):**
  ```bash
  python analysis/code/run_models.py --hypothesis H1 --seed 20251016 --config config/agent_config.yaml
  ```

### H2 — Parental Guidance & Adult Health (Family: wellbeing)
- **Outcome:** Ordered `okq5xh8` (general health).
- **Predictor:** `pqo6jmj` guidance scale (0–12).
- **Controls:** Age, gender, current class (`classcurrent`), teen class (`classteen`). The chronic illness indicator (`mentalillness`) is currently empty in the delivered dataset, so it is excluded from interim models until valid values are supplied (see `outputs/run_models_loop003_H2.json`).
- **Exploratory analytic N:** 14,430 observations (Loop 003 exploratory run).
- **Estimand:** Difference in predicted probability of reporting “very good/excellent” health between top and bottom guidance quartiles (ordered logit + post-estimation).
- **Robustness:** (a) Treat health as continuous 1–5. (b) Limit to respondents without chronic illness indicator `mentalillness`.
- **Command stub:** same script with `--hypothesis H2`.

### H3 — Childhood Abuse & Adult Self-Love (Family: psychosocial)
- **Outcome:** Likert `2l8994l` (“I love myself”).
- **Predictor:** Binary `mds78zu` (parents verbally/emotionally abusive ages 0–12).
- **Controls:** Age, gender, sibling count (`siblingnumber`), socioeconomic controls.
- **Exploratory analytic N:** 13,507 respondents (Loop 003 exploratory run).
- **Estimand:** Average difference in self-love score between abuse vs no abuse (survey-weighted linear regression).
- **Robustness:** (a) Add teen-stage abuse indicator to check cumulative exposure. (b) Exclude respondents who reported perpetration (`rapist` == 1) to test sensitivity.
- **Command stub:** same script with `--hypothesis H3`.

## Data Management Plan
- Raw data remain immutable under `data/raw/`.
- Recode scripts live under `analysis/code/` and write outputs to `data/clean/` with filenames containing the seed (e.g., `childhood_imputed_stack_loop005.csv`, created in Loop 006).
- All transformations are now logged in `analysis/data_processing.md` (DP1–DP8) with explicit commands, seeds, and artifact paths; any new derivation must update both this ledger and `analysis/decision_log.csv`.
- Loop 002 added `analysis/code/describe_dataset.py` and `analysis/code/validate_metadata.py` so QC summaries (`artifacts/describe_dataset_loop002.json`, `qc/metadata_validation.md`) regenerate from a single command.
- Loop 003 implemented `analysis/code/run_models.py` (H1–H3 estimators), `analysis/code/missingness_profile.py`, and `analysis/code/measure_validity_checks.py`. Regeneration examples:
  ```bash
  python analysis/code/run_models.py --hypothesis all --config config/agent_config.yaml --seed 20251016 --draws 300 --output-prefix outputs/run_models_loop003
  python analysis/code/missingness_profile.py --input data/raw/childhoodbalancedpublic_original.csv --output-csv outputs/missingness_loop003.csv --output-md qc/missingness_loop003.md --seed 20251016
  python analysis/code/measure_validity_checks.py --config config/agent_config.yaml --output-md qc/measures_validity.md --output-json artifacts/measurement_validity_loop003.json
  ```
- Loop 005 added deterministic hot-deck MI tooling plus multiplicity automation, and Loop 006 reran the commands so the promised artifacts now exist in the repo:
  ```bash
  python analysis/code/impute_and_stack.py --m 5 --stacked-output data/clean/childhood_imputed_stack_loop005.parquet --summary-output artifacts/imputation_summary_loop005.json --seed 20251016
  # The script falls back to CSV if parquet engines are unavailable; see summary JSON for the actual path used.
  python analysis/code/calc_bh.py --config config/agent_config.yaml --input-csv analysis/results_pre_bh.csv --output-csv analysis/results.csv --summary-json artifacts/bh_summary.json
  ```

## Manuscript Linkage
- Each hypothesis maps to claims `[CLAIM:C1]`–`[CLAIM:C3]` in `papers/main/manuscript.tex` (stubs added in initial draft). The PAP freeze commit hash will be cited in the manuscript Methods section.

## Analysis Execution Order
1. **Data hygiene:** `analysis/code/describe_dataset.py`, `validate_metadata.py`, and `missingness_profile.py` run with seed 20251016; outputs referenced in `qc/data_overview_loop002.md`, `qc/metadata_validation.md`, and `qc/missingness_loop003.md`.
2. **Measurement dossier:** `analysis/code/measure_validity_checks.py` updates `qc/measures_validity.md` and `artifacts/measurement_validity_loop003.json`; all H1–H3 variables now have coding + DIF notes.
3. **Model estimation:** `analysis/code/run_models.py --hypothesis {H1|H2|H3}` executes ordered-logit / linear models with deterministic draws=300 for marginal effects.
4. **Imputation (if invoked):** `analysis/code/impute_and_stack.py --m 5 --seed 20251016` now produces a stacked hot-deck MI file plus `artifacts/imputation_summary_loop005.json`. Until pyarrow is available the script writes CSV outputs (`data/clean/childhood_imputed_stack_loop005.csv`) and records the fallback reason for transparency.
5. **BH correction:** Once confirmatory estimates exist, run `python analysis/code/calc_bh.py --config config/agent_config.yaml --input-csv analysis/results_pre_bh.csv --output-csv analysis/results.csv --summary-json artifacts/bh_summary.json` to append `q_value`, `family`, `targeted`, and `bh_in_scope` columns using Benjamini–Hochberg at q=0.05 per family (wellbeing, psychosocial).
6. **Disclosure review:** Draft `qc/disclosure_check_loop_{loop}` with min cell sizes and suppression summary before any tables/figures leave the repo.

## Outstanding Tasks Before Freeze
1. Restore Semantic Scholar access (or obtain formal waiver). Loop 007 query (`lit/queries/loop_007/query_001.json`) still returns 403; PAP freeze deferred until a working credential or waiver is recorded in `analysis/decision_log.csv`.
2. Register and freeze the PAP (`status: frozen`, `registry_url`, `freeze_commit`) once literature + QC gates are satisfied and the disclosure checklist automation (DP8) is linked to every planned table/figure.
3. Keep `analysis/data_processing.md` synchronized with any new derivations (e.g., sensitivity specifications) and cite the ledger whenever PAP text references transformation history.
4. Confirm whether `mentalillness` has valid data in future drops; if not, update H2 controls and document the missing control in `analysis/results.csv` once confirmatory runs occur.***

_No confirmatory analysis will begin until the status is set to `frozen` with registry details and a recorded commit/tag._
