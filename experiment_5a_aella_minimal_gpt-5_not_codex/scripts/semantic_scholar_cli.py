#!/usr/bin/env python3
"""
Semantic Scholar CLI helper.

Requirements per AGENTS.md:
- Load API key `S2_API_Key` from `.env` in repo root.
- Enforce 1 request/second via `artifacts/.s2_rate_limit.json`.
- Save raw JSON responses under `lit/queries/...`.

Usage examples:
  python scripts/semantic_scholar_cli.py search --query "childhood resiliency wellbeing" --limit 5 --output lit/queries/loop_000/query_001.json
  python scripts/semantic_scholar_cli.py paper --paper-id 10.1001/jama.2024.12345 --output lit/queries/loop_000/query_002.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import urllib.parse
import urllib.request

REPO = Path(__file__).resolve().parents[1]
RATE_FILE = REPO / 'artifacts' / '.s2_rate_limit.json'


def _load_env_key() -> str:
    env_path = REPO / '.env'
    if env_path.exists():
        # Minimal .env parsing
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                if k.strip() == 'S2_API_Key':
                    return v.strip().strip('"').strip("'")
    # Also allow environment variable
    return os.environ.get('S2_API_Key', '')


def _enforce_rate_limit():
    RATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    last = 0.0
    if RATE_FILE.exists():
        try:
            last = json.loads(RATE_FILE.read_text()).get('last_ts', 0.0)
        except Exception:
            last = 0.0
    wait = max(0.0, 1.0 - (now - last))
    if wait > 0:
        time.sleep(wait)
    RATE_FILE.write_text(json.dumps({'last_ts': time.time()}))


def _http_get(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                return {'raw': data.decode('utf-8', errors='ignore')}
    except Exception as e:  # Capture HTTPError and others; return structured error
        out: Dict[str, Any] = {
            'error': True,
            'reason': str(e),
            'url': url,
        }
        if hasattr(e, 'code'):
            out['http_status'] = getattr(e, 'code')
        try:
            # Attempt to read response body
            body = e.read() if hasattr(e, 'read') else None
            if body:
                try:
                    out['body'] = json.loads(body.decode('utf-8'))
                except Exception:
                    out['body'] = body.decode('utf-8', errors='ignore')
        except Exception:
            pass
        return out


def cmd_search(args: argparse.Namespace, api_key: str) -> Dict[str, Any]:
    base = 'https://api.semanticscholar.org/graph/v1/paper/search'
    params = {
        'query': args.query,
        'limit': str(args.limit or 5),
        'fields': args.fields or 'title,authors,year,venue,externalIds,url,abstract'
    }
    url = base + '?' + urllib.parse.urlencode(params)
    headers = {'x-api-key': api_key} if api_key else {}
    _enforce_rate_limit()
    return _http_get(url, headers)


def cmd_paper(args: argparse.Namespace, api_key: str) -> Dict[str, Any]:
    pid = args.paper_id
    base = f'https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(pid)}'
    params = {
        'fields': args.fields or 'title,authors,year,venue,externalIds,url,abstract'
    }
    url = base + '?' + urllib.parse.urlencode(params)
    headers = {'x-api-key': api_key} if api_key else {}
    _enforce_rate_limit()
    return _http_get(url, headers)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Semantic Scholar CLI helper')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_search = sub.add_parser('search', help='Search papers')
    p_search.add_argument('--query', required=True)
    p_search.add_argument('--limit', type=int, default=5)
    p_search.add_argument('--fields', default=None)
    p_search.add_argument('--output', required=True)

    p_paper = sub.add_parser('paper', help='Fetch paper by ID/DOI')
    p_paper.add_argument('--paper-id', required=True)
    p_paper.add_argument('--fields', default=None)
    p_paper.add_argument('--output', required=True)

    args = parser.parse_args(argv)

    api_key = _load_env_key()
    if not api_key:
        print('Warning: S2_API_Key not found in .env or environment; proceeding unauthenticated (may be rate-limited).', file=sys.stderr)

    if args.cmd == 'search':
        data = cmd_search(args, api_key)
    elif args.cmd == 'paper':
        data = cmd_paper(args, api_key)
    else:
        parser.error('Unknown command')

    out_path = REPO / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2))
    print(str(out_path))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
