#!/usr/bin/env python3
"""Lightweight Semantic Scholar CLI wrapper with repo-specific guardrails."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import requests

ROOT = Path(__file__).resolve().parents[1]
RATE_LIMIT_PATH = ROOT / "artifacts" / ".s2_rate_limit.json"
DEFAULT_FIELDS = (
    "title,abstract,year,authors,url,venue,publicationTypes,externalIds"
)


def load_env() -> Dict[str, str]:
    env = {}
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def get_api_key() -> str | None:
    return os.environ.get("S2_API_Key") or load_env().get("S2_API_Key")


def enforce_rate_limit(min_interval: float = 1.0) -> None:
    RATE_LIMIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    if RATE_LIMIT_PATH.exists():
        try:
            last = json.loads(RATE_LIMIT_PATH.read_text())
            last_ts = float(last.get("last_request_ts", 0.0))
        except Exception:
            last_ts = 0.0
        wait = min_interval - (now - last_ts)
        if wait > 0:
            time.sleep(wait)
    RATE_LIMIT_PATH.write_text(json.dumps({"last_request_ts": time.time()}))


def make_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"User-Agent": "ai_scientist_cli/1.0"}
    api_key = get_api_key()
    if api_key:
        headers["x-api-key"] = api_key
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def write_output(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def cmd_search(args: argparse.Namespace) -> None:
    enforce_rate_limit()
    params = {
        "query": args.query,
        "limit": args.limit,
        "fields": args.fields or DEFAULT_FIELDS,
    }
    payload = make_request("https://api.semanticscholar.org/graph/v1/paper/search", params)
    write_output(args.output, payload)


def cmd_paper(args: argparse.Namespace) -> None:
    enforce_rate_limit()
    params = {"fields": args.fields or DEFAULT_FIELDS}
    url = f"https://api.semanticscholar.org/graph/v1/paper/{args.paper_id}"
    payload = make_request(url, params)
    write_output(args.output, payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Semantic Scholar helper CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Run a paper search query.")
    search.add_argument("--query", required=True, help="Search query string.")
    search.add_argument("--limit", type=int, default=10, help="Max papers to return.")
    search.add_argument(
        "--fields",
        default=None,
        help="Comma-separated list of Graph API fields (default: curated set).",
    )
    search.add_argument("--output", type=Path, required=True, help="Where to save JSON.")
    search.set_defaults(func=cmd_search)

    paper = subparsers.add_parser("paper", help="Fetch metadata for a paper id/DOI.")
    paper.add_argument("--paper-id", required=True, help="Paper identifier or DOI.")
    paper.add_argument(
        "--fields",
        default=None,
        help="Comma-separated list of Graph API fields (default: curated set).",
    )
    paper.add_argument("--output", type=Path, required=True, help="Where to save JSON.")
    paper.set_defaults(func=cmd_paper)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except requests.HTTPError as err:
        sys.stderr.write(f"Semantic Scholar request failed: {err}\\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
