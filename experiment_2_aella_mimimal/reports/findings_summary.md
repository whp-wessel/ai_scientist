# Findings Summary: Religion Practice, Happiness, and Economic Standing (Loop 11)

- Prepared: 2025-11-04T20:35:05Z
- Seed: 20251016 (from `config/agent_config.yaml`)
- Dataset: `childhoodbalancedpublic_original.csv`
- Privacy guardrail: suppress cells with n < 10 (all referenced results exceed this threshold).

## Design Context
- Survey-weight metadata remain unavailable; analyses treat the file as a simple random sample (SRS) with Taylor linearized standard errors.
- Weighting placeholders in `docs/survey_design.yaml` and `config/agent_config.yaml` document this assumption and will be revised once calibrated weights, strata, and PSU identifiers arrive.
- Design checks and sponsor communications are logged in `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md`.
- Proxy calibration targets from the 2023 ACS (sex and age margins) now live in `docs/calibration_targets.yaml`. Deterministic pseudo-weights are generated via `python scripts/generate_pseudo_weights.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --targets docs/calibration_targets.yaml --out tables/pseudo_weights.csv --manifest artifacts/pseudo_weight_manifest.json`; convergence diagnostics are recorded in `artifacts/pseudo_weight_manifest.json`.

## H1: Active Religion Practice by Biological Sex
- Source tables: `tables/h1_religion_by_biomale.csv`, `tables/h1_religion_by_biomale_diff.csv` (manifest in `artifacts/h1_religion_by_biomale_manifest.json`).
- Weighted proportion of active practice (`religion > 0`):
  - Not biologically male (n = 5,931): 34.50% (SE 0.62%, 95% CI [33.29%, 35.71%]).
  - Biologically male (n = 8,512): 28.65% (SE 0.49%, 95% CI [27.69%, 29.61%]).
- Difference (male - non-male): -5.84 percentage points (SE 0.79, 95% CI [-7.39, -4.30]); non-male respondents report higher active practice.

## H2: Childhood Religious Strictness vs. Adult Happiness Change
- Source tables: `tables/h2_happiness_by_religion_strictness.csv`, `tables/h2_happiness_by_religion_strictness_diff.csv` (manifest in `artifacts/h2_religion_strictness_vs_happiness_manifest.json`).
- Mean self-reported change in happiness (scale from survey instrument):
  - Tercile 1 (`externalreligion = 0`, n = 5,224): 0.779 (SE 0.027).
  - Tercile 2 (`externalreligion` in [1, 2], n = 5,801): 0.675 (SE 0.026).
  - Tercile 3 (`externalreligion` in [3, 4], n = 3,411): 0.819 (SE 0.033).
- Bonferroni-adjusted pairwise comparisons:
  - Tercile 2 - Tercile 1: -0.104 (SE 0.037, 95% CI [-0.193, -0.015]).
  - Tercile 3 - Tercile 2: 0.144 (SE 0.042, 95% CI [0.043, 0.244]).
  - Tercile 3 - Tercile 1: 0.040 (SE 0.043, 95% CI [-0.062, 0.142]).
- Respondents with strict childhood religious environments (tercile 3) report the largest positive shift in adult happiness relative to childhood, while moderate strictness (tercile 2) trails both other groups.

## H3: Net Worth vs. Work/Career Satisfaction
- Source tables: `tables/h3_networth_work_satisfaction.csv`, `tables/h3_networth_work_satisfaction_diff.csv` (manifest in `artifacts/h3_networth_vs_work_manifest.json`).
- Mean satisfaction (scale -3 to 3) rises with net worth:
  - Heavy debt ($-100{,}000$ bracket, n = 348): -0.08 (SE 0.11).
  - Moderate debt ($-10{,}000$, n = 795): -0.72 (SE 0.07).
  - Net worth $0$ (n = 1,304): -0.84 (SE 0.05).
  - $100{,}000$ bracket (n = 3,763): 0.60 (SE 0.03).
  - $1{,}000{,}000$ bracket (n = 2,005): 1.01 (SE 0.04).
  - $10{,}000{,}000$ bracket (n = 460): 1.30 (SE 0.08).
  - $100{,}000{,}000$ or more (n = 360): 0.87 (SE 0.11).
- Differences vs. the lowest bracket:
  - $-10{,}000$ debt: -0.64 (SE 0.13, 95% CI [-0.89, -0.38]).
  - $100{,}000$: 0.68 (SE 0.11, 95% CI [0.46, 0.90]).
  - $1{,}000{,}000$: 1.09 (SE 0.11, 95% CI [0.87, 1.32]).
  - $10{,}000{,}000$: 1.38 (SE 0.13, 95% CI [1.12, 1.64]).
- Spearman correlation between net worth code and satisfaction: 0.32 (Pearson: 0.28); all brackets exceed the n ≥ 10 privacy threshold.

## Reproducibility Notes
- Regeneration commands:
  - `python scripts/analyze_h1_religion_by_biomale.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h1_religion_by_biomale.csv --diff-out tables/h1_religion_by_biomale_diff.csv --manifest artifacts/h1_religion_by_biomale_manifest.json`
  - `python scripts/analyze_h2_religion_strictness_vs_happiness.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h2_happiness_by_religion_strictness.csv --diff-out tables/h2_happiness_by_religion_strictness_diff.csv --manifest artifacts/h2_religion_strictness_vs_happiness_manifest.json`
  - `python scripts/analyze_h3_networth_vs_work_satisfaction.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h3_networth_work_satisfaction.csv --diff-out tables/h3_networth_work_satisfaction_diff.csv --manifest artifacts/h3_networth_vs_work_manifest.json`
- All computations are deterministic under the shared seed (20251016); no additional randomness introduced during reporting.
- When sponsor-provided design metadata arrive, rerun the scripts above with updated configuration to refresh the results under the final survey design.

## Planned Sensitivity Work
- A deterministic roadmap for addressing missing survey weights and replicate designs is now documented in `analysis/sensitivity_plan.md` (generated via `python scripts/generate_sensitivity_plan.py --out analysis/sensitivity_plan.md --timestamp 2025-11-04T08:24:44Z`).
- Scenario coverage includes (i) maintaining the current SRS benchmark, (ii) proxy weight calibration against external margins, (iii) design-effect multiplier sweeps, and (iv) pseudo-replicate construction via deterministic clustering.
- Associated backlog items T-013 through T-015 track implementation of these scenarios; updates will be logged in `analysis/decision_log.csv` and mirrored in `artifacts/state.json`.
