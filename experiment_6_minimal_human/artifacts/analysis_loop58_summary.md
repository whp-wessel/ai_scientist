# Loop 58 Analysis Results

## Sample information

- Rows with positive weight: 14,443
- Religionchildhood nonmissing (not used): 0
- H1 analytic sample comparison saved in artifacts/h1_sample_comparison_loop58.csv
- VIF results saved in artifacts/h1_vif_loop58.csv
- Regression record snapshot saved in artifacts/regression_records_loop58.csv
- Environment snapshot saved in artifacts/pip_freeze_loop58.txt

## H1 results

Weighted guidance index effects:
- Anxiety (npvfh98): β=-0.135 (95% CI [-0.152, -0.118]), p=0.000 (BH-FDR=0.000) with N=14430.
- Depression (wz901dj): β=0.193 (95% CI [0.176, 0.210]), p=0.000 (BH-FDR=0.000) with N=14431.
- Functional impairment (kd4qc3z): β=-0.163 (95% CI [-0.180, -0.146]), p=0.000 (BH-FDR=0.000) with N=14430.

## H2 results

- Relationship satisfaction (hp9qz6f): β=0.008 (95% CI [-0.010, 0.025]), p=0.379 (BH-FDR=0.379) with N=14429.
- Self-love (2l8994l): β=0.037 (95% CI [0.019, 0.054]), p=0.000 (BH-FDR=0.000) with N=14428.
- Unhappiness (ix5iyv3): β=-0.034 (95% CI [-0.051, -0.017]), p=0.000 (BH-FDR=0.000) with N=14430.
- Relationship satisfaction (hp9qz6f): β=-0.013 (95% CI [-0.030, 0.004]), p=0.134 (BH-FDR=0.201) with N=14430.
- Self-love (2l8994l): β=0.017 (95% CI [0.000, 0.034]), p=0.044 (BH-FDR=0.132) with N=14429.
- Unhappiness (ix5iyv3): β=0.000 (95% CI [-0.016, 0.016]), p=0.967 (BH-FDR=0.967) with N=14431.

## H3 results

Weighted interaction effects (support × adversity):
- Anxiety (npvfh98): β=0.070 (95% CI [0.055, 0.085]), p=0.000 (BH-FDR=0.000) with N=14031.
- Depression (wz901dj): β=-0.049 (95% CI [-0.064, -0.034]), p=0.000 (BH-FDR=0.000) with N=14032.
- Unhappiness (ix5iyv3): β=0.046 (95% CI [0.031, 0.061]), p=0.000 (BH-FDR=0.000) with N=14032.
- Self-love (2l8994l): β=-0.041 (95% CI [-0.058, -0.025]), p=0.000 (BH-FDR=0.000) with N=14030.

Simple slopes at support = -1/0/1 saved to artifacts/h3_simple_slopes_loop58.csv

Predicted outcomes at low/average/high support (mean adversity) saved to artifacts/h3_predicted_supports_loop58.csv

## Limitations

- The column Religionchildhood is entirely missing, so that planned control could not be included.
- Simple slopes and predictions assume covariates remain at their analytic means.
- The `religion` control was dropped from H2 regressions because it mirrors the active religiosity measures and inflated coefficients.