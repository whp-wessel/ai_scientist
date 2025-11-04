# Research Notebook (Bootstrap Scaffold)

**Seed:** 20251016  
**Regeneration command:** `python scripts/bootstrap_artifacts.py`

## Session 0 Overview
- Initialized repository structure and placeholder metadata files.
- Documented initial hypotheses and PAP priorities (see `analysis/pre_analysis_plan.md`).
- Recorded backlog items in `artifacts/state.json`.

## Planned Next Entries
1. Run exploratory weighted summaries for religion and happiness variables.
2. Document QA checks and sync findings with `manuscript.tex`.
3. Monitor sponsor communications for survey design metadata updates.

> Update this notebook after each analysis loop with commands run, seeds used, and outputs generated.

## Loop 1 - Survey Design Validation

- **Commands:**  
  - `python scripts/design_scan.py --csv childhoodbalancedpublic_original.csv`  
  - `python - <<'PY'` (counts rows; see `qc/design_validation.md`)
- **Seed:** 20251016 (inherited; no stochastic procedures invoked).
- **Outcome:** No survey weight, strata, cluster, or replicate columns detected. Updated `docs/survey_design.yaml`, `config/agent_config.yaml`, and `qc/data_checks.md`; recorded findings in `qc/design_validation.md`.

## Loop 2 - Exploratory Summaries for Key Outcomes

- **Commands:**  
  - `python scripts/exploratory_summaries.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --out tables/summary_key_outcomes.csv`
- **Seed:** 20251016 (deterministic computation; no stochastic elements beyond fixed seed).
- **Outputs:** `tables/summary_key_outcomes.csv`, `tables/summary_key_outcomes.json`
- **Notes:** Generated unweighted descriptive statistics for priority outcomes because calibrated survey weights remain unavailable. All reported cells meet the minimum count threshold (>=10) enforced within the script.

## Loop 3 - Sponsor Design Metadata Monitoring

- **Commands:**  
  - `python scripts/design_scan.py --csv childhoodbalancedpublic_original.csv`
- **Seed:** 20251016 (deterministic scan; no randomness invoked).
- **Outcome:** Confirmed no new sponsor-provided survey design metadata files. Script matches only questionnaire columns containing "weight" or "jk" substrings; none correspond to calibrated weights or replicate designs. See `qc/design_metadata_monitor.md` for details.

## Loop 6 - H1 Religion by Sex Estimates

- **Commands:**  
  - `python scripts/analyze_h1_religion_by_biomale.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h1_religion_by_biomale.csv --diff-out tables/h1_religion_by_biomale_diff.csv --manifest artifacts/h1_religion_by_biomale_manifest.json`
- **Seed:** 20251016 (set via config; analysis deterministic under SRS assumption).
- **Outputs:** `tables/h1_religion_by_biomale.csv`, `tables/h1_religion_by_biomale_diff.csv`, `artifacts/h1_religion_by_biomale_manifest.json`.
- **Notes:** Recast `religion` responses into an "any practice" indicator (`religion > 0`). The SRS-based estimate indicates non-male respondents practice religion at a higher rate than male respondents (difference ≈ -0.058, 95% CI [-0.074, -0.043]). All subgroup counts exceed the privacy threshold (>=10).

## Loop 7 - H2 Religion Strictness vs Happiness

- **Commands:**  
  - `python scripts/analyze_h2_religion_strictness_vs_happiness.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h2_happiness_by_religion_strictness.csv --diff-out tables/h2_happiness_by_religion_strictness_diff.csv --manifest artifacts/h2_religion_strictness_vs_happiness_manifest.json`
- **Seed:** 20251016 (deterministic SRS means; no additional randomness).
- **Outputs:** `tables/h2_happiness_by_religion_strictness.csv`, `tables/h2_happiness_by_religion_strictness_diff.csv`, `artifacts/h2_religion_strictness_vs_happiness_manifest.json`.
- **Notes:** Ordinal `externalreligion` values were partitioned into terciles (0 | 1-2 | 3-4) using deterministic cumulative counts. Mean adult-vs-childhood happiness scores rise from Tercile 2 to Tercile 3 (difference ≈ 0.144, Bonferroni-adjusted 95% CI [0.043, 0.244]) while Tercile 1 exceeds Tercile 2 by ≈0.104 in the negative direction. All reported cells satisfy the minimum n ≥ 10 privacy guardrail.
