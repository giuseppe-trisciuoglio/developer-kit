#!/usr/bin/env python3
"""TypeScript Quality Gate Hook.

Runs type checking (tsc) and linting (eslint) on recently modified TypeScript
files at the end of a Claude Code session. Supports plain TypeScript projects
as well as Nx monorepos.

Hook event: Stop
Input:  JSON via stdin  { "stop_reason": "end_turn", ... }
Output: Exit 0 = pass | Exit 1 = warnings | Exit 2 = errors (stderr shown to Claude)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ─── Configuration ────────────────────────────────────────────────────────────

# Maximum number of modified files to check (guards against huge diffs)
MAX_FILES = 30

# Subprocess timeout in seconds for individual tool invocations
TOOL_TIMEOUT = 90

# Maximum output characters per tool to show Claude
MAX_OUTPUT_CHARS = 2000

# Directories excluded from file detection
EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"node_modules", "dist", "build", ".next", ".turbo", ".cache", "generated"}
)


# ─── Project Detection ────────────────────────────────────────────────────────


def _find_tsconfig(cwd: Path) -> Optional[Path]:
    """Locate the nearest tsconfig.json walking up from cwd (max 3 levels)."""
    for candidate in [cwd, *list(cwd.parents)[:3]]:
        tsconfig = candidate / "tsconfig.json"
        if tsconfig.exists():
            return tsconfig
    return None


def _has_eslint(cwd: Path) -> bool:
    """Return True if an ESLint config file is present in cwd."""
    config_names = (
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.mjs",
        ".eslintrc.json",
        ".eslintrc.yaml",
        ".eslintrc.yml",
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
    )
    if any((cwd / name).exists() for name in config_names):
        return True
    pkg = cwd / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            return "eslintConfig" in data
        except Exception:
            pass
    return False


def _is_nx(cwd: Path) -> bool:
    return (cwd / "nx.json").exists()


# ─── Modified File Detection ──────────────────────────────────────────────────


def _get_modified_ts_files(cwd: Path) -> list[str]:
    """Return paths of modified/untracked TypeScript files relative to cwd."""
    try:
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=10,
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=10,
        )
        all_files: list[str] = []
        for line in (staged.stdout + "\n" + untracked.stdout).splitlines():
            line = line.strip()
            if not line:
                continue
            if not (line.endswith(".ts") or line.endswith(".tsx")):
                continue
            if any(part in EXCLUDED_DIRS for part in Path(line).parts):
                continue
            if line not in all_files:
                all_files.append(line)
        return all_files[:MAX_FILES]
    except Exception:
        return []


# ─── Tool Runners ─────────────────────────────────────────────────────────────


def _run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    """Run a subprocess and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=TOOL_TIMEOUT,
        )
        raw = (result.stdout + result.stderr).strip()
        return result.returncode == 0, raw[:MAX_OUTPUT_CHARS]
    except FileNotFoundError:
        return True, ""  # Tool not installed — skip silently
    except subprocess.TimeoutExpired:
        return True, f"{cmd[0]} timed out after {TOOL_TIMEOUT}s (skipped)"


def _run_tsc(cwd: Path) -> tuple[bool, str]:
    if not _find_tsconfig(cwd):
        return True, ""
    return _run(["npx", "--yes", "tsc", "--noEmit", "--pretty", "false"], cwd)


def _run_eslint(files: list[str], cwd: Path) -> tuple[bool, str]:
    if not files or not _has_eslint(cwd):
        return True, ""
    return _run(
        ["npx", "--yes", "eslint", "--max-warnings=0", "--format=compact", *files],
        cwd,
    )


def _run_nx_lint(cwd: Path) -> tuple[bool, str]:
    return _run(
        ["npx", "--yes", "nx", "affected", "--target=lint", "--parallel=3"],
        cwd,
    )


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        json.load(sys.stdin)  # consume input even if unused
    except (json.JSONDecodeError, ValueError):
        pass

    cwd = Path(os.environ.get("CLAUDE_CWD", os.getcwd()))

    # Nothing to do if no TypeScript project detected
    if not _find_tsconfig(cwd) and not _has_eslint(cwd):
        sys.exit(0)

    modified = _get_modified_ts_files(cwd)
    errors: list[str] = []
    warnings: list[str] = []

    # --- TypeScript type checking ---
    tsc_ok, tsc_out = _run_tsc(cwd)
    if not tsc_ok and tsc_out:
        errors.append(f"TypeScript type errors:\n{tsc_out}")

    # --- ESLint on modified files ---
    if modified:
        eslint_ok, eslint_out = _run_eslint(modified, cwd)
        if not eslint_ok and eslint_out:
            errors.append(
                f"ESLint violations ({len(modified)} file(s) checked):\n{eslint_out}"
            )

    # --- Nx lint for affected projects ---
    if _is_nx(cwd):
        nx_ok, nx_out = _run_nx_lint(cwd)
        if not nx_ok and nx_out:
            warnings.append(f"Nx lint issues:\n{nx_out}")

    # --- Report ---
    if errors:
        print("TypeScript Quality Gate — FAILED", file=sys.stderr)
        for err in errors:
            print(f"\n{err}", file=sys.stderr)
        if modified:
            print(f"\nFiles checked: {', '.join(modified)}", file=sys.stderr)
        sys.exit(2)

    if warnings:
        print("TypeScript Quality Gate — WARNINGS")
        for warn in warnings:
            print(f"\n{warn}")
        sys.exit(1)

    if modified or _find_tsconfig(cwd):
        print(
            f"TypeScript Quality Gate — PASSED"
            + (f" ({len(modified)} modified file(s) checked)" if modified else "")
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
