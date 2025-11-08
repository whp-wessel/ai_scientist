status: draft
title: Childhood Experiences, Religiosity, and Adult Wellbeing — Minimal PAP

overview:
- Objective: Explore associations between childhood religious environment, demographics, and adult wellbeing/relationships using `childhoodbalancedpublic_original.csv`.
- Phase: literature → pap (draft)
- Reproducibility: default seed 20251016 (see `artifacts/seed.txt`).

data:
- file: childhoodbalancedpublic_original.csv (read-only)
- codebook: data/codebook.yaml (TODO; infer types during EDA)
- survey_design: config/survey_design.yaml (no weights/strata/clusters; SRS justified for now)

estimands (exploratory; directions not pre-specified):
- H1 (Wellbeing): Association between childhood religious strictness (`externalreligion`) and adult unhappiness (dataset column label: `I am not happy (ix5iyv3)-neg`). Estimand: slope from linear regression of standardized outcome on standardized predictor; covariates `selfage`, `gendermale`.
- H2 (Relationships): Association of current religious practice (`religion`) with monogamy preference (`monogamy`) and relationship satisfaction (label: `I am satisfied with my romantic relationships (hp9qz6f)`). Estimand: difference in means (or marginal effect in ordinal/logit), adjusting for `selfage`, `gendermale`.
- H3 (MentalHealth): Association between teen family SES (`classteen`) and adult depression (label: `I tend to suffer from depression (wz901dj)`) and stress sensitivity (label: `I'm quite sensitive to stress (qhyti2r)-neg`). Estimand: regression slope(s) with covariates.
- H4 (Demographics): Difference in anxiety (label: `I tend to suffer from anxiety (npvfh98)-neg`) by `gendermale`, adjusting for `selfage`.

design assumptions:
- No survey weights/strata/clusters detected; analyses will assume SRS with explicit justification noted in `analysis/results.csv`.
- If design metadata become available, we will re-run primary analyses setting `design_used=true` and update this PAP accordingly.

analysis plan (deterministic commands; to be expanded):
1) Inspect columns and value ranges
   - Command: python scripts/analysis/eda.py --input childhoodbalancedpublic_original.csv --summary outputs/eda_summary.json --public-counts tables/key_vars_value_counts.csv
   - Seed: 20251016
2) Fit minimal models (exploratory)
   - Command: python scripts/analysis/run_models.py --input childhoodbalancedpublic_original.csv --hypotheses analysis/hypotheses.csv --results analysis/results.csv --seed 20251016
   - Seed: 20251016

multiple testing:
- All hypotheses are exploratory at this stage (confirmatory=false). If any family is later promoted to confirmatory with >1 test, we will control FDR at q ≤ 0.05 and compute q_values.

literature:
- Use Semantic Scholar via `scripts/semantic_scholar_cli.py` (loads `S2_API_Key` from `.env` or environment; unauthenticated mode may rate-limit but still saves JSON).
- Queries conducted so far (examples):
  - loop_011: `lit/queries/loop_011/query_001.json` (youth religiosity and depression/anxiety; added E22–E26 to `lit/evidence_map.csv`).
  - loop_012: `lit/queries/loop_012/query_001.json` (religiosity, depression/anxiety, monogamy, relationship satisfaction; appended 5 DOIs to `lit/evidence_map.csv`).
  - loop_013: `lit/queries/loop_013/query_002.json` (adolescent religiosity → adult wellbeing, longitudinal; appended 3 DOIs to `lit/evidence_map.csv`).
  - loop_014: `lit/queries/loop_014/query_001.json` (childhood religiosity → adult wellbeing/relationships, longitudinal framing; HTTP 429 captured unauthenticated; 0 DOIs appended this loop).
  - loop_015: `lit/queries/loop_015/query_001.json` (adolescent religiosity → adult relationship satisfaction/monogamy, longitudinal; 4 DOIs appended to `lit/evidence_map.csv`).
- Evidence is curated into `lit/evidence_map.csv` and citable entries in `lit/bibliography.bib`; main claims will cite at least one peer-reviewed source (DOI/URL).

reproducibility notes:
- Record all seeds, commands, and repo state in `analysis/decision_log.csv`. Snapshot major artifacts each loop and request a commit via `artifacts/git_message.txt`.

freezing protocol:
- This is a draft PAP. Before any confirmatory results, we will freeze with header: `status: frozen (commit <hash>)` and tag the repo accordingly.
