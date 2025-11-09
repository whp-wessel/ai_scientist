# Findings Summary — Loop 067
**Date:** 2025-11-09  
**Seed:** 20251016

## Loop updates
- Reran the full sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) with loop-specific outputs; the commands are catalogued in `analysis/sensitivity_manifest.md` while the artifacts live under `outputs/sensitivity_pseudo_weights_loop067/`, `outputs/sensitivity_design_effect_grid_loop067.*`, and `outputs/sensitivity_replicates_loop067/sensitivity_replicates_summary.json`, offering a deterministic uncertainty envelope for this loop.
- The pseudo-weight scenarios show the effective sample shrinking from 14,443 (DEFF=1.0, CV=0.000) to 11,628.5 (DEFF=1.25, CV≈0.492) to 9,533.2 (DEFF=1.5, CV≈0.718) while H1/H2 stay near −0.1201/+0.0998 (SE=0.0354/0.0057) and H3’s estimate deepens to −0.6339 (SE=0.0370, 95% CI [−0.707, −0.561]) at DEFF=1.25 and −0.667 (SE=0.0405, 95% CI [−0.747, −0.588]) at DEFF=1.5, so the negative gap never approaches zero even as the pseudo-weight variance swells.
- The design-effect grid CSV/MD (`outputs/sensitivity_design_effect_grid_loop067.csv`/`.md`) documents the targeted family’s n_effective falling toward ~11,550 (DEFF=1.25), ~9,625 (DEFF=1.5), ~7,219 (DEFF=2.0 for H1) and ~6,754 for H3 while each CI keeps its sign and the BH q-values stay tied to the original family because the base estimates did not change.
- The pseudo-replicate jackknife summary (`outputs/sensitivity_replicates_loop067/sensitivity_replicates_summary.json`) reports replicate SEs of ≈0.01903 (H1), 0.00203 (H2), and 0.01766 (H3), mirroring the HC1 uncertainty band documented in `analysis/results.csv`.
- No new public tables or figures were released this loop, so `qc/disclosure_check_loop_064.md` (violations: 0) still covers the public artifacts while the sensitivity suite leaves the writing-phase QC milestone (N14) as the next gate.

## Next actions
1. Execute the writing-phase QC pass: synchronize `papers/main/manuscript.tex` with the Markdown twin, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, revisit `reports/identification.md` with the DAG, rebuild the manuscript (record outcome in `papers/main/build_log.txt`), and capture the results in the next findings log entry.
2. Continue logging Semantic Scholar (or CrossRef fallback) queries so each `[CLAIM:<ID>]` keeps a DOI-backed source; archive responses under `lit/queries/loop_<idx>/`, mirror metadata in `lit/evidence_map.csv`, and update the bibliography before advancing.
3. Keep the notebook, decision log, and reports in sync so reviewers can follow the deterministic path through sensitivity, planned writing-phase QC, and the impending review gate.
