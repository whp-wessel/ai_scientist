# Data Quality Checklist (Bootstrap)

- [ ] Confirm file integrity for `childhoodbalancedpublic_original.csv` (checksum pending).
- [ ] Verify survey weight variable presence once metadata is populated in `docs/survey_design.yaml`.
- [ ] Inspect missingness for key variables (`religion`, `biomale`, `externalreligion`, `h33e6gg`).
- [ ] Validate categorical coding against `docs/codebook.json` once completed.
- [ ] Record any data issues and remediation steps here before analysis loops proceed.

**Regeneration command:** `python scripts/bootstrap_artifacts.py`
