status: draft
phase: pap
last_updated: 2025-11-08T20:28Z
freeze_commit: TBD
registry_url: TBD

# Pre-Analysis Plan — Draft
This draft documents priority hypotheses for the Childhood Resilience Study. The PAP will be frozen (status: frozen) only after:
1. Evidence map contains ≥3 DOI-backed sources supporting each targeted outcome.
2. Measurement validity dossier (`qc/measures_validity.md`) is populated for every referenced construct.
3. Reproducible code lives under `analysis/code/` with command lines captured below.

Loop 011 note: Semantic Scholar CLI attempts continue to return 403s (see `lit/queries/loop_011/query_001.json`); PAP remains draft while we prepare a formal waiver request citing the accumulated evidence (Loops 008–011) unless ops can restore access immediately.

Loop 012 note: Loop-mandated Semantic Scholar attempt again failed with 403 (see `lit/queries/loop_012/query_001.json`). To avoid literature stagnation, we logged a CrossRef-backed article on emotional maltreatment → adult depression/self-compassion (`10.1016/j.chiabu.2019.03.016`) and updated `lit/evidence_map.csv` / `lit/bibliography.*`. PAP freeze remains blocked pending a working S2 key or documented waiver.

Loop 013 note: Added `lit/semantic_scholar_waiver_loop013.md`, consolidating loops 008–013 403 payloads and CrossRef fallbacks to request a temporary waiver while the Semantic Scholar key is repaired. PAP cannot freeze until that waiver is approved or a working key is restored.

Loop 014 note: Semantic Scholar failure persisted (`lit/queries/loop_014/query_001.json`), so we logged a CrossRef-backed spirituality article (`Pandya 2017`, DOI `10.1080/15332985.2016.1222982`) that links faith-based support to lower childhood depression. The waiver memo now covers loops 008–014 and cites this new DOI, but PAP status stays draft until the waiver is approved or the API credential resumes service.

Loop 015 note: Loop-mandated Semantic Scholar query (`childhood parental guidance adult health`) again returned 403 (`lit/queries/loop_015/query_001.json`). We captured a CrossRef fallback on parental monitoring vs. hazardous drinking (Turrisi et al., 2010; DOI `10.7312/guil14080-006`) and synchronized `lit/evidence_map.csv`, `lit/bibliography.*`, and the waiver memo. PAP remains draft until either the waiver is formally approved or the API key is reissued.

Loop 016 note: Another Semantic Scholar attempt (`childhood emotional neglect adult self compassion`) failed with 403 (`lit/queries/loop_016/query_001.json`). To keep H3 literature current, we captured an SSRN preprint (Larkin et al., 2024; DOI `10.2139/ssrn.4703219`), a new Child Abuse & Neglect article (Qu, 2024; DOI `10.1016/j.chiabu.2024.107020`), an IJSR trauma review (Renu, 2023; DOI `10.21275/SR23621004642`), and an Oxford chapter on young-adult mental health (Hulvershorn et al., 2009; DOI `10.1093/med:psych/9780195332711.003.0004`) via CrossRef (see `lit/queries/loop_016/crossref_query_001.json` and `lit/queries/loop_016/crossref_query_002.json`) and propagated them to the evidence map/bibliography. The waiver memo now documents loops 008–016; PAP status stays draft until either the waiver is approved or Semantic Scholar access is restored.

Loop 017 note: Mandatory Semantic Scholar query (`childhood religious participation adult depression support`) still returned 403 (`lit/queries/loop_017/query_001.json`). To maintain H2 coverage we captured a CrossRef DOI linking parental involvement to health-care transitions among adolescent/young adult cancer survivors (Loecher et al., 2023; DOI `10.1089/jayao.2022.0097`; see `lit/queries/loop_017/crossref_query_003.json`) and synced the evidence map/bibliography plus the waiver memo, which now covers loops 008–017. PAP remains draft until ops approves the waiver or restores the API key.

