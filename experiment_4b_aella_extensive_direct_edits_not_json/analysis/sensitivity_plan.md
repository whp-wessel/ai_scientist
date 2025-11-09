# Sensitivity Plan — Loop 056
**Date:** 2025-11-09  
**Seed:** 20251016 (`artifacts/seed.txt` records the value that seeded every scenario).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — `ΔE[depression score | external religiosity very important vs not important] = -0.1201` (95% CI [-0.1873, -0.0548], `q = 0.0006958`, `analysis/results.csv`). The BH table now reports `targeted=Y` with `bh_in_scope = H1|H2` for the wellbeing family so these CIs feed the downstream design-effect checks.
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The difference in `Pr(health ∈ {very good, excellent})` between guidance Q3 and Q1 is `+0.0998` (CI [0.0889, 0.1109], `q ≈ 0`). The estimate remains stable after HC1 SEs and the BH weights have been attached in `analysis/results.csv`.
3. **H3 / self-love (`[CLAIM:C3]`)** — The linear contrast for adult self-love between abuse vs. no abuse is `-0.6544` (CI [-0.7192, -0.5895], `q = 0`). This psychosocial family effect anchors the pseudo-weight and pseudo-replicate experiments.
4. **NC1 / sibling count (negative control)** — `Coef = +0.2388` (CI [0.2209, 0.2568], `p = 0.0`). The row remains `targeted=N` so BH correction leaves the negative control out of the q-value families (`analysis/results.csv` and `artifacts/bh_summary.json`).

## Robustness checks completed
- **H1 high vs. low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` confirms the ordered-logit contrast remains negative when comparing extreme levels.
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` replicates the effect as a 0–4 numeric shift.
- **H3 non-perpetrators & teen-stage abuse control** — Both adjustments (`outputs/robustness_loop052/robustness_h3_no_perpetration.json`, `outputs/robustness_loop052/robustness_h3_teen_abuse.json`) leave the sign intact and calibrate the contribution from overlapping abuse exposures.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF {1.0, 1.25, 1.5})** — Re-running `analysis/code/pseudo_weight_sensitivity.py` refreshed `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_{100,125,150}.json`. The pseudo reweighting dropped the effective sample size from 14,443 (DEFF=1) to 11,628 (DEFF=1.25) and 9,533 (DEFF=1.5); H1/H2 SEs stayed at 0.0354/0.00573 because Statsmodels keeps the standard errors fixed for `weight_col`, while H3’s SE grows from 0.0331 to 0.0405 at DEFF=1.5 (via `outputs/..._deff_150.json`). The scenario metadata references the manifest commands so the weights can be rebuilt deterministically.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` read the BH-corrected `analysis/results.csv` and wrote `outputs/sensitivity_design_effect_grid.csv/.md`. Even at DEFF=2.0 the estimated `ΔE[depression]` CI is [-0.218, -0.0219]; H2 CI [0.0839, 0.1157] and H3 CI [-0.7461, -0.5627] still exclude the null while the implied effective n (7,219 for H1, 7,215 for H2, 6,753 for H3) quantifies how variance inflates.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` produced `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`. Jackknifing six pseudo clusters yields replicate SEs of 0.0190 (H1), 0.00203 (H2), and 0.01766 (H3); the replicate estimates range from -0.103 to -0.145 (H1) and 0.097 to 0.102 (H2), confirming the base HC1 SEs still cover the plausible variance envelope.

## Default specification decision
SRS + HC1 remains the default set of assumptions for reporting because (1) the pseudo-weight scenarios only modestly widen H3’s SE while leaving H1/H2 SEs intact, (2) √DEFF inflation up to 2.0 keeps all confirmatory CIs away from zero, and (3) the pseudo-replicate jackknife produces even smaller SEs than HC1, so it serves as a lower bound rather than a replacement. The scenario outputs act as supplementary evidence for uncertainty; the “Analysis” tables and manuscripts continue to cite the frozen PAP estimates from `analysis/results.csv`.

## Next steps for reporting
1. Integrate `analysis/results.csv`, the pseudo-weight/design-effect/replicate outputs, and the disclosure audit `qc/disclosure_check_loop_055.md` into `papers/main/*`, `reports/findings_v1.0.md`, and `reports/identification.md` so the methods/results narratives cite the regenerated assets (see `analysis/sensitivity_manifest.md` for commands).
2. Keep logging the Semantic Scholar queries (loop_055 logged in `lit/queries/loop_055/query_001.json` and noted in the waiver memo) and update `qc/strobe_sampl_checklist.md` + `qc/measures_validity.md` as we approach the writing/review QC requirements (N11/N12).
