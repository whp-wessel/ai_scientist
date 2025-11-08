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
- To be reported in `analysis/results.csv` and public tables under `tables/` with n<10 suppression.

References:
- See `lit/bibliography.bib` and `lit/evidence_map.csv`.
