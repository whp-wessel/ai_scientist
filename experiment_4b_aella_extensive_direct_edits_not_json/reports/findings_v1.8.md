# Findings Log — Version 1.8
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Added `Jung (2018)` (Childhood Adversity, Religion, and Change in Adult Mental Health, DOI `10.1177/0164027516686662`) to `lit/evidence_map.csv`, `lit/bibliography.*`, and logged the CrossRef fallback in `lit/queries/loop_071/crossref_query_003.json` so `[CLAIM:C1]` keeps DOI-backed resilience coverage while the Semantic Scholar key still blocks the same query.
- Reran the disclosure audit (`python analysis/code/disclosure_check.py --tables-dir tables --figures-dir figures --output-md qc/disclosure_check_loop_070.md --seed 20251016`) to confirm `tables/results_summary.*` and `figures/dag_design.png` still pass the $n \geq 10$ rule for public release.
- Updated the release checklist (`reports/review_checklist.md`), findings summary (`reports/findings_summary.md`), and `artifacts/state.json` (loop_counter=71, new next action `N16`) so the release-phase gate is auditable while we await the restored Semantic Scholar credential.

## Next steps
1. Keep waiver `N8` in place: once the S2 key is restored, rerun the archived Semantic Scholar queries, append their responses + ticket ID to `lit/semantic_scholar_waiver_loop013.md`, and push any new DOI-backed evidence into `lit/evidence_map.csv`/`lit/bibliography.*`.
2. Use `N16` to keep the review checklist, disclosure memo, DAG, and findings log synchronized so the final release can proceed immediately after the literature gate clears.
3. Monitor `review/research_findings.md` for any new reviewer directives before the release gate; log every update in `analysis/decision_log.csv` and adjust the release backlog if further fixes are needed.
