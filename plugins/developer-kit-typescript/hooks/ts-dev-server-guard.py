#!/usr/bin/env python3
"""TypeScript Dev Server Guard Hook.

Intercepts long-running dev server commands (npm run dev, nest start, etc.)
and automatically wraps them in a named tmux session so they run detached,
logs are preserved, and Claude Code is not blocked.

Hook event: PreToolUse (Bash)
Input:  JSON via stdin  { "tool_name": "Bash", "tool_input": { "command": "..." } }
Output:
  - Modified JSON (command wrapped in tmux)  → stdout + exit 0
  - Advisory message                          → stdout + exit 1  (tmux not found)
  - Pass-through                              → no output + exit 0  (not a dev server)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

# ─── Dev Server Command Detection ────────────────────────────────────────────

_DEV_SERVER_RE = re.compile(
    r"(?:^|&&|\||\s)"  # start, chain, or whitespace
    r"\s*(?:"
    r"npm\s+run\s+(?:dev|start|watch)"
    r"|npm\s+start"
    r"|pnpm\s+(?:run\s+)?(?:dev|start|watch)"
    r"|yarn\s+(?:run\s+)?(?:dev|start|watch)"
    r"|bun\s+run\s+(?:dev|start)"
    r"|nest\s+start(?:\s+--watch)?"
    r"|ts-node(?:-dev)?\s+src/main"
    r")\b",
    re.IGNORECASE,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _in_tmux() -> bool:
    """Return True if the current process is already running inside tmux."""
    return bool(os.environ.get("TMUX", ""))


def _tmux_available() -> bool:
    """Return True if tmux is installed on this system."""
    return shutil.which("tmux") is not None


def _sanitize_session_name(name: str) -> str:
    """Create a safe tmux session name from a directory name."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return sanitized[:32] or "dev"


def _escape_for_single_quotes(s: str) -> str:
    """Escape a string for safe use inside single-quoted shell arguments."""
    return s.replace("'", "'\\''")


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    cmd: str = data.get("tool_input", {}).get("command", "")
    if not cmd or not _DEV_SERVER_RE.search(cmd):
        sys.exit(0)

    # Already inside a tmux session — pass through unchanged
    if _in_tmux():
        sys.exit(0)

    # Tmux not installed — show advisory so Claude can decide
    if not _tmux_available():
        print(
            "⚠️  Dev server detected outside tmux. Logs may be lost when the session ends.\n"
            "   To preserve logs, install tmux (brew install tmux / apt install tmux)\n"
            "   then re-run the command. Proceeding without tmux."
        )
        sys.exit(1)

    # ── Transform: wrap command in a named tmux session ────────────────────
    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())
    session_name = _sanitize_session_name(Path(cwd).name)
    escaped_cmd = _escape_for_single_quotes(cmd)

    tmux_cmd = (
        f'SESSION="{session_name}"; '
        f"tmux kill-session -t \"$SESSION\" 2>/dev/null || true; "
        f"tmux new-session -d -s \"$SESSION\" '{escaped_cmd}' && "
        f"echo \"[Dev Server] Started in tmux session '{session_name}'. "
        f"View logs: tmux attach -t {session_name} | "
        f"tail: tmux capture-pane -t {session_name} -p -S -100\""
    )

    data["tool_input"]["command"] = tmux_cmd
    print(json.dumps(data))
    sys.exit(0)


if __name__ == "__main__":
    main()
