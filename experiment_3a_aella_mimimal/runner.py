#!/usr/bin/env python3
"""
Merged Runner: Robust mechanics (from V2) + Constitutional guardrails (from V1)
and programmatic checks for non-negotiables:

Checks (fail-fast STOP):
  1) PAP freeze gate: If confirmatory results exist, require pre_analysis_plan.md has
     'status: frozen (commit <hash>)' and that <hash> is an ancestor of HEAD.
  2) Small-cell privacy: Any CSV under tables/ (and reports/) must not contain cells
     with n<10 in columns named like ['n','count','freq','frequency'] (case-insensitive).
  3) Survey design assertion: If codebook/config indicates weights/strata/clusters,
     then confirmatory results must either set design_used=true OR provide srs_justification.
  4) Multiplicity/FDR: For any confirmatory hypothesis_family with >1 test, require
     q_value present and non-null; assert FDR control.

This file is self-contained (stdlib only).
"""

from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import os, sys, json, csv, subprocess, re, time, hashlib, platform, random
from typing import Any, Dict, Optional, Tuple, List, Iterable
from datetime import datetime, timezone
from pathlib import Path

# --- Repo & runtime configuration -------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR
repo_root_override = os.environ.get("REPO_ROOT")
if repo_root_override:
    override_path = Path(repo_root_override)
    if not override_path.is_absolute():
        override_path = (SCRIPT_DIR / override_path).resolve()
    else:
        override_path = override_path.resolve()
    REPO = override_path
MAIN_BRANCH = os.environ.get("GIT_MAIN_BRANCH", "main")
MODEL = os.environ.get("CODEX_MODEL", "gpt-5-codex")
REASONING_EFFORT = os.environ.get("CODEX_REASONING_EFFORT", "high")
SLEEP_SECONDS = int(os.environ.get("LOOP_SLEEP_SECONDS", "0"))
MAX_CONSEC_GIT_FAILS = 2
MAX_CONSEC_PARSE_FAILS = 2

def _normalize_network_setting(value: str) -> str:
    val = value.strip().lower()
    if val in {"on", "enable", "enabled", "true", "1", "yes"}:
        return "enabled"
    if val in {"off", "disable", "disabled", "false", "0", "no"}:
        return "disabled"
    return val

_network_raw = os.environ.get("CODEX_NETWORK_ACCESS") or os.environ.get("CODEX_ALLOW_NET")
NETWORK_ACCESS = _normalize_network_setting(_network_raw) if _network_raw else ""

STATE_PATH = REPO / "artifacts" / "state.json"
DECISION_LOG = REPO / "analysis" / "decision_log.csv"
STOP_FLAG = REPO / "artifacts" / "stop.flag"
LAST_ABORT_PATH = REPO / "artifacts" / "last_abort.json"

PHASE_ORDER: list[str] = [
    "literature",
    "pap",
    "analysis",
    "sensitivity",
    "writing",
    "review",
    "release",
]

ALLOWED_TOP_LEVEL_DIRS = {
    "analysis","artifacts","docs","figures","lit","notebooks","outputs","qc",
    "reports","tables","papers","config","scripts","manuscript","review","qa","tmp",
    ".github",".codex",
}
ALLOWED_ROOT_FILE_EXTS = {
    ".md",".txt",".py",".yaml",".yml",".json",".csv",".tex",".rst",".ini",".cfg",".toml",".lock",".sh",".env",".gitignore",".bat",".ps1",
}
ALLOWED_ROOT_FILENAMES = {"Makefile","LICENSE","Dockerfile","Procfile","README","README.md"}
ALLOWED_BINARY_SUFFIXES = {".png",".pdf",".jpg",".jpeg",".gif",".svg"}
MAX_BINARY_FILE_BYTES = int(os.environ.get("RUNNER_MAX_BINARY_BYTES", 25 * 1024 * 1024))

class UserAbort(Exception): pass

# --- Prompt loading from agents.md ----------------------------------------------

DEFAULT_TOTAL_LOOPS = int(os.environ.get("DEFAULT_TOTAL_LOOPS", "50"))

PROMPT_FILE = REPO / "agents.md"
PROMPT_PATTERN = re.compile(r"<!--PROMPT:([A-Z0-9_]+)-->(.*?)<!--END PROMPT:\1-->", re.DOTALL)
_PROMPT_CACHE: Optional[Dict[str, str]] = None

def _load_prompts() -> Dict[str, str]:
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    text = PROMPT_FILE.read_text(encoding="utf-8")
    prompts: Dict[str, str] = {}
    for match in PROMPT_PATTERN.finditer(text):
        prompts[match.group(1).strip()] = match.group(2).strip()
    if not prompts:
        raise RuntimeError("No prompt blocks found in agents.md")
    return prompts

def get_prompt(name: str) -> str:
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        _PROMPT_CACHE = _load_prompts()
    if name not in _PROMPT_CACHE:
        raise KeyError(f"Prompt '{name}' missing from agents.md")
    return _PROMPT_CACHE[name]

# --- Helpers ---------------------------------------------------------------------

JSON_FENCE_RE = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
REVIEW_SECTION_RE = re.compile(r"^##\s+Loop\s+(\d+)[^\n]*\n([\s\S]*?)(?=^##\s+Loop\s+\d+|\Z)", re.MULTILINE)

def extract_json_block(text: str):
    m = JSON_FENCE_RE.search(text)
    candidate = m.group(1) if m else None
    if not candidate:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
    if not candidate:
        return None
    l, r = candidate.find("{"), candidate.rfind("}")
    return candidate[l:r+1] if (l != -1 and r != -1 and r > l) else None

def _record_invalid_json(tag: str, payload: str) -> Path:
    safe_tag = re.sub(r"[^0-9A-Za-z_.-]", "_", str(tag))
    path = REPO / "artifacts" / f"invalid_json_{safe_tag}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path

