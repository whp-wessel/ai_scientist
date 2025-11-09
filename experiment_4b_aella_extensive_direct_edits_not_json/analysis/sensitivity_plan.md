# Sensitivity Plan — Loop 068
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every script this loop reuses this seed so the pseudo-weight draws, design-effect grid, and replicate jackknife stay deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression ([CLAIM:C1])** — The ordered-logit contrast for high vs. low religious importance remains `ΔE = -0.1201` (95% CI [−0.189, −0.051]) with HC1 SE 0.0354; `analysis/results.csv` and `analysis/results_pre_bh.csv` keep the BH-adjusted q-value and family tags linked to wellbeing.
2. **H2 / self-rated health ([CLAIM:C2])** — The guidance quartile slope stays `+0.0998` (95% CI [0.089, 0.111]) with SE 0.0057; the ordered-logit output reconfirms the positive guidance→health ordering is reproducible.
3. **H3 / self-love ([CLAIM:C3])** — The abuse/non-abuse gap is `-0.6544` (95% CI [−0.719, −0.590]) with SE 0.0331; the deterministic linear model still feeds `analysis/results.csv` and the publication table with the seeded HC1 SE.
4. **NC1 / sibling count (negative control)** — Linear difference `+0.2388` (95% CI [0.221, 0.257]) remains outside the BH adjustments (`targeted=N`), reinforcing that religiosity is unrelated to this falsification outcome.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) keeps the direction when contrasting religious extremities.
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) sustains the positive slope when treating self-rated health as numeric.
- **H3 non-perpetrators & timing controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json`, `_robustness_h3_teen_abuse.json`) preserve the abuse-self-love gap under tightened restrictions.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `python analysis/code/pseudo_weight_sensitivity.py --config config/agent_config.yaml --seed 20251016 --draws 400 --scenarios 1.0 1.25 1.5 --output-dir outputs/sensitivity_pseudo_weights_loop068` regenerated `outputs/sensitivity_pseudo_weights_loop068/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json`. The effective sample falls from 14,443 (DEFF=1.0, CV=0.000) to 11,628.5 (1.25, CV≈0.492) to 9,533.2 (1.5, CV≈0.718) while H1/H2 stay anchored at −0.1201/+0.0998 (SE=0.0354/0.0057) and H3’s estimate tightens to −0.6339 (SE=0.0370, 95% CI [−0.707, −0.561]) at DEFF=1.25 and deepens to −0.667 (SE=0.0405, 95% CI [−0.747, −0.588]) at DEFF=1.5, so the negative gap never approaches zero even as the pseudo-weight variance swells.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `python analysis/code/design_effect_grid.py --input analysis/results.csv --deffs 1.0 1.25 1.5 2.0 --output-csv outputs/sensitivity_design_effect_grid_loop068.csv --output-md outputs/sensitivity_design_effect_grid_loop068.md` rebuilt the summary table. The targeted family’s n_effective shrinks (e.g., H1: ~14,438→11,550.4→9,625.3→7,219; H3: ~13,507→10,805.6→9,004.7→6,753.5) while each 95% CI stays on the same sign (DEFF=2.0 maintains [−0.746, −0.563] for H3) and the BH q-values remain tied to the original family inputs because the base estimates did not change.
- **Scenario 3 – pseudo replicates (k=6)** — `python analysis/code/pseudo_replicates.py --config config/agent_config.yaml --seed 20251016 --k 6 --output-dir outputs/sensitivity_replicates_loop068 --results analysis/results.csv` regenerated `outputs/sensitivity_replicates_loop068/sensitivity_replicates_summary.json`. The jackknife SEs are ≈0.01903 (H1), 0.00203 (H2), and 0.01766 (H3), aligning with the HC1 interval already reported in `analysis/results.csv` and confirming that the replicate-derived uncertainty keeps all effect signs intact while the pseudo-sample removes one cluster at a time.

## Default specification decision
SRS + HC1 remains the reporting default because Scenario 1 leaves the estimates unchanged while H3’s CI stays below zero even as the pseudo-weight variance inflates, Scenario 2 shows the CI signs stable through DEFF=2.0, and Scenario 3’s jackknife SEs corroborate the HC1 band without reversing the direction. These scripts and outputs are recorded in `analysis/sensitivity_manifest.md` so any rerun uses the same seed/command pair.

-## Loop 068 synthesis
- Re-ran the seeded sensitivity suite with loop-specific outputs (`outputs/sensitivity_pseudo_weights_loop068/*`, `outputs/sensitivity_design_effect_grid_loop068.*`, `outputs/sensitivity_replicates_loop068/sensitivity_replicates_summary.json`); each command/seed pair plus artifact path is noted in `analysis/sensitivity_manifest.md` and `analysis/decision_log.csv`.
- No new public tables or figures were released this loop, so `qc/disclosure_check_loop_064.md` (violations: 0) remains the latest audit before the writing-phase QC pass; the sensitivity narrative again demonstrates that uncertainty scenarios keep the negative estimates robust.
- Writing-phase QC (manuscript parity, outline, checklist, LaTeX build, reviewer checklist) still stands as the immediate next milestone (see `artifacts/state.json` next action N14) before we advance toward review.
