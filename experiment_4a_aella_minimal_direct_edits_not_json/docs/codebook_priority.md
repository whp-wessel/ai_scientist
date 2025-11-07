# Priority Variable Codebook — Loop 001

Generated from `childhoodbalancedpublic_original.csv` on 2025-11-07 (seedless deterministic read via pandas). Descriptive statistics are stored in `tables/loop001_numeric_descriptives.csv` and `tables/loop001_categorical_counts.csv`.

## H1 · Childhood Emotional Abuse → Adult Depression

### Exposure: Parental emotional abuse (ages 0–12)
- **Column**: `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` → stored raw as a 7-point Likert integer scaled from -3 (“strongly disagree”) to +3 (“strongly agree”).
- **Coverage**: 14,426 non-missing responses (99.9% of sample); mean = -0.225, SD = 2.41, range [-3, 3].
- **Interpretation**: Distribution skews negative (25th percentile = -3), indicating most respondents deny experiencing verbal/emotional abuse; positive tail (max = 3) captures the exposed group for H1 contrasts.

### Outcome: Adult depression self-assessment
- **Column**: `I tend to suffer from depression (wz901dj)`; same -3 to +3 Likert structure with 14,438 valid records (≈100% coverage), mean = -0.407, SD = 2.09.
- **Notes**: Will be standardized (z) only if needed; current coding already symmetric with intuitive direction (higher = worse depression).

## H2 · Parental Guidance → Adult Self-Love

### Exposure: Childhood parental guidance
- **Column**: `during ages *0-12*: Your parents gave useful guidance (pqo6jmj)`.
- **Scale & coverage**: 14,431 non-missing (99.9%), mean = 0.625, SD = 2.00, range [-3, 3]; higher scores already reflect more guidance.

### Outcome: Self-love
- **Column**: `I love myself (2l8994l)`; 14,436 responses (≈100%), mean = 0.613, SD = 1.86, range [-3, 3].
- **Comment**: Both exposure/outcome share the balanced 7-point scale, enabling direct OLS with optional standardization to ease interpretation.

## H3 · Childhood Class → Adult Net Worth

### Exposure: Childhood class
- **Columns**: numeric `classchild` (0–6) and categorical prompt `When you were a child (0-12 years old), your family was (hxyr6oa)`.
- **Category map** (`hxyr6oa` counts from `tables/loop001_categorical_counts.csv`):
  - Underclass (very poor): 807 (5.6%)
  - Low class: 2,021 (14.0%)
  - Lower-middle class: 3,559 (24.6%)
  - Middle class: 4,412 (30.6%)
  - Upper-middle class: 2,866 (19.9%)
  - Upper class: 636 (4.4%)
  - Elite class (very rich): 135 (0.9%)
- **Numeric summary**: `classchild` mean = 2.62, SD = 1.28, min 0, max 6, no missing.

### Outcome: Current net worth
- **Column**: `Your CURRENT net worth is closest to (nhoz8ia)` with 10 ordered buckets (see `tables/loop001_categorical_counts.csv`).
- **Top categories**: `$100,000` (26%), `$10,000` (24%), `$1,000,000` (14%). Lowest-frequency category is `$-1,000 (in debt)` with 236 respondents (>n=10 privacy threshold).
- **Analysis note**: Treat as ordered outcome for primary spec (ordered logit) plus dichotomies (≥$100k, ≥$1M) as exploratory.

## H4 · Religiosity → Anxiety Frequency

### Exposure: Current religious practice
- **Column**: `Do you *currently* actively practice a religion? (902tbll)`.
- **Response distribution**: No (68.9%), Yes slightly (17.8%), Yes moderately (7.9%), Yes very seriously (5.4%); 0% missing.
- **Coding plan**: Convert to ordinal scale (0–3) and, for robustness, a binary indicator (any practice vs. none).

### Outcome: Anxiety frequency
- **Column**: `I tend to suffer from anxiety (npvfh98)-neg`.
- **Scale**: -3 to +3 (higher = worse anxiety after accounting for “-neg” suffix); coverage 14,437 (≈100%), mean = -0.827, SD = 2.03.
- **Handling**: Keep as continuous for mean-difference tests; examine need for re-flipping pending confirmation that “-neg” already reversed (current direction aligns with label: higher = more agreement with “suffer from anxiety”).

## Shared Measurement Notes
- All Likert items share a symmetric seven-point coding already centered at zero with unit steps; no additional rescaling performed yet.
- Missingness across priority variables is ≤0.12%, so listwise deletion is viable for exploratory work. Missingness diagnostics will be repeated if additional covariates introduce >5% loss.
- No survey design variables (weights, strata, clusters) were detected when scanning column headers for the strings “weight”, “strata”, or “cluster”; see `analysis/pre_analysis_plan.md` for the SRS justification.

## Teen Exposures & Adjustment Covariates — Loop 002 Extension

Descriptive summaries are exported to `tables/loop002_teen_covariate_numeric.csv` (numeric Likert/ordinal variables) and `tables/loop002_teen_covariate_categorical.csv` (public-safe counts, n≥10 cells). These variables support teen-period contrasts and the adjustment set planned for OLS/logit prototypes.

### Teen Emotional Abuse (Ages 13–18)
- **Column**: `during ages *13-18*: your parents verbally or emotionally abused you (v1k988q)`.
- **Coverage**: 14,426 valid responses (missing 0.12%).
- **Distribution**: Mean = -0.045, SD = 2.41 on the -3→3 Likert scale; mirrors the childhood exposure but shifts slightly toward neutrality for the teen years.

### Teen Parental Guidance
- **Column**: `during ages *13-18*: Your parents gave useful guidance (dcrx5ab)`.
- **Coverage**: 14,431 valid responses (missing 0.08%).
- **Distribution**: Mean = 0.283, SD = 2.08; still skewed positive but less so than the 0–12 measure, suggesting greater heterogeneity in adolescence.

### Teen Socioeconomic Class
- **Ordinal scale**: `classteen` (0–6) has full coverage with mean 2.76 (SD 1.25), indicating a slight upward shift relative to childhood class (mean 2.62).
- **Categorical prompt**: `When you were a teen (13-18 years old), your family was (uky2ksa)` remains balanced: Middle class (32%), Upper-middle (23%), Lower-middle (23%), Low (12%), Upper (5%), Underclass (4%), Elite (0.8%). All cells exceed the n≥10 disclosure threshold.

### Current Class & Demographics (Adjustment Set)
- **Current class**: `classcurrent` spans 0–6 with mean 3.02 (SD 1.26), reflecting slight upward mobility relative to teen status.
- **Age**: `selfage` (18–75) averages 30.4 years (SD 10.2).
- **Education**: Seven-point attainment scale (`education`) centers at 4.38 (SD 1.61), suggesting most respondents completed at least some college.
- **Gender identity**: `gendermale` (binary) has mean 0.57 (57% identifying as male); `cis` averages 0.92, indicating 92% cis-identifying respondents. Both variables are fully observed.

These additions complete the shared adjustment set for multivariate models and document the teen-period analogues of the primary exposures.
