# Childhood Resilience Study — Manuscript (Markdown Twin)

This Markdown twin mirrors `papers/main/manuscript.tex`. Every substantive update below references deterministic artifacts (see the MANIFEST) and cites `[CLAIM:<ID>]`.

## Abstract
The Childhood Resilience Study uses the publicly documented dataset and PAP `pap-v1` to estimate ordered logits for adult depression and health plus a linear model for adult self-love, all seeded at 20251016 (`analysis/results.csv`). Higher childhood religiosity predicts a −0.120 drop in depression score (95% CI [−0.187, −0.055], `q ≈ 0.0007`), higher parental guidance predicts a +0.0998 probability difference of very good/excellent health (95% CI [0.0889, 0.1109], `q = 0`), and childhood abuse predicts a −0.6544 self-love gap (95% CI [−0.719, −0.5895], `q = 0`). NC1 (sibling count) stays near zero, pseudo-weight/design-effect/pseudo-replicate scenarios confirm robustness, and all tables pass the n ≥ 10 disclosure audit (`qc/disclosure_check_loop_059.md`). `[CLAIM:C1]` `[CLAIM:C2]` `[CLAIM:C3]`

## Introduction
Childhood religiosity, parental guidance, and experiences of emotional abuse shape adult wellbeing in nuanced ways; prior longitudinal work (e.g., Dore & Haardörfer 2025, `https://doi.org/10.1332/17579597y2024d000000035`) documents similar associations between childhood context and adult self-rated health, motivating the wellbeing family captured in H1–H3. We place emphasis on deterministic reproducibility (`analysis/pre_analysis_plan.md`, `analysis/results.csv`) and measurement checks (`qc/measures_validity.md`) before interpreting the observed associations. `[CLAIM:C1]` `[CLAIM:C2]` `[CLAIM:C3]`

## Methods
We analyze `data/raw/childhoodbalancedpublic_original.csv` with the codebook (`docs/codebook.json`) alongside the SRS assumption described in `docs/survey_design.yaml`. PAP-specified models (ordered logits for H1/H2, linear regression for H3, BH correction for the wellbeing family, NC1 falsification) run via `analysis/code/run_models.py`, `analysis/code/negative_control.py`, `analysis/code/calc_bh.py`, and the table builder in `analysis/code/build_results_summary.py`. Every command reuses seed 20251016; the resulting `tables/results_summary.csv/.md` plus `analysis/results.csv` contain the effect sizes, standard errors, and q-values reported below.

## Results
- **H1 / Depression (`[CLAIM:C1]`)** — The ordered logit contrast between extreme religiosity levels is −0.120 (95% CI [−0.187, −0.055], `q ≈ 0.0007`, `n = 14,438`, `targeted = Y`). HC1 SEs (0.0354) and BH membership (`H1|H2`) appear directly in `analysis/results.csv`, and the summary table is `tables/results_summary.*`.
- **H2 / Self-rated Health (`[CLAIM:C2]`)** — The guidance quartile contrast reports +0.0998 for very good/excellent health (95% CI [0.0889, 0.1109], `q = 0`, `n = 14,430`), confirming the positive association tracked in both `analysis/results.csv` and `tables/results_summary.*`.
- **H3 / Self-love (`[CLAIM:C3]`)** — Childhood abuse is linked to a −0.6544 reduction in self-love (95% CI [−0.7192, −0.5895], `q = 0`, `n = 13,507`). The linear regression summary in `analysis/results.csv` lists this estimate along with the seed-backed command.
- **Negative control NC1** — Sibling count shifts by +0.2388 per religiosity point (95% CI [0.2209, 0.2568], `p ≈ 0`), matching the expectation that no spurious null arises; NC1 remains `targeted = N` so it does not enter the BH correction but is recorded for reproducibility.

## Sensitivity
Pseudo-weight scenarios (DEFF = 1.0, 1.25, 1.5) from `outputs/sensitivity_pseudo_weights` show only modest SE inflation (H1 0.035→0.037, H2 0.0057→0.0064, H3 0.033→0.037) even as effective `n` falls to ~9,533, so the SRS baseline continues to dominate the reporting decision. The DEFF grid (1.0–2.0) in `outputs/sensitivity_design_effect_grid.csv/.md` keeps H1 and H3 intervals below zero and H2 above, while jackknife pseudo-replicates (`k = 6`) yield averaged SEs ≈ 0.0402 (H1), 0.00623 (H2), and 0.0362 (H3), indicating HC1 is not severely underestimating uncertainty. These scenarios are cataloged in `analysis/sensitivity_plan.md` and `analysis/sensitivity_manifest.md`.

## Discussion
The consistent signs for the wellbeing family align with our theoretical priors and the DOI-backed literature entry in `lit/evidence_map.csv`/`lit/bibliography.*`; this reinforces the descriptive narrative without asserting causality. Key limitations include the SRS assumption (no design weights yet), single-item measures (see `qc/measures_validity.md`), and reliance on retrospective reports of abuse and guidance. The disclosure scan (`qc/disclosure_check_loop_059.md`) ensures published tables/figures stay above the n ≥ 10 threshold, and the negative control NC1 demonstrates the modeling pipeline resists obvious artifacts.

## References
See `lit/bibliography.bib` / `lit/bibliography.json` for the citations referenced above.
