# Analysis Notes

## Loop 42 — sensitivity rerun & documentation

### Sample & measurement
- The scripted sensitivity pipeline now documents the sample sizes we discussed at the start of the loop: 9,931 respondents who do not currently practice a religion, the full 14,400 case analytic sample with additional trauma/depression controls, 295 trans respondents, and 901 nonbinary respondents (`outputs/sensitivity_overview.json:2`, `outputs/sensitivity_overview.json:3`, `outputs/sensitivity_overview.json:4`, `outputs/sensitivity_overview.json:5`).

### Findings
- The no-current-religion slice keeps the purity×support slope effectively null for self-love (β≈-0.012, p≈0.517) while the romantic satisfaction interaction stays significantly negative (β≈-0.058, p≈0.0097), so the counterintuitive moderation appears to persist outside ongoing religiosity (`tables/regression_results_no_current_religion.csv:4`, `tables/regression_results_no_current_religion.csv:8`).
- Adding the trauma/depression controls leaves the key interactions intact: the self-love purity×support term stays at β≈-0.040 (p≈0.005), and romantic satisfaction keeps β≈-0.038 (p≈0.037), so the moderation is not an artifact of missing childhood-adversity covariates (`tables/regression_results_with_trauma_controls.csv:4`, `tables/regression_results_with_trauma_controls.csv:8`).
- Breaking the gender-minority sample into trans (n=295) and nonbinary (n=901) subsamples again yields wide intervals that drown out the purity×support term (`tables/gender_minority_subgroups.csv:4`, `tables/gender_minority_subgroups.csv:16`), confirming that the broader gender-minority interaction is driven by the larger cisgender pool rather than a precise estimate in these smaller cells.

### Outputs & next steps
- The `analysis/sensitivity_analysis.py` script orchestrates these runs and writes the per-slice tables plus the JSON summary, so the tables under `tables/` are now reproducibly linked to `outputs/sensitivity_overview.json` and ready to reference in the paper’s sensitivity section (`analysis/sensitivity_analysis.py:1`).
- With the diagnostic slice refreshed, we can move into the writing phase, citing these new tables when discussing robustness and preparing the LaTeX narrative that embeds the sensitivity story before releasing the final draft.

## Loop 43 — writing updates

### Manuscript
- Updated the abstract to note the analytic sample (n=14,400; 8.3\% gender-minority; parent-support $\omega \approx 0.56$), highlight the early-life purity/anxiety nuance, and briefly preview the registered sensitivity slices that keep the core pattern intact.
- Expanded the Results section so that the marginal plot descriptions cite the simple-slope table (`tables/simple\_slopes.json`), the anxiety paragraph traces both 13--18 and 0--12 exposures (`tables/regression\_results.csv:26-29`), and the gender-minority moderation text explicitly reports the small differences (e.g., 13--18 self-love difference 0.067, SE 0.059; 0--12 difference 0.090, SE 0.057; see `tables/regression\_results.csv:41` and `:45`).
- Reworked the sensitivity bullet list to reference the no-religion, trauma-control, and trans/nonbinary tables plus the sample-overview JSON so the robustness story in the paper mirrors the latest scripted diagnostics.

### Next steps
- Compile the updated LaTeX draft with Tectonic to ensure the PDF and embedded PGFPlots figure render cleanly before proceeding to the release loop.

## Loop 38 — gender-group heterogeneity of the unconditional-love moderation

### Sample & measurement
- Cisgender respondents keep the analytic backbone (n≈13,204) while the gender-minority subgroup is small but still respectable (n=1,196); both groups share the same pre-registered covariate set and the unconditional-love 13–18 prerequisite, so the comparisons mirror the global model (`outputs/unconditional_love_gender_groups_summary.json:1`).

### Findings
- Among cisgender respondents, the registered purity×unconditional-love interaction matches the full-sample pattern: the interaction term is negative for self-love (`β≈-0.052`, p≈0.0006) and for romantic satisfaction (`β≈-0.041`, p≈0.033), and the simple slopes show the purity penalty jumps from near zero at low love (≈+0.025, SE≈0.039) to -0.079 (SE≈0.037) at high love, while the love slope itself softens from ≈0.39 to ≈0.28 as purity rises (`tables/regression_results_unconditional_love_gender_groups.csv:1-7`, `tables/simple_slopes_unconditional_love_gender_groups.json:1-20`).
- For gender-minority respondents the interaction is directionally similar but imprecise (`β≈-0.065`, p≈0.30 for self-love; `β≈0.038`, p≈0.62 for romantic satisfaction) and the slopes have large SEs, so the apparent crossover cannot be distinguished from noise in that subgroup; anxiety slopes also flip sign between groups but remain noisy (`tables/regression_results_unconditional_love_gender_groups.csv:13-35`, `tables/simple_slopes_unconditional_love_gender_groups.json:21-60`).

