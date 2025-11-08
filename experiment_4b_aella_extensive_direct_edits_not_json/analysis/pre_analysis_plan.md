status: draft
phase: pap
last_updated: 2025-11-08
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
- **Seed discipline:** `20251016` (per `config/agent_config.yaml`) is passed explicitly to every script (`analysis/code/run_models.py`, `analysis/code/missingness_profile.py`, `analysis/code/measure_validity_checks.py`) to maintain determinism.
- **Disclosure threshold:** n ≥ 10 per `config/agent_config.yaml`; exploratory summaries in Loops 002–003 remained comfortably above this threshold (minimum reported cell n = 187 in `qc/data_overview_loop002.md`).
- **Outputs + manifests:** Every figure/table command will be recorded inside `papers/main/MANIFEST.md` and the relevant QC markdown before PAP freeze.

## Privacy & Disclosure Controls
- All confirmatory tables/figures will cite the n ≥ 10 rule and will be screened via loop-specific disclosure memos (`qc/disclosure_check_loop_{loop:03d}.md`). The template will be created during PAP freeze and populated before any release.
- Sensitive predictors/outcomes (abuse, depression, self-love) are tagged in `analysis/hypotheses.csv` and `qc/measures_validity.md`; any subgroup slices yielding n < 10 will be suppressed or binned per `config/agent_config.yaml::small_cells`.
- For manuscript-ready numbers, we will store both machine-readable CSVs (`tables/*.csv`) and markdown tables with clear suppression notes, referencing the exact command string that generated them.
- `reports/identification.md` will also record the disclosure guardrails to ensure readers understand that all estimates exclude identifiable cells.

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
- Recode scripts will live under `analysis/code/` and write outputs to `data/clean/` with filenames containing the seed (e.g., `childhood_clean_seed20251016.parquet`).
- All transformations logged in `analysis/data_processing.md` (to be created) and referenced in `analysis/decision_log.csv`.
- Loop 002 added `analysis/code/describe_dataset.py` and `analysis/code/validate_metadata.py` so QC summaries (`artifacts/describe_dataset_loop002.json`, `qc/metadata_validation.md`) regenerate from a single command.
- Loop 003 implemented `analysis/code/run_models.py` (H1–H3 estimators), `analysis/code/missingness_profile.py`, and `analysis/code/measure_validity_checks.py`. Regeneration examples:
  ```bash
  python analysis/code/run_models.py --hypothesis all --config config/agent_config.yaml --seed 20251016 --draws 300 --output-prefix outputs/run_models_loop003
  python analysis/code/missingness_profile.py --input data/raw/childhoodbalancedpublic_original.csv --output-csv outputs/missingness_loop003.csv --output-md qc/missingness_loop003.md --seed 20251016
  python analysis/code/measure_validity_checks.py --config config/agent_config.yaml --output-md qc/measures_validity.md --output-json artifacts/measurement_validity_loop003.json
  ```

## Manuscript Linkage
- Each hypothesis maps to claims `[CLAIM:C1]`–`[CLAIM:C3]` in `papers/main/manuscript.tex` (stubs added in initial draft). The PAP freeze commit hash will be cited in the manuscript Methods section.

## Analysis Execution Order
1. **Data hygiene:** `analysis/code/describe_dataset.py`, `validate_metadata.py`, and `missingness_profile.py` run with seed 20251016; outputs referenced in `qc/data_overview_loop002.md`, `qc/metadata_validation.md`, and `qc/missingness_loop003.md`.
2. **Measurement dossier:** `analysis/code/measure_validity_checks.py` updates `qc/measures_validity.md` and `artifacts/measurement_validity_loop003.json`; all H1–H3 variables now have coding + DIF notes.
3. **Model estimation:** `analysis/code/run_models.py --hypothesis {H1|H2|H3}` executes ordered-logit / linear models with deterministic draws=300 for marginal effects.
4. **Imputation (if invoked):** `analysis/code/impute_and_stack.py` (placeholder) will implement multiple imputation using `miceforest` with `m=5`, `burn_in=50`, `iterations=50`, and seed 20251016 before confirmatory runs. PAP will be updated if MI is required due to MAR patterns.
5. **BH correction:** After confirmatory estimates are produced, apply Benjamini–Hochberg at q=0.05 per family (wellbeing, psychosocial) and populate `analysis/results.csv` with `family`, `targeted`, and `bh_in_scope`.
6. **Disclosure review:** Draft `qc/disclosure_check_loop_{loop}` with min cell sizes and suppression summary before any tables/figures leave the repo.

## Outstanding Tasks Before Freeze
1. Restore Semantic Scholar access (or obtain formal waiver). Loop 004 query (`lit/queries/loop_004/query_001.json`) still returns 403; PAP freeze deferred until a working credential or written waiver exists.
2. Register and freeze the PAP (`status: frozen`, `registry_url`, `freeze_commit`) once literature + QC gates are satisfied and the disclosure checklist template is in place.
3. Produce causal stance artifacts: `figures/dag_design.png` and `reports/identification.md`, clearly stating that current analyses are associational (descriptive) under SRS unless new design metadata arrive.
4. Maintain `qc/disclosure_check_loop_004.md` (template created this loop) and populate it automatically once tables/figures exist.
5. Confirm whether `mentalillness` has valid data in future drops; if not, update H2 controls and document the missing control in `analysis/results.csv` once confirmatory runs occur.

_No confirmatory analysis will begin until the status is set to `frozen` with registry details and a recorded commit/tag._
