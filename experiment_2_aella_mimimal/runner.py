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

from __future__ import annotations

import argparse
import contextlib
import os, sys, json, csv, subprocess, re, time, hashlib, platform, random
from typing import Any, Dict, Optional
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
SLEEP_SECONDS = int(os.environ.get("LOOP_SLEEP_SECONDS", "0"))  # set 3600 for hourly
MAX_CONSEC_GIT_FAILS = 2
MAX_CONSEC_PARSE_FAILS = 2


def _normalize_network_setting(value: str) -> str:
    val = value.strip().lower()
    if val in {"on", "enable", "enabled", "true", "1", "yes"}:
        return "enabled"
    if val in {"off", "disable", "disabled", "false", "0", "no"}:
        return "disabled"
    return val


_network_raw = os.environ.get("CODEX_NETWORK_ACCESS")
if _network_raw is None:
    _network_raw = os.environ.get("CODEX_ALLOW_NET")
NETWORK_ACCESS = _normalize_network_setting(_network_raw) if _network_raw else ""

STATE_PATH = REPO / "artifacts" / "state.json"
DECISION_LOG = REPO / "analysis" / "decision_log.csv"
STOP_FLAG = REPO / "artifacts" / "stop.flag"
LAST_ABORT_PATH = REPO / "artifacts" / "last_abort.json"


class UserAbort(Exception):
    """Raised when the runner is interrupted by the user (e.g., Ctrl+C)."""


    pass

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
        name = match.group(1).strip()
        body = match.group(2).strip()
        prompts[name] = body
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


def _record_invalid_json(tag: str, payload: str) -> Path:
    """Persist invalid JSON fragments for post-mortem debugging."""

    safe_tag = tag.replace("/", "_")
    path = REPO / "artifacts" / f"invalid_json_{safe_tag}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return path


def run_cmd(cmd, input_bytes=None, check=False):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "ignore"), proc.stderr.decode("utf-8", "ignore")


def _terminate_process(proc: subprocess.Popen) -> None:
    """Best-effort termination helper that swallows common failures."""

    with contextlib.suppress(Exception):
        proc.terminate()
    try:
        proc.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    with contextlib.suppress(Exception):
        proc.kill()
    with contextlib.suppress(Exception):
        proc.wait(timeout=2)


def mark_user_abort(phase: str, loop_idx: Optional[int] = None, note: str | None = None) -> None:
    """Persist information about a user-triggered cancellation."""

    record: Dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
    }
    if loop_idx is not None:
        record["loop"] = loop_idx
    if note:
        record["note"] = note

    state = read_state_json()
    current = ensure_state_defaults(state)
    current["last_abort"] = record
    write_state_json(current)

    LAST_ABORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAST_ABORT_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")


def clear_user_abort(phase: str | None = None, loop_idx: Optional[int] = None) -> None:
    """Clear any stored user-abort metadata once safely recovered."""

    state = read_state_json()
    current = ensure_state_defaults(state)
    last = current.get("last_abort")
    if not isinstance(last, dict):
        return
    if phase is not None and last.get("phase") != phase:
        return
    if phase == "loop" and loop_idx is not None:
        last_loop = last.get("loop")
        if last_loop is not None and loop_idx < last_loop:
            return

    if "last_abort" in current:
        current.pop("last_abort", None)
        write_state_json(current)
    if LAST_ABORT_PATH.exists():
        with contextlib.suppress(Exception):
            LAST_ABORT_PATH.unlink()

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


def _print_codex_event(label: str, text: str | None = None):
    snippet = ""
    if text:
        clean = text.strip()
        if len(clean) > 280:
            snippet = clean[:280] + " …"
        else:
            snippet = clean
    msg = f"[codex][{label}]"
    if snippet:
        msg += f" {snippet}"
    print(msg, flush=True)


def _handle_codex_line(line: str, last_message: str | None) -> str | None:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        _print_codex_event("raw", line)
        return last_message

    ev_type = event.get("type", "?")

    if ev_type == "item.completed":
        item = event.get("item", {})
        item_type = item.get("type", "?")
        text = item.get("text", "")
        _print_codex_event(item_type, text)
        if item_type == "agent_message":
            return text
        return last_message

    if ev_type == "turn.started":
        _print_codex_event("turn", "started")
    elif ev_type == "turn.completed":
        usage = event.get("usage", {})
        summary = ", ".join(
            f"{k}={v}" for k, v in usage.items()
        ) if usage else "completed"
        _print_codex_event("turn", summary)
    elif ev_type == "thread.started":
        _print_codex_event("thread", f"id={event.get('thread_id','?')}")
    else:
        _print_codex_event(ev_type, json.dumps(event, ensure_ascii=False))

    return last_message


