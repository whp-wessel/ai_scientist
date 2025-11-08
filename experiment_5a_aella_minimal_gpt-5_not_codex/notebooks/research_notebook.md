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

---
## Loop 005 (literature)
- Attempted focused Semantic Scholar search on relational outcomes:
  - `python scripts/semantic_scholar_cli.py search --query "religiosity monogamy relationship satisfaction" --limit 5 --output lit/queries/loop_005/query_001.json`
  - Result: HTTP 429 (unauthenticated); structured error saved to `lit/queries/loop_005/query_001.json` per protocol.
- Updated decision log and state; preparing to checkpoint this loop.

Notes:
- Literature enrichment remains blocked by missing `.env` `S2_API_Key`. Once available, I will extract `externalIds.DOI` from saved query results into `lit/evidence_map.csv` and cite in `reports/paper.md`.

Next:
- Provide `.env` with `S2_API_Key` and rerun the literature searches; map DOIs to `lit/evidence_map.csv`.
- If literature remains blocked, proceed to draft sensitivity plan (nonlinearity for Likert, potential confounders) while staying exploratory.

---
## Loop 006 (literature — reproducibility fix)
- Addressed Non-negotiable alert by verifying and ensuring `analysis/decision_log.csv` includes loop_005 entries (search attempt, notebook/state updates, commit request).
- Hardened literature artifacts by adding DOI URL to `lit/evidence_map.csv` (E1 → https://doi.org/10.1016/S0749-3797(98)00017-8).
- Updated `artifacts/state.json` to reflect loop_counter=6 and refreshed `artifacts/git_message.txt` to request a checkpoint.

Notes:
- Semantic Scholar expansion remains blocked by missing `.env` `S2_API_Key`. Saved queries are in `lit/queries/` and will be re-run once the key is available.

Next:
- Add `.env` with `S2_API_Key` and execute saved queries; extract `externalIds.DOI` into `lit/evidence_map.csv` and cite in `reports/paper.md`.
- Begin drafting `analysis/sensitivity_notes.md` covering ordinal modeling and potential confounders.

---
## Loop 007 (literature)
- Ran Semantic Scholar search via helper (unauthenticated):
  - `python scripts/semantic_scholar_cli.py search --query "childhood religion religiosity adult wellbeing mental health" --limit 5 --output lit/queries/loop_007/query_001.json`
- Query succeeded; saved JSON under `lit/queries/loop_007/query_001.json`.
- Extracted DOIs from the saved JSON into `lit/evidence_map.csv` using:
  - `python scripts/lit/extract_dois.py --input lit/queries/loop_007/query_001.json --output lit/evidence_map.csv --topic "childhood religiosity and wellbeing"`
- Updated `analysis/decision_log.csv` with both actions. No confirmatory analyses added this loop.

Next:
- Add `.env` with `S2_API_Key` to broaden literature queries and follow-up on abstracts most relevant to religiosity, monogamy, and wellbeing.
- Start drafting `analysis/sensitivity_notes.md` (ordinal models, nonlinearities, additional covariates) ahead of PAP freeze.

---
## Loop 008 (literature)
- Ran two Semantic Scholar queries via helper:
  - search: "religiosity monogamy relationship satisfaction" → `lit/queries/loop_008/query_001.json` (HTTP 429 unauthenticated; recorded)
  - paper: DOI 10.1016/S0749-3797(98)00017-8 → `lit/queries/loop_008/paper_ace.json` (metadata saved)
  - search: "childhood religious strictness unhappiness" → `lit/queries/loop_008/query_002.json` (success)
- Extracted DOIs from successful search into `lit/evidence_map.csv` (added E7–E11) using `scripts/lit/extract_dois.py`.
- Added `analysis/sensitivity_notes.md` (draft) outlining ordinal models, nonlinear terms, added covariates, and design-based re-runs if metadata surface.
- Updated decision log and `artifacts/state.json` (loop_counter=8). Added one-line commit request in `artifacts/git_message.txt`.

Next:
- Provide `.env` with `S2_API_Key`; expand literature (1 req/sec) and map additional DOIs into `lit/evidence_map.csv`.
- Begin implementing ordered logit refits for H1–H4 (exploratory) and evaluate nonlinearity.

---
## Loop 009 (literature)
- Ran Semantic Scholar search via helper (unauthenticated, 1 req/sec enforced):
  - `python scripts/semantic_scholar_cli.py search --query "childhood religiosity adult wellbeing depression anxiety" --limit 5 --output lit/queries/loop_009/query_001.json`
- Extracted DOIs from the saved JSON into `lit/evidence_map.csv` using:
  - `python scripts/lit/extract_dois.py --input lit/queries/loop_009/query_001.json --output lit/evidence_map.csv --topic "childhood religiosity and mental health"`
- Updated decision log and state; prepared commit message.

Notes:
- Literature coverage expanded with five additional DOIs relevant to childhood experiences and mental health/wellbeing links.
- No confirmatory analyses added; phase remains literature; PAP remains `status: draft`.

Next:
- If `.env` `S2_API_Key` becomes available, broaden searches and pull abstracts for the most relevant items to inform PAP finalization.
- Begin implementing ordered/ordinal models for key Likert outcomes (exploratory) and outline criteria for PAP freeze.

---
## Loop 010 (literature)
- Ran targeted Semantic Scholar search to support H2 (religion ↔ monogamy/satisfaction):
  - `python scripts/semantic_scholar_cli.py search --query "religiosity monogamy relationship satisfaction adult" --limit 5 --output lit/queries/loop_010/query_001.json`
- Extracted DOIs from the saved JSON into the evidence map:
  - `python scripts/lit/extract_dois.py --input lit/queries/loop_010/query_001.json --output lit/evidence_map.csv --topic "religiosity, monogamy, relationship satisfaction"`
- Updated `analysis/decision_log.csv`; no confirmatory analyses this loop; PAP remains `status: draft`.

Notes:
- Unauthenticated use succeeded (key still absent). Helper continues enforcing 1 req/sec.

Next:
- Provide `.env` with `S2_API_Key` and broaden literature (e.g., infidelity, religious homogamy, and wellbeing).
- Move toward PAP-freeze criteria: finalize estimands and covariates, then freeze/tag before any confirmatory testing.

---
## Loop 011 (literature)
- Ran focused Semantic Scholar search to broaden coverage across H1–H4 (wellbeing, relationships, mental health):
  - `python scripts/semantic_scholar_cli.py search --query "childhood religiosity adult wellbeing depression anxiety monogamy" --limit 5 --output lit/queries/loop_011/query_001.json`
- Extracted DOIs into the evidence map with topic tag "childhood religiosity and adult outcomes":
  - `python scripts/lit/extract_dois.py --input lit/queries/loop_011/query_001.json --output lit/evidence_map.csv --topic "childhood religiosity and adult outcomes"`
- Updated `analysis/decision_log.csv` and bumped `artifacts/state.json` (loop_counter=11; phase=literature). Wrote a commit message to `artifacts/git_message.txt`.

Notes:
- Five new DOIs appended (E22–E26), including a 2023 systematic review on religiosity/spirituality and depression/anxiety in youth (BMC Psychiatry; DOI: 10.1186/s12888-023-05091-2) and an older piece linking adolescent religiosity to adult wellbeing (DOI: 10.1108/02683940310484044).
- No confirmatory analyses; PAP remains `status: draft`. All public artifacts maintain n<10 suppression.

Next:
- Add `.env` with `S2_API_Key` to sustain broader literature and fetch abstracts/metadata for highly relevant items for citation in `reports/paper.md` and `lit/bibliography.bib`.
- Start drafting a literature synthesis section (theory + measurement alignment) and refine PAP estimands toward freeze.
