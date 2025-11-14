# Loop 3 Literature Phase Notes

## Dataset overview
- `childhoodbalancedpublic_original.csv` has 14,443 completed responses and 718 survey columns capturing demographics, childhood experiences, mental health attitudes, and life satisfaction.
- Respondents are predominantly from the United States (7,498), followed by the United Kingdom (1,191), Canada (963), Australia (545), and western Europe (443), with a politicized preference distribution centered on "Equally liberal/conservative" (4,870) and a lean toward slightly/moderately conservative (3,806) compared to liberal (3,390).
- Subjective social-class indicators (`classchild`, `classteen`, `classcurrent`) use a 0-6 scale (higher = higher class); most responses cluster in the middle values (2-4) but the distribution spans the full scale.

## Key constructs and variables of interest
- **Subjective childhood socioeconomic position**: `classchild` counts show 2-4 dominating (80% of sample) but with meaningful lower-class (0-1) and upper-class (5-6) tails, which allows heterogeneity for modeling social-class gradients in adulthood.
- **Adult mental health/self-concept proxies**: Items such as `I tend to suffer from depression (wz901dj)`, `I tend to suffer from anxiety (npvfh98)-neg`, `I love myself (2l8994l)`, and `I am not happy (ix5iyv3)-neg` are recorded on Likert scales and have population means near the neutral point (means range roughly -0.83 to 0.61), so they can serve as outcomes describing well-being.
- **Childhood relational experiences**: There are fine-grained Likert records for parental behavior (e.g., `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` and the 13-18 equivalent) and parental support (`during ages *0-12*: Your parents gave useful guidance (pqo6jmj)`), each ranging from -3 to +3, giving a balance of reported abuse and guidance experiences with low missingness.

## Literature context (peer-reviewed sources)
1. Franziska Reiss (2013) synthesizes longitudinal and cross-sectional studies showing that lower socioeconomic position in childhood and adolescence consistently predicts mental-health problems such as depression and anxiety into later adolescence and adulthood (Reiss, *Social Science & Medicine*, 90:24-31, doi:10.1016/j.socscimed.2013.04.026).
2. Norman et al. (2012) meta-analyze global evidence and report that each form of childhood maltreatment—including emotional abuse—carries elevated odds of adult depression, anxiety, and suicidality, even after adjusting for socioeconomic covariates (Norman et al., *PLoS Medicine*, 9(11):e1001349, doi:10.1371/journal.pmed.1001349).
3. Masten (2001) identifies responsive caregiving and guidance as core protective factors, highlighting how consistent parental support contributes to resilience and positive self-regard across development (Masten, *American Psychologist*, 56(3):227-238, doi:10.1037/0003-066X.56.3.227).

## Candidate hypotheses grounded in data and literature
1. **Childhood social class gradient in adult well-being**: Respondents reporting lower `classchild` will report worse adult mental-health indicators (higher values on `I tend to suffer from depression` and lower values on `I love myself`). This aligns with Reiss (2013), who finds stable associations between childhood socioeconomic disadvantage and later depression/anxiety after controlling for confounders.
2. **Emotional/verbally abusive parenting and adult distress**: Respondents with more negative scores on `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` or its teen counterpart will have worse adult well-being (higher `I am not happy` and `I tend to suffer from anxiety`). Norman et al. (2012) demonstrates that emotional abuse carries sustained adult mental-health penalties even in samples weighted for other adversities.
3. **Parental guidance as a resilience factor**: Higher scores on `during ages *0-12*: Your parents gave useful guidance (pqo6jmj)` and the 13-18 equivalent should predict higher adult self-esteem (`I love myself`) and work/career satisfaction (`I am satisfied with my work/career life`). Masten (2001) frames positive parental support as a consistent protective resilience process that alters trajectories after hardship.

## Reproducibility notes
- All summaries above derive from `childhoodbalancedpublic_original.csv` (14,443 × 718) using Pandas scripts that read the file with default parsing and compute `value_counts()` for key columns; the relevant Python commands are recorded in the working log.
- Future analysts should re-run the same scripts (or equivalent R/tidyverse pipelines) to regenerate the descriptive counts described above.

# Loop 4 Literature Phase Notes

## Dataset refresh
- The same `childhoodbalancedpublic_original.csv` includes 14,443 records and 718 columns; most respondents (7,498) report living in the United States, with sizable samples from the United Kingdom (1,191), Canada (963), Australia (545), and western Europe (443).
- Subjective social class scales retain a roughly normal spread: `classchild` mean 2.62 (SD 1.28), `classteen` mean 2.76 (SD 1.25), and `classcurrent` mean 3.02 (SD 1.26) on a 0-6 scale, so both low- and high-class experiences are well represented.
- Mental-health proxies remain close to neutral: `I tend to suffer from depression (wz901dj)` mean -0.41 (SD 2.09), `I tend to suffer from anxiety (npvfh98)-neg` mean -0.83 (SD 2.03), `I love myself (2l8994l)` mean 0.61 (SD 1.86), and `I am not happy (ix5iyv3)-neg` mean 0.15 (SD 1.98). This spread should allow modeling both positive and negative well-being outcomes.
- Religion practice is concentrated among non-practitioners (9,953 say "No" to current practice), with a smaller group reporting varying levels of religiosity; this suggests we can control for religious engagement when modeling subjective outcomes.

