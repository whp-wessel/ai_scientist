# Social Support Predictor Feasibility
Generated: 2025-11-03T21:35:00Z | Seed: 20251016  
Regenerate via:

```bash
python analysis/code/social_support_missingness.py \
  --dataset data/clean/childhoodbalancedpublic_with_csa_indicator.csv \
  --out-csv tables/social_support_missingness.csv \
  --config config/agent_config.yaml
```

## Inputs
- `data/clean/childhoodbalancedpublic_with_csa_indicator.csv`
- `config/agent_config.yaml` (small cell threshold = 10)

## Findings (Exploratory)
- Social support item tied to hypothesis HYP-004 (`...tend treat me really well (tmt46e6)`) is observed for 383 respondents (2.65% of N=14,443); 97.35% missing.
- Alternative item with identical wording but code `71mn55g` is populated for 14,054 respondents (97.3% coverage) and shares the same 7-point response structure.
- Responses are mutually exclusive across the two instrument codes (no overlapping respondents), implying survey routing or form-version differences rather than random attrition.
- Both high-missing (`tmt46e6`) and high-coverage (`71mn55g`) variants exceed the disclosure threshold at the aggregate level; no category-level counts are released to avoid cells <10.

## Implications
- HYP-004 is not feasible with `tmt46e6` due to insufficient power and severe missingness.
- Recommend updating the hypothesis to use `71mn55g` (after confirming instrument equivalence) or deferring the hypothesis if instrument harmonisation is not defensible.
- Next step: confirm with survey documentation whether `tmt46e6` and `71mn55g` are interchangeable, then refresh the codebook and PAP accordingly prior to freeze.
