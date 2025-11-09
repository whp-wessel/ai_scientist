# Sensitivity Plan — Loop 061
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every command below reuses this seed so the rerun remains deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — Ordered-logit contrast for “religion very important” vs “not at all important” remains `ΔE = -0.1201` (95% CI [−0.189, −0.051]; `q ≈ 0.0007`; `analysis/results.csv`). The `wellbeing` family still records `bh_in_scope = H1|H2` and `targeted = Y`, ensuring the BH adjustment keeps this row in scope.
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The guided health contrast stays positive (`+0.0998`, 95% CI [0.088, 0.111], `q = 0`); `analysis/results.csv` now shows the fully re-run estimate with HC1 SE = 0.0057 and total `n = 14,430`.
3. **H3 / self-love (`[CLAIM:C3]`)** — The abuse vs. none gap is `-0.6544` (95% CI [−0.719, −0.590]; `q = 0`), with HC1 SE = 0.0331 and `n = 13,507` recorded in `analysis/results.csv`.
4. **NC1 / sibling count (negative control)** — Linear null check (`outputs/negative_control_loop059.json`) still yields `+0.2388` (95% CI [0.2209, 0.2568]; `p ≈ 0`); `targeted = N` so the BH step excludes it while keeping a record for diagnostics.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) preserves the negative contrast when contrasting “very important” with “not at all important.”
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) keeps the positive slope when self-rated health is treated as a 0–4 numeric outcome.
- **H3 non-perpetrators & matched teen-stage abuse controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `outputs/robustness_loop052/robustness_h3_teen_abuse.json`) sustain the self-love gap once the sample restricts to non-perpetrators or adds timing controls.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` rewrote `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json`. Effective samples drift from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5), while H1/H2 SEs stay at 0.0354 and 0.0057 and H3’s SE climbs only to 0.0405, keeping the direction intact.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` generated `outputs/sensitivity_design_effect_grid.csv/.md`. Even at the extreme DEFF=2.0 the 95% CIs remain negative for H1 ([-0.218, -0.022]) and H3 ([-0.746, -0.563]), while the implied effective sample shrinks to ∼7,200 for H1/H2 and ∼6,750 for H3, so the association signs stay stable across this uncertainty grid.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` wrote `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`. Jackknife replicates reproduce the base estimates within 0.01 and deliver replicate SEs of ~0.019 (H1), 0.002 (H2), and 0.0177 (H3), confirming that the HC1 baseline is conservative compared to replicate-based variance.

## Default specification decision
The SRS + HC1 sequence (run_models → summarize_results → calc_bh → build_results_summary) remains the default because pseudo weights only modestly inflate uncertainty, even DEFF=2.0 still excludes zero while the estimated `n_effective` stays above ∼6,700, and the pseudo-replicates deliver slightly tighter SEs that reinforce the same direction of effects. The replicate outputs serve as a robustness anchor when we describe uncertainty in reporting, but the HC1 estimates are the conservative baseline for tables and manuscripts.

## Loop 061 synthesis
- Re-aggregated the H1–H3 JSON outputs via `analysis/code/summarize_results.py` and applied BH with `analysis/code/calc_bh.py` so `analysis/results.csv`, `artifacts/bh_summary.json`, and the Markdown/CSV tables (`analysis/code/build_results_summary.py`) now reflect the loop-061 deterministic estimates and q-values.
- Executed the full sensitivity suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty bounds around the SRS + HC1 baseline.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_061.md` to confirm `tables/results_summary.csv` and `figures/dag_design.png` remain above the n ≥ 10 disclosure threshold before any release-ready artifact references them (violations=0).
- Issued the loop-mandated Semantic Scholar query (`lit/queries/loop_061/query_001.json`) which still returned HTTP 403, then logged the CrossRef fallback (`lit/queries/loop_061/crossref_query_001.json`) for DOI `10.23880/mhrij-16000182` so `[CLAIM:C1]` keeps a DOI-backed citation while the Semantic Scholar key remains blocked; the new evidence is now in `lit/evidence_map.csv` and `lit/bibliography.*`.

## Next steps for reporting
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the scenario outputs, and `qc/disclosure_check_loop_061.md` into `papers/main/*`, `papers/main/imrad_outline.md`, and `reports/identification.md` so every `[CLAIM:<ID>]` cites the deterministic artifacts (N11).
2. Continue recording the blocked Semantic Scholar queries and CrossRef fallbacks (e.g., `lit/queries/loop_061/…`) so `lit/evidence_map.csv` and `lit/bibliography.*` stay DOI-backed until the waiver/request resolves (N8).
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and the decision log so the QC coverage matches the updated confirmatory+sensitivity assets before moving into the writing/review QC suite (N12).
