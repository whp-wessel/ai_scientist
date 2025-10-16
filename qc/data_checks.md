# Data Quality Checklist (Bootstrap)

Generated: 2025-10-16T12:44:10Z  
Seed: 20251016  
Regenerate: `python analysis/code/bootstrap_setup.py --only qc`

## Pending Checks

- [ ] Verify dataset schema against `docs/codebook.json`.
- [ ] Confirm presence/validity of survey weight, strata, and cluster variables.
- [ ] Inspect missingness patterns for variables referenced in HYP-001 to HYP-003.
- [ ] Screen for small cells (<10) before publishing tables or plots.
- [ ] Record outcome variable distributions (Exploratory only).

## Notes

This checklist is a living document; mark items complete and add diagnostics as the project progresses.
