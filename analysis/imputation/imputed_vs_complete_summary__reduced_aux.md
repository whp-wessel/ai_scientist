# Imputed vs Complete-Case Review (Exploratory)

- Completed: 2025-10-16T14:15:47.817777Z
- Seed (logged): 20251016
- Original dataset: `childhoodbalancedpublic_original.csv`
- Imputed dataset: `data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz`
- Summary CSV: `tables/imputed_vs_complete_summary__reduced_aux.csv`
- All computations deterministic (no additional randomness).

## Key Findings
- Imputed means and variances remain within ±15% of complete-case benchmarks for all reviewed variables.

## Next Steps
- Integrate complete-case vs imputed comparisons into PAP robustness checks.
- Inspect joint distributions (e.g., abuse × self-love) using MI once PAP is finalized.

## Regeneration
```bash
python analysis/code/review_imputed_vs_complete.py --dataset childhoodbalancedpublic_original.csv --imputed data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz --mapping analysis/imputation/mice_variable_map__reduced_aux.json --csv-out tables/imputed_vs_complete_summary__reduced_aux.csv --md-out analysis/imputation/imputed_vs_complete_summary__reduced_aux.md --seed 20251016
```