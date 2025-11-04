# Social Support Instrument Equivalence
Generated: 2025-11-03T22:05:00Z | Seed: 20251016  
Regenerate via:

```bash
python analysis/code/verify_social_support_equivalence.py \
  --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
  --out-summary tables/social_support_equivalence_summary.csv \
  --out-distribution tables/social_support_equivalence_distributions.csv \
  --out-overlap tables/social_support_instrument_overlap.csv \
  --config config/agent_config.yaml \
  --columns \
  "In general, people in my *current* social circles tend treat me really well (tmt46e6)" \
  "In general, people in my *current* social circles tend to treat me really well (71mn55g)"
```

## Inputs
- `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`
- `config/agent_config.yaml` (seed=20251016; small_cell_threshold=10)

## Outputs
- `tables/social_support_equivalence_summary.csv` (+ `.meta.json`)
- `tables/social_support_equivalence_distributions.csv`
- `tables/social_support_instrument_overlap.csv`

## Findings (QC)
- Both instrument variants share the same 7-point Likert scale (−3 to +3) and nearly identical prompt text; the only observed difference is the missing word “to” in the tmt46e6 metadata.
- Coverage differs sharply: `tmt46e6` observes 383 respondents (2.65%), while `71mn55g` covers 14,054 respondents (97.3%).
- No respondent appears in both instruments (overlap table confirms zero dual non-missing cases), indicating routing/form-version separation rather than partial nonresponse.
- Distribution tables suppress cell counts <10; remaining counts exceed disclosure thresholds and confirm similar response profiles across forms.

## Implications
- Treat `In general, people in my *current* social circles tend to treat me really well (71mn55g)` as the analytic predictor for HYP-004 going forward; retain `tmt46e6` for archival sensitivity checks only.
- Updated `docs/codebook.json` and `analysis/hypotheses.csv` to reflect the instrument pivot and equivalence verification.
- Next action: integrate revised predictor into confirmatory model skeleton before PAP freeze (see backlog item T-008).
