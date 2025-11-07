# Research Notebook

## 2025-11-07 – Bootstrap Loop
- Skimmed repository layout; no prior analyses existed. Confirmed dataset dimensions (14,443 × 718) via `python` pandas peek and noted absence of apparent weight/strata columns → provisional SRS assumption recorded in PAP + hypotheses.
- Created `scripts/semantic_scholar_cli.py` to comply with the mandated Semantic Scholar workflow (rate-limited via `artifacts/.s2_rate_limit.json`). Ran kickoff query on _childhood adversity & adult wellbeing_; stored JSON under `lit/queries/loop_000/query_001.json`.
- Drafted baseline documentation (`docs/baseline_inputs.md`), initial PAP (`analysis/pre_analysis_plan.md`), and populated `analysis/hypotheses.csv` with four exploratory hypotheses spanning abuse, guidance, class mobility, and religiosity.
- Seeded literature tracking by extracting bibliographic details from the kickoff query, opening `lit/bibliography.md`/`lit/evidence_map.csv`, and noting need for deeper review.
- Logged actions + commands in `analysis/decision_log.csv` and updated `artifacts/state.json` with bootstrap completion + next-action checklist.

### Immediate Next Steps
1. Build lightweight codebook from column headers (question text + recode logic).
2. Generate descriptive statistics + missingness plots for variables tied to H1–H4.
3. Deepen literature review (2–3 more targeted queries) to support PAP freeze.

## 2025-11-07 – Loop 001
- Rebuilt the H1–H4 variable codebook by scanning all 718 headers and extracting the paired “question text + short code” columns; summarized distributions via `python tables/loop001_*` scripts (see `tables/loop001_numeric_descriptives.csv` and `tables/loop001_categorical_counts.csv`) and documented interpretations in `docs/codebook_priority.md`.
- Verified the lack of design/weight variables by searching headers for `weight`, `strata`, and `cluster`; updated both the PAP and hypothesis register with an explicit SRS justification grounded in that scan.
- Exported public-ready descriptive tables (all cells n≥135) and cross-referenced them inside the PAP for reproducibility.
- Expanded the literature base: ran a Semantic Scholar search on “childhood emotional abuse adult depression longitudinal” (`lit/queries/loop_001/query_001.json`) and, after repeated 429 throttles, switched to DOI-based `paper` pulls (`query_002.json`, `query_003.json`) to cover ACE→depression moderation and religiosity→anxiety evidence. Logged all attempts plus the rate-limit workaround here for traceability.
- Updated `lit/bibliography.md` and `lit/evidence_map.csv` with four new peer-reviewed sources tied to H1 and H4, noting which JSON file each entry came from.
- Recorded the loop in `analysis/decision_log.csv` and refreshed `artifacts/state.json`(loop counter, next actions) to keep the experiment state machine aligned.
