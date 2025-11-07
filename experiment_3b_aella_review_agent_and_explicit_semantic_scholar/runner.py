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
import base64
import binascii
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
    "analysis",
    "artifacts",
    "docs",
    "figures",
    "lit",
    "notebooks",
    "outputs",
    "qc",
    "reports",
    "tables",
    "papers",
    "config",
    "scripts",
    "manuscript",
    "review",
    "qa",
    "tmp",
    ".github",
    ".codex",
}

ALLOWED_ROOT_FILE_EXTS = {
    ".md",
    ".txt",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".csv",
    ".tex",
    ".rst",
    ".ini",
    ".cfg",
    ".toml",
    ".lock",
    ".sh",
    ".env",
    ".gitignore",
    ".bat",
    ".ps1",
}

ALLOWED_ROOT_FILENAMES = {
    "Makefile",
    "LICENSE",
    "Dockerfile",
    "Procfile",
    "README",
    "README.md",
}

ALLOWED_BINARY_SUFFIXES = {
    ".png",
    ".pdf",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
}

MAX_BINARY_FILE_BYTES = int(os.environ.get("RUNNER_MAX_BINARY_BYTES", 25 * 1024 * 1024))


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
REVIEW_SECTION_RE = re.compile(
    r"^##\s+Loop\s+(\d+)[^\n]*\n([\s\S]*?)(?=^##\s+Loop\s+\d+|\Z)",
    re.MULTILINE,
)
PAP_STATUS_RE = re.compile(r"^\s*status\s*:\s*(.+)\s*$", re.IGNORECASE)
PAP_FROZEN_MARK_RE = re.compile(r"pap\s+frozen", re.IGNORECASE)
PAP_COMMIT_TAG_RE = re.compile(r"(commit|tag)\s*[:=]\s*\S+", re.IGNORECASE)
PAP_REGISTRY_URL_RE = re.compile(r"^\s*registry_url\s*:\s*(https?://\S+)", re.IGNORECASE)
PAP_FREEZE_REF_RE = re.compile(r"^\s*freeze_(?:commit|tag)\s*:\s*\S+", re.IGNORECASE)
DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
MEASURE_TABLE_HEADER_RE = re.compile(
    r"\|\s*measure_id\s*\|\s*item_wording\s*\|\s*coding\s*\|\s*reliability_alpha\s*\|\s*dif_check",
    re.IGNORECASE,
)
CLAIM_TAG_RE = re.compile(r"\[CLAIM:([A-Za-z0-9_-]+)\]")
BUILD_STATUS_RE = re.compile(r"LaTeX build:\s*(PASS|FAIL)", re.IGNORECASE)
BIBTEX_WARN_RE = re.compile(r"BibTeX warnings:\s*(\d+)", re.IGNORECASE)
VIOLATIONS_RE = re.compile(r"violations\s*:\s*(\d+)", re.IGNORECASE)
REVIEW_DECISION_RE = re.compile(r"DECISION\s*:\s*([A-Za-z \-]+)", re.IGNORECASE)
TARGETED_TRUE_VALUES = {
    "1",
    "y",
    "yes",
    "true",
    "t",
    "primary",
    "confirmatory",
    "targeted",
}

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
    for p in ["analysis","artifacts","artifacts/llm_raw","docs","figures","lit","notebooks","outputs","qc","reports","tables","papers","review"]:
        (REPO / p).mkdir(parents=True, exist_ok=True)
    if not DECISION_LOG.exists():
        with DECISION_LOG.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ts","action","inputs","rationale_short","code_path","outputs","status"])

