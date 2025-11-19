# Analysis Notes (Loop 32)

## Sample characteristics
- Analytic sample: 14,400 respondents after listwise dropping (matching the pre-registered plan); 1,196 (8.3 %) fall into the gender-minority categories defined in the plan.
- Outcome SDs: `self_love` 1.86, `romantic_satisfaction` 2.23, `anxiety` 2.03. The `parent_support` composite has a McDonald’s omega-like estimate (2*r/(1+r)) of 0.56, flagging limited internal consistency between humor and guidance.

## Hypothesis 1 (purity × parental support)
- Main effects: parental support is strongly positive for self-love (`β≈0.21`, d≈0.11, p<10⁻³³) and romantic satisfaction (`β≈0.19`, d≈0.09, p<10⁻¹⁸); purity (ages 13–18) is significantly negative only for romantic satisfaction (`β≈−0.11`, d≈−0.05, p≈0.009).
- Interaction pattern (self-love): the `purity13_support` term is negative (`β≈−0.040`, p≈0.005, d≈−0.022). Simple slopes show the purity‑self-love slope goes from ~0.000 (SE≈0.037) at −1 SD of support to −0.080 (SE≈0.036) at +1 SD; conversely, the parental support slope decreases with higher purity (0.253 → 0.172). Put bluntly, higher parental support sharpens the negative association between adolescent purity messaging and adult self-love, rather than buffering it. The same interaction is also significant for romantic satisfaction (`β≈−0.038`, p≈0.037, d≈−0.017) with the same direction.
- Marginal predictions in `figures/marginal_self_love.png` show that low-purity adolescents gain self-love rapidly with increasing parental support, while high-purity adolescents start from a slightly higher baseline but their slope with support is flatter and eventually crosses under the low-purity line.

## Hypothesis 2 (purity × gender-minority stress)
- Gender-minority status shows large main disadvantages (self-love `β≈−0.34`, anxiety `β≈0.13`), but no registered interaction reaches significance. The simple-slope output shows the purity × gender-minority differences are small (e.g., `Δslope≈0.067`, SE≈0.059 for purity13 × self-love) and not distinguishable from zero, so we cannot claim privileged vulnerability of gender minorities in this dataset.

## Limitations & open questions
- Parent-support composite has modest internal consistency; future work should test the two items separately (guidance/humor) or gather richer family climate measures.
- Interactions reverse the pre-registered buffering story: the significant negative moderation suggests adolescents who remembered high purity messages plus involved parents now report poorer adult self-love and romantic satisfaction, which might reflect complicated family investments rather than simple support. This counter-intuitive pattern deserves qualitative follow-up.
- Registered gender-minority moderation remains null; the large main effect of minority status hints at minority stress, but it does not appear to amplify purity-effects in this cross-sectional recall sample. Further work could explore whether specific purity doctrines (e.g., literal abstinence vs. moral double standards) or intersectional axes (race, class) shape the effect instead.
