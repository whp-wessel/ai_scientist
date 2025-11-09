# Findings Summary — Loop 059
**Date:** 2025-11-09  
**Seed:** 20251016  

## Loop updates
- Rebuilt the PAP command chain (`analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now exist with the latest deterministic outputs that feed the manuscript tables and BH adjustment.
- Captured the cross-reflected small-cell audit via `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_059.md` (violations=0 for `tables/results_summary.csv` and `figures/dag_design.png`), keeping the n ≥ 10 rule in place before any public tables are released.
- Replayed the loop_059 Semantic Scholar attempt (403) and recorded the CrossRef fallback `10.1332/17579597y2024d000000035` for the adult self-rated health literature, archiving both `lit/queries/loop_059/query_001.json` and `lit/queries/loop_059/crossref_query_001.json` so the evidence map now carries a DOI-backed row for `[CLAIM:C2]`.
- Generated the full sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) so `outputs/sensitivity_*` document how heavier DEFFs and jackknife draws affect SEs while the SRS + HC1 baseline remains the default as documented in `analysis/sensitivity_plan.md`.

## Next actions
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the sensitivity outputs, `qc/disclosure_check_loop_059.md`, and the DOI-backed literature update into `papers/main/*`, `papers/main/imrad_outline.md`, and `reports/identification.md` (per N11) so every `[CLAIM:<ID>]` cites regenerable evidence.
2. Keep the Semantic Scholar outage/waiver log current (N8) while the key is repaired and continue adding DOI-backed sources whenever possible so the evidence map/bibliography stay in sync with the reviewer-mandated literature gate.
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and `analysis/decision_log.csv` to reflect the confirmed estimates, sensitivity doses, and disclosure audit before transitioning toward the writing/review QC suite (per N12).
