# IMRaD Outline — Loop 059

## Introduction
- I1: Describe the Childhood Resilience dataset, survey instrumentation, and the SRS assumption documented in `docs/survey_design.yaml`, linking to the measurement dossier (`qc/measures_validity.md`). [CLAIM:C1]
- I2: Summarize the theoretical mechanisms linking childhood religiosity, parental guidance, and emotional abuse to adult wellbeing, noting recent longitudinal evidence (e.g., Dore & Haardörfer 2025; `https://doi.org/10.1332/17579597y2024d000000035`) that motivates H2 and C2. [CLAIM:C2]
- I3: Note that the study remains descriptive but emphasizes deterministic modeling commands (PAP `pap-v1`, `analysis/pre_analysis_plan.md`) and measurement checks in `qc/measures_validity.md`. [CLAIM:C3]

## Methods
- M1: Document data sources (`data/raw/childhoodbalancedpublic_original.csv`, `docs/codebook.json`) plus the SRS/HC1 default and the deterministic seed in `config/agent_config.yaml`.
- M2: Outline the modeling pipeline (ordered logits for H1/H2, linear regression for H3, BH correction, NC1 falsification) and mention `analysis/results.csv`, `artifacts/bh_summary.json`, and `analysis/code/build_results_summary.py` as the regenerable command.
- M3: Reference the pre-specified sensitivity suite (pseudo weights, design-effect grid, pseudo replicates from `analysis/sensitivity_manifest.md`) and the disclosure scan (`qc/disclosure_check_loop_059.md`).

## Results
- R1: Depression (H1) ordered logit effect `−0.120` with 95% CI [−0.187, −0.055] and `q ≈ 0.0007` referencing `tables/results_summary.*` and `[CLAIM:C1]`.
- R2: Health (H2) guidance contrast `+0.0998` for “very good/excellent” health (95% CI [0.0889, 0.1109], `q = 0`) referencing `analysis/results.csv` and `[CLAIM:C2]`.
- R3: Self-love (H3) mean difference `−0.6544` (95% CI [−0.7192, −0.5895], `q = 0`) referencing `tables/results_summary.*` and `[CLAIM:C3]`.
- R4: Negative control NC1 (sibling count) returns `+0.2388` with a 95% CI that excludes zero, confirming the falsification expectation documented in `analysis/results.csv`.

## Discussion
- D1: Situate the consistent wellbeing signals relative to the literature (especially the new DOI-supported evidence in `lit/evidence_map.csv` and `lit/bibliography.*` for C2) and note the descriptive interpretation.
- D2: Highlight limitations (lack of design weights, single-item measures, potential recall bias) and the measurement dossier for each variable (`qc/measures_validity.md`).
- D3: Emphasize robustness: pseudo-weight and design-effect grids plus jackknife replicates keep effects in the same sign and the disclosure audit keeps `tables/results_summary.csv` + DAG above the n ≥ 10 threshold.
