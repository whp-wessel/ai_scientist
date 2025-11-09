# IMRaD Outline — Loop 074

## Introduction
- I1: Describe the Childhood Resilience dataset, codebook, and SRS assumption (`data/raw/childhoodbalancedpublic_original.csv`, `docs/codebook.json`, `docs/survey_design.yaml`), linking to the measurement dossier (`qc/measures_validity.md`, `artifacts/measurement_validity_loop061.json`), the descriptive framing in `reports/identification.md`, and the latest resilience evidence (Morris & Hays-Grudo 2023, World Psychiatry) recorded in `lit/evidence_map.csv` (`lit/queries/loop_073/crossref_query_001.json`). [CLAIM:C1]
- I2: Summarize theoretical mechanisms linking childhood religiosity, parental guidance, and emotional abuse to adult wellbeing, referencing DOI-backed literature in `lit/evidence_map.csv` that motivates H1–H3. [CLAIM:C2]
- I3: Emphasize deterministic reproducibility via `analysis/pre_analysis_plan.md`, the frozen PAP tag `pap-v1`, and the sensitivity plan (`analysis/sensitivity_plan.md`). [CLAIM:C3]

## Methods
- M1: Document data sources (`data/raw/childhoodbalancedpublic_original.csv`, `docs/codebook.json`) plus SRS/HC1 defaults, measurement reliability (`qc/measures_validity.md`), and the global seed (20251016) in `config/agent_config.yaml`.
- M2: Outline the modeling pipeline (ordered logits for H1/H2, linear regression for H3, BH correction for the wellbeing family, NC1 falsification) and mention `analysis/results.csv`, `artifacts/bh_summary.json`, and `analysis/code/build_results_summary.py` as the regenerable commands.
- M3: Reference the pre-specified sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) in `analysis/sensitivity_manifest.md`, note the disclosure scan (`qc/disclosure_check_loop_061.md`), and cite the DAG/disclosure guard in `reports/identification.md`.

## Results
- R1: Depression (H1) ordered logit effect `−0.120` (CI [−0.187, −0.055], `q ≈ 0.0007`) references `analysis/results.csv` and `[CLAIM:C1]`.
- R2: Self-rated health (H2) guidance contrast `+0.0998` (CI [0.0889, 0.1109], `q = 0`) references `analysis/results.csv` and `[CLAIM:C2]`.
- R3: Self-love (H3) difference `−0.6544` (CI [−0.719, −0.590], `q = 0`) references `analysis/results.csv` and `[CLAIM:C3]`.
- R4: Negative control NC1 remains `+0.2388` (CI [0.2209, 0.2568]) and `targeted = N`, confirming no spurious signals.

## Discussion
- D1: Situate the consistent wellbeing family signals relative to the DOI-backed literature in `lit/evidence_map.csv` (including the World Psychiatry 2023 crossref fallback) and maintain the descriptive tone from `reports/identification.md`.
- D2: Highlight limitations (unweighted SRS assumption, single-item measures, recall bias) and reference the measurement dossier (`qc/measures_validity.md`) before attributing any directional claims.
- D3: Emphasize robustness: pseudo-weight/design-effect/pseudo-replicate scenarios preserve effect direction while the disclosure audit (`qc/disclosure_check_loop_069.md`) keeps `tables/results_summary.*` and `figures/dag_design.png` above the n ≥ 10 threshold.