def run_cmd(cmd, input_bytes=None, check=False):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "ignore"), proc.stderr.decode("utf-8", "ignore")

def _terminate_process(proc: subprocess.Popen) -> None:
    with contextlib.suppress(Exception): proc.terminate()
    try:
        proc.wait(timeout=2); return
    except subprocess.TimeoutExpired:
        pass
    with contextlib.suppress(Exception): proc.kill()
    with contextlib.suppress(Exception): proc.wait(timeout=2)

def mark_user_abort(phase: str, loop_idx: Optional[int] = None, note: str | None = None) -> None:
    record: Dict[str, Any] = {"ts": datetime.now(timezone.utc).isoformat(), "phase": phase}
    if loop_idx is not None: record["loop"] = loop_idx
    if note: record["note"] = note
    state = read_state_json()
    current = ensure_state_defaults(state)
    current["last_abort"] = record
    write_state_json(current)
    LAST_ABORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAST_ABORT_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")

def clear_user_abort(phase: str | None = None, loop_idx: Optional[int] = None) -> None:
    state = read_state_json()
    current = ensure_state_defaults(state)
    last = current.get("last_abort")
    if not isinstance(last, dict): return
    if phase is not None and last.get("phase") != phase: return
    if phase == "loop" and loop_idx is not None:
        last_loop = last.get("loop")
        if last_loop is not None and loop_idx < last_loop: return
    if "last_abort" in current:
        current.pop("last_abort", None); write_state_json(current)
    if LAST_ABORT_PATH.exists():
        with contextlib.suppress(Exception): LAST_ABORT_PATH.unlink()

def _combine_prompts(user_prompt: str, system_prompt: str | None) -> str:
    if not system_prompt: return user_prompt
    return "\n\n".join(["<<SYS>>", system_prompt.strip(), "<</SYS>>", "<<USER>>", user_prompt.strip(), "<</USER>>"])

def _print_codex_event(label: str, text: str | None = None):
    snippet = ""
    if text:
        clean = text.strip()
        snippet = clean[:280] + (" …" if len(clean) > 280 else "")
    msg = f"[codex][{label}]"
    if snippet: msg += f" {snippet}"
    print(msg, flush=True)

def _handle_codex_line(line: str, last_message: str | None) -> str | None:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        _print_codex_event("raw", line); return last_message
    ev_type = event.get("type", "?")
    if ev_type == "item.completed":
        item = event.get("item", {})
        item_type = item.get("type", "?")
        text = item.get("text", "")
        _print_codex_event(item_type, text)
        if item_type == "agent_message": return text
        return last_message
    if ev_type == "turn.started":
        _print_codex_event("turn", "started")
    elif ev_type == "turn.completed":
        usage = event.get("usage", {}); summary = ", ".join(f"{k}={v}" for k, v in usage.items()) if usage else "completed"
        _print_codex_event("turn", summary)
    elif ev_type == "thread.started":
        _print_codex_event("thread", f"id={event.get('thread_id','?')}")
    else:
        _print_codex_event(ev_type, json.dumps(event, ensure_ascii=False))
    return last_message

def run_codex_cli(user_prompt: str, system_prompt: str = None, model: str = MODEL, retries: int = 2) -> str:
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    prompt = _combine_prompts(user_prompt, system_prompt)
    cmd = [codex_bin, "exec", "--json", "-m", model]
    if REASONING_EFFORT: cmd += ["-c", f"model_reasoning_effort=\"{REASONING_EFFORT}\""]
    if NETWORK_ACCESS:   cmd += ["-c", f"network_access=\"{NETWORK_ACCESS}\""]
    cmd.append("-")
    last_err = ""
    for attempt in range(retries + 1):
        try:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        except FileNotFoundError as e:
            raise RuntimeError(f"codex executable not found: {e}")
        stderr_text = ""; rc: Optional[int] = None; last_message = None
        try:
            if proc.stdin:
                try: proc.stdin.write(prompt)
                except BrokenPipeError: pass
                finally: proc.stdin.close()
            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if not line: continue
                    last_message = _handle_codex_line(line, last_message)
        finally:
            if proc.stdout: proc.stdout.close()
            if proc.stderr:
                try: stderr_text = proc.stderr.read().strip()
                except Exception: stderr_text = ""
                proc.stderr.close()
            try: rc = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _terminate_process(proc)
                try: rc = proc.wait(timeout=5)
                except subprocess.TimeoutExpired: rc = proc.poll()
        if stderr_text: _print_codex_event("stderr", stderr_text)
        if rc == 0 and last_message: return last_message
        last_err = stderr_text or f"exit={rc}, no agent message"
        time.sleep(0.7 * (attempt + 1))
    raise RuntimeError(f"codex CLI failed after {retries+1} attempts: {last_err}")

def ensure_repo_structure():
    for p in ["analysis","artifacts","artifacts/llm_raw","docs","figures","lit","notebooks","outputs","qc","reports","tables","papers","review"]:
        (REPO / p).mkdir(parents=True, exist_ok=True)
    if not DECISION_LOG.exists():
        with DECISION_LOG.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ts","action","inputs","rationale_short","code_path","outputs","status"])

