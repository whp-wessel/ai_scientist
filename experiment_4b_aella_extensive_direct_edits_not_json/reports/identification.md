# Identification Memo — Childhood Resilience Study
Updated: 2025-11-08
Seed: 20251016

## Study Stance
- The current PAP phase is **descriptive**: associations between childhood contexts (religious adherence, parental guidance, abuse) and adult wellbeing will be reported without causal claims until a survey-weighted design with valid instruments is established.
- All estimands rely on the SRS assumption documented in `docs/survey_design.yaml`; if design weights become available, the PAP will be revised before confirmatory analysis.

## DAG Reference
- The conceptual graph in `figures/dag_design.png` (`python analysis/code/plot_dag.py --output-png figures/dag_design.png --output-json figures/dag_design.json`) encodes the following structure:
  - **Exposures:** Childhood religious adherence, parental guidance, and childhood abuse.
  - **Outcomes:** Adult depression (`wz901dj`), adult health (`okq5xh8`), adult self-love (`2l8994l`).
  - **Confounders:** Childhood SES, family structure, demographics; mediators include support networks, coping, and adult SES.
- The DAG JSON spec (`figures/dag_design.json`) documents the coordinates and edges for reproducibility and will be referenced in manuscripts (Methods + Identification sections).

## Identification Assumptions
1. **No unmeasured confounding beyond documented covariates.** We assume childhood SES, family structure, and core demographics capture the common causes of both exposures and outcomes. Deviations will be handled via sensitivity checks (e.g., negative controls in the sensitivity phase).
2. **Measurement validity:** Constructs used as exposures/outcomes must have reliability evidence in `qc/measures_validity.md`. Any future re-scaling or DIF corrections will be logged there.
3. **Temporal ordering:** Childhood exposures precede adolescent mediators which precede adult outcomes, consistent with survey wording.
4. **No disclosure risk:** DAG + memo contain no cell-level data; public tables will be filtered through `qc/disclosure_check_loop_{loop}` before release.

## Next Actions
- Keep `reports/identification.md` synchronized with DAG revisions and PAP updates.
- Document any new causal assumptions (e.g., instruments, natural experiments) before attempting causal language.
- Reference this memo in `papers/main/MANIFEST.md`, `papers/main/imrad_outline.md`, and `analysis/pre_analysis_plan.md` whenever exposures or robustness checks change.
