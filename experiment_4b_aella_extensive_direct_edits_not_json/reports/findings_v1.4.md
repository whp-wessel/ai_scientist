# Findings Log — Version 1.4
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Re-ran the seeded sensitivity suite with loop-specific directories (`outputs/sensitivity_pseudo_weights_loop066/*`, `outputs/sensitivity_design_effect_grid_loop066.*`, `outputs/sensitivity_replicates_loop066/sensitivity_replicates_summary.json`) so each uncertainty artifact is reproducible via the commands recorded in `analysis/sensitivity_manifest.md`.
- The pseudo-weight draws show the effective sample dropping from 14,443 (DEFF=1.0) to 9,533.2 (DEFF=1.5) while H1/H2 remain near −0.1201/+0.0998 and H3’s SE expands from 0.0331 to 0.0405; the design-effect grid keeps CIs negative down to ~6,754 effective observations at DEFF=2.0, and the jackknife replicates report SEs of ≈0.0190/0.0020/0.0177 for H1/H2/H3, respectively, matching the HC1 band.
- No new tables or figures were published this loop, so the `qc/disclosure_check_loop_064.md` audit (violations: 0) still covers the released artifacts while the scenario suite primes the writing-phase QC pass (N14).

## Next steps
1. Complete the writing-phase QC pass: verify Markdown/LaTeX parity, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, validate `reports/identification.md` (with the DAG), rebuild the manuscript, and record the results in `reports/findings_v1.5.md` once the loop passes the writing gate.
2. Continue logging Semantic Scholar (or CrossRef fallback) queries so each `[CLAIM:<ID>]` keeps a DOI-backed source; archive the responses under `lit/queries/loop_<idx>/` and mirror the metadata in `lit/evidence_map.csv` + bibliography artifacts before advancing.
3. Keep the decision log, notebooks, and reports synchronized so reviewers can follow the deterministic path through sensitivity, planned writing QC, and the impending review gate.
