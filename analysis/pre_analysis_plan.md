# Pre-Analysis Plan (Draft)

- Document status: Draft (not frozen)
- Generated: 2025-10-16T12:44:10Z
- Last updated: 2025-10-16T14:51:51Z
- Seed: 20251016
- Regeneration: `python analysis/code/bootstrap_setup.py --only pap`

## Scope

This draft PAP covers preliminary confirmatory planning for three wellbeing, socioeconomic, and relational hypotheses (HYP-001 through HYP-003). Status remains exploratory until design diagnostics and weighting strategy are finalized.

## Data

- Dataset: `childhoodbalancedpublic_original.csv` (n=14,443; p=718) as inspected on 2025-10-16.
- Inclusion: respondents with non-missing variables required per hypothesis.
- Survey design: TODO — pending confirmation of weight/strata/cluster variables. Analyses will assume SRS with weights=1 until metadata is verified.
- 2025-10-16T14:51:51Z — Weight/strata search re-run; no validated design variables found. HYP-003 confirmatory model will proceed under simple random sampling with unit weights until task `T-003` resolves.

## Hypotheses

1. **HYP-001 (wellbeing)** — Respondents reporting greater childhood emotional abuse will show lower adult self-love scores.
2. **HYP-002 (socioeconomic)** — Higher perceived childhood class associates with higher current net worth category.
3. **HYP-003 (relationships)** — Active religious practice is associated with preferring monogamy.

## Outcomes, Predictors, Controls

### HYP-001
- Outcome: `I love myself (2l8994l)` (Likert; treat as approximately continuous pending scale confirmation).
- Predictor: `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` (ordinal frequency).
- Controls: `selfage`, `gendermale`, `education`.
- Estimand: Survey-weighted mean difference across abuse frequency categories; fallback to ordinal regression if Likert assumptions break.

### HYP-002
- Outcome: `networth` (ordered categories).
- Predictor: `classchild` (ordered categories).
- Controls: `selfage`, `gendermale`, `education`.
- Estimand: Survey-weighted cumulative logit (proportional odds). Will assess proportional odds assumption.

### HYP-003 (updated 2025-10-16T14:51:51Z)
- Outcome: `monogamy` recoded to ordered categories {full monogamy, leaning monogamy, leaning nonmonogamy, full nonmonogamy}; codes outside these options (e.g., 'Prefer not to answer') will be set to missing.
- Predictor: `Do you *currently* actively practice a religion? (902tbll)` with four ordered responses (No, Yes/slightly, Yes/moderately, Yes/very seriously); modelled as categorical indicators with 'No' as reference.
- Controls: `selfage`, `gendermale`, `Are you in a romantic relationship?` (binary indicator `Are you in a romantic relationship?`).
- Estimand: Log-odds ratios from a simple-random-sample proportional-odds cumulative logit model quantifying how religious practice shifts the likelihood of preferring more monogamous relationship styles.
- Planned model: Fit `statsmodels.miscmodels.ordinal_model.OrderedModel` (logit link, robust HC1 covariance) with seed 20251016 via `analysis/code/run_pap_models.py --hypotheses HYP-003 --model-type ordered-logit --seed 20251016`; report category probabilities and average marginal effects for `full monogamy`.
- Sample exclusions: Drop observations with missing outcome/predictor/control values; enforce k=10 disclosure by collapsing the two non-monogamy categories if any post-exclusion cell count falls below threshold.
- Exploratory motivation (2025-10-16T14:45Z cross-tab): Under the SRS assumption, full monogamy prevalence ranges from 54% (non-practitioners) to 80% (very serious practitioners) with n≥34 in every religion-practice stratum (see `tables/exploratory_monogamy_by_religion.*`).

## Missing Data Strategy

- Profile missingness for all variables listed above.
- If missingness > 5% on key variables and plausibly MAR, implement multiple imputation with seed 20251016; otherwise use listwise deletion for preliminary analyses.

## Robustness Checks (pre-specified)

- **HYP-001:** (1) Recode abuse predictor into binary (any vs none). (2) Estimate proportional-odds model for the Likert outcome. (3) Contrast MI-pooled estimates with complete-case regression. (4) Repeat models on reduced-auxiliary imputations (`run_label=reduced_aux`) to isolate dependence on auxiliary covariates.
- **HYP-002:** (1) Collapse extreme net worth bins to ensure cell size ≥ 10. (2) Fit survey-weighted linear regression on net-worth midpoints. (3) Report MI-pooled vs complete-case proportional-odds estimates. (4) Repeat models on reduced-auxiliary imputations for stability assessment.
- **HYP-003:** (1) Restrict sample to respondents currently in relationships. (2) Collapse non-monogamy categories into a single group for sensitivity. (3) Re-estimate using multinomial logit to assess departures from proportional odds.

## Multiplicity

- Apply Benjamini–Hochberg FDR control at q=0.05 within the set {HYP-001, HYP-002, HYP-003} once confirmatory analyses commence.

## 2025-10-16T14:24Z — Reduced Auxiliary MI Diagnostics (Exploratory)

- Command: `python analysis/code/mice_prototype.py --dataset childhoodbalancedpublic_original.csv --config config/agent_config.yaml --seed 20251016 --n-imputations 20 --burn-in 10 --run-label reduced_aux --columns selfage biomale gendermale cis education classchild classteen classcurrent networth "I love myself (2l8994l)" "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"`
- Comparative checks: `analysis/code/review_imputed_vs_complete.py` (reduced_aux vs complete-case) and `analysis/code/compare_imputation_runs.py` (reduced_aux vs prototype) with seed 20251016.
- Findings: No variable showed >15% shift in weighted means or SDs relative to the prototype run; small-cell checks confirmed all public outputs mask counts <10. Variables absent from the reduced-aux run (religion, liberal identity, monogamy) drove no observable instability in wellbeing or net-worth summaries.
- Implication for PAP: Maintain reduced-auxiliary MI as a pre-specified robustness check for HYP-001 and HYP-002; document any confirmatory deviations alongside pooled-vs-complete-case contrasts.

## Deviations & Updates

- Any deviations from this draft must be documented in `analysis/pre_analysis_plan.md` with timestamped notes and reason. PAP will be frozen only after survey design validation.

## Reproducibility Notes

- Regenerate this draft with `python analysis/code/bootstrap_setup.py --only pap`.
- All analyses will honor the global project seed `20251016`.
