# Pre-Analysis Plan

status: frozen
registry_url: 
freeze_commit: 5939f2931aeb78069b38b609597d65a377879481

## Research questions
- RQ1: How does exposure to purity-culture messaging during the two developmental windows (ages 0–12 vs. 13–18) link to adult self-love and romantic satisfaction, and can early parental support buffer any negative effects?
- RQ2: Does purity-culture conditioning have a disproportionately adverse association with adult anxiety and self-love for gender-minority respondents (transgender or nonbinary) compared to cisgender respondents?

## Literature & Theory

- **Purity culture measurement.** Klement, Sagarin, and Skowronski (2022) validate a Purity Culture Beliefs construct in *Sexuality & Culture* (DOI `10.1007/s12119-022-09986-2`), demonstrating that items tapping abstinence, shame, and moral boundaries load together while remaining distinguishable from broader rape-culture attitudes. This gives us confidence that the purity variables in the dataset map onto a coherent psychological syndrome rather than a collection of unrelated memories.
- **Parental warmth as a buffer.** Family-process research repeatedly finds that parental guidance and humor/affection attenuate links between stressful childhood exposures and adolescent/adult anxiety or depression (Franck & Buehler 2007, *Journal of Family Psychology*, DOI `10.1037/0893-3200.21.4.614`; Zheng & McMahon 2019, *Journal of Clinical Child & Adolescent Psychology*, DOI `10.1080/15374416.2019.1678166`). These studies justify our focus on parental guidance/humor as moderators of purity-culture effects on well-being.
- **Gender-minority stress in religious contexts.** Conservatively religious gender-minority individuals report more internalizing symptoms, in part because conservative teachings often pathologize non-cis identities (Skidmore, Sorrell, & Lefevor 2022, *Journal of Homosexuality*, DOI `10.1080/00918369.2022.2087483`). Lekwauwa, Funaro, & Doolittle’s systematic review (2022, *Journal of Gay & Lesbian Mental Health*, DOI `10.1080/19359705.2022.2107592`) further catalogs religion/spirituality distress among transgender adolescents, echoing earlier work linking family rejection that is often faith-motivated to anxiety and suicidality in sexual-minority youth (Ryan et al. 2009, *Pediatrics*, DOI `10.1542/peds.2009-1527`). Together, these sources establish that purity-culture messages are plausible sites of minority stress for gender-minority respondents.

## Hypotheses
1. **Purity culture + parental support.** Drawing on Klement, Sagarin, & Skowronski (2022, *Sexuality & Culture*, DOI `10.1007/s12119-022-09986-2`) for a validated purity-culture belief scale and the buffering literature on parental warmth (Franck & Buehler 2007, *Journal of Family Psychology*, DOI `10.1037/0893-3200.21.4.614`; Zheng & McMahon 2019, *Journal of Clinical Child & Adolescent Psychology*, DOI `10.1080/15374416.2019.1678166`), higher purity-culture scores—especially during adolescence (13–18)—predict lower values on the adult self-love and romantic satisfaction anchors, but the slope is attenuated for respondents who report strong parental guidance/family humor during the same window. We expect the adolescent purity slope to be the most consequential, so we will anchor our interpretation on a 1-SD shift in `during ages *13-18*` purity and translate that into Cohen’s d equivalents (roughly 0.10–0.20) for key outcomes. We will also compute the empirical reliability of the parental support composite (guidance + humor) and, if Cronbach’s α falls below 0.70, report both items separately while keeping the moderation interpretation consistent.
2. **Purity culture × gender-minority stress.** In line with Skidmore, Sorrell, & Lefevor (2022, *Journal of Homosexuality*, DOI `10.1080/00918369.2022.2087483`) and Lekwauwa, Funaro, & Doolittle’s 2022 systematic review in *Journal of Gay & Lesbian Mental Health* (DOI `10.1080/19359705.2022.2107592`) documenting religion/spirituality distress among transgender adolescents, purity-culture exposure will show larger negative associations with self-love and larger positive associations with anxiety among gender-minority respondents than among cisgender respondents. We will estimate separate interaction terms for the 0–12 and 13–18 windows and interpret the differential slopes at ±1 SD of purity for gender-minority respondents, again translating coefficients into Cohen’s d (per hypothesis) so that the interaction can be read as a standardized moderator effect.

## Data & sample
- Source: `childhoodbalancedpublic_original.csv`, 14,443 respondents × 718 columns.
- We will keep respondents with non-missing values on the targeted exposures, moderators, outcomes, and covariates (list below) and document the resulting sample size. No survey weights are supplied, so we proceed with unweighted OLS while reporting descriptive demographics.
- Gender-minority status is coded as any respondent who selects “Nonbinary/other” (assigned male or female at birth) or “Man/Woman (trans)” in `Which category fits you best? (4790ydl)`; all other responses are coded as cis gender.
- After filtering, we expect approximately 14,400 respondents in the analytic sample and will record the exact count plus exclusions in `outputs/sample_summary.json` (or a similar artifact) so we can later justify the denominator for each estimation. We will also log the pre-standardization distribution of the purity items so that we can confirm the SDs used for interpretation match the observed variability.

