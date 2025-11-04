# Anxiety Convergent Validity Diagnostics
Generated: 2025-11-04T20:35:47.415120+00:00 | Seed: 20251016

- Outcome: `I tend to suffer from anxiety (npvfh98)-neg`
- Dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`
- Config: `config/agent_config.yaml`

## Correlation Summary
| Comparator | Expected Direction | Direction OK | n | Pearson r | 95% CI | Spearman ρ | Polychoric r | q (BH, Pearson) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `I tend to suffer from depression (wz901dj)` | positive | True | 14437 | 0.615 | [0.604, 0.625] | 0.610 | 0.665 | 0.000 | pairwise complete; polychoric OK |
| `I'm quite sensitive to stress (qhyti2r)-neg` | positive | True | 14437 | 0.617 | [0.607, 0.627] | 0.622 | 0.674 | 0.000 | pairwise complete; polychoric OK |
| `I love myself (2l8994l)` | negative | False | 14436 | 0.368 | [0.354, 0.382] | 0.374 | 0.409 | 0.000 | pairwise complete; polychoric OK; pearson sign != expected negative |
| `I tend to be calm/peaceful (6e6zhy3)` | negative | False | 14436 | 0.383 | [0.369, 0.397] | 0.389 | 0.431 | 0.000 | pairwise complete; polychoric OK; pearson sign != expected negative |

## Reliability Benchmarks
- Negative affect triad (anxiety, depression, stress): Cronbach's α = 0.800 (n=14437).
- Self-regulation composite (anxiety vs. reversed calm/self-love): Cronbach's α = -0.682 (n=14435; negative suggests opposing construct directions).

## Interpretation
- I love myself (2l8994l) correlation is 0.368 (observed positive, expected negative).
- I tend to be calm/peaceful (6e6zhy3) correlation is 0.383 (observed positive, expected negative).
- q-values apply Benjamini–Hochberg (q=0.05) across Pearson correlations within this diagnostic family.

## Reproducibility
- Command: `python analysis/code/evaluate_anxiety_convergence.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/anxiety_convergence.csv --out-md qc/anxiety_convergence.md --seed 20251016`
