# Measurement Validity Dossier (Loop 003)

_Command_: `python analysis/code/measure_validity_checks.py --config config/agent_config.yaml --output-md qc/measures_validity.md --output-json artifacts/measurement_validity_loop059.json`

measure_id | item_wording | coding | reliability_alpha | dif_check | notes
--- | --- | --- | --- | --- | ---
wz901dj | Depression tendency (self-assessed) | Likert -3..3 (higher = more depression) | single_item | Δ(biomale=1 minus 0) = 0.916 (p = 0.000, n = 14438) | Outcome for H1.
externalreligion | Perceived childhood religious importance | Ordinal 0-4 (higher = stricter adherence) | single_item | Δ(biomale=1 minus 0) = -0.142 (p = 0.000, n = 14443) | Predictor for H1; coded from numeric/text scale.
pqo6jmj | Parents gave useful guidance (0-12) | Likert -3..3 (higher = more guidance) | single_item | Δ(biomale=1 minus 0) = 0.589 (p = 0.000, n = 14431) | Predictor for H2.
okq5xh8 | Self-rated general health | Ordinal 0-4 (poor→excellent) | single_item | Δ(biomale=1 minus 0) = 0.343 (p = 0.000, n = 14437) | Outcome for H2.
mds78zu | Childhood emotional abuse (0-12) | Binary indicator (1 = any reported abuse > neutral) | single_item | Δ(biomale=1 minus 0) = -0.239 (p = 0.000, n = 13509) | Predictor for H3 (derived from Likert).
2l8994l | Self-love statement | Likert -3..3 (higher = more self-love) | single_item | Δ(biomale=1 minus 0) = 0.203 (p = 0.000, n = 14436) | Outcome for H3.