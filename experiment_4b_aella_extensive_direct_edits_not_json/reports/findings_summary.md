# Findings Summary — Loop 066
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Re-ran the full sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) with the same seeded commands as recorded in `analysis/sensitivity_manifest.md`; loop-specific outputs now live under `outputs/sensitivity_pseudo_weights_loop066/`, `outputs/sensitivity_design_effect_grid_loop066.*`, and `outputs/sensitivity_replicates_loop066/sensitivity_replicates_summary.json`, so each uncertainty artifact is distinct for loop 066.
- The pseudo-weight scenarios show the effective sample shrinking from 14,443 (DEFF=1.0, CV=0.000) to 11,628.5 (DEFF=1.25, CV≈0.492) to 9,533.2 (DEFF=1.5, CV≈0.718) while H1/H2 remain near −0.1201/+0.0998 (SE=0.0354) and H3’s SE widens from 0.0331 to 0.0405 without flipping the negative estimate.
- The design-effect grid CSV/MD (`outputs/sensitivity_design_effect_grid_loop066.csv`/`.md`) logs that the targeted family’s n_effective falls toward ~11,550 (DEFF=1.25), ~9,625 (DEFF=1.5), ~7,219 (DEFF=2.0) and only ~6,754 for H3 while each 95% CI stays on the same side of zero and the BH q-values remain tied to the original family.
- The pseudo-replicate jackknife summary (`outputs/sensitivity_replicates_loop066/sensitivity_replicates_summary.json`) reports jackknife SEs of ≈0.0190 (H1), 0.0020 (H2), and 0.0177 (H3), matching the HC1 uncertainty band documented in `analysis/results.csv`.
- No new public tables or figures were released this loop, so `qc/disclosure_check_loop_064.md` (violations: 0) remains the latest audit; the sensitivity suite preparation now clears the path for the writing-phase QC milestone (N14).

## Next actions
1. Execute the writing-phase QC pass: sync `papers/main/manuscript.tex` with the Markdown twin, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, verify `reports/identification.md` against `figures/dag_design.png`, rerun the LaTeX build (and append `papers/main/build_log.txt`), and capture the outcome in the next findings log entry.
2. Keep issuing Semantic Scholar queries (with CrossRef fallbacks while the API still fails) so each `[CLAIM:<ID>]` stays DOI-backed; log every response in `analysis/decision_log.csv`, `lit/queries/loop_<idx>/`, and `lit/evidence_map.csv` before advancing phases.
3. Maintain the research narrative (notebooks, decision log, reports) so reviewers can trace loop-by-loop reproducible steps as we head toward the pending review gate.
