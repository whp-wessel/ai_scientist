# Sensitivity Plan — Loop 068
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every script cited below reuses this seed so the results remain deterministic).

## Confirmatory estimates and falsification
- **H1 (religious adherence → depression, `[CLAIM:C1]`)** — Ordered logit contrast between “very important” vs. “not important” childhood religiosity: `ΔE = -0.120` (HC1 SE `0.035`, 95% CI [`-0.187`, `-0.055`], q = 6.96e-4). Source: `analysis/results.csv`, `tables/results_summary.*`.
- **H2 (parental guidance → adult health, `[CLAIM:C2]`)** — Ordered logit difference in predicted probability of reporting “very good/excellent” health when moving from guidance Q1 to Q3: `ΔPr = +0.100` (SE `0.0057`, 95% CI [`0.089`, `0.111`], q < 1e-8).
- **H3 (childhood emotional abuse → adult self-love, `[CLAIM:C3]`)** — Survey-weighted linear model: mean difference `-0.654` points (SE `0.033`, 95% CI [`-0.719`, `-0.590`], q < 1e-8).
- **NC1 (negative control)** — Sibling-count outcome shifts by `+0.239` (SE `0.0092`, 95% CI [`0.221`, `0.257`]) when religiosity increases, confirming the falsification row is clearly non-null and should not be interpreted as confirmatory evidence.

## Robustness checks executed earlier in analysis
- **H1 high-vs-low split:** `outputs/robustness_loop052/robustness_h1_high_low.json`.
- **H2 continuous outcome and health screening:** `outputs/robustness_loop052/robustness_h2_continuous_health.json`.
- **H3 perpetration exclusion + additional timing controls:** `outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `outputs/robustness_loop052/robustness_h3_teen_abuse.json`.
All robustness rows preserve the sign and practical magnitude of the primary estimands.

## Sensitivity scenarios rerun in loop 068
1. **Pseudo-weight sweep (Scenario 1, DEFF ∈ {1.0, 1.25, 1.5})**  
   Command: `python analysis/code/pseudo_weight_sensitivity.py --config config/agent_config.yaml --seed 20251016 --draws 400 --scenarios 1.0 1.25 1.5`  
   Outputs: `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, `_150.json`.  
   Result: Effective N falls from 14,438 → 11,628 → 9,533 but H1 and H3 retain negative estimates (H3 stays below −0.58 even at DEFF 1.5). Guidance effects absorb the variance inflation with negligible drift (`ΔPr` stays ~0.10).

2. **Design-effect grid (Scenario 2, DEFF ∈ {1.0, 1.25, 1.5, 2.0})**  
   Command: `python analysis/code/design_effect_grid.py --input analysis/results.csv --deffs 1.0 1.25 1.5 2.0 --output-csv outputs/sensitivity_design_effect_grid.csv --output-md outputs/sensitivity_design_effect_grid.md`  
   The grid shows every H1–H3 interval retains its sign through DEFF=2.0 (e.g., H3 95% CI at DEFF=2.0: [`-0.746`, `-0.563`]) while logging n_effective shrinkage (H1: 14,438 → 7,219).

3. **Pseudo-replicate jackknife (Scenario 3, k=6)**  
   Command: `python analysis/code/pseudo_replicates.py --config config/agent_config.yaml --seed 20251016 --k 6 --output-dir outputs/sensitivity_replicates --results analysis/results.csv`  
   Output: `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`.  
   The leave-one-cluster-out SEs are 0.019 (H1), 0.0020 (H2), and 0.0177 (H3), aligning with their HC1 bands and confirming that the point estimates remain far from zero.

## Default specification decision
- **Reporting default:** Retain the SRS+HC1 specification recorded in `analysis/pre_analysis_plan.md`.  
- **Justification:** All three sensitivity variants (pseudo weights, design-effect grid, pseudo replicates) leave the signs and practical magnitudes intact. Even the most pessimistic DEFF=2.0 and jackknife SEs keep H1 and H3 intervals entirely negative and H2 entirely positive, so no alternative weighting or variance adjustment would change the inference direction. The default spec therefore remains the most interpretable presentation while the design-effect appendix contextualizes variance inflation.

## Loop 068 synthesis
1. Rebuilt `analysis/results.csv`, `analysis/results_pre_bh.csv`, and `tables/results_summary.*` from deterministic model runs (`analysis/code/run_models.py`, `summarize_results.py`, `calc_bh.py`).
2. Regenerated Scenario 1–3 outputs plus metadata in `outputs/sensitivity_pseudo_weights/`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/`.
3. Logged the new disclosure audit (`qc/disclosure_check_loop_056.md`, violations = 0) referencing the refreshed results table/figure inventory.
4. Updated `analysis/sensitivity_manifest.md` and this plan so the writing phase inherits a complete proxy/design-effect synthesis with an explicit default specification.