Loop 018 note: Semantic Scholar remains blocked (`lit/queries/loop_018/query_001.json` logged another HTTP 403), so we captured CrossRef metadata for Merrill & Salazar (2002; DOI `10.1080/13674670110059569`) via `lit/queries/loop_018/crossref_query_001.json`. The study links regular church attendance to better adult mental health among Mormon and non-Mormon residents, strengthening H1's religiosity mechanism while the waiver request awaits approval. PAP status therefore stays draft.

Loop 019 note: Semantic Scholar attempt (`lit/queries/loop_019/query_001.json`, query "childhood faith community adult resilience depression") resulted in the 12th consecutive 403. To keep H1 grounded we logged a CrossRef-backed longitudinal paper (Eliassen, 2013; DOI `10.1007/s13644-013-0110-9`, see `lit/queries/loop_019/crossref_query_004.json`) showing that weekly pre-teen service attendance plus high stress exposure conditions religious coping's association with young-adult depression. PAP remains draft until the waiver is approved or the API credential is restored, and we added this stress-interaction nuance to the planned robustness checks.

Loop 020 note: Semantic Scholar query (`childhood spiritual involvement adult depressive symptoms social support`) produced yet another 403 (`lit/queries/loop_020/query_001.json`). To avoid stalling H1 evidence, we captured CrossRef metadata for Kasen et al. (2014; DOI `10.1002/da.22131`, see `lit/queries/loop_020/crossref_query_001.json`), which reports that higher religiosity predicts improved psychosocial functioning among high-risk young adults. The same query also surfaced Giri et al. (2025; DOI `10.2139/ssrn.5144651`) and Grummitt et al. (2024; DOI `10.1001/jamapsychiatry.2024.0804`), documenting intergenerational ACE transmission and maltreatment-attributable mental-disorder burdens, which inform H3’s parental-history controls and effect-size expectations. PAP status stays draft until the S2 key or waiver clears, and these papers add motivation for modeling stress-by-religiosity interactions plus trauma-informed controls.

Loop 021 note: Mandatory Semantic Scholar search (`childhood parental guidance adult health resilience`) continued to fail with HTTP 403 (`lit/queries/loop_021/query_001.json`). As fallback we logged CrossRef metadata for McLeod (1991; DOI `10.2307/2136804`) showing that childhood parental loss predicts adult depression, and Wheeler (2023; DOI `10.1136/archdischild-2023-326071`) summarizing evidence that parental influence persists into young adulthood. Both citations now live in `lit/evidence_map.csv` / `lit/bibliography.*` and motivate adding family-loss indicators plus sustained guidance quartiles to the PAP robustness section once the waiver or new API credential clears.

Loop 022 note: Semantic Scholar remains blocked (`lit/queries/loop_022/query_001.json` logged another 403 for the query “childhood parental warmth adult mental health resilience”), so we captured CrossRef metadata for Taskesen et al. (2025; DOI `10.3389/fpsyg.2025.1629350`). The study shows parental autonomy support and warmth boosting young-adult resilience via “emotion crafting,” reinforcing H2’s guidance mechanism and the need to pre-specify mediator adjustments (emotion awareness/action, savoring beliefs) once the waiver or new API credential enables PAP freeze.

Loop 023 note: Mandated Semantic Scholar query (“childhood parental warmth adult emotional health”) still returned 403 (`lit/queries/loop_023/query_001.json`), so we logged a CrossRef fallback for Van Alen et al. (2020; DOI `10.31234/osf.io/gjt94`). The MIDUS cohort evidence ties higher childhood parental warmth to better midlife HF-HRV and lower cardiovascular risk, so the PAP draft now flags vagal-tone mechanisms and records this blocker until the waiver or a restored API key lets us freeze the plan.

Loop 024 note: Semantic Scholar attempt (“childhood parental support adult cardiovascular resilience”) again failed with 403 (`lit/queries/loop_024/query_001.json`). To keep H2 literature current we logged the JAMA Cardiology article on childhood parental incarceration and adult-onset hypertension (`10.1001/jamacardio.2023.2672`), updated `lit/evidence_map.csv` / `lit/bibliography.*`, and extended the waiver memo through Loop 024. PAP status remains draft until the waiver is approved or the API credential is restored, and the plan now highlights family-disruption covariates (parental incarceration, loss) as mandatory controls for the guidance models.

