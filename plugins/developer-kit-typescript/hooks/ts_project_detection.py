#!/usr/bin/env python3
"""Shared TypeScript project detection helpers for plugin hooks."""

import json
import os
from pathlib import Path
from typing import Optional

_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"node_modules", ".git", "dist", "build", ".next", ".turbo", ".cache", "coverage"}
)
_TS_EXTENSIONS: tuple[str, ...] = (".ts", ".tsx", ".mts", ".cts")
_TS_PACKAGES: frozenset[str] = frozenset(
    {"typescript", "ts-node", "tsx", "ts-jest", "@swc-node/register"}
)


def get_cwd() -> Path:
    """Return the Claude working directory as a Path."""
    return Path(os.environ.get("CLAUDE_CWD", os.getcwd()))


def _package_declares_typescript(package_json: Path) -> bool:
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False

    dependency_blocks = (
        data.get("dependencies", {}),
        data.get("devDependencies", {}),
        data.get("peerDependencies", {}),
        data.get("optionalDependencies", {}),
    )

    return any(pkg in deps for deps in dependency_blocks for pkg in _TS_PACKAGES)


def _directory_has_typescript_markers(path: Path) -> bool:
    try:
        if any(path.glob("tsconfig*.json")):
            return True
    except OSError:
        return False

    package_json = path / "package.json"
    return package_json.exists() and _package_declares_typescript(package_json)


def _scan_descendants(path: Path, max_depth: int = 3) -> bool:
    try:
        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            depth = len(root_path.relative_to(path).parts)
            dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIRS]

            if depth >= max_depth:
                dirs[:] = []

            if any(name.startswith("tsconfig") and name.endswith(".json") for name in files):
                return True

            if any(Path(name).suffix in _TS_EXTENSIONS for name in files):
                return True

            package_json = root_path / "package.json"
            if package_json.exists() and _package_declares_typescript(package_json):
                return True
    except OSError:
        return False

    return False


def is_typescript_project(cwd: Optional[Path] = None) -> bool:
    """Return True when the current workspace looks like a TypeScript project."""
    current = (cwd or get_cwd()).resolve()

    for candidate in [current, *list(current.parents)[:6]]:
        if _directory_has_typescript_markers(candidate):
            return True

    return _scan_descendants(current)
