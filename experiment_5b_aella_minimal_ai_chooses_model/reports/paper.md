# Childhood Contexts and Adult Wellbeing

_Status: analysis draft (loop 5 confirmatory results)_

## 1. Introduction
- Placeholder: summarize motivation around childhood adversity, resilience, and adult outcomes.

## 2. Data
- Dataset: `childhoodbalancedpublic_original.csv` (Balanced Data release, n unknown pending cleaning).
- No official weights/strata supplied; analyses currently assume SRS with caveats.

## 3. Methods
- Primary variables follow hypotheses H1–H4 (see `analysis/hypotheses.csv`). The PAP is frozen at commit `565989e` (tag `pap_freeze_loop004`), enforcing one confirmatory OLS(HC3) test per family plus the pre-registered H3 ordered-logit sensitivity.
- `analysis/scripts/derive_likert_scales.py` generates centered (`*_scaled`) and standardized (`*_z`) variants of each −3..3 exposure/outcome plus the shared covariate stack (age, gender, education, childhood/teen/adult class). All downstream models read from `analysis/derived/loop002_likert_scales.csv`.
- Confirmatory estimation reuses those deterministic transforms: `python analysis/scripts/run_confirmatory_ols.py` fits the four OLS models with HC3 SEs, and `python analysis/scripts/ordered_logit_h3.py` fits the logit-link ordered model for H3’s ordinal outcome. The design remains SRS because no official weights/strata exist for the Balanced Data release.

## 4. Confirmatory Findings
- Childhood emotional abuse (H1) is associated with lower adult happiness: β=−0.181 (SE=0.0069, 95% CI [−0.195, −0.168], n=14,426; `python analysis/scripts/run_confirmatory_ols.py`), reinforcing longitudinal evidence that emotional maltreatment elevates adult distress (Gartland et al., 2024, DOI 10.1371/journal.pone.0301620).
- Parental guidance (H2) predicts higher adult career satisfaction: β=0.114 (SE=0.0086, 95% CI [0.097, 0.131], n=14,429), aligning with evidence that structured parental support boosts occupational outcomes (So, 2024, DOI 10.15284/kjhd.2024.31.2.11).
- Digital exposure (H3) shows a positive socioeconomic gradient: OLS β=0.042 (SE=0.010, p=3.1×10⁻⁵, n=14,428) and the ordered-logit sensitivity yields β=0.091 (SE=0.022, z=4.08, p=4.4×10⁻⁵), echoing findings that early digital literacy complements later economic opportunity (Asmayawati, 2023, DOI 10.47191/ijmra/v6-i11-30).
- Childhood depression (H4) strongly relates to adult depression: β=−0.324 (SE=0.0071, 95% CI [−0.338, −0.310], n=14,428), consistent with Zhang et al. (2025, DOI 10.1016/j.chiabu.2025.107294) on the persistence of affective symptoms from adolescence to adulthood.

## 5. Literature & Context
- Childhood adversity and adult wellbeing: Gartland et al. (2024), DOI 10.1371/journal.pone.0301620; Zhang et al. (2025), DOI 10.1016/j.chiabu.2025.107294.
- Parental support and occupational outcomes: So (2024), DOI 10.15284/kjhd.2024.31.2.11.
- Digital exposure and later skills: Asmayawati (2023), DOI 10.47191/ijmra/v6-i11-30.

## 6. Next Steps
- Extend sensitivity diagnostics (gender interactions, quadratic terms, leverage) and move toward robustness checks per the PAP.
- Draft tables/figures for manuscript inclusion and prepare public-release tables with n<10 suppression as needed.