Loop 025 note: Semantic Scholar query (“childhood parental nurturance adult metabolic health”) produced yet another 403 (`lit/queries/loop_025/query_001.json`), so we captured CrossRef metadata for Liu & Yin (2025 preprint; DOI `10.21203/rs.3.rs-6195416/v1`). The study shows maternal warmth mediating the effect of inter-parent conflict on emerging-adult aggression, reinforcing H2’s need to pre-specify emotion-regulation covariates and maternal/paternal warmth interactions before PAP freeze. The waiver memo and literature registries now include this DOI while we wait for a working API credential or formal waiver approval.

Loop 025 action items: map survey columns `parentwarm_mom`, `parentwarm_dad`, and the short-form Difficulties in Emotion Regulation Scale (see codebook fields `e3y0vab`–`e3y0vah`) into a composite that mirrors Liu & Yin’s maternal warmth and dysregulation constructs so the PAP can cite a concrete coding plan once S2 access or the waiver clears.

Loop 026 note: The required Semantic Scholar query (“childhood parental warmth adult aggression regulation”) again returned HTTP 403 (`lit/queries/loop_026/query_001.json`). To keep the mediator plan moving we captured a CrossRef-backed chapter by Talmon (2023; DOI `10.1017/9781009304368.007`) showing how parents’ own maltreatment histories impair emotion regulation and warmth, reinforcing the need to script DERS-based composites plus maternal/paternal warmth interactions before PAP freeze. The waiver memo now covers loop 026 and cites this DOI, but the PAP remains draft until Semantic Scholar access is restored or the waiver is approved.

Loop 027 note: Semantic Scholar is still blocked (`lit/queries/loop_027/query_001.json` captured another HTTP 403 for the “childhood parental warmth adult psychosocial resilience” query). We logged a CrossRef fallback for Lacey et al. (2013; DOI `10.1016/j.psyneuen.2013.05.007`), which shows that childhood parental separation predicts elevated adult C-reactive protein through material and psychosocial stressors. This addition means the PAP must now pre-specify family disruption covariates and inflammation proxies (where available) within the H2 health models, but the plan remains draft until the API credential is restored or the documented waiver is approved.

Loop 028 note: The mandated Semantic Scholar search (`childhood parental support adult inflammation resilience`) again returned HTTP 403 (`lit/queries/loop_028/query_001.json`). To keep the evidence base expanding we logged the CrossRef record for Nelson (1982; DOI `10.1007/bf00583891`), which provides additional Canadian data showing childhood parental death continues to predict adult depression even after socioeconomic controls. H1/H2 robustness sections now flag explicit adversity-loss covariates plus stress-buffer interactions, yet the PAP remains draft until the waiver is approved or the Semantic Scholar credential is restored so canonical S2 sourcing is satisfied.

Loop 029 note: Semantic Scholar query (`childhood parental warmth adult cortisol regulation`) is still blocked (see `lit/queries/loop_029/query_001.json`), so we logged CrossRef metadata for Gerra et al. (2016; DOI `10.1016/j.psychres.2016.09.001`). The study links low childhood parental care to dysregulated ACTH/cortisol and elevated nicotine dependence in adults, so the PAP now highlights cortisol/stress proxies plus nicotine-use controls within the H2 specification. Status remains `draft` until either the waiver is approved or the Semantic Scholar credential is restored and the queued S2 searches can be replayed.

Loop 030 note: Semantic Scholar query (`childhood parental nurturance adult immune resilience`) continued to return HTTP 403 (`lit/queries/loop_030/query_001.json`). The CrossRef fallback produced Oh & Han (2019; DOI `10.37918/kce.2019.05.116.47`), which shows that secure childhood parental attachment reduces adult attachment anxiety and parenting stress. This evidence reinforces the need to script DERS-style emotion regulation composites plus maternal/paternal warmth indicators before PAP freeze, ensuring H2 robustness checks explicitly test attachment-anxiety mediators once the S2 credential or waiver clears.

