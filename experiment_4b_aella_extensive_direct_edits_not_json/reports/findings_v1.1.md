# Findings Log — Version 1.1
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Confirmatory H1–H3 outputs (JSONs → `analysis/results_pre_bh.csv` → `analysis/results.csv`) plus `tables/results_summary.csv/.md` now reflect the deterministic seed, BH q-values, and `bh_in_scope` metadata so every table row matches the PAP-estimated effects.
- The sensitivity package (pseudo weights, design-effect grid, jackknife pseudo replicates) has been rerun with the loop-063 seed so `analysis/sensitivity_plan.md` and `outputs/sensitivity_*` preserve the uncertainty envelope that keeps HC1 the default descriptor.
- Disclosure control (`qc/disclosure_check_loop_063.md`), measurement validity (`qc/measures_validity.md`), and a new LaTeX build (`tectonic --keep-logs papers/main/manuscript.tex`) documented in `papers/main/build_log.txt` (PASS with overfull warnings) confirm that the manuscript/table/figure chain remains reproducible.
- Semantic Scholar queries still return HTTP 403, but `lit/queries/loop_063/crossref_query_001.json` captured DOI `10.1080/19349637.2014.864543` and `lit/evidence_map.csv` plus `lit/bibliography.*` now cite the same DOI so [CLAIM:C1] stays DOI-backed while the outage persists.
- The loop-063 narrative is now mirrored in `reports/findings_summary.md`, `notebooks/research_notebook.md`, and `analysis/decision_log.csv` to keep the deterministic ledger in sync before advancing to the writing phase.

## Next steps
1. Begin the writing-phase QC pass: refresh `papers/main/imrad_outline.md` if any new text belongs there, confirm LaTeX/Markdown parity, rerun `qc/strobe_sampl_checklist.md`, and draft `reports/findings_v1.2.md` once the DAG/identification plus disclosure story stays stable.
2. Continue logging blocked Semantic Scholar queries + CrossRef fallbacks (lit/queries/loop_0XX/) so every `[CLAIM:<ID>]` maintains DOI coverage; each query needs a `analysis/decision_log.csv` entry and an updated `lit/evidence_map.csv` row until S2 is back online.
3. Keep tracking the loop-level ledger (notebook, reports/findings_*.md, analysis/decision_log.csv) so reviewers see the deterministic path before review-phase checks begin.
