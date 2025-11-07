# Schema Alignment Check
Generated: 2025-11-03T20:50:32Z | Seed: 20251016  
Regeneration: `python analysis/code/align_codebook_schema.py --dataset childhoodbalancedpublic_original.csv --codebook-in docs/codebook.json --codebook-out docs/codebook.json`

- Empirical schema matched six analysis variables; all were present with expected ordinal/count structure.
- Value frequencies below the small-cell threshold (10) remain redacted and frequency tables are omitted from the public codebook to avoid sparse tail disclosure (retained internally via regeneration command).
- CSA score spans 0–22 with heavy point mass at 0; long tail retained for robustness planning.

| Variable | Storage | Allowed Values (truncated) | Missing | Mean | Std Dev |
| --- | --- | --- | ---: | ---: | ---: |
| classchild | float64 | 0, 1, 2, 3, 4, 5, 6 | 0 | 2.621 | 1.276 |
| classcurrent | float64 | 0, 1, 2, 3, 4, 5, 6 | 0 | 3.022 | 1.259 |
| I love myself (2l8994l) | float64 | -3, -2, -1, 0, 1, 2, 3 | 7 | 0.613 | 1.862 |
| I tend to suffer from depression (wz901dj) | float64 | -3, -2, -1, 0, 1, 2, 3 | 5 | -0.407 | 2.089 |
| I tend to suffer from anxiety (npvfh98)-neg | float64 | -3, -2, -1, 0, 1, 2, 3 | 6 | -0.827 | 2.031 |
| CSA_score | float64 | 0, 1, 2, 3, 4, 5, 6... | 0 | 1.035 | 2.758 |

Notes: The timestamp above matches the `generated_at` field in `docs/codebook.json`. Confirm final value labels with the official survey instrument before publication.
