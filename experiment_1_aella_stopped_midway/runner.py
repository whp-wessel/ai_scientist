#!/usr/bin/env python3
"""
Runner for the Survey Science Agent.

Key principles:
- The agent must emit a single ```json fenced block (see BOOTSTRAP/LOOP system prompts).
- All actions must be logged to analysis/decision_log.csv.
- **Reproducibility-first:** Everything—including experiments/analyses—must be reproducible.
  This runner snapshots environment info and dataset checksums on each run, records raw
  model output, and captures git HEAD after commits.

This file is self-contained (stdlib only).
"""

import os, sys, json, csv, subprocess, re, time, shutil, hashlib, platform, random
from datetime import datetime, timezone
from pathlib import Path

# --- Repo & runtime configuration -------------------------------------------------

REPO = Path(os.environ.get("REPO_ROOT", ".")).resolve()
MAIN_BRANCH = os.environ.get("GIT_MAIN_BRANCH", "main")
MODEL = os.environ.get("CODEX_MODEL", "gpt-5-codex")
REASONING_EFFORT = os.environ.get("CODEX_REASONING_EFFORT", "high")
SLEEP_SECONDS = int(os.environ.get("LOOP_SLEEP_SECONDS", "0"))  # set 3600 for hourly
MAX_CONSEC_GIT_FAILS = 2
MAX_CONSEC_PARSE_FAILS = 2

STATE_PATH = REPO / "artifacts" / "state.json"
DECISION_LOG = REPO / "analysis" / "decision_log.csv"
STOP_FLAG = REPO / "artifacts" / "stop.flag"

# --- System / user prompts sent to the model -------------------------------------

BOOTSTRAP_SYSTEM = """You are a research automation agent for survey data.
Follow rigorous scientific and reproducible standards. Never reveal chain-of-thought.
Instead, produce auditable artifacts and a concise Decision Log entry.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be
fully reproducible given the recorded seed and environment. Every output must be
regenerable from versioned code and documented commands. Always log seeds used.

Your entire reply MUST be a single ```json fenced block containing a top-level JSON
object matching the schema below. No other text. If you cannot proceed safely, set
"stop_now": true and include a "stop_reason"."""
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

**Reproducibility requirement:** Provide explicit regeneration commands for each artifact you create
and record any random seeds. Prefer deterministic operations.

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

LOOP_SYSTEM = """You are a research automation agent continuing a survey-science workflow.
Never reveal chain-of-thought; provide artifacts plus a concise Decision Log update.

**Reproducibility requirement:** Everything — including experiments/analyses — MUST be
fully reproducible with the recorded seed and environment. Any randomness must be seeded
and logged. Include regeneration commands in MANIFEST-style notes where appropriate.

Reply as a single ```json fenced block matching the schema. No extra text."""
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

# --- Helpers ---------------------------------------------------------------------

# Robust fenced-JSON extractor: capture the content within ```json ... ``` even if
# nested braces appear inside, or fall back to outermost { ... }.
JSON_FENCE_RE = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)

def extract_json_block(text: str):
    m = JSON_FENCE_RE.search(text)
    candidate = None
    if m:
        candidate = m.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
    if not candidate:
        return None
    l = candidate.find("{")
    r = candidate.rfind("}")
    if l != -1 and r != -1 and r > l:
        return candidate[l:r+1]
    return None

def run_cmd(cmd, input_bytes=None, check=False):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "ignore"), proc.stderr.decode("utf-8", "ignore")

def _combine_prompts(user_prompt: str, system_prompt: str | None) -> str:
    if not system_prompt:
        return user_prompt
    return "\n\n".join([
        "<<SYS>>",
        system_prompt.strip(),
        "<</SYS>>",
        "<<USER>>",
        user_prompt.strip(),
        "<</USER>>"
    ])


def _parse_codex_jsonl(stream: str) -> str:
    last_message = None
    for line in stream.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                last_message = item.get("text", "")
    if last_message is None:
        raise ValueError("No agent_message found in codex output")
    return last_message


def run_codex_cli(user_prompt: str, system_prompt: str = None, model: str = MODEL, retries: int = 2) -> str:
    """Invoke the codex CLI using JSONL streaming output."""
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    prompt = _combine_prompts(user_prompt, system_prompt)
    cmd = [codex_bin, "exec", "--json", "-m", model]
    if REASONING_EFFORT:
        cmd += ["-c", f"model_reasoning_effort=\"{REASONING_EFFORT}\""]
    cmd.append("-")
    last_err = ""
    for attempt in range(retries + 1):
        rc, out, err = run_cmd(cmd, input_bytes=prompt.encode("utf-8"))
        if rc == 0:
            try:
                return _parse_codex_jsonl(out)
            except Exception as parse_exc:
                last_err = f"parse failure: {parse_exc}"
        else:
            last_err = err.strip() or out.strip()
        time.sleep(0.7 * (attempt + 1))
    raise RuntimeError(f"codex CLI failed after {retries+1} attempts: {last_err}")

