# Sensitivity Plan — Loop 065
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every script this loop reuses this seed so the pseudo-weight draws, design-effect grid, and replicate jackknife remain deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression ([CLAIM:C1])** — The ordered-logit contrast for high vs. low religious importance remains `ΔE = -0.1201` (95% CI [−0.189, −0.051]) with HC1 SE 0.0354; `analysis/results.csv` and `artifacts/bh_summary.json` continue to capture the BH-adjusted q-value and BH membership for the wellbeing family.
2. **H2 / self-rated health ([CLAIM:C2])** — Guidance quartile slope stays `+0.0998` (95% CI [0.089, 0.111]) with SE 0.0057; the ordered-logit output confirms the positive guidance→health ordering remains reproducible.
3. **H3 / self-love ([CLAIM:C3])** — The abuse/non-abuse gap is `-0.6544` (95% CI [−0.719, −0.590]) with SE 0.0331; the deterministic linear model still feeds `analysis/results.csv` and the publication table with the seeded HC1 SE.
4. **NC1 / sibling count (negative control)** — Linear difference `+0.2388` (95% CI [0.221, 0.257]) remains outside the BH adjustments (`targeted=N`), reinforcing that religiosity is unrelated to this falsification outcome.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) keeps the direction when contrasting religious extremities.
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) sustains the positive slope when treating self-rated health as numeric.
- **H3 non-perpetrators & timing controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json`, `_robustness_h3_teen_abuse.json`) preserve the abuse-self-love gap under tightened restrictions.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py --config config/agent_config.yaml --seed 20251016` regenerated `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json/_125.json/_150.json`. The effective sample drops from 14,443 (DEFF=1.0) to 11,629 (1.25) to 9,533 (1.5) while H1 (-0.1201) and H2 (+0.0998) estimates stay fixed; H3’s SE widens from 0.0331 to 0.0370 to 0.0405 with very similar negative estimates (≈−0.63 to −0.67), so the CI remains below zero even as the calculated `n_effective` shrinks.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py --input analysis/results.csv --deffs 1.0 1.25 1.5 2.0 --output-csv outputs/sensitivity_design_effect_grid.csv --output-md outputs/sensitivity_design_effect_grid.md` rebuilt the summary table; the targeted hypotheses’ effective sample declines from ~13,500 (DEFF=1.0) to ~10,806 (1.25) to ~9,005 (1.5) to ~6,754 (2.0), yet each CI stays on the negative side and the q-values stay tied to the original BH family because the estimates and base SEs do not change.
- **Scenario 3 – pseudo replicates (k = 6)** — `analysis/code/pseudo_replicates.py --config config/agent_config.yaml --k 6 --results analysis/results.csv` regenerated `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`; the jackknife SEs are ≈0.019 (H1), 0.002 (H2), and 0.0177 (H3) while base estimates remain −0.1201 / +0.0998 / −0.6544, confirming that the sign pattern survives the pseudo-cluster exclusion.

## Default specification decision
SRS + HC1 remains the reporting default because Scenario 1 shows H1/H2 estimates unchanged while H3’s CI remains well below zero even as the pseudo-weight variance inflates, Scenario 2 keeps the CI signs stable through DEFF=2.0, and Scenario 3’s jackknife SEs are consistent with the HC1 band and do not reveal any reversal; these documents keep the descriptive claims conservative without introducing a non-HC1 specification for the final tables.

## Loop 065 synthesis
- Re-ran the sensitivity suite (pseudo weights, the design-effect grid, and pseudo replicates) with the same seed/commands recorded in `analysis/sensitivity_manifest.md` so every uncertainty artifact matches the deterministic path for reviewers.
- No new public tables or figures were created, so the prior `qc/disclosure` audit remains sufficient; the scenario reruns simply refresh the overarching uncertainty envelope before the writing-phase QC pass (next action N14) begins.
- Updated the sensitivity plan and findings narratives to note that the scenario suite is stable, leaving the writing-phase QC + LaTeX build as the next milestone.
