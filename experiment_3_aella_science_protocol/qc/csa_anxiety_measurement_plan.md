# CSA–Anxiety Measurement Diagnostic Plan
Generated: 2025-11-04T13:15:00Z | Seed: 20251016

## Context
- Confirmatory results (HYP-003) show a −0.49 point association between CSA exposure and self-reported anxiety agreement on the −3 to +3 scale.
- Directional diagnostics (`qc/csa_anxiety_direction.md`) confirm CSA-exposed respondents report lower anxiety agreement. Cell counts exceed the suppression threshold (10).
- Item routing review (`qc/anxiety_item_routing.md`) indicates the anxiety prompt is single-item, negatively coded, and situated alongside other affect measures; no reverse phrasing flag appears in instrument metadata.

## Diagnostic Objectives
1. Evaluate whether the anxiety response scale behaves equivalently across CSA exposure and key demographic subgroups (gender, age cohort).
2. Assess convergent validity of the anxiety item with companion affect indicators (e.g., depression, stress, self-love).
3. Examine whether distributional, routing, or missingness patterns indicate measurement artifacts or differential reporting.
4. Document implications for interpretation and reporting in the main manuscript.

## Diagnostic Modules
| Module | Purpose | Primary Command(s) | Planned Outputs | Notes |
|---|---|---|---|---|
| M1: Polarity Verification | Re-run CSA vs anxiety mean comparison to confirm sign and magnitude, inspect category frequencies | `python analysis/code/diagnose_csa_anxiety_direction.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --outcome "I tend to suffer from anxiety (npvfh98)-neg" --indicator CSA_score_indicator --out-table tables/diagnostics/csa_anxiety_direction.csv --out-md qc/csa_anxiety_direction.md` | `tables/diagnostics/csa_anxiety_direction.csv`, `qc/csa_anxiety_direction.md` | Already executed; rerun only if upstream data change. |
| M2: Response Category Audit | Summarise anxiety item distribution overall and by CSA exposure; verify no sparse categories (n < 10) | `python analysis/code/diagnose_csa_anxiety_direction.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --outcome "I tend to suffer from anxiety (npvfh98)-neg" --indicator CSA_score_indicator --out-table tables/diagnostics/csa_anxiety_direction.csv --out-md qc/csa_anxiety_direction.md --include-category-counts` | `tables/diagnostics/csa_anxiety_direction_counts.csv`, `qc/csa_anxiety_direction.md` (appendix) | Extend script to emit category-level counts; ensure suppression rules. |
| M3: Convergent Validity | Correlate anxiety item with depression and self-love; estimate reliability via polychoric correlations | `python analysis/code/evaluate_anxiety_convergence.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/anxiety_convergence.csv --out-md qc/anxiety_convergence.md` | `tables/diagnostics/anxiety_convergence.csv`, `qc/anxiety_convergence.md` | New script required; apply Benjamini–Hochberg within correlation family. |
| M4: DIF / Subgroup Checks | Fit nested ordinal logistic models for anxiety item with CSA, gender, their interaction; profile subgroup means to prioritise additional interaction tests | `python analysis/code/test_anxiety_dif.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --outcome "I tend to suffer from anxiety (npvfh98)-neg" --csa CSA_score_indicator --group gender --group-value-column gendermale --out-table tables/diagnostics/anxiety_dif.csv --out-md qc/anxiety_dif.md`<br>`python analysis/code/anxiety_subgroup_summary.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --out-table tables/diagnostics/anxiety_subgroup_summary.csv --out-md qc/anxiety_subgroup_summary.md` | `tables/diagnostics/anxiety_dif.csv`, `qc/anxiety_dif.md`, `tables/diagnostics/anxiety_subgroup_summary.csv`, `qc/anxiety_subgroup_summary.md` | DIF run completed (CSA×gender not significant); subgroup summary confirms no small cells and highlights largest gaps. |
| M5: Sensitivity Recode | Recode anxiety item to 0–6 scale and binary high-anxiety indicator; re-run confirmatory model as robustness | `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --hypotheses HYP-003 --robustness-set anxiety_scale_recodes` | `tables/robustness/hyp-003_anxiety_recodes.csv`, `qc/hyp-003_anxiety_recodes.md` | Extend robustness script to include recode routine. |

## Task Breakdown
| Task ID | Priority | Description | Status | Linked Module(s) |
|---|---|---|---|---|
| T-019 | 2 | Draft measurement diagnostic plan for CSA–anxiety anomaly | Completed | All |
| T-020 | 3 | Identify subgroup heterogeneity tests for anxiety outcome | Completed | M4 |
| T-021 | 1 | Implement ordinal DIF analysis for anxiety item (CSA × gender) | Completed | M4 |
| T-022 | 2 | Assess convergent validity across anxiety, depression, self-love | Pending | M3 |

## Subgroup Heterogeneity Plan (Task T-020)
- **Gender (CSA×gender DIF)**: Ordinal logit interaction completed via `analysis/code/test_anxiety_dif.py`; retain as baseline diagnostic and report non-significant interaction (p=0.62) with supporting subgroup means.
- **Cisgender identity**: Plan HC3 OLS and ordinal logit models with CSA×cis interaction; prioritise due to largest mean gap (−1.38 vs −2.20). Ensure scripted implementation (`analysis/code/test_anxiety_interactions.py`, forthcoming) applies BH correction across exploratory interactions.
- **Age cohort**: Use 18–29, 30–44, 45–59, 60+ cohorts (minimum n=56 CSA-exposed) for CSA×age interaction; monitor leverage for 60+ group and consider collapsing if diagnostics flag instability.
- **Childhood class**: Collapse classchild to lower/middle/upper as summarised; estimate CSA×class interactions in OLS and, if non-linearities appear, extend to semiparametric robustness (e.g., spline on classchild).
- **Documentation**: Archive intermediary stats in `tables/diagnostics/anxiety_subgroup_summary.csv` and narrative in `qc/anxiety_subgroup_summary.md`; log all follow-up commands in `papers/main/MANIFEST.md`.

## Reporting Commitments
- Document all outputs in `qc/` and `tables/diagnostics/` with generation commands in `papers/main/MANIFEST.md`.
- Update `reports/findings_v0.3.md` and `papers/main/manuscript.tex` once convergence and DIF diagnostics are executed; include limitations if anomalies persist.
- Append decision log entries for each module executed, tagging the corresponding task IDs.

## Privacy & Suppression
- Maintain the small-cell threshold of 10 for all subgroup summaries; collapse categories when necessary.
- Mask or omit DIF results for strata with post-weighted counts below threshold.

## Next Steps
1. Execute Module M3 (Task T-022) to contextualise the anxiety item within the affect battery.
2. Translate cis/age/class interaction plans into executable scripts and QC templates.
3. Revisit robustness scripting to incorporate the sensitivity recodes outlined in Module M5.
