# Research Notebook

## 2025-11-08 — Bootstrap (Loop 0)
- Surveyed repository: dataset present but no codebook/design files. Logged TODOs under `docs/TODO.md`.
- Inspected first rows of `childhoodbalancedpublic_original.csv`; ~718 columns mixing demographics, childhood context, and adult wellbeing indicators.
- Created baseline artifacts (`analysis/pre_analysis_plan.md`, `analysis/hypotheses.csv`, `analysis/results.csv`) and articulated four thematic hypotheses.
- Implemented `scripts/semantic_scholar_cli.py` to comply with the required Semantic Scholar workflow; captured first query output at `lit/queries/loop_000/query_001.json`.
- Seeded literature tracking (see `lit/bibliography.bib` + `lit/evidence_map.csv`) and recorded bootstrap decisions in `analysis/decision_log.csv`.
- Next loop priorities: profile missingness & distributions for key variables, draft recode scripts, and expand literature on childhood adversity ↔ adult wellbeing.

## 2025-11-08 — Loop 1
- Ran `python analysis/scripts/profile_key_variables.py` (seedless) to summarize exposures/outcomes for H1–H4. All eight targets have ≥14,400 observations with ≤17 missing cases (≤0.12%), recorded in `analysis/profiling/loop001_key_vars_summary.csv`.
- Value-count outputs confirm the Likert coding spans −3 (strongly disagree/low exposure) to +3 (strongly agree/high exposure). This supports a future recode that rescales variables to −1..1 (centered) while keeping the ordinal ordering intact.
- Childhood adversity items (e.g., emotional abuse, depression) show long tails toward +3, whereas adult happiness/career satisfaction skew positive; important for modeling to include nonlinear terms or treat as ordered outcomes.
- Logged that `classcurrent` is roughly centered near the mid-class (mean ≈3.0 on a 0–6 ladder), giving adequate variance for H3.
- Expanded literature via `scripts/semantic_scholar_cli.py` searches (see `lit/queries/loop_001/query_001-006.json`). Added: So 2024 on parental career support→occupational engagement, Zhang 2025 on childhood emotional neglect mediating adult depression, Lin & Chiao 2024 on ACEs and problematic internet use, and Asmayawati 2023 on early digital literacy, all captured in `lit/bibliography.bib`/`lit/evidence_map.csv`.
- Privacy note: missing-value counts are <10 but remain in `analysis/profiling/` only (non-public). Future public tables under `tables/` will suppress any <10 cells.

## 2025-11-08 — Loop 2
- Built `analysis/scripts/derive_likert_scales.py` to center/standardize the −3..3 variables feeding H1–H4. The script writes `analysis/derived/loop002_likert_scales.csv` containing both `_scaled` (÷3) and `_z` ((x−μ)/σ) variants plus the shared covariate set (selfage, gendermale, education, classchild, classteen, classcurrent).
- Updated the PAP + hypotheses registry so future models explicitly reference the derived columns and the fixed covariate stack; SRS justification unchanged pending design metadata.
- Prototyped H1/H2 using `python analysis/scripts/prototype_h1_h2_regressions.py` (OLS + HC3). Results: each one-unit increase in `mds78zu_scaled` associates with −0.18 SDs in adult unhappiness (`ix5iyv3_scaled`, n=14,426), while each unit increase in `pqo6jmj_scaled` predicts +0.11 SDs in work satisfaction (`z0mhd63_scaled`, n=14,429). Recorded effect sizes in `analysis/results.csv` (exploratory only) and stored full regression outputs under `analysis/results/loop002_h1_h2_regressions.csv`.
- Next focus: extend harmonized scales to the H3/H4 outcomes, profile interaction terms (e.g., sex × adversity), and freeze the PAP before labeling any confirmatory tests.

## 2025-11-08 — Loop 3
- Extended scale derivation to include `classcurrent_scaled` and `classcurrent_z` in `analysis/scripts/derive_likert_scales.py`; regenerated `analysis/derived/loop002_likert_scales.csv` (n=14,443).
- Implemented `analysis/scripts/prototype_h3_h4_regressions.py`:
  - H3 (digital_exposure): OLS(HC3) of `classcurrent_z` on `4tuoqly_scaled` + covariates (age, male, education, classchild, classteen); n=14,428; β=0.0425 (SE=0.0102, p=3.07e-05).
  - H4 (mental_health_continuity): OLS(HC3) of `wz901dj_scaled` on `dfqbzi5_scaled` + covariates (age, male, education, classchild, classteen, classcurrent); n=14,428; β=−0.3240 (SE=0.0071, p<1e-300).
- Appended results to `analysis/results.csv` (exploratory) and saved detailed outputs to `analysis/results/loop003_h3_h4_regressions.csv`.
- Updated the PAP with a freeze-ready diagnostics plan and clarified H3 outcome handling (ordinal status, ordered-logit sensitivity).
- Next: decide confirmatory families and freeze/tag the PAP; add pre-specified interaction terms and run ordered logit sensitivity for H3.

## 2025-11-08 — Loop 4
- Froze the PAP: set `analysis/pre_analysis_plan.md` to `status: frozen (commit <hash>)`, defined four confirmatory families (H1–H4) with precise estimands and OLS(HC3) models; H3 adds a pre-specified ordered-logit sensitivity.
- Pre-specified sensitivities: gender interaction (`gendermale × predictor`) and quadratic terms for H1/H2; these are sensitivity-only, not confirmatory.
- Marked primary hypotheses as confirmatory in `analysis/hypotheses.csv` (one primary test per family), preserving SRS justification.
- Added `analysis/scripts/ordered_logit_h3.py` to operationalize H3’s ordered-logit sensitivity for the next loop.
- Logged actions in `analysis/decision_log.csv` and prepared a commit request in `artifacts/git_message.txt` with tag plan `pap_freeze_loop004`.