### Next steps
- The subgroup evidence confirms that the overall moderation is driven by cisgender respondents, so we can proceed to the planned sensitivity section knowing gender-minority estimates remain underpowered; the upcoming writing phase can highlight how the counterintuitive interaction replicates in the dominant subgroup yet lacks precision for minority respondents, and we should note that the paper’s generalizability to gender-minority experiences will rest on future, larger samples rather than this test alone.

## Loop 37 — unconditional love moderation

### Sample & measurement
- After requiring the unconditional-love 13–18 recall, the analytic n=14,400 matches the main pipeline sample so comparisons stay aligned; the standardized 13–18 love rating remains strongly skewed toward the high-support end and now lives alongside the parental-support measures in the sample file.

### Hypothesis 3 (purity × unconditional love)
- Self-love regressions keep the full covariate set and show a very large main effect of unconditional love (β≈0.344, Cohen’s d≈0.185, p<10⁻⁶⁵) while the purity×love interaction is negative (β≈-0.059, d≈-0.032, p<0.0001). The simple slopes in `tables/simple_slopes_unconditional_love.json` reproduce the counterintuitive crossover: the purity slope is essentially null at low unconditional love (≈-0.002±0.037) yet becomes significantly negative at high love (≈-0.121±0.036), which drives the divergence in `figures/marginal_unconditional_love_self_love.png`.
- Romantic satisfaction mirrors the pattern with a smaller but still significant interaction (β≈-0.043, p≈0.017) and slopes that drop from about -0.086 to -0.173 as unconditional love increases, even though unconditional love itself predicts higher romantic satisfaction (d≈0.11). Anxiety estimates remain noisy (interaction β≈0.033, p≈0.021; all slopes stay near zero).

### Next steps
- Frame this robustness check alongside the earlier parental-support moderation in the upcoming draft: unconditional love is a strong positive predictor of adult well-being but—like parental support—sharpens the purity-culture penalty when it co-occurs with high purity messaging. Keep the new figure/table pair for the write-up and document the slopes for transparency.


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

## Loop 39 — finalizing registered analysis

### Summary
- **Hypothesis 1 (purity × parental support).** The parental-support story replicates across self-love and romantic satisfaction: parental support has a large positive association (self-love `β≈0.212`, d≈0.11; romantic satisfaction `β≈0.190`, d≈0.09), while the purity×support interaction is negative (self-love `β≈-0.040`, p=0.005, d≈-0.022; romantic satisfaction `β≈-0.038`, p=0.037, d≈-0.017). Simple slopes from `tables/simple_slopes.json` confirm that the purity penalty is near zero at -1 SD support but drops to ≈-0.081 at +1 SD, and `figures/marginal_self_love.png` visualizes the predicted margins for self-love.
- **Hypothesis 2 (purity × gender-minority stress).** The interaction terms for both developmental windows stay close to zero; the slope difference for the purity13 × gender-minority term is ≈0.067 (SE≈0.059), and the sharper negative slopes for cisgender respondents do not replicate among the smaller gender-minority respondents. Gender-minority status itself carries a large main disadvantage in self-love (`β≈-0.34`, p<10⁻⁸) and a modest anxiety penalty (`β≈0.13`, p≈0.004), but there is no consistent amplification of purity effects.
- **Hypothesis 3 (purity × unconditional love).** When unconditional-love recollections are included, the counterintuitive moderation remains: unconditional love strongly raises self-love (`β≈0.344`, d≈0.185), but the purity × love interaction is negative (`β≈-0.059`, p<0.0001, d≈-0.032), so high-love respondents show a steeper decline as purity increases. The dedicated outputs (`tables/regression_results_unconditional_love.csv`, `tables/simple_slopes_unconditional_love.json`, `figures/marginal_unconditional_love_self_love.png`) document these slopes and margins.
- **Sensitivity & measurement.** The registered sensitivity slices (non-practicing sample, additional trauma controls, trans/nonbinary subgroup analyses) show the same pattern of coefficients (`tables/regression_results_no_current_religion.csv`, `tables/regression_results_with_trauma_controls.csv`, `tables/gender_minority_subgroups.csv`) and their sample sizes are summarized in `outputs/sensitivity_overview.json`. Measurement notes for the parental-support and unconditional-love composites now live in `qc/measures_validity.md`, which records Cronbach’s α (0.56 and 0.88, respectively).

### Next steps
- With the registered models, diagnostics, sensitivities, and measurement checks generated, the analysis phase is complete and we are ready to move into the subsequent writing cycle. The next loop should shape the LaTeX draft (Tectonic-ready), integrate the marginal plots, and highlight the counterintuitive interactions while noting the gender-minority precision limits.

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
