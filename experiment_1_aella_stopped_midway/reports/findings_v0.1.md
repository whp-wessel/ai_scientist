---
version: 0.1
timestamp_utc: 2025-10-16T13:18:00Z
status: exploratory
seed: 20251016
primary_outputs:
  - tables/exploratory_selflove_by_abuse.csv
  - tables/exploratory_networth_by_classchild.csv
  - tables/exploratory_missingness_key_vars.csv
regenerate: python analysis/code/eda_weighted_summaries.py
---

# Findings v0.1 (Exploratory)

## Overview

- Focus: descriptive summaries for wellbeing (`I love myself (2l8994l)`) and socioeconomic (`networth`) outcomes under an SRS assumption.
- Dataset: `childhoodbalancedpublic_original.csv` (n = 14,443); no design weights available.

## Methods

- Seed fixed to `20251016`; analyses conducted via `analysis/code/eda_weighted_summaries.py`.
- Negative numeric codes (< 0) treated as non-response prior to aggregation.
- `classchild` and `networth` recoded into grouped categories to avoid cells < 10.
- All statistics are unweighted (implicit equal weights) pending official survey design metadata.

## Results (Exploratory)

- **Self-love by childhood abuse frequency:** mean self-love ranges 1.32–1.48 with modest variation; respondents reporting more frequent emotional abuse show slightly higher self-love averages (difference ≈ 0.17 points). Counts remain well above the suppression threshold.
- **Net worth by childhood class:** Higher childhood class groups show larger shares in high net worth categories (up to 41% of the `5-6 upper` group versus 18% in the `0 = unsure/other` group).
- **Missingness:** Abuse and self-love items exhibit substantial non-response (48% and 28%, respectively), mostly due to negative-coded refusals/soft refusals.

## Limitations

- Descriptive only; no causal interpretation.
- Heavy item non-response may bias estimates; imputation plans needed before confirmatory analysis.
- Absence of survey weights may under/overstate variability; results conditional on SRS assumption.

## Robustness & Next Steps

1. Audit response-pattern correlates of missingness to inform imputation strategy.
2. Await or request official survey weight documentation (`T-003`).
3. Extend exploratory summaries to additional wellbeing and relational outcomes once coding validated.

## Ethics & Privacy

- Cells < 10 suppressed by design; grouping strategies ensure privacy standard (`k=10`).
- No raw PII exposed; data remain on secure local environment.

## Open Questions

- Why do self-love and abuse items have elevated negative codes? Are these design features (e.g., skip logic)?
- Does the slight elevation in self-love among higher abuse frequency reflect resilience or measurement artifact? Requires theory review and further testing.

_Changelog_: Initial exploratory report established from SRS-weighted summaries.
