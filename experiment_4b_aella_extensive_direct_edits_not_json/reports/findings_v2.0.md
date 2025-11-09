# Findings Log — Version 2.0
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Synced the release-phase dossier (review checklist, findings summary, identification memo, STROBE/SAMPL checklist, and manuscript) with the frozen PAP while keeping `[CLAIM:C1]` DOI-backed via the Morris & Hays-Grudo 2023 CrossRef fallback recorded at `lit/queries/loop_073/crossref_query_001.json`.
- Executed the disclosure scan for this candidate (`qc/disclosure_check_loop_074.md`) so `tables/results_summary.*` and `figures/dag_design.png` satisfy the $n \geq 10$ guardrail before public dissemination.
- Rebuilt the manuscript with `tectonic --keep-logs papers/main/manuscript.tex` and logged the successful compile in `papers/main/build_log.txt` (BibTeX warnings = 0, Overfull hboxes flagged but unchanged), keeping the TeX/Markdown twins synchronized.

## Next steps
1. Complete `N17` by packaging the release assets (final `papers/main/manuscript` PDF, `reports/findings_v2.0`, `reports/review_checklist`, `qc/disclosure_check_loop_074.md`, and the build log) and confirming the waiver-backed crossref ledger continues to anchor `[CLAIM:C1]` while the release gate closes.
2. Monitor `review/research_findings.md` for any new reviewer directives and log responses in `analysis/decision_log.csv` before declaring the final release-phase gate satisfied.
3. Keep the CrossRef/waiver ledger ready for `N8` (resume Semantic Scholar once OPS restores the S2 credential) so any late-breaking citation updates remain traceable even after the release package ships.
