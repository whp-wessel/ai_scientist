# Findings Report v0.4
Version: 0.4.0 (robustness integration)  
Updated: 2025-11-04T20:52Z | Seed: 20251016

> **Parity requirement:** Keep this Markdown report in sync with `papers/main/manuscript.tex`. Any change here must be mirrored in LaTeX during the same commit.

## Changelog
- Applied robustness summaries to `analysis/results.csv`, marking passes and annotating limitations.
- Synced narrative updates across `reports/findings_v0.4.md` and `papers/main/manuscript.tex`.
- Re-confirmed Benjamini–Hochberg interpretation using `tables/fdr_adjustment_confirmatory.csv`.
- Logged notebook entry for confirmatory-reporting integration.
- Documented exploratory CSA×moderator diagnostics (Task T-018) to contextualise anxiety findings.

## Abstract
Confirmatory analyses (n = 14,436) indicate that each one-step increase in childhood class corresponds to a 0.18-point rise in adult self-love on the 7-point agreement scale (95% CI [0.16, 0.20], q ≈ 3.9e-51), roughly 0.10 standard deviations. Respondents reporting any childhood sexual abuse agreement average 0.49 points lower on the anxiety agreement scale (95% CI [-0.56, -0.42], q ≈ 6.9e-41), nearly a quarter of a standard deviation. All pre-registered robustness checks corroborate the directions and magnitudes, and the workflow remains reproducible with seed 20251016.

## Methods
- Data source: `data/raw/childhoodbalancedpublic_original.csv` (SHA-256 logged in `artifacts/checksums.json`).
- Derived dataset: `data/clean/childhoodbalancedpublic_with_csa_indicator.csv` regenerated via  
  `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`.
- Confirmatory scope: HYP-001 and HYP-003 (see `analysis/pre_analysis_plan.md`, frozen 2025-11-04T07:58:50Z).
- Statistical plan: HC3 OLS under SRS assumption; Benjamini–Hochberg at q=0.05 within confirmatory family; robustness checks executed per frozen PAP.

## Results
- **HYP-001 (Wellbeing family; Confidence: High)** — Childhood class exhibits a positive association with adult self-love (β = 0.181, SE = 0.012; 95% CI [0.158, 0.205]; q = 3.9e-51). Relative to the outcome SD (1.86), the estimate equals ≈0.10 SD and implies ~0.5-point difference when comparing respondents three class steps apart, holding age, gender, and cis identity constant.
- **HYP-003 (MentalHealth family; Confidence: Medium)** — Any CSA exposure is linked to −0.491 points on the anxiety agreement scale (SE = 0.037; 95% CI [-0.562, -0.419]; q = 6.9e-41). Because higher agreement maps to greater anxiety, the negative coefficient implies CSA-exposed respondents report lower agreement with “I tend to suffer from anxiety,” opposite to the preregistered expectation.
- Benjamini–Hochberg adjustments (q = 0.05 family-wise) leave inference unchanged because both p-values remain far below the threshold.

## Robustness and Sensitivity
- **HYP-001 — Status: Pass**. Treating childhood class as categorical with Helmert contrasts yields an average class effect of 0.07 (F = 89.7). An ordinal logit specification reports a log-odds coefficient of 0.17 (p ≈ 7.3e-48), and z-scoring the outcome produces β = 0.097 (p ≈ 1.6e-51); all checks retain positive direction and comparable magnitude.
- **HYP-003 — Status: Pass**. A logistic model contrasting high anxiety agreement (≥1) produces an odds ratio of 0.57 (95% CI ≈ [0.51, 0.64]). Binning CSA intensity into 0/1–3/4+ bins and trimming the CSA >15 tail both preserve negative associations (β_bins = -0.33; trimmed β = -0.48). An ordinal-logit DIF diagnostic including CSA×gender yields χ²(1) = 0.24 (p = 0.625), mitigating gender-linked measurement concerns.
- **CSA–anxiety subgroup diagnostics (Exploratory)** — Interaction models (CSA×cis identity, CSA×age cohort, CSA×childhood class) fitted via `analysis/code/anxiety_interactions.py` show the CSA main effect stays negative across strata, with interaction terms small and imprecise (|β| < 0.22). Descriptive means confirm CSA-exposed respondents report lower anxiety agreement in every subgroup; the cis/non-cis gap is largest (Δ ≈ -0.80 among exposed). These findings support Task T-019's interpretation of unexpected positive correlations with self-regulation items.
- **Limitations noted in results**: Analyses rely on the SRS assumption; ordinal outcomes are treated as interval measures; CSA indicator derives from a composite score and may embed measurement artefacts affecting sign interpretation.

## Interpretation and Context
Childhood class effects appear modest in scale units yet align with roughly a tenth of the variability in the self-love measure. Meta-analytic work links childhood sexual abuse to elevated anxiety (Lindert et al., 2014; Hashim et al., 2024), and symptom network analysis highlights worry and restlessness as central nodes among CSA survivors (Li et al., 2023). The observed negative coefficient likely reflects measurement or reporting dynamics—potentially stigma-driven disagreement with the negatively framed anxiety item, treatment uptake reducing symptoms, or sample composition differences relative to clinical cohorts. The absence of CSA×gender DIF reduces the likelihood of gender-specific reporting bias. Follow-up diagnostics (T-016) will probe scale direction and subgroup heterogeneity before deriving substantive implications.

## Ethics, Privacy, and Disclosure
- Small-cell suppression threshold: n < 10 (per `config/agent_config.yaml`); apply rounding/binning accordingly.
- Data contain sensitive childhood trauma indicators; confirm IRB posture before dissemination.

## Open Questions
- Prioritize CSA-anxiety scale direction diagnostics and subgroup heterogeneity review (T-016).
- Evaluate readiness of the social support hypothesis (HYP-004) for confirmatory expansion once routing documentation is secured.

## Reproducibility Notes
- Environment snapshot: `artifacts/session_info.txt`; seed: `artifacts/seed.txt` (20251016).
- Confirmatory estimates:  
  `python analysis/code/confirmatory_models.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --survey-design docs/survey_design.yaml --hypotheses HYP-001 HYP-003 --results-csv analysis/results.csv --overwrite`
- FDR adjustment:  
  `python analysis/code/fdr_adjust.py --results analysis/results.csv --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --family-scope confirmatory --audit-table tables/fdr_adjustment_confirmatory.csv`
- Robustness checks:  
  `python analysis/code/run_robustness_checks.py --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --config config/agent_config.yaml --qc-dir qc --tables-dir tables/robustness --hypotheses HYP-001 HYP-003`
- Literature queries (respect 120 s throttle):  
  `sleep 120 && curl -s 'https://api.semanticscholar.org/graph/v1/paper/search?query=childhood%20sexual%20abuse%20anxiety%20adult&limit=3&fields=title,authors,year,venue,url,journal,externalIds' > lit/queries/20251104_semanticscholar_csa_anxiety_adult.json`  
  `sleep 120 && curl -s 'https://api.semanticscholar.org/graph/v1/paper/search?query=childhood%20sexual%20abuse%20anxiety%20depression%20network%20analysis&limit=1&fields=title,authors,year,venue,url,journal,externalIds,abstract' > lit/queries/20251104_semanticscholar_csa_anxiety_network.json`
- No new analytical commands were executed for this update; edits derive from `analysis/results.csv` and `tables/robustness/robustness_checks_summary.csv`.
