#!/usr/bin/env python3
"""TypeScript Prettier Auto-Format Hook.

Automatically runs Prettier on TypeScript/JavaScript files after Claude writes
or edits them, keeping the codebase consistently formatted without requiring a
manual format step.

Hook event: PostToolUse (Write | Edit | MultiEdit)  [async]
Input:  JSON via stdin with tool_name and tool_input
Output:
  - Exit 0 = file formatted silently (or prettier not found)
  - Exit 1 = advisory note shown to Claude (formatted successfully)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ─── Target file extensions ───────────────────────────────────────────────────

_FORMATTABLE: tuple[str, ...] = (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs")

# ─── Prettier config file names ───────────────────────────────────────────────

_PRETTIER_CONFIGS: tuple[str, ...] = (
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yaml",
    ".prettierrc.yml",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
    "prettier.config.ts",
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _find_project_root(start: Path) -> Path:
    """Walk up from start to find the nearest package.json (= project root)."""
    current = start if start.is_dir() else start.parent
    for _ in range(20):
        if (current / "package.json").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return start if start.is_dir() else start.parent


def _has_prettier(root: Path) -> bool:
    """Return True if the project has a Prettier config or lists prettier as a dependency."""
    # Config file presence
    for cfg in _PRETTIER_CONFIGS:
        if (root / cfg).exists():
            return True
    # package.json "prettier" key or devDependency
    pkg = root / "package.json"
    if pkg.exists():
        try:
            import json as _json

            data = _json.loads(pkg.read_text(encoding="utf-8"))
            if "prettier" in data:
                return True
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "prettier" in deps:
                return True
        except Exception:
            pass
    return False


def _resolve_prettier(root: Path) -> list[str]:
    """Return the command prefix to invoke prettier, preferring local bin."""
    local = root / "node_modules" / ".bin" / "prettier"
    if local.exists():
        return [str(local)]
    npx = shutil.which("npx")
    if npx:
        return [npx, "prettier"]
    return []


def _get_file_path(tool_name: str, tool_input: dict) -> str:
    """Extract the target file path from any tool type."""
    return tool_input.get("file_path", "")


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path = _get_file_path(tool_name, data.get("tool_input", {}))
    if not file_path:
        sys.exit(0)

    # Only format TS/JS files
    if not any(file_path.endswith(ext) for ext in _FORMATTABLE):
        sys.exit(0)

    resolved = Path(file_path)
    if not resolved.exists():
        sys.exit(0)

    cwd = Path(os.environ.get("CLAUDE_CWD", os.getcwd()))
    root = _find_project_root(resolved)

    if not _has_prettier(root):
        sys.exit(0)

    prettier_cmd = _resolve_prettier(root)
    if not prettier_cmd:
        sys.exit(0)

    try:
        subprocess.run(
            [*prettier_cmd, "--write", str(resolved)],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=15,
        )
        # Brief advisory so Claude knows the file was reformatted
        rel = resolved.relative_to(cwd) if resolved.is_absolute() and resolved.is_relative_to(cwd) else resolved
        message = f"[Prettier] Auto-formatted: {rel}"
        # Output JSON format for advisory
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": message
            }
        }
        print(json.dumps(output))
        sys.exit(0)
    except (subprocess.TimeoutExpired, OSError):
        sys.exit(0)


if __name__ == "__main__":
    main()
