# Disclosure Control Check
Date: 2025-11-09T21:23:59Z

Seed: 20251016

Threshold: n ≥ 10

Command to reproduce:
```bash
python /Users/wessel/ai_scientist/experiment_4b_aella_extensive_direct_edits_not_json/analysis/code/disclosure_check.py --tables-dir tables --figures-dir figures --output-md qc/disclosure_check_loop_074.md --min-n 10 --seed 20251016
```

| artifact | description | min_cell_n | threshold | suppression_action | notes |
| --- | --- | --- | --- | --- | --- |
| tables/results_summary.csv | table | 13507 | 10 | ok | auto scan of numeric columns |
| figures/dag_design.png | figure | n/a | 10 | n/a | Structural figure (no cells) |

violations: 0
