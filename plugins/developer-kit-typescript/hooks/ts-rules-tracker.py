#!/usr/bin/env python3
"""TypeScript Rules Tracker Hook.

Fires after Claude writes or edits a TypeScript file. Finds .claude/rules/
entries whose 'paths:' frontmatter matches the modified file and persists them
to a per-session state file so the Prompt hook can pick them up.

Hook event: PostToolUse (Write | Edit | MultiEdit)
Input:  JSON via stdin with tool_name and tool_input
Output: always Exit 0 — side effect only (writes state file)

Zero external dependencies — pure Python 3 standard library only.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

# State directory lives under $CLAUDE_CWD/.claude/ (project-local, not world-readable)
_STATE_FILENAME_PREFIX = ".ts-rules-pending-"

TS_EXTENSIONS: tuple[str, ...] = (".ts", ".tsx", ".js", ".jsx")


# ─── Minimal YAML Frontmatter Parser ─────────────────────────────────────────


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Handles only the simple subset used in
    .claude/rules files: top-level key:value pairs and list items (- value)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end: Optional[int] = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}, text

    fm: dict = {}
    current_key: Optional[str] = None
    for line in lines[1:end]:
        stripped = line.strip()
        if stripped.startswith("- "):
            val = stripped[2:].strip().strip("\"'")
            if current_key is not None and isinstance(fm.get(current_key), list):
                fm[current_key].append(val)
        elif ":" in stripped:
            key, _, val = stripped.partition(":")
            key, val = key.strip(), val.strip().strip("\"'")
            if val:
                fm[key] = val
                current_key = None
            else:
                fm[key] = []
                current_key = key

    return fm, "\n".join(lines[end + 1 :]).strip()


# ─── Path Matching ────────────────────────────────────────────────────────────


def _matches_any(file_path: str, patterns: list[str]) -> bool:
    p = Path(file_path)
    rel = Path(p.as_posix().lstrip("/"))
    return any(p.match(pat) or rel.match(pat) for pat in patterns)


# ─── State File ───────────────────────────────────────────────────────────────


def _session_key() -> str:
    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())
    return hashlib.sha256(cwd.encode()).hexdigest()[:12]


def _state_path() -> Path:
    cwd = Path(os.environ.get("CLAUDE_CWD", os.getcwd()))
    state_dir = cwd / ".claude"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{_STATE_FILENAME_PREFIX}{_session_key()}.json"


def _load_state() -> list[dict]:
    sp = _state_path()
    if sp.exists():
        try:
            return json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_state(entries: list[dict]) -> None:
    try:
        sp = _state_path()
        sp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        os.chmod(sp, 0o600)
    except OSError:
        pass


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path: str = data.get("tool_input", {}).get("file_path", "")
    if not file_path or not any(file_path.endswith(ext) for ext in TS_EXTENSIONS):
        sys.exit(0)

    cwd = Path(os.environ.get("CLAUDE_CWD", os.getcwd()))
    rules_dir = cwd / ".claude" / "rules"
    if not rules_dir.is_dir():
        sys.exit(0)

    matched: list[dict] = []
    for rule_file in sorted(rules_dir.glob("*.md")):
        try:
            raw = rule_file.read_text(encoding="utf-8")
        except OSError:
            continue

        fm, body = _parse_frontmatter(raw)
        paths = fm.get("paths", [])
        if not paths:
            continue
        if isinstance(paths, str):
            paths = [paths]
        if not _matches_any(file_path, paths):
            continue

        # Extract H1 title from body
        title = rule_file.stem.replace("-", " ").title()
        for line in body.splitlines():
            heading = line.lstrip("#").strip()
            if heading:
                title = heading
                break

        matched.append(
            {
                "file": rule_file.name,
                "title": title,
                "body": body[:2000],
            }
        )

    if not matched:
        sys.exit(0)

    # Append to state (avoid duplicates for the same file)
    state = _load_state()
    existing_files = {e["written_file"] for e in state}
    if file_path not in existing_files:
        state.append({"written_file": file_path, "rules": matched})
        _save_state(state)

    sys.exit(0)  # Always non-blocking — Prompt hook does the actual verification


if __name__ == "__main__":
    main()
