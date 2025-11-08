# Research Notebook

Date: 2025-11-08
Seed: 20251016
Phase: literature (bootstrap)

Progress:
- Verified dataset presence and inspected header (718 columns).
- No codebook or survey-design metadata found; created TODO stubs (`data/codebook.yaml`, `config/survey_design.yaml`).
- Drafted 4 exploratory hypotheses across wellbeing, relationships, mental health, and demographics.
- Wrote a minimal PAP (`analysis/pre_analysis_plan.md`) with SRS justification and future FDR handling.
- Seeded literature with one canonical reference in `lit/bibliography.bib` and created an evidence map entry.
- Semantic Scholar query deferred pending `.env` with `S2_API_Key` and CLI script; placeholder created under `lit/queries/loop_000/query_001.json`.

Next:
- Add the Semantic Scholar CLI helper and `.env` key, then run the kickoff query.
- Build EDA and modeling scripts to generate `analysis/results.csv` entries and initial tables (with n<10 suppression).
- Expand the codebook by inferring types/ranges and documenting coercions.

---
## Loop 001 (literature)
- Ran Semantic Scholar kickoff query via `scripts/semantic_scholar_cli.py`; request returned HTTP 429 unauthenticated.
- Saved placeholder response to `lit/queries/loop_000/query_002.json` and logged in `analysis/decision_log.csv`.
- Evidence map unchanged pending successful query; will extract DOIs once API is available.

Next:
- Add `.env` with `S2_API_Key` and rerun the search (1 req/sec enforced).
- Start minimal EDA script to profile key variables and ranges; draft `tables/` outputs with n<10 suppression logic.
