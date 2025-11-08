status: draft
phase: pap
last_updated: 2025-11-07
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
- **Seed:** 20251016 (propagated to all scripts and random procedures).
- **Disclosure threshold:** n ≥ 10 per config.

## Hypotheses Under Consideration
### H1 — Childhood Religious Adherence & Adult Depression (Family: wellbeing)
- **Outcome:** Likert 1–5 `wz901dj` (“I tend to suffer from depression”).
- **Predictor:** Ordinal `externalreligion` (importance of childhood religious adherence).
- **Controls:** Age (`selfage`), gender indicators (`biomale`, `gendermale`, `cis`), childhood class (`classchild`).
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
- **Controls:** Age, gender, current class (`classcurrent`), teen class (`classteen`).
- **Estimand:** Difference in predicted probability of reporting “very good/excellent” health between top and bottom guidance quartiles (ordered logit + post-estimation).
- **Robustness:** (a) Treat health as continuous 1–5. (b) Limit to respondents without chronic illness indicator `mentalillness`.
- **Command stub:** same script with `--hypothesis H2`.

### H3 — Childhood Abuse & Adult Self-Love (Family: psychosocial)
- **Outcome:** Likert `2l8994l` (“I love myself”).
- **Predictor:** Binary `mds78zu` (parents verbally/emotionally abusive ages 0–12).
- **Controls:** Age, gender, sibling count (`siblingnumber`), socioeconomic controls.
- **Estimand:** Average difference in self-love score between abuse vs no abuse (survey-weighted linear regression).
- **Robustness:** (a) Add teen-stage abuse indicator to check cumulative exposure. (b) Exclude respondents who reported perpetration (`rapist` == 1) to test sensitivity.
- **Command stub:** same script with `--hypothesis H3`.

## Data Management Plan
- Raw data remain immutable under `data/raw/`.
- Recode scripts will live under `analysis/code/` and write outputs to `data/clean/` with filenames containing the seed (e.g., `childhood_clean_seed20251016.parquet`).
- All transformations logged in `analysis/data_processing.md` (to be created) and referenced in `analysis/decision_log.csv`.

## Manuscript Linkage
- Each hypothesis maps to claims `[CLAIM:C1]`–`[CLAIM:C3]` in `papers/main/manuscript.tex` (stubs added in initial draft). The PAP freeze commit hash will be cited in the manuscript Methods section.

## Outstanding Tasks Before Freeze
1. Populate `lit/evidence_map.csv` with ≥3 DOI-backed sources relevant to H1–H3.
2. Create `analysis/code/run_models.py` implementing survey-aware estimators with CLI interface.
3. Complete `qc/measures_validity.md` with reliability metrics for included scales.
4. Document missingness patterns in `qc/data_checks.md`.

_No confirmatory analysis will begin until the status is set to `frozen` with registry details and a recorded commit/tag._
