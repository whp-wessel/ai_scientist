#!/usr/bin/env python3
"""
Direct‑Edit Runner (V1 minimal charter, no JSON handshake)

Purpose:
- Preserve Version 1’s autonomy + constitutional guardrails.
- Remove JSON payload expectations entirely. The agent edits files directly.
- Commit via artifacts/git_message.txt. Push after commit.
- Fail‑fast on V1 non‑negotiables (PAP freeze before confirmatory, small‑cell privacy,
  survey design assertion for confirmatory rows, FDR for confirmatory families).

This file is stdlib‑only.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import os
import platform
import random
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

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
DEFAULT_TOTAL_LOOPS = int(os.environ.get("DEFAULT_TOTAL_LOOPS", "50"))

def _model_descriptor() -> str:
    model = (MODEL or "").strip()
    effort = (REASONING_EFFORT or "").strip()
    if model and effort:
        return f"{model}-{effort}"
    return model or effort

def _print_model_banner() -> None:
    descriptor = _model_descriptor()
    if descriptor:
        print(f"[codex][model] {descriptor}")

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

PROMPT_FILE = REPO / "agents.md"
PROMPT_PATTERN = re.compile(r"<!--PROMPT:([A-Z0-9_]+)-->(.*?)<!--END PROMPT:\1-->", re.DOTALL)
_PROMPT_CACHE: Optional[Dict[str, str]] = None

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

CONTROL_PLANE_PATHS = {
    "artifacts/git_message.txt",
}

# --- Utilities: prompts, commands, reproducibility --------------------------------

def _load_prompts() -> Dict[str, str]:
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    text = PROMPT_FILE.read_text(encoding="utf-8")
    prompts: Dict[str, str] = {}
    for m in PROMPT_PATTERN.finditer(text):
        prompts[m.group(1).strip()] = m.group(2).strip()
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

def run_cmd(cmd, input_bytes=None, check=False):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8","ignore"), proc.stderr.decode("utf-8","ignore")

def _terminate_process(proc: subprocess.Popen) -> None:
    with contextlib.suppress(Exception): proc.terminate()
    try:
        proc.wait(timeout=2); return
    except subprocess.TimeoutExpired:
        pass
    with contextlib.suppress(Exception): proc.kill()
    with contextlib.suppress(Exception): proc.wait(timeout=2)

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

def read_state_json():
    if STATE_PATH.exists():
        try: return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception: return {}
    return {}

def write_state_json(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

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

# --- Non‑negotiable checks (from V1) ---------------------------------------------

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
    indicators = {"weights": False, "strata": False, "clusters": False}
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

def _small_cell_violations(threshold: int = 10) -> List[Tuple[Path, List[Tuple[str,int]]]]:
    public_dirs = [REPO/"tables", REPO/"reports"]
    violations: List[Tuple[Path, List[Tuple[str,int]]]] = []
    for d in public_dirs:
        if not d.exists(): continue
        for p in d.rglob("*.csv"):
            hits = _scan_small_cells_in_csv(p, threshold=threshold)
            if hits:
                violations.append((p, hits[:5]))
    return violations

def _check_small_cell_privacy() -> Tuple[bool, str]:
    violations = _small_cell_violations(threshold=10)
    if not violations: return True, ""
    msg_lines = ["Small-cell privacy check failed (n<10) in public outputs:"]
    for p, hits in violations:
        msg_lines.append(f" - {p.relative_to(REPO)}: {', '.join(f'{c}={v}' for c,v in hits)}")
    return False, "\n".join(msg_lines)

def _pap_status_alert_message() -> Optional[str]:
    """Return a prompt-ready alert when confirmatory work lacks a literal frozen commit header."""
    results_path = REPO/"analysis"/"results.csv"
    if not results_path.exists(): return None
    if not _confirmatory_rows(results_path): return None
    pap_path = REPO/"analysis"/"pre_analysis_plan.md"
    if not pap_path.exists():
        return ("Confirmatory results exist but analysis/pre_analysis_plan.md is missing. "
                "Create it and set the header to `status: frozen (commit <hash>)` referencing the frozen git commit.")
    commit = _pap_frozen_commit()
    if commit: return None
    try:
        text = pap_path.read_text(encoding="utf-8")
    except Exception:
        return None
    status_details = ""
    match = re.search(r"status:\s*frozen\s*\(([^)]*)\)", text, re.IGNORECASE)
    if match:
        status_details = match.group(1).strip()
    if status_details:
        return ("Confirmatory results exist but the PAP header currently reads "
                f"`status: frozen ({status_details})`. Replace it with the literal "
                "`status: frozen (commit <hash>)` form by inserting the git hash behind the freeze tag "
            "(e.g., run `git rev-parse pap_freeze_loop006`).")
    return ("Confirmatory results exist but the PAP header is missing the literal "
            "`status: frozen (commit <hash>)`. Update the header with the frozen git commit hash before continuing.")

def _small_cell_alert_message() -> Optional[str]:
    violations = _small_cell_violations(threshold=10)
    if not violations:
        return None
    summaries = []
    for path, hits in violations[:3]:
        rel = path.relative_to(REPO)
        hit_desc = ", ".join(f"{c}={v}" for c, v in hits)
        summaries.append(f"{rel} ({hit_desc})")
    detail = "; ".join(summaries)
    remaining = len(violations) - len(summaries)
    if remaining > 0:
        detail += f"; +{remaining} more file(s)"
    return (
        "You failed Principle 2 (Privacy): "
        f"{detail}. Please revert these public outputs to the last compliant version "
        "or suppress the n<10 cells, then continue from there."
    )

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
        missing_q = [r for r in rows if (r.get("q_value") is None or str(r.get("q_value")).strip() == "")]
        if missing_q:
            offenders.append(fam)
    if not offenders: return True, ""
    return False, f"Multiplicity/FDR check failed: families without q_value computed: {', '.join(offenders[:10])}"

def perform_nonnegotiable_checks() -> Tuple[bool, str]:
    results_path = REPO/"analysis"/"results.csv"
    if results_path.exists():
        ok, msg = _check_pap_freeze_for_confirmatory(results_path)
        if not ok: return ok, msg
        ok, msg = _check_survey_design_assertion(results_path)
        if not ok: return ok, msg
        ok, msg = _check_multiplicity_fdr(results_path)
        if not ok: return ok, msg
    ok, msg = _check_small_cell_privacy()
    if not ok:
        print(f"[guardrail] Privacy alert (non-blocking): {msg}")
    return True, ""

# --- Change detection & git -------------------------------------------------------

@dataclass
class ChangeRecord:
    path: str
    staged: str
    workspace: str

    def __str__(self) -> str:
        status = f"{self.staged}{self.workspace}".strip() or "??"
        return f"{status} {self.path}"

def _list_changed_files() -> list[ChangeRecord]:
    rc, out, err = run_cmd(["git", "status", "--porcelain=1"])
    if rc != 0:
        raise RuntimeError(f"git status failed: {err.strip() or out.strip()}")
    changes: list[ChangeRecord] = []
    for line in out.splitlines():
        if not line or len(line) < 4: continue
        status = line[:2]
        path_part = line[3:]
        if " -> " in path_part: path_part = path_part.split(" -> ", 1)[1]
        changes.append(ChangeRecord(path=path_part.strip(), staged=status[0], workspace=status[1]))
    return changes

def git_checkpoint(message: str, push: bool = True, record_head: bool = True):
    repo_path = str(REPO.resolve())

    def _run_git(args: list[str]) -> tuple[int, str, str]:
        cmd = ["git", "-C", repo_path] + args
        return run_cmd(cmd)

    def _record_head() -> None:
        rc, out, _ = _run_git(["rev-parse", "HEAD"])
        head = out.strip() if rc == 0 else ""
        (REPO / "artifacts").mkdir(parents=True, exist_ok=True)
        (REPO / "artifacts" / "last_commit.txt").write_text(head + "\n", encoding="utf-8")

    base_cmds = [
        ["add", "-A"],
        ["commit", "-m", message],
    ]
    for args in base_cmds:
        rc, out, err = _run_git(args)
        text_lower = f"{out}\n{err}".lower()
        if "nothing to commit" in text_lower:
            continue
        if rc != 0:
            cmd_display = " ".join(["git", "-C", repo_path, *args])
            return False, f"{cmd_display} -> {err.strip() or out.strip()}"

    push_failed = False
    if push:
        push_cmd = ["push", "origin", MAIN_BRANCH]
        rc, out, err = _run_git(push_cmd)
        if rc != 0:
            push_failed = True
            reason = err.strip() or out.strip() or "push failed"
            print(f"[git] warning: {' '.join(['git', '-C', repo_path, *push_cmd])} -> {reason}")

    if record_head:
        _record_head()
    if push_failed:
        return True, ""
    return True, ""

def _read_git_message() -> Optional[str]:
    path = REPO / "artifacts" / "git_message.txt"
    if not path.exists(): return None
    try: text = path.read_text(encoding="utf-8")
    except Exception: return None
    message = ""
    for line in text.splitlines():
        line = line.strip()
        if line:
            message = line
            break
    with contextlib.suppress(FileNotFoundError):
        path.unlink()
    return message or None

def maybe_commit(loop_idx: Optional[int], changes: Sequence[ChangeRecord]) -> tuple[bool, str]:
    if not changes:
        msg = _read_git_message()
        if msg:
            print("[git] git_message.txt provided but there are no changes to commit; ignoring.")
        return True, ""
    message = _read_git_message() or (f"chore: {'bootstrap' if not loop_idx or loop_idx<=0 else f'loop_{loop_idx:03d}'}")
    return git_checkpoint(message)

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

def log_runner_decision(action: str, changes: Sequence[ChangeRecord], status: str, note: str, inputs: Optional[Sequence[str]] = None) -> None:
    append_decision_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "inputs": list(inputs or []),
        "rationale_short": note[:80],
        "code_path": "runner.py",
        "outputs": [rec.path for rec in changes][:20],
        "status": status,
    })

def _write_raw_output(tag: str, content: str, *, update_latest: bool = True) -> None:
    if not isinstance(content, str): content = str(content)
    raw_dir = REPO / "artifacts" / "llm_raw"; raw_dir.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^0-9A-Za-z_.-]", "_", str(tag)) or "output"
    target = raw_dir / f"{safe_tag}.txt"; target.write_text(content, encoding="utf-8")
    if update_latest: (REPO / "artifacts" / "last_model_raw.txt").write_text(content, encoding="utf-8")

# --- Review automation (unchanged philosophy) ------------------------------------

REVIEW_SECTION_RE = re.compile(r"^##\s+Loop\s+(\d+)[^\n]*\n([\s\S]*?)(?=^##\s+Loop\s+\d+|\Z)", re.MULTILINE)

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

def run_loop_review(loop_idx: int, changes: Sequence[ChangeRecord]) -> tuple[bool, str]:
    try:
        review_system = get_prompt("REVIEW_SYSTEM")
        review_user_template = get_prompt("REVIEW_USER_TEMPLATE")
    except KeyError:
        print(f"[review {loop_idx:03d}] prompts missing; skipping automated review.")
        return False, ""
    state_snapshot = ensure_state_defaults(read_state_json())
    state_json = json.dumps(state_snapshot, indent=2, sort_keys=True)
    file_lines = "\n".join(f"- {str(rec)}" for rec in changes) if changes else "(none)"
    user_prompt = review_user_template.format(loop_index=f"{loop_idx:03d}", state_json=state_json, files_written=file_lines)
    try:
        raw_review = run_codex_cli(user_prompt, review_system)
    except Exception as exc:
        print(f"[review {loop_idx:03d}] error invoking reviewer: {exc}"); return False, ""
    _write_raw_output(f"review_{loop_idx:03d}", raw_review, update_latest=False)
    review_text = raw_review.strip()
    review_dir = REPO / "review"; review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / "research_findings.md"
    if not review_file.exists():
        review_file.write_text("# Science Agent Review Findings\n\n", encoding="utf-8")
    timestamp = datetime.now(timezone.utc).isoformat()
    entry_lines = [f"## Loop {loop_idx:03d} — {timestamp}", review_text or "DECISION: CONTINUE", ""]
    with review_file.open("a", encoding="utf-8") as fh: fh.write("\n".join(entry_lines) + "\n")
    # Detect STOP
    m = re.search(r"(?im)^DECISION\s*:\s*(STOP)\b", review_text)
    if m: 
        reason = review_text.splitlines()[0]
        return True, reason
    return False, ""

# --- Core execution ---------------------------------------------------------------

def _ensure_clean_worktree(context: str) -> None:
    rc, out, err = run_cmd(["git", "status", "--porcelain=1"])
    if rc != 0:
        raise RuntimeError(f"git status failed: {err.strip() or out.strip()}")
    if out.strip():
        # Auto-snapshot any pre-existing changes to avoid mixing runs
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[runner] auto-committing pre-existing change(s) before {context}.")
        ok, err = git_checkpoint(f"chore: pre-run snapshot before {context} ({stamp})", push=False, record_head=False)
        if not ok:
            raise RuntimeError(f"Auto-commit failed: {err}")

def do_bootstrap():
    ensure_repo_structure()
    try:
        _ensure_clean_worktree("bootstrap")
    except RuntimeError as exc:
        print(f"[bootstrap] {exc}"); return True
    update_reproducibility()
    print("== Bootstrap session ==")
    _print_model_banner()
    bootstrap_system = get_prompt("BOOTSTRAP_SYSTEM")
    bootstrap_user = get_prompt("BOOTSTRAP_USER")
    small_cell_alert = _small_cell_alert_message()
    if small_cell_alert:
        bootstrap_user = f"{bootstrap_user}\nNon-negotiable alert: {small_cell_alert}"
    try:
        raw = run_codex_cli(bootstrap_user, bootstrap_system)
    except Exception as exc:
        state = ensure_state_defaults(read_state_json()); state["last_abort"] = {"ts": datetime.now(timezone.utc).isoformat(), "phase":"bootstrap", "note": str(exc)}
        write_state_json(state)
        print("[bootstrap] cancelled or failed."); return True
    _write_raw_output("bootstrap", raw, update_latest=True)

    # V1 fail-fast checks
    ok, msg = perform_nonnegotiable_checks()
    if not ok:
        print(f"[bootstrap] STOP: {msg}")
        return True

    changes = _list_changed_files()
    log_runner_decision("bootstrap", changes, "success", "runner auto-log", inputs=[f"phase:{read_state_json().get('phase','?')}"])
    ok_git, err = maybe_commit(None, changes)
    if not ok_git: print(f"[git] warning: {err}")

    # mark bootstrap complete
    state = ensure_state_defaults(read_state_json())
    if not state.get("bootstrap_complete"): 
        state["bootstrap_complete"] = True
        write_state_json(state)

    latest_state = ensure_state_defaults(read_state_json())
    if latest_state.get("stop_now"):
        reason = latest_state.get("stop_reason", "unspecified")
        print(f"Bootstrap requested stop: {reason}")
        return True
    return False

def do_loop(iter_ix: int, consecutive_git_fails: int):
    ensure_repo_structure()
    try:
        _ensure_clean_worktree(f"loop {iter_ix:03d}")
    except RuntimeError as exc:
        print(f"[loop {iter_ix}] {exc}")
        return True, consecutive_git_fails
    update_reproducibility()
    _print_model_banner()
    loop_system = get_prompt("LOOP_SYSTEM")
    user_template = get_prompt("LOOP_USER_TEMPLATE")
    state_snapshot = ensure_state_defaults(read_state_json())
    state_json = json.dumps(state_snapshot, indent=2, sort_keys=True)
    user_prompt = user_template.format(loop_index=f"{iter_ix:03d}", state_json=state_json)

    # Provide progress note (non-binding)
    loops_remaining = max(int(state_snapshot.get("total_loops", DEFAULT_TOTAL_LOOPS)) - int(state_snapshot.get("loop_counter", 0)), 0)
    progress_note = (
        f"\nLoop progress: completed={state_snapshot.get('loop_counter', 0)}, "
        f"remaining={loops_remaining}, total={state_snapshot.get('total_loops', DEFAULT_TOTAL_LOOPS)}."
    )
    if NETWORK_ACCESS: progress_note += f" Network access={NETWORK_ACCESS}."
    review_log_path = REPO / "review" / "research_findings.md"
    if review_log_path.exists():
        try: rel_review = review_log_path.relative_to(REPO)
        except ValueError: rel_review = review_log_path
        progress_note += f" Review log: {rel_review}."
    user_prompt += progress_note
    pap_alert = _pap_status_alert_message()
    if pap_alert:
        user_prompt += f"\nNon-negotiable alert: {pap_alert}"
    small_cell_alert = _small_cell_alert_message()
    if small_cell_alert:
        user_prompt += f"\nNon-negotiable alert: {small_cell_alert}"

    try:
        raw = run_codex_cli(user_prompt, loop_system)
    except Exception as exc:
        state = ensure_state_defaults(read_state_json()); state["last_abort"] = {"ts": datetime.now(timezone.utc).isoformat(), "phase":"loop", "loop": iter_ix, "note": str(exc)}
        write_state_json(state)
        print(f"[loop {iter_ix}] cancelled or failed.")
        return True, consecutive_git_fails

    _write_raw_output(f"loop_{iter_ix:03d}", raw, update_latest=True)

    # Guardrails
    ok, msg = perform_nonnegotiable_checks()
    if not ok:
        print(f"[loop {iter_ix}] STOP (non-negotiable): {msg}")
        return True, consecutive_git_fails

    changes = _list_changed_files()
    log_runner_decision(f"loop_{iter_ix:03d}", changes, "success", "runner auto-log", inputs=[f"phase:{read_state_json().get('phase','?')}"])
    ok_git, err = maybe_commit(iter_ix, changes)
    if not ok_git:
        consecutive_git_fails += 1
        print(f"[git] failure #{consecutive_git_fails}: {err}")
    else:
        consecutive_git_fails = 0

    latest_state = ensure_state_defaults(read_state_json())
    if latest_state.get("stop_now"):
        print(f"[loop {iter_ix}] agent requested stop: {latest_state.get('stop_reason', 'unspecified')}")
        return True, consecutive_git_fails
    if consecutive_git_fails >= MAX_CONSEC_GIT_FAILS:
        print(f"[loop {iter_ix}] too many consecutive git failures; stopping.")
        return True, consecutive_git_fails
    if STOP_FLAG.exists():
        print(f"[loop {iter_ix}] stop.flag detected; stopping.")
        return True, consecutive_git_fails

    # Reviewer
    review_stop, review_reason = run_loop_review(iter_ix, changes)
    # Record loop counter
    state = ensure_state_defaults(read_state_json())
    if iter_ix > state.get("loop_counter", 0):
        state["loop_counter"] = iter_ix
        write_state_json(state)
    if review_stop:
        print(f"[loop {iter_ix}] automated review requested stop: {review_reason}")
        return True, consecutive_git_fails
    return False, consecutive_git_fails

def run_loop_batch(start_loop: int, loops_to_run: int, sleep_seconds: Optional[float]) -> bool:
    consecutive_git_fails = 0
    final_loop = start_loop + loops_to_run - 1
    for loop_idx in range(start_loop, final_loop + 1):
        print(f"== Loop {loop_idx} / target {final_loop} ==")
        try:
            should_stop, consecutive_git_fails = do_loop(loop_idx, consecutive_git_fails)
        except KeyboardInterrupt:
            # mark abort
            state = ensure_state_defaults(read_state_json()); state["last_abort"] = {"ts": datetime.now(timezone.utc).isoformat(), "phase":"loop", "loop": loop_idx, "note":"Interrupted mid-loop"}
            write_state_json(state)
            print(f"[loop {loop_idx}] cancelled by user.")
            return True
        if should_stop: return True
        if sleep_seconds and sleep_seconds > 0 and loop_idx < final_loop:
            try: time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                next_loop = loop_idx + 1
                state = ensure_state_defaults(read_state_json()); state["last_abort"] = {"ts": datetime.now(timezone.utc).isoformat(), "phase":"loop", "loop": next_loop, "note":"Interrupted during inter-loop delay"}
                write_state_json(state)
                print(f"[loop {next_loop}] cancelled during sleep before start.")
                return True
    return False

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or resume the survey science agent (direct‑edit).")
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
    loops_to_run = args.loops if args.loops is not None else max(total_loops - completed_loops, 0)
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
            state_after_interrupt["last_abort"] = {"ts": datetime.now(timezone.utc).isoformat(), "phase":"runner", "note":"Interrupted outside loop batch"}
            write_state_json(state_after_interrupt)
        print("[runner] interrupted by user."); return 130
    if stopped: print("[runner] loop sequence halted early.")
    else: print("[runner] loop sequence finished.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"[runner] interrupted by user.", file=sys.stderr); sys.exit(130)
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr); sys.exit(1)
