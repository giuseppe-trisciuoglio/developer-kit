#!/usr/bin/env python3
"""TypeScript Rules Verifier Hook.

Fires before Claude generates its next response. Reads the pending-verification
state written by ts-rules-tracker.py and injects an explicit verification
directive so Claude actively checks each written file against the matching
project rules — and fixes any violations before continuing.

Hook event: Prompt
Input:  JSON via stdin  { "prompt": "...", ... }
Output: Exit 0 = nothing pending | Exit 1 = inject verification directive to Claude

Zero external dependencies — pure Python 3 standard library only.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Must match ts-rules-tracker.py
_STATE_FILENAME_PREFIX = ".ts-rules-pending-"


# ─── State File ───────────────────────────────────────────────────────────────


def _session_key() -> str:
    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())
    return hashlib.sha256(cwd.encode()).hexdigest()[:12]


def _state_path() -> Path:
    cwd = Path(os.environ.get("CLAUDE_CWD", os.getcwd()))
    state_dir = cwd / ".claude"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{_STATE_FILENAME_PREFIX}{_session_key()}.json"


def _consume_state() -> list[dict]:
    """Read and delete the pending-verification state."""
    sp = _state_path()
    if not sp.exists():
        return []
    try:
        entries = json.loads(sp.read_text(encoding="utf-8"))
        sp.unlink(missing_ok=True)
        return entries
    except Exception:
        return []


# ─── Prompt Builder ───────────────────────────────────────────────────────────


def _build_directive(entries: list[dict]) -> str:
    """Build the verification directive injected into Claude's context."""
    lines: list[str] = [
        "## Project Rules Verification — Action Required",
        "",
        "You have written the following TypeScript file(s) this session.",
        "Before responding to the user, **verify each file against its matching",
        "project rules** (listed below). If any violation is found, **fix the file",
        "immediately** using the Write tool, then confirm what was corrected.",
        "",
    ]

    for entry in entries:
        written = entry.get("written_file", "")
        rules: list[dict] = entry.get("rules", [])
        lines.append(f"### File: `{Path(written).name}` (`{written}`)")
        lines.append("")
        for rule in rules:
            lines.append(f"#### Rule: {rule.get('title', rule.get('file', ''))}")
            lines.append(rule.get("body", ""))
            lines.append("")

    lines += [
        "---",
        "After verifying (and fixing if needed), continue with the user's request.",
    ]

    return "\n".join(lines)


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        json.load(sys.stdin)  # consume input
    except (json.JSONDecodeError, ValueError):
        pass

    entries = _consume_state()
    if not entries:
        sys.exit(0)

    directive = _build_directive(entries)
    print(directive)
    sys.exit(1)  # Exit 1: inject directive into Claude's next prompt turn


if __name__ == "__main__":
    main()
