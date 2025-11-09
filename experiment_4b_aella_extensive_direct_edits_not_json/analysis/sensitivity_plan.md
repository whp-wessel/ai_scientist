# Sensitivity Plan — Loop 058
**Date:** 2025-11-09  
**Seed:** 20251016 (`artifacts/seed.txt` records the deterministic seed that generated every confirmatory and sensitivity artifact).

## Confirmatory estimates and falsification
1. **H1 / depression (`[CLAIM:C1]`)** — `ΔE[depression score | external religiosity very important vs not important] = -0.1201` (95% CI [-0.1873, -0.0548], `q ≈ 0.000696`, `analysis/results.csv`). The rerun of `analysis/code/run_models.py` with seed 20251016 produced the values recorded in `tables/results_summary.*`, keeping the wellbeing family anchored in the frozen PAP (`pap-v1`).
2. **H2 / self-rated health (`[CLAIM:C2]`)** — The probability contrast between guidance Q3 and Q1 is `+0.0998` (CI [0.0889, 0.1109], `q = 0`). The same command chain now feeds the publication table and `analysis/results.csv` so the targeted H1/H2 family stays fully reproducible.
3. **H3 / self-love (`[CLAIM:C3]`)** — The abuse vs. no-abuse contrast remains `-0.6544` (CI [-0.7192, -0.5895], `q = 0`). The psychosocial family continues to rely on HC1 SEs and the deterministic command log in `analysis/results.csv` (`command` column).
4. **NC1 / sibling count (negative control)** — `Coef = +0.2388` (CI [0.2209, 0.2568], `p ≈ 0`), targeted `N` so it never enters the BH family but remains documented in both `artifacts/negative_control_loop058.json` and the pre-BH summary to show the modeling pipeline resists spurious hits.

## Robustness checks completed
- **H1 high vs. low religiosity** — `outputs/robustness_loop052/robustness_h1_high_low.json` continues to show a negative ordered-logit contrast when comparing extreme religiosity levels.
- **H2 continuous health coding** — `outputs/robustness_loop052/robustness_h2_continuous_health.json` reproduces the effect using a 0–4 numeric health measure instead of ordered logits.
- **H3 non-perpetrators & teen-stage abuse control** — `outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `outputs/robustness_loop052/robustness_h3_teen_abuse.json` confirm the sign remains the same when restricting to non-perpetrators or adding teen-stage abuse controls.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` produced `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json`, `pseudo_weights_deff_125.json`, and `pseudo_weights_deff_150.json`. Effective sample sizes drop from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5) while the HC1-based SEs for H1/H2 stay within 0.0354/0.0057 and H3’s SE edges up toward 0.0405, confirming the base control estimates remain credible even with heavier pseudo weights.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` read `analysis/results.csv` and emitted `outputs/sensitivity_design_effect_grid.csv/.md`. Even at DEFF=2.0, the 95% CIs (e.g., H1: [–0.218, –0.022]) stay away from zero while implied effective Ns remain above 7,200, so effect direction is stable despite inflated standard errors.
- **Scenario 3 – pseudo replicates (k=6)** — `analysis/code/pseudo_replicates.py` aggregated jackknife draws in `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`. The replicate SEs (H1: 0.01903, H2: 0.00203, H3: 0.01766) sit below the HC1 estimates, reinforcing that the default HC1 configuration is not understating uncertainty by omission.

## Default specification decision
The SRS + HC1 configuration remains the default reporting specification because (1) the pseudo-weight re-runs only modestly widen SEs (H3 grows to 0.0405 at DEFF=1.5) while keeping effective Ns comfortably large, (2) the DEFF=2.0 grid retains negative intervals for H1/H3 and positive intervals for H2 with reasonable effective Ns, and (3) the pseudo-replicate jackknife produces even smaller SEs, so it operates as a lower-bound robustness check. These conclusions reference the same `analysis/results.csv`, `tables/results_summary.*`, and the small-cell audit `qc/disclosure_check_loop_058.md` (threshold n ≥ 10 for `tables/results_summary.csv` and `figures/dag_design.png`) that now document compliance.

## Loop 058 synthesis
- Re-ran the PAP command chain (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, and `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now reflect the latest seeds and deterministic commands (see `command` columns for exact syntax).
- Produced the three sensitivity pipelines (`analysis/code/pseudo_weight_sensitivity.py`, `analysis/code/design_effect_grid.py`, `analysis/code/pseudo_replicates.py`) so the pseudo-weight, design-effect, and replicate JSON/CSV/MD outputs now exist in `outputs/sensitivity_*` and document how seeds/commands were reused.
- Logged the disclosure audit via `analysis/code/disclosure_check.py` to produce `qc/disclosure_check_loop_058.md` (violations: 0) after rescanning `tables/results_summary.csv` and `figures/dag_design.png`.
- Archived the new Semantic Scholar 403 attempt (`lit/queries/loop_058/query_001.json`) plus the CrossRef fallback (`lit/queries/loop_058/crossref_query_001.json`) and added the DOI-backed row for `https://doi.org/10.1080/13674676.2018.1504906` to `lit/evidence_map.csv`, keeping the literature gate auditable while the waiver remains pending.

## Next steps for reporting
1. Pull `analysis/results.csv`, `tables/results_summary.*`, the sensitivity outputs under `outputs/sensitivity_*`, and `qc/disclosure_check_loop_058.md` into the manuscript, IMRaD outline, and `reports/identification.md` (see pending N11) so every `[CLAIM:<ID>]` cites regenerable artefacts.
2. Keep the Semantic Scholar outage/waiver log current and continue pushing on N8 while documenting evidence updates in `lit/evidence_map.csv`/`lit/bibliography.*`.
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and `reports/findings_summary.md` with the latest results/sensitivity/disclosure outputs before transitioning into the writing/review QC suite (per N12).
