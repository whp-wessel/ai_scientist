# Loop 80 Analysis Results

## Sample information

- Rows with positive weight: 14,443
- Religionchildhood nonmissing (not used): 0
- H1 analytic sample comparison saved in artifacts/h1_sample_comparison_loop80.csv
- VIF results saved in artifacts/h1_vif_loop80.csv
- Regression record snapshot saved in artifacts/regression_records_loop80.csv
- Environment snapshot saved in artifacts/pip_freeze_loop80.txt

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

Simple slopes at support = -1/0/1 saved to artifacts/h3_simple_slopes_loop80.csv

Predicted outcomes at low/average/high support (mean adversity) saved to artifacts/h3_predicted_supports_loop80.csv

## Limitations

- The column Religionchildhood is entirely missing, so that planned control could not be included.
- Simple slopes and predictions assume covariates remain at their analytic means.
- The `religion` control was dropped from H2 regressions because it mirrors the active religiosity measures and inflated coefficients.

## Sensitivity checks

- Trimmed-weight models are archived in artifacts/sensitivity_trimmed_weights_loop80.csv and cohesion/adversity checks in artifacts/sensitivity_cohesion_loop80.csv and sensitivity_adversity_loop80.csv.

### Trimmed weights

- Guidance index → Anxiety (npvfh98): β=-0.135 (95% CI [-0.152, -0.118]), p=1.94e-54 with N=14430.
- Guidance index → Depression (wz901dj): β=0.193 (95% CI [0.176, 0.210]), p=2.67e-115 with N=14431.
- Guidance index → Functional impairment (kd4qc3z): β=-0.163 (95% CI [-0.180, -0.146]), p=3.81e-79 with N=14430.
- H2 trimmed coefficients stay within ±0.02 of the base estimates (see table).

### Trimmed H3 interactions

- Adversity × support → Anxiety (npvfh98): β=0.070 (95% CI [0.055, 0.085]), p=1.48e-19 with N=14031.
- Adversity × support → Depression (wz901dj): β=-0.049 (95% CI [-0.064, -0.033]), p=4.38e-10 with N=14032.
- Adversity × support → Unhappiness (ix5iyv3): β=0.046 (95% CI [0.031, 0.061]), p=3.42e-09 with N=14032.
- Adversity × support → Self-love (2l8994l): β=-0.041 (95% CI [-0.058, -0.024]), p=1.61e-06 with N=14030.

### Alternative cohesion composite (Guidance + playful cohesion index)

- Guidance + playful cohesion index → Anxiety (npvfh98): β=-0.126 (95% CI [-0.142, -0.109]), p=1.87e-50 with N=14418.
- Guidance + playful cohesion index → Depression (wz901dj): β=0.183 (95% CI [0.167, 0.199]), p=1.57e-109 with N=14419.
- Guidance + playful cohesion index → Functional impairment (kd4qc3z): β=-0.160 (95% CI [-0.176, -0.144]), p=2.8e-83 with N=14418.

### Alternative adversity composites

- Parental verbal/emotional abuse × support → Anxiety (npvfh98): β=0.058 (95% CI [0.042, 0.074]), p=1.02e-12 with N=14040.
- Parental verbal/emotional abuse × support → Depression (wz901dj): β=-0.037 (95% CI [-0.052, -0.021]), p=4.27e-06 with N=14041.
- Parental verbal/emotional abuse × support → Unhappiness (ix5iyv3): β=0.049 (95% CI [0.034, 0.065]), p=4.73e-10 with N=14041.
- Parental verbal/emotional abuse × support → Self-love (2l8994l): β=-0.039 (95% CI [-0.057, -0.022]), p=9.51e-06 with N=14039.
- Feelings of being at war with yourself × support → Anxiety (npvfh98): β=0.078 (95% CI [0.063, 0.093]), p=5.17e-25 with N=14048.
- Feelings of being at war with yourself × support → Depression (wz901dj): β=-0.062 (95% CI [-0.076, -0.047]), p=3.51e-17 with N=14049.
- Feelings of being at war with yourself × support → Unhappiness (ix5iyv3): β=0.048 (95% CI [0.033, 0.063]), p=2.38e-10 with N=14049.
- Feelings of being at war with yourself × support → Self-love (2l8994l): β=-0.045 (95% CI [-0.062, -0.028]), p=1.2e-07 with N=14047.

### Guidance–depression pattern

- The correlation between guidance-index and raw depression scores remains 0.270; the binned averages are saved to artifacts/guidance_depression_sensitivity_loop80.csv to document the U-shaped trend.