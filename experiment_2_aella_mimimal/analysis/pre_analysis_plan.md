# Pre-Analysis Plan (Draft)

**Seed:** 20251016  
**Regeneration command:** `python scripts/bootstrap_artifacts.py`

## Project Overview
This document sketches the initial analytic roadmap for the childhood balance public survey. It is a living draft that will be versioned until the PAP is frozen. The plan prioritizes reproducibility, privacy (minimum cell size = 10), and alignment between Markdown deliverables and the future LaTeX manuscript (`manuscript.tex`).

## Data & Design Inputs
- Primary dataset: `childhoodbalancedpublic_original.csv` (read-only source).
- Metadata: `docs/codebook.json` (variable stubs) and `docs/survey_design.yaml` (design placeholders).
- Weighting: pending confirmation of the final weight variable. Analyses will default to unweighted diagnostic checks until `weight_variable` is populated, after which all estimates will be weighted.

## Candidate Hypotheses (Descriptive/Associational)
1. **H-A:** The weighted proportion of respondents who currently practice a religion (`religion`) differs by biological sex (`biomale`).
2. **H-B:** Greater reported importance of childhood religious adherence (`externalreligion`) is associated with higher adult happiness relative to childhood (`I am happier as an adult than I was in childhood (h33e6gg)`).
3. **H-C:** Respondents reporting higher current net worth brackets (`networth`) are more satisfied with their work or career (`I am satisfied with my work/career life (z0mhd63)`).
4. **H-D:** Self-reported depression tendency (`I tend to suffer from depression (wz901dj)`) is positively associated with stress sensitivity (`I'm quite sensitive to stress (qhyti2r)-neg`).
5. **H-E:** Older respondents (`selfage`) report higher counts of lifetime sexual partners (`How many people have you had sex with? (ewvvaz2)`).

## Priority Hypotheses for Immediate Work
### H1 (Priority: High)
- **Statement:** The weighted proportion of active religious practice (`religion`) varies by biological sex (`biomale`).
- **Estimand:** Difference in weighted proportions male vs. non-male.
- **Approach:**
  - Confirm weight and design variables from `docs/survey_design.yaml`.
  - Recode `religion` as an indicator for any active practice (`religion > 0`) to align with survey response gradations.
  - Use survey-weighted proportion estimates with 95% confidence intervals (Taylor linearization initially).
  - Apply privacy guardrails by suppressing any subgroup estimate with n < 10.
  - Implement deterministic workflow via `python scripts/analyze_h1_religion_by_biomale.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h1_religion_by_biomale.csv --diff-out tables/h1_religion_by_biomale_diff.csv --manifest artifacts/h1_religion_by_biomale_manifest.json`.
- **Diagnostics:** Assess missingness in `religion` and `biomale`; compare unweighted vs. weighted proportions.

### H2 (Priority: Medium)
- **Statement:** Higher childhood religious strictness (`externalreligion`) is associated with greater adult happiness change (`h33e6gg`).
- **Estimand:** Survey-weighted difference in mean adult-vs-childhood happiness scores across terciles of `externalreligion`.
- **Approach:**
  - Confirm scale direction for both variables using the codebook.
  - Construct deterministic terciles of `externalreligion` via ordinal breakpoints (0 | 1-2 | 3-4) under SRS assumptions.
  - Estimate SRS means and Bonferroni-adjusted pairwise differences for `On average, I am happier as an adult than I was in childhood (h33e6gg)`.
  - Suppress cells where any tercile has <10 observations contributing to the estimate.
  - Regeneration command (seed=20251016):  
    `python scripts/analyze_h2_religion_strictness_vs_happiness.py --csv childhoodbalancedpublic_original.csv --config config/agent_config.yaml --design docs/survey_design.yaml --out tables/h2_happiness_by_religion_strictness.csv --diff-out tables/h2_happiness_by_religion_strictness_diff.csv --manifest artifacts/h2_religion_strictness_vs_happiness_manifest.json`
- **Diagnostics:** Explore missing data patterns and perform sensitivity checks with unweighted comparisons.

## Analysis Workflow Outline
1. Validate design information (`T-001`).
2. Produce weighted descriptive summaries for variables in H1 and H2 (`T-002`).
3. Generate deterministic H1 proportion estimates via `scripts/analyze_h1_religion_by_biomale.py` and archive manifests.
4. Draft shell scripts for deterministic data processing once design metadata confirmed.
5. Update manuscript (`manuscript.tex`) after each major analytic milestone to mirror Markdown findings.

## Privacy and Quality Control
- Enforce minimum cell size of 10 in all tables and plots.
- Document QA steps in `qc/data_checks.md` with pass/fail status and regeneration commands.
- Use deterministic seeds for any resampling or imputation; record seeds alongside outputs.

## Manuscript Coordination
- Maintain synchronized updates between Markdown narratives (e.g., `reports/`) and `manuscript.tex`.
- Record versioned changes in git immediately after producing major artifacts (state updates, PAP revisions, hypotheses registry adjustments).

## Outstanding TODOs Before Freezing PAP
- Populate `docs/codebook.json` with full variable metadata.
- Confirm survey design elements and update `config/agent_config.yaml` defaults.
- Prototype analysis scripts to automate the above regeneration command.
- Revisit hypotheses list after exploratory summaries to ensure feasibility and refine estimands.
