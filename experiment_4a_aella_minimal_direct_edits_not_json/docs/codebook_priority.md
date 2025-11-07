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
