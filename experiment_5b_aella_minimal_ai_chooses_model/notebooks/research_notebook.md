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