Loop 031 note: Semantic Scholar remains blocked (`lit/queries/loop_031/query_001.json` logs another HTTP 403 for the parental-warmth stress-buffering search). The CrossRef fallback yielded Xu & Zheng (2025; DOI `10.31234/osf.io/82u5e_v1`), a 30-day diary study showing that daily parental warmth interrupts the link between parent stress and adolescent adjustment. This reinforces the need to finalize reproducible transformations for the survey’s parental-warmth, stress, and positive-affect scales so H2 specifications can explicitly test stress-buffering mediators once the API credential or waiver clears.

Loop 032 note: The latest Semantic Scholar attempt (`childhood parental warmth adult inflammatory markers`; see `lit/queries/loop_032/query_001.json`) still returned HTTP 403. CrossRef fallback #2 for this loop surfaced Moran et al. (2018; DOI `10.1037/fam0000401`, recorded in `lit/queries/loop_032/crossref_query_002.json`), which shows that higher childhood parental warmth predicts better adult coping and well-being. We propagated this DOI to `lit/evidence_map.csv` / `lit/bibliography.*` to keep H2 mediator coverage moving, and refreshed `lit/semantic_scholar_waiver_loop013.md` so the header/attempt log now spans loops 008–032 as the reviewer requested. PAP remains `status: draft` until the waiver is approved or the API credential is restored.

Loop 033 note: Mandatory Semantic Scholar query (`childhood mentorship adult coping resilience`; `lit/queries/loop_033/query_001.json`) again yielded HTTP 403, so we logged CrossRef fallback #1 for this loop (`lit/queries/loop_033/crossref_query_001.json`) and added Kennedy et al. (2017; DOI `10.1016/j.aogh.2017.03.265`) to the evidence map/bibliography as mentorship-based support evidence for H2. The waiver memo now covers loops 008–033 with the new attempt row plus mentorship summary, but PAP status remains draft until either the waiver is approved or Semantic Scholar access is restored so confirmatory analyses stay paused.

Loop 034 note: Semantic Scholar remains down (`lit/queries/loop_034/query_001.json` logged another 403 for "childhood mentorship coping adult resilience"), so we captured CrossRef metadata (`lit/queries/loop_034/crossref_query_002.json`) and added Gasper (2020; DOI `10.5040/9781350100763.ch-003`) to document how structured childhood mentoring/coaching builds coping/self-regulation skills relevant to H2. Waiver memo now spans loops 008–034 with the new attempt row and fallback, and PAP status stays draft until the credential is restored or the waiver is approved.

## Design Summary
- **Population:** Respondents in `data/raw/childhoodbalancedpublic_original.csv`, aged ≥18.
- **Survey design:** No weights currently available; treat as SRS while monitoring for forthcoming design info (see `docs/survey_design.yaml`). Any newly provided weights will trigger a PAP revision before freeze.
- **Seed discipline:** `20251016` (per `config/agent_config.yaml`) is passed explicitly to every script (`analysis/code/run_models.py`, `analysis/code/missingness_profile.py`, `analysis/code/measure_validity_checks.py`, `analysis/code/impute_and_stack.py`, `analysis/code/calc_bh.py`) to maintain determinism.
- **Disclosure threshold:** n ≥ 10 per `config/agent_config.yaml`; exploratory summaries in Loops 002–003 remained comfortably above this threshold (minimum reported cell n = 187 in `qc/data_overview_loop002.md`).
- **Outputs + manifests:** Every figure/table command will be recorded inside `papers/main/MANIFEST.md` and the relevant QC markdown before PAP freeze.

## Privacy & Disclosure Controls
- All confirmatory tables/figures will cite the n ≥ 10 rule and will be screened via loop-specific disclosure memos (`qc/disclosure_check_loop_{loop:03d}.md`). `analysis/code/disclosure_check.py` now automates this process (see `qc/disclosure_check_loop_006.md`).
- Sensitive predictors/outcomes (abuse, depression, self-love) are tagged in `analysis/hypotheses.csv` and `qc/measures_validity.md`; any subgroup slices yielding n < 10 will be suppressed or binned per `config/agent_config.yaml::small_cells`.
- For manuscript-ready numbers, we will store both machine-readable CSVs (`tables/*.csv`) and markdown tables with clear suppression notes, referencing the exact command string that generated them.
- `reports/identification.md` records the disclosure guardrails to ensure readers understand that all estimates exclude identifiable cells.
- Loop 006 regenerated `figures/dag_design.png` (see `papers/main/MANIFEST.md`) and refreshed the identification memo after the reviewer STOP.

