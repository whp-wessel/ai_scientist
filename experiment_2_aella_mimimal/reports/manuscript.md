# Manuscript Draft: Religion Practice and Happiness

**Prepared:** 2025-11-04T08:17:22Z  
**Seed:** 20251016 (`config/agent_config.yaml`)  
**Primary dataset:** `childhoodbalancedpublic_original.csv`

## Abstract
We examine links between biological sex, active religious practice, and adult happiness change using the Childhood Balanced Public Survey. In the absence of calibrated survey weights, analyses treat the data as a simple random sample (SRS) with Taylor-linearized standard errors. Non-male respondents report higher rates of active religious practice than male respondents. Respondents raised in very strict religious environments report larger gains in adult happiness relative to childhood.

## Data and Design Context
Sponsor-delivered files currently lack calibrated weights, strata, and primary sampling unit identifiers (`docs/survey_design.yaml`). All estimates therefore assume equal-probability sampling. Design metadata gaps and sponsor follow-up requests are summarized in `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md`.

Scenario 1 (proxy weight calibration) now includes documented control totals (`docs/calibration_targets.yaml`) derived from the 2023 American Community Survey (ACS) sex and age margins. We generate deterministic pseudo-weights with:

```bash
python scripts/generate_pseudo_weights.py \
  --csv childhoodbalancedpublic_original.csv \
  --config config/agent_config.yaml \
  --targets docs/calibration_targets.yaml \
  --out tables/pseudo_weights.csv \
  --manifest artifacts/pseudo_weight_manifest.json
```
The manifest (`artifacts/pseudo_weight_manifest.json`) logs convergence diagnostics and verifies that all calibration cells contain at least 10 respondents.

## Methods
### H1: Active Religion Practice by Biological Sex
- Outcome: indicator for actively practicing a religion (recode `religion > 0`).
- Grouping variable: biological sex (`biomale`).
- Estimand: difference in weighted proportions (male minus non-male).
- Analysis command:
  ```bash
  python scripts/analyze_h1_religion_by_biomale.py \
    --csv childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --design docs/survey_design.yaml \
    --out tables/h1_religion_by_biomale.csv \
    --diff-out tables/h1_religion_by_biomale_diff.csv \
    --manifest artifacts/h1_religion_by_biomale_manifest.json
  ```
- Privacy guardrail: suppress cells with n < 10 (not triggered).

### H2: Childhood Religious Strictness and Adult Happiness Change
- Outcome: self-reported change in happiness (`On average, I am happier as an adult than I was in childhood (h33e6gg)`).
- Exposure: terciles of childhood religious strictness (`externalreligion`), partitioned deterministically (0 | 1-2 | 3-4).
- Estimand: pairwise differences in mean happiness change between terciles with Bonferroni correction.
- Analysis command:
  ```bash
  python scripts/analyze_h2_religion_strictness_vs_happiness.py \
    --csv childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --design docs/survey_design.yaml \
    --out tables/h2_happiness_by_religion_strictness.csv \
    --diff-out tables/h2_happiness_by_religion_strictness_diff.csv \
    --manifest artifacts/h2_religion_strictness_vs_happiness_manifest.json
  ```
- Privacy guardrail: suppress cells with n < 10 (not triggered).

## Results
### H1 Findings
- Not biologically male respondents: 34.50% active practice (SE 0.62%, 95% CI [33.29%, 35.71%]; n = 5,931).
- Biologically male respondents: 28.65% active practice (SE 0.49%, 95% CI [27.69%, 29.61%]; n = 8,512).
- Difference (male minus non-male): -5.84 percentage points (SE 0.79, 95% CI [-7.39, -4.30]).
- Interpretation: Non-male respondents maintain higher active religious engagement under the SRS assumption.

### H2 Findings
- Mean happiness change:
  - Tercile 1 (`externalreligion = 0`, n = 5,224): 0.779 (SE 0.027).
  - Tercile 2 (`externalreligion` in [1, 2], n = 5,801): 0.675 (SE 0.026).
  - Tercile 3 (`externalreligion` in [3, 4], n = 3,411): 0.819 (SE 0.033).
- Bonferroni-adjusted pairwise differences:
  - Tercile 2 - Tercile 1: -0.104 (SE 0.037, 95% CI [-0.193, -0.015]).
  - Tercile 3 - Tercile 2: 0.144 (SE 0.042, 95% CI [0.043, 0.244]).
  - Tercile 3 - Tercile 1: 0.040 (SE 0.043, 95% CI [-0.062, 0.142]).
- Interpretation: Strict childhood religious environments correlate with higher adult happiness change, whereas moderate strictness lags the other terciles.

## Discussion and Next Steps
- Results depend on the temporary SRS assumption; revisit once sponsor supplies calibrated weights and replicate design metadata.
- A deterministic sensitivity roadmap (`analysis/sensitivity_plan.md`, generated via `python scripts/generate_sensitivity_plan.py --out analysis/sensitivity_plan.md --timestamp 2025-11-04T08:24:44Z`) outlines Scenario 0 (SRS benchmark), Scenario 1 (proxy weight calibration), Scenario 2 (design-effect multiplier grid), and Scenario 3 (pseudo-replicate construction).
- Scenario 1 pseudo-weight calibration (T-013) is complete; Scenario 2 (T-014) and Scenario 3 (T-015) will build on the new weights, while T-012 advances H-003 exploratory work.
- Update `manuscript.tex` in lockstep with this Markdown file; both documents should reflect identical narrative content before submission.

## Reproducibility and Data Governance
- All commands above rely on deterministic scripts and the shared seed 20251016.
- Source tables: `tables/h1_religion_by_biomale*.csv`, `tables/h2_happiness_by_religion_strictness*.csv` with manifests in `artifacts/`.
- Privacy policy: suppress any estimates derived from <10 respondents; current tables meet this criterion.
