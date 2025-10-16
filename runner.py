#!/usr/bin/env python3
import os, sys, json, csv, subprocess, re, time, shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("REPO_ROOT", ".")).resolve()
MAIN_BRANCH = os.environ.get("GIT_MAIN_BRANCH", "main")
MODEL = os.environ.get("CODEX_MODEL", "codex-high")
SLEEP_SECONDS = int(os.environ.get("LOOP_SLEEP_SECONDS", "0"))  # set 3600 for hourly
MAX_CONSEC_GIT_FAILS = 2
MAX_CONSEC_PARSE_FAILS = 2

STATE_PATH = REPO / "artifacts" / "state.json"
DECISION_LOG = REPO / "analysis" / "decision_log.csv"
STOP_FLAG = REPO / "artifacts" / "stop.flag"

BOOTSTRAP_SYSTEM = """You are a research automation agent for survey data. Follow rigorous scientific and reproducible standards. Never reveal chain-of-thought. Instead, produce auditable artifacts and a concise Decision Log entry. Your entire reply MUST be a single ```json fenced block containing a top-level JSON object matching the schema below. No other text. If you cannot proceed safely, set "stop_now": true and include a "stop_reason"."""
BOOTSTRAP_USER = """PROJECT CONTEXT
- Repository root is the working directory.
- Inputs we expect (create stubs if absent):
  - docs/codebook.json             (variable names, labels, types, coded values)
  - docs/survey_design.yaml        (weight, strata, cluster, replicate weights if any)
  - config/agent_config.yaml       (use default thresholds if missing; seed=20251016)
- Create the folder structure if missing: analysis/, artifacts/, docs/, figures/, lit/, notebooks/, qc/, reports/, tables/.
- Adopt Decision Log (CSV) at analysis/decision_log.csv with headers:
  ts,action,inputs,rationale_short,code_path,outputs,status

YOUR TASKS (Bootstrap)
1) Sanity checks: presence/validity of codebook, survey design, config. If missing, create well-formed placeholders with TODO notes.
2) Initialize persistence:
   - artifacts/state.json with backlog (prioritized), next_actions, loop_counter=0.
   - analysis/hypotheses.csv (empty template row only).
   - analysis/pre_analysis_plan.md (skeleton, not frozen).
   - qc/data_checks.md (initial checklist).
3) Write a short Research Notebook scaffold at notebooks/research_notebook.md.
4) Propose 3–8 candidate, testable hypotheses grounded in available variables (descriptive or associational only).
5) Produce a minimal Pre‑Analysis Plan draft for 1–3 priority hypotheses (not frozen yet).
6) Add literature stubs in lit/bibliography.bib and lit/evidence_map.csv (placeholders with TODOs).
7) Git checkpoint: request commit with a clear message (see "git" field below).

dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)
OUTPUT PROTOCOL — return ONLY this JSON object in a fenced block:
{
  "files": [  // files to CREATE or OVERWRITE
    {"path": "<relative/path.ext>", "content": "<full file content>", "mode": "text"}
  ],
  "decision_log_row": {
    "ts": "<ISO-8601Z>",
    "action": "bootstrap",
    "inputs": ["docs/codebook.json","docs/survey_design.yaml","config/agent_config.yaml"],
    "rationale_short": "<≤40 words describing what you did>",
    "code_path": "N/A",
    "outputs": ["artifacts/state.json","analysis/hypotheses.csv","analysis/pre_analysis_plan.md"],
    "status": "success"
  },
  "next_actions": [
    {"id":"T-001","priority":1,"desc":"Validate survey weights and replicate design","estimate_min":"15m"},
    {"id":"T-002","priority":2,"desc":"Exploratory weighted summaries for key outcomes","estimate_min":"20m"}
  ],
  "state_update": { "loop_counter": 0 },
  "git": { "commit": true, "message": "feat(bootstrap): init repo structure, state, PAP draft, and hypothesis registry" },
  "stop_now": false,
  "stop_reason": ""
}
EARLY-STOP RULES YOU MUST APPLY
- If PII risk, missing required survey design when codebook references weights, or repo is read-only => set stop_now=true with stop_reason.
"""

