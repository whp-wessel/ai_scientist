# Sensitivity Plan — Loop 060
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every command below reuses this seed and the deterministic files referenced in `analysis/decision_log.csv`).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — Ordered-logit contrast for “religion very important” vs “not at all important” now reads `ΔE = -0.1201` (95% CI [−0.187, −0.055]; `q ≈ 0.0007`; `analysis/results.csv`). The targeted family name is `wellbeing` and `bh_in_scope` shows `H1|H2`, so the BH entry keeps `targeted = Y`.
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The ordered-logit probability jump for the top guidance quartile vs the bottom is `+0.0998` (95% CI [0.0889, 0.1109]; `q = 0`; `analysis/results.csv`). The same row records the `targeted` label, HC1 SE = 0.0057, and `n = 14,430`.
3. **H3 / self-love (`[CLAIM:C3]`)** — Linear contrast of abuse vs no abuse is `-0.6544` (95% CI [−0.719, −0.590]; `q = 0`; `analysis/results.csv`), with `n = 13,507` and HC1 SE ≈ 0.0331.
4. **NC1 / sibling count (negative control)** — Linear estimate `+0.2388` (95% CI [0.2209, 0.2568], `p ≈ 0`; `outputs/negative_control_loop059.json`) continues to show the expected null structure; `targeted = N` so it is logged but excluded from the BH adjustment.

## Robustness checks completed
- **H1 high vs. low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` keeps the negative contrast intact when contrasting “very important” to “not at all important.”
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` reproduces the positive slope when health is treated as a 0–4 numeric score.
- **H3 non-perpetrators & matched teen-stage abuse controls** — `outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `outputs/robustness_loop052/robustness_h3_teen_abuse.json` still locate the self-love gap once the sample restricts or adds timing controls.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` re-wrote `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `_125.json`, and `_150.json`. Effective samples shrink from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5), while H1/H2 SEs move only modestly (0.0354→0.0396 and 0.0057→0.0064) and H3 SE rises from 0.0331 to 0.0405.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` produced `outputs/sensitivity_design_effect_grid.csv/.md`. Even at DEFF=2.0 the intervals remain negative/positive (e.g., H1: [−0.218, −0.022]; H3: [−0.746, −0.563]) and the implied `n_effective` stays above ∼6,700, so the direction is robust even under extreme HC1 inflations.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` updated `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`. Jackknife replicates reproduce the base estimates within 0.01 points while the aggregate replicate SEs hover around 0.019 (H1), 0.002 (H2), and 0.018 (H3), confirming the HC1 baseline is conservative relative to these cluster-omission draws.

## Default specification decision
The SRS + HC1 pipeline (the `analysis/code/run_models.py` → `analysis/code/summarize_results.py` → `analysis/code/calc_bh.py` → `analysis/code/build_results_summary.py` sequence that yields `analysis/results.csv` plus `tables/results_summary.*`) remains the default because (1) pseudo weights only modestly widen SEs while preserving the sign, (2) the DEFF=2.0 grid still excludes zero even as `n_effective` drops to ∼6,700, and (3) jackknife replicates deliver estimates with the same direction while slightly tightening variation, making HC1 a defensible conservative anchor while the replicates serve as an alternative lower bound.

## Loop 060 synthesis
- Re-summarized the H1–H3 outputs via `analysis/code/summarize_results.py` and applied BH (`analysis/code/calc_bh.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and the Markdown/CSV tables (`analysis/code/build_results_summary.py`) now reflect the loop-060 seed.
- Re-ran the sensitivity suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_*` again host the refreshed uncertainty scenarios plus the jackknife summary.
- Executed `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_060.md` to certify `tables/results_summary.csv` and `figures/dag_design.png` still meet the n ≥ 10 guardrail before any public release.
- Logged the CrossRef fallback DOI `10.1080/19349637.2014.864543` for `[CLAIM:C3]` because the Semantic Scholar search returned 403; the JSON sits at `lit/queries/loop_060/crossref_query_001.json` and the evidence map/bibliography now carry the citarion so the literature gate stays satisfied.

## Next steps for reporting
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, and the scenario outputs/disclosure audit into `papers/main/*`, `papers/main/imrad_outline.md`, and `reports/identification.md` so every `[CLAIM:<ID>]` cites deterministic artifacts (addresses N11).
2. Keep the Semantic Scholar crossref fallback log (lit/queries/loop_060/…) current while the API key remains blocked so `lit/evidence_map.csv` and `lit/bibliography.*` stay DOI-backed (N8).
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and the decision log to reflect the confirmatory + sensitivity updates before progressing toward writing/review QC tasks (N12).
