# Reduced-Auxiliary MICE Sensitivity Plan

- Prepared: 2025-10-16T14:08:49Z (UTC)
- Seed: `20251016`
- Status: Planning (no data written)
- Purpose: Stress-test key wellbeing/socioeconomic inferences by rerunning MICE with a trimmed predictor set, isolating dependence on auxiliary covariates.

## Column Set (Run Label `reduced_aux`)
Use only outcome/predictor/control variables required for HYP-001 and HYP-002 plus demographic core:

```
selfage
biomale
gendermale
cis
education
classchild
classteen
classcurrent
networth
I love myself (2l8994l)
during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)
```

Rationale: retain structural covariates necessary for PAP analyses while omitting auxiliary predictors (religion, liberal identity, monogamy, mentalillness) to assess influence on imputed distributions.

## Execution Template
```
python analysis/code/mice_prototype.py \
  --dataset childhoodbalancedpublic_original.csv \
  --config config/agent_config.yaml \
  --seed 20251016 \
  --n-imputations 20 \
  --burn-in 10 \
  --run-label reduced_aux \
  --columns \
    selfage biomale gendermale cis education classchild classteen classcurrent \
    networth "I love myself (2l8994l)" \
    "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)"
```

Outputs (auto-generated via run label):
- `data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz`
- `analysis/imputation/mice_imputation_summary__reduced_aux.csv`
- `analysis/imputation/mice_prototype_summary__reduced_aux.md`
- `analysis/imputation/mice_prototype_metadata__reduced_aux.json`
- `analysis/imputation/mice_variable_map__reduced_aux.json`

## Planned Diagnostics
1. **Convergence** — Inspect pseudo-trace plots from stacked imputations (`analysis/imputation/mice_prototype_summary__reduced_aux.md`).
2. **Distribution Shift** — Rerun `analysis/code/review_imputed_vs_complete.py` twice to compare (a) reduced-aux vs complete-case and (b) reduced-aux vs full-aux (`prototype`) imputations. Store CSV/MD under `analysis/imputation/` with label suffixes.
3. **Estimate Stability** — Refit primary models for HYP-001 and HYP-002 using the reduced-aux stacks; compare effect estimates and pooled SEs to prototype run. Flag deviations >15% for discussion.
4. **Small-Cell Audit** — Confirm all published tables/plots mask counts <10; update suppression notes if any new low-frequency combinations appear.

## Follow-Up Tasks
- Extend decision log and PAP robustness section once diagnostics are executed.
- Archive comparative summaries in `tables/` and reference in `reports/findings_v*.md` when confirmatory analyses begin.
- If reduced-aux run diverges materially, schedule additional MI run reintroducing subsets of auxiliaries to localize sensitivity.

## Regeneration Notes
- Requires `statsmodels` MICE implementation (see `artifacts/session_info.txt`).
- All randomness seeded via NumPy global RNG (`seed=20251016`).
- Execute within repository root; outputs overwrite same-label artifacts only.
