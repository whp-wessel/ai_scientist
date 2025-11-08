# Childhood Contexts and Adult Wellbeing

_Status: outline_

## 1. Introduction
- Placeholder: summarize motivation around childhood adversity, resilience, and adult outcomes.

## 2. Data
- Dataset: `childhoodbalancedpublic_original.csv` (Balanced Data release, n unknown pending cleaning).
- No official weights/strata supplied; analyses currently assume SRS with caveats.

## 3. Methods
- Primary variables follow hypotheses H1–H4 (see `analysis/hypotheses.csv`). Detailed estimands will be added post PAP freeze.
- `analysis/scripts/derive_likert_scales.py` generates centered (`*_scaled`) and standardized (`*_z`) variants of each −3..3 exposure/outcome plus the shared covariate stack (age, gender, education, childhood/teen/adult class). All downstream models read from `analysis/derived/loop002_likert_scales.csv`.
- Exploratory prototypes use OLS with HC3 SEs and the fixed covariate set; confirmatory models will reuse these specifications unless the PAP freeze documents changes.

## 4. Preliminary Findings
- Exploratory OLS indicates that a one-unit increase in childhood emotional abuse (`mds78zu_scaled`) predicts a −0.18 SD change in adult unhappiness (`ix5iyv3_scaled`, n=14,426; command `python analysis/scripts/prototype_h1_h2_regressions.py`).
- The same modeling stack finds a +0.11 SD association between parental guidance (`pqo6jmj_scaled`) and adult work satisfaction (`z0mhd63_scaled`, n=14,429). Both effects remain exploratory until the PAP is frozen.
 - Extending to H3, childhood digital exposure (`4tuoqly_scaled`) associates with higher current socioeconomic status (`classcurrent_z`), β=0.042 (SE=0.010, p≈3.1e−5; n=14,428; command `python analysis/scripts/prototype_h3_h4_regressions.py`).
 - For H4, childhood depression (`dfqbzi5_scaled`) strongly predicts adult depression (`wz901dj_scaled`), β=−0.324 (SE=0.007, p<1e−300; n=14,428). These results are exploratory and subject to the forthcoming PAP freeze and sensitivity checks (including ordered logit for H3).

## 5. Literature & Context
- Childhood adversity and adult wellbeing: Gartland et al. (2024), DOI 10.1371/journal.pone.0301620; Zhang et al. (2025), DOI 10.1016/j.chiabu.2025.107294.
- Parental support and occupational outcomes: So (2024), DOI 10.15284/kjhd.2024.31.2.11.
- Digital exposure and later skills: Asmayawati (2023), DOI 10.47191/ijmra/v6-i11-30.

## 6. Next Steps
- Finalize survey design documentation (weights/strata) or lock in the SRS justification before PAP freeze.
- Extend the harmonized scale workflow + regression prototypes to H3/H4 and stress-test nonlinearities/interactions.
- Freeze the PAP and transition to confirmatory estimation once diagnostic checks are complete.
