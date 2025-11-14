# Hypothesis Exploration Notes

## Candidate hypotheses grounded in the dataset and literature

1. **Childhood emotional/verbal abuse predicts adult psychological distress.**
   - Rationale: The dataset includes `during ages 0-12` and `during ages 13-18` indicators for parental verbal/emotional abuse. The adult well-being items (`I tend to suffer from depression`, `I am not happy`, `I love myself`, etc.) provide direct outcomes to assess. Felitti et al. (1998) document a robust link between childhood abuse/household dysfunction and adult depression and negative health outcomes (Am. J. Prev. Med., DOI:10.1016/S0749-3797(98)00017-8).
   - Candidate operationalization: average of the two abuse items as the key independent variable; adult depression self-ratings as the dependent variable.

2. **Perceived current social support mitigates the relationship between childhood abuse and current affect.**
   - Rationale: `In general, people in my current social circles tend treat me really well` (tmt46e6) can index current support. The dataset allows testing whether higher support associates with better self-esteem/satisfaction and whether it moderates the abuse → well-being link. Cohen & Wills (1985) established the stress-buffering hypothesis for social support and mental health (Psychological Bulletin, DOI:10.1037/0033-2909.98.2.310).
   - Candidate operationalization: treat `tmt46e6` as support measure; examine interaction with abuse index on depression/happiness outcomes.

3. **Current religiosity/spiritual engagement is linked to higher positive affect among adults with childhood adversity.**
   - Rationale: The survey captures religious practice (`Do you currently actively practice a religion?`) and perceived religion moderation; prior work (Jung 2017) shows religious salience/spirituality buffer the negative impact of childhood abuse on positive affect (Res. Aging, DOI:10.1177/0164027516686662).
   - Candidate operationalization: ordinal coding of current religiosity (0=No, 1=Yes, slightly, 2=Yes, moderately, 3=Yes, very seriously) as predictor; examine its association with positive affect (e.g., `I love myself`, `I am satisfied with my romantic relationships`) controlling for abuse.
