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

---
## Loop 002 (literature)
- Implemented `scripts/analysis/eda.py` and ran:
  - `python scripts/analysis/eda.py --input childhoodbalancedpublic_original.csv --summary outputs/eda_summary.json --public-counts tables/key_vars_value_counts.csv`
- Produced `outputs/eda_summary.json` (rows=14443, cols=718) and `tables/key_vars_value_counts.csv` (public; n<10 suppressed as "<10").
- Aligned hypotheses with actual dataset column labels for outcome items that exist only as label strings (e.g., `I am not happy (ix5iyv3)-neg`).
- Expanded `data/codebook.yaml` with entries for key variables and noted coding assumptions.
- Literature search remains deferred pending `.env` with `S2_API_Key` for the Semantic Scholar helper.

Next:
- Add `.env` with `S2_API_Key` and run the saved search; extract DOIs into `lit/evidence_map.csv`.
- Draft minimal modeling script and begin exploratory estimates for H1–H4 (record in `analysis/results.csv`).
