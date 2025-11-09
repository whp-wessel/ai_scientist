# Findings Log — Version 1.1
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Confirmatory H1–H3 models now live in `analysis/results.csv` (with BH-adjusted q-values) and the publication-ready `tables/results_summary.csv/.md`; the deterministic pipeline anchors every estimate and `bh_in_scope` metadata entry for reproducibility.
- Sensitivity artifacts (`analysis/sensitivity_manifest.md` plus `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) document pseudo-weight, design-effect, and replicate experiments that bound how design complexity could widen the HC1 CIs, reinforcing the descriptive stance captured in `analysis/sensitivity_plan.md`.
- The measurement dossier (`qc/measures_validity.md`, `artifacts/measurement_validity_loop061.json`) and disclosure scan (`qc/disclosure_check_loop_061.md`) confirm that the PAP outcomes/predictors have valid codings and that every table/figure (e.g., `tables/results_summary.*`, `figures/dag_design.png`) stays above $n \geq 10$.
- All DAM (manuscript, outline, identification, QC, notebook, reports) artifacts now cite the rerun results and sensitivity outputs, and the DOI-backed literature log remains current via `lit/queries/loop_061/` and the evidence map/bibliographies.

## Next steps
1. Begin the writing-phase QC pass: update `papers/main/build_log.txt` with a deterministic `latexmk -pdf` run (expect `LaTeX build: PASS`), confirm the updated LaTeX version matches the Markdown twin, and consider exporting the compiled PDF once STROBE/SAMPL items are verified.
2. Keep logging blocked Semantic Scholar queries plus CrossRef fallbacks (N8) so every `[CLAIM:<ID>]` continues to point to a DOI-backed source until the S2 key or waiver clears.
3. Maintain the loop-level ledger in `reports/findings_summary.md`, `reports/findings_v*.md`, `notebooks/research_notebook.md`, and `analysis/decision_log.csv` so reviewers can trace each iteration before advancing to the review phase.
