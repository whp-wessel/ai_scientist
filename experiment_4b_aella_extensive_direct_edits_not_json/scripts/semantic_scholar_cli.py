#!/usr/bin/env python3
"""Thin Semantic Scholar CLI wrapper mandated by agents.md.

Usage examples:
  python scripts/semantic_scholar_cli.py search --query "childhood religiosity wellbeing" --limit 5 --output lit/queries/loop_000/query_001.json
  python scripts/semantic_scholar_cli.py paper --paper-id 10.1001/jama.2024.12345 --output lit/queries/loop_000/query_002.json

The script enforces a 1 request/second rate limit via `artifacts/.s2_rate_limit.json`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RATE_FILE = REPO_ROOT / "artifacts" / ".s2_rate_limit.json"
BASE_URL = os.getenv("SEMANTIC_SCHOLAR_BASE_URL", "https://api.semanticscholar.org/graph/v1")
DEFAULT_FIELDS = "paperId,title,authors,venue,year,doi,url,tldr,abstract"


def load_api_key() -> str:
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line or line.strip().startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                if key.strip() == "S2_API_Key":
                    value = value.strip().strip('"').strip("'")
                    if value:
                        return value
    api_key = os.getenv("S2_API_Key")
    if api_key:
        return api_key
    raise RuntimeError("S2_API_Key not found in .env or environment variables.")


def enforce_rate_limit():
    now = time.time()
    if RATE_FILE.exists():
        try:
            last_call = json.loads(RATE_FILE.read_text()).get("last_call", 0.0)
        except json.JSONDecodeError:
            last_call = 0.0
        wait = 1.0 - (now - last_call)
        if wait > 0:
            time.sleep(wait)
    RATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    RATE_FILE.write_text(json.dumps({"last_call": time.time()}, indent=2))


def request(endpoint: str, params: dict[str, str] | None = None) -> tuple[dict | None, dict | None]:
    api_key = load_api_key()
    if params:
        params = {k: str(v) for k, v in params.items() if v is not None}
        query = urllib.parse.urlencode(params)
        url = f"{BASE_URL}/{endpoint}?{query}"
    else:
        url = f"{BASE_URL}/{endpoint}"
    enforce_rate_limit()
    headers = {
        "x-api-key": api_key,
        "User-Agent": "SurveyScienceAgent/0.1 (+https://github.com)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
        return json.loads(data), None
    except urllib.error.HTTPError as exc:
        return None, {
            "status_code": exc.code,
            "reason": exc.reason,
            "body": exc.read().decode("utf-8", errors="ignore"),
        }
    except urllib.error.URLError as exc:
        return None, {"status_code": None, "reason": str(exc.reason)}
    except json.JSONDecodeError as exc:
        return None, {"status_code": None, "reason": f"Failed to parse JSON response: {exc}"}


def save_output(payload: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Semantic Scholar CLI helper")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search for papers")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--fields", default=DEFAULT_FIELDS)
    search.add_argument("--offset", type=int, default=0)
    search.add_argument("--output", required=True)

    paper = sub.add_parser("paper", help="Fetch a paper by DOI/ID")
    paper.add_argument("--paper-id", required=True)
    paper.add_argument("--fields", default=DEFAULT_FIELDS)
    paper.add_argument("--output", required=True)

    return parser.parse_args()


def main():
    args = parse_args()
    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    metadata = {"timestamp": timestamp}
    if args.command == "search":
        endpoint = "paper/search"
        params = {
            "query": args.query,
            "limit": args.limit,
            "offset": args.offset,
            "fields": args.fields,
        }
        metadata.update({"command": "search", "endpoint": endpoint, "params": params})
        response, error = request(endpoint, params)
    elif args.command == "paper":
        endpoint = f"paper/{urllib.parse.quote(args.paper_id, safe='')}"
        params = {"fields": args.fields}
        metadata.update({"command": "paper", "endpoint": endpoint, "params": params, "paper_id": args.paper_id})
        response, error = request(endpoint, params)
    else:
        raise SystemExit("Unsupported command")

    output_path = REPO_ROOT / args.output
    if error:
        payload = {"error": error, "request": metadata}
        save_output(payload, output_path)
        print(f"Saved Semantic Scholar response to {output_path}", file=sys.stderr)
        sys.exit(0)

    payload = response or {}
    if isinstance(payload, dict):
        payload.setdefault("_request_metadata", metadata)
    save_output(payload, output_path)
    print(f"Saved Semantic Scholar response to {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
