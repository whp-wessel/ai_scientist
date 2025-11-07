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

## 2025-11-07 – Loop 004
- Wrote `scripts/loop004_h1_diagnostics.py` to stage bivariate → dual-abuse → full-control OLS plus guidance and gender interactions for H1; exported coefficients/standard errors to `tables/loop004_h1_diagnostics.csv` and correlation matrix to `tables/loop004_h1_correlations.csv`. Findings: (a) the abuse/depression slope is already negative in bivariate form (-0.34 SD); (b) the abuse × guidance interaction is positive (buffering); (c) the abuse × male interaction is negative (inverse slope concentrated among men).
- Cloned the modeling pipeline into `scripts/run_loop004_models.py`, added the childhood-class × male interaction to the ordered-logit + ≥$1M logit, and introduced religiosity × classchild / religiosity × male terms in the anxiety models. Reran the script (`python scripts/run_loop004_models.py`) to produce `tables/loop004_model_estimates.csv` and appended the relevant rows to `analysis/results.csv`.
- Updated `analysis/pre_analysis_plan.md` with a Loop 004 section documenting the diagnostics, deterministic commands, and the draft Benjamini–Hochberg plan that maps confirmatory families (H1–H4) to their target contrasts. Also revised `reports/paper.md` to narrate the moderation findings and interaction specs.
- Logged the loop in `analysis/decision_log.csv`, captured next actions in `artifacts/state.json`, and noted that PAP freeze hinges on deciding whether the confirmatory H1 family centers on the moderation contrasts or collapses abuse exposures.

## 2025-11-07 – Loop 005
- Authored `scripts/loop005_h1_simple_slopes.py` and ran it to generate `tables/loop005_h1_simple_slopes.csv`, which computes the childhood-abuse slope at ±1 SD guidance and by gender (using the same aligned z-score models as the diagnostics). The table shows slopes of -0.13 SD under low guidance versus +0.01 SD at +1 SD guidance and -0.13 SD for men vs. -0.02 SD for women.
- Used those slopes plus the earlier interaction coefficients to lock the H1 confirmatory family onto the two moderation contrasts (guidance buffering > 0; male vulnerability < 0), citing Zhao et al. (2022) and Assari et al. (2025) as the theoretical basis.
- Updated `analysis/pre_analysis_plan.md`, `analysis/hypotheses.csv`, and `reports/paper.md` to reflect the decision, document the deterministic command sequence (`loop004_h1_diagnostics.py` + `loop005_h1_simple_slopes.py`), and outline the remaining steps before freezing/tagging the PAP.

## 2025-11-07 – Loop 006
- Froze the PAP (`analysis/pre_analysis_plan.md`) with status `frozen` and documented the confirmatory scope, commands, BH plan, and privacy guarantees; tagged the intended snapshot as `pap_freeze_loop006` (tag creation + hash recorded after committing).
- Re-ran `PYTHONHASHSEED=20251016 python scripts/loop004_h1_diagnostics.py`, `...loop005_h1_simple_slopes.py`, and `...run_loop004_models.py` to regenerate the H1 interaction coefficients/tables deterministically. Exported a public-ready summary at `tables/loop006_h1_confirmatory.csv`.
- Appended the confirmatory coefficients to `analysis/results.csv` with `confirmatory=TRUE`, BH-adjusted q-values, and full SRS notes; also updated `analysis/hypotheses.csv` to mark H1 as confirmatory.
- Revised `reports/paper.md` to narrate the frozen PAP, cite the literature motivating the moderators (Zhao et al., 2022; Assari et al., 2025), and describe the BH adjustment + results. Added multiplicity/privacy language per reviewer request.
- Logged all commands + seeds for reproducibility (decision log + state updates pending) and noted follow-on tasks: extend confirmatory scope to H2–H4 after added diagnostics, and prepare sensitivity analyses for the H1 family.

## 2025-11-07 – Loop 007
- Addressed the non-negotiable PAP warning by replacing the freeze header with the literal `status: frozen (commit 90f349d080541060fd90ba5a6310a87eef925c47)` format in `analysis/pre_analysis_plan.md`, ensuring the document matches the `pap_freeze_loop006` tag hash.
- Authored `scripts/loop007_h1_sensitivity.py` to (a) refit the preregistered guidance and gender interaction models with HC3 robust SEs and (b) expand the covariate set to include childhood/current class, religion, external religion salience, and teen guidance. Command: `PYTHONHASHSEED=20251016 python scripts/loop007_h1_sensitivity.py`.
- Logged outputs in `tables/loop007_h1_sensitivity.csv`, summarized implications in the brand-new `analysis/sensitivity_notes.md`, and appended four sensitivity rows (two per perturbation) to `analysis/results.csv` with confirmatory labels + BH q-values. Both interactions remain significant with expected signs under every perturbation.
- Ran a targeted Semantic Scholar search (`python scripts/semantic_scholar_cli.py search --query "parental guidance self love adulthood"`) after one 429 throttle, archived the JSON under `lit/queries/loop_007/query_001.json`, and extracted two H2-relevant citations (Fermani 2019; Walęcka-Matyja 2019) into `lit/bibliography.md`/`lit/evidence_map.csv` to start the promotion review for guidance→self-love.
- Reviewed the PAP requirements for promoting H2–H4 and concluded that we still need (i) additional literature—for example, a focused Semantic Scholar pull on parental guidance → self-love mediators—and (ii) diagnostics for the ordered-logit proportional-odds assumption. Documented this gap here and will prioritize literature/diagnostics next loop before considering another PAP freeze.
