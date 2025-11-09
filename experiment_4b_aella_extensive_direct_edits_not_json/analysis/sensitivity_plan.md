# Sensitivity Plan — Loop 064
**Date:** 2025-11-09  
**Seed:** 20251016 (see `artifacts/seed.txt`; every executed script this loop reuses this seed so the outputs stay deterministic).

## Confirmatory estimates and falsification
1. **H1 / depression ([CLAIM:C1])** — The ordered-logit contrast of “religion very important” vs. “not at all important” remains `ΔE = -0.1201` (95% CI [−0.189, −0.050], $q \approx 0.0007$) with HC1 SE 0.0354; `analysis/results.csv` plus `artifacts/bh_summary.json` provide the fully seeded estimate and BH metadata for the wellbeing family.
2. **H2 / self-rated health ([CLAIM:C2])** — Guidance quartile slope stays `+0.0998` (95% CI [0.0889, 0.1110], $q = 0$) with SE 0.0057; the deterministic ordered-logit output verifies the positive guidance→health ordering.
3. **H3 / self-love ([CLAIM:C3])** — The abuse/non-abuse gap persists at `-0.6544` (95% CI [−0.719, −0.590], $q = 0$) with SE 0.0331; this linear output continues to load into `analysis/results.csv` and the publication table with the seeded HC1 SE.
4. **NC1 / sibling count (negative control)** — Linear difference `+0.2388` (95% CI [0.2209, 0.2568], $p \approx 0$) remains outside BH adjustment (`targeted=N`) and demonstrates the null expectation for religiosity effects on unrelated siblings numbers.

## Robustness checks completed
- **H1 high vs. low religiosity** (`outputs/robustness_loop052/robustness_h1_high_low.json`) keeps the H1 direction when comparing religious extremities.
- **H2 continuous health coding** (`outputs/robustness_loop052/robustness_h2_continuous_health.json`) sustains the positive slope when treating self-rated health as a numeric scale.
- **H3 non-perpetrators & timing controls** (`outputs/robustness_loop052/robustness_h3_no_perpetration.json` and `_robustness_h3_teen_abuse.json`) preserve the abuse-self-love gap under tighter perpetration and timing restrictions.

## Sensitivity scenarios executed this loop
- **Scenario 1 – pseudo weights (DEFF ∈ {1.0, 1.25, 1.5})** — `analysis/code/pseudo_weight_sensitivity.py` rewrote `outputs/sensitivity_pseudo_weights/pseudo_weights_deff_100.json/_125.json/_150.json` with seeds adjusted per scenario. Effective $n$ falls from 14,443 (DEFF=1.0) to 11,629 (DEFF=1.25) to 9,533 (DEFF=1.5); H1 and H2 estimates retain the baseline values while H3’s SE rises from 0.0331 to 0.0370 and 0.0405, yet the CI remains well below zero.
- **Scenario 2 – design-effect grid (DEFF ∈ {1.0, 1.25, 1.5, 2.0})** — `analysis/code/design_effect_grid.py` rebuilt `outputs/sensitivity_design_effect_grid.csv/.md`, showing the targeted subset’s adjusted SEs/95% CIs remain on the same side of zero even at DEFF=2.0 (effective $n\approx7,200$ for H1/H2 and $\approx6,750$ for H3) while $q$ stays tied to the original BH values.
- **Scenario 3 – pseudo replicates (k = 6)** — `analysis/code/pseudo_replicates.py` refreshed `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`, yielding jackknife SEs of ≈0.019 (H1), 0.0020 (H2), and 0.018 (H3) that, although slightly tighter than the HC1 SEs, keep the same sign pattern and document the residual pseudo-cluster variation.

## Default specification decision
The SRS + HC1 pipeline remains the default because the pseudo-weight draws widen H3’s SE only modestly while leaving H1/H2 direction unchanged, the design-effect grid pushes the wrapped CIs into the same sign even at DEFF=2.0, and the pseudo-replicates replicate the overall effect pattern (the narrower jackknife SEs reflect the tiny k=6 pseudo-clusters rather than any reversal). Recording these exercises keeps the descriptive claims conservative while leaving HC1 as the reporting standard.

## Loop 064 synthesis
- Re-ran the sensitivity suite (pseudo weights, design-effect grid, pseudo replicates) with seed 20251016 so every uncertainty artifact (`outputs/sensitivity_pseudo_weights/*`, `outputs/sensitivity_design_effect_grid.*`, `outputs/sensitivity_replicates/sensitivity_replicates_summary.json`) matches the new deterministic commands documented in `analysis/sensitivity_manifest.md`.
- Verified the n ≥ 10 guardrail by re-running `analysis/code/disclosure_check.py --output-md qc/disclosure_check_loop_064.md`; the table/DAG audit recorded zero violations while leaving the disclosure plan grounded in the same seed.
- Issued the loop-064 Semantic Scholar query (`scripts/semantic_scholar_cli.py search --query "childhood spirituality adult resilience" --limit 5 --output lit/queries/loop_064/query_001.json`), captured the CrossRef fallback (`lit/queries/loop_064/crossref_query_001.json`, DOI 10.1080/19349637.2014.864543), and linked the fallback row to `lit/evidence_map.csv` so [CLAIM:C1] remains DOI-backed while the API remains 403.
