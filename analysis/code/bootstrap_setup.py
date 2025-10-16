#!/usr/bin/env python3
"""
Bootstrap reproducibility script for initial survey research scaffolding.

Recreate deterministic artifacts using the project seed.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

SEED = 20251016
GENERATED = "2025-10-16T12:44:10Z"

CODEBOOK_CONTENT = '{\n  "dataset": "childhoodbalancedpublic_original.csv",\n  "description": "Bootstrap codebook scaffold; expand with detailed metadata before analysis.",\n  "generated": "2025-10-16T12:44:10Z",\n  "seed": 20251016,\n  "variables": [\n    {\n      "name": "selfage",\n      "label": "Respondent self-reported age (years)",\n      "type": "numeric",\n      "allowed_values": ">= 0, integer",\n      "notes": "TODO: Verify value range, recode implausible ages"\n    },\n    {\n      "name": "I love myself (2l8994l)",\n      "label": "Self-love Likert agreement",\n      "type": "ordinal",\n      "allowed_values": "Likert scale 1-7 (TODO confirm codes)",\n      "notes": "Outcome candidate for wellbeing hypotheses"\n    },\n    {\n      "name": "during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)",\n      "label": "Childhood emotional abuse indicator",\n      "type": "ordinal",\n      "allowed_values": "Likert frequency (TODO confirm mapping)",\n      "notes": "Primary predictor for HYP-001"\n    },\n    {\n      "name": "classchild",\n      "label": "Perceived family socioeconomic status ages 0-12",\n      "type": "categorical",\n      "allowed_values": "TODO: map text labels to ordered categories",\n      "notes": "Use as socioeconomic background indicator"\n    },\n    {\n      "name": "networth",\n      "label": "Current net worth category",\n      "type": "categorical",\n      "allowed_values": "Binned dollar ranges (TODO verify codes)",\n      "notes": "Outcome candidate for socioeconomic hypotheses"\n    },\n    {\n      "name": "monogamy",\n      "label": "Current monogamy preference",\n      "type": "categorical",\n      "allowed_values": "Monogamy vs non-monogamy categories (TODO reconcile labels)",\n      "notes": "Outcome candidate for relational hypotheses"\n    },\n    {\n      "name": "Do you *currently* actively practice a religion? (902tbll)",\n      "label": "Current religious practice indicator",\n      "type": "categorical",\n      "allowed_values": "Yes/No/Other (TODO confirm coding)",\n      "notes": "Predictor for HYP-003"\n    }\n  ],\n  "todo": [\n    "Audit all variables referenced in hypotheses for coding consistency.",\n    "Import official metadata if provided by survey administrators."\n  ],\n  "regeneration_command": "python analysis/code/bootstrap_setup.py --only codebook"\n}\n'

SURVEY_DESIGN_CONTENT = 'dataset: childhoodbalancedpublic_original.csv\ngenerated: 2025-10-16T12:44:10Z\nseed: 20251016\nscript: analysis/code/bootstrap_setup.py\nweights:\n  weight_var: null\n  notes: "TODO: Confirm whether a weight variable is available in raw data."\nstrata:\n  strata_var: null\n  notes: "TODO: Identify strata if design information becomes available."\nclusters:\n  cluster_var: null\n  notes: "TODO: Identify primary sampling units if applicable."\nreplicate_weights: []\nfinite_population_correction: null\nassumptions:\n  - "Assuming simple random sampling until survey design metadata is verified."\ntodo:\n  - "Review docs/codebook.json for weight metadata."\n  - "Inspect raw data for variables matching weight/strata conventions."\nregeneration_command: "python analysis/code/bootstrap_setup.py --only survey_design"\n'

AGENT_CONFIG_CONTENT = 'time_budget_minutes_per_loop: 15\nfdr_q: 0.05\nsmall_cell_threshold_k: 10\nreport_variables_of_interest:\n  - outcome1\n  - outcome2\nallowed_languages:\n  - python\n  - r\npython_packages:\n  - pandas\n  - numpy\n  - statsmodels\n  - linearmodels\n  - matplotlib\n  - scipy\nr_packages:\n  - survey\n  - srvyr\n  - mice\n  - ggplot2\n  - sandwich\n  - clubSandwich\nseed: 20251016\nregeneration_command: "python analysis/code/bootstrap_setup.py --only agent_config"\nnotes: |\n  Bootstrap configuration seeded for reproducibility. Update thresholds and packages as project needs evolve.\n'

STATE_JSON_CONTENT = '{\n  "loop_counter": 0,\n  "last_updated": "2025-10-16T12:44:10Z",\n  "backlog": [\n    {\n      "id": "T-001",\n      "priority": 1,\n      "description": "Validate survey weights and replicate design metadata against data files.",\n      "status": "pending",\n      "estimate_min": "15m"\n    },\n    {\n      "id": "T-002",\n      "priority": 2,\n      "description": "Produce exploratory weighted summaries for key wellbeing and socioeconomic outcomes.",\n      "status": "pending",\n      "estimate_min": "20m"\n    }\n  ],\n  "next_actions": [\n    {\n      "id": "T-001",\n      "priority": 1,\n      "description": "Validate survey weights and replicate design metadata against data files.",\n      "estimate_min": "15m"\n    },\n    {\n      "id": "T-002",\n      "priority": 2,\n      "description": "Produce exploratory weighted summaries for key wellbeing and socioeconomic outcomes.",\n      "estimate_min": "20m"\n    }\n  ],\n  "notes": "Bootstrap state initialized; update after each research loop.",\n  "regeneration_command": "python analysis/code/bootstrap_setup.py --only state"\n}\n'

HYPOTHESES_CSV_CONTENT = 'id,family,description,outcome_var,predictors,controls,population/subset,estimand,status,notes\nHYP-TEMPLATE,template,"TODO: replace this row with real hypotheses","outcome_var","predictors","controls","population or subset definition","estimand description","status","notes"\nHYP-001,wellbeing,"Childhood emotional abuse associates with lower adult self-love scores.","I love myself (2l8994l)","during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)","selfage;gendermale;education","Adults with non-missing outcome and predictor responses","Survey-weighted mean difference in self-love score across abuse frequency categories","proposed","Confidence rating: Low (awaiting data diagnostics)."\nHYP-002,socioeconomic,"Higher perceived childhood class associates with higher current net worth category.","networth","classchild","selfage;gendermale;education","Adults with non-missing childhood class and net worth data","Survey-weighted ordered logit comparing net worth categories across childhood class levels","proposed","Confidence rating: Low (requires ordinal coding confirmation)."\nHYP-003,relationships,"Active religious practice is associated with preferring monogamy.","monogamy","Do you *currently* actively practice a religion? (902tbll)","selfage;gendermale","Adults reporting current relationship status information","Survey-weighted multinomial logit estimating relative risk ratios for monogamy preference","proposed","Confidence rating: Low (categorical harmonization pending)."\nHYP-004,health,"History of mental health diagnosis associates with current emotional work/social difficulty.","""In the past *4 weeks*, you've had difficulty accomplishing things in work or social activities due to *emotional issues* (such as depression, anxiety, etc) (kd4qc3z)""","Have you been diagnosed with any of the following (njjh37w)","selfage;gendermale;education","Adults responding to emotional difficulty item","Survey-weighted mean difference (or ordinal regression) in emotional difficulty score by diagnosis status","proposed","Confidence rating: Low (requires scale interpretation)."\n'

