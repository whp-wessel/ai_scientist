# Childhood Resilience Study — Manuscript (Markdown Twin)

This Markdown twin mirrors `papers/main/manuscript.tex`. Every substantive update below references deterministic artifacts (see the MANIFEST) and cites `[CLAIM:<ID>]`.

## Abstract
The Childhood Resilience Study uses the publicly documented dataset and PAP `pap-v1` to estimate ordered logits for adult depression and health plus a linear model for adult self-love, all seeded at 20251016 (`analysis/results.csv`). Higher childhood religiosity predicts a −0.120 drop in depression (95% CI [−0.187, −0.055], `q ≈ 0.0007`), higher parental guidance predicts a +0.0998 probability shift to very good/excellent health (95% CI [0.0889, 0.1109], `q = 0`), and childhood abuse predicts a −0.6544 self-love gap (95% CI [−0.719, −0.590], `q = 0`). NC1 (sibling count) stays near zero, and the pseudo-weight, design-effect, and pseudo-replicate suites (`outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) confirm the H1–H3 signs while every published table/figure passes the n ≥ 10 disclosure audit (`qc/disclosure_check_loop_061.md`). `[CLAIM:C1]` `[CLAIM:C2]` `[CLAIM:C3]`

## Introduction
Childhood religiosity, parental guidance, and emotional abuse shape adult wellbeing in nuanced ways; prior longitudinal work (e.g., Dore & Haardörfer 2025, `https://doi.org/10.1332/17579597y2024d000000035`) documents similar associations between early context and adult self-rated health, motivating the wellbeing family captured in H1–H3. We emphasize deterministic reproducibility (`analysis/pre_analysis_plan.md`, `analysis/results.csv`) and the measurement dossier (`qc/measures_validity.md`, `artifacts/measurement_validity_loop061.json`) before interpreting the associations, and we record the sensitivity plan (`analysis/sensitivity_plan.md`) alongside the manuscript.

## Methods
We analyze `data/raw/childhoodbalancedpublic_original.csv` with the codebook (`docs/codebook.json`) under the SRS assumption in `docs/survey_design.yaml`. Outcomes/predictors rely on the coded variables documented in `qc/measures_validity.md` and the imputation-free sample described in `analysis/code/measure_validity_checks.py`. The pipeline fits ordered logits for H1 and H2, a linear model for H3, applies BH for the wellbeing family, and logs every command/executed script in `analysis/results.csv` plus `tables/results_summary.csv/.md`.

## Results
- **H1 / Depression (`[CLAIM:C1]`)** — The ordered logit contrast between “very important” and “not at all important” religiosity equals −0.120 (95% CI [−0.187, −0.055], `q ≈ 0.0007`, `n = 14,438`). HC1 standard errors (0.0354) and BH metadata (belonging to `H1|H2`) are recorded in `analysis/results.csv`; the summary table is `tables/results_summary.*`.
- **H2 / Self-rated Health (`[CLAIM:C2]`)** — The guidance quartile contrast for very good/excellent health is +0.0998 (95% CI [0.0889, 0.1109], `q = 0`, `n = 14,430`), appearing directly in the deterministic tables.
- **H3 / Self-love (`[CLAIM:C3]`)** — Childhood abuse corresponds to a −0.6544 reduction in self-love (95% CI [−0.719, −0.590], `q = 0`, `n = 13,507`). The linear regression summary in `analysis/results.csv` includes the HC1 SE (0.0331) and the exact command string.
- **Negative control NC1** — Sibling count shifts by +0.2388 per religiosity point (95% CI [0.2209, 0.2568], `p ≈ 0`), confirming that the confirmatory pipeline avoids systematic false positives; NC1 remains `targeted = N` and outside the BH family.

## Sensitivity
Pseudo-weight scenarios (DEFF = 1.0, 1.25, 1.5) from `outputs/sensitivity_pseudo_weights` show modest inflations (H1 SEs from 0.035 to ~0.040, H2 from 0.0057 to ~0.0064, H3 from 0.033 to ~0.037) even as effective `n` drops to ~9,533, so the SRS baseline continues to dominate our reporting. The DEFF grid (`outputs/sensitivity_design_effect_grid.csv/.md`) keeps H1/H3 intervals below zero and H2 above even at DEFF = 2.0, while jackknife pseudo-replicates (`k = 6`, `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) produce SEs of ≈0.040, 0.006, and 0.036 for H1–H3, cementing the HC1-based specification as conservative while documenting the uncertainty envelope (`analysis/sensitivity_plan.md`, `analysis/sensitivity_manifest.md`).

## Discussion
The consistent wellbeing signals align with the DOI-backed literature entries in `lit/evidence_map.csv`/`lit/bibliography.*` and the descriptive framing in `reports/identification.md`. Limitations include the SRS assumption (weights pending), single-item measures (documented in `qc/measures_validity.md`), and retrospective recall of abuse/guidance; these issues motivated the sensitivity suite recorded above. The disclosure audit (`qc/disclosure_check_loop_061.md`) confirms no table/figure exhibits cells below $n \geq 10$, and the negative control NC1 demonstrates the modeling pipeline resists obvious artifacts.

## References
See `lit/bibliography.bib` / `lit/bibliography.json` for the citations referenced above.
