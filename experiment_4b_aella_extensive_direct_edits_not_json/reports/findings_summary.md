# Findings Summary — Loop 061
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Rebuilt the PAP reporting chain (`analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now capture the loop-061 deterministic estimates and q-values that feed the manuscript tables.
- Executed the sensitivity suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty corridors around the SRS + HC1 baseline.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_061.md`, confirming `tables/results_summary.csv` and `figures/dag_design.png` still meet the n ≥ 10 threshold before release-ready artifacts reference them (violations=0).
- Issued the loop-061 Semantic Scholar query (`lit/queries/loop_061/query_001.json`) which still returned HTTP 403 and logged the CrossRef fallback (`lit/queries/loop_061/crossref_query_001.json`) for DOI `10.23880/mhrij-16000182`, so `[CLAIM:C1]` retains DOI-backed coverage while the Semantic Scholar key remains blocked; the new evidence propagates through `lit/evidence_map.csv` and `lit/bibliography.*`.

## Next actions
1. Integrate `analysis/results.csv`, `tables/results_summary.*`, the sensitivity outputs, and `qc/disclosure_check_loop_061.md` into `papers/main/*`, `papers/main/imrad_outline.md`, and `reports/identification.md` so each `[CLAIM:<ID>]` cites deterministic artifacts (N11).
2. Continue capturing the blocked Semantic Scholar queries plus CrossRef fallbacks (e.g., `lit/queries/loop_061/…`) so `lit/evidence_map.csv` and `lit/bibliography.*` remain DOI-backed until the waiver resolves (N8).
3. Refresh `qc/strobe_sampl_checklist.md`, `qc/measures_validity.md`, and the decision log so the QC records match the confirmatory+sensitivity rerun before advancing to the writing/review QC suite (N12).
