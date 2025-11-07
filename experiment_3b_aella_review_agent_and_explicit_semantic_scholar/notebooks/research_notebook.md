# Research Notebook

## Loop 000 — Bootstrap Refresh (2025-11-07)

**Seed:** 20251016  
**Dataset:** `childhoodbalancedpublic_original.csv` (14,443 x 718; verified this loop).  
**Global regeneration command (scaffold):**
```bash
python runner.py --phase literature --loop 0 --seed 20251016
```

### 1. Data Sanity + Reproducibility Hooks
- Confirmed dataset shape and column availability via:
  ```bash
  python - <<'PY'
  import pandas as pd
  df = pd.read_csv('childhoodbalancedpublic_original.csv')
  print({'rows': len(df), 'cols': df.shape[1]})
  print(df.columns[:10].tolist())
  PY
  ```
  DtypeWarning (mixed types in column 68) logged for remediation in cleaning script.
- `qc/data_checks.md` updated with the command above, PII scan notes, and the plan
  to codify checks inside `analysis/scripts/data_checks.py`.
- Reaffirmed seed 20251016; all future scripts will accept `--seed` and write it
  into manifests.

### 2. Hypothesis Ideation (Descriptive/Associational)
- **H1 (C1, wellbeing family):** Upper childhood SES (classchild>=4) linked to higher
  adult happiness vs childhood (h33e6gg). Priority for PAP.
- **H2 (C2, adversity family):** Childhood verbal/emotional abuse (mds78zu) increases
  likelihood of adult depression (wz901dj). Priority for PAP with negative-control
  outcome requirement.
- **H3 (C3, economic family):** Childhood SES predicts adult net worth (networth)
  after adjusting for education.
- **H4 (C4, psychosocial family):** Higher anxiety (npvfh98) aligns with lower adult
  happiness relative to childhood.
  These hypotheses are now recorded in `analysis/hypotheses.csv` with status tags.

### 3. PAP Drafting + LaTeX Alignment Plan
- `analysis/pre_analysis_plan.md` refreshed (status: draft) with detailed estimands,
  missingness/imputation approach, robustness checks, and explicit regeneration
  commands. It reiterates that LaTeX parity will be tracked via
  `papers/main/build_log.txt` once manuscript drafting begins.
- Blockers before freeze: survey design verification, literature coverage (>=3 DOI
  sources for claim IDs), measurement validity table, and scripted pipeline.

### 4. Literature Scoping (Semantic Scholar)
- Query executed via Python `urllib`:
  `graph/v1/paper/search?query=childhood+nutrition+adult+wellbeing+survey&limit=5&fields=title,year,venue,externalIds,url,openAccessPdf,authors,citationCount,abstract`
- Response stored at `lit/queries/loop_000/query_001.json` with timestamp and full
  payload. No rate-limit issues.
- Extracted three immediately relevant sources:
  1. Lam et al. (2024) on childhood food security and cardiometabolic health.
  2. Liu et al. (2022) on childhood green space and adult mental wellbeing.
  3. Li et al. (2022) on childhood SES influencing adult wellbeing via hope/control.
  Bibliography + evidence map now reference these DOIs with rationale scores.

### 5. Next Steps
1. **T-001:** Confirm survey weight/replicate availability or lock in SRS assumption.
2. **T-002:** Produce exploratory weighted (or SRS) summaries for wellbeing and
   adversity outcomes, labeling them "Exploratory" in notebooks/tables.
3. **T-003:** Extend literature sweep to cover mediators (parental support, hope)
   and begin drafting `qc/measures_validity.md`.
