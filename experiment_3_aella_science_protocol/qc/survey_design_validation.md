# Survey Design Validation
Generated: 2025-11-03T20:29:10.282966Z | Seed: 20251016

Command: `python analysis/code/validate_survey_design.py --dataset childhoodbalancedpublic_original.csv --codebook docs/codebook.json --config config/agent_config.yaml --output docs/survey_design.yaml --report qc/survey_design_validation.md`

## Dataset Summary
- File: `childhoodbalancedpublic_original.csv`
- Observations: 14443
- Columns: 718
- Design: **Simple Random Sampling**

## Detection Summary
### Weight-like Columns
| name | codebook_label | non_missing_fraction | dtype |
| --- | --- | --- | --- |
| `weight` | — | 1.000000 | float64 |

### Strata-like Columns
None detected.

### Cluster-like Columns
None detected.

### Replicate Weight Columns
None detected.

## Notes
No survey weights, strata, or clusters detected; proceed as SRS pending provider confirmation.

All findings remain exploratory; confirm with documentation when available.

_Exploratory diagnostics only; no confidential data disclosed._