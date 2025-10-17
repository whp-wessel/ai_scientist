# HYP-002 MI Robustness (Exploratory)

- Completed: 2025-10-17T22:58:59.012898Z
- Seed: 20251016
- Alpha: 0.05
- Scenarios: complete_case, mi_prototype, mi_reduced_aux
- Coefficient CSV: `tables/robustness_hyp002_mi_scenarios_coefficients.csv`
- Coefficient Markdown: `tables/robustness_hyp002_mi_scenarios_coefficients.md`
- Secondary CSV: `tables/robustness_hyp002_mi_scenarios_secondary.csv`
- Secondary Markdown: `tables/robustness_hyp002_mi_scenarios_secondary.md`

## Key Comparisons
- complete_case: estimate=0.3164, 95% CI [0.2909, 0.3419]
- mi_prototype: estimate=0.3164, 95% CI [0.2909, 0.3419]
- mi_reduced_aux: estimate=0.3164, 95% CI [0.2909, 0.3419]
- Max difference across scenarios: 0.0000.

## Regeneration
```bash
python analysis/code/run_mi_robustness.py --seed 20251016
```