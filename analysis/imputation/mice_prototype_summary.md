# Multiple Imputation Prototype (Exploratory)

- Completed: 2025-10-16T13:49:53.340817Z
- Dataset: `childhoodbalancedpublic_original.csv`
- Seed: `20251016`
- Imputations: 20
- Burn-in iterations: 10
- Output (stacked imputations): `data/derived/childhoodbalancedpublic_mi_prototype.csv.gz`
- Summary table: `analysis/imputation/mice_imputation_summary.csv`
- All randomness seeded via NumPy global state.

## Missingness (Counts masked <10)
- Dropped columns with no observed values: Religionchildhood, mentalillness
- selfage: missing_before=<10, missing_fraction=0.00000, mean_after=30.425, sd_after=10.169
- biomale: missing_before=<10, missing_fraction=0.00000, mean_after=0.589, sd_after=0.492
- gendermale: missing_before=<10, missing_fraction=0.00000, mean_after=0.572, sd_after=0.495
- cis: missing_before=<10, missing_fraction=0.00000, mean_after=0.917, sd_after=0.276
- liberal: missing_before=<10, missing_fraction=0.00000, mean_after=0.120, sd_after=1.659
- education: missing_before=<10, missing_fraction=0.00000, mean_after=4.379, sd_after=1.611
- religion: missing_before=<10, missing_fraction=0.00000, mean_after=0.496, sd_after=0.854
- monogamy: missing_before=<10, missing_fraction=0.00000, mean_after=1.142, sd_after=1.270
- classcurrent: missing_before=<10, missing_fraction=0.00000, mean_after=3.022, sd_after=1.259
- networth: missing_before=<10, missing_fraction=0.00000, mean_after=2.050, sd_after=1.899
- I love myself (2l8994l): missing_before=<10, missing_fraction=0.00049, mean_after=0.613, sd_after=1.862
- classteen: missing_before=<10, missing_fraction=0.00000, mean_after=2.760, sd_after=1.249
- classchild: missing_before=<10, missing_fraction=0.00000, mean_after=2.621, sd_after=1.276
- during ages *0-12*: your parents verbally or emotionally abused you (mds78zu): missing_before=17, missing_fraction=0.00118, mean_after=-0.225, sd_after=2.408

## Regeneration
```bash
python analysis/code/mice_prototype.py --dataset childhoodbalancedpublic_original.csv --config config/agent_config.yaml --seed 20251016 --n-imputations 20 --burn-in 10
```

*Exploratory output — do not use for confirmatory analyses without a frozen PAP.*