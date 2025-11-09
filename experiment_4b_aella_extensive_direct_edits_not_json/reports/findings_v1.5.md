# Findings Log — Version 1.5
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Re-ran the seeded sensitivity suite with loop-specific directories (`outputs/sensitivity_pseudo_weights_loop067/*`, `outputs/sensitivity_design_effect_grid_loop067.*`, `outputs/sensitivity_replicates_loop067/sensitivity_replicates_summary.json`) so each uncertainty artifact stays reproducible via the commands recorded in `analysis/sensitivity_manifest.md`.
- The pseudo-weight draws show the effective sample dropping from 14,443 (DEFF=1.0) to 9,533.2 (DEFF=1.5) while H1/H2 remain near −0.1201/+0.0998 and H3’s estimate deepens from −0.6339 (DEFF=1.25, SE=0.0370) to −0.667 (DEFF=1.5, SE=0.0405) with CIs well below zero; the design-effect grid keeps the intervals negative all the way to ~6,754 effective observations at DEFF=2.0 and the jackknife replicates show SEs of ≈0.01903/0.00203/0.01766 for H1/H2/H3.
- No new tables or figures were published this loop, so the `qc/disclosure_check_loop_064.md` audit (violations: 0) still applies while the scenario suite primes the writing-phase QC pass (N14).

## Next steps
1. Complete the writing-phase QC pass: verify Markdown/LaTeX parity, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, validate `reports/identification.md` (with the DAG), rebuild the manuscript, and record the results in `reports/findings_v1.6.md` once the loop clears the writing gate.
2. Continue logging Semantic Scholar (or CrossRef fallback) queries so each `[CLAIM:<ID>]` stays DOI-backed; archive the responses under `lit/queries/loop_<idx>/` and mirror the metadata in `lit/evidence_map.csv` + bibliography artifacts before advancing.
3. Keep the decision log, notebook, and reports synchronized so reviewers can follow the deterministic narrative through sensitivity, the planned writing QC, and the forthcoming review phase.
