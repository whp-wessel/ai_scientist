# Analysis Notes (Loop 36)

## Loop 36 — pipeline rerun & sensitivity digest

### Sample & measurement
- Analytic sample n=14,400 after listwise dropping, with 1,196 gender-minority respondents (approx. 8.3%) and outcome SDs roughly 1.86 (self-love), 2.23 (romantic satisfaction), and 2.03 (anxiety); the parent-support composite (mean of verbal guidance and family humor) continues to show modest reliability (omega approx. 0.56), so we keep reporting both the aggregate and its components whenever precision allows.

### Hypothesis 1 (purity × parental support, ages 13-18)
- Self-love regression: parental support β=0.212 (d approx. 0.11, p<10⁻³³) and the purity₁₃₋₁₈ × support interaction remains negative (β approx. -0.040, p=0.005), producing the counter-intuitive simple slopes in `tables/simple_slopes.json` (purity slope approx. 0 at -1 SD support vs. approx. -0.08 at +1 SD, support slope approx. 0.253 at low purity vs. approx. 0.172 at high purity). High-support respondents therefore report steeper declines in self-love as adolescent purity messaging increases, while the support benefit is largest for those who recall lower purity demands.
- Romantic satisfaction regression: purity₁₃₋₁₈ main effect still negative (β approx. -0.111, d approx. -0.05, p=0.009) and the interaction likewise negative (β approx. -0.038, p=0.037), echoing the self-love pattern even though the slope magnitudes are smaller. Anxiety continues to show a non-significant positive purity association (β approx. 0.043, p=0.22) and no meaningful interaction or support slope.

### Hypothesis 2 (gender-minority moderation)
- Added interaction terms for both the 0-12 and 13-18 windows remain near zero for all outcomes (e.g., self-love difference ~0.067, SE approx. 0.059; romantic satisfaction difference ~0.068, SE approx. 0.072; anxiety difference <0.06), so we have no persuasive evidence that gender-minority status magnifies purity-culture harms in this sample.

### Sensitivity slices
- Restricting to respondents who no longer practice a religion (n approx. 9,931) keeps parental support positive and the purity×support term negative for romantic satisfaction (β approx. -0.058, p=0.009) while the self-love interaction attenuates toward zero, so the counterintuitive steepening effect is not solely driven by currently religious respondents.
- Adding aggregated childhood trauma/depression covariates leaves the key coefficients virtually unchanged (self-love interaction still approx. -0.040 with the same significance, romantic satisfaction interaction approx. -0.038), confirming the pattern is not an artifact of broader childhood adversity or depressive recall.
- Gender-minority subgroup regressions (trans n=295; nonbinary n=901) show that parental support remains positive for both groups, but the purity×support interaction coefficients are imprecise and switch signs depending on the subgroup, so we cannot parse heterogeneity within the gender-minority umbrella yet.

### Next steps
- With the registered models, diagnostics, and sensitivity slices rerun from scratch, we can now transition toward crafting the write-up and figures for the upcoming paper draft.

## Loop 35 — sensitivity runs

### No current religion sample (n=9,931)

### No current religion sample (n=9,931)
- Restricting to respondents who no longer practice a religion leaves the parental-support coefficient unchanged (self-love `β≈0.23`, d≈0.13; romantic satisfaction `β≈0.24`, d≈0.11) while the purity-13×support interaction is still negative for romantic satisfaction (`β≈-0.058`, p≈0.010) and near zero for self-love, showing that the counterintuitive steepening of purity’s negative slope is not driven by active religion participation.
- Anxiety retains the directionally positive purity-13 association (`β≈0.055`, p≈0.19) and no buffering by support emerges, which mirrors the full-sample estimates but now excludes currently religious respondents whose doctrinal investments might otherwise dominate the story.

### Additional childhood trauma/depression controls
- Adding the averaged 0–12/13–18 emotional-abuse and depression composites (standardized and entered on top of the registered covariate set) keeps the key moderating coefficient for self-love at `β≈-0.040`, p≈0.005, and leaves the romantic-satisfaction interaction and gender-minority slopes almost unchanged, so the purity/support pattern is not an artifact of broader trauma exposures.

### Gender-minority subgroups (trans n=295; nonbinary n=901)
- Running the Hypothesis 1 parental-support model separately for trans and nonbinary respondents shows that parental support remains a positive predictor of self-love in both subsamples (trans `β≈0.26`, p≈0.036; nonbinary `β≈0.25`, p<0.001), but the purity×support interaction and the purity main effect remain imprecise in these smaller cells, so we cannot distinguish differential moderation within the gender-minority umbrella yet.

