# Findings Log — Version 1.6
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Re-ran the seeded sensitivity suite so the commands in `analysis/sensitivity_manifest.md` now cite the loop-068 directories (`outputs/sensitivity_pseudo_weights_loop068/*`, `outputs/sensitivity_design_effect_grid_loop068.*`, `outputs/sensitivity_replicates_loop068/sensitivity_replicates_summary.json`) and the deterministic seed before we tackle writing-phase QC.
- The pseudo-weight scenarios show the effective sample dropping from 14,443 (DEFF=1.0) to 11,628.5 (DEFF=1.25) to 9,533.2 (DEFF=1.5) while H1/H2 remain near −0.1201/+0.0998 and H3 stays below zero (~−0.6339 at DEFF=1.25, −0.667 at DEFF=1.5). The design-effect grid keeps the targeted family’s intervals on the same side of zero through DEFF=2.0 (e.g., H3 remains [−0.746, −0.563]) and the pseudo-replicate jackknife still reports SEs of ≈0.01903/0.00203/0.01766 for H1/H2/H3, aligning with the HC1 bands in `analysis/results.csv`.
- Logged the Semantic Scholar search for “childhood religiosity adulthood depression protective factors” (HTTPS 403 stored at `lit/queries/loop_068/query_001.json`), captured the CrossRef fallback DOI 10.1093/oso/9780195069853.003.0006 (`lit/queries/loop_068/crossref_query_001.json`), and pushed the source/doi into `lit/evidence_map.csv` and both bibliography files so Claim C1 remains DOI-backed while the API still refuses access.
- No new public tables/figures surfaced this loop, so `qc/disclosure_check_loop_064.md` (violations: 0) continues to be the latest published audit while the writing-phase QC suite (manuscript parity, outline, checklist, LaTeX build) remains the next milestone before review.

## Next steps
1. Finish the writing-phase QC pass: sync `papers/main/manuscript.tex` with its Markdown twin, refresh `papers/main/imrad_outline.md`, rerun `qc/strobe_sampl_checklist.md`, revisit `reports/identification.md` (DAG/assumptions), rebuild the manuscript (`papers/main/build_log.txt` should capture the command and warnings), and record the refreshed status in the next findings log entry.
2. Continue issuing Semantic Scholar (or CrossRef fallback) queries so each `[CLAIM:<ID>]` retains ≥1 DOI-backed source; persist every response under `lit/queries/loop_<idx>/`, update `lit/evidence_map.csv` and `lit/bibliography.*`, and surface gaps if the API regression persists.
3. Keep the decision log, notebook, and reports synchronized so the deterministic story from sensitivity through the writing-phase QC and upcoming review remains auditable.
