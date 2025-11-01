# Multiple Imputation Prototype (Exploratory)

- Completed: 2025-10-17T16:31:09.464551Z
- Dataset: `childhoodbalancedpublic_original.csv`
- Seed: `20251016`
- Imputations: 20
- Burn-in iterations: 10
- Output (stacked imputations): `data/derived/childhoodbalancedpublic_mi_reduced_aux.csv.gz`
- Summary table: `analysis/imputation/mice_imputation_summary__reduced_aux.csv`
- Run label: `reduced_aux`
- All randomness seeded via NumPy global state.

## Missingness (Counts masked <10)
- selfage: missing_before=<10, missing_fraction=0.00000, mean_after=30.425, sd_after=10.169
- biomale: missing_before=<10, missing_fraction=0.00000, mean_after=0.589, sd_after=0.492
- gendermale: missing_before=<10, missing_fraction=0.00000, mean_after=0.572, sd_after=0.495
- cis: missing_before=<10, missing_fraction=0.00000, mean_after=0.917, sd_after=0.276
- education: missing_before=<10, missing_fraction=0.00000, mean_after=4.379, sd_after=1.611
- classcurrent: missing_before=<10, missing_fraction=0.00000, mean_after=3.022, sd_after=1.259
- networth: missing_before=<10, missing_fraction=0.00000, mean_after=2.050, sd_after=1.899
- I love myself (2l8994l): missing_before=<10, missing_fraction=0.00049, mean_after=0.613, sd_after=1.862
- classteen: missing_before=<10, missing_fraction=0.00000, mean_after=2.760, sd_after=1.249
- classchild: missing_before=<10, missing_fraction=0.00000, mean_after=2.621, sd_after=1.276
- during ages *0-12*: your parents verbally or emotionally abused you (mds78zu): missing_before=17, missing_fraction=0.00118, mean_after=-0.225, sd_after=2.408

## Regeneration
```bash
python analysis/code/mice_prototype.py --dataset childhoodbalancedpublic_original.csv --config config/agent_config.yaml --seed 20251016 --n-imputations 20 --burn-in 10 --run-label reduced_aux --columns selfage biomale gendermale cis education classchild classteen classcurrent networth 'I love myself (2l8994l)' 'during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)'
```

*Exploratory output — do not use for confirmatory analyses without a frozen PAP.*