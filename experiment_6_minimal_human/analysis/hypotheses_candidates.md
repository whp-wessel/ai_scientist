# Hypothesis Exploration Notes

## Candidate hypotheses grounded in the dataset and literature

1. **Childhood emotional/verbal abuse predicts adult psychological distress.**
   - Rationale: The dataset includes `during ages 0-12` and `during ages 13-18` indicators for parental verbal/emotional abuse, while adult scales (`I tend to suffer from depression`, `I tend to suffer from anxiety`, `I am not happy`, `I love myself`) capture internalizing symptoms. Felitti et al. (1998) demonstrate a graded ACE-impact on adult depression, anxiety, and mortality (Am. J. Prev. Med. 14(4):245–258, DOI:10.1016/S0749-3797(98)00017-8), providing a peer-reviewed anchor for this pathway.
   - Candidate operationalization: Collapse the two abuse items into a single mean index (or treat them separately) and regress adult depression/anxiety outcomes on this exposure while controlling for core covariates (age, gender, classchild).

2. **Perceived current social support attenuates the adverse effect of childhood abuse on wellbeing.**
   - Rationale: The literal social support item (`In general, people in my current social circles tend to treat me really well` 71mn55g) has near-complete coverage (14,054 respondents) and can be modeled as either a main effect or moderator. Cohen & Wills (1985) provide the foundational stress-buffering model for social support and mental health (Psychol. Bull. 98(2):310–357, DOI:10.1037/0033-2909.98.2.310), which justifies testing whether current positive circles dampen the abuse → depression/anxiety link.
   - Candidate operationalization: Include the social support score as a moderator in models predicting `I tend to suffer from depression` or `I am not happy` from the abuse index, controlling for demographic covariates and testing interaction terms.

3. **Current religiosity/spiritual engagement correlates with higher positive affect, particularly among those with childhood adversity.**
   - Rationale: The rich ordinal religiosity variable (9,958 “No” to 774 “Yes, very seriously”), taken alongside Koenig, King, & Carson’s (2012) Handbook of Religion and Health (Oxford Univ. Press) and Pargament, Koenig, & Perez (2000) findings on religious coping (J. Clin. Psychol. 56(4):519–543), supports expecting religious engagement to serve as a protective resource for self-esteem and relational satisfaction, even when adversity is present.
   - Candidate operationalization: Model positive affect outcomes (`I love myself`, `I am satisfied with my romantic relationships`) on the ordinal religiosity measure and test whether religiosity interacts with the abuse index or parental guidance scales to predict higher wellbeing.

4. **Higher childhood socio-economic standing and supportive guidance predict better adult economic and subjective outcomes.**
   - Rationale: The dataset supplies class tiers across childhood, teenage, and current periods (`classchild`, `classteen`, `classcurrent`), plus net worth and parental guidance (`pqo6jmj`, `dcrx5ab`). Conger & Donnellan (2007) review the impact of economic pressure across the family life course (Annu. Rev. Psychol. 58:175–199), and Kim et al. (2025) demonstrate cross-national continuities between childhood resources and adult purpose (npj Mental Health Research 4(1): DOI:10.1038/s44184-025-00127-9), together suggesting SES and positive parenting should correlate with both objective economic status and subjective wellbeing.
   - Candidate operationalization: Test whether higher `classchild`/`classteen` predict `classcurrent`, `networth`, and wellbeing scales, and examine whether positive parenting (guidance) or lack of purity culture messaging moderates these relationships to reveal resilience pathways.
