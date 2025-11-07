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

## 2025-11-07 – Loop 002
- Extended the codebook to cover teen-period exposures and adjustment covariates by writing `scripts/make_loop002_descriptives.py`, exporting `tables/loop002_teen_covariate_numeric.csv` and `tables/loop002_teen_covariate_categorical.csv`, and summarizing the additions inside `docs/codebook_priority.md`.
- Prototyped regression models via `scripts/run_loop002_models.py`: OLS for H1/H2 and a binary logit for H3 (≥$1M net worth), logging coefficients to `tables/loop002_model_estimates.csv`, appending exploratory results to `analysis/results.csv`, and creating `tables/loop002_reverse_code_check.csv` to document that the anxiety “-neg” column is already aligned.
- Noted that several Likert items (e.g., self-love, abuse) yield counter-intuitive signs, so the next loop will diagnose and standardize polarity before PAP freeze; this is reflected in the PAP “Loop 002 Updates” section.
- Literature coverage: initial Semantic Scholar `search` call returned repeated 429s; switched to DOI-specific `paper` pulls for Moore & Shell (2017) and Hansen (2014), adding both entries to `lit/bibliography.md` and `lit/evidence_map.csv` under `lit/queries/loop_002/`.
- Scaffolded `reports/paper.md` with an outline, preliminary narrative, and citations so future loops can iterate toward a submit-ready manuscript.
- Updated state/logs (`analysis/decision_log.csv`, `artifacts/state.json`) with commands, seeds (deterministic), and follow-on tasks centered on scale orientation, richer models (ordered logits + H4), and PAP freezing.

## 2025-11-07 – Loop 003
- Ran Semantic Scholar query `lit/queries/loop_003/query_001.json` for “Likert reverse coding measurement reliability,” adding Sumin (2022) to cite the sign-flip + z-score strategy for aligned scales.
- Built `scripts/likert_utils.py` + `scripts/loop003_scale_audit.py` to automate the polarity check; exported diagnostics to `tables/loop003_likert_alignment.csv` showing all H1–H4 Likerts require multiplying by -1 (Strongly Agree = -3).
- Refit models through `scripts/run_loop003_models.py`, which now: (a) re-estimates H1/H2 with aligned z-scores; (b) fits an ordered logit spanning all ten wealth brackets plus the legacy ≥$1M binary logit; and (c) introduces OLS + logit religiosity→anxiety regressions with the same covariate set. Output stored in `tables/loop003_model_estimates.csv` and summarized in `analysis/results.csv`.
- Updated PAP/codebook/manuscript to document the measurement correction and note that H1 remains unexpectedly negative after alignment, motivating further investigation before freezing confirmatory claims.
- Refreshed `analysis/decision_log.csv`, `artifacts/state.json`, and `reports/paper.md` with the new findings and next-step checklist (interaction specs + PAP freeze).
