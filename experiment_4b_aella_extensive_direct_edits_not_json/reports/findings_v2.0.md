# Findings Log — Version 2.0
**Date:** 2025-11-09  
**Seed:** 20251016  
**PAP:** Frozen at commit `2b3ee167762ad47af1426ab47d392d38323d1b74`, tag `pap-v1`, registry `https://osf.io/5x8hu`

## Summary
- Maintained `[CLAIM:C1]`'s DOI coverage by adding the Conkbayir (2023) CrossRef fallback (DOI `10.4324/b23180`, loop 075) alongside the existing Morris & Hays-Grudo (2023) entry, updating the evidence map/bibliography while Semantic Scholar continues to return 403.
- Completed the N17 release packaging bundle (review checklist, findings log, manuscript parity, and STROBE/SAMPL checklist) so the release candidate now cites `qc/disclosure_check_loop_074.md` plus the CrossRef evidence before the gate.
- Rebuilt the manuscript with `tectonic --keep-logs papers/main/manuscript.tex` and logged the pass in `papers/main/build_log.txt` (BibTeX warnings = 0, Overfull hbox notices unchanged), keeping PDF/Markdown twins synchronized.

## Next steps
1. Await a `DECISION: CONTINUE` in `review/research_findings.md`, log any reviewer directives in `analysis/decision_log.csv`, and only activate the release gate once the reviewer clears the candidate.
2. Keep the CrossRef/waiver ledger (lit/semantic_scholar_waiver_loop013.md + lit/evidence_map.csv) current so `[CLAIM:C1]` remains DOI-backed while Semantic Scholar stays offline.
3. Stand ready to bundle the release artifact package (PDF, build log, disclosure report, review checklist, findings log) for immediate hand-off once reviewer clearance arrives.
