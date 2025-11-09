# Findings Summary — Loop 063
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Re-aggregated the H1–H3 JSON outputs (`outputs/run_models_loop059_H1.json`–`H3.json`) via `analysis/code/summarize_results.py`, reapplied BH (`analysis/code/calc_bh.py`), and rebuilt `tables/results_summary.csv/.md` (`analysis/code/build_results_summary.py`) so `analysis/results.csv`, `artifacts/bh_summary.json`, and the public table now mirror the deterministic seed and q-values.
- Re-ran the sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now host the refreshed uncertainty bounds that document the SRS + HC1 safety net.
- Ran `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_063.md` and compiled `papers/main/manuscript.tex` with `tectonic --keep-logs`, capturing the new `papers/main/manuscript.pdf` plus logs while `papers/main/build_log.txt` now records `LaTeX build: PASS` despite overfull-box warnings.
- Issued the loop-063 Semantic Scholar search (`lit/queries/loop_063/query_001.json`), captured the CrossRef fallback (`lit/queries/loop_063/crossref_query_001.json`, DOI `10.1080/19349637.2014.864543`), and refreshed `lit/evidence_map.csv`, `lit/bibliography.bib`, and `lit/bibliography.json` so at least one DOI-backed row covers [CLAIM:C1] while the API remains 403.
- Updated `reports/findings_v1.1.md` and `notebooks/research_notebook.md` with this loop’s synthesis plus the writing-phase QC progress so the recorded narrative keeps pace with the deterministic commands.

## Next actions
1. Begin the writing-phase QC pass: confirm `papers/main/manuscript.tex` aligns with the Markdown twin, rerun `qc/strobe_sampl_checklist.md` if needed, and lock the next `reports/findings_v1.2.md` entry before entering review once STROBE/SAMPL + DAG/identification tasks are satisfied.
2. Continue logging blocked Semantic Scholar queries plus CrossRef fallbacks (lit/queries/loop_0XX/) so every `[CLAIM:<ID>]` stays DOI-backed; record each query in `analysis/decision_log.csv` and the evidence map until the S2 key or waiver is restored.
3. Maintain the notebook/report ledger (notebook, reports/findings_*.md, analysis/decision_log.csv) so reviewers can trace the deterministic path before advancing past the sensitivity phase.
