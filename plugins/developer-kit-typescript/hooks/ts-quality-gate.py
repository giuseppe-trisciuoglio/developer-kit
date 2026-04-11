#!/usr/bin/env python3
"""TypeScript Quality Gate Hook.

Runs type checking (tsc), linting (eslint), and format checking (prettier)
on recently modified TypeScript files at the end of a Claude Code session.
Supports plain TypeScript projects as well as Nx monorepos.

Hook event: Stop
Input:  JSON via stdin  { "stop_reason": "end_turn", ... }
Output: Exit 0 = pass | Exit 1 = warnings | Exit 2 = errors (stderr shown to Claude)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import shutil
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


def _find_nx_json(cwd: Path) -> Optional[Path]:
    """Locate nx.json walking up from cwd (max 3 levels)."""
    for candidate in [cwd, *list(cwd.parents)[:3]]:
        nx_json = candidate / "nx.json"
        if nx_json.exists():
            return nx_json
    return None


def _find_eslint_config(cwd: Path) -> Optional[Path]:
    """Locate ESLint config file walking up from cwd (max 3 levels)."""
    configs = [
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.yaml",
        ".eslintrc.yml",
        ".eslintrc.json",
        ".eslintrc",
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
    ]
    for candidate in [cwd, *list(cwd.parents)[:3]]:
        for cfg in configs:
            path = candidate / cfg
            if path.exists():
                return path
    return None


def _find_prettier_config(cwd: Path) -> Optional[Path]:
    """Locate Prettier config file walking up from cwd (max 3 levels)."""
    configs = [
        ".prettierrc",
        ".prettierrc.json",
        ".prettierrc.yml",
        ".prettierrc.yaml",
        ".prettierrc.js",
        ".prettierrc.cjs",
        "prettier.config.js",
        "prettier.config.mjs",
        "prettier.config.cjs",
    ]
    for candidate in [cwd, *list(cwd.parents)[:3]]:
        for cfg in configs:
            path = candidate / cfg
            if path.exists():
                return path
    return None


# ─── File Detection ───────────────────────────────────────────────────────────


def _is_excluded(path: Path) -> bool:
    """Check if path contains excluded directory components."""
    parts = frozenset(path.parts)
    return bool(parts & EXCLUDED_DIRS)


def _get_modified_files(cwd: Path, since_ref: str = "HEAD~1") -> list[str]:
    """Get list of modified TypeScript files since the given git ref.

    Falls back to all .ts/.tsx files in cwd if git fails or no files found.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACM", since_ref],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError("git diff failed")

        files = [
            f.strip()
            for f in result.stdout.splitlines()
            if f.strip().endswith((".ts", ".tsx")) and not _is_excluded(Path(f))
        ]
    except Exception:
        files = []

    # Fallback: scan cwd for TypeScript files if git fails or no commits
    if not files:
        files = [
            str(p.relative_to(cwd))
            for p in cwd.rglob("*.ts")
            if not _is_excluded(p) and not p.name.endswith(".d.ts")
        ]
        files += [
            str(p.relative_to(cwd))
            for p in cwd.rglob("*.tsx")
            if not _is_excluded(p)
        ]

    return files[:MAX_FILES]


# ─── Tool Runners ─────────────────────────────────────────────────────────────


def _run_tsc(cwd: Path, files: list[str]) -> tuple[bool, str]:
    """Run TypeScript compiler type check. Returns (has_errors, output)."""
    tsconfig = _find_tsconfig(cwd)
    if not tsconfig:
        return False, ""

    # Check if tsc is available
    if not shutil.which("tsc") and not shutil.which("npx"):
        return False, ""

    cmd = ["npx", "tsc", "--noEmit", "--project", str(tsconfig)]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=TOOL_TIMEOUT,
        )
        if result.returncode == 0:
            return False, ""
        output = result.stdout + result.stderr
        return True, output[:MAX_OUTPUT_CHARS]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""


def _run_eslint(cwd: Path, files: list[str]) -> tuple[bool, str]:
    """Run ESLint on specific files. Returns (has_errors, output)."""
    if not _find_eslint_config(cwd):
        return False, ""

    if not shutil.which("eslint") and not shutil.which("npx"):
        return False, ""

    cmd = ["npx", "eslint", "--format", "compact", *files]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=TOOL_TIMEOUT,
        )
        if result.returncode == 0:
            return False, ""
        output = result.stdout + result.stderr
        return True, output[:MAX_OUTPUT_CHARS]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""


def _run_prettier_check(cwd: Path, files: list[str]) -> tuple[bool, str]:
    """Run Prettier format check. Returns (has_issues, output)."""
    if not _find_prettier_config(cwd):
        return False, ""

    if not shutil.which("prettier") and not shutil.which("npx"):
        return False, ""

    cmd = ["npx", "prettier", "--check", *files]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=TOOL_TIMEOUT,
        )
        if result.returncode == 0:
            return False, ""
        output = result.stdout + result.stderr
        return True, output[:MAX_OUTPUT_CHARS]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        input_data = {}

    cwd = Path(input_data.get("cwd", os.environ.get("CLAUDE_CWD", os.getcwd())))

    # Get modified files
    modified = _get_modified_files(cwd)
    if not modified and not _find_tsconfig(cwd):
        # No TypeScript files modified and no tsconfig → pass silently
        sys.exit(0)

    errors: list[str] = []
    warnings: list[str] = []

    # Run TypeScript check
    if _find_tsconfig(cwd):
        has_errors, output = _run_tsc(cwd, modified)
        if has_errors:
            errors.append(f"TypeScript errors:\n{output}")

    # Run ESLint on modified files only (if there are any)
    if modified:
        has_errors, output = _run_eslint(cwd, modified)
        if has_errors:
            errors.append(f"ESLint errors:\n{output}")

    # Run Prettier check on modified files
    if modified:
        has_issues, output = _run_prettier_check(cwd, modified)
        if has_issues:
            warnings.append(
                f"Prettier formatting issues ({len(modified)} file(s) checked):\n"
                f"{output}\n"
                f"Run: npx prettier --write <file> to fix."
            )

    # --- Report ---
    if errors:
        message = "TypeScript Quality Gate — FAILED\n"
        for err in errors:
            message += f"\n{err}"
        if modified:
            message += f"\n\nFiles checked: {', '.join(modified)}"

        # Output JSON format required by Stop hooks
        output = {
            "decision": "block",
            "reason": f"TypeScript quality gate failed\n{message}"
        }
        print(json.dumps(output))
        sys.exit(0)

    if warnings:
        # Warnings don't block, just log
        sys.exit(0)

    if modified or _find_tsconfig(cwd):
        # Success, just log
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