def _resolve_and_validate_path(path_str: str) -> Path:
    if not isinstance(path_str, str):
        raise ValueError("File path must be a string.")
    clean = path_str.strip()
    if not clean:
        raise ValueError("File path cannot be empty.")
    if "\x00" in clean:
        raise ValueError("File path contains null bytes.")
    path = Path(clean)
    if path.is_absolute():
        raise ValueError("Absolute paths are not permitted.")
    parts = path.parts
    for part in parts:
        if part in {"", ".."}:
            raise ValueError(f"Path traversal detected in '{path_str}'.")
        if part == "." and len(parts) == 1:
            raise ValueError("Writing to '.' is not permitted.")
    resolved = (REPO / path).resolve()
    try:
        rel_path = resolved.relative_to(REPO)
    except ValueError as exc:
        raise ValueError(f"Path escapes repository root: '{path_str}'") from exc
    if not rel_path.parts:
        raise ValueError("Cannot write to repository root.")
    top = rel_path.parts[0]
    if len(rel_path.parts) == 1:
        suffix = resolved.suffix.lower()
        root_name = rel_path.parts[0]
        if suffix not in ALLOWED_ROOT_FILE_EXTS and root_name not in ALLOWED_ROOT_FILENAMES:
            raise ValueError(f"Writing '{path_str}' at repo root is not allowed.")
    else:
        if top not in ALLOWED_TOP_LEVEL_DIRS:
            raise ValueError(f"Top-level directory '{top}' is not allowed for writes.")
    return resolved