## Literature reinforcement
- Reiss (2013) systematically reviews longitudinal and cross-sectional studies in *Social Science & Medicine* and concludes that lower childhood socioeconomic status predicts persistent adolescent and adult mental-health problems (doi:10.1016/j.socscimed.2013.04.026).
- Norman et al. (2012) conduct a meta-analysis in *PLoS Medicine* showing that emotional abuse—a component of verbal or psychological mistreatment—has a large, persistent effect on adult depression, anxiety, and suicidality even after adjusting for socioeconomic covariates (doi:10.1371/journal.pmed.1001349).
- Masten (2001) in *American Psychologist* describes "ordinary magic" resilience, highlighting responsive parenting and guidance as protective processes that foster positive self-regard and life satisfaction among youth exposed to adversity (doi:10.1037/0003-066X.56.3.227).

## Refined hypotheses
1. **Childhood class gradients**: Lower `classchild` remains a strong candidate predictor of higher adult depression and lower self-love (`I tend to suffer from depression (wz901dj)` and `I love myself (2l8994l)`), aligning with Reiss (2013).
2. **Emotional/verbal abuse pathways**: More negative scores on `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` (and the teen version) should correlate with worse adult well-being (higher `I tend to suffer from anxiety (npvfh98)-neg` and `I am not happy (ix5iyv3)-neg`), consistent with Norman et al. (2012).
3. **Parental guidance as resilience**: Higher parental guidance scores across both childhood and teen windows should predict elevated self-esteem and work satisfaction (`I love myself (2l8994l)` and `I am satisfied with my work/career life (z0mhd63)`), as described by Masten (2001).

## Reproducibility notes
- Descriptive statistics in this loop came from the Python commands above; re-running the same `pandas` script reproduces the reported means, SDs, and value counts.
- Maintain version control of this artifact and rerun data-intake scripts before the Pap phase so that any sample updates are captured.

# Loop 5 Literature Phase Notes

## Dataset update
- `childhoodbalancedpublic_original.csv` still comprises 14,443 responses and 718 columns, with repeated modules capturing the same respondent at different life stages (0-12, 13-18, current) so we can directly compare how adversity, guidance, and attitudes shift over time.
- Adult well-being is recorded with Likert items such as `I tend to suffer from anxiety (npvfh98)-neg` (mean = -0.83, SD = 2.03), `I tend to suffer from depression (wz901dj)` (mean = -0.41, SD = 2.09), `I love myself (2l8994l)` (mean = 0.61, SD = 1.86), and `I am not happy (ix5iyv3)-neg` (mean = 0.15, SD = 1.98), providing both positive and negative affect lenses that span the -3 to +3 scale.
- Religiosity data include 9,953 respondents reporting "No" to `Do you *currently* actively practice a religion? (902tbll)` and smaller groups reporting slight/moderate/serious practice, while `monogamy` choices cluster at 2.0 (8,329 cases) and 1.0 (3,429 cases) on the -2 to +2 preference scale.
- The childhood/adolescent modules include dozens of items about parental behaviors, purity teaching, media monitoring, relational warmth, verbal/emotional abuse, and childhood sexual abuse (both general yes/no follow-ups and detailed distress ratings during and after the events). These fine-grained exposures mirror the "networks of adversity" approach and create enough variation for latent exposure indices or additive scores.

## Literature update
- **Wood et al. (2020, *Journal of Epidemiology and Community Health*)** use three British longitudinal cohorts to link childhood warmth, economic stability, and educational opportunities to adult positive mental well-being, underscoring the dataset's potential for parsing protective versus harmful early-life influences in a large international online sample.
- **Pollmann et al. (2022, *Research on Child and Adolescent Psychopathology*)** map networks of adversity across childhood/adolescence and show that cumulative exposures better predict adult anxiety/depression than isolated incidents, which justifies modeling the multiple abuse/guidance/purity items as a system rather than single predictors.
- **Richter et al. (2018, *International Journal of Child Abuse & Neglect*)** follow boys in South Africa and demonstrate that childhood sexual abuse carries long-term penalties for adult mental health, paralleling our columns documenting incidence plus acute and later distress.
- **Kim et al. (2025, *npj Mental Health Research*, Global Flourishing Study)** find childhood relational and spiritual resources (including religious upbringing) are strong predictors of adult purpose and meaning, which resonates with our religion/practice modules and the broad well-being statements.

## Fresh candidate hypotheses
1. **Networks of childhood adversity**: Summed or latent scores from parental abuse, oversight/purity, and sexual abuse indicators (especially the 0-12 versus 13-18 windows) will explain more variance in adult anxiety/depression items than any single exposure, following Pollmann et al. (2022).
2. **Childhood sexual abuse severity**: Respondents with affirmative answers to the sexual-abuse modules—especially those reporting acute fear/pain during the events—will show worse adult well-being (higher depression/anxiety and `I am not happy`), extending Richter et al. (2018) to a broader, mixed-gender sample.
3. **Religiosity and guidance as resilience**: Early-life religious adherence and parental guidance scores should predict higher adult self-regard (`I love myself`) and life/work satisfaction, echoing the protective purpose findings of Kim et al. (2025) and the well-being correlates identified by Wood et al. (2020).

## Reproducibility notes
- All descriptive numbers in this loop derive from `python3 - <<'PY'` scripts that load `childhoodbalancedpublic_original.csv` with `pandas.read_csv`, compute `.describe()`, and call `.value_counts()` on the columns listed above; re-running those commands reproduces every statistic reported in this file.
- Literature context comes from the Semantic Scholar API searches `childhood family environment adult well-being`, `religious upbringing adult mental health`, and `childhood sexual abuse adult mental health longitudinal`; those `curl` commands remain in the shell history and can be re-executed to fetch updated metadata if needed.
