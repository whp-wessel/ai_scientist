# STROBE + SAMPL Checklist — Loop 074

| item | status | description | artifact |
| --- | --- | --- | --- |
| Title / abstract | PASS | The abstract highlights the main estimates, BH q-values, and sensitivity suite while referencing `analysis/results.csv`, the deterministic seed, and the refreshed disclosure scan. | `papers/main/manuscript.md` / `papers/main/manuscript.tex` |
| Study design / sampling | PASS | The Methods section documents the data source, SRS assumption (`docs/survey_design.yaml`), and measurement dossier (`qc/measures_validity.md`, `artifacts/measurement_validity_loop061.json`). | `papers/main/manuscript.md` / `analysis/pre_analysis_plan.md` |
| Measures / measurement validity | PASS | Each PAP outcome/predictor is listed with wording, coding, reliability, and DIF checks (`qc/measures_validity.md` / `artifacts/measurement_validity_loop061.json`). | `qc/measures_validity.md` / `analysis/code/measure_validity_checks.py` |
| Results / effect estimates | PASS | H1–H3 effect sizes, CIs, q-values, and the NC1 falsification appear in `analysis/results.csv` and `tables/results_summary.csv/.md`, covering effect reporting requirements. | `tables/results_summary.csv` / `analysis/results.csv` |
| Uncertainty / sensitivity | PASS | Pseudo-weight, design-effect, and pseudo-replicate scripts document how DEFF and jackknife draws shift SEs while keeping effects on the same side of zero (`analysis/sensitivity_plan.md`). | `analysis/sensitivity_plan.md` / `outputs/sensitivity_*` |
| Disclosure / privacy | PASS | `qc/disclosure_check_loop_074.md` audits every release-ready table/figure (e.g., `tables/results_summary.*`, `figures/dag_design.png`) to confirm n ≥ 10 before publication. | `qc/disclosure_check_loop_074.md` |
| Literature mapping | PASS | Literature queries (Semantic Scholar 403 + CrossRef fallback) and DOI-backed references feed `lit/evidence_map.csv` and `lit/bibliography.*` for each `[CLAIM:<ID>]`; loop 073 captures World Psychiatry 2023 (Morris & Hays-Grudo) via `lit/queries/loop_073/crossref_query_001.json`. | `lit/evidence_map.csv` / `lit/bibliography.*` / `lit/queries/loop_073/` |
