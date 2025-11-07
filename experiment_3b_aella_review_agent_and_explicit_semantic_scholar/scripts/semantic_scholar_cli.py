#!/usr/bin/env python3
"""Helper for authenticated Semantic Scholar queries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib import error, parse, request

DEFAULT_ENDPOINT = "https://api.semanticscholar.org/graph/v1"
RATE_LIMIT_SECONDS = 1.0
USER_AGENT = "aella-research-agent/1.0"

REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"
RATE_PATH = REPO / "artifacts" / ".s2_rate_limit.json"


def _read_env_file() -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not ENV_PATH.exists():
        return values
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        cleaned = value.strip().strip("\"").strip("'")
        values[key.strip()] = cleaned
    return values


def _load_api_key() -> str:
    key = os.environ.get("S2_API_Key") or os.environ.get("S2_API_KEY")
    if not key:
        env_values = _read_env_file()
        key = env_values.get("S2_API_Key") or env_values.get("S2_API_KEY")
    if not key:
        raise SystemExit("S2_API_Key not found. Set it in .env or export it before running this script.")
    return key.strip()


def _wait_for_slot() -> None:
    last_call = 0.0
    if RATE_PATH.exists():
        try:
            meta = json.loads(RATE_PATH.read_text(encoding="utf-8"))
            last_call = float(meta.get("last_call", 0.0))
        except Exception:
            last_call = 0.0
    now = time.time()
    wait_time = RATE_LIMIT_SECONDS - (now - last_call)
    if wait_time > 0:
        time.sleep(wait_time)


def _record_call_timestamp() -> None:
    RATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RATE_PATH.write_text(json.dumps({"last_call": time.time()}), encoding="utf-8")


def _build_url(endpoint: str, resource: str, params: Dict[str, Any]) -> str:
    base = endpoint.rstrip("/")
    path = resource.lstrip("/")
    url = f"{base}/{path}"
    if params:
        query = parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
        if query:
            url = f"{url}?{query}"
    return url


def _perform_request(url: str, api_key: str, timeout: int) -> Dict[str, Any]:
    headers = {
        "x-api-key": api_key,
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    req = request.Request(url, headers=headers)
    _wait_for_slot()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            data = json.loads(payload)
            status = resp.status
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise SystemExit(f"Semantic Scholar API error {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SystemExit(f"Network error contacting Semantic Scholar: {exc.reason}") from exc
    finally:
        _record_call_timestamp()
    return {"status": status, "body": data}


def _write_output(path: str, payload: Dict[str, Any]) -> Path:
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = (REPO / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def _common_metadata(resource: str, params: Dict[str, Any], url: str) -> Dict[str, Any]:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "resource": resource,
        "url": url,
        "params": params,
    }


def run_search(args: argparse.Namespace) -> None:
    params = {
        "query": args.query,
        "limit": args.limit,
        "offset": args.offset,
        "fields": args.fields,
    }
    resource = "paper/search"
    url = _build_url(args.endpoint, resource, params)
    api_key = _load_api_key()
    response = _perform_request(url, api_key, args.timeout)
    payload = {
        "meta": _common_metadata(resource, params, url),
        "response_status": response["status"],
        "data": response["body"],
    }
    out_path = _write_output(args.output, payload)
    total = response["body"].get("total") if isinstance(response["body"], dict) else None
    count = len(response["body"].get("data", [])) if isinstance(response["body"], dict) else None
    summary = f"saved {count} results" if count is not None else "saved response"
    if total is not None:
        summary = f"{summary} (total={total})"
    print(f"Semantic Scholar search {summary} -> {out_path.relative_to(REPO)}")


def run_paper(args: argparse.Namespace) -> None:
    params = {"fields": args.fields or None}
    resource = f"paper/{args.paper_id}"
    url = _build_url(args.endpoint, resource, params)
    api_key = _load_api_key()
    response = _perform_request(url, api_key, args.timeout)
    payload = {
        "meta": _common_metadata(resource, params, url),
        "response_status": response["status"],
        "data": response["body"],
    }
    out_path = _write_output(args.output, payload)
    title = response["body"].get("title") if isinstance(response["body"], dict) else None
    if title:
        print(f"Semantic Scholar paper '{title}' saved -> {out_path.relative_to(REPO)}")
    else:
        print(f"Semantic Scholar paper saved -> {out_path.relative_to(REPO)}")


def run_custom(args: argparse.Namespace) -> None:
    params = {}
    for pair in args.param or []:
        if "=" not in pair:
            raise SystemExit(f"Invalid --param '{pair}'. Use key=value format.")
        key, value = pair.split("=", 1)
        params[key] = value
    resource = args.resource
    url = _build_url(args.endpoint, resource, params)
    api_key = _load_api_key()
    response = _perform_request(url, api_key, args.timeout)
    payload = {
        "meta": _common_metadata(resource, params, url),
        "response_status": response["status"],
        "data": response["body"],
    }
    out_path = _write_output(args.output, payload)
    print(f"Semantic Scholar custom call saved -> {out_path.relative_to(REPO)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Authenticated Semantic Scholar helper (1 request/sec limit)")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Base API endpoint")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Call /graph/v1/paper/search")
    search.add_argument("--query", required=True, help="Search query string")
    search.add_argument("--limit", type=int, default=5, help="Number of records to return")
    search.add_argument("--offset", type=int, default=0, help="Pagination offset")
    search.add_argument("--output", required=True, help="Path to write the JSON response")
    search.add_argument(
        "--fields",
        default="title,authors,year,venue,url,externalIds,abstract,publicationTypes",
        help="Comma-separated fields to request",
    )
    search.set_defaults(func=run_search)

    paper = subparsers.add_parser("paper", help="Fetch a specific paper by ID/DOI/arXiv")
    paper.add_argument("--paper-id", required=True, help="Semantic Scholar paper ID, DOI, or arXiv identifier")
    paper.add_argument("--output", required=True, help="Path to write the JSON response")
    paper.add_argument(
        "--fields",
        default="title,abstract,authors,year,venue,url,openAccessPdf,externalIds,citationCount",
        help="Comma-separated fields to request",
    )
    paper.set_defaults(func=run_paper)

    custom = subparsers.add_parser("custom", help="Call an arbitrary Graph API resource")
    custom.add_argument("--resource", required=True, help="Resource path, e.g., paper/search or author/<id>")
    custom.add_argument("--param", action="append", help="Additional query params in key=value form")
    custom.add_argument("--output", required=True, help="Path to write the JSON response")
    custom.set_defaults(func=run_custom)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
