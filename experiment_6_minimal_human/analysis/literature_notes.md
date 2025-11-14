# Literature Notes

## Dataset overview
- **Sample**: 14,443 respondents across 718 question columns derived from the balanced-childhood public survey.
- **Demographics**: Ages range from 18 to 75 (mean 30.4, SD 10.2); detailed variables capture gender identity, ethnicity, education, class, net worth, and religious background.
- **Psychosocial measurements**: Many Likert-type items coded from −3 to 3 describe adulthood well-being (e.g., anxiety, depression, relationship satisfaction, life satisfaction) and childhood experiences (e.g., parental guidance, family humor, media restrictions, teachings about purity).
- **Key outcome candidates**: adult emotional health (e.g., `I tend to suffer from anxiety (npvfh98)-neg`, `I tend to suffer from depression (wz901dj)`, and `In the past 4 weeks, you've had difficulty accomplishing things due to emotional issues (kd4qc3z)`), relational satisfaction (`I am satisfied with my romantic relationships (hp9qz6f)`), and self-regard (`I love myself (2l8994l)`).
- **Key exposure candidates**: childhood family cohesion/guidance (`during ages 0-12: Your parents gave useful guidance (pqo6jmj)` / `during ages 13-18: Your parents gave useful guidance (dcrx5ab)`), family culture (e.g., joking or stress), and religiosity variables (`Do you currently actively practice a religion? (902tbll)`, `religion`, `Religionchildhood`, `externalreligion`).
- **Coding notes**: Many scale items present negative/positive labels (e.g., columns ending with `-neg`); the dataset will require consistent recoding (higher values representing higher endorsement) and transparent handling of missing data.

## Relevant literature
- Cobb et al. (2024), *Perceived childhood family cohesiveness prior to deployment prospectively moderates risk for war-zone psychopathology in theater among deployed U.S. soldiers* (Psychological Trauma). This recent peer-reviewed study shows that greater perceived childhood family cohesion predicts lower psychopathology in later high-stress environments, which supports examining childhood socialization and adult emotional health in the current dataset.
- Koenig (2012), *Religion, Spirituality, and Health: The Research and Clinical Implications* (ISRN Psychiatry). This widely cited review documents robust associations between religiosity/spirituality and mental well-being, suggesting that current or remembered religious engagement may correlate with adult emotional outcomes in the survey.

## Next-phase considerations
- Prioritize defining reproducible variable construction for exposures (e.g., recoding `pqo6jmj`, `dcrx5ab`, the multi-level religiosity question) and outcomes (e.g., standardizing anxiety/depression items).
- Outline covariates for later models (age, gender/cis indicators, class, education, parental socioeconomic status from `classchild`/`classteen`).
- Document data-cleaning steps (missingness thresholds, scale direction) so future loops can reproduce preprocessing.