### Outputs & next steps
- The full coefficient tables for these slices live in `tables/regression_results_no_current_religion.csv`, `tables/regression_results_with_trauma_controls.csv`, and `tables/gender_minority_subgroups.csv`, with the sample counts summarized in `outputs/sensitivity_overview.json`.
- With the registered sensitivity runs now scripted and documented, the next task is to fold them into the planned sensitivity section of the paper and move toward the writing phase while keeping this set of diagnostics reproducible.

## Loop 33 — baseline summary

### Sample characteristics
- Analytic sample: 14,400 respondents after listwise dropping (matching the pre-registered plan); 1,196 (8.3 %) fall into the gender-minority categories defined in the plan.
- Outcome SDs: `self_love` 1.86, `romantic_satisfaction` 2.23, `anxiety` 2.03. The `parent_support` composite has a McDonald’s omega-like estimate (2*r/(1+r)) of 0.56, flagging limited internal consistency between humor and guidance.
- Parent support composite reliability remains modest (ω≈0.56), so the planned sensitivity check that treats guidance and humor separately is still warranted before drawing stronger buffering claims.

### Hypothesis 1 (purity × parental support)
- Main effects: parental support is strongly positive for self-love (`β≈0.21`, d≈0.11, p<10⁻³³) and romantic satisfaction (`β≈0.19`, d≈0.09, p<10⁻¹⁸); purity (ages 13–18) is significantly negative only for romantic satisfaction (`β≈-0.11`, d≈-0.05, p≈0.009).
- Interaction pattern (self-love): the `purity13_support` term is negative (`β≈-0.040`, p≈0.005, d≈-0.022). Simple slopes show the purity‑self-love slope goes from ~0.000 (SE≈0.037) at -1 SD of support to -0.080 (SE≈0.036) at +1 SD; conversely, the parental support slope decreases with higher purity (0.253 → 0.172). Put bluntly, higher parental support sharpens the negative association between adolescent purity messaging and adult self-love, rather than buffering it. The same interaction is also significant for romantic satisfaction (`β≈-0.038`, p≈0.037) with the same direction.
- Marginal predictions in `figures/marginal_self_love.png` show that low-purity adolescents gain self-love rapidly with increasing parental support, while high-purity adolescents start from a slightly higher baseline but their slope with support is flatter and eventually crosses under the low-purity line.
- Detailed simple slopes pulled from `tables/simple_slopes.json` confirm the interaction: the purity slope evens out near zero at low levels of parent support (slope≈0.000, SE≈0.037) and becomes significantly negative (slope≈-0.081, SE≈0.036) at high support, while support itself has a stronger slope for low-purity respondents (≈0.253) than for high-purity respondents (≈0.172), reinforcing the counterintuitive crossover revealed by the marginal-plot figure.

### Hypothesis 2 (purity × gender-minority stress)
- Gender-minority status shows large main disadvantages (self-love `β≈-0.34`, anxiety `β≈0.13`), but the registered interactions remain null. The simple-slope table highlights that the slope difference between cis and gender-minority respondents for purity13 on self-love is only ≈0.067 (SE≈0.059) and directionally inconsistent across outcomes, so there is no robust evidence that purity-culture exposure disproportionately erodes their well-being in this sample.

### Diagnostics
- Variance inflation factors for the exposures and their moderators stay very low (≈1.00–1.10 across `tables/vif_summary.csv`), so the interaction coefficients are not inflated by collinearity even though the terms interact with their base scales.

### Limitations & open questions
- Parent-support composite has modest internal consistency; future work should test the two items separately (guidance/humor) or gather richer family climate measures.
- Interactions reverse the pre-registered buffering story: the significant negative moderation suggests adolescents who remembered high purity messages plus involved parents now report poorer adult self-love and romantic satisfaction, which might reflect complicated family investments rather than simple support. This counter-intuitive pattern deserves qualitative follow-up.
- Registered gender-minority moderation remains null; the large main effect of minority status hints at minority stress, but it does not appear to amplify purity-effects in this cross-sectional recall sample. Further work could explore whether specific purity doctrines (e.g., literal abstinence vs. moral double standards) or intersectional axes (race, class) shape the effect instead.
- The next phase should probe sensitivity to public-health-appropriate covariates (e.g., replacing the single parent-support composite with its two items, testing whether current religiosity interacts with purity, and sampling alternative subsamples) before we finalize the paper narrative.
