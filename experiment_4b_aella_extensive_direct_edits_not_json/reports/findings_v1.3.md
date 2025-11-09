# Findings Log — Version 1.3
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Reconstructed the full sensitivity suite so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now trace the seeded pseudo-weight (DEFF=1.0/1.25/1.5), design-effect (up to DEFF=2.0), and jackknife (k=6) scenarios described in `analysis/sensitivity_plan.md`, documenting the effective n shrinkage and the persistence of the negative H3 gap even as SEs inflate.
- The pseudo-weight draws evidence shows H1/H2 retaining −0.1201/+0.0998 while H3’s SE rises from 0.0331 to ~0.0405 and the effective n falls to ~9,533 at DEFF=1.5; the design-effect grid keeps the CI on the same side up to ~6,754 effective observations (DEFF=2.0), and the jackknife replicates report SEs of ~0.019/0.002/0.0177 for H1/H2/H3, respectively, confirming the seeded HC1 reporting envelope.
- No confirmatory tables/figures were released, so the previous disclosure audit remains sufficient; the narrative now notes that the scenario suite is stable ahead of the writing-phase QC pass, which will re-sync the manuscript/outline/checklist/build logs before review.

## Next steps
1. Execute the writing-phase QC pass: ensure `papers/main/manuscript.tex` and the Markdown twin stay in lockstep, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, re-validate `reports/identification.md` against `figures/dag_design.png`, rebuild the LaTeX manuscript per `papers/main/build_log.txt`, and capture the outcome in the next findings log entry (v1.4) once the outline/checklist/build all show PASS.
2. Continue logging Semantic Scholar queries (plus CrossRef fallbacks while the API remains blocked) so every `[CLAIM:<ID>]` stays DOI-backed, and mirror the results in `analysis/decision_log.csv`, `lit/evidence_map.csv`, and the query archives before advancing phases.
3. Keep the narrative ledger (notebooks, decision log, reports) synchronized so future reviewer entries can trace the deterministic loop-by-loop progress as we transition into the review-phase gate.