def _resolve_and_validate_path(path_str: str) -> Path:
    if not isinstance(path_str, str): raise ValueError("File path must be a string.")
    clean = path_str.strip()
    if not clean: raise ValueError("File path cannot be empty.")
    if "\x00" in clean: raise ValueError("File path contains null bytes.")
    path = Path(clean)
    if path.is_absolute(): raise ValueError("Absolute paths are not permitted.")
    parts = path.parts
    for part in parts:
        if part in {"",".."}: raise ValueError(f"Path traversal detected in '{path_str}'.")
        if part == "." and len(parts) == 1: raise ValueError("Writing to '.' is not permitted.")
    resolved = (REPO / path).resolve()
    try: rel_path = resolved.relative_to(REPO)
    except ValueError as exc: raise ValueError(f"Path escapes repository root: '{path_str}'") from exc
    if not rel_path.parts: raise ValueError("Cannot write to repository root.")
    top = rel_path.parts[0]
    if len(rel_path.parts) == 1:
        suffix = resolved.suffix.lower(); root_name = rel_path.parts[0]
        if suffix not in ALLOWED_ROOT_FILE_EXTS and root_name not in ALLOWED_ROOT_FILENAMES:
            raise ValueError(f"Writing '{path_str}' at repo root is not allowed.")
    else:
        if top not in ALLOWED_TOP_LEVEL_DIRS:
            raise ValueError(f"Top-level directory '{top}' is not allowed for writes.")
    return resolved

def write_files(files):
    for f in files:
        path_str = f.get("path"); resolved_path = _resolve_and_validate_path(path_str)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        mode = f.get("mode", "text")
        if mode == "text":
            content = f.get("content", "")
            if not isinstance(content, str): raise ValueError(f"Text mode requires string content for '{path_str}'.")
            resolved_path.write_text(content, encoding="utf-8")
        elif mode in {"base64","binary"}:
            content = f.get("content", "")
            if not isinstance(content, str): raise ValueError(f"{mode} mode requires base64 string content for '{path_str}'.")
            try: payload = base64.b64decode(content, validate=True)
            except (binascii.Error, ValueError) as exc: raise ValueError(f"Invalid base64 payload for '{path_str}'.") from exc
            if len(payload) > MAX_BINARY_FILE_BYTES: raise ValueError(f"Binary payload too large for '{path_str}'.")
            suffix = resolved_path.suffix.lower()
            if suffix not in ALLOWED_BINARY_SUFFIXES: raise ValueError(f"Binary writes limited to {sorted(ALLOWED_BINARY_SUFFIXES)}; got '{suffix}' for '{path_str}'.")
            resolved_path.write_bytes(payload)
        else:
            raise ValueError(f"Unsupported file mode '{mode}' for '{path_str}'.")

def _validate_file_entry(entry: dict) -> None:
    if not isinstance(entry, dict): raise ValueError("Each file entry must be a dict.")
    if "path" not in entry: raise ValueError("File entry missing 'path'.")
    _resolve_and_validate_path(entry["path"])
    mode = entry.get("mode", "text")
    if not isinstance(mode, str): raise ValueError(f"File mode for '{entry['path']}' must be a string.")
    if mode not in {"text","base64","binary"}: raise ValueError(f"Unsupported file mode '{mode}' for '{entry['path']}'.")
    content = entry.get("content","")
    if mode == "text":
        if not isinstance(content, str): raise ValueError(f"Text mode requires string content for '{entry['path']}'.")
    else:
        if not isinstance(content, str): raise ValueError(f"{mode} mode requires base64 content for '{entry['path']}'.")

def validate_payload(data: Any, context: str) -> None:
    if not isinstance(data, dict): raise ValueError(f"{context}: JSON payload must be an object.")
    files = data.get("files")
    if files is None or not isinstance(files, list): raise ValueError(f"{context}: 'files' must be a list.")
    for entry in files: _validate_file_entry(entry)
    decision_log = data.get("decision_log_row")
    if decision_log is not None and not isinstance(decision_log, dict): raise ValueError(f"{context}: 'decision_log_row' must be an object when provided.")
    git_info = data.get("git")
    if git_info is None or not isinstance(git_info, dict): raise ValueError(f"{context}: 'git' field must be provided as an object.")
    commit_flag = git_info.get("commit")
    if not isinstance(commit_flag, bool): raise ValueError(f"{context}: 'git.commit' must be boolean.")
    if commit_flag:
        message = git_info.get("message", "")
        if not isinstance(message, str) or not message.strip(): raise ValueError(f"{context}: commit requested but 'git.message' is missing or empty.")
    elif "message" in git_info and git_info.get("message") is not None and not isinstance(git_info.get("message"), str):
        raise ValueError(f"{context}: 'git.message' must be a string when provided.")
    stop_now = data.get("stop_now")
    if not isinstance(stop_now, bool): raise ValueError(f"{context}: 'stop_now' must be boolean.")
    if "stop_reason" in data and data["stop_reason"] is not None and not isinstance(data["stop_reason"], str):
        raise ValueError(f"{context}: 'stop_reason' must be a string when provided.")
    if "next_actions" in data and data["next_actions"] is not None and not isinstance(data["next_actions"], list):
        raise ValueError(f"{context}: 'next_actions' must be a list when provided.")
    state_update = data.get("state_update")
    if state_update is not None and not isinstance(state_update, dict):
        raise ValueError(f"{context}: 'state_update' must be an object when provided.")
    signals = data.get("signals")
    if signals is None or not isinstance(signals, dict):
        raise ValueError(f"{context}: 'signals' must be provided as an object.")
    phase = signals.get("phase")
    if not isinstance(phase, str): raise ValueError(f"{context}: 'signals.phase' must be a string.")
    if phase not in PHASE_ORDER: raise ValueError(f"{context}: 'signals.phase' must be one of {PHASE_ORDER}.")
    notes_val = signals.get("notes", "")
    if not isinstance(notes_val, str): raise ValueError(f"{context}: 'signals.notes' must be a string when provided.")

