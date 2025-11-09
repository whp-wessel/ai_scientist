# Review Checklist — Loop 074

| Concern | Status | Evidence |
| --- | --- | --- |
| **R1 – Reproducibility & seeds** | ✅ | `analysis/results.csv:1`, `artifacts/seed.txt:1`, `analysis/decision_log.csv:818|821`, `reports/findings_summary.md:1` |
| **L1 – Literature coverage** | ✅ | `lit/evidence_map.csv:63`, `lit/bibliography.bib`:morris2023protective, `lit/bibliography.json`:morris2023protective, `lit/queries/loop_073/crossref_query_001.json`, `lit/semantic_scholar_waiver_loop013.md` |
| **P1 – Disclosure audit** | ✅ | `qc/disclosure_check_loop_074.md:1` |
| **N1 – Release gate readiness** | ✅ | `artifacts/state.json:phase=release`, `reports/findings_summary.md:1`, `reports/review_checklist.md:1` |

Notes:
- The World Psychiatry (2023) CrossRef fallback (DOI 10.1002/wps.21042) keeps `[CLAIM:C1]` DOI-backed while Semantic Scholar remains offline; the metadata live in `lit/queries/loop_073/crossref_query_001.json` and the waiver log.
- The new release disclosure run (`qc/disclosure_check_loop_074.md`) reconfirms `tables/results_summary.*` and `figures/dag_design.png` exceed $n \geq 10$, so no suppression actions are needed for this candidate.
- Release gating now depends on `N16` tracking the final artifact consolidation (review checklist, findings log, manuscript parity, build log) while `N8` stays satisfied under the waiver, so the gate can clear as soon as the release package is sealed.
