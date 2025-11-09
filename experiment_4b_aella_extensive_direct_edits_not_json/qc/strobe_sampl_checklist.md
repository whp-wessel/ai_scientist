# STROBE + SAMPL Checklist — Loop 059

| item | status | description | artifact |
| --- | --- | --- | --- |
| Title / abstract | PASS | The manuscript abstract highlights the main estimates, BH q-values, and sensitivity suite while referencing the deterministic seed and confirmatory artifacts. | `papers/main/manuscript.md` / `papers/main/manuscript.tex` |
| Study design / sampling | PASS | The Methods section documents the data source, SRS assumption (`docs/survey_design.yaml`), and measurement dossier, satisfying SAMPL/STROBE design reporting. | `papers/main/manuscript.md` / `analysis/pre_analysis_plan.md` |
| Measures / measurement validity | PASS | Each PAP outcome/predictor is listed with wording, coding, reliability, and DIF checks (`qc/measures_validity.md`). | `qc/measures_validity.md` / `analysis/code/measure_validity_checks.py` |
| Results / effect estimates | PASS | H1–H3 effect sizes, CIs, q-values, and the NC1 falsification appear in `analysis/results.csv` and `tables/results_summary.csv/.md`, covering effect size reporting. | `tables/results_summary.csv` / `analysis/results.csv` |
| Uncertainty / sensitivity | PASS | Pseudo-weight, design-effect, and pseudo-replicate scripts document how DEFF and jackknife draws shift SEs while keeping effects in place (`analysis/sensitivity_plan.md`). | `analysis/sensitivity_plan.md` / `outputs/sensitivity_*` |
| Disclosure / privacy | PASS | The disclosure scan (`qc/disclosure_check_loop_059.md`) verifies n ≥ 10 in all released tables/figures and documents the command for regeneration. | `qc/disclosure_check_loop_059.md` |
| Literature mapping | PASS | Literature queries (Semantic Scholar 403 attempt + CrossRef fallback) and DOI-backed references feed `lit/evidence_map.csv` and the `.bib`/`.json` registries for each `[CLAIM:<ID>]`. | `lit/evidence_map.csv` / `lit/bibliography.*` / `lit/queries/loop_059/` |
