# Findings Summary — Loop 060
**Date:** 2025-11-09  
**Seed:** 20251016  

## Loop updates
- Rebuilt the PAP reporting chain (`analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now capture the loop-060 deterministic estimates and q-values that feed the manuscript tables.
- Executed the scenario suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` reserve the heavier-DEFF and jackknife uncertainty bounds around the SRS + HC1 baseline.
- Re-ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_060.md`, confirming `tables/results_summary.csv` and `figures/dag_design.png` still meet the n ≥ 10 guardrail (violations=0) before any release-ready artifacts are referenced.
- Logged the CrossRef fallback DOI `10.1080/19349637.2014.864543` for `[CLAIM:C3]` (lit/queries/loop_060/crossref_query_001.json) because the Semantic Scholar search returned 403; the evidence map and bibliographies now carry the peer-reviewed citation until the API key is restored.

## Next actions
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the sensitivity outputs, and `qc/disclosure_check_loop_060.md` into `papers/main/*`, `papers/main/imrad_outline.md`, and `reports/identification.md` so every `[CLAIM:<ID>]` cites deterministic artifacts (N11).
2. Keep recording the blocked Semantic Scholar queries and crossref fallbacks (lit/queries/loop_060/…) so `lit/evidence_map.csv`/`lit/bibliography.*` remain DOI-backed while the waiver request is outstanding (N8).
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and the decision log so the QC coverage reflects the latest confirmatory+sensitivity assets before the writing/review QC suite (N12).
