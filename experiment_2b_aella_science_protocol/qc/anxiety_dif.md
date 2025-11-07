# Anxiety Item DIF (CSA \u00d7 Gender)
Generated: 2025-11-04T09:36:03.886043+00:00 | Seed: 20251016

- Outcome: `I tend to suffer from anxiety (npvfh98)-neg`
- CSA indicator: `CSA_score_indicator`
- Group variable: `gendermale`

## Model Specification
- Ordinal logistic (logit link) with thresholds for 7 response categories.
- Baseline model: CSA + group (no interaction).
- Full model: CSA + group + CSA\u00d7group interaction.

## Interaction Effect
- Estimate: -0.037 (SE = 0.075)
- z = -0.489, p = 0.6246
- 95% CI: [-0.183, 0.110]

## Likelihood-Ratio Test
- LR statistic = 0.239 on 1 df, p = 0.6248

## Subgroup Means (complete cases)

| CSA | Gender (1=focal) | n | Mean | SD |
|---|---|---|---|---|
| 0 | 0 | 4062 | -1.323 | 1.802 |
| 0 | 1 | 7155 | -0.245 | 2.103 |
| 1 | 0 | 2121 | -1.783 | 1.608 |
| 1 | 1 | 1099 | -0.944 | 1.879 |

## Interpretation
- The interaction term captures differential item functioning (DIF); non-zero values indicate CSA-related shifts differ by gender.
- Likelihood-ratio test compares models with and without the interaction.

## Reproducibility
- Command: `python analysis/code/test_anxiety_dif.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --outcome "I tend to suffer from anxiety (npvfh98)-neg" --csa CSA_score_indicator --group gender --group-value-column gendermale --out-table tables/diagnostics/anxiety_dif.csv --out-md qc/anxiety_dif.md`
