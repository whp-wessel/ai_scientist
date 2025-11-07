#!/usr/bin/env python3
"""Minimal Semantic Scholar CLI helper with rate limiting and local logging."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional
from urllib import parse, request, error

BASE_URL = "https://api.semanticscholar.org/graph/v1"
RATE_LIMIT_FILE = Path("artifacts/.s2_rate_limit.json")
DEFAULT_FIELDS = [
    "title",
    "year",
    "abstract",
    "url",
    "venue",
    "authors",
    "publicationTypes",
    "publicationDate",
    "externalIds",
]


def _load_env_value(env_key: str, env_path: Path = Path(".env")) -> Optional[str]:
    """Return environment variable, falling back to a simple .env parser."""
    value = os.environ.get(env_key)
    if value:
        return value.strip()
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip() == env_key:
                return val.strip().strip('"').strip("'")
    return None


def _respect_rate_limit(min_interval: float = 1.0) -> None:
    """Enforce the 1 req/s limit documented in the charter."""
    RATE_LIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    last_ts = None
    if RATE_LIMIT_FILE.exists():
        try:
            last_ts = json.loads(RATE_LIMIT_FILE.read_text()).get("last_request_ts")
        except json.JSONDecodeError:
            last_ts = None
    if isinstance(last_ts, (int, float)) and now - last_ts < min_interval:
        time.sleep(min_interval - (now - last_ts))
    RATE_LIMIT_FILE.write_text(json.dumps({"last_request_ts": time.time()}))


def _request(path: str, params: Dict[str, str], headers: Dict[str, str]) -> Dict:
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{parse.urlencode(params)}"
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except error.HTTPError as exc:  # pragma: no cover - network failure path
        sys.stderr.write(f"Semantic Scholar API error: {exc.read().decode('utf-8')}\n")
        raise


def _write_output(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Run a paper search query.")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--fields", default=",".join(DEFAULT_FIELDS))
    search.add_argument("--output", required=True)

    paper = subparsers.add_parser("paper", help="Fetch a paper by Semantic Scholar ID/DOI.")
    paper.add_argument("--paper-id", required=True)
    paper.add_argument("--fields", default=",".join(DEFAULT_FIELDS))
    paper.add_argument("--output", required=True)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    headers = {
        "User-Agent": "ai-scientist-cli/0.1",
        "Accept": "application/json",
    }
    api_key = _load_env_value("S2_API_Key")
    if api_key:
        headers["x-api-key"] = api_key

    if args.command == "search":
        path = "/paper/search"
        params = {"query": args.query, "limit": str(args.limit), "fields": args.fields}
    else:
        path = f"/paper/{parse.quote(args.paper_id)}"
        params = {"fields": args.fields}

    _respect_rate_limit()
    payload = _request(path, params, headers)
    _write_output(Path(args.output), payload)


if __name__ == "__main__":
    main()
