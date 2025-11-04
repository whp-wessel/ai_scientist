#!/usr/bin/env python3

"""
Update reproducibility checkpoint artifacts (session info + dataset checksums).

Usage:
    python analysis/code/update_repro_checkpoints.py \
        --config config/agent_config.yaml \
        --data data/raw/childhoodbalancedpublic_original.csv \
        --data data/clean/childhoodbalancedpublic_with_csa_indicator.csv

The script reads seed/output locations from the config file unless paths are
provided via CLI flags. All random operations are seeded to ensure deterministic
behaviour conditional on the environment.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import platform
import random
import subprocess
import sys
from typing import Iterable, List

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh reproducibility checkpoints.")
    parser.add_argument(
        "--config",
        default="config/agent_config.yaml",
        help="Path to agent configuration YAML.",
    )
    parser.add_argument(
        "--data",
        action="append",
        default=[],
        help="Data file(s) to checksum; repeat flag for multiple files.",
    )
    parser.add_argument(
        "--session-info",
        default=None,
        help="Override output path for session info text file.",
    )
    parser.add_argument(
        "--checksums",
        default=None,
        help="Override output path for dataset checksums JSON.",
    )
    return parser.parse_args()


def load_config(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_parent(path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def gather_session_info(seed: int) -> dict:
    info = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "model": os.environ.get("CODEX_MODEL", "gpt-5-codex"),
        "seed": seed,
    }
    try:
        info["git_head"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError as exc:
        info["git_head_error"] = str(exc)

    try:
        info["git_status"] = subprocess.check_output(
            ["git", "status", "--short", "--branch"], text=True
        )
    except subprocess.CalledProcessError as exc:
        info["git_status_error"] = str(exc)

    try:
        info["pip_freeze"] = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True
        )
    except subprocess.CalledProcessError as exc:
        info["pip_freeze_error"] = str(exc)

    return info


def write_session_info(path: pathlib.Path, info: dict) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fh:
        for key in [
            "timestamp_utc",
            "python",
            "platform",
            "cwd",
            "model",
            "seed",
            "git_head",
            "git_status",
        ]:
            if key in info:
                fh.write(f"{key}: {info[key]}\n")
        if "pip_freeze" in info:
            fh.write("pip_freeze:\n")
            fh.write(info["pip_freeze"])
        if "pip_freeze_error" in info:
            fh.write("pip_freeze_error:\n")
            fh.write(info["pip_freeze_error"])


def compute_checksums(paths: Iterable[pathlib.Path]) -> List[dict]:
    rows = []
    for path in paths:
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        stat = path.stat()
        rows.append(
            {
                "path": str(path),
                "sha256": sha,
                "size_bytes": stat.st_size,
                "mtime": dt.datetime.fromtimestamp(
                    stat.st_mtime, tz=dt.timezone.utc
                ).isoformat(),
            }
        )
    return rows


def write_checksums(path: pathlib.Path, rows: Iterable[dict]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(list(rows), fh, indent=2)
        fh.write("\n")


def main() -> None:
    args = parse_args()
    cfg_path = pathlib.Path(args.config)
    cfg = load_config(cfg_path)

    seed = int(cfg.get("seed", 0))
    random.seed(seed)

    repro_cfg = cfg.get("reproducibility", {})

    session_info_path = pathlib.Path(
        args.session_info or repro_cfg.get("session_info", "artifacts/session_info.txt")
    )
    checksums_path = pathlib.Path(
        args.checksums or repro_cfg.get("checksums", "artifacts/checksums.json")
    )

    data_files = (
        [pathlib.Path(p) for p in args.data]
        if args.data
        else [
            pathlib.Path("data/raw/childhoodbalancedpublic_original.csv"),
            pathlib.Path("data/clean/childhoodbalancedpublic_with_csa_indicator.csv"),
        ]
    )

    info = gather_session_info(seed)
    write_session_info(session_info_path, info)

    checksum_rows = compute_checksums(data_files)
    write_checksums(checksums_path, checksum_rows)


if __name__ == "__main__":
    main()
