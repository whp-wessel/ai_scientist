# QC Checklist
Generated: 2025-11-03T21:05:45Z | Seed: 20251016
Regeneration:
- `python analysis/code/bootstrap_setup.py --artifact qc/data_checks.md` (scaffold)
- `python analysis/code/profile_missingness.py --dataset childhoodbalancedpublic_original.csv --codebook docs/codebook.json --hypotheses analysis/hypotheses.csv --config config/agent_config.yaml --out-csv tables/missingness_profile.csv --out-patterns tables/missingness_patterns.csv`
- `python analysis/code/derive_csa_indicator.py --dataset data/raw/childhoodbalancedpublic_original.csv --out-dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv --out-distribution tables/csa_indicator_distribution.csv --config config/agent_config.yaml --codebook-in docs/codebook.json --codebook-out docs/codebook.json`
- `cat tables/missingness_profile.meta.json` (metadata)

- [x] Dataset present (read-only).
- [x] Align schema with codebook (see `qc/schema_alignment.md`).
- [x] Confirm weight/strata/cluster variables (see `qc/survey_design_validation.md`).
- [x] Summarise missingness for key variables (outputs suppressed where n<10).
- [x] Ensure no small cells (n<10) in shared outputs.
- [x] Validate CSA indicator distribution (`tables/csa_indicator_distribution.csv`).

Notes:
- High item nonresponse (97.35%) for social support predictor `In general, people in my *current* social circles tend treat me really well (tmt46e6)`; confirm suitability before PAP freeze.
- `CSA_score_indicator` derived from `CSA_score` (>0) via reproducible script; distribution reviewed (no suppressed cells).
