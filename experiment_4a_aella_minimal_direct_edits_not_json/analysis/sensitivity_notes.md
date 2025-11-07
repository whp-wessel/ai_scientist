# H1 Sensitivity Analyses — Loop 007 (2025-11-07)

All runs rely on the frozen dataset (`childhoodbalancedpublic_original.csv`), the aligned Likert pipeline in `scripts/likert_utils.py`, and the default seed `PYTHONHASHSEED=20251016`. Command:  
`PYTHONHASHSEED=20251016 python scripts/loop007_h1_sensitivity.py`

The script regenerates the confirmatory models with two perturbations and stores the coefficients/q-values in `tables/loop007_h1_sensitivity.csv` (no privacy risks—coefficients only, n≈14.4k per row).

## 1. HC3 Robust Standard Errors (preregistered controls)
- **Spec**: Matches the PAP controls (`classteen`, `selfage`, `gendermale`, `education`) but reports HC3 heteroskedasticity-consistent SEs.
- **Findings**: Guidance-buffering coefficient remains 0.068 with HC3 SE 0.00855 (p=2.2e-15, q=4.5e-15); male-vulnerability coefficient stays -0.103 with HC3 SE 0.0158 (p=q≈8.7e-11). Both still exceed the confirmatory threshold (q≤0.05) while preserving the preregistered signs.

## 2. Expanded Covariate Set
- **Spec**: Adds `classchild`, `classcurrent`, `religion`, `externalreligion`, and `guidance_teen_z` to the PAP controls to probe socioeconomic/religious confounding.
- **Findings**: Guidance-buffering drops modestly to 0.063 (SE 0.00815, p=1.1e-14, q=2.2e-14). Male-vulnerability attenuates to -0.095 (SE 0.0154, p=q≈6.2e-10). Effects remain significant with identical signs, indicating robustness to plausible omitted controls.

## Takeaways
- The confirmatory H1 contrasts are resilient to both heteroskedasticity adjustments and richer socioeconomic/religious controls.
- No evidence suggests that PAP conclusions hinge on homoskedastic SEs or the baseline covariate set; we can cite `tables/loop007_h1_sensitivity.csv` in the manuscript’s robustness section and proceed to broader sensitivity work (e.g., bootstraps or alternative outcome codings) in later loops if needed.
