# Data Quality Checks

Generated: 2025-10-16T13:08:09Z
Seed: 20251016
Regenerate: `python analysis/code/validate_survey_design.py`

## Survey Design Metadata Audit

- Dataset file: `childhoodbalancedpublic_original.csv`
- Rows (unweighted): 14443
- Columns: 718
- Weight variable specified in design: None
- Strata variable specified in design: None
- Cluster variable specified in design: None

## Weight / Strata / Cluster Validation

| Component | Expected | Present in data | Status | Notes |
| --- | --- | --- | --- | --- |
| Weights | None | Your weight is closest to: (n0iwzg0), weight | missing | No survey weight variable documented; defaulting to equal weights until clarified. |
| Strata | None | None detected | missing | No strata metadata provided. |
| Clusters | None | None detected | missing | No cluster metadata provided. |
| Replicate weights | None | None defined | n/a | Replicate weights not specified. |

### Candidate Columns Containing 'weight'

| Column | Dtype | Non-null n | Unique non-null | Sample values | Likely survey weight? |
| --- | --- | --- | --- | --- | --- |
| weight | float64 | 14443 | 14 | 170.0, 310.0, 130.0, 110.0, 150.0 | No |

## Assessment

No survey-design variables (weights/strata/clusters) are available in the provided dataset. Proceeding analyses must assume equal-probability sampling (simple random sampling) until official design information is supplied. Columns containing 'weight' were inspected; all appear to capture respondent body weight categories and are unsuitable as survey weights. Columns reviewed: `Your weight is closest to: (n0iwzg0)`, `weight`.

## Follow-up Actions

- [ ] Request official survey weight documentation from data provider.
- [ ] Document SRS assumption in PAP and subsequent analyses until metadata is updated.
