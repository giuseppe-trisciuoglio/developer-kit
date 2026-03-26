#!/usr/bin/env python3
"""TypeScript File Structure Validator Hook.

Validates file naming conventions (kebab-case) and NestJS module structure
when Claude writes a TypeScript file.

Hook event: PostToolUse (Write)
Input:  JSON via stdin  { "tool_name": "Write", "tool_input": { "file_path": "...", "content": "..." } }
Output: Exit 0 = valid | Exit 2 = block (stderr shown to Claude)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

# ─── Naming Convention Configuration ──────────────────────────────────────────

# Compound suffixes used in NestJS — order matters (longest first)
NESTJS_SUFFIXES: tuple[str, ...] = (
    ".controller.spec.ts",
    ".service.spec.ts",
    ".module.spec.ts",
    ".controller.ts",
    ".service.ts",
    ".module.ts",
    ".guard.ts",
    ".interceptor.ts",
    ".pipe.ts",
    ".filter.ts",
    ".decorator.ts",
    ".middleware.ts",
    ".resolver.ts",
    ".gateway.ts",
    ".repository.ts",
    ".dto.ts",
    ".entity.ts",
    ".schema.ts",
    ".interface.ts",
    ".enum.ts",
    ".constants.ts",
    ".types.ts",
    ".config.ts",
    ".mock.ts",
    ".fixture.ts",
    ".spec.ts",
    ".test.ts",
    ".e2e-spec.ts",
    ".d.ts",
)

# Directories that bypass all validation
EXEMPT_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        ".git",
        "dist",
        "build",
        ".next",
        ".turbo",
        "__tests__",
        "test",
        "tests",
        "e2e",
        "mocks",
        "__mocks__",
        "generated",
        ".cache",
    }
)

# Regex for valid kebab-case base names (lowercase letters, digits, hyphens)
_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# Regex for valid index files
_INDEX_RE = re.compile(r"^index\.(ts|tsx|js|jsx)$")


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _to_kebab(name: str) -> str:
    """Convert PascalCase / camelCase to kebab-case."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s).lower()


def _split_name(filename: str) -> tuple[str, str]:
    """Return (base, compound_suffix) for a filename.

    Example: 'user-profile.controller.ts' → ('user-profile', '.controller.ts')
    """
    for suffix in NESTJS_SUFFIXES:
        if filename.endswith(suffix):
            return filename[: -len(suffix)], suffix
    p = Path(filename)
    return p.stem, p.suffix


def _in_exempt_dir(path: Path) -> bool:
    return any(part in EXEMPT_DIRS for part in path.parts[:-1])


# ─── Validation ───────────────────────────────────────────────────────────────


def _validate(file_path: str) -> Optional[str]:
    """Return an error message string if the file violates naming rules, else None."""
    path = Path(file_path)
    filename = path.name

    # Only validate TypeScript / TSX files
    if not (file_path.endswith(".ts") or file_path.endswith(".tsx")):
        return None

    # Skip exempt directories
    if _in_exempt_dir(path):
        return None

    # Allow index files without further checks
    if _INDEX_RE.match(filename):
        return None

    base, suffix = _split_name(filename)

    if not base:
        return None

    if not _KEBAB_RE.match(base):
        suggested = _to_kebab(base)
        return (
            f"File naming violation: '{filename}'\n"
            f"  Base name '{base}' must use kebab-case.\n"
            f"  Rename to: '{suggested}{suffix}'\n"
            f"  Examples: 'user-profile{suffix}', 'auth-token{suffix}'"
        )

    return None


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name") != "Write":
        sys.exit(0)

    file_path: str = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    error = _validate(file_path)
    if error:
        print("TypeScript file structure violation:", file=sys.stderr)
        print(f"  {error}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Correct the file name before proceeding.", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