## Hypotheses Under Consideration
### H1 — Childhood Religious Adherence & Adult Depression (Family: wellbeing)
- **Outcome:** Likert 1–5 `wz901dj` (“I tend to suffer from depression”).
- **Predictor:** Ordinal `externalreligion` (importance of childhood religious adherence).
- **Controls:** Age (`selfage`), gender indicators (`biomale`, `gendermale`, `cis`), childhood class (`classchild`).
- **Exploratory analytic N:** 14,438 observations after listwise deletion (`outputs/run_models_loop003_H1.json`).
- **Estimand:** Average marginal effect of moving from “not important” to “very important” on depression score (ordered logit).
- **Model:** Survey-weighted (currently SRS) ordered logistic regression using `statsmodels`. Robust SEs clustered at household not available; default to HC1.
- **Missing data:** Explore patterns; if MAR plausible, use multiple imputation via `miceforest` with seed 20251016.
- **Robustness (pre-specified):** (a) Treat predictor as binary high/low. (b) Replace outcome with binary indicator `wz901dj >=4` and run logit.
- **Regeneration command (planned):**
  ```bash
  python analysis/code/run_models.py --hypothesis H1 --seed 20251016 --config config/agent_config.yaml
  ```

### H2 — Parental Guidance & Adult Health (Family: wellbeing)
- **Outcome:** Ordered `okq5xh8` (general health).
- **Predictor:** `pqo6jmj` guidance scale (0–12).
- **Controls:** Age, gender, current class (`classcurrent`), teen class (`classteen`). The chronic illness indicator (`mentalillness`) is currently empty in the delivered dataset, so it is excluded from interim models until valid values are supplied (see `outputs/run_models_loop003_H2.json`).
- **Exploratory analytic N:** 14,430 observations (Loop 003 exploratory run).
- **Estimand:** Difference in predicted probability of reporting “very good/excellent” health between top and bottom guidance quartiles (ordered logit + post-estimation).
- **Robustness:** (a) Treat health as continuous 1–5. (b) Limit to respondents without chronic illness indicator `mentalillness`.
- **Command stub:** same script with `--hypothesis H2`.

### H3 — Childhood Abuse & Adult Self-Love (Family: psychosocial)
- **Outcome:** Likert `2l8994l` (“I love myself”).
- **Predictor:** Binary `mds78zu` (parents verbally/emotionally abusive ages 0–12).
- **Controls:** Age, gender, sibling count (`siblingnumber`), socioeconomic controls.
- **Exploratory analytic N:** 13,507 respondents (Loop 003 exploratory run).
- **Estimand:** Average difference in self-love score between abuse vs no abuse (survey-weighted linear regression).
- **Robustness:** (a) Add teen-stage abuse indicator to check cumulative exposure. (b) Exclude respondents who reported perpetration (`rapist` == 1) to test sensitivity.
- **Command stub:** same script with `--hypothesis H3`.

## Data Management Plan
- Raw data remain immutable under `data/raw/`.
- Recode scripts live under `analysis/code/` and write outputs to `data/clean/` with filenames containing the seed (e.g., `childhood_imputed_stack_loop005.csv`, created in Loop 006).
- All transformations are now logged in `analysis/data_processing.md` (DP1–DP8) with explicit commands, seeds, and artifact paths; any new derivation must update both this ledger and `analysis/decision_log.csv`.
- Loop 002 added `analysis/code/describe_dataset.py` and `analysis/code/validate_metadata.py` so QC summaries (`artifacts/describe_dataset_loop002.json`, `qc/metadata_validation.md`) regenerate from a single command.
- Loop 003 implemented `analysis/code/run_models.py` (H1–H3 estimators), `analysis/code/missingness_profile.py`, and `analysis/code/measure_validity_checks.py`. Regeneration examples:
  ```bash
  python analysis/code/run_models.py --hypothesis all --config config/agent_config.yaml --seed 20251016 --draws 300 --output-prefix outputs/run_models_loop003
  python analysis/code/missingness_profile.py --input data/raw/childhoodbalancedpublic_original.csv --output-csv outputs/missingness_loop003.csv --output-md qc/missingness_loop003.md --seed 20251016
  python analysis/code/measure_validity_checks.py --config config/agent_config.yaml --output-md qc/measures_validity.md --output-json artifacts/measurement_validity_loop003.json
  ```
