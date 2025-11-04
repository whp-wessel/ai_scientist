# Findings Summary: Religion Practice and Happiness (Loop 8)

- Prepared: 2025-11-04T08:17:22Z
- Seed: 20251016 (from `config/agent_config.yaml`)
- Dataset: `childhoodbalancedpublic_original.csv`
- Privacy guardrail: suppress cells with n < 10 (all referenced results exceed this threshold).

## Design Context
- Survey-weight metadata remain unavailable; analyses treat the file as a simple random sample (SRS) with Taylor linearized standard errors.
- Weighting placeholders in `docs/survey_design.yaml` and `config/agent_config.yaml` document this assumption and will be revised once calibrated weights, strata, and PSU identifiers arrive.
- Design checks and sponsor communications are logged in `reports/design_metadata_brief.md` and `reports/sponsor_follow_up.md`.

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

## Reproducibility Notes
- Regeneration commands:
  - `python scripts/analyze_h1_religion_by_biomale.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h1_religion_by_biomale.csv --diff-out tables/h1_religion_by_biomale_diff.csv --manifest artifacts/h1_religion_by_biomale_manifest.json`
  - `python scripts/analyze_h2_religion_strictness_vs_happiness.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h2_happiness_by_religion_strictness.csv --diff-out tables/h2_happiness_by_religion_strictness_diff.csv --manifest artifacts/h2_religion_strictness_vs_happiness_manifest.json`
- All computations are deterministic under the shared seed (20251016); no additional randomness introduced during reporting.
- When sponsor-provided design metadata arrive, rerun the scripts above with updated configuration to refresh the results under the final survey design.

## Planned Sensitivity Work
- A deterministic roadmap for addressing missing survey weights and replicate designs is now documented in `analysis/sensitivity_plan.md` (generated via `python scripts/generate_sensitivity_plan.py --out analysis/sensitivity_plan.md --timestamp 2025-11-04T08:24:44Z`).
- Scenario coverage includes (i) maintaining the current SRS benchmark, (ii) proxy weight calibration against external margins, (iii) design-effect multiplier sweeps, and (iv) pseudo-replicate construction via deterministic clustering.
- Associated backlog items T-013 through T-015 track implementation of these scenarios; updates will be logged in `analysis/decision_log.csv` and mirrored in `artifacts/state.json`.
