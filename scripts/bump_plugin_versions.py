#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bump versions in marketplace.json, plugin.json files, and tile.json."
    )
    parser.add_argument(
        "--version",
        default=os.environ.get("VERSION", "").strip(),
        help="Explicit semantic version to set (x.y.z).",
    )
    parser.add_argument(
        "--bump",
        default=os.environ.get("BUMP", "patch").strip() or "patch",
        choices=("major", "minor", "patch"),
        help="Semver segment to bump when --version is not provided.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def compute_version(current_version: str, requested_version: str, bump_kind: str) -> str:
    if not SEMVER_PATTERN.match(current_version):
        print(
            f"Current marketplace version is not semantic: {current_version}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if requested_version:
        if not SEMVER_PATTERN.match(requested_version):
            print(
                f"Invalid VERSION: {requested_version}. Expected semantic version x.y.z",
                file=sys.stderr,
            )
            raise SystemExit(1)
        return requested_version

    major, minor, patch = (int(part) for part in current_version.split("."))
    if bump_kind == "major":
        return f"{major + 1}.0.0"
    if bump_kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    tile_path = repo_root / "tile.json"
    plugin_paths = sorted((repo_root / "plugins").glob("*/.claude-plugin/plugin.json"))

    if not marketplace_path.exists():
        print(f"Missing {marketplace_path}", file=sys.stderr)
        return 1
    if not tile_path.exists():
        print(f"Missing {tile_path}", file=sys.stderr)
        return 1
    if not plugin_paths:
        print("No plugin.json files found under plugins/", file=sys.stderr)
        return 1

    marketplace = load_json(marketplace_path)
    current_version = str(marketplace.get("version", "")).strip()
    new_version = compute_version(current_version, args.version.strip(), args.bump)

    marketplace["version"] = new_version
    for plugin in marketplace.get("plugins", []):
        plugin["version"] = new_version
    write_json(marketplace_path, marketplace)

    for plugin_path in plugin_paths:
        plugin_data = load_json(plugin_path)
        plugin_data["version"] = new_version
        write_json(plugin_path, plugin_data)

    tile = load_json(tile_path)
    tile["version"] = new_version
    write_json(tile_path, tile)

    print(f"Bumped version: {current_version} -> {new_version}")
    print(f"Updated marketplace file: {marketplace_path.relative_to(repo_root)}")
    print(f"Updated plugin manifests: {len(plugin_paths)}")
    print(f"Updated tile file: {tile_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
