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

---
## Loop 003 (literature → exploratory analysis)
- Implemented `scripts/analysis/run_models.py` and ran:
  - `python scripts/analysis/run_models.py --input childhoodbalancedpublic_original.csv --hypotheses analysis/hypotheses.csv --results analysis/results.csv --seed 20251016`
- Appended 6 exploratory OLS results (standardized) to `analysis/results.csv` for H1–H4. All analyses assume SRS (no weights/strata/clusters detected) and include justification.
- Attempted Semantic Scholar search via helper; received HTTP 429 unauthenticated. Saved structured error to `lit/queries/loop_003/query_002.json`. Helper updated to handle and persist HTTP errors.

Highlights (exploratory; not confirmatory):
- H3 (Teen SES → depression, stress) shows positive associations (p≈0).
- H4 (Gender → anxiety item) shows positive association (p≈0).
- H2 (Religion → monogamy) positive association; relationship satisfaction ~ religion is small and not significant at conventional levels.
- H1 (Childhood religious strictness → unhappiness) near zero.

Next:
- Provide `.env` with `S2_API_Key` to run literature queries and extract DOIs into `lit/evidence_map.csv`.
- Consider robustness (e.g., nonlinearity, ordinal models) and potential confounders; plan sensitivity checks.

---
## Loop 004 (literature)
- Ran Semantic Scholar search via helper (unauthenticated; awaiting `.env` `S2_API_Key`):
  - `python scripts/semantic_scholar_cli.py search --query "childhood religion religiosity adult wellbeing mental health" --limit 5 --output lit/queries/loop_004/query_001.json`
  - Result: HTTP 429 captured to `lit/queries/loop_004/query_001.json` (rate-limited without key).
- Added safe public cross-tabulation table with small-cell suppression (n<10 → "<10"):
  - `python scripts/analysis/make_tables.py --input childhoodbalancedpublic_original.csv --var1 religion --var2 monogamy --output tables/religion_by_monogamy.csv --threshold 10`
  - Output: `tables/religion_by_monogamy.csv`.

Notes:
- Literature expansion remains blocked by missing API key. Once provided, I will re-run the saved search(es) and extract DOIs to `lit/evidence_map.csv`.

Next:
- Provide `.env` with `S2_API_Key`; then parse `externalIds.DOI` from successful search results into `lit/evidence_map.csv`.
- Consider ordinal models for Likert items and robustness checks; prepare sensitivity plan draft.