def write_files(files):
    for f in files:
        path_str = f.get("path")
        resolved_path = _resolve_and_validate_path(path_str)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        mode = f.get("mode", "text")
        if mode == "text":
            content = f.get("content", "")
            if not isinstance(content, str):
                raise ValueError(f"Text mode requires string content for '{path_str}'.")
            resolved_path.write_text(content, encoding="utf-8")
        elif mode in {"base64", "binary"}:
            content = f.get("content", "")
            if not isinstance(content, str):
                raise ValueError(f"{mode} mode requires base64 string content for '{path_str}'.")
            try:
                payload = base64.b64decode(content, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise ValueError(f"Invalid base64 payload for '{path_str}'.") from exc
            if len(payload) > MAX_BINARY_FILE_BYTES:
                raise ValueError(f"Binary payload for '{path_str}' exceeds size limit ({MAX_BINARY_FILE_BYTES} bytes).")
            suffix = resolved_path.suffix.lower()
            if suffix not in ALLOWED_BINARY_SUFFIXES:
                raise ValueError(f"Binary writes limited to {sorted(ALLOWED_BINARY_SUFFIXES)}; got '{suffix}' for '{path_str}'.")
            resolved_path.write_bytes(payload)
        else:
            raise ValueError(f"Unsupported file mode '{mode}' for '{path_str}'.")


def _validate_file_entry(entry: dict) -> None:
    if not isinstance(entry, dict):
        raise ValueError("Each file entry must be a dict.")
    if "path" not in entry:
        raise ValueError("File entry missing 'path'.")
    _resolve_and_validate_path(entry["path"])
    mode = entry.get("mode", "text")
    if not isinstance(mode, str):
        raise ValueError(f"File mode for '{entry['path']}' must be a string.")
    if mode not in {"text", "base64", "binary"}:
        raise ValueError(f"Unsupported file mode '{mode}' for '{entry['path']}'.")
    if mode == "text":
        content = entry.get("content", "")
        if not isinstance(content, str):
            raise ValueError(f"Text mode requires string content for '{entry['path']}'.")
    else:
        content = entry.get("content", "")
        if not isinstance(content, str):
            raise ValueError(f"{mode} mode requires base64 content for '{entry['path']}'.")


def validate_payload(data: Any, context: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{context}: JSON payload must be an object.")

    files = data.get("files")
    if files is None or not isinstance(files, list):
        raise ValueError(f"{context}: 'files' must be a list.")
    for entry in files:
        _validate_file_entry(entry)

    decision_log = data.get("decision_log_row")
    if decision_log is not None and not isinstance(decision_log, dict):
        raise ValueError(f"{context}: 'decision_log_row' must be an object when provided.")

    git_info = data.get("git")
    if git_info is None or not isinstance(git_info, dict):
        raise ValueError(f"{context}: 'git' field must be provided as an object.")
    commit_flag = git_info.get("commit")
    if not isinstance(commit_flag, bool):
        raise ValueError(f"{context}: 'git.commit' must be boolean.")
    if commit_flag:
        message = git_info.get("message", "")
        if not isinstance(message, str) or not message.strip():
            raise ValueError(f"{context}: commit requested but 'git.message' is missing or empty.")
    elif "message" in git_info and git_info.get("message") is not None and not isinstance(git_info.get("message"), str):
        raise ValueError(f"{context}: 'git.message' must be a string when provided.")

    stop_now = data.get("stop_now")
    if not isinstance(stop_now, bool):
        raise ValueError(f"{context}: 'stop_now' must be boolean.")
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
    if not isinstance(phase, str):
        raise ValueError(f"{context}: 'signals.phase' must be a string.")
    if phase not in PHASE_ORDER:
        raise ValueError(f"{context}: 'signals.phase' must be one of {PHASE_ORDER}.")
    scorecard = signals.get("scorecard")
    if not isinstance(scorecard, dict):
        raise ValueError(f"{context}: 'signals.scorecard' must be an object.")
    for key in ("rigor", "identification_risk", "reproducibility", "literature_coverage"):
        val = scorecard.get(key)
        if not isinstance(val, (int, float)):
            raise ValueError(f"{context}: 'signals.scorecard.{key}' must be numeric.")
    if "privacy_compliance" not in scorecard or not isinstance(scorecard["privacy_compliance"], bool):
        raise ValueError(f"{context}: 'signals.scorecard.privacy_compliance' must be boolean.")
    notes_val = scorecard.get("notes")
    if not isinstance(notes_val, str):
        raise ValueError(f"{context}: 'signals.scorecard.notes' must be a string.")

    sem_block = signals.get("semantic_scholar")
    if not isinstance(sem_block, dict):
        raise ValueError(f"{context}: 'signals.semantic_scholar' must be an object.")
    queried = sem_block.get("queried")
    if not isinstance(queried, bool):
        raise ValueError(f"{context}: 'signals.semantic_scholar.queried' must be boolean.")
    queries = sem_block.get("queries", [])
    if not isinstance(queries, list) or any(not isinstance(q, str) for q in queries):
        raise ValueError(f"{context}: 'signals.semantic_scholar.queries' must be a list of strings.")
    reason = sem_block.get("reason", "")
    if not isinstance(reason, str):
        raise ValueError(f"{context}: 'signals.semantic_scholar.reason' must be a string.")
    if queried:
        if not queries:
            raise ValueError(f"{context}: 'signals.semantic_scholar.queries' must be non-empty when queried=true.")
    else:
        if phase == "literature":
            raise ValueError(f"{context}: Semantic Scholar query is mandatory during literature phase.")
        if not reason.strip():
            raise ValueError(f"{context}: Provide 'signals.semantic_scholar.reason' when queried=false.")


def _normalize_repo_path_for_checks(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _pap_status() -> tuple[bool, str]:
    pap_path = REPO / "analysis" / "pre_analysis_plan.md"
    if not pap_path.exists():
        return False, "analysis/pre_analysis_plan.md missing."
    try:
        text = pap_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read analysis/pre_analysis_plan.md ({exc})."
    status_frozen = False
    for line in text.splitlines():
        match = PAP_STATUS_RE.match(line)
        if match:
            if "frozen" in match.group(1).lower():
                status_frozen = True
                break
            return False, "analysis/pre_analysis_plan.md status must be set to 'frozen'."
    if not status_frozen:
        if not (PAP_FROZEN_MARK_RE.search(text) and PAP_COMMIT_TAG_RE.search(text)):
            return False, "Add 'status: frozen' (with commit/tag note) to analysis/pre_analysis_plan.md."
    registry_match = PAP_REGISTRY_URL_RE.search(text)
    if not registry_match:
        return False, "Add 'registry_url: https://osf.io/...'(or similar) to analysis/pre_analysis_plan.md."
    freeze_match = PAP_FREEZE_REF_RE.search(text)
    if not freeze_match:
        return False, "Add 'freeze_commit:' or 'freeze_tag:' line referencing the lock point."
    return True, "PAP frozen with registry URL and freeze reference."


def _check_literature_gate() -> tuple[bool, str]:
    evidence_path = REPO / "lit" / "evidence_map.csv"
    if not evidence_path.exists():
        return False, "lit/evidence_map.csv missing (need ≥3 DOI or URL-backed sources)."
    qualifying_rows = 0
    try:
        with evidence_path.open("r", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                cells = [cell.strip() for cell in row if cell]
                if any(DOI_RE.search(cell) or URL_RE.search(cell) for cell in cells):
                    qualifying_rows += 1
    except Exception as exc:
        return False, f"Unable to parse lit/evidence_map.csv ({exc})."
    if qualifying_rows < 3:
        return False, f"Need ≥3 literature rows with DOI or URL; found {qualifying_rows}."

    bib_path = REPO / "lit" / "bibliography.bib"
    if not bib_path.exists():
        return False, "lit/bibliography.bib missing (required before PAP)."
    try:
        bib_text = bib_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read lit/bibliography.bib ({exc})."
    if "@" not in bib_text:
        return False, "lit/bibliography.bib has no BibTeX entries."
    if bib_text.count("{") != bib_text.count("}"):
        return False, "lit/bibliography.bib brace count mismatch; fix syntax."
    return True, ""


def _check_measure_validity() -> tuple[bool, str]:
    path = REPO / "qc" / "measures_validity.md"
    if not path.exists():
        return False, "qc/measures_validity.md missing."
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read qc/measures_validity.md ({exc})."
    if not MEASURE_TABLE_HEADER_RE.search(text):
        return False, "qc/measures_validity.md must include the table header (measure_id | item_wording | coding | reliability_alpha | dif_check)."
    table_lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    if len(table_lines) < 3:
        return False, "qc/measures_validity.md table needs at least one data row documenting a measure."
    return True, ""


def _check_outline_and_checklist() -> tuple[bool, str]:
    outline_path = REPO / "papers" / "main" / "imrad_outline.md"
    if not outline_path.exists():
        return False, "papers/main/imrad_outline.md missing."
    try:
        outline_text = outline_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read papers/main/imrad_outline.md ({exc})."
    for section in ("introduction", "methods", "results", "discussion"):
        pattern = re.compile(rf"(?im)^\s*(?:[#\-\*]+\s*)?{section}\b")
        if not pattern.search(outline_text):
            return False, f"papers/main/imrad_outline.md missing '{section.title()}' section."
    checklist_path = REPO / "qc" / "strobe_sampl_checklist.md"
    if not checklist_path.exists():
        return False, "qc/strobe_sampl_checklist.md missing."
    try:
        checklist_text = checklist_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read qc/strobe_sampl_checklist.md ({exc})."
    lowered = checklist_text.lower()
    if "strobe" not in lowered or "sampl" not in lowered:
        return False, "qc/strobe_sampl_checklist.md must cover both STROBE and SAMPL items."
    if "pass" not in lowered and "justified" not in lowered:
        return False, "qc/strobe_sampl_checklist.md must mark items as PASS or justified."
    return True, ""


def _check_build_log() -> tuple[bool, str]:
    log_path = REPO / "papers" / "main" / "build_log.txt"
    if not log_path.exists():
        return False, "papers/main/build_log.txt missing."
    try:
        text = log_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read papers/main/build_log.txt ({exc})."
    matches = list(BUILD_STATUS_RE.finditer(text))
    if not matches:
        return False, "papers/main/build_log.txt must contain 'LaTeX build: PASS/FAIL' entries."
    last = matches[-1]
    if last.group(1).upper() != "PASS":
        return False, "Latest LaTeX build did not pass; fix compilation before release."
    tail = text[last.start():]
    warn_match = BIBTEX_WARN_RE.search(tail) or BIBTEX_WARN_RE.search(text)
    if not warn_match:
        return False, "Record 'BibTeX warnings: <int>' alongside the latest LaTeX build entry."
    return True, ""


def _check_dag_and_identification() -> tuple[bool, str]:
    dag_png = REPO / "figures" / "dag_design.png"
    dag_svg = REPO / "figures" / "dag_design.svg"
    if not dag_png.exists() and not dag_svg.exists():
        return False, "figures/dag_design.(png|svg) missing."
    ident_path = REPO / "reports" / "identification.md"
    if not ident_path.exists():
        return False, "reports/identification.md missing."
    try:
        text = ident_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read reports/identification.md ({exc})."
    lowered = text.lower()
    if "non-causal" not in lowered and "assumption" not in lowered:
        return False, "reports/identification.md must explicitly state the non-causal stance or enumerate causal assumptions."
    if "dag" not in lowered and "dag_design" not in lowered:
        return False, "reports/identification.md should reference the DAG figure."
    return True, ""


def _check_disclosure_audit() -> tuple[bool, str]:
    reports = sorted(REPO.glob("qc/disclosure_check_loop_*.md"))
    if not reports:
        return False, "No qc/disclosure_check_loop_XXX.md files found."
    latest = reports[-1]
    try:
        text = latest.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read {latest.relative_to(REPO)} ({exc})."
    match = VIOLATIONS_RE.search(text)
    if not match:
        return False, f"{latest.relative_to(REPO)} missing 'violations: <int>' line."
    try:
        violations = int(match.group(1))
    except ValueError:
        return False, f"{latest.relative_to(REPO)} has non-numeric violations count."
    if violations != 0:
        return False, f"{latest.relative_to(REPO)} reports {violations} violation(s); cannot release."
    if "table" not in text.lower() and "|" not in text:
        return False, f"{latest.relative_to(REPO)} must list each public table/figure audited."
    return True, ""


def _check_claim_coverage() -> tuple[bool, str]:
    manuscript_path = REPO / "papers" / "main" / "manuscript.tex"
    if not manuscript_path.exists():
        return False, "papers/main/manuscript.tex missing."
    try:
        manuscript = manuscript_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read papers/main/manuscript.tex ({exc})."
    claims = sorted(set(CLAIM_TAG_RE.findall(manuscript)))
    if not claims:
        return False, "papers/main/manuscript.tex contains no [CLAIM:<ID>] tags."
    evidence_path = REPO / "lit" / "evidence_map.csv"
    if not evidence_path.exists():
        return False, "lit/evidence_map.csv missing for claim coverage."
    try:
        with evidence_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = reader.fieldnames or []
            lower_map = {name.strip().lower(): name for name in fieldnames}
            claim_field = lower_map.get("claim_id")
            if not claim_field:
                return False, "lit/evidence_map.csv must include a 'claim_id' column."
            coverage: dict[str, bool] = {}
            for row in reader:
                claim_id = (row.get(claim_field) or "").strip()
                if not claim_id:
                    continue
                has_doi = any(DOI_RE.search(str(val) or "") for val in row.values())
                coverage.setdefault(claim_id, False)
                if has_doi:
                    coverage[claim_id] = True
    except Exception as exc:
        return False, f"Unable to parse lit/evidence_map.csv ({exc})."
    missing = [cid for cid in claims if not coverage.get(cid)]
    if missing:
        return False, f"Claims lacking DOI-backed evidence_map rows: {', '.join(missing[:5])}"
    return True, ""


def _check_reviewer_continue() -> tuple[bool, str]:
    review_path = REPO / "review" / "research_findings.md"
    if not review_path.exists():
        return False, "review/research_findings.md missing; run the reviewer before release."
    try:
        text = review_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read review/research_findings.md ({exc})."
    decisions = REVIEW_DECISION_RE.findall(text)
    if not decisions:
        return False, "review/research_findings.md missing 'DECISION:' entries."
    last = decisions[-1].strip().upper()
    if not last.startswith("CONTINUE"):
        return False, f"Latest reviewer decision is '{last}'; cannot release."
    return True, ""


def _check_release_artifacts() -> tuple[bool, str]:
    checks = [
        _check_outline_and_checklist,
        _check_build_log,
        _check_dag_and_identification,
        _check_disclosure_audit,
        _check_claim_coverage,
        _check_reviewer_continue,
    ]
    for checker in checks:
        ok, reason = checker()
        if not ok:
            return False, reason
    return True, ""


def _validate_results_csv() -> tuple[bool, str]:
    results_path = REPO / "analysis" / "results.csv"
    if not results_path.exists():
        return False, "analysis/results.csv missing."
    try:
        with results_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = reader.fieldnames or []
            lower_map = {name.strip().lower(): name for name in fieldnames}
            required = ["family", "targeted", "bh_in_scope", "q_value", "hypothesis_id"]
            for key in required:
                if key not in lower_map:
                    return False, f"analysis/results.csv missing '{key}' column."
            fam_col = lower_map["family"]
            targeted_col = lower_map["targeted"]
            bh_col = lower_map["bh_in_scope"]
            q_col = lower_map["q_value"]
            hyp_col = lower_map["hypothesis_id"]
            missing_q: list[str] = []
            targeted_rows = 0
            for row_ix, row in enumerate(reader, start=2):
                family = (row.get(fam_col) or "").strip()
                if not family:
                    return False, f"analysis/results.csv row {row_ix} missing family designation."
                bh_scope = (row.get(bh_col) or "").strip()
                if not bh_scope:
                    return False, f"analysis/results.csv row {row_ix} missing bh_in_scope entry."
                targeted_val = (row.get(targeted_col) or "").strip().lower()
                if targeted_val in TARGETED_TRUE_VALUES:
                    targeted_rows += 1
                    q_val = (row.get(q_col) or "").strip()
                    hyp_id = (row.get(hyp_col) or "").strip() or f"row {row_ix}"
                    if not q_val:
                        missing_q.append(hyp_id)
                    else:
                        try:
                            float(q_val)
                        except ValueError:
                            missing_q.append(hyp_id)
            if missing_q:
                return False, f"Targeted hypotheses missing numeric q_value: {', '.join(missing_q[:5])}"
            if targeted_rows == 0:
                return False, "analysis/results.csv never labels a hypothesis as targeted (targeted column true)."
    except Exception as exc:
        return False, f"Unable to parse analysis/results.csv ({exc})."
    return True, ""


def enforce_post_write_validations(files: list[dict]) -> None:
    if not isinstance(files, list):
        return
    needs_results_check = False
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            continue
        norm = _normalize_repo_path_for_checks(path)
        if norm == "analysis/results.csv":
            needs_results_check = True
            break
    if needs_results_check:
        ok, reason = _validate_results_csv()
        if not ok:
            raise ValueError(reason)


def _detect_confirmatory_writes(files: list[dict]) -> list[str]:
    confirm_paths = []
    for entry in files or []:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            continue
        norm = _normalize_repo_path_for_checks(path)
        if not norm:
            continue
        if norm.startswith("tables/") or norm.startswith("analysis/results"):
            confirm_paths.append(path)
    return confirm_paths


def enforce_confirmatory_requirements(files: list[dict]) -> None:
    confirm_paths = _detect_confirmatory_writes(files)
    if not confirm_paths:
        return
    frozen, reason = _pap_status()
    if not frozen:
        raise ValueError(
            "Confirmatory outputs blocked: analysis/pre_analysis_plan.md must declare 'status: frozen' "
            f"before writing {confirm_paths}. ({reason})"
        )


def enforce_phase_transition_rules(state_snapshot: Dict[str, Any], state_update: Optional[Dict[str, Any]]) -> None:
    if not isinstance(state_update, dict):
        return
    current_phase = str(state_snapshot.get("phase", "literature")).lower()
    target_phase = None
    explicit_phase = state_update.get("phase")
    if isinstance(explicit_phase, str):
        target_phase = explicit_phase.lower()
    elif state_update.get("advance_phase"):
        try:
            idx = PHASE_ORDER.index(current_phase)
        except ValueError:
            idx = -1
        if idx != -1 and idx < len(PHASE_ORDER) - 1:
            target_phase = PHASE_ORDER[idx + 1]
    if not target_phase or target_phase == current_phase:
        return
    if current_phase == "literature" and target_phase == "pap":
        ok, reason = _check_literature_gate()
        if not ok:
            raise ValueError(f"Cannot advance to PAP: {reason}")
    if target_phase == "analysis":
        frozen, reason = _pap_status()
        if not frozen:
            raise ValueError(f"Cannot advance to analysis until PAP is frozen: {reason}")
        measures_ok, measures_reason = _check_measure_validity()
        if not measures_ok:
            raise ValueError(f"Cannot advance to analysis: {measures_reason}")
    if target_phase == "review":
        outline_ok, outline_reason = _check_outline_and_checklist()
        if not outline_ok:
            raise ValueError(f"Cannot advance to review: {outline_reason}")
    if target_phase == "release":
        release_ok, release_reason = _check_release_artifacts()
        if not release_ok:
            raise ValueError(f"Cannot advance to release: {release_reason}")


def enforce_payload_guards(state_snapshot: Dict[str, Any], payload: Dict[str, Any]) -> None:
    enforce_phase_transition_rules(state_snapshot, payload.get("state_update"))
    enforce_confirmatory_requirements(payload.get("files", []))


def _write_raw_output(tag: str, content: str, *, update_latest: bool = True) -> None:
    if not isinstance(content, str):
        content = str(content)
    raw_dir = REPO / "artifacts" / "llm_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^0-9A-Za-z_.-]", "_", str(tag))
    if not safe_tag:
        safe_tag = "output"
    target = raw_dir / f"{safe_tag}.txt"
    target.write_text(content, encoding="utf-8")
    if update_latest:
        (REPO / "artifacts" / "last_model_raw.txt").write_text(content, encoding="utf-8")
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
    for k, v in update.items():
        if k == "loop_counter" and isinstance(v, str) and v.strip() == "+=1":
            merged[k] = int(merged.get(k, 0)) + 1
        elif k == "advance_phase" and v:
            cur_phase = str(merged.get("phase", "literature"))
            try:
                idx = PHASE_ORDER.index(cur_phase)
            except ValueError:
                idx = -1
            next_idx = min(idx + 1, len(PHASE_ORDER) - 1)
            merged["phase"] = PHASE_ORDER[next_idx]
            merged["phase_ix"] = next_idx
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
    phase = updated.get("phase")
    if phase not in PHASE_ORDER:
        updated["phase"] = "literature"
        updated["phase_ix"] = 0
    else:
        updated["phase_ix"] = PHASE_ORDER.index(updated["phase"])
    return updated


def _build_phase_user_prompt(base_template: str, state_snapshot: Dict[str, Any]) -> str:
    phase = str(state_snapshot.get("phase", "literature"))
    state_prompt = json.dumps(state_snapshot, indent=2)
    phase_key = f"PHASE_{phase.upper()}"
    try:
        phase_block = get_prompt(phase_key)
    except KeyError:
        phase_block = ""
    prefix = ""
    if phase_block:
        prefix = (
            "\n\n=== PHASE CONTEXT START ===\n"
            f"{phase_block}\n"
            "=== PHASE CONTEXT END ===\n\n"
        )
    return base_template.format(state_json=state_prompt) + prefix + f"\n(Current phase: {phase})\n"


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
        "- artifacts/llm_raw/loop_XXX.txt (per-loop raw LLM output snapshots)",
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
        _write_raw_output("bootstrap", raw, update_latest=True)
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
    try:
        validate_payload(data, "bootstrap")
    except ValueError as exc:
        raise RuntimeError(f"Bootstrap payload validation failed: {exc}") from exc
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


def _get_review_entry(loop_idx: int) -> str:
    """Return the stored review entry for a specific loop, if recorded."""

    if loop_idx < 1:
        return ""
    review_path = REPO / "review" / "research_findings.md"
    if not review_path.exists():
        return ""
    try:
        text = review_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    for match in REVIEW_SECTION_RE.finditer(text):
        try:
            recorded_loop = int(match.group(1))
        except (TypeError, ValueError):
            continue
        if recorded_loop == loop_idx:
            return match.group(2).strip()
    return ""

def run_loop_review(loop_idx: int, agent_payload: Dict[str, Any]) -> tuple[bool, str]:
    """Run the automated reviewer for a completed loop."""

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
        file_lines = "\n".join(
            f"- {entry.get('path','<missing path>')}" for entry in files if isinstance(entry, dict)
        )
    else:
        file_lines = "(none)"

    user_prompt = review_user_template.format(
        loop_index=f"{loop_idx:03d}",
        state_json=state_json,
        agent_payload_json=payload_json,
        files_written=file_lines,
    )
    try:
        raw_review = run_codex_cli(user_prompt, review_system)
    except UserAbort:
        mark_user_abort("review", loop_idx, note="Interrupted during review generation")
        raise
    except Exception as exc:
        print(f"[review {loop_idx:03d}] error invoking reviewer: {exc}")
        return False, ""

    _write_raw_output(f"review_{loop_idx:03d}", raw_review, update_latest=False)
    review_text = raw_review.strip()
    review_dir = REPO / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / "research_findings.md"
    if not review_file.exists():
        review_file.write_text("# Science Agent Review Findings\n\n", encoding="utf-8")
    review_payload = review_text if review_text else "DECISION: CONTINUE\nNotes: Reviewer response was empty."
    review_payload = review_payload.strip()
    timestamp = datetime.now(timezone.utc).isoformat()
    entry_lines = [
        f"## Loop {loop_idx:03d} — {timestamp}",
        review_payload,
        "",
    ]
    with review_file.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(entry_lines) + "\n")

    decision_line = ""
    for line in review_payload.splitlines():
        stripped = line.strip()
        if stripped:
            decision_line = stripped
            break
    if not decision_line.upper().startswith("DECISION"):
        return False, ""
    decision_value = decision_line.split(":", 1)[1].strip() if ":" in decision_line else ""
    if not decision_value:
        return False, ""
    if decision_value.upper().startswith("STOP"):
        reason = decision_value[len("STOP"):].strip(" –-")
        if not reason:
            reason = "review requested stop"
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
    progress_note = (
        f"\nLoop progress: completed={state_snapshot.get('loop_counter', 0)}, "
        f"remaining={loops_remaining}, total={state_snapshot.get('total_loops', DEFAULT_TOTAL_LOOPS)}."
    )
    if NETWORK_ACCESS:
        progress_note += f" Network access={NETWORK_ACCESS}."
    review_log_path = REPO / "review" / "research_findings.md"
    if review_log_path.exists():
        rel_review = review_log_path.relative_to(REPO)
        progress_note += f" Review log: {rel_review}; acknowledge how you addressed the most recent critiques."
    prior_loop_idx = iter_ix - 1
    if prior_loop_idx >= 1:
        prior_notes = _get_review_entry(prior_loop_idx)
        if prior_notes:
            progress_note += (
                f"\nLatest review findings (loop {prior_loop_idx:03d}):\n"
                f"{prior_notes}\n"
                "Document in your decision_log how you handled each item."
            )
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

    try:
        validate_payload(data, f"loop_{iter_ix}")
    except ValueError as exc:
        print(f"[loop {iter_ix}] payload validation error: {exc}")
        return True, consecutive_git_fails, consecutive_parse_fails

    try:
        enforce_payload_guards(state_snapshot, data)
    except ValueError as exc:
        print(f"[loop {iter_ix}] guard violation: {exc}")
        return True, consecutive_git_fails, consecutive_parse_fails

    write_files(data.get("files",[]))

    try:
        enforce_post_write_validations(data.get("files", []))
    except ValueError as exc:
        print(f"[loop {iter_ix}] post-write validation error: {exc}")
        return True, consecutive_git_fails, consecutive_parse_fails

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

    review_stop = False
    review_reason = ""
    try:
        review_stop, review_reason = run_loop_review(iter_ix, data)
    except UserAbort:
        print(f"[loop {iter_ix}] review interrupted by user.")
        raise

    record_loop_counter(iter_ix)
    if review_stop:
        print(f"[loop {iter_ix}] automated review requested stop: {review_reason}")
        return True, consecutive_git_fails, consecutive_parse_fails
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
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the Codex model for this run (defaults to CODEX_MODEL env or gpt-5-codex).",
    )
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        default=None,
        help="Override model_reasoning_effort (defaults to CODEX_REASONING_EFFORT env).",
    )
    parser.add_argument(
        "--network-access",
        type=str,
        default=None,
        help="Override network_access setting ('enabled' or 'disabled').",
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

    global MODEL, REASONING_EFFORT, NETWORK_ACCESS
    if args.model:
        MODEL = args.model
    if args.reasoning_effort:
        REASONING_EFFORT = args.reasoning_effort
    if args.network_access:
        override = _normalize_network_setting(args.network_access)
        if override in {"enabled", "disabled"}:
            NETWORK_ACCESS = override
        else:
            NETWORK_ACCESS = args.network_access

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
