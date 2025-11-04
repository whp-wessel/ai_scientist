# CSA–Anxiety Interaction Diagnostics
Generated: 2025-11-04T20:51:58.839628+00:00 | Seed: 20251016

- Dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`
- Outcome: `I tend to suffer from anxiety (npvfh98)-neg`
- Predictor: `CSA_score_indicator`

## Interaction: `CSA_score_indicator:cis_identity`

- Moderator label: **Cisgender Identity**
- Sample (complete cases): 14437
- Outcome levels analysed: -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0

### Coefficients
| model | term | estimate | se | ci_low | ci_high | p_value |
| --- | --- | --- | --- | --- | --- | --- |
| ols_hc3 | Intercept | -2.346511 | 0.063959 | -2.47187 | -2.221151 | 0.0 |
| ols_hc3 | moderator[T.Not cis] | -0.443998 | 0.06529 | -0.571966 | -0.316029 | 0.0 |
| ols_hc3 | predictor | -0.472625 | 0.039658 | -0.550355 | -0.394895 | 0.0 |
| ols_hc3 | predictor:moderator[T.Not cis] | -0.03455 | 0.095181 | -0.221104 | 0.152004 | 0.716618 |
| ols_hc3 | selfage | 0.027934 | 0.001672 | 0.024657 | 0.031211 | 0.0 |
| ols_hc3 | gendermale | 0.823325 | 0.034198 | 0.756297 | 0.890354 | 0.0 |
| ols_hc3 | classchild | 0.130469 | 0.012756 | 0.105467 | 0.155472 | 0.0 |
| ordinal_logit | moderator[T.Not cis] | -0.492664 | 0.071947 | -0.63368 | -0.351648 | 0.0 |
| ordinal_logit | predictor | -0.47297 | 0.040069 | -0.551505 | -0.394435 | 0.0 |
| ordinal_logit | predictor:moderator[T.Not cis] | -0.177237 | 0.120132 | -0.412696 | 0.058221 | 0.140117 |
| ordinal_logit | selfage | 0.026001 | 0.001509 | 0.023043 | 0.028958 | 0.0 |
| ordinal_logit | gendermale | 0.777171 | 0.033062 | 0.712371 | 0.841972 | 0.0 |
| ordinal_logit | classchild | 0.127728 | 0.012019 | 0.104171 | 0.151286 | 0.0 |

### Subgroup Means (CSA level × Moderator level)
| csa_level | moderator_level | estimate | se | n_unweighted |
| --- | --- | --- | --- | --- |
| 0 | Cis | -0.561784 | 0.020241 | 10472 |
| 0 | Not cis | -1.671141 | 0.060762 | 745 |
| 1 | Cis | -1.380246 | 0.034021 | 2764 |
| 1 | Not cis | -2.199561 | 0.060715 | 456 |

## Interaction: `CSA_score_indicator:age_cohort`

- Moderator label: **Age Cohort**
- Sample (complete cases): 14437
- Outcome levels analysed: -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0

### Coefficients
| model | term | estimate | se | ci_low | ci_high | p_value |
| --- | --- | --- | --- | --- | --- | --- |
| ols_hc3 | Intercept | -1.78631 | 0.043464 | -1.8715 | -1.70112 | 0.0 |
| ols_hc3 | C(moderator)[T.30-44] | 0.405111 | 0.041265 | 0.324232 | 0.485991 | 0.0 |
| ols_hc3 | C(moderator)[T.45-59] | 0.631961 | 0.074675 | 0.485597 | 0.778324 | 0.0 |
| ols_hc3 | C(moderator)[T.60+] | 1.368998 | 0.151088 | 1.072866 | 1.665129 | 0.0 |
| ols_hc3 | predictor | -0.513005 | 0.043332 | -0.597936 | -0.428074 | 0.0 |
| ols_hc3 | predictor:C(moderator)[T.30-44] | 0.063563 | 0.081193 | -0.095576 | 0.222702 | 0.433722 |
| ols_hc3 | predictor:C(moderator)[T.45-59] | 0.047783 | 0.143077 | -0.232648 | 0.328214 | 0.738409 |
| ols_hc3 | predictor:C(moderator)[T.60+] | 0.051695 | 0.300886 | -0.53804 | 0.641431 | 0.863589 |
| ols_hc3 | gendermale | 0.903909 | 0.033323 | 0.838595 | 0.969222 | 0.0 |
| ols_hc3 | classchild | 0.129691 | 0.012854 | 0.104496 | 0.154885 | 0.0 |
| ordinal_logit | C(moderator)[T.30-44] | 0.341826 | 0.036721 | 0.269853 | 0.413799 | 0.0 |
| ordinal_logit | C(moderator)[T.45-59] | 0.574755 | 0.063492 | 0.450311 | 0.699199 | 0.0 |
| ordinal_logit | C(moderator)[T.60+] | 1.19951 | 0.129057 | 0.946558 | 1.452462 | 0.0 |
| ordinal_logit | predictor | -0.567041 | 0.048312 | -0.661733 | -0.47235 | 0.0 |
| ordinal_logit | predictor:C(moderator)[T.30-44] | 0.150687 | 0.081281 | -0.008624 | 0.309998 | 0.063753 |
| ordinal_logit | predictor:C(moderator)[T.45-59] | 0.136237 | 0.131147 | -0.120811 | 0.393285 | 0.298893 |
| ordinal_logit | predictor:C(moderator)[T.60+] | 0.239527 | 0.262476 | -0.274927 | 0.75398 | 0.361471 |
| ordinal_logit | gendermale | 0.862095 | 0.0321 | 0.799179 | 0.925011 | 0.0 |
| ordinal_logit | classchild | 0.127659 | 0.012023 | 0.104093 | 0.151224 | 0.0 |

### Subgroup Means (CSA level × Moderator level)
| csa_level | moderator_level | estimate | se | n_unweighted |
| --- | --- | --- | --- | --- |
| 0 | 18-29 | -0.916694 | 0.02512 | 6194 |
| 0 | 30-44 | -0.390369 | 0.033675 | 3904 |
| 0 | 45-59 | -0.057546 | 0.070203 | 921 |
| 0 | 60+ | 0.641414 | 0.144241 | 198 |
| 1 | 18-29 | -1.763784 | 0.035541 | 1977 |
| 1 | 30-44 | -1.197383 | 0.062023 | 917 |
| 1 | 45-59 | -0.840741 | 0.119786 | 270 |
| 1 | 60+ | -0.107143 | 0.261959 | 56 |

## Interaction: `CSA_score_indicator:classchild_collapsed`

- Moderator label: **Childhood Class (Collapsed)**
- Sample (complete cases): 14437
- Outcome levels analysed: -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0

### Coefficients
| model | term | estimate | se | ci_low | ci_high | p_value |
| --- | --- | --- | --- | --- | --- | --- |
| ols_hc3 | Intercept | -2.293582 | 0.065097 | -2.421171 | -2.165993 | 0.0 |
| ols_hc3 | C(moderator)[T.Middle (2-3)] | 0.081208 | 0.051533 | -0.019796 | 0.182212 | 0.115081 |
| ols_hc3 | C(moderator)[T.Upper (4-6)] | 0.525736 | 0.058654 | 0.410774 | 0.640697 | 0.0 |
| ols_hc3 | predictor | -0.432257 | 0.068215 | -0.565959 | -0.298555 | 0.0 |
| ols_hc3 | predictor:C(moderator)[T.Middle (2-3)] | -0.075279 | 0.08323 | -0.23841 | 0.087852 | 0.365763 |
| ols_hc3 | predictor:C(moderator)[T.Upper (4-6)] | -0.220759 | 0.108039 | -0.432516 | -0.009003 | 0.041038 |
| ols_hc3 | selfage | 0.029439 | 0.001665 | 0.026175 | 0.032703 | 0.0 |
| ols_hc3 | gendermale | 0.885309 | 0.033296 | 0.820049 | 0.95057 | 0.0 |
| ordinal_logit | C(moderator)[T.Middle (2-3)] | 0.057159 | 0.048033 | -0.036986 | 0.151305 | 0.234049 |
| ordinal_logit | C(moderator)[T.Upper (4-6)] | 0.464027 | 0.05339 | 0.359383 | 0.56867 | 0.0 |
| ordinal_logit | predictor | -0.51432 | 0.07114 | -0.653754 | -0.374886 | 0.0 |
| ordinal_logit | predictor:C(moderator)[T.Middle (2-3)] | 0.013222 | 0.086759 | -0.156825 | 0.18327 | 0.878868 |
| ordinal_logit | predictor:C(moderator)[T.Upper (4-6)] | -0.10659 | 0.109248 | -0.320717 | 0.107536 | 0.329228 |
| ordinal_logit | selfage | 0.02749 | 0.001503 | 0.024544 | 0.030435 | 0.0 |
| ordinal_logit | gendermale | 0.848553 | 0.032127 | 0.785584 | 0.911522 | 0.0 |

### Subgroup Means (CSA level × Moderator level)
| csa_level | moderator_level | estimate | se | n_unweighted |
| --- | --- | --- | --- | --- |
| 0 | Lower (0-1) | -0.874856 | 0.04779 | 1742 |
| 0 | Middle (2-3) | -0.734441 | 0.025436 | 6379 |
| 0 | Upper (4-6) | -0.296835 | 0.038306 | 3096 |
| 1 | Lower (0-1) | -1.577348 | 0.053217 | 1086 |
| 1 | Middle (2-3) | -1.52354 | 0.042937 | 1593 |
| 1 | Upper (4-6) | -1.253235 | 0.078806 | 541 |

## Reproducibility
- Command: `python analysis/code/anxiety_interactions.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --interactions CSA_score_indicator:cis_identity CSA_score_indicator:age_cohort CSA_score_indicator:classchild_collapsed --out-table tables/diagnostics/anxiety_interactions.csv --out-md qc/anxiety_subgroup_extensions.md --seed 20251016`