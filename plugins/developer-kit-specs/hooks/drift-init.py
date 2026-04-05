#!/usr/bin/env python3
"""Drift Guard Initialization Hook for Claude Code.

Initializes drift tracking when /specs:task-implementation is invoked.
Extracts task ID, reads TASK-XXX.md, parses "Files to Create" section,
and saves initial state to _drift/state.json.

Hook event: UserPromptSubmit
Input:  JSON via stdin { "prompt": "...", "session_id": "...", "cwd": "..." }
Output: Exit 0 = proceed | Initialization Notice on stdout | Exit 2 = block

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ─── Constants ──────────────────────────────────────────────────────────────

TASK_IMPLEMENTATION_PATTERN = re.compile(r'--task="([^"]+)"|--task=\'([^\']+)\'|--task=([^\s]+)')
FILES_TO_CREATE_MARKER = "## Files to Create"
STATE_FILE_NAME = "state.json"
DRIFT_DIR_NAME = "_drift"


# ─── Prompt Parsing ───────────────────────────────────────────────────────────


def extract_task_id_from_prompt(prompt: str) -> str | None:
    """Extract task file path from prompt containing /specs:task-implementation."""
    match = TASK_IMPLEMENTATION_PATTERN.search(prompt)
    if match:
        # The regex has 3 capture groups: double-quoted, single-quoted, unquoted
        # Return the first non-None group
        return match.group(1) or match.group(2) or match.group(3)
    return None


def resolve_task_path(task_identifier: str, cwd: str) -> str | None:
    """Resolve task identifier to absolute file path.

    Supports:
    - Full paths: docs/specs/001-feature/tasks/TASK-001.md
    - Task IDs: TASK-001
    - Relative paths from cwd

    Security: Validates paths don't escape intended boundaries.
    """
    # Security: Reject path traversal attempts
    if ".." in task_identifier:
        return None

    # If it's already a full path or contains directory separators
    if "/" in task_identifier or "\\" in task_identifier:
        # Handle absolute paths: accept only if within cwd
        if os.path.isabs(task_identifier):
            # Security: Ensure absolute path is within cwd
            cwd_abs = os.path.abspath(cwd)
            if not task_identifier.startswith(cwd_abs):
                return None
            return task_identifier

        # Handle relative paths
        resolved = os.path.normpath(os.path.join(cwd, task_identifier))

        # Security: Ensure resolved path is still within cwd
        cwd_abs = os.path.abspath(cwd)
        resolved_abs = os.path.abspath(resolved)
        if not resolved_abs.startswith(cwd_abs):
            return None

        return resolved

    # Try TASK-XXX format with validation
    if task_identifier.startswith("TASK-"):
        # Validate format: TASK- followed by digits
        if not re.match(r"^TASK-\d+$", task_identifier):
            return None

        # Use glob for efficient pattern matching
        glob = __import__("glob")
        search_paths = [
            os.path.join(cwd, "docs/specs"),
            os.path.join(cwd, "docs"),
            cwd,
        ]

        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue

            # Use glob pattern for efficient search
            pattern = os.path.join(base_path, "**", f"{task_identifier}.md")
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

    return None


# ─── Task File Parsing ────────────────────────────────────────────────────────


def extract_files_to_create(task_file_path: str) -> list[str] | None:
    """Extract file paths from 'Files to Create' section in task markdown.

    Returns None if section not found or empty (graceful degradation).
    Returns list of file paths if section exists.
    """
    try:
        with open(task_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the Files to Create section
        marker_index = content.find(FILES_TO_CREATE_MARKER)
        if marker_index == -1:
            # Section not found → graceful degradation
            return None

        # Extract content after the marker (until next ## or EOF)
        section_start = marker_index + len(FILES_TO_CREATE_MARKER)
        next_section = content.find("\n## ", section_start)
        if next_section == -1:
            section_content = content[section_start:]
        else:
            section_content = content[section_start:next_section]

        # Parse bullet list items: "- `path` - description" or "- path - description"
        files = []
        for line in section_content.split("\n"):
            line = line.strip()
            if not line.startswith("- "):
                continue

            # Extract path from various Markdown formats:
            # - `path/to/file.ext` - description
            # - path/to/file.ext - description
            # - `path/to/file.ext`
            # - path/to/file.ext

            # Remove the leading "- "
            line = line[2:].strip()

            # Try to extract backtick-enclosed path first
            backtick_match = re.match(r"^`([^`]+)`", line)
            if backtick_match:
                file_path = backtick_match.group(1)
            else:
                # No backticks, extract until " - " (description separator)
                # This handles paths with spaces like "plugins/developer-kit/specs"
                match = re.match(r"^([^\s]+(?:\s+[^\s]+)*?)\s+-", line)
                if not match:
                    # Try to extract entire line if no separator
                    match = re.match(r"^([^\s]+(?:\s+[^\s]+)*)$", line)
                if match:
                    file_path = match.group(1).strip()
                else:
                    continue

            # Security: Basic path validation
            # Reject obviously malicious paths
            if file_path.startswith(("/", "\\", "../")):
                continue  # Skip absolute/relative paths that escape

            # Reject paths with suspicious characters
            if any(char in file_path for char in ["\x00", "\n", "\r"]):
                continue

            files.append(file_path)

        return files if files else None  # Empty list → None for graceful degradation

    except FileNotFoundError:
        # Expected: task file not found → graceful degradation
        return None
    except (PermissionError, UnicodeDecodeError) as e:
        # Unexpected error: log to stderr for debugging (non-blocking)
        sys.stderr.write(f"[Drift Guard] Warning: Cannot read task file: {e}\n")
        return None


# ─── State Management ─────────────────────────────────────────────────────────


def get_spec_folder_from_task_path(task_file_path: str) -> str:
    """Extract spec folder path from task file path.

    Example: docs/specs/001-feature/tasks/TASK-001.md → docs/specs/001-feature
    """
    path = Path(task_file_path)

    # Navigate up from tasks/ directory
    if path.parent.name == "tasks":
        return str(path.parent.parent)
    else:
        # Task file not in tasks/ subdirectory, use its parent as spec folder
        return str(path.parent)


def initialize_drift_state(
    spec_folder: str, task_id: str, task_file: str, expected_files: list[str]
) -> str:
    """Create _drift directory and save initial state.

    Returns absolute path to created state.json.
    """
    drift_dir = os.path.join(spec_folder, DRIFT_DIR_NAME)

    # Create or reset _drift directory
    # Use exception handling to avoid TOCTOU race condition
    shutil = __import__("shutil")
    try:
        shutil.rmtree(drift_dir)
    except FileNotFoundError:
        pass  # Directory doesn't exist, that's fine
    os.makedirs(drift_dir, exist_ok=True)

    # Create state.json
    state = {
        "task_id": task_id,
        "task_file": task_file,
        "expected_files": expected_files,
        "initialized_at": datetime.now().isoformat(),
    }

    state_file_path = os.path.join(drift_dir, STATE_FILE_NAME)

    with open(state_file_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return state_file_path


# ─── Entry Point ───────────────────────────────────────────────────────────────


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Non-blocking: malformed input

    if input_data.get("hook_event_name") != "UserPromptSubmit":
        sys.exit(0)  # Wrong event, not for us

    prompt = input_data.get("prompt", "")
    if not prompt:
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())

    # 1. Check if prompt contains /specs:task-implementation
    task_identifier = extract_task_id_from_prompt(prompt)
    if not task_identifier:
        # Not a task implementation command → silent exit
        sys.exit(0)

    # 2. Resolve task file path
    task_file_path = resolve_task_path(task_identifier, cwd)
    if not task_file_path:
        # Task file not found → emit Initialization Notice and exit
        message = f"[Drift Guard] Task file not found: {task_identifier}"
        output = {"type": "notification", "message": message}
        print(json.dumps(output))
        sys.exit(0)

    # 3. Extract "Files to Create" section
    expected_files = extract_files_to_create(task_file_path)
    if expected_files is None:
        # Section not found or empty → graceful degradation, silent exit
        sys.exit(0)

    # 4. Initialize drift state
    spec_folder = get_spec_folder_from_task_path(task_file_path)

    # Extract task ID from file path for state
    task_id = Path(task_file_path).stem  # TASK-001 from TASK-001.md

    try:
        state_path = initialize_drift_state(
            spec_folder=spec_folder,
            task_id=task_id,
            task_file=task_file_path,
            expected_files=expected_files,
        )
        # Silent success, state initialized
    except (OSError, IOError) as e:
        # Graceful degradation on filesystem errors
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
