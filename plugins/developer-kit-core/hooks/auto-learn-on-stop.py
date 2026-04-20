#!/usr/bin/env python3
"""Auto-Learn Stop Hook for Claude Code.

Triggers the learn skill to analyze the codebase and extract project rules
when a session is terminated, enabling autonomous learning from development
sessions.

Hook event: Stop
Input:  JSON via stdin (ignored — no tool-specific input for Stop events)
Output: JSON to stdout with decision (approve/block)

Flow:
  1. First stop attempt → block and instruct Claude to run the learn skill
  2. Second stop attempt → marker exists, approve stop and clean up

Zero external dependencies — pure Python 3 standard library only.
"""

import hashlib
import json
import os
import sys
import tempfile

# ─── Configuration ─────────────────────────────────────────────────────────────

MARKER_DIR = os.path.join(tempfile.gettempdir(), "claude-auto-learn")

LEARN_SYSTEM_MESSAGE = """\
Before ending this session, run the **learn** skill to extract project patterns \
discovered during this session.

Execute the full learn workflow:
1. Assess project context and existing rules
2. Delegate deep analysis to the learn-analyst sub-agent
3. Filter and rank findings (discard duplicates and low-impact patterns)
4. Present top findings to the user for approval
5. Save approved rules to .claude/rules/

If no new patterns are found or the user declines, you may proceed to stop.\
"""


# ─── Helpers ───────────────────────────────────────────────────────────────────


def _get_marker_path() -> str:
    """Generate a marker file path unique to the current working directory.

    Uses an MD5 hash of the CWD so that concurrent sessions in different
    projects do not interfere with each other.
    """
    cwd = os.getcwd()
    cwd_hash = hashlib.md5(cwd.encode()).hexdigest()[:12]
    return os.path.join(MARKER_DIR, f"learn-triggered-{cwd_hash}")


# ─── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    # Consume stdin to prevent broken-pipe errors (Stop hooks may send data).
    try:
        sys.stdin.read()
    except Exception:
        pass

    marker = _get_marker_path()

    if os.path.exists(marker):
        # Learn was already triggered in this stop cycle — allow stop.
        try:
            os.remove(marker)
        except OSError:
            pass
        json.dump({"decision": "approve"}, sys.stdout)
        return

    # First stop attempt — create marker and block to trigger learn.
    os.makedirs(MARKER_DIR, exist_ok=True)
    with open(marker, "w") as f:
        f.write("1")

    json.dump(
        {
            "decision": "block",
            "reason": "Auto-learn: extracting project patterns before session end",
            "systemMessage": LEARN_SYSTEM_MESSAGE,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
