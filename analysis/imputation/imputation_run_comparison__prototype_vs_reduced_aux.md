# Imputation Run Comparison (Exploratory)

- Completed: 2025-10-16T14:16:46.353044Z
- Baseline summary (`label_a`): `analysis/imputation/mice_imputation_summary.csv` (prototype)
- Comparison summary (`label_b`): `analysis/imputation/mice_imputation_summary__reduced_aux.csv` (reduced_aux)
- Output CSV: `tables/imputation_run_comparison__prototype_vs_reduced_aux.csv`
- Seed (logged): 20251016
- No randomness introduced; deterministic join of summary tables.

## Key Findings
- No variables show mean shifts beyond 15% between `reduced_aux` and `prototype` runs.
- Variables only present in `prototype` run (dropped in `reduced_aux`): liberal, monogamy, religion.

## Regeneration
```bash
python analysis/code/compare_imputation_runs.py --summary-a analysis/imputation/mice_imputation_summary.csv --summary-b analysis/imputation/mice_imputation_summary__reduced_aux.csv --label-a prototype --label-b reduced_aux --csv-out tables/imputation_run_comparison__prototype_vs_reduced_aux.csv --md-out analysis/imputation/imputation_run_comparison__prototype_vs_reduced_aux.md --seed 20251016
```