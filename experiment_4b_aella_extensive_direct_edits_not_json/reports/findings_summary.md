# Findings Summary — Loop 065
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Re-ran the full sensitivity suite so `outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, and `outputs/sensitivity_replicates/sensitivity_replicates_summary.json` now reflect the seeded pseudo-weight (DEFF=1.0, 1.25, 1.5), design-effect grid (up to DEFF=2.0), and pseudo-replicate (k=6 jackknife) scenarios described in `analysis/sensitivity_plan.md` and recorded in `analysis/sensitivity_manifest.md`.
- The pseudo-weight draws show the effective n shrinking from ~14,443 (DEFF=1.0) to ~9,533 (DEFF=1.5) while H1/H2 stay at −0.1201/+0.0998 and H3’s SE expands from 0.0331 to about 0.0405, so the CI stays below zero even with appreciable inflation.
- The design-effect grid plot/table documents how the targeted family’s n_effective dwindles to ~6,754 at DEFF=2.0 without flipping the sign of the BH-adjusted estimates, and the pseudo-replicate JSON now reports jackknife SEs of roughly 0.019 (H1), 0.002 (H2), and 0.0177 (H3) that align with the HC1 band.
- No new public tables or figures were released, so disclosure control remains with the prior audit; the loop refreshed the sensitivity narrative so the writing-phase QC tasks (manuscript parity, outline, DAG, checklist, LaTeX build) can be tackled next.

## Next actions
1. Execute the writing-phase QC pass: align `papers/main/manuscript.tex` with the Markdown twin, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, verify `reports/identification.md` against `figures/dag_design.png`, rerun the LaTeX build per `papers/main/build_log.txt`, and capture the resulting reflection in `reports/findings_v1.4.md` once the checklist/DAG remain stable.
2. Keep documenting every Semantic Scholar attempt (with the CrossRef fallback if the API still 403s) so each `[CLAIM:<ID>]` stays DOI-backed; log the commands/responses in `analysis/decision_log.csv`, `lit/queries/loop_0XX/`, and `lit/evidence_map.csv` until the key is restored.
3. Maintain the narrative ledger (notebooks + reports + decision log) so reviewers can follow the deterministic path through writing-phase QC and into the pending review-phase gate.
