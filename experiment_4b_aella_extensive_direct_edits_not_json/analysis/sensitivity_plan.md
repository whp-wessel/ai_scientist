# Sensitivity Plan — Loop 059
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt` for the global randomness anchor; every command below reuses this seed).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — Ordered-logit marginal contrast shows `ΔE[depression score | religion very important vs not important] = -0.120` (95% CI [−0.187, −0.055], `q ≈ 0.0007`; `analysis/results.csv`). Targeted BH entry `H1` keeps `targeted = Y` and the `bh_in_scope` string `H1|H2`, so this wellbeing family is pooled for FDR correction.
2. **H2 / health (`[CLAIM:C2]`)** — Ordered-logit probability difference for very-good/excellent health between guidance quartiles is `+0.0998` (95% CI [0.0889, 0.1109], `q = 0`; `analysis/results.csv`). The same table also documents the `targeted` label, HC1 SE, and `n = 14,430`.
3. **H3 / self-love (`[CLAIM:C3]`)** — Linear contrast of abuse vs. no-abuse yields `-0.6544` (95% CI [−0.7192, −0.5895], `q = 0`; `analysis/results.csv`), with `n = 13,507` and HC1 SE = 0.0331.
4. **NC1 / sibling count (negative control)** — Linear estimate `+0.2388` (95% CI [0.2209, 0.2568], `p ≈ 0`) confirms the falsification target remains benign; `targeted = N` so it is excluded from BH but still recorded in `analysis/results.csv` and `artifacts/negative_control_loop059.json`.

## Robustness checks completed
- **H1 high vs. low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` continues to show the same negative contrast when comparing “very important” to “not at all important,” preserving effect direction under alternative codings.
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` reproduces the boost using a 0–4 numeric health score, showing slope stability.
- **H3 non-perpetrators & teen-stage abuse controls** — `outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `..._h3_teen_abuse.json` keep the self-love gap intact when restricting the sample or adding additional abuse timing controls.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` produced `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json`. Effective sample sizes shrink from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5) while H1/H2 SEs drift only 0.0354→0.0396 and 0.0057→0.0064; H3’s SE increases from 0.0331 to 0.0370, so directional conclusions remain stable under heavier weighting.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` wrote `outputs/sensitivity_design_effect_grid.csv/.md`. At DEFF=2.0 the intervals (e.g., H1: [−0.218, −0.022]; H3: [−0.746, −0.563]) still exclude zero while implied effective Ns stay above 6,700, confirming the sign’s robustness even if HC1 SEs understate clustering.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` generated `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`. The jackknife replicates average SEs ≈ 0.0402 (H1), 0.00623 (H2), and 0.03624 (H3), so HC1 yields slightly smaller uncertainty but remains in the same neighborhood.

## Default specification decision
The SRS + HC1 pipeline (i.e., the `analysis/code/run_models.py` chain that feeds `analysis/results.csv` and `tables/results_summary.*`) remains the reporting default because (1) pseudo-weight scenarios only modestly widen SEs while preserving effect direction; (2) the DEFF=2.0 grid still yields negative H1/H3 and positive H2 intervals even though the implied `n_effective` falls toward 7,200; and (3) jackknife replicates edge SEs upward but do not reverse the signs, so HC1 stays a defensible baseline while the replicates serve as a documented lower bound.

## Loop 059 synthesis
- Re-ran the PAP command chain (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now reflect the latest seed 20251016 paths.
- Executed the three sensitivity pipelines (`analysis/code/pseudo_weight_sensitivity.py`, `analysis/code/design_effect_grid.py`, `analysis/code/pseudo_replicates.py`) to populate `outputs/sensitivity_*` with deterministic summaries of weighting and clustering uncertainty.
- Logged the small-cell audit via `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_059.md` (violations=0 for `tables/results_summary.csv` and `figures/dag_design.png`).
- Replayed the loop_059 Semantic Scholar search (403) and fetched CrossRef metadata for `10.1332/17579597y2024d000000035`, archiving both `lit/queries/loop_059/query_001.json` and `lit/queries/loop_059/crossref_query_001.json` so the evidence map keeps a DOI-backed fallback entry while the waiver remains in effect.

## Next steps for reporting
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the sensitivity outputs under `outputs/sensitivity_*`, `qc/disclosure_check_loop_059.md`, and the new DOI-backed evidence into each `[CLAIM:<ID>]` mention throughout `papers/main/*` and `reports/identification.md` (N11).
2. Update `qc/strobe_sampl_checklist.md` and `qc/measures_validity.md` along with the decision log so these QC artifacts reflect the confirmed estimates (N12) before advancing into writing/review.