def run_codex_cli(user_prompt: str, system_prompt: str = None, model: str = MODEL, retries: int = 2) -> str:
    """Invoke the codex CLI using JSONL streaming output."""
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    prompt = _combine_prompts(user_prompt, system_prompt)
    cmd = [codex_bin, "exec", "--json", "-m", model]
    if REASONING_EFFORT:
        cmd += ["-c", f"model_reasoning_effort=\"{REASONING_EFFORT}\""]
    if NETWORK_ACCESS:
        cmd += ["-c", f"network_access=\"{NETWORK_ACCESS}\""]
    cmd.append("-")
    last_err = ""
    for attempt in range(retries + 1):
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError as launch_err:
            raise RuntimeError(f"codex executable not found: {launch_err}")

        stderr_text = ""
        rc: Optional[int] = None
        last_message = None
        try:
            if proc.stdin:
                try:
                    proc.stdin.write(prompt)
                except BrokenPipeError:
                    pass
                except KeyboardInterrupt as exc:
                    _terminate_process(proc)
                    raise UserAbort("user cancelled while sending prompt") from exc
                finally:
                    proc.stdin.close()

            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    last_message = _handle_codex_line(line, last_message)
        except KeyboardInterrupt as exc:
            _terminate_process(proc)
            raise UserAbort("user cancelled during Codex streaming") from exc
        finally:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                try:
                    stderr_text = proc.stderr.read().strip()
                except Exception:
                    stderr_text = ""
                proc.stderr.close()
            try:
                rc = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _terminate_process(proc)
                try:
                    rc = proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    rc = proc.poll()
            except KeyboardInterrupt as exc:
                _terminate_process(proc)
                raise UserAbort("user cancelled during Codex shutdown") from exc
            if rc is None:
                rc = proc.returncode

        if stderr_text:
            _print_codex_event("stderr", stderr_text)

        if rc == 0 and last_message:
            return last_message

        last_err = stderr_text or f"exit={rc}, no agent message"
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