- Loop 005 added deterministic hot-deck MI tooling plus multiplicity automation, and Loop 006 reran the commands so the promised artifacts now exist in the repo:
  ```bash
  python analysis/code/impute_and_stack.py --m 5 --stacked-output data/clean/childhood_imputed_stack_loop005.parquet --summary-output artifacts/imputation_summary_loop005.json --seed 20251016
  # The script falls back to CSV if parquet engines are unavailable; see summary JSON for the actual path used.
  python analysis/code/calc_bh.py --config config/agent_config.yaml --input-csv analysis/results_pre_bh.csv --output-csv analysis/results.csv --summary-json artifacts/bh_summary.json
  ```

## Manuscript Linkage
- Each hypothesis maps to claims `[CLAIM:C1]`–`[CLAIM:C3]` in `papers/main/manuscript.tex` (stubs added in initial draft). The PAP freeze commit hash will be cited in the manuscript Methods section.

## Analysis Execution Order
1. **Data hygiene:** `analysis/code/describe_dataset.py`, `validate_metadata.py`, and `missingness_profile.py` run with seed 20251016; outputs referenced in `qc/data_overview_loop002.md`, `qc/metadata_validation.md`, and `qc/missingness_loop003.md`.
2. **Measurement dossier:** `analysis/code/measure_validity_checks.py` updates `qc/measures_validity.md` and `artifacts/measurement_validity_loop003.json`; all H1–H3 variables now have coding + DIF notes.
3. **Model estimation:** `analysis/code/run_models.py --hypothesis {H1|H2|H3}` executes ordered-logit / linear models with deterministic draws=300 for marginal effects.
4. **Imputation (if invoked):** `analysis/code/impute_and_stack.py --m 5 --seed 20251016` now produces a stacked hot-deck MI file plus `artifacts/imputation_summary_loop005.json`. Until pyarrow is available the script writes CSV outputs (`data/clean/childhood_imputed_stack_loop005.csv`) and records the fallback reason for transparency.
5. **BH correction:** Once confirmatory estimates exist, run `python analysis/code/calc_bh.py --config config/agent_config.yaml --input-csv analysis/results_pre_bh.csv --output-csv analysis/results.csv --summary-json artifacts/bh_summary.json` to append `q_value`, `family`, `targeted`, and `bh_in_scope` columns using Benjamini–Hochberg at q=0.05 per family (wellbeing, psychosocial).
6. **Disclosure review:** Draft `qc/disclosure_check_loop_{loop}` with min cell sizes and suppression summary before any tables/figures leave the repo.

## Outstanding Tasks Before Freeze
1. Restore Semantic Scholar access (or record a partner-approved waiver). Loops 008–015 remain 403-only (see `lit/queries/loop_{008-015}/query_001.json`), so PAP freeze is deferred until either the key is fixed or the waiver is approved and logged in `analysis/decision_log.csv`.
2. Close the waiver action by capturing the approval decision (or credential fix) plus replaying the queued Semantic Scholar searches so the canonical evidence source is satisfied before PAP freeze.
3. Register and freeze the PAP (`status: frozen`, `registry_url`, `freeze_commit`) once the literature gate clears and disclosure checklist automation (DP8) is linked to every planned table/figure.
4. Keep `analysis/data_processing.md` synchronized with any new derivations (e.g., sensitivity specifications) and cite the ledger whenever PAP text references transformation history.
5. Confirm whether `mentalillness` has valid data in future drops; if not, update H2 controls and document the missing control in `analysis/results.csv` once confirmatory runs occur.***

_No confirmatory analysis will begin until the status is set to `frozen` with registry details and a recorded commit/tag._