PAP_CONTENT = '# Pre-Analysis Plan (Draft)\n\n- Document status: Draft (not frozen)\n- Generated: 2025-10-16T12:44:10Z\n- Seed: 20251016\n- Regeneration: `python analysis/code/bootstrap_setup.py --only pap`\n\n## Scope\n\nThis draft PAP covers preliminary confirmatory planning for three wellbeing, socioeconomic, and relational hypotheses (HYP-001 through HYP-003). Status remains exploratory until design diagnostics and weighting strategy are finalized.\n\n## Data\n\n- Dataset: `childhoodbalancedpublic_original.csv` (n=14,443; p=718) as inspected on 2025-10-16.\n- Inclusion: respondents with non-missing variables required per hypothesis.\n- Survey design: TODO — pending confirmation of weight/strata/cluster variables. Analyses will assume SRS with weights=1 until metadata is verified.\n\n## Hypotheses\n\n1. **HYP-001 (wellbeing)** — Respondents reporting greater childhood emotional abuse will show lower adult self-love scores.\n2. **HYP-002 (socioeconomic)** — Higher perceived childhood class associates with higher current net worth category.\n3. **HYP-003 (relationships)** — Active religious practice is associated with preferring monogamy.\n\n## Outcomes, Predictors, Controls\n\n### HYP-001\n- Outcome: `I love myself (2l8994l)` (Likert; treat as approximately continuous pending scale confirmation).\n- Predictor: `during ages *0-12*: your parents verbally or emotionally abused you (mds78zu)` (ordinal frequency).\n- Controls: `selfage`, `gendermale`, `education`.\n- Estimand: Survey-weighted mean difference across abuse frequency categories; fallback to ordinal regression if Likert assumptions break.\n\n### HYP-002\n- Outcome: `networth` (ordered categories).\n- Predictor: `classchild` (ordered categories).\n- Controls: `selfage`, `gendermale`, `education`.\n- Estimand: Survey-weighted cumulative logit (proportional odds). Will assess proportional odds assumption.\n\n### HYP-003\n- Outcome: `monogamy` (categorical).\n- Predictor: `Do you *currently* actively practice a religion? (902tbll)`.\n- Controls: `selfage`, `gendermale`.\n- Estimand: Survey-weighted multinomial logit relative risk ratios for monogamy preference categories.\n\n## Missing Data Strategy\n\n- Profile missingness for all variables listed above.\n- If missingness > 5% on key variables and plausibly MAR, implement multiple imputation with seed 20251016; otherwise use listwise deletion for preliminary analyses.\n\n## Robustness Checks (pre-specified)\n\n- **HYP-001:** (1) Recode abuse predictor into binary (any vs none). (2) Use ordinal logistic regression for Likert outcome categories.\n- **HYP-002:** (1) Collapse extreme net worth bins to ensure cell size ≥ 10. (2) Fit survey-weighted linear regression on mid-point dollars as sensitivity.\n- **HYP-003:** (1) Restrict sample to respondents currently in relationships. (2) Alternative coding that groups non-monogamous categories together.\n\n## Multiplicity\n\n- Apply Benjamini–Hochberg FDR control at q=0.05 within the set {HYP-001, HYP-002, HYP-003} once confirmatory analyses commence.\n\n## Deviations & Updates\n\n- Any deviations from this draft must be documented in `analysis/pre_analysis_plan.md` with timestamped notes and reason. PAP will be frozen only after survey design validation.\n\n## Reproducibility Notes\n\n- Regenerate this draft with `python analysis/code/bootstrap_setup.py --only pap`.\n- All analyses will honor the global project seed `20251016`.\n'

