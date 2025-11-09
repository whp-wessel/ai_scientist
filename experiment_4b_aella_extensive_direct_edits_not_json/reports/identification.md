# Identification Memo — Childhood Resilience Study
Updated: 2025-11-09  
Seed: 20251016

## Study Stance
    - The current PAP phase remains **descriptive**: the regressions for childhood religiosity, parental guidance, and emotional abuse are associations under the SRS + HC1 assumption, and the sensitivity plan (`analysis/sensitivity_plan.md`) documents alternative specifications (pseudo weights, design-effect grid, pseudo replicates) before any causal claims are attempted. `analysis/results.csv`, `analysis/sensitivity_plan.md`, and `analysis/pre_analysis_plan.md` anchor the descriptive reporting, and we keep Claim C1 DOI-backed through Poole et al. (2017, Child Abuse & Neglect) recorded in `lit/evidence_map.csv` plus the fallback log `lit/queries/loop_069/crossref_query_002.json` while Semantic Scholar refuses the same query.
- We continue to rely on the SRS assumption articulated in `docs/survey_design.yaml`; any future introduction of design weights or instruments must be re-registered. Measurement validity for each outcome/predictor is documented in `qc/measures_validity.md` plus the JSON summary (`artifacts/measurement_validity_loop061.json`), ensuring DIF/reliability diagnostics precede effect interpretation.
    - The disclosure scan (`qc/disclosure_check_loop_069.md`) shows that `tables/results_summary.csv`, `tables/results_summary.md`, and `figures/dag_design.png` remain above $n \geq 10$ before referencing them in public reports, so the data release plan meets the STROBE/SAMPL small-cell thresholds.
- The pseudo-weight/design-effect/pseudo-replicate experiments expand the uncertainty envelope while confirming the HC1-based estimates, supporting the descriptive interpretation in the absence of valid weights.

## DAG Reference
- The conceptual graph in `figures/dag_design.png` (`python analysis/code/plot_dag.py --output-png figures/dag_design.png --output-json figures/dag_design.json`) encodes the following structure:
  - **Exposures:** Childhood religious adherence, parental guidance, and emotional abuse.
  - **Outcomes:** Adult depression (`wz901dj`), adult health (`okq5xh8`), and adult self-love (`2l8994l`).
  - **Confounders:** Childhood SES, family structure, demographics, and siblings; mediators include support networks, coping, and adult SES.
- The DAG JSON spec (`figures/dag_design.json`) documents the coordinates and edges for reproducibility and will be cited in Methods, Identification, and DAG captions.

## Identification Assumptions
1. **No unmeasured confounding beyond documented covariates.** Controls (SES, demographics, siblings, class variables) stand in for the most plausible common causes; the scenario suite (negative control, pseudo weights, design-effect grid, pseudo replicates) helps gauge how deviations would affect the estimates.
2. **Measurement validity.** Every PAP outcome/predictor is documented in `qc/measures_validity.md` and `artifacts/measurement_validity_loop061.json` with wording, coding, reliability (α), and DIF results before use.
3. **Temporal ordering.** Childhood exposures precede the adult outcomes by design, consistent with the survey’s recall window and the DAG structure.
4. **Disclosure guardrails.** Tables (`tables/results_summary.*`) and figures (`figures/dag_design.png`) pass the `qc/disclosure_check_loop_061.md` scan (n ≥ 10) so no small-cell suppression is required for these release-ready artifacts.

## Next Actions
- Keep `reports/identification.md` synchronized with DAG or PAP adjustments and document any new causal assumptions (e.g., instruments, natural experiments) before expanding the causal language.
    - Continue logging blocked Semantic Scholar queries plus CrossRef fallbacks (e.g., `lit/queries/loop_069/crossref_query_002.json`) until the S2 key returns or the waiver is formalized.
- After the writing-phase QC pass (STROBE/SAMPL checklist update, LaTeX build log, new disclosure scans), revisit this memo to confirm the assumptions still hold and to reference the updated figures/tables.
