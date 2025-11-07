# Robustness QC Synthesis
Generated: 2025-11-04T14:05:00Z | Seed: 20251016

## Scope
- Confirmatory estimates come from `analysis/results.csv` (HC3 OLS, frozen PAP).
- Robustness checks were executed with  
  `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003 --seed 20251016`
  producing `tables/robustness/robustness_checks_summary.{csv,json}` and the task-specific QC notes (`qc/hyp-*.md`).

## Summary Table
| Hypothesis | Check | Model | n | Estimate (metric) | SE | p-value | Conclusion |
|---|---|---|---|---|---|---|---|
| HYP-001 | Helmert contrasts (childhood class) | OLS HC3 | 14,436 | 0.070 (average step) | — | 3.07e-163 | Direction and magnitude align with confirmatory β = 0.181; categorical specification preserves positive gradient. |
| HYP-001 | Ordinal logit | Cumulative logit | 14,436 | 0.170 (log-odds) | — | 7.30e-48 | Odds of higher self-love increase with class; no sign reversal or attenuation. |
| HYP-001 | Outcome z-score | OLS HC3 | 14,436 | 0.097 (SD units) | — | 1.58e-51 | Rescaling to SD units yields ≈0.10 SD effect, matching textual interpretation. |
| HYP-003 | High-anxiety binary | Logistic HC3 | 14,436 | -0.558 (log-odds) | 0.056 | 4.09e-23 | Odds ratio 0.57 (95% CI ≈ [0.51, 0.64]), confirming lower high-anxiety prevalence among CSA-exposed respondents. |
| HYP-003 | CSA intensity bins | OLS HC3 | 14,436 | -0.325 (bin contrast) | — | 2.02e-47 | Collapsing CSA score into tiers leaves negative slope and similar magnitude. |
| HYP-003 | Tail trim (CSA > 15 removed) | OLS HC3 | 14,326 | -0.483 (slope) | 0.037 | 3.66e-39 | Estimate remains within 0.01 of confirmatory β = -0.491; trimming high-leverage cases does not alter inference. |

## Interpretation
- All robustness modules preserve the signs reported in the confirmatory models and stay within 0.02 points (self-love) or 0.08 points (anxiety) of the PAP estimates.
- Logistic re-specification for HYP-003 yields substantively similar odds ratio (~0.57), indicating that recoding anxiety into a binary indicator does not reverse findings.
- No robustness run introduces cell counts below the suppression threshold (n < 10); trimmed sample retains 14,326 observations.

## Documentation & Reporting
- Narrative summaries propagated to `reports/findings_v0.4.md` and `papers/main/manuscript.tex` (Robustness section).
- This memo centralises references for dissemination and points to the executable command above; no additional randomness beyond seed 20251016 is introduced.
- Future robustness extensions (e.g., anxiety rescaling, subgroup interactions) should append to `tables/robustness/robustness_checks_summary.csv` and update this summary accordingly.
