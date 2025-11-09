# Sensitivity Plan — Loop 053
**Date:** 2025-11-09
**Seed:** 20251016 (recorded in `artifacts/seed.txt`)

## Confirmatory estimates and falsification
1. **H1 / well-being ([CLAIM:C1])** — Ordered-logit difference for the highest vs lowest religiosity importance is **–0.120** (95% CI [–0.187, –0.055], q=0.00070) after controlling for demographics (`analysis/results.csv`).
2. **H2 / self-rated health ([CLAIM:C2])** — Ordered-logit predicted probability gap is **+0.100** (95% CI [0.089, 0.111], q≈0) for adults whose parents provided guidance in the top quartile vs bottom quartile.
3. **H3 / self-love ([CLAIM:C3])** — Linear difference of **–0.654** (95% CI [–0.719, –0.590], q≈0) for respondents reporting childhood emotional abuse vs none, holding the standard controls.
4. **NC1 / sibling count (negative control)** — Linear change **+0.239** (CI [0.221, 0.257]) with religiosity; targeted=N so the estimate documents model stability rather than a hypothesis test.

All confirmatory runs rely on the SRS assumption (no weights yet) and HC1-derived uncertainties; sample sizes exceed the n≥10 disclosure threshold (`qc/disclosure_check_loop_052.md`).

## Robustness checks completed (Loop 052 commands captured in `outputs/robustness_loop052/*.json`)
- **H1 high vs low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` reports ΔE[depression] = –0.088, 95% CI [–0.163, –0.012], n=14,438, confirming the direction and magnitude persist when collapsing the ordered predictor to a binary contrast.
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` shows a per-point guidance increase of 0.0785 on the 0–4 health scale (CI [0.0696, 0.0874], n=14,430) even when the outcome is treated as continuous instead of ordered logits.
- **H3 non-perpetrators** — `outputs/robustness_loop052/robustness_h3_no_perpetration.json` restricts the sample to respondents who did not report perpetration; the abuse gap remains –0.650 (CI [–0.720, –0.580], n=11,769).
- **H3 teen-stage abuse control** — `outputs/robustness_loop052/robustness_h3_teen_abuse.json` adds teen-abuse exposure (`v1k988q_binary`) to the control set; the abuse coefficient shrinks toward –0.264 (CI [–0.374, –0.154]) but retains directionality, suggesting teen exposures explain part of the observed adult gap.

These robustness outputs share the same seed (20251016) and commands in `analysis/code/robustness_checks.py`, so reproduction is deterministic.

## Planned sensitivity scenarios (architecture for the upcoming sensitivity phase)
1. **Scenario 1 — Pseudo weights:** simulate plausible design-weight scaling factors (DEFF ∈ {1.0, 1.25, 1.5}) by creating a `pseudo_weight` column that multiplies the nominal sampling weight (1.0 under SRS). We will re-run `analysis/code/run_models.py` for H1–H3 with `--weight pseudo_weight` (new flag to be added or by modifying the DataFrame before fitting) and record the adjusted standard errors/CI bounds. Example placeholder command (to be implemented):
   ```bash
   python analysis/code/pseudo_weight_sensitivity.py --scenarios 1.0 1.25 1.5 --seed 20251016 --output-dir outputs/sensitivity_pseudo_weights
   ```
   The script will log the ratio, n, and UI. This clarifies how much the H1–H3 CIs would widen if a moderate cluster/deweight effect were present.
2. **Scenario 2 — Design-effect grid:** treat the observed HC1 SEs as if they were inflated by a design effect. For DEFF ∈ {1.0, 1.25, 1.5, 2.0}, compute `se_adj = se * sqrt(DEFF)` for each targeted estimate in `analysis/results.csv`, and recompute 95% CIs/p-values accordingly. We will script this under `analysis/code/design_effect_grid.py` and generate a CSV/Markdown table showing the new limits plus the implied effective sample size (`n_eff = n / DEFF`). This quantifies how much the uncertainty, not the point estimate, responds to survey design mis-specification.
3. **Scenario 3 — Pseudo replicates:** construct `k=6` pseudo-replicate datasets by randomly stratifying the sample into pseudo-clusters (e.g., `classchild_score` quintiles + `classcurrent_score`), re-fitting each confirmatory model, and using the replicate variance to estimate design-based SEs (`Var_rep = (k − 1)^−1 Σ (θ_r − θ̄)^2`). We will capture the replicate estimates/SEs in `outputs/sensitivity_replicates/` and include the command metadata (seed, clustering heuristic, replicates, script path). This builds a rough analog to BRR/Jackknife until actual survey weights arrive.

Each scenario will log the `seed` and all commands within a new `MANIFEST.md` entry (for example, in `analysis/sensitivity_manifest.md`), so the sensitivity results remain reproducible.

## Executed scenario summaries (loop 054)
- **Pseudo-weight scenarios**: lognormal pseudo weights calibrated to DEFF = 1.0 / 1.25 / 1.5 (see `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_{100,125,150}.json`). The outputs record the generated weight CVs, effective sample sizes, and the weighted H1–H3 contrasts so readers can see how moderate weight variability widens the ordered-logit and linear CIs without moving the point estimates. Commands + metadata are in `analysis/sensitivity_manifest.md`.
- **Design-effect grid**: inflated the BH-adjusted SEs (`analysis/results.csv`) by √DEFF for DEFF ∈ {1.0, 1.25, 1.5, 2.0} and recomputed 95% CIs/p-values plus implied `n_effective`. Refer to `outputs/sensitivity_design_effect_grid.csv/.md` for the adjusted intervals and guidance on uncertainty growth as DEFF climbs.
- **Pseudo replicates**: `k=6` jackknife replicates leave out pseudo-clusters defined by `classchild_score + classcurrent_score`; the summary file `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` lists each replicate’s estimate, cluster omitted, and variance-based SE relative to the base BH estimate.

## Next steps for reporting
- Integrate the confirmatory + sensitivity outputs (`analysis/results.csv`, `outputs/sensitivity_*`, `analysis/sensitivity_manifest.md`) into `reports/findings_v1.0.md` and the manuscript narrative so the revised effect sizes, CIs, and design-effect grid are auditable.
- Refresh `papers/main/imrad_outline.md`, `papers/main/manuscript.*`, and `reports/identification.md` to cite the new [CLAIM:<ID>] story, note the pseudo-weight/design-effect/pseudo-replicate robustness, and reference `qc/disclosure_check_loop_054.md`.
- Keep the Semantic Scholar waiver log, disclosure checklist, and `analysis/decision_log.csv` aligned while the credential outage persists, then turn attention to the writing-phase QC items called out in `artifacts/state.json` (N11/N12).
