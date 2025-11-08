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
