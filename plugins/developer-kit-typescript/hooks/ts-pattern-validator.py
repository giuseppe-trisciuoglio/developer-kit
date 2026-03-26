#!/usr/bin/env python3
"""TypeScript Architectural Pattern Validator Hook.

Detects common anti-patterns and NestJS architectural violations in TypeScript
files written or edited by Claude Code. Emits advisory warnings (non-blocking)
so the developer can make an informed decision without halting the workflow.

Hook event: PostToolUse (Write | Edit | MultiEdit)
Input:  JSON via stdin with tool_name and tool_input
Output: Exit 0 = no issues | Exit 1 = advisory warnings (stdout shown to Claude)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import re
import sys
from pathlib import Path

# ─── NestJS Component Patterns ────────────────────────────────────────────────

# Maps NestJS compound file suffix → at least one of these strings must appear
_NESTJS_DECORATOR_MAP: dict[str, list[str]] = {
    ".controller.ts": ["@Controller"],
    ".service.ts": ["@Injectable"],
    ".module.ts": ["@Module"],
    ".guard.ts": ["@Injectable", "CanActivate"],
    ".interceptor.ts": ["@Injectable", "NestInterceptor"],
    ".pipe.ts": ["@Injectable", "PipeTransform"],
    ".filter.ts": ["@Catch", "ExceptionFilter"],
    ".resolver.ts": ["@Resolver"],
    ".gateway.ts": ["@WebSocketGateway"],
}

# ─── Anti-Pattern Rules ───────────────────────────────────────────────────────
# Each entry: (regex_pattern, short_title, actionable_advice)
# Patterns are matched against a comment/string-stripped version of the source.

_ANTI_PATTERNS: list[tuple[str, str, str]] = [
    (
        r"\bany\b",
        "Unsafe 'any' type",
        "Replace 'any' with a specific type or 'unknown' to preserve type safety.",
    ),
    (
        r"@ts-ignore",
        "TypeScript suppression @ts-ignore",
        "Fix the underlying type error instead of suppressing it.",
    ),
    (
        r"@ts-nocheck",
        "TypeScript suppression @ts-nocheck",
        "Fix type errors in this file instead of disabling type checking.",
    ),
    (
        r"\brequire\s*\(",
        "CommonJS require()",
        "Use ES module 'import' syntax. TypeScript projects should avoid require().",
    ),
    (
        r"\bconsole\.(log|debug|info|warn|error)\s*\(",
        "console.* in production code",
        "Use a structured logger (e.g., NestJS Logger, Winston, Pino) instead of console.*.",
    ),
    (
        r"new\s+[A-Z][a-zA-Z]+Service\s*\(",
        "Direct service instantiation",
        "Inject services via the constructor instead of instantiating them with 'new'.",
    ),
    (
        r"new\s+[A-Z][a-zA-Z]+Repository\s*\(",
        "Direct repository instantiation",
        "Inject repositories via the constructor instead of 'new'.",
    ),
]

# ─── Controller-Specific Checks ───────────────────────────────────────────────

# Patterns that suggest direct data-access logic inside a controller
_DB_PATTERNS: list[str] = [
    r"\.(find|findOne|findAll|findById|save|create|update|delete|remove|upsert)\s*\(",
    r"\bRepository\s*<",
    r"\bEntityManager\b",
    r"\bDataSource\b",
    r"\bgetRepository\s*\(",
    r"\bprisma\.",
    r"\bknex\(",
    r"\bdb\.(query|execute|run)\s*\(",
]

# ─── Skip Rules ───────────────────────────────────────────────────────────────

_EXEMPT_SUFFIXES: tuple[str, ...] = (
    ".spec.ts",
    ".test.ts",
    ".e2e-spec.ts",
    ".d.ts",
    ".mock.ts",
    ".fixture.ts",
    ".config.ts",
    ".constants.ts",
    ".seed.ts",
)

_EXEMPT_DIRS: frozenset[str] = frozenset(
    {"node_modules", "dist", "build", ".next", ".turbo", "generated", "__mocks__"}
)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _strip_noise(src: str) -> str:
    """Remove comments and string literals to reduce false positives."""
    # Block comments
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    # Line comments
    src = re.sub(r"//[^\n]*", " ", src)
    # Template literals (basic)
    src = re.sub(r"`[^`]*`", '""', src, flags=re.DOTALL)
    # Double-quoted strings
    src = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', src)
    # Single-quoted strings
    src = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", src)
    return src


def _check_nestjs_decorators(file_path: str, content: str) -> list[str]:
    """Warn if a NestJS component file is missing its expected decorator."""
    warnings: list[str] = []
    for suffix, expected in _NESTJS_DECORATOR_MAP.items():
        if not file_path.endswith(suffix):
            continue
        if not any(dec in content for dec in expected):
            warnings.append(
                f"Missing decorator: '{Path(file_path).name}' should contain "
                f"{' or '.join(expected)}. "
                f"Verify this is a complete NestJS {suffix.lstrip('.')} file."
            )
    return warnings


def _check_anti_patterns(content: str) -> list[str]:
    """Scan stripped source for common TypeScript anti-patterns."""
    warnings: list[str] = []
    clean = _strip_noise(content)
    for pattern, title, advice in _ANTI_PATTERNS:
        if re.search(pattern, clean):
            warnings.append(f"{title}: {advice}")
    return warnings


def _check_controller_db_access(file_path: str, content: str) -> list[str]:
    """Warn if a NestJS controller contains direct database access."""
    if not file_path.endswith(".controller.ts"):
        return []
    clean = _strip_noise(content)
    for pattern in _DB_PATTERNS:
        if re.search(pattern, clean):
            return [
                "Business logic in controller: Direct database/ORM access detected. "
                "Move data access to a service or repository and inject it into the controller."
            ]
    return []


# ─── Entry Point ─────────────────────────────────────────────────────────────


def _extract_content(tool_name: str, tool_input: dict) -> str:
    """Return the new content being written/edited, based on tool type."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "MultiEdit":
        return "\n".join(
            edit.get("new_string", "") for edit in tool_input.get("edits", [])
        )
    return ""


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path: str = tool_input.get("file_path", "")
    content: str = _extract_content(tool_name, tool_input)

    if not file_path or not content:
        sys.exit(0)

    # Only TypeScript / TSX files
    if not (file_path.endswith(".ts") or file_path.endswith(".tsx")):
        sys.exit(0)

    # Skip exempt types and directories
    if any(file_path.endswith(s) for s in _EXEMPT_SUFFIXES):
        sys.exit(0)

    path_obj = Path(file_path)
    if any(part in _EXEMPT_DIRS for part in path_obj.parts):
        sys.exit(0)

    warnings: list[str] = []
    warnings.extend(_check_nestjs_decorators(file_path, content))
    warnings.extend(_check_anti_patterns(content))
    warnings.extend(_check_controller_db_access(file_path, content))

    if warnings:
        print(f"TypeScript pattern advisory for '{path_obj.name}':")
        for i, msg in enumerate(warnings, 1):
            print(f"  {i}. {msg}")
        sys.exit(1)  # Advisory only — does NOT block

    sys.exit(0)


if __name__ == "__main__":
    main()