QC_CONTENT = '# Data Quality Checklist (Bootstrap)\n\nGenerated: 2025-10-16T12:44:10Z  \
Seed: 20251016  \
Regenerate: `python analysis/code/bootstrap_setup.py --only qc`\n\n## Pending Checks\n\n- [ ] Verify dataset schema against `docs/codebook.json`.\n- [ ] Confirm presence/validity of survey weight, strata, and cluster variables.\n- [ ] Inspect missingness patterns for variables referenced in HYP-001 to HYP-003.\n- [ ] Screen for small cells (<10) before publishing tables or plots.\n- [ ] Record outcome variable distributions (Exploratory only).\n\n## Notes\n\nThis checklist is a living document; mark items complete and add diagnostics as the project progresses.\n'

NOTEBOOK_CONTENT = '# Research Notebook (Exploratory)\n\nGenerated: 2025-10-16T12:44:10Z  \
Seed: 20251016  \
Regenerate: `python analysis/code/bootstrap_setup.py --only notebook`\n\n## Datasets\n\n- `childhoodbalancedpublic_original.csv` — 14,443 rows, 718 columns (initial inspection).\n- Additional metadata files: `docs/codebook.json`, `docs/survey_design.yaml`, `config/agent_config.yaml` (placeholders pending validation).\n\n## Work Completed\n\n- Created bootstrap scaffolding for reproducibility artifacts and documentation.\n- Drafted initial hypothesis registry (HYP-001 to HYP-004).\n- Authored preliminary pre-analysis plan covering priority hypotheses.\n- Logged tasks in `artifacts/state.json` and `analysis/decision_log.csv`.\n\n## Candidate Hypotheses (Exploratory)\n\n- `HYP-001`: Childhood emotional abuse ↔ adult self-love score.\n- `HYP-002`: Childhood socioeconomic status ↔ current net worth category.\n- `HYP-003`: Current religious practice ↔ monogamy preference.\n- `HYP-004`: Mental health diagnosis ↔ recent emotional difficulty.\n\n## Immediate Next Steps\n\n1. Validate survey design elements (weights, strata, clusters).\n2. Generate weighted descriptive statistics for outcome and predictor variables.\n3. Assess missingness and coding for variables in the draft PAP.\n\n## Open Questions\n\n- Are official survey weights available, or must we model SRS?\n- How are Likert responses encoded (numeric vs string labels)?\n\n## Reproducibility\n\n- Notebook scaffold is text-only; regenerate via `python analysis/code/bootstrap_setup.py --only notebook`.\n- All future code executed in separate scripts / notebooks with seed `20251016`.\n'

