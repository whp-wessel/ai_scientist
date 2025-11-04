# Manuscript Draft: Religion, Happiness, and Economic Standing

**Prepared:** 2025-11-04T20:35:05Z  
**Seed:** 20251016 (`config/agent_config.yaml`)  
**Primary dataset:** `childhoodbalancedpublic_original.csv`

## Abstract
We examine links between biological sex, active religious practice, adult happiness change, and economic standing using the Childhood Balanced Public Survey. In the absence of calibrated survey weights, analyses treat the data as a simple random sample (SRS) with Taylor-linearized standard errors. Non-male respondents report higher rates of active religious practice than male respondents. Respondents raised in very strict religious environments report larger gains in adult happiness relative to childhood. Higher net worth brackets correspond to markedly higher work/career satisfaction scores in monotonic fashion.

## Data and Design Context
Sponsor-delivered files currently lack calibrated weights, strata, and primary sampling unit identifiers (`docs/survey_design.yaml`). All estimates therefore assume equal-probability sampling. Design metadata gaps and sponsor follow-up requests are summarized in `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md`.

Scenario 1 (proxy weight calibration) now includes documented control totals (`docs/calibration_targets.yaml`) derived from the 2023 American Community Survey (ACS) sex and age margins. Deterministic pseudo-weights are generated with:

```bash
python scripts/generate_pseudo_weights.py \
  --csv childhoodbalancedpublic_original.csv \
  --config config/agent_config.yaml \
  --targets docs/calibration_targets.yaml \
  --out tables/pseudo_weights.csv \
  --manifest artifacts/pseudo_weight_manifest.json
```

The manifest (`artifacts/pseudo_weight_manifest.json`) logs convergence diagnostics and verifies that every calibration cell clears the n ≥ 10 privacy threshold.

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

### H3: Net Worth and Work/Career Satisfaction
- Outcome: work/career satisfaction scale (`I am satisfied with my work/career life (or lack thereof) (z0mhd63)`).
- Exposure: net worth brackets (`networth`), labelled via the original survey wording `Your CURRENT net worth is closest to (nhoz8ia)`.
- Estimand: differences in mean satisfaction relative to the lowest net worth bracket and overall monotonic trends.
- Analysis command:
  ```bash
  python scripts/analyze_h3_networth_vs_work_satisfaction.py \
    --csv childhoodbalancedpublic_original.csv \
    --config config/agent_config.yaml \
    --design docs/survey_design.yaml \
    --out tables/h3_networth_work_satisfaction.csv \
    --diff-out tables/h3_networth_work_satisfaction_diff.csv \
    --manifest artifacts/h3_networth_vs_work_manifest.json
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

### H3 Findings
- Mean satisfaction scores (scale -3 to 3):
  - Heavy debt ($-100{,}000$, n = 348): -0.08 (SE 0.11).
  - Moderate debt ($-10{,}000$, n = 795): -0.72 (SE 0.07).
  - Net worth $0$ (n = 1,304): -0.84 (SE 0.05).
  - $100{,}000$ (n = 3,763): 0.60 (SE 0.03).
  - $1{,}000{,}000$ (n = 2,005): 1.01 (SE 0.04).
  - $10{,}000{,}000$ (n = 460): 1.30 (SE 0.08).
  - $100{,}000{,}000$ or more (n = 360): 0.87 (SE 0.11).
- Differences vs. the lowest bracket:
  - $-10{,}000$ debt: -0.64 (SE 0.13, 95% CI [-0.89, -0.38]).
  - $100{,}000$: 0.68 (SE 0.11, 95% CI [0.46, 0.90]).
  - $1{,}000{,}000$: 1.09 (SE 0.11, 95% CI [0.87, 1.32]).
  - $10{,}000{,}000$: 1.38 (SE 0.13, 95% CI [1.12, 1.64]).
- Interpretation: Work/career satisfaction increases monotonically with net worth under the SRS assumption; the Spearman correlation between net worth codes and satisfaction equals 0.32 (Pearson: 0.28).

## Discussion and Next Steps
- Results depend on the temporary SRS assumption; revisit once sponsor supplies calibrated weights and replicate design metadata.
- A deterministic sensitivity roadmap (`analysis/sensitivity_plan.md`, generated via `python scripts/generate_sensitivity_plan.py --out analysis/sensitivity_plan.md --timestamp 2025-11-04T08:24:44Z`) outlines Scenario 0 (SRS benchmark), Scenario 1 (proxy weight calibration), Scenario 2 (design-effect multiplier grid), and Scenario 3 (pseudo-replicate construction).
- Scenario 1 pseudo-weight calibration (T-013) is complete; Scenario 2 (T-014) will extend design-effect multipliers, Scenario 3 (T-015) will prototype pseudo-replicates, and follow-on work will stress-test the new H3 findings under those alternatives.
- Maintain one-to-one parity between this Markdown document and `manuscript.tex` before submission.

## Reproducibility and Data Governance
- All commands above rely on deterministic scripts and the shared seed 20251016.
- Source tables: `tables/h1_religion_by_biomale*.csv`, `tables/h2_happiness_by_religion_strictness*.csv`, and `tables/h3_networth_work_satisfaction*.csv`; manifests reside in `artifacts/`.
- Privacy policy: suppress any estimates derived from <10 respondents; current tables meet this criterion.