def _write_raw_output(tag: str, content: str, *, update_latest: bool = True) -> None:
    if not isinstance(content, str): content = str(content)
    raw_dir = REPO / "artifacts" / "llm_raw"; raw_dir.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^0-9A-Za-z_.-]", "_", str(tag)) or "output"
    target = raw_dir / f"{safe_tag}.txt"; target.write_text(content, encoding="utf-8")
    if update_latest: (REPO / "artifacts" / "last_model_raw.txt").write_text(content, encoding="utf-8")

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
        if "nothing to commit" in out.lower() or "nothing to commit" in err.lower(): continue
        if rc != 0: return False, f"{' '.join(cmd)} -> {err.strip() or out.strip()}"
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"])
    head = out.strip() if rc == 0 else ""
    (REPO/"artifacts"/"last_commit.txt").write_text(head + "\n", encoding="utf-8")
    return True, ""

def read_state_json():
    if STATE_PATH.exists():
        try: return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception: return {}
    return {}

def write_state_json(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

def merge_state(current: Dict[str, Any], update: Dict[str, Any]):
    if not update: return current
    merged = dict(current)
    for k, v in update.items():
        if k == "loop_counter" and isinstance(v, str) and v.strip() == "+=1":
            merged[k] = int(merged.get(k, 0)) + 1
        elif k == "advance_phase" and v:
            cur_phase = str(merged.get("phase", "literature"))
            try: idx = PHASE_ORDER.index(cur_phase)
            except ValueError: idx = -1
            next_idx = min(idx + 1, len(PHASE_ORDER) - 1)
            merged["phase"] = PHASE_ORDER[next_idx]; merged["phase_ix"] = next_idx
        else:
            merged[k] = v
    return merged

def ensure_state_defaults(state: Dict[str, Any], total_loops: Optional[int] = None) -> Dict[str, Any]:
    updated = dict(state)
    if "loop_counter" not in updated or not isinstance(updated.get("loop_counter"), int):
        try: updated["loop_counter"] = int(updated.get("loop_counter", 0) or 0)
        except Exception: updated["loop_counter"] = 0
    if total_loops is not None: updated["total_loops"] = max(int(total_loops), 0)
    elif "total_loops" not in updated: updated["total_loops"] = DEFAULT_TOTAL_LOOPS
    updated.setdefault("bootstrap_complete", False)
    phase = updated.get("phase")
    if phase not in PHASE_ORDER: updated["phase"] = "literature"; updated["phase_ix"] = 0
    else: updated["phase_ix"] = PHASE_ORDER.index(updated["phase"])
    return updated

def _build_phase_user_prompt(base_template: str, state_snapshot: Dict[str, Any]) -> str:
    phase = str(state_snapshot.get("phase", "literature"))
    state_prompt = json.dumps(state_snapshot, indent=2)
    phase_key = f"PHASE_{phase.upper()}"
    try: phase_block = get_prompt(phase_key)
    except KeyError: phase_block = ""
    prefix = ""
    if phase_block:
        prefix = "\n\n=== PHASE CONTEXT START ===\n" + phase_block + "\n=== PHASE CONTEXT END ===\n\n"
    return base_template.format(state_json=state_prompt) + prefix + f"\n(Current phase: {phase})\n"

def record_loop_counter(loop_idx: int) -> None:
    state = read_state_json(); current = ensure_state_defaults(state)
    if loop_idx > current.get("loop_counter", 0):
        current["loop_counter"] = loop_idx; write_state_json(current)

# --- Reproducibility utilities ----------------------------------------------------

def read_seed_from_config(default_seed: int = 20251016) -> int:
    cfg = REPO / "config" / "agent_config.yaml"
    if not cfg.exists(): return default_seed
    try:
        text = cfg.read_text(encoding="utf-8")
        m = re.search(r"(?m)^\s*seed\s*:\s*(\d+)\s*$", text)
        if m: return int(m.group(1))
    except Exception: pass
    return default_seed

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def snapshot_checksums():
    targets = []
    for base in ["data/raw","data/clean"]:
        base_path = REPO / base
        if base_path.exists():
            for p in base_path.rglob("*"):
                if p.is_file() and p.suffix.lower() in (".csv",".tsv",".parquet"): targets.append(p)
    info = []
    for p in targets:
        rel = str(p.relative_to(REPO))
        try:
            info.append({"path": rel,"sha256": compute_sha256(p),"size_bytes": p.stat().st_size,"mtime": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()})
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
    if NETWORK_ACCESS: lines.append(f"network_access: {NETWORK_ACCESS}")
    lines.append(f"seed: {seed}")
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"])
    if rc == 0: lines.append(f"git_head: {out.strip()}")
    rc, out, _ = run_cmd(["git","status","-sb"])
    if rc == 0:
        lines.append("git_status: |")
        for ln in out.splitlines(): lines.append(f"  {ln}")
    rc, out, _ = run_cmd([sys.executable,"-m","pip","freeze"])
    if rc == 0 and out.strip():
        lines.append("pip_freeze: |")
        for ln in out.splitlines(): lines.append(f"  {ln}")
    (REPO/"artifacts"/"session_info.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_repro_report():
    rc, out, _ = run_cmd(["git","rev-parse","HEAD"]); head = out.strip() if rc == 0 else ""
    report = [
        "# Reproducibility Report","","- Generated: " + datetime.now(timezone.utc).isoformat(),
        f"- Git HEAD: {head or '<unknown>'}", f"- Model: {MODEL}", f"- Network access: {NETWORK_ACCESS or 'not specified'}","",
        "Artifacts:","- artifacts/session_info.txt","- artifacts/checksums.json","- artifacts/llm_raw/loop_XXX.txt","- analysis/decision_log.csv","",
        "Principle: Any figure/table/result must be regenerable from code committed at the cited HEAD, with the recorded seed and environment."
    ]
    (REPO/"artifacts"/"repro_report.md").write_text("\n".join(report), encoding="utf-8")

def update_reproducibility():
    seed = read_seed_from_config()
    os.environ["PYTHONHASHSEED"] = str(seed); os.environ["AGENT_SEED"] = str(seed)
    try: random.seed(seed)
    except Exception: pass
    try:
        import numpy as _np  # optional
        _np.random.seed(seed)
    except Exception: pass
    write_session_info(seed)
    snapshot_checksums()
    write_repro_report()
    (REPO/"artifacts"/"seed.txt").write_text(str(seed) + "\n", encoding="utf-8")

# --- Programmatic Non-Negotiable Checks ------------------------------------------

def _read_csv_rows(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []

def _str2bool(x: Any) -> Optional[bool]:
    if isinstance(x, bool): return x
    if x is None: return None
    s = str(x).strip().lower()
    if s in {"true","1","yes","y"}: return True
    if s in {"false","0","no","n"}: return False
    return None

def _detect_survey_design_features() -> Dict[str, bool]:
    """Heuristically detect presence of weights/strata/clusters."""
    indicators = {"weights": False, "strata": False, "clusters": False}
    # Look for common config/codebook files
    candidates = [
        REPO/"data"/"codebook.json",
        REPO/"config"/"survey_design.yaml",
        REPO/"config"/"survey_design.yml",
        REPO/"config"/"survey_design.json",
        REPO/"data"/"codebook.yaml",
        REPO/"data"/"codebook.yml",
    ]
    for p in candidates:
        if not p.exists(): continue
        try:
            text = p.read_text(encoding="utf-8").lower()
        except Exception:
            continue
        for key in indicators.keys():
            if re.search(rf"\b{key}\b", text): indicators[key] = True
    return indicators

def _confirmatory_rows(results_path: Path) -> List[Dict[str,str]]:
    rows = _read_csv_rows(results_path)
    out = []
    for r in rows:
        # multiple possible schema names
        conf = _str2bool(r.get("confirmatory")) or _str2bool(r.get("is_confirmatory"))
        rtype = (r.get("result_type","") or "").strip().lower()
        status = (r.get("status","") or "").strip().lower()
        if conf is True or rtype == "confirmatory" or status == "confirmatory":
            out.append(r)
    return out

def _pap_frozen_commit() -> Optional[str]:
    pap = REPO/"analysis"/"pre_analysis_plan.md"
    if not pap.exists(): return None
    try:
        text = pap.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r"status:\s*frozen\s*\(commit\s+([0-9a-fA-F]{7,40})\)", text, re.IGNORECASE)
    return m.group(1) if m else None

def _git_commit_is_ancestor(commit_hash: str) -> bool:
    rc, _, _ = run_cmd(["git","merge-base","--is-ancestor", commit_hash, "HEAD"])
    return rc == 0

def _check_pap_freeze_for_confirmatory(results_path: Path) -> Tuple[bool, str]:
    conf_rows = _confirmatory_rows(results_path)
    if not conf_rows: return True, ""
    commit = _pap_frozen_commit()
    if not commit:
        return False, "PAP freeze check failed: confirmatory results present but PAP not marked 'status: frozen (commit <hash>)'."
    if not _git_commit_is_ancestor(commit):
        return False, f"PAP freeze check failed: frozen commit {commit} is not an ancestor of HEAD."
    return True, ""

def _scan_small_cells_in_csv(path: Path, threshold: int = 10) -> List[Tuple[str,int]]:
    rows = _read_csv_rows(path)
    if not rows: return []
    count_cols = {"n","count","freq","frequency"}
    hits: List[Tuple[str,int]] = []
    # detect relevant columns present
    present_cols = [c for c in rows[0].keys() if c and c.strip().lower() in count_cols]
    for c in present_cols:
        for r in rows:
            val = r.get(c)
            try:
                if val is None: continue
                v = int(float(str(val).strip()))
                if v < threshold:
                    hits.append((c, v))
            except Exception:
                continue
    return hits

def _check_small_cell_privacy() -> Tuple[bool, str]:
    public_dirs = [REPO/"tables", REPO/"reports"]
    violations = []
    for d in public_dirs:
        if not d.exists(): continue
        for p in d.rglob("*.csv"):
            hits = _scan_small_cells_in_csv(p, threshold=10)
            if hits:
                violations.append((p, hits[:5]))  # cap for message
    if not violations: return True, ""
    msg_lines = ["Small-cell privacy check failed (n<10) in public outputs:"]
    for p, hits in violations:
        msg_lines.append(f" - {p.relative_to(REPO)}: {', '.join(f'{c}={v}' for c,v in hits)}")
    return False, "\n".join(msg_lines)

def _check_survey_design_assertion(results_path: Path) -> Tuple[bool, str]:
    indicators = _detect_survey_design_features()
    requires_design = any(indicators.values())
    if not requires_design: return True, ""
    conf_rows = _confirmatory_rows(results_path)
    if not conf_rows: return True, ""
    missing = 0
    for r in conf_rows:
        design_used = _str2bool(r.get("design_used"))
        srs_just = (r.get("srs_justification","") or "").strip()
        if design_used is True: continue
        if srs_just: continue
        missing += 1
    if missing == 0: return True, ""
    return False, f"Survey design check failed: {missing} confirmatory rows lack design_used=true and missing srs_justification."

def _check_multiplicity_fdr(results_path: Path) -> Tuple[bool, str]:
    conf_rows = _confirmatory_rows(results_path)
    if not conf_rows: return True, ""
    by_family: Dict[str, List[Dict[str,str]]] = {}
    for r in conf_rows:
        fam = (r.get("hypothesis_family") or r.get("family") or "").strip()
        if not fam: fam = "<unlabeled>"
        by_family.setdefault(fam, []).append(r)
    offenders = []
    for fam, rows in by_family.items():
        if len(rows) <= 1: continue
        # require q_value present & non-empty for all rows in family
        missing_q = [r for r in rows if (r.get("q_value") is None or str(r.get("q_value")).strip() == "")]
        if missing_q:
            offenders.append(fam)
    if not offenders: return True, ""
    return False, f"Multiplicity/FDR check failed: families without q_value computed: {', '.join(offenders[:10])}"

def perform_nonnegotiable_checks() -> Tuple[bool, str]:
    """Run all fail-fast checks. Returns (ok, message)."""
    # Only proceed if results exist
    results_path = REPO/"analysis"/"results.csv"
    if results_path.exists():
        ok, msg = _check_pap_freeze_for_confirmatory(results_path)
        if not ok: return ok, msg
        ok, msg = _check_survey_design_assertion(results_path)
        if not ok: return ok, msg
        ok, msg = _check_multiplicity_fdr(results_path)
        if not ok: return ok, msg
    ok, msg = _check_small_cell_privacy()
    if not ok: return ok, msg
    return True, ""

# --- Core execution ---------------------------------------------------------------

def do_bootstrap():
    ensure_repo_structure()
    update_reproducibility()
    print("== Bootstrap session ==")
    bootstrap_system = get_prompt("BOOTSTRAP_SYSTEM")
    bootstrap_user = get_prompt("BOOTSTRAP_USER")
    parse_failures = 0
    while True:
        try:
            raw = run_codex_cli(bootstrap_user, bootstrap_system)
        except UserAbort:
            mark_user_abort("bootstrap", note="Interrupted during bootstrap")
            print("[bootstrap] cancelled by user."); return True
        _write_raw_output("bootstrap", raw, update_latest=True)
        js = extract_json_block(raw)
        if not js:
            parse_failures += 1
            print(f"[bootstrap] parse failure: missing JSON block (attempt {parse_failures}/{MAX_CONSEC_PARSE_FAILS}).")
            if parse_failures >= MAX_CONSEC_PARSE_FAILS:
                raise RuntimeError("Bootstrap: could not find JSON block in model output after retries.")
            continue
        try:
            data = json.loads(js); break
        except json.JSONDecodeError as err:
            parse_failures += 1
            fragment_path = _record_invalid_json(f"bootstrap_{parse_failures:02d}", js)
            try: rel_fragment = fragment_path.relative_to(REPO)
            except ValueError: rel_fragment = fragment_path
            print(f"[bootstrap] invalid JSON ({err}) attempt {parse_failures}/{MAX_CONSEC_PARSE_FAILS}. Saved: {rel_fragment}.")
            if parse_failures >= MAX_CONSEC_PARSE_FAILS:
                raise RuntimeError(f"Bootstrap invalid JSON after retries: {err}") from err
    validate_payload(data, "bootstrap")
    write_files(data.get("files",[]))
    # Persist state_update
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    new_state = ensure_state_defaults(new_state)
    new_state["bootstrap_complete"] = True
    write_state_json(new_state)
    clear_user_abort("bootstrap")
    # Decision log
    if "decision_log_row" in data: append_decision_log(data["decision_log_row"])
    # Programmatic checks (allow bootstrap to pass unless public tables already emitted)
    ok, msg = perform_nonnegotiable_checks()
    if not ok:
        print(f"[bootstrap] STOP: {msg}")
        return True
    # Git
    git_info = data.get("git",{})
    if git_info.get("commit"):
        ok_git, err = git_checkpoint(git_info.get("message","chore: checkpoint"))
        if not ok_git: print(f"[git] warning: {err}")
    # Early stop?
    if data.get("stop_now"):
        print(f"Bootstrap requested stop: {data.get('stop_reason')}"); 
        state_with_flag = read_state_json()
        if state_with_flag.get("bootstrap_complete", False) and data.get("stop_now"):
            state_with_flag["bootstrap_complete"] = False; write_state_json(state_with_flag)
        return True
    return False

def _get_review_entry(loop_idx: int) -> str:
    if loop_idx < 1: return ""
    review_path = REPO / "review" / "research_findings.md"
    if not review_path.exists(): return ""
    try: text = review_path.read_text(encoding="utf-8")
    except Exception: return ""
    for match in REVIEW_SECTION_RE.finditer(text):
        try: recorded_loop = int(match.group(1))
        except (TypeError, ValueError): continue
        if recorded_loop == loop_idx: return match.group(2).strip()
    return ""

def run_loop_review(loop_idx: int, agent_payload: Dict[str, Any]) -> tuple[bool, str]:
    try:
        review_system = get_prompt("REVIEW_SYSTEM")
        review_user_template = get_prompt("REVIEW_USER_TEMPLATE")
    except KeyError:
        print(f"[review {loop_idx:03d}] prompts missing; skipping automated review.")
        return False, ""
    state_snapshot = ensure_state_defaults(read_state_json())
    state_json = json.dumps(state_snapshot, indent=2, sort_keys=True)
    payload_json = json.dumps(agent_payload, indent=2, sort_keys=True)
    files = agent_payload.get("files")
    if isinstance(files, list) and files:
        file_lines = "\n".join(f"- {entry.get('path','<missing path>')}" for entry in files if isinstance(entry, dict))
    else:
        file_lines = "(none)"
    user_prompt = review_user_template.format(loop_index=f"{loop_idx:03d}", state_json=state_json, agent_payload_json=payload_json, files_written=file_lines)
    try:
        raw_review = run_codex_cli(user_prompt, review_system)
    except UserAbort:
        mark_user_abort("review", loop_idx, note="Interrupted during review generation"); raise
    except Exception as exc:
        print(f"[review {loop_idx:03d}] error invoking reviewer: {exc}"); return False, ""
    _write_raw_output(f"review_{loop_idx:03d}", raw_review, update_latest=False)
    review_text = raw_review.strip()
    review_dir = REPO / "review"; review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / "research_findings.md"
    if not review_file.exists(): review_file.write_text("# Science Agent Review Findings\n\n", encoding="utf-8")
    review_payload = review_text if review_text else "DECISION: CONTINUE\nNotes: Reviewer response was empty."
    review_payload = review_payload.strip()
    timestamp = datetime.now(timezone.utc).isoformat()
    entry_lines = [f"## Loop {loop_idx:03d} — {timestamp}", review_payload, ""]
    with review_file.open("a", encoding="utf-8") as fh: fh.write("\n".join(entry_lines) + "\n")
    decision_line = ""
    for line in review_payload.splitlines():
        stripped = line.strip()
        if stripped: decision_line = stripped; break
    if not decision_line.upper().startswith("DECISION"): return False, ""
    decision_value = decision_line.split(":", 1)[1].strip() if ":" in decision_line else ""
    if not decision_value: return False, ""
    if decision_value.upper().startswith("STOP"):
        reason = decision_value[len("STOP"):].strip(" –-") or "review requested stop"
        return True, reason
    return False, ""

def do_loop(iter_ix: int, consecutive_git_fails: int, consecutive_parse_fails: int):
    ensure_repo_structure()
    update_reproducibility()
    loop_system = get_prompt("LOOP_SYSTEM")
    user_template = get_prompt("LOOP_USER_TEMPLATE")
    state_snapshot = ensure_state_defaults(read_state_json())
    user_prompt = _build_phase_user_prompt(user_template, state_snapshot)
    loops_remaining = max(int(state_snapshot.get("total_loops", DEFAULT_TOTAL_LOOPS)) - int(state_snapshot.get("loop_counter", 0)), 0)
    progress_note = f"\nLoop progress: completed={state_snapshot.get('loop_counter', 0)}, remaining={loops_remaining}, total={state_snapshot.get('total_loops', DEFAULT_TOTAL_LOOPS)}."
    if NETWORK_ACCESS: progress_note += f" Network access={NETWORK_ACCESS}."
    review_log_path = REPO / "review" / "research_findings.md"
    if review_log_path.exists():
        rel_review = review_log_path.relative_to(REPO)
        progress_note += f" Review log: {rel_review}; acknowledge how you addressed the most recent critiques."
    prior_loop_idx = iter_ix - 1
    if prior_loop_idx >= 1:
        prior_notes = _get_review_entry(prior_loop_idx)
        if prior_notes:
            progress_note += f"\nLatest review findings (loop {prior_loop_idx:03d}):\n{prior_notes}\nDocument in your decision_log how you handled each item."
    user_prompt = user_prompt + progress_note

    try:
        raw = run_codex_cli(user_prompt, loop_system)
    except UserAbort:
        mark_user_abort("loop", iter_ix, note="Interrupted during loop execution")
        print(f"[loop {iter_ix}] cancelled by user.")
        return True, consecutive_git_fails, consecutive_parse_fails
    _write_raw_output(f"loop_{iter_ix:03d}", raw, update_latest=True)
    js = extract_json_block(raw)
    if not js:
        print(f"[loop {iter_ix}] parse failure: no JSON fenced block.")
        consecutive_parse_fails += 1
        if consecutive_parse_fails >= MAX_CONSEC_PARSE_FAILS:
            print("Too many parse failures; stopping.")
            return True, consecutive_git_fails, consecutive_parse_fails
        return False, consecutive_git_fails, consecutive_parse_fails
    try:
        data = json.loads(js)
    except json.JSONDecodeError as err:
        consecutive_parse_fails += 1
        fragment_path = _record_invalid_json(f"loop_{iter_ix:03d}", js)
        try: rel_fragment = fragment_path.relative_to(REPO)
        except ValueError: rel_fragment = fragment_path
        print(f"[loop {iter_ix}] invalid JSON ({err}). Saved fragment to {rel_fragment}.")
        if consecutive_parse_fails >= MAX_CONSEC_PARSE_FAILS:
            print("Too many parse failures; stopping.")
            return True, consecutive_git_fails, consecutive_parse_fails
        return False, consecutive_git_fails, consecutive_parse_fails
    consecutive_parse_fails = 0

    try:
        validate_payload(data, f"loop_{iter_ix}")
    except ValueError as exc:
        print(f"[loop {iter_ix}] payload validation error: {exc}")
        return True, consecutive_git_fails, consecutive_parse_fails

    # Write files from agent
    write_files(data.get("files",[]))

    # Persist state updates (merge)
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    new_state = ensure_state_defaults(new_state)
    write_state_json(new_state)
    clear_user_abort("loop", iter_ix)

    # Decision log
    if "decision_log_row" in data: append_decision_log(data["decision_log_row"])

    # === Non-negotiable programmatic checks (fail fast, before git) ===
    ok, msg = perform_nonnegotiable_checks()
    if not ok:
        print(f"[loop {iter_ix}] STOP (non-negotiable): {msg}")
        return True, consecutive_git_fails, consecutive_parse_fails

    # Git (only if checks passed)
    git_info = data.get("git",{})
    if git_info.get("commit"):
        ok_git, err = git_checkpoint(git_info.get("message","chore: loop checkpoint"))
        if not ok_git:
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

    # Automated review after successful write + checks (so reviewer sees artifacts)
    review_stop, review_reason = run_loop_review(iter_ix, data)
    record_loop_counter(iter_ix)
    if review_stop:
        print(f"[loop {iter_ix}] automated review requested stop: {review_reason}")
        return True, consecutive_git_fails, consecutive_parse_fails
    return False, consecutive_git_fails, consecutive_parse_fails

def run_loop_batch(start_loop: int, loops_to_run: int, sleep_seconds: Optional[float]) -> bool:
    consecutive_git_fails = 0; consecutive_parse_fails = 0
    final_loop = start_loop + loops_to_run - 1
    for loop_idx in range(start_loop, final_loop + 1):
        print(f"== Loop {loop_idx} / target {final_loop} ==")
        try:
            should_stop, consecutive_git_fails, consecutive_parse_fails = do_loop(loop_idx, consecutive_git_fails, consecutive_parse_fails)
        except KeyboardInterrupt:
            mark_user_abort("loop", loop_idx, note="Interrupted mid-loop")
            print(f"[loop {loop_idx}] cancelled by user.")
            return True
        if should_stop: return True
        if sleep_seconds and sleep_seconds > 0 and loop_idx < final_loop:
            try: time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                next_loop = loop_idx + 1
                mark_user_abort("loop", next_loop, note="Interrupted during inter-loop delay")
                print(f"[loop {next_loop}] cancelled during sleep before start.")
                return True
    return False

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or resume the survey science agent (merged).")
    parser.add_argument("--dry-run", action="store_true", help="Refresh reproducibility artifacts without invoking the agent.")
    parser.add_argument("--loops", type=int, default=None, help="Number of loops to execute this run (defaults to remaining loops).")
    parser.add_argument("--total-loops", type=int, default=None, help=f"Override total loop budget (default {DEFAULT_TOTAL_LOOPS}). Stored in state.")
    parser.add_argument("--force-bootstrap", action="store_true", help="Run bootstrap even if already completed.")
    parser.add_argument("--skip-bootstrap", action="store_true", help="Skip bootstrap even if not marked complete.")
    parser.add_argument("--sleep-seconds", type=float, default=None, help="Pause between loops (overrides LOOP_SLEEP_SECONDS).")
    parser.add_argument("--model", type=str, default=None, help="Override the Codex model for this run.")
    parser.add_argument("--reasoning-effort", type=str, default=None, help="Override model_reasoning_effort.")
    parser.add_argument("--network-access", type=str, default=None, help="Override network_access setting ('enabled' or 'disabled').")
    args = parser.parse_args(argv)
    if args.loops is not None and args.loops <= 0: parser.error("--loops must be a positive integer")
    if args.total_loops is not None and args.total_loops <= 0: parser.error("--total-loops must be a positive integer")
    if args.force_bootstrap and args.skip_bootstrap: parser.error("Use only one of --force-bootstrap or --skip-bootstrap")
    return args

def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    global MODEL, REASONING_EFFORT, NETWORK_ACCESS
    if args.model: MODEL = args.model
    if args.reasoning_effort: REASONING_EFFORT = args.reasoning_effort
    if args.network_access:
        override = _normalize_network_setting(args.network_access)
        NETWORK_ACCESS = override if override in {"enabled","disabled"} else args.network_access

    ensure_repo_structure(); os.chdir(REPO)
    if args.dry_run:
        print("[dry-run] ensuring structure + reproducibility snapshots only")
        update_reproducibility(); return 0

    # Load and persist state defaults
    state_before = read_state_json()
    state = ensure_state_defaults(state_before, args.total_loops)
    if state != state_before: write_state_json(state)

    bootstrap_complete = bool(state.get("bootstrap_complete"))
    bootstrap_needed = args.force_bootstrap or (not bootstrap_complete and not args.skip_bootstrap)
    if not bootstrap_complete and args.skip_bootstrap and not args.force_bootstrap:
        print("[runner] WARNING: bootstrap not marked complete but skipping as requested.")

    if bootstrap_needed:
        early_stop = do_bootstrap()
        if early_stop: return 0
        state = ensure_state_defaults(read_state_json(), args.total_loops); write_state_json(state)

    raw_state_after = read_state_json()
    state = ensure_state_defaults(raw_state_after, args.total_loops)
    if state != raw_state_after: write_state_json(state)

    last_abort = state.get("last_abort")
    if isinstance(last_abort, dict):
        phase = last_abort.get("phase", "unknown")
        loop_note = f", loop={last_abort.get('loop')}" if last_abort.get("loop") is not None else ""
        extra = f" ({last_abort.get('note')})" if last_abort.get("note") else ""
        print(f"[runner] prior session ended early (phase={phase}{loop_note}){extra}.")

    total_loops = int(state.get("total_loops", DEFAULT_TOTAL_LOOPS))
    completed_loops = int(state.get("loop_counter", 0))
    if args.loops is not None:
        loops_to_run = args.loops
    else:
        loops_to_run = max(total_loops - completed_loops, 0)
    if loops_to_run <= 0:
        print(f"[runner] No loops to run (completed={completed_loops}, total={total_loops})."); return 0

    start_loop = completed_loops + 1
    final_loop = start_loop + loops_to_run - 1
    print(f"[runner] executing loops {start_loop}..{final_loop} (completed={completed_loops}, total={total_loops}).")
    sleep_seconds = args.sleep_seconds if args.sleep_seconds is not None else SLEEP_SECONDS
    try:
        stopped = run_loop_batch(start_loop, loops_to_run, sleep_seconds)
    except KeyboardInterrupt:
        state_after_interrupt = read_state_json()
        if not isinstance(state_after_interrupt.get("last_abort"), dict):
            mark_user_abort("runner", note="Interrupted outside loop batch")
        print("[runner] interrupted by user."); return 130
    if stopped: print("[runner] loop sequence halted early.")
    else: print("[runner] loop sequence finished.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except UserAbort as exc:
        print(f"[runner] interrupted by user: {exc}", file=sys.stderr); sys.exit(130)
    except KeyboardInterrupt:
        print(f"[runner] interrupted by user.", file=sys.stderr); sys.exit(130)
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr); sys.exit(1)