LOOP_SYSTEM = """You are a research automation agent continuing a survey-science workflow. Never reveal chain-of-thought; provide artifacts plus a concise Decision Log update. Reply as a single ```json fenced block matching the schema. No extra text."""
LOOP_USER_TEMPLATE = """Per-hour continuation.

Context:
- You may assume prior files exist. If missing, create them.
- Here is a brief state snapshot (may be empty on first runs):
STATE_JSON_START
{state_json}
STATE_JSON_END

Instructions:
- Execute the top backlog item(s) within a ~15m budget.
- Respect privacy; suppress small cells (<10).
- If you detect a fatal condition, set "stop_now": true and state "stop_reason".
- Include a "git" object with commit=true and a good message.
dataset: childhoodbalancedpublic_original.csv (don't edit this file, you can duplicate and edit a copy)

Return ONLY the JSON block per schema (files, decision_log_row, next_actions, state_update, git, stop_now, stop_reason, signals)."""

def run_cmd(cmd, input_bytes=None, check=False):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "ignore"), proc.stderr.decode("utf-8", "ignore")

def run_codex_cli(user_prompt: str, system_prompt: str = None, model: str = MODEL) -> str:
    """
    Adjust this to your codex CLI. This version assumes:
      codex chat -m <model> --system "<system>" 
    The prompt is sent via STDIN.
    """
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    cmd = [codex_bin, "chat", "-m", model]
    if system_prompt:
        cmd += ["--system", system_prompt]
    # Many CLIs accept stdin as the user message. If yours needs -p/--prompt, adapt here:
    # cmd += ["-p", user_prompt]
    rc, out, err = run_cmd(cmd, input_bytes=user_prompt.encode("utf-8"))
    if rc != 0:
        raise RuntimeError(f"codex CLI failed (rc={rc}): {err.strip()}")
    return out

JSON_FENCE_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)

def extract_json_block(text: str):
    m = JSON_FENCE_RE.search(text)
    if m:
        return m.group(1)
    # fallback: try to find first { ... } top-level
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return None

def ensure_repo_structure():
    for p in ["analysis","artifacts","docs","figures","lit","notebooks","qc","reports","tables"]:
        (REPO / p).mkdir(parents=True, exist_ok=True)
    if not DECISION_LOG.exists():
        with DECISION_LOG.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ts","action","inputs","rationale_short","code_path","outputs","status"])

def write_files(files):
    for f in files:
        path = REPO / f["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f.get("content","")
        mode = f.get("mode","text")
        if mode != "text":
            raise ValueError("Only text mode supported in this runner.")
        path.write_text(content, encoding="utf-8")

def append_decision_log(row):
    with DECISION_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            row.get("ts",""),
            row.get("action",""),
            ";".join(row.get("inputs",[])),
            row.get("rationale_short",""),
            row.get("code_path",""),
            ";".join(row.get("outputs",[])),
            row.get("status","")
        ])

def git_checkpoint(message: str):
    cmds = [
        ["git","add","-A"],
        ["git","commit","-m",message],
        ["git","pull","--rebase","origin",MAIN_BRANCH],
        ["git","push","origin",MAIN_BRANCH]
    ]
    for cmd in cmds:
        rc, out, err = run_cmd(cmd)
        # allow "nothing to commit"
        if "nothing to commit" in out.lower() or "nothing to commit" in err.lower():
            continue
        if rc != 0:
            return False, f"{' '.join(cmd)} -> {err.strip() or out.strip()}"
    return True, ""

def read_state_json():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def merge_state(current: dict, update: dict):
    if not update:
        return current
    merged = dict(current)
    for k,v in update.items():
        if k == "loop_counter" and isinstance(v, str) and v.strip() == "+=1":
            merged[k] = int(merged.get(k,0)) + 1
        else:
            merged[k] = v
    return merged

