# Findings Summary — Loop 062
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Rebuilt the PAP reporting chain (`analysis/code/summarize_results.py`, `analysis/code/calc_bh.py`, `analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and `tables/results_summary.csv/.md` now capture loop-062 deterministic estimates and q-values that feed the manuscript tables.
- Re-ran the sensitivity suite (pseudo weights, the DEFF grid, and pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty corridors seeded at 20251016.
- Ran `analysis/code/measure_validity_checks.py --output-json artifacts/measurement_validity_loop061.json` so `qc/measures_validity.md` plus the JSON dossier reflect the latest reliability/DIF diagnostics for every PAP outcome/predictor.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_061.md`, confirming `tables/results_summary.csv` and `figures/dag_design.png` still meet the n ≥ 10 threshold before release-ready artifacts reference them (violations=0).
- Integrated the rerun confirmatory/sensitivity outputs into `papers/main/manuscript.*`, `papers/main/imrad_outline.md`, `reports/identification.md`, `qc/strobe_sampl_checklist.md`, and `reports/findings_v1.1.md`, and kept the DOI-backed literature log current via `lit/queries/loop_061/`.
- Issued the loop-061 Semantic Scholar query (`lit/queries/loop_061/query_001.json`, still HTTP 403) and logged the CrossRef fallback (`lit/queries/loop_061/crossref_query_001.json`, DOI `10.23880/mhrij-16000182`) so `[CLAIM:C1]` retains DOI-backed coverage while the Semantic Scholar key remains blocked; the new evidence propagates through `lit/evidence_map.csv` and `lit/bibliography.*`.

## Next actions
1. With N11/N12 complete, shift focus to writing-phase QC: refresh the STROBE/SAMPL checklist for any new tables/figures, run the deterministic LaTeX build (`latexmk -pdf papers/main/manuscript.tex`), log a `LaTeX build: PASS` entry in `papers/main/build_log.txt`, and re-run disclosure checks for any new publishable assets.
2. Continue logging blocked Semantic Scholar queries plus CrossRef fallbacks (N8) so `lit/evidence_map.csv` and `lit/bibliography.*` remain DOI-backed until the S2 key or waiver clears.
3. Keep documenting loop-level deltas in `reports/findings_summary.md`, `reports/findings_v*.md`, and `notebooks/research_notebook.md` so the manuscript team can trace every change before the writing phase advances.
