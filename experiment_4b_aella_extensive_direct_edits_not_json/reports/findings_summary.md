# Findings Summary — Loop 064
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Re-ran the full sensitivity suite (pseudo weights, the design-effect grid, and jackknife pseudo replicates) with seed 20251016 so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` archive the refreshed uncertainty bounds while `analysis/sensitivity_manifest.md` lists the deterministic commands.
- Verified the n ≥ 10 disclosure guardrail by rerunning `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_064.md`, guaranteeing every referenced table/figure still meets the suppression threshold before writing-phase references.
- Issued the loop-064 Semantic Scholar query (403) and captured the CrossRef fallback (DOI 10.1080/19349637.2014.864543) so [CLAIM:C1] remains DOI-backed; the new evidence-map row ties the fallback to `lit/queries/loop_064/crossref_query_001.json` while the lineage is recorded in `analysis/decision_log.csv`.
- Documented the loop-064 synthesis in `analysis/sensitivity_plan.md`, created `reports/findings_v1.2.md`, and appended the narrative to `notebooks/research_notebook.md` so the ledger mirrors the deterministic commands prior to the writing-phase QC pass.

## Next actions
1. Kick off the writing-phase QC pass: align `papers/main/manuscript.tex` with the Markdown twin, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, ensure `reports/identification.md` still matches the DAG, rerun the LaTeX build with logs, and collect new `reports/findings_v1.3.md` material.
2. Continue logging every Semantic Scholar attempt plus CrossRef fallback (lit/queries/loop_0XX/) so each `[CLAIM:<ID>]` stays DOI-backed until the S2 key returns; record these steps in `analysis/decision_log.csv` and `lit/evidence_map.csv`.
3. Keep the notebook/report ledger (notebook, reports/findings_*.md, decision log) updated so the reviewer can trace the deterministic path before review-phase checks begin.
