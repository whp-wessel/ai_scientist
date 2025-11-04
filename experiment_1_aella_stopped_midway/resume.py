#!/usr/bin/env python3
"""Resume the survey science agent loops without re-running bootstrap."""

from __future__ import annotations

import argparse
import sys
import time

import runner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resume Codex survey agent loops by invoking runner.do_loop() for the "
            "remaining iterations."
        )
    )
    parser.add_argument(
        "--loops-to-go",
        type=int,
        default=20,
        help="Number of loops still to execute (default: 20).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=None,
        help="Optional pause between loops to throttle execution.",
    )
    parser.add_argument(
        "--start-after-loop",
        type=int,
        default=None,
        help=(
            "Override the loop index after which to resume. If not provided, the "
            "value is inferred from artifacts/state.json (loop_counter)."
        ),
    )
    return parser.parse_args()


def determine_start_loop(state: dict[str, object], override: int | None) -> int:
    if override is not None:
        return override + 1
    raw_completed = state.get("loop_counter", 0) if state else 0
    try:
        completed = int(raw_completed)
    except (TypeError, ValueError):
        completed = 0
    return completed + 1


def main() -> int:
    args = parse_args()
    loops_to_go = args.loops_to_go
    if loops_to_go <= 0:
        print("[resume] loops-to-go must be a positive integer.", file=sys.stderr)
        return 1

    runner.ensure_repo_structure()
    state = runner.read_state_json()
    start_loop = determine_start_loop(state, args.start_after_loop)

    print(f"[resume] loops-to-go: {loops_to_go}")
    print(f"[resume] starting at loop index {start_loop}")

    consecutive_git_fails = 0
    consecutive_parse_fails = 0
    final_loop = start_loop + loops_to_go - 1

    for loop_idx in range(start_loop, final_loop + 1):
        print(f"== Resumed Loop {loop_idx} / target {final_loop} ==")
        should_stop, consecutive_git_fails, consecutive_parse_fails = runner.do_loop(
            loop_idx,
            consecutive_git_fails,
            consecutive_parse_fails,
        )
        if should_stop:
            print("[resume] stop requested by agent or guardrail; exiting early.")
            return 0
        if args.sleep_seconds and loop_idx < final_loop:
            time.sleep(args.sleep_seconds)

    print("[resume] completed requested loops.")
    return 0


if __name__ == "__main__":
    sys.exit(main())