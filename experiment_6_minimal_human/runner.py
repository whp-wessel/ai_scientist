#!/usr/bin/env python3
"""Minimal science runner with bootstrap, phase gates, and Codex integration."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

REPO = Path(__file__).resolve().parent
STATE_PATH = REPO / "artifacts" / "state.json"
RAW_OUTPUT_DIR = REPO / "artifacts" / "llm_raw"
STOP_FLAG = REPO / "artifacts" / "stop.flag"
PHASE_ORDER = ["literature", "pap", "analysis", "sensitivity", "writing", "release"]
DEFAULT_TOTAL_LOOPS = int(os.environ.get("DEFAULT_TOTAL_LOOPS", "75"))
DEFAULT_SLEEP_SECONDS = float(os.environ.get("LOOP_SLEEP_SECONDS", "0"))
MODEL = os.environ.get("CODEX_MODEL", "gpt-5.1-codex-mini") #keep using gpt-5.1-codex-mini
REASONING_EFFORT = os.environ.get("CODEX_REASONING_EFFORT", "high")
PROMPT_HINT = "see agents.md for your prompt/guidance. please fully implement it."
BOOTSTRAP_DIRS = [
    "analysis",
    "artifacts",
    "artifacts/llm_raw",
    "docs",
    "figures",
    "lit",
    "outputs",
    "papers",
    "qc",
    "tables",
]
BOOTSTRAP_FILES = {
    "analysis/pre_analysis_plan.md": (
        "# Pre-Analysis Plan\n\n"
        "status: draft\n"
        "registry_url: \n"
        "freeze_commit: \n"
    ),
    "qc/measures_validity.md": (
        "| measure_id | item_wording | coding | reliability_alpha | dif_check |\n"
        "| --- | --- | --- | --- | --- |\n"
    ),
}


def _normalize_network_setting(value: str | None) -> str:
    if value is None:
        return ""
    val = value.strip().lower()
    if val in {"on", "true", "1", "yes", "enable", "enabled"}:
        return "enabled"
    if val in {"off", "false", "0", "no", "disable", "disabled"}:
        return "disabled"
    return val


NETWORK_ACCESS = _normalize_network_setting(
    os.environ.get("CODEX_NETWORK_ACCESS") or os.environ.get("CODEX_ALLOW_NET")
)


class UserAbort(Exception):
    """Raised when the user interrupts a Codex stream."""


def ensure_repo_dirs() -> None:
    for path in (STATE_PATH.parent, RAW_OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def read_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def write_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _normalize_phase(value: Any) -> str:
    if not value:
        return "literature"
    lower = str(value).strip().lower()
    return lower if lower in PHASE_ORDER else "literature"


def ensure_state_defaults(state: Dict[str, Any]) -> Dict[str, Any]:
    data: Dict[str, Any] = dict(state) if isinstance(state, dict) else {}
    try:
        data["loop_counter"] = int(data.get("loop_counter", 0) or 0)
    except Exception:
        data["loop_counter"] = 0
    try:
        total = int(data.get("total_loops", DEFAULT_TOTAL_LOOPS))
    except Exception:
        total = DEFAULT_TOTAL_LOOPS
    data["total_loops"] = max(total, 0)
    data["phase"] = _normalize_phase(data.get("phase"))
    data["stop_now"] = bool(data.get("stop_now", False))
    data["stop_reason"] = str(data.get("stop_reason", "") or "")
    return data


def run_bootstrap() -> None:
    ensure_repo_dirs()
    for rel in BOOTSTRAP_DIRS:
        (REPO / rel).mkdir(parents=True, exist_ok=True)
    for rel, content in BOOTSTRAP_FILES.items():
        path = REPO / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    if not STATE_PATH.exists():
        write_state(ensure_state_defaults({}))
    print("[bootstrap] repository prepared")


def _print_codex_event(label: str, text: str | None = None) -> None:
    snippet = (text or "").strip()
    if len(snippet) > 280:
        snippet = snippet[:280] + " …"
    if snippet:
        print(f"[codex][{label}] {snippet}")
    else:
        print(f"[codex][{label}]")


def _handle_codex_line(line: str, last_message: str | None) -> str | None:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        _print_codex_event("raw", line)
        return last_message
    ev_type = event.get("type", "?")
    if ev_type == "item.completed":
        item = event.get("item", {})
        if item.get("type") == "agent_message":
            text = item.get("text", "")
            _print_codex_event("agent", text)
            return text
        _print_codex_event(item.get("type", "item"), item.get("text", ""))
        return last_message
    if ev_type == "turn.started":
        _print_codex_event("turn", "started")
        return last_message
    if ev_type == "turn.completed":
        usage = event.get("usage", {})
        summary = ", ".join(f"{k}={v}" for k, v in usage.items()) if usage else "completed"
        _print_codex_event("turn", summary)
        return last_message
    if ev_type == "thread.started":
        _print_codex_event("thread", f"id={event.get('thread_id', '?')}")
        return last_message
    _print_codex_event(ev_type, json.dumps(event, ensure_ascii=False))
    return last_message


def _terminate_process(proc: subprocess.Popen[str]) -> None:
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


def run_codex_cli(
    user_prompt: str,
    *,
    model: str,
    reasoning_effort: str,
    network_access: str,
    retries: int,
) -> str:
    ensure_repo_dirs()
    codex_bin = os.environ.get("CODEX_BIN", "codex")
    cmd = [codex_bin, "exec", "--json", "-m", model]
    if reasoning_effort:
        cmd += ["-c", f"model_reasoning_effort=\"{reasoning_effort}\""]
    if network_access:
        cmd += ["-c", f"network_access=\"{network_access}\""]
    cmd.append("-")
    last_error = ""
    for attempt in range(retries + 1):
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(REPO),
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"codex executable not found: {exc}") from exc
        try:
            if proc.stdin:
                proc.stdin.write(user_prompt)
                proc.stdin.close()
            last_message: str | None = None
            if proc.stdout:
                for raw_line in proc.stdout:
                    line = raw_line.strip()
                    if not line:
                        continue
                    last_message = _handle_codex_line(line, last_message)
        except KeyboardInterrupt as exc:
            _terminate_process(proc)
            raise UserAbort("interrupted during Codex stream") from exc
        finally:
            stderr_text = ""
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
                rc = proc.returncode
            if stderr_text:
                _print_codex_event("stderr", stderr_text)
            if rc == 0 and last_message:
                return last_message
            last_error = stderr_text or f"exit={proc.returncode}, no agent message"
        time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"codex CLI failed after {retries + 1} attempts: {last_error}")


def _print_model_banner(model: str, reasoning_effort: str) -> None:
    descriptor = model
    if reasoning_effort:
        descriptor = f"{descriptor}-{reasoning_effort}"
    print(f"[codex][model] {descriptor}")


def run_git(args: Sequence[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(REPO),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def git_status_lines() -> List[str]:
    rc, out, err = run_git(["status", "--porcelain"])
    if rc != 0:
        raise RuntimeError(f"git status failed: {err.strip()}")
    return [line.rstrip() for line in out.splitlines() if line.strip()]


def ensure_clean_worktree() -> None:
    dirty = git_status_lines()
    if dirty:
        raise RuntimeError(
            "Working tree has uncommitted changes. Commit or stash before running the loop runner."
        )


def auto_commit(loop_idx: int, status_lines: Sequence[str]) -> bool:
    if not status_lines:
        print(f"[git] loop {loop_idx:03d} produced no tracked file changes; skipping commit.")
        return True
    rc, _, err = run_git(["add", "-A"])
    if rc != 0:
        print(f"[git] add failed: {err.strip()}")
        return False
    message = f"loop {loop_idx:03d}"
    rc, out, err = run_git(["commit", "-m", message])
    if rc != 0:
        combined = (err or out).strip()
        if "nothing to commit" in combined.lower():
            print(f"[git] loop {loop_idx:03d} had nothing to commit after staging; continuing.")
            return True
        print(f"[git] commit failed: {combined}")
        return False
    print(out.strip() or f"[git] committed {message}")
    return True


def record_raw_output(tag: str, text: str) -> None:
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    path = RAW_OUTPUT_DIR / f"{tag}.txt"
    path.write_text(f"# {timestamp}\n{text.strip()}\n", encoding="utf-8")


def pap_is_frozen() -> tuple[bool, str]:
    pap_path = REPO / "analysis" / "pre_analysis_plan.md"
    if not pap_path.exists():
        return False, "analysis/pre_analysis_plan.md missing"
    try:
        text = pap_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"Unable to read pre-analysis plan: {exc}"
    lower = text.lower()
    if "status: frozen" not in lower:
        return False, "Add 'status: frozen' to the pre-analysis plan"
    if "registry_url" not in lower:
        return False, "Pre-analysis plan must record registry_url"
    if "freeze_commit" not in lower and "freeze_tag" not in lower:
        return False, "Document freeze_commit or freeze_tag in the pre-analysis plan"
    return True, ""


def enforce_phase_transition(before: Dict[str, Any], after: Dict[str, Any]) -> None:
    prev_phase = before.get("phase", "literature")
    next_phase = after.get("phase", prev_phase)
    prev_idx = PHASE_ORDER.index(prev_phase)
    next_idx = PHASE_ORDER.index(next_phase)
    if next_idx < prev_idx:
        raise RuntimeError(f"Phase regression is not allowed ({prev_phase} → {next_phase}).")
    if next_idx > prev_idx + 1:
        raise RuntimeError(f"Cannot skip phases ({prev_phase} → {next_phase}).")
    if prev_phase != next_phase and next_phase == "analysis":
        frozen, reason = pap_is_frozen()
        if not frozen:
            raise RuntimeError(f"Cannot enter analysis until PAP is frozen: {reason}")


def build_loop_prompt(loop_idx: int, state: Dict[str, Any]) -> str:
    datasets = sorted(p.name for p in REPO.glob("*.csv"))
    context = {
        "mode": "science_loop",
        "loop_index": loop_idx,
        "total_loops": state.get("total_loops"),
        "phase_order": PHASE_ORDER,
        "state": state,
        "available_datasets": datasets,
    }
    context_json = json.dumps(context, indent=2, sort_keys=True)
    return f"{PROMPT_HINT}\n\n{context_json}"


def run_science_loop(loop_idx: int, args: argparse.Namespace) -> Dict[str, Any]:
    ensure_repo_dirs()
    ensure_clean_worktree()
    before_state = ensure_state_defaults(read_state())
    if not STATE_PATH.exists():
        write_state(before_state)
    _print_model_banner(args.model, args.reasoning_effort)
    user_prompt = build_loop_prompt(loop_idx, before_state)
    try:
        raw = run_codex_cli(
            user_prompt,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            network_access=args.network_access,
            retries=args.codex_retries,
        )
    except UserAbort:
        raise RuntimeError("Loop cancelled by user during Codex streaming")
    record_raw_output(f"loop_{loop_idx:03d}", raw)
    after_state = ensure_state_defaults(read_state())
    enforce_phase_transition(before_state, after_state)
    status_lines = git_status_lines()
    if not auto_commit(loop_idx, status_lines):
        raise RuntimeError("Unable to auto-commit loop changes")
    updated_state = ensure_state_defaults(after_state)
    updated_state["loop_counter"] = loop_idx
    write_state(updated_state)
    if STOP_FLAG.exists():
        updated_state["stop_now"] = True
        updated_state["stop_reason"] = "stop.flag present"
        write_state(updated_state)
    return ensure_state_defaults(updated_state)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal science loop runner")
    parser.add_argument("--bootstrap", action="store_true", help="Run bootstrap setup and exit unless loops are requested")
    parser.add_argument("--loops", type=int, default=None, help="Number of loops to run (defaults to remaining budget)")
    parser.add_argument("--total-loops", type=int, default=None, help="Override total loop budget stored in state.json")
    parser.add_argument("--model", type=str, default=None, help="Codex model override")
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        default=None,
        help="Override model_reasoning_effort (default from CODEX_REASONING_EFFORT)",
    )
    parser.add_argument(
        "--network-access",
        type=str,
        default=None,
        help="Override network access setting (enabled/disabled)",
    )
    parser.add_argument(
        "--codex-retries",
        type=int,
        default=2,
        help="Number of automatic Codex retries on failure",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=None,
        help="Delay between loops",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    args.model = args.model or MODEL
    args.reasoning_effort = args.reasoning_effort or REASONING_EFFORT
    args.network_access = _normalize_network_setting(args.network_access) or NETWORK_ACCESS
    args.sleep_seconds = args.sleep_seconds if args.sleep_seconds is not None else DEFAULT_SLEEP_SECONDS
    if args.bootstrap:
        run_bootstrap()
        if args.loops in (None, 0):
            return 0
    state = ensure_state_defaults(read_state())
    if args.total_loops is not None:
        state["total_loops"] = max(int(args.total_loops), 0)
        write_state(state)
        state = ensure_state_defaults(read_state())
    loop_budget = args.loops
    if loop_budget is None:
        loop_budget = max(state["total_loops"] - state["loop_counter"], 0)
    if loop_budget <= 0:
        print("No loops to run (budget exhausted or zero loops requested).")
        return 0
    for iteration in range(loop_budget):
        state = ensure_state_defaults(read_state())
        loop_idx = state["loop_counter"] + 1
        print(f"== Loop {loop_idx:03d} ==")
        try:
            state = run_science_loop(loop_idx, args)
        except KeyboardInterrupt:
            print(f"[loop {loop_idx:03d}] interrupted by user")
            return 1
        except RuntimeError as exc:
            print(f"[loop {loop_idx:03d}] {exc}")
            return 1
        if state.get("stop_now"):
            reason = state.get("stop_reason", "agent requested stop")
            print(f"[loop {loop_idx:03d}] stop requested: {reason}")
            break
        loops_left = loop_budget - iteration - 1
        if args.sleep_seconds and loops_left > 0:
            try:
                time.sleep(args.sleep_seconds)
            except KeyboardInterrupt:
                print("Sleep interrupted by user; exiting.")
                return 1
    return 0


if __name__ == "__main__":
    ensure_repo_dirs()
    raise SystemExit(main(sys.argv[1:]))
