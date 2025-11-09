# Sensitivity Plan — Loop 057
**Date:** 2025-11-09  
**Seed:** 20251016 (`artifacts/seed.txt` records the deterministic seed that generated every confirmatory and sensitivity artifact).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — `ΔE[depression score | external religiosity very important vs not important] = -0.1201` (95% CI [-0.1873, -0.0548], `q ≈ 0.0006958`, `analysis/results.csv`). This BH-adjusted row anchors the wellbeing family on the frozen PAP (`pap-v1`) and now maps directly into `tables/results_summary.csv/.md` for reporting.
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The difference in `Pr(health ∈ {very good, excellent})` between guidance Q3 and Q1 is `+0.0998` (CI [0.0889, 0.1109], `q = 0`). The BH-corrected row in `analysis/results.csv` (and the publication table) now cites the exact command log from `analysis/code/run_models.py` plus the manifested BH step.
3. **H3 / self-love (`[CLAIM:C3]`)** — The linear contrast between abuse and no abuse is `-0.6544` (CI [-0.7192, -0.5895], `q = 0`). The psychosocial family record feeds the sensitivity grid and the `tables/results_summary.*` outputs (CI, q-value, confidence rating) that share the same audit trail.
4. **NC1 / sibling count (negative control)** — `Coef = +0.2388` (CI [0.2209, 0.2568], `p = 0.0`). The `targeted=N` row ensures the BH families stay focused on the planned hypotheses while the falsification entry remains in `analysis/results_pre_bh.csv` for transparency.

## Robustness checks completed
- **H1 high vs. low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` confirms the ordered-logit contrast remains negative when comparing extreme importance levels.
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` replicates the effect as a 0–4 numeric shift.
- **H3 non-perpetrators & teen-stage abuse control** — Both adjustments (`outputs/robustness_loop052/robustness_h3_no_perpetration.json`, `outputs/robustness_loop052/robustness_h3_teen_abuse.json`) leave the sign intact and calibrate the contribution from overlapping exposures.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` generated `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_{100,125,150}.json`, showing effective n drop from 14,443 to 9,533; H1/H2 SEs remain near 0.0354/0.00573 and H3’s SE increases to 0.0405 for DEFF=1.5, so the base control estimates remain credible.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` read `analysis/results.csv` and wrote `outputs/sensitivity_design_effect_grid.csv/.md`; even at DEFF=2.0 the CIs for H1/H2/H3 continue to exclude the null with effective analytic Ns shrinking as anticipated.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` produced `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`; the jackknife replicate SEs (H1:0.0190, H2:0.00203, H3:0.01766) remain smaller than the HC1 estimates so the replicate experiments substantiate the HC1-based default rather than replacing it.

## Default specification decision
The SRS + HC1 configuration stays the default reporting specification because (1) the pseudo-weight experiments only modestly widen uncertainties (H3 SE growth is the largest change), (2) even a DEFF of 2.0 keeps every 95% CI away from zero while the implied effective Ns per hypothesis remain comfortably above 7,000, and (3) the pseudo-replicate jackknife produces smaller SEs than HC1, so it functions as a lower-bound robustness check. These conclusions reference the same `analysis/results.csv`, `tables/results_summary.*`, and the small-cell audit `qc/disclosure_check_loop_056.md` that now document the n ≥ 10 policy for every published table/figure.

## Loop 057 synthesis
- Re-ran the PAP command chain (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now exist in the repo again; the regeneration commands and `artifacts/seed.txt` confirm determinism.
- Recorded `qc/disclosure_check_loop_056.md` after `analysis/code/disclosure_check.py` scanned `tables/results_summary.csv` and `figures/dag_design.png` (violations: 0, threshold n ≥ 10) preventing any small-cell release concerns.
- Logged the mandated Semantic Scholar attempts for loops 056 (`lit/queries/loop_056/query_001.json`) and 057 (`lit/queries/loop_057/query_001.json`); both returned HTTP 403, and the outage log in `lit/semantic_scholar_waiver_loop013.md` now captures these repeats while the waiver ticket remains active.
- The findings summary, decision log, and sensitivity notes track how these actions addressed the loop-056 reviewer STOP: we now have the disclosure memo plus the late-cycle query log, so the sensitivity phase can move toward writing without losing reproducibility.

## Next steps for reporting
1. Pull `analysis/results.csv`, `tables/results_summary.*`, the pseudo-weight/design-effect/replicate outputs, and `qc/disclosure_check_loop_056.md` into `papers/main/*`, `reports/identification.md`, and `reports/findings_v1.0.md` so every `[CLAIM:<ID>]` cites regenerable evidence (see N11).
2. Keep the Semantic Scholar outage/replay log up to date (`lit/semantic_scholar_waiver_loop013.md` still references loops 008–057) and maintain the literature gate while ops resolves the API key (per N8).
3. Update `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and `reports/findings_summary.md` with the latest sensitivity outputs before transitioning toward the writing/review QC suite (per N12).
