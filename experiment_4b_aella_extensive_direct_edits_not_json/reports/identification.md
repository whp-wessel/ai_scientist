# Identification Memo — Childhood Resilience Study
Updated: 2025-11-09
Seed: 20251016

## Study Stance
- The current PAP phase remains **descriptive**: the regressions for childhood religiosity, parental guidance, and emotional abuse will be reported as associations rather than causal effects while the design remains anchored in SRS plus HC1 variance estimation (`analysis/results.csv`, `analysis/sensitivity_plan.md`).
- We continue to rely on the SRS assumption articulated in `docs/survey_design.yaml` and document the alternative specifications via pseudo weights, design-effect grids, and pseudo replicates; any future inclusion of survey weights or valid instruments must be re-registered before interpreting effects as causal.

## DAG Reference
- The conceptual graph in `figures/dag_design.png` (`python analysis/code/plot_dag.py --output-png figures/dag_design.png --output-json figures/dag_design.json`) encodes the following structure:
  - **Exposures:** Childhood religious adherence, parental guidance, and childhood abuse.
  - **Outcomes:** Adult depression (`wz901dj`), adult health (`okq5xh8`), adult self-love (`2l8994l`).
  - **Confounders:** Childhood SES, family structure, demographics; mediators include support networks, coping, and adult SES.
- The DAG JSON spec (`figures/dag_design.json`) documents the coordinates and edges for reproducibility and will be referenced in manuscripts (Methods + Identification sections).

## Identification Assumptions
1. **No unmeasured confounding beyond documented covariates.** Childhood SES, family structure, siblings, and demographic controls stand in for the plausible common causes of exposures and adulthood wellbeing; any drift from this assumption is interrogated in the sensitivity suite (negative control NC1, pseudo weights, design-effect grid, pseudo replicates).
2. **Measurement validity:** Every outcome/predictor referenced in the PAP (and recorded in `analysis/hypotheses.csv`) is documented in `qc/measures_validity.md` so we can justify the coding, reliability check, and DIF examination before relying on the resulting scores.
3. **Temporal ordering:** Childhood exposures (religiosity, parental guidance, abuse) precede the mediators and adult outcomes by design, consistent with the survey’s recall structure, and are visualized in `figures/dag_design.png`.
4. **Disclosure guardrails:** All reporting tables (e.g., `tables/results_summary.csv`) and structural figures undergo the `qc/disclosure_check_loop_059.md` scan (threshold n ≥ 10) so public artifacts never expose small cells.

## Next Actions
- Keep `reports/identification.md` synchronized with DAG revisions and PAP updates.
- Document any new causal assumptions (e.g., instruments, natural experiments) before attempting causal language.
- Reference this memo in `papers/main/MANIFEST.md`, `papers/main/imrad_outline.md`, and `analysis/pre_analysis_plan.md` whenever exposures or robustness checks change.
