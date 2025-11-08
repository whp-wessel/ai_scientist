Title: Childhood Experiences, Religiosity, and Adult Wellbeing — Initial Study

Status: working draft

Abstract:
We examine associations between childhood religious environment, demographics, and adult wellbeing and relationships using a public survey dataset (childhoodbalancedpublic_original.csv). This initial iteration specifies hypotheses and a reproducible analysis plan; results are exploratory and not confirmatory.

Introduction:
Childhood environments can shape adult wellbeing and relational outcomes. Prior work suggests that adverse childhood experiences are linked to adult health and mental health (Felitti et al., 1998; DOI: 10.1016/S0749-3797(98)00017-8). We explore how childhood religious strictness and socioeconomic context relate to adult self-reported wellbeing.

Data:
- Source: `childhoodbalancedpublic_original.csv` (read-only in repo root)
- Codebook: `data/codebook.yaml` (placeholder to be expanded)
- Survey design: `config/survey_design.yaml` (no weights/strata/clusters; SRS assumed)

Methods:
- Pre-registered elements are captured in `analysis/pre_analysis_plan.md` (status: draft).
- We will estimate associations using linear or logistic models, reporting effect sizes with uncertainty.
- Multiplicity controls (FDR) will apply if/when confirmatory families are registered with >1 test.

Results:
- EDA summary generated (see `outputs/eda_summary.json`); public counts for key variables provided in `tables/key_vars_value_counts.csv` (cells with n<10 masked as "<10").
- Inferential results will be added to `analysis/results.csv` in later phases; current work remains exploratory.

Public Tables (Privacy-Aware):
- `tables/religion_by_monogamy.csv`: cross-tabulation of current religious practice by monogamy preference with n<10 cell suppression.

Exploratory estimates (Loop 003; standardized OLS; SRS assumption):
- See `analysis/results.csv` for full details. Briefly: teen SES positively associated with depression and stress items; male indicator positively associated with anxiety item; religion positively associated with monogamy preference; religion ~ relationship satisfaction effect is small; childhood religious strictness ~ unhappiness is near zero. All non-confirmatory.

References:
- See `lit/bibliography.bib` and `lit/evidence_map.csv`.