## Variables
### Dependent variables (Y)
- `I love myself (2l8994l)` (continuous, −3…+3).
- `I am satisfied with my romantic relationships (hp9qz6f)` (continuous, −3…+3).
- `I tend to suffer from anxiety (npvfh98)-neg` (continuous, −3…+3, higher = more anxiety).
Each hypothesis will be evaluated separately for each outcome; effect sizes will be reported per 1-SD increase in the exposure or interaction term.

### Key exposures (X)
- `during ages *0-12*:  taught a purity culture that encouraged abstinance/waiting until marriage (wgbq7hv)`
- `during ages *13-18*:  taught a purity culture that encouraged abstinance/waiting until marriage (wxgm38d)`
We will standardize each exposure to mean zero and SD one within the analytic sample.

### Moderators / interaction terms
- Family support: `during ages *13-18*: Your parents gave useful guidance (dcrx5ab)` and `during ages *13-18*:  family/culture had hilarious joking... (i1g8u4j)` to index parental warmth/family humor alongside purity exposures. (We may average to a composite or examine each separately but will pre-register whichever returns the stronger preliminary reliability.)
- Gender-minority indicator (non-cis vs. cis) interacts with both purity windows to capture differential stress accumulation.

### Covariates
- Age (`selfage`), education (`education`), current socioeconomic status (`classcurrent`, `networth`), childhood class proxies (`classchild`, `classteen`).
- Current religious practice (`Do you *currently* actively practice a religion? (902tbll)`), the religiosity intensity anchor (`In your childhood, how important was adherence to the religion? ... (xvlgpp5)`), and current external religiosity (`externalreligion`).
- Childhood co-occurring adversities (e.g., `during ages *0-12*: Parents divorcing/separating (jib24si)` and `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)`) to ensure purity culture estimates are not solely proxies for family disruption.
- Gender identity (full categorical indicator) so cisgender comparisons adjust for baseline differences besides the binary gender-minority variable.

## Estimation strategy
- Primary models will be OLS regressions with HC3 robust standard errors:

```
Y = β0 + β1&#8208;purity13 + β2&#8208;(parental_support) + β3&#8208;(purity13 × parental_support) + β4&#8208;purity0 + γX + ε
```

for Hypothesis 1, and replace the interaction term with `purityX × gender_minority` for Hypothesis 2 (testing both purity 0–12 and 13–18 windows in separate specifications). We will center all continuous covariates (including purity and support) at their sample means before multiplying to aid interpretability.
- We will report coefficient estimates, standard errors, 95% confidence intervals, and Cohen’s d equivalents when beneficial. Marginal effects plots at ±1 SD of moderators will accompany key findings.
- Results will be presented separately for each dependent variable; we will flag any consistent patterns across outcomes but interpret each in its respective social-psychological context. No p-value threshold is pre-specified, but results will be discussed in terms of effect size magnitude and uncertainty rather than binary significance.
- Covariates include the gender-category dummies (using “Woman (cis)” as the reference) so that the gender-minority interaction is not conflated with main differences between cis men/women and the rest of the sample. We will also compute variance inflation factors (VIFs) for the main exposures and moderators to report that multicollinearity is not driving the interaction estimates.

## Interpretation & effect size translation
- All continuous exposures and moderators are standardized so that each coefficient represents a one-standard-deviation shift, which aids comparison across the self-love, romantic satisfaction, and anxiety anchors. We will accompanying a Cohen’s d equivalent and the raw predicted difference between individuals at −1 SD vs. +1 SD on the exposure/marginalized condition (e.g., high purity & low support vs. low purity & high support) so interpretations stay grounded in substantive group differences.
- Marginal effects plots (e.g., parental support × purity for self-love) will include 95% confidence ribbons; we will comment on the range of uncertainty and note when the confidence interval overlaps zero even if the point estimate matches expectations.

## Missing data & sample construction
- Complete-case analysis across the variables listed above. We will report the number and percentage of respondents excluded due to missingness and compare excluded vs. included cases on age, gender identity, and purity scores.
- If missingness patterns raise concerns, we will explore multiple imputation as a sensitivity analysis.
- In addition to the overall exclusion count, we will detail which key exposures or covariates are most affected by missingness so that we can transparently defend our complete-case sample. Any imputed models will share the same predictor set and use chained equations with 10 imputations, mirroring the complete-case covariates for comparability.

## Sensitivity checks
- Re-estimate all models excluding respondents who report a current religion to test whether the purity-culture effects persist outside formal religious engagement.
- Re-estimate with additional controls for childhood emotional abuse (`during ages 0-12`: `parents verbally emotionally abused you (mds78zu)`) and depression indicators to ensure the purity coefficient is not conflated with broader trauma.
- Test whether trans vs. nonbinary subsamples (among the gender-minority group) show consistent effect patterns, while reporting the smaller cell sizes transparently.

## Reproducibility
- All data cleaning, variable construction, and modeling steps will be scripted in `analysis/analysis_pipeline.py` (or a Jupyter notebook to be added later) with explicit seeds for any random operations. The final paper will include summary tables generated directly from these scripts to ensure replication.
- We will commit the `analysis/analysis_pipeline.py` version used for the PAP alongside the `outputs/sample_summary.json` and `tables/regression_results.csv` so that the entire analytic pipeline (data → table → figure) can be rerun with the same `figures/marginal_self_love.png` output. Those figures will be embedded via Tectonic in the final LaTeX paper so that reproduction requires only rerunning the script and building the TeX.
