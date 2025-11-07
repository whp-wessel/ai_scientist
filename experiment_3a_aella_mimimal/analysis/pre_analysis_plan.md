---
status: draft
updated: 2025-11-07T10:59:04Z
phase: literature
seed: 20251016
---

# Pre-Analysis Plan (draft)

## Objective
Study how childhood socialization, religious expectations, and family dynamics relate to adult well-being, relationship preferences, and socioeconomic attainment using the `childhoodbalancedpublic_original.csv` survey.

## Data Inputs and Provenance
- Primary dataset: `childhoodbalancedpublic_original.csv` (read-only snapshot).
- Codebook / survey config: **missing** -- see `docs/codebook_status.md` for a standing TODO to obtain instrument metadata.
- Survey design features: not yet located; defaulting to a simple random sample (SRS) assumption until weights/strata/clusters are found or confirmed absent.

## Hypothesis Registry (see `analysis/hypotheses.csv` for details)
1. **H1 (wellbeing_parenting):** Higher childhood parental guidance (0-12) associates with higher current self-love scores.
2. **H2 (sexual_attitudes):** Exposure to purity culture before age 12 increases the likelihood of preferring strict monogamy in adulthood.
3. **H3 (socioeconomic_mobility):** Higher perceived childhood class predicts higher current net-worth categories.
4. **H4 (mental_health):** Experiencing parental emotional abuse during adolescence (13-18) associates with greater adult anxiety.

All hypotheses are exploratory at this stage; confirmatory status will only be assigned after freezing this PAP and tagging the commit per the Constitution.

## Planned Data Handling (draft)
- Load data via reproducible Python scripts (pandas) using the default seed `20251016` for any stochastic operations (e.g., bootstrapping, train/test splits).
- Inspect and harmonize Likert scales; recode textual responses into ordered categorical or binary variables as needed.
- Document any derived variables (e.g., terciles for guidance, binary monogamy indicators) in `analysis/code/` scripts with deterministic logic.

## Modeling Strategy (initial thoughts)
- H1/H4: Linear or ordered logistic regression of standardized well-being/anxiety scales on binary/tercile exposure indicators, adjusting for age, gender, and current class.
- H2: Logistic/ordinal regression for monogamy preference on purity-culture exposure with controls for religiosity and age.
- H3: Ordered logistic regression linking childhood class to adult net worth, with controls for education and gender.

## Design + Inference Considerations
- Pending confirmation of survey weights; if none exist, provide an explicit SRS justification referencing the sampling frame once clarified.
- Control false discovery rate (target q <= 0.05) within each hypothesis family once multiple tests are run.

## Outstanding Questions / TODOs
1. Obtain official codebook and survey design documentation.
2. Verify whether any weights or replicate weights are bundled elsewhere in the repo.
3. Clarify coding for "-neg" labeled items (e.g., anxiety) to ensure directionality is interpreted correctly.
4. Define data-cleaning scripts under version control before moving beyond exploratory summaries.