BIBLIOGRAPHY_CONTENT = '@misc{TODO2025bootstrap,\n  title = {Placeholder: Literature on Childhood Context and Adult Wellbeing},\n  author = {{TODO: Author Name}},\n  year = {2025},\n  note = {TODO: Replace with peer-reviewed citation relevant to HYP-001--HYP-004.},\n  howpublished = {\\\\url{TODO}},\n  urldate = {2025-10-16},\n  keywords = {TODO},\n}\n% Regenerate: python analysis/code/bootstrap_setup.py --only bibliography\n'

EVIDENCE_MAP_CONTENT = 'concept,source_id,source_type,quality_rating,notes,status,regeneration_command\nchildhood_context_and_wellbeing,TODO2025bootstrap,placeholder,unrated,"TODO: Replace with validated source linked to HYP-001--HYP-004.",pending,"python analysis/code/bootstrap_setup.py --only evidence_map"\n'

BIBLIOGRAPHY_JSON_CONTENT = '[\n  {\n    "id": "TODO2025bootstrap",\n    "title": "Placeholder: Literature on Childhood Context and Adult Wellbeing",\n    "authors": [\n      "TODO: Author Name"\n    ],\n    "venue": "TODO",\n    "year": null,\n    "url": "TODO",\n    "accessed": "2025-10-16",\n    "notes": "TODO: Replace with peer-reviewed citation relevant to HYP-001--HYP-004.",\n    "regeneration_command": "python analysis/code/bootstrap_setup.py --only bibliography_json"\n  }\n]\n'

DECISION_LOG_CONTENT = 'ts,action,inputs,rationale_short,code_path,outputs,status\n2025-10-16T12:44:10Z,bootstrap,"docs/codebook.json|docs/survey_design.yaml|config/agent_config.yaml","Initialized bootstrap scaffolding, placeholders, and reproducibility script.","analysis/code/bootstrap_setup.py","artifacts/state.json|analysis/hypotheses.csv|analysis/pre_analysis_plan.md","success"\n'

FILES = {
    "codebook": ("docs/codebook.json", CODEBOOK_CONTENT),
    "survey_design": ("docs/survey_design.yaml", SURVEY_DESIGN_CONTENT),
    "agent_config": ("config/agent_config.yaml", AGENT_CONFIG_CONTENT),
    "state": ("artifacts/state.json", STATE_JSON_CONTENT),
    "hypotheses": ("analysis/hypotheses.csv", HYPOTHESES_CSV_CONTENT),
    "pap": ("analysis/pre_analysis_plan.md", PAP_CONTENT),
    "qc": ("qc/data_checks.md", QC_CONTENT),
    "notebook": ("notebooks/research_notebook.md", NOTEBOOK_CONTENT),
    "bibliography": ("lit/bibliography.bib", BIBLIOGRAPHY_CONTENT),
    "evidence_map": ("lit/evidence_map.csv", EVIDENCE_MAP_CONTENT),
    "bibliography_json": ("lit/bibliography.json", BIBLIOGRAPHY_JSON_CONTENT),
    "decision_log": ("analysis/decision_log.csv", DECISION_LOG_CONTENT),
}


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate bootstrap survey-research artifacts.")
    parser.add_argument("--only", nargs="+", help="Subset of artifact keys to regenerate.")
    parser.add_argument("--list", action="store_true", help="List available artifact keys.")
    args = parser.parse_args()

    if args.list:
        for key, (target, _) in FILES.items():
            print(f"{key}: {target}")
        return

    if args.only:
        keys = []
        for raw in args.only:
            key = raw.lower()
            if key not in FILES:
                print(f"[WARN] Unknown artifact key: {raw}", file=sys.stderr)
                continue
            keys.append(key)
        if not keys:
            raise SystemExit("No valid artifact keys selected.")
    else:
        keys = list(FILES.keys())

    for key in keys:
        target, content = FILES[key]
        write_file(Path(target), content)
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
