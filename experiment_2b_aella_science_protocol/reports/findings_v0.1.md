# Findings Report v0.1
Version: 0.1.0 (frozen PAP reference)  
Updated: 2025-11-04T09:25:35Z | Seed: 20251016

> **Parity requirement:** Keep this Markdown report in sync with `papers/main/manuscript.tex`. Any change here must be mirrored in LaTeX during the same commit.

## Abstract
Confirmatory analyses (n = 14,436) indicate that each one-step increase in childhood class corresponds to a 0.18-point rise in adult self-love on the 7-point scale (95% CI [0.16, 0.20], q ≈ 3.9×10⁻⁵¹). Contrary to the preregistered direction, respondents reporting any childhood sexual abuse agreement average 0.49 points lower on the anxiety agreement scale (95% CI [−0.56, −0.42], q ≈ 6.9×10⁻⁴¹). All estimates rely on HC3 OLS under a simple random sampling assumption and are reproducible with seed 20251016.

## Methods
- Data source: `data/raw/childhoodbalancedpublic_original.csv` (SHA-256 logged in `artifacts/checksums.json`).
- Derived dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv` regenerated via  
  `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.
- Confirmatory scope: HYP-001, HYP-003 (see `analysis/pre_analysis_plan.md`, frozen 2025-11-04T07:58:50Z).
- Statistical plan: HC3 OLS under SRS assumption; Benjamini–Hochberg at q=0.05 within confirmatory family; robustness checks pre-specified in PAP.

## Results
- **HYP-001 (Wellbeing family)**: Childhood class exhibits a positive association with adult self-love (β = 0.181, SE = 0.012; 95% CI [0.158, 0.205]; q = 3.9×10⁻⁵¹). This implies roughly a fifth of a scale point increase in self-love for each class step when covarying age, gender, and cis identity.
- **HYP-003 (MentalHealth family)**: Any CSA exposure is linked to −0.491 points on the anxiety agreement scale (SE = 0.037; 95% CI [−0.562, −0.419]; q = 6.9×10⁻⁴¹). The negative sign reflects lower agreement with the statement “I tend to suffer from anxiety,” running counter to the preregistered positive direction.

Benjamini–Hochberg adjustments (q = 0.05 family-wise) do not alter inference because the extremely small p-values remain far below the threshold.

## Robustness and Sensitivity
- **HYP-001**: Treating childhood class as categorical with Helmert contrasts yields an average class effect of 0.07 (F = 89.7). An ordinal logit specification reports a log-odds coefficient of 0.17 (p ≈ 7.3×10⁻⁴⁸), and z-scoring the outcome produces β = 0.097 (p ≈ 1.6×10⁻⁵¹). All three checks retain the positive direction and similar magnitudes.
- **HYP-003**: A logistic model contrasting high anxiety agreement (≥ 1) produces an odds ratio of 0.57 (95% CI ≈ [0.51, 0.64]). Binning CSA intensity into 0/1–3/4+ bins and trimming the CSA>15 tail both keep negative associations (β_bins = −0.33; trimmed β = −0.48). Sensitivity diagnostics therefore corroborate the observed direction despite diverging from the preregistered expectation.

## Limitations
1. Survey provider has not confirmed the absence of design weights; we proceed under a simple random sampling assumption and flag potential bias from undisclosed complex design features.
2. Both outcomes are ordinal but modeled as interval variables; effect magnitudes should be interpreted as approximate.
3. CSA exposure is derived from a composite score and its association with lower anxiety agreement suggests possible measurement or reporting artifacts that merit qualitative follow-up.

## Ethics, Privacy, and Disclosure
- Small-cell suppression threshold: n < 10 (per `config/agent_config.yaml`); adhere to rounding/binning in all outputs.
- Data contain sensitive childhood trauma indicators; confirm IRB posture before dissemination.

## Open Questions
1. Should HYP-004 (social support) advance to confirmatory status once routing documentation is secured?
2. Does the negative CSA–anxiety association stem from coding (neg vs. pos framing) or from differential nonresponse requiring additional weighting or qualitative context?

## Reproducibility Notes
- Environment snapshot: `artifacts/session_info.txt`.
- Seed: `artifacts/seed.txt` (20251016).
- Regeneration commands:  
  - Confirmatory estimates: `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`  
  - FDR adjustment: `python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --audit-table tables/fdr_adjustment_confirmatory.csv`  
  - Robustness checks: `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`
- Manual edits remain synchronized with `papers/main/manuscript.tex`; document any automated regeneration (e.g., via pandoc) in `papers/main/MANIFEST.md`.
