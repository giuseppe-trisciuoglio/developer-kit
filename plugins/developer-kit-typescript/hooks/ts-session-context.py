#!/usr/bin/env python3
"""TypeScript Session Context Hook.

Injects project context (git branch, recent commits, pending TODOs) into
Claude's context window at the start of each development session.

Hook event: PreToolUse (any tool, first invocation only per session)
Input:  JSON via stdin  { "tool_name": "...", "tool_input": {...} }
Output: Exit 0 = silent proceed | Exit 1 = inject context message to Claude

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

# Temporary marker file prefix — keyed by process group to scope to session
_MARKER_PREFIX = "/tmp/.ts-session-ctx-"

# Maximum characters for TODO.md content to avoid flooding the context
_TODO_MAX_CHARS = 600

# Maximum number of recent commits to show
_COMMIT_COUNT = 5

# Known TypeScript/JavaScript framework dependencies to detect
_FRAMEWORK_DEPS: list[tuple[str, str]] = [
    ("@nestjs/core", "NestJS"),
    ("next", "Next.js"),
    ("react", "React"),
    ("expo", "Expo / React Native"),
    ("turbo", "Turborepo"),
    ("nx", "Nx monorepo"),
    ("@nrwl/workspace", "Nx monorepo"),
    ("@angular/core", "Angular"),
    ("vue", "Vue"),
    ("svelte", "Svelte"),
    ("fastify", "Fastify"),
    ("express", "Express"),
    ("hono", "Hono"),
]


# ─── Session Marker ───────────────────────────────────────────────────────────


def _session_key() -> str:
    """Return a stable per-session identifier (process group ID)."""
    try:
        return str(os.getpgrp())
    except AttributeError:
        return str(os.getpid())


def _is_first_call() -> bool:
    """Return True (and create the marker) if this is the first hook call in the session."""
    marker = Path(f"{_MARKER_PREFIX}{_session_key()}")
    if marker.exists():
        return False
    try:
        marker.touch()
    except OSError:
        pass
    return True


# ─── Context Collectors ───────────────────────────────────────────────────────


def _run_git(args: list[str], cwd: str) -> str:
    """Run a git command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _git_section(cwd: str) -> str:
    """Build a Git context block (branch, recent commits, working tree status)."""
    parts: list[str] = []

    branch = _run_git(["branch", "--show-current"], cwd)
    if branch:
        parts.append(f"Branch: {branch}")

    commits = _run_git(["log", "--oneline", f"-{_COMMIT_COUNT}"], cwd)
    if commits:
        indented = "\n  ".join(commits.splitlines())
        parts.append(f"Recent commits:\n  {indented}")

    status = _run_git(["status", "--short"], cwd)
    if status:
        indented = "\n  ".join(status.splitlines())
        parts.append(f"Uncommitted changes:\n  {indented}")

    return "\n".join(parts) if parts else ""


def _project_section(cwd: str) -> str:
    """Detect TypeScript project metadata from package.json."""
    pkg_path = Path(cwd) / "package.json"
    if not pkg_path.exists():
        return ""
    try:
        data = json.loads(pkg_path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    frameworks = [label for dep, label in _FRAMEWORK_DEPS if dep in all_deps]

    name = data.get("name", "")
    version = data.get("version", "")
    stack = ", ".join(frameworks) if frameworks else "TypeScript"

    parts: list[str] = []
    if name:
        parts.append(f"Project: {name}" + (f" v{version}" if version else ""))
    parts.append(f"Stack: {stack}")

    node_version = data.get("engines", {}).get("node", "")
    if node_version:
        parts.append(f"Node engine: {node_version}")

    return "\n".join(parts) if parts else ""


def _todo_section(cwd: str) -> str:
    """Read TODO.md (or TODO) if present."""
    for name in ("TODO.md", "todo.md", "TODO"):
        path = Path(cwd) / name
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    truncated = content[:_TODO_MAX_CHARS]
                    suffix = "..." if len(content) > _TODO_MAX_CHARS else ""
                    return f"{name}:\n{truncated}{suffix}"
            except OSError:
                pass
    return ""


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        json.load(sys.stdin)  # consume input
    except (json.JSONDecodeError, ValueError):
        pass

    if not _is_first_call():
        sys.exit(0)

    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())

    sections: list[str] = []

    project = _project_section(cwd)
    if project:
        sections.append(project)

    git = _git_section(cwd)
    if git:
        sections.append(git)

    todos = _todo_section(cwd)
    if todos:
        sections.append(todos)

    if not sections:
        sys.exit(0)

    header = "=== TypeScript Project Context ==="
    body = "\n\n".join(sections)
    print(f"{header}\n{body}")

    sys.exit(1)  # Exit 1: show context to Claude without blocking the tool


if __name__ == "__main__":
    main()
