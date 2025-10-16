# Research Notebook (Exploratory)

Generated: 2025-10-16T12:44:10Z  
Seed: 20251016  
Regenerate: `python analysis/code/bootstrap_setup.py --only notebook`

## Datasets

- `childhoodbalancedpublic_original.csv` — 14,443 rows, 718 columns (initial inspection).
- Additional metadata files: `docs/codebook.json`, `docs/survey_design.yaml`, `config/agent_config.yaml` (placeholders pending validation).

## Work Completed

- Created bootstrap scaffolding for reproducibility artifacts and documentation.
- Drafted initial hypothesis registry (HYP-001 to HYP-004).
- Authored preliminary pre-analysis plan covering priority hypotheses.
- Logged tasks in `artifacts/state.json` and `analysis/decision_log.csv`.

## Candidate Hypotheses (Exploratory)

- `HYP-001`: Childhood emotional abuse ↔ adult self-love score.
- `HYP-002`: Childhood socioeconomic status ↔ current net worth category.
- `HYP-003`: Current religious practice ↔ monogamy preference.
- `HYP-004`: Mental health diagnosis ↔ recent emotional difficulty.

## Immediate Next Steps

1. Validate survey design elements (weights, strata, clusters).
2. Generate weighted descriptive statistics for outcome and predictor variables.
3. Assess missingness and coding for variables in the draft PAP.

## Open Questions

- Are official survey weights available, or must we model SRS?
- How are Likert responses encoded (numeric vs string labels)?

## Reproducibility

- Notebook scaffold is text-only; regenerate via `python analysis/code/bootstrap_setup.py --only notebook`.
- All future code executed in separate scripts / notebooks with seed `20251016`.