def write_state_json(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def merge_state(current: Dict[str, Any], update: Dict[str, Any]):
    if not update:
        return current
    merged = dict(current)
    for k,v in update.items():
        if k == "loop_counter" and isinstance(v, str) and v.strip() == "+=1":
            merged[k] = int(merged.get(k,0)) + 1
        else:
            merged[k] = v
    return merged


def ensure_state_defaults(state: Dict[str, Any], total_loops: Optional[int] = None) -> Dict[str, Any]:
    updated = dict(state)
    if "loop_counter" not in updated or not isinstance(updated.get("loop_counter"), int):
        try:
            updated["loop_counter"] = int(updated.get("loop_counter", 0) or 0)
        except Exception:
            updated["loop_counter"] = 0
    if total_loops is not None:
        updated["total_loops"] = max(int(total_loops), 0)
    elif "total_loops" not in updated:
        updated["total_loops"] = DEFAULT_TOTAL_LOOPS
    updated.setdefault("bootstrap_complete", False)
    return updated


def record_loop_counter(loop_idx: int) -> None:
    state = read_state_json()
    current = ensure_state_defaults(state)
    if loop_idx > current.get("loop_counter", 0):
        current["loop_counter"] = loop_idx
        write_state_json(current)

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
    if NETWORK_ACCESS:
        lines.append(f"network_access: {NETWORK_ACCESS}")
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
        f"- Network access: {NETWORK_ACCESS or 'not specified'}",
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
    bootstrap_system = get_prompt("BOOTSTRAP_SYSTEM")
    bootstrap_user = get_prompt("BOOTSTRAP_USER")
    parse_failures = 0
    while True:
        try:
            raw = run_codex_cli(bootstrap_user, bootstrap_system)
        except UserAbort:
            mark_user_abort("bootstrap", note="Interrupted during bootstrap")
            print("[bootstrap] cancelled by user.")
            return True
        (REPO/"artifacts"/"last_model_raw.txt").write_text(raw, encoding="utf-8")
        js = extract_json_block(raw)
        if not js:
            parse_failures += 1
            print(f"[bootstrap] parse failure: missing JSON block (attempt {parse_failures}/{MAX_CONSEC_PARSE_FAILS}).")
            if parse_failures >= MAX_CONSEC_PARSE_FAILS:
                raise RuntimeError("Bootstrap: could not find JSON block in model output after retries.")
            continue
        try:
            data = json.loads(js)
            break
        except json.JSONDecodeError as err:
            parse_failures += 1
            fragment_path = _record_invalid_json(f"bootstrap_{parse_failures:02d}", js)
            try:
                rel_fragment = fragment_path.relative_to(REPO)
            except ValueError:
                rel_fragment = fragment_path
            print(f"[bootstrap] parse failure: invalid JSON ({err}) (attempt {parse_failures}/{MAX_CONSEC_PARSE_FAILS}). Saved fragment to {rel_fragment}.")
            if parse_failures >= MAX_CONSEC_PARSE_FAILS:
                raise RuntimeError(f"Bootstrap: invalid JSON after retries: {err}") from err
    # Minimal schema presence
    for k in ("files","decision_log_row","git","stop_now"):
        if k not in data:
            raise RuntimeError(f"Bootstrap: missing required key '{k}' in model JSON.")
    write_files(data.get("files",[]))
    # Persist state_update if provided
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    new_state = ensure_state_defaults(new_state)
    # Mark bootstrap completion if no early stop flag is requested later.
    new_state["bootstrap_complete"] = True
    write_state_json(new_state)
    clear_user_abort("bootstrap")
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
        # Preserve bootstrap_complete flag only if the agent wrote it explicitly.
        state_with_flag = read_state_json()
        if state_with_flag.get("bootstrap_complete", False) and data.get("stop_now"):
            state_with_flag["bootstrap_complete"] = False
            write_state_json(state_with_flag)
        return True
    return False

def do_loop(iter_ix: int, consecutive_git_fails: int, consecutive_parse_fails: int):
    ensure_repo_structure()
    update_reproducibility()
    loop_system = get_prompt("LOOP_SYSTEM")
    user_template = get_prompt("LOOP_USER_TEMPLATE")
    state_snapshot = ensure_state_defaults(read_state_json())
    state_prompt = json.dumps(state_snapshot, indent=2)
    user_prompt = user_template.format(state_json=state_prompt)
    loops_remaining = max(int(state_snapshot.get("total_loops", DEFAULT_TOTAL_LOOPS)) - int(state_snapshot.get("loop_counter", 0)), 0)
    progress_note = (
        f"\nLoop progress: completed={state_snapshot.get('loop_counter', 0)}, "
        f"remaining={loops_remaining}, total={state_snapshot.get('total_loops', DEFAULT_TOTAL_LOOPS)}."
    )
    if NETWORK_ACCESS:
        progress_note += f" Network access={NETWORK_ACCESS}."
    user_prompt = user_prompt + progress_note

    try:
        raw = run_codex_cli(user_prompt, loop_system)
    except UserAbort:
        mark_user_abort("loop", iter_ix, note="Interrupted during loop execution")
        print(f"[loop {iter_ix}] cancelled by user.")
        return True, consecutive_git_fails, consecutive_parse_fails
    (REPO/"artifacts"/"last_model_raw.txt").write_text(raw, encoding="utf-8")
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
        try:
            rel_fragment = fragment_path.relative_to(REPO)
        except ValueError:
            rel_fragment = fragment_path
        print(f"[loop {iter_ix}] parse failure: invalid JSON ({err}). Saved fragment to {rel_fragment}.")
        if consecutive_parse_fails >= MAX_CONSEC_PARSE_FAILS:
            print("Too many parse failures; stopping.")
            return True, consecutive_git_fails, consecutive_parse_fails
        return False, consecutive_git_fails, consecutive_parse_fails
    consecutive_parse_fails = 0

    write_files(data.get("files",[]))

    # Persist state updates (merge)
    state = read_state_json()
    new_state = merge_state(state, data.get("state_update",{}))
    new_state = ensure_state_defaults(new_state)
    write_state_json(new_state)
    clear_user_abort("loop", iter_ix)

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

    record_loop_counter(iter_ix)
    return False, consecutive_git_fails, consecutive_parse_fails

def run_loop_batch(start_loop: int, loops_to_run: int, sleep_seconds: Optional[float]) -> bool:
    """Run a contiguous batch of loops. Returns True if stopped early."""

    consecutive_git_fails = 0
    consecutive_parse_fails = 0
    final_loop = start_loop + loops_to_run - 1
    for loop_idx in range(start_loop, final_loop + 1):
        print(f"== Loop {loop_idx} / target {final_loop} ==")
        try:
            should_stop, consecutive_git_fails, consecutive_parse_fails = do_loop(
                loop_idx,
                consecutive_git_fails,
                consecutive_parse_fails,
            )
        except KeyboardInterrupt:
            mark_user_abort("loop", loop_idx, note="Interrupted mid-loop")
            print(f"[loop {loop_idx}] cancelled by user.")
            return True
        if should_stop:
            return True
        if sleep_seconds and sleep_seconds > 0 and loop_idx < final_loop:
            try:
                time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                next_loop = loop_idx + 1
                mark_user_abort("loop", next_loop, note="Interrupted during inter-loop delay")
                print(f"[loop {next_loop}] cancelled during sleep before start.")
                return True
    return False


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or resume the survey science agent.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Refresh reproducibility artifacts without invoking the agent.",
    )
    parser.add_argument(
        "--loops",
        type=int,
        default=None,
        help="Number of loops to execute this run (defaults to remaining loops).",
    )
    parser.add_argument(
        "--total-loops",
        type=int,
        default=None,
        help=f"Override total loop budget (default {DEFAULT_TOTAL_LOOPS}). Stored in state.",
    )
    parser.add_argument(
        "--force-bootstrap",
        action="store_true",
        help="Run bootstrap even if already completed.",
    )
    parser.add_argument(
        "--skip-bootstrap",
        action="store_true",
        help="Skip bootstrap even if not marked complete.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=None,
        help="Pause between loops (overrides LOOP_SLEEP_SECONDS).",
    )
    args = parser.parse_args(argv)

    if args.loops is not None and args.loops <= 0:
        parser.error("--loops must be a positive integer")
    if args.total_loops is not None and args.total_loops <= 0:
        parser.error("--total-loops must be a positive integer")
    if args.force_bootstrap and args.skip_bootstrap:
        parser.error("Use only one of --force-bootstrap or --skip-bootstrap")
    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    ensure_repo_structure()
    os.chdir(REPO)

    if args.dry_run:
        print("[dry-run] ensuring structure + reproducibility snapshots only")
        update_reproducibility()
        return 0

    # Load and persist state defaults
    state_before = read_state_json()
    state = ensure_state_defaults(state_before, args.total_loops)
    if state != state_before:
        write_state_json(state)

    bootstrap_complete = bool(state.get("bootstrap_complete"))
    bootstrap_needed = args.force_bootstrap or (not bootstrap_complete and not args.skip_bootstrap)
    if not bootstrap_complete and args.skip_bootstrap and not args.force_bootstrap:
        print("[runner] WARNING: bootstrap not marked complete but skipping as requested.")

    if bootstrap_needed:
        early_stop = do_bootstrap()
        if early_stop:
            return 0
        state = ensure_state_defaults(read_state_json(), args.total_loops)
        write_state_json(state)

    raw_state_after = read_state_json()
    state = ensure_state_defaults(raw_state_after, args.total_loops)
    if state != raw_state_after:
        write_state_json(state)

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
        print(f"[runner] No loops to run (completed={completed_loops}, total={total_loops}).")
        return 0

    start_loop = completed_loops + 1
    final_loop = start_loop + loops_to_run - 1
    print(
        f"[runner] executing loops {start_loop}..{final_loop} "
        f"(completed={completed_loops}, total={total_loops})."
    )

    sleep_seconds = args.sleep_seconds if args.sleep_seconds is not None else SLEEP_SECONDS
    try:
        stopped = run_loop_batch(start_loop, loops_to_run, sleep_seconds)
    except KeyboardInterrupt:
        # Avoid overwriting detailed loop-level aborts if already recorded.
        state_after_interrupt = read_state_json()
        if not isinstance(state_after_interrupt.get("last_abort"), dict):
            mark_user_abort("runner", note="Interrupted outside loop batch")
        print("[runner] interrupted by user.")
        return 130
    if stopped:
        print("[runner] loop sequence halted early.")
    else:
        print("[runner] loop sequence finished.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except UserAbort as exc:
        print(f"[runner] interrupted by user: {exc}", file=sys.stderr)
        sys.exit(130)
    except KeyboardInterrupt:
        print("[runner] interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)
