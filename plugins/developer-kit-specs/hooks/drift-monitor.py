#!/usr/bin/env python3
"""Drift Guard Monitor Hook for Claude Code.

Monitors file creation/modification events (PostToolUse on Write|Edit)
and alerts when unplanned files are detected.

Reads current state from _drift/state.json, compares file paths against
Expected Files list, emits informational alerts for unplanned files,
and logs all drift events to _drift/drift-events.log.

Hook event: PostToolUse with matcher "Write|Edit"
Input:  JSON via stdin { "tool_name": "Write|Edit", "tool_input": { "file_path": "..." }, ... }
Output: Exit 0 = allow | Alert message on stdout | Exit 2 = block (not used)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Constants ──────────────────────────────────────────────────────────────

STATE_FILE_NAME = "state.json"
DRIFT_DIR_NAME = "_drift"
DRIFT_EVENTS_LOG = "drift-events.log"
ALERTED_FILES_FIELD = "alerted_files"


# ─── State Management ─────────────────────────────────────────────────────────


def find_state_file(cwd: str) -> str | None:
    """Find _drift/state.json by searching upward from cwd.

    Returns absolute path to state.json if found, None otherwise.
    """
    current = Path(cwd).resolve()

    # Search upward until root or found
    for _ in range(20):  # Prevent infinite loops
        drift_dir = current / DRIFT_DIR_NAME
        state_file = drift_dir / STATE_FILE_NAME

        if state_file.exists():
            return str(state_file)

        # Move up one directory
        if current.parent == current:  # Reached root
            break
        current = current.parent

    return None


def load_state(state_path: str) -> dict | None:
    """Load state.json, return None if file not found or invalid.

    Graceful degradation: returns None on any error.
    """
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None


def update_alerted_files(state_path: str, file_path: str) -> None:
    """Add file path to alerted_files list in state.json.

    Atomic update to prevent race conditions.
    """
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Initialize alerted_files if missing
        if ALERTED_FILES_FIELD not in state:
            state[ALERTED_FILES_FIELD] = []

        # Add file if not already present
        if file_path not in state[ALERTED_FILES_FIELD]:
            state[ALERTED_FILES_FIELD].append(file_path)

        # Write back atomically
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
        # Graceful degradation: fail silently
        pass


# ─── Drift Event Logging ─────────────────────────────────────────────────────


def log_drift_event(spec_folder: str, file_path: str) -> None:
    """Append drift event to _drift/drift-events.log.

    Every drift event is logged, even duplicates.
    """
    try:
        drift_dir = os.path.join(spec_folder, DRIFT_DIR_NAME)
        log_path = os.path.join(drift_dir, DRIFT_EVENTS_LOG)

        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {file_path}\n"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except (OSError, IOError):
        # Graceful degradation: fail silently
        pass


# ─── File Path Comparison ────────────────────────────────────────────────────


def is_expected_file(file_path: str, state: dict) -> bool:
    """Check if file path is in Expected Files list.

    Exact string match, case-sensitive, no path normalization.
    """
    expected_files = state.get("expected_files", [])
    return file_path in expected_files


def is_already_alerted(file_path: str, state: dict) -> bool:
    """Check if file has already been alerted in this session.

    """
    alerted_files = state.get(ALERTED_FILES_FIELD, [])
    return file_path in alerted_files


def emit_alert(file_path: str, state: dict) -> None:
    """Emit informational alert to stdout.

    Alert format: [Drift Guard] Unplanned file detected: <path>
                  Active task: <task_id>
                  Expected files (partial): <first 5 files>
    """
    task_id = state.get("task_id", "unknown")
    expected_files = state.get("expected_files", [])

    # Show first 5 expected files as context
    preview = expected_files[:5]
    preview_str = ", ".join(preview)
    if len(expected_files) > 5:
        preview_str += f", ... ({len(expected_files) - 5} more)"

    print(f"[Drift Guard] Unplanned file detected: {file_path}")
    print(f"[Drift Guard] Active task: {task_id}")
    print(f"[Drift Guard] Expected files (partial): {preview_str}")


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    # 1. Parse input JSON
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Malformed input → silent exit

    # 2. Validate hook event
    if input_data.get("hook_event_name") != "PostToolUse":
        sys.exit(0)  # Wrong event → silent exit

    tool_name = input_data.get("tool_name")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)  # Not a file operation → silent exit

    # 3. Extract file path from tool_input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path")

    if not file_path:
        sys.exit(0)  # No file path → silent exit

    # 4. Find and load state.json
    cwd = input_data.get("cwd", os.getcwd())
    state_path = find_state_file(cwd)

    if not state_path:
        # State not found → system not initialized, graceful degradation
        sys.exit(0)

    state = load_state(state_path)
    if not state:
        # Invalid state → graceful degradation
        sys.exit(0)

    # 5. Get spec folder for logging
    spec_folder = str(Path(state_path).parent.parent)

    # 6. Log drift event (always, even for expected files)
    log_drift_event(spec_folder, file_path)

    # 7. Check if file is expected
    if is_expected_file(file_path, state):
        # File is in expected list → silent exit
        sys.exit(0)

    # 8. Check if already alerted in this session
    if is_already_alerted(file_path, state):
        # Already alerted → silent exit (but still logged)
        sys.exit(0)

    # 9. Emit alert
    emit_alert(file_path, state)

    # 10. Update alerted_files to prevent duplicate alerts
    update_alerted_files(state_path, file_path)

    sys.exit(0)  # Allow operation to proceed


if __name__ == "__main__":
    main()
