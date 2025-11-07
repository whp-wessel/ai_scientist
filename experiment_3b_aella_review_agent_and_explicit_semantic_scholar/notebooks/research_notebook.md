# Research Notebook

## Loop 000 — Bootstrap (2025-11-07)

**Seed**: 20251016  
**Dataset**: `childhoodbalancedpublic_original.csv` (14,443 × 718).  
**Regeneration command** (scaffold):
```bash
python runner.py --phase literature --loop 0 --seed 20251016
```

### Objectives This Loop
1. Stand up reproducibility scaffolding (state file, PAP draft, hypothesis registry).
2. Document initial data availability & QC checklist.
3. Launch first Semantic Scholar query (childhood nutrition framing) and capture artifact.

### Data Snapshot
- Executed quick inspection via `python - <<'PY' ...` to confirm matrix dimensions and key
  columns (age, gender, childhood class, wellbeing, trauma, net worth).
- Noted DtypeWarning on column 68 (mixed types) — plan to coerce to numeric during cleaning.

### Candidate Hypotheses (Descriptive/Associational)
1. **H1 (C1)**: Higher childhood SES (classchild) correlates with stronger agreement that
   adult life is happier than childhood (h33e6gg).
2. **H2 (C2)**: Adolescents who received useful parental guidance (dcrx5ab) show lower
   current anxiety (npvfh98).
3. **H3 (C3)**: Childhood verbal/emotional abuse (mds78zu) associates with higher adult
   depression (wz901dj).
4. **H4 (C4)**: Larger sibling groups predict lower current net worth brackets (networth).

Priority hypotheses for PAP drafting: **H1** and **H3** due to policy relevance for
intergenerational wellbeing and trauma mitigation.

### Literature Plan
- Semantic Scholar query issued: `graph/v1/paper/search?query=childhood+nutrition&limit=5&fields=title,year,venue,externalIds,url,authors`.
- Response returned HTTP 429 (rate-limited). Captured JSON under
  `lit/queries/loop_000/query_001.json` for auditability.
- Next actions: retry with exponential backoff and/or register for API key; in parallel
  prepare fallback general web search log if rate-limit persists.

### PAP & Reporting Alignment
- Drafted `analysis/pre_analysis_plan.md` (status: draft) with pathways for hypotheses H1 & H3
  and placeholder regeneration command referencing forthcoming scripts.
- Notebook + PAP both specify how LaTeX parity will be maintained (MANIFEST + build log once
  writing phase begins).

### Outstanding Risks / TODOs
- Survey weights unknown (Task T-001).
- Evidence map currently has placeholders only; need ≥3 DOI-backed cites before PAP freeze.
- Measurement validity table absent; flagged as blocker before confirmatory analysis.

### Artifacts Created / Updated
- `docs/codebook.json`, `docs/survey_design.yaml`, `config/agent_config.yaml`
- `analysis/hypotheses.csv`, `analysis/pre_analysis_plan.md`
- `qc/data_checks.md`, `artifacts/state.json`, `lit/evidence_map.csv`, `lit/bibliography.bib`
- `lit/queries/loop_000/query_001.json`

All artifacts above are deterministic text files; re-running the regeneration command at the
top of this section reproduces the bootstrap state (modulo manual edits tracked via git).
