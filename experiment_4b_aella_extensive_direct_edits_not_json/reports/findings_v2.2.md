# Findings Log — Version 2.2
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Reviewer `DECISION: CONTINUE` (loop 075) keeps the release gate closed; `[CLAIM:C1]` continues to reference the Conkbayir (2023) CrossRef fallback (DOI `10.4324/b23180`) via `lit/queries/loop_075/crossref_query_001.json`, `lit/evidence_map.csv:64`, and `lit/bibliography.*` while the Semantic Scholar API is offline.
- The release dossier (manuscript PDF, LaTeX build log, tables, `reports/review_checklist.md`, and `reports/findings_v2.2`) integrates the final disclosure audit (`qc/disclosure_check_loop_076.md`), the frozen PAP, and the reviewer clearance trail so the candidate can be handed off with a complete command/log audit.
- Documentation now highlights the stabilized release artifacts, crossref/waiver evidence, and the zero-violation disclosure scan that together satisfy the release-phase requirements and preserve the deterministic seed trace in `artifacts/session_info.txt`.

## Next steps
1. Archive the release package (manuscript PDF, build log, disclosure audit, review checklist, and this findings log) for downstream publication and confirm the archive references the recorded commands.
2. Keep `lit/semantic_scholar_waiver_loop013.md` and `lit/evidence_map.csv` updated with any new CrossRef fallback entries for `[CLAIM:C1]` until Semantic Scholar access is restored.
3. Wait for release scheduling guidance; treat this experiment as complete unless new instructions arrive.