def do_bootstrap():
    ensure_repo_structure()
    print("== Bootstrap session ==")
    raw = run_codex_cli(BOOTSTRAP_USER, BOOTSTRAP_SYSTEM)
    js = extract_json_block(raw)
    if not js:
        raise RuntimeError("Bootstrap: could not find JSON block in model output.")
    data = json.loads(js)
    write_files(data.get("files",[]))
    # Persist state_update if provided
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    if new_state:
        (REPO/"artifacts"/"state.json").write_text(json.dumps(new_state, indent=2), encoding="utf-8")
    # Decision log
    if "decision_log_row" in data:
        append_decision_log(data["decision_log_row"])
    # Git
    git_info = data.get("git",{})
    if git_info.get("commit"):
        ok, err = git_checkpoint(git_info.get("message","chore: checkpoint"))
        if not ok:
            print(f"[git] warning: {err}")
    # Early stop?
    if data.get("stop_now"):
        print(f"Bootstrap requested stop: {data.get('stop_reason')}")
        return True
    return False

def do_loop(iter_ix: int, consecutive_git_fails: int, consecutive_parse_fails: int):
    ensure_repo_structure()
    state_json = read_state_json()
    user_prompt = LOOP_USER_TEMPLATE.format(state_json=json.dumps(state_json, indent=2))
    raw = run_codex_cli(user_prompt, LOOP_SYSTEM)
    js = extract_json_block(raw)
    if not js:
        print(f"[loop {iter_ix}] parse failure: no JSON fenced block.")
        consecutive_parse_fails += 1
        if consecutive_parse_fails >= MAX_CONSEC_PARSE_FAILS:
            print("Too many parse failures; stopping.")
            return True, consecutive_git_fails, consecutive_parse_fails
        return False, consecutive_git_fails, consecutive_parse_fails
    consecutive_parse_fails = 0
    data = json.loads(js)

    write_files(data.get("files",[]))

    # Persist state updates (merge)
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    if new_state:
        (REPO/"artifacts"/"state.json").write_text(json.dumps(new_state, indent=2), encoding="utf-8")

    # Decision log
    if "decision_log_row" in data:
        append_decision_log(data["decision_log_row"])

    # Git
    git_info = data.get("git",{})
    if git_info.get("commit"):
        ok, err = git_checkpoint(git_info.get("message","chore: loop checkpoint"))
        if not ok:
            consecutive_git_fails += 1
            print(f"[git] failure #{consecutive_git_fails}: {err}")
        else:
            consecutive_git_fails = 0

    # Early stops
    if data.get("stop_now"):
        print(f"[loop {iter_ix}] agent requested stop: {data.get('stop_reason')}")
        return True, consecutive_git_fails, consecutive_parse_fails
    if consecutive_git_fails >= MAX_CONSEC_GIT_FAILS:
        print(f"[loop {iter_ix}] too many consecutive git failures; stopping.")
        return True, consecutive_git_fails, consecutive_parse_fails
    if STOP_FLAG.exists():
        print(f"[loop {iter_ix}] stop.flag detected; stopping.")
        return True, consecutive_git_fails, consecutive_parse_fails

    return False, consecutive_git_fails, consecutive_parse_fails

def main():
    os.chdir(REPO)
    # Bootstrap once
    early_stop = do_bootstrap()
    if early_stop:
        sys.exit(0)

    # Run loop 23 times (or until early stop)
    consecutive_git_fails = 0
    consecutive_parse_fails = 0
    for i in range(1, 24):  # 1..23
        print(f"== Loop {i}/23 ==")
        should_stop, consecutive_git_fails, consecutive_parse_fails = do_loop(
            i, consecutive_git_fails, consecutive_parse_fails
        )
        if should_stop:
            break
        if SLEEP_SECONDS > 0 and i < 23:
            time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)