def ensure_repo_structure():
    for p in ["analysis","artifacts","docs","figures","lit","notebooks","qc","reports","tables","papers"]:
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
    # record HEAD after (attempted) push
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"])
    head = out.strip() if rc == 0 else ""
    (REPO/"artifacts"/"last_commit.txt").write_text(head + "\n", encoding="utf-8")
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

# --- Reproducibility utilities ----------------------------------------------------

def read_seed_from_config(default_seed: int = 20251016) -> int:
    cfg = REPO / "config" / "agent_config.yaml"
    if not cfg.exists():
        return default_seed
    try:
        text = cfg.read_text(encoding="utf-8")
        m = re.search(r"(?m)^\s*seed\s*:\s*(\d+)\s*$", text)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return default_seed

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def snapshot_checksums():
    targets = []
    for base in ["data/raw","data/clean"]:
        base_path = REPO / base
        if base_path.exists():
            for p in base_path.rglob("*"):
                if p.is_file() and p.suffix.lower() in (".csv",".tsv",".parquet"):
                    targets.append(p)
    info = []
    for p in targets:
        rel = str(p.relative_to(REPO))
        try:
            info.append({
                "path": rel,
                "sha256": compute_sha256(p),
                "size_bytes": p.stat().st_size,
                "mtime": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
            })
        except Exception as e:
            info.append({"path": rel, "error": str(e)})
    (REPO/"artifacts").mkdir(parents=True, exist_ok=True)
    (REPO/"artifacts"/"checksums.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

def write_session_info(seed: int):
    lines = []
    lines.append(f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"python: {sys.version.splitlines()[0]}")
    lines.append(f"platform: {platform.platform()}")
    lines.append(f"cwd: {str(REPO)}")
    lines.append(f"model: {MODEL}")
    lines.append(f"seed: {seed}")
    # git head
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"])
    if rc == 0:
        lines.append(f"git_head: {out.strip()}")
    # git status (short)
    rc, out, _ = run_cmd(["git","status","-sb"])
    if rc == 0:
        lines.append("git_status: |")
        for ln in out.splitlines():
            lines.append(f"  {ln}")
    # pip freeze (best-effort)
    rc, out, _ = run_cmd([sys.executable,"-m","pip","freeze"])
    if rc == 0 and out.strip():
        lines.append("pip_freeze: |")
        for ln in out.splitlines():
            lines.append(f"  {ln}")
    (REPO/"artifacts"/"session_info.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_repro_report():
    """Human-readable summary tying together reproducibility artifacts."""
    head = ""
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"])
    if rc == 0:
        head = out.strip()
    report = [
        "# Reproducibility Report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Git HEAD: {head or '<unknown>'}",
        f"- Model: {MODEL}",
        "",
        "Artifacts:",
        "- artifacts/session_info.txt  (env + packages + HEAD)",
        "- artifacts/checksums.json    (dataset file hashes)",
        "- artifacts/last_model_raw.txt (last raw LLM output)",
        "- analysis/decision_log.csv   (append-only action log)",
        "",
        "Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD,",
        "with the recorded seed and environment. If randomness is used, it must be seeded and logged.",
        ""
    ]
    (REPO/"artifacts"/"repro_report.md").write_text("\n".join(report), encoding="utf-8")

def update_reproducibility():
    seed = read_seed_from_config()
    # set deterministic seeds where applicable
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["AGENT_SEED"] = str(seed)
    try:
        random.seed(seed)
    except Exception:
        pass
    try:
        import numpy as _np  # optional
        _np.random.seed(seed)
    except Exception:
        pass
    write_session_info(seed)
    snapshot_checksums()
    write_repro_report()
    (REPO/"artifacts"/"seed.txt").write_text(str(seed) + "\n", encoding="utf-8")

# --- Core execution ---------------------------------------------------------------

def do_bootstrap():
    ensure_repo_structure()
    update_reproducibility()
    print("== Bootstrap session ==")
    raw = run_codex_cli(BOOTSTRAP_USER, BOOTSTRAP_SYSTEM)
    (REPO/"artifacts"/"last_model_raw.txt").write_text(raw, encoding="utf-8")
    js = extract_json_block(raw)
    if not js:
        raise RuntimeError("Bootstrap: could not find JSON block in model output.")
    data = json.loads(js)
    # Minimal schema presence
    for k in ("files","decision_log_row","git","stop_now"):
        if k not in data:
            raise RuntimeError(f"Bootstrap: missing required key '{k}' in model JSON.")
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
    update_reproducibility()
    state_json = read_state_json()
    user_prompt = LOOP_USER_TEMPLATE.format(state_json=json.dumps(state_json, indent=2))
    raw = run_codex_cli(user_prompt, LOOP_SYSTEM)
    (REPO/"artifacts"/"last_model_raw.txt").write_text(raw, encoding="utf-8")
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
    if "--dry-run" in sys.argv:
        print("[dry-run] ensuring structure + reproducibility snapshots only")
        ensure_repo_structure()
        update_reproducibility()
        sys.exit(0)

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