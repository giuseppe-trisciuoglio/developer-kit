#!/usr/bin/env python3
"""Drift Guard Fidelity Report Generator for Claude Code.

Generates fidelity report at TaskCompleted event.
Reads _drift/state.json (Expected Files) and _drift/drift-events.log (actual files),
calculates matched/missing/extra, and generates _drift/fidelity-report.md.

Hook event: TaskCompleted
Input:  JSON via stdin { "hook_event_name": "TaskCompleted", "task_id": "...", ... }
Output: Exit 0 = proceed | Report generated | Exit 2 = block (not used)

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
FIDELITY_REPORT_NAME = "fidelity-report.md"


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


def load_drift_events(spec_folder: str) -> list[str]:
    """Load drift events from _drift/drift-events.log.

    Returns list of unique file paths that were created/modified.
    Returns empty list if log file doesn't exist (graceful degradation).
    """
    try:
        drift_dir = os.path.join(spec_folder, DRIFT_DIR_NAME)
        log_path = os.path.join(drift_dir, DRIFT_EVENTS_LOG)

        if not os.path.exists(log_path):
            # Log file doesn't exist → no drift events
            return []

        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse log entries: "2026-04-03T12:34:56.789 | file/path"
        files = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract file path after " | "
            if " | " in line:
                _, file_path = line.split(" | ", 1)
                files.append(file_path)

        # Return unique files (deduplicate)
        return list(set(files))

    except (OSError, IOError):
        # Graceful degradation: return empty list
        return []


# ─── Fidelity Calculation ────────────────────────────────────────────────────


def calculate_fidelity(
    expected_files: list[str], actual_files: list[str]
) -> dict:
    """Calculate fidelity metrics.

    Returns dict with:
    - total_expected: int
    - matched: list[str] (files in both expected and actual)
    - missing: list[str] (files in expected but not actual)
    - extra: list[str] (files in actual but not expected)
    - matched_count: int
    - missing_count: int
    - extra_count: int
    """
    expected_set = set(expected_files)
    actual_set = set(actual_files)

    matched = expected_set & actual_set
    missing = expected_set - actual_set
    extra = actual_set - expected_set

    return {
        "total_expected": len(expected_files),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "extra": sorted(list(extra)),
        "matched_count": len(matched),
        "missing_count": len(missing),
        "extra_count": len(extra),
    }


def get_fidelity_summary(metrics: dict) -> str:
    """Generate human-readable fidelity summary statement."""
    total = metrics["total_expected"]
    matched = metrics["matched_count"]
    extra = metrics["extra_count"]

    if total == 0:
        if extra == 0:
            return "✓ Full fidelity — No expected files and no drift events"
        else:
            return f"⚠ Partial fidelity — {extra} unplanned file(s) created"

    # Calculate percentage of expected files that were matched
    percentage = (matched / total) * 100 if total > 0 else 0

    if matched == total and extra == 0:
        return "✓ Full fidelity — All expected files produced, no drift"
    elif matched == total and extra > 0:
        return f"✓ Full fidelity with drift — All {total} expected files produced, {extra} unplanned file(s)"
    elif percentage >= 80:
        return f"⚠ Partial fidelity — {matched}/{total} expected files produced ({percentage:.0f}%), {extra} unplanned file(s)"
    elif percentage >= 50:
        return f"⚠ Low fidelity — {matched}/{total} expected files produced ({percentage:.0f}%), {extra} unplanned file(s)"
    else:
        return f"❌ Very low fidelity — Only {matched}/{total} expected files produced ({percentage:.0f}%), {extra} unplanned file(s)"


# ─── Report Generation ────────────────────────────────────────────────────────


def generate_fidelity_report(
    spec_folder: str, task_id: str, state: dict, metrics: dict
) -> None:
    """Generate _drift/fidelity-report.md with all required elements.

    Report includes:
    1. Total Expected Files count
    2. Matched files count
    3. Missing files list
    4. Extra files list
    5. Fidelity summary statement
    """
    drift_dir = os.path.join(spec_folder, DRIFT_DIR_NAME)
    report_path = os.path.join(drift_dir, FIDELITY_REPORT_NAME)

    # Build report content
    lines = [
        f"# Fidelity Report — {task_id}",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Task**: {task_id}",
        "",
        "## Summary",
        "",
        get_fidelity_summary(metrics),
        "",
        "## Metrics",
        "",
        f"- **Total Expected Files**: {metrics['total_expected']}",
        f"- **Matched Files**: {metrics['matched_count']}",
        f"- **Missing Files**: {metrics['missing_count']}",
        f"- **Extra Files**: {metrics['extra_count']}",
        "",
    ]

    # Add Missing Files section if any
    if metrics["missing"]:
        lines.extend([
            "## Missing Files (Expected but Not Produced)",
            "",
        ])
        for file_path in metrics["missing"]:
            lines.append(f"- `{file_path}`")
        lines.append("")

    # Add Extra Files section if any
    if metrics["extra"]:
        lines.extend([
            "## Extra Files (Produced but Not Expected)",
            "",
        ])
        for file_path in metrics["extra"]:
            lines.append(f"- `{file_path}`")
        lines.append("")

    # Add Matched Files section if any
    if metrics["matched"]:
        lines.extend([
            "## Matched Files (Expected and Produced)",
            "",
        ])
        for file_path in metrics["matched"]:
            lines.append(f"- `{file_path}`")
        lines.append("")

    # Write report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ─── Entry Point ───────────────────────────────────────────────────────────────


def main() -> None:
    # 1. Parse input JSON
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Malformed input → silent exit

    # 2. Validate hook event
    if input_data.get("hook_event_name") != "TaskCompleted":
        sys.exit(0)  # Wrong event → silent exit

    # 3. Get current working directory
    cwd = input_data.get("cwd", os.getcwd())

    # 4. Find and load state.json
    state_path = find_state_file(cwd)

    if not state_path:
        # State not found → graceful degradation, silent exit
        sys.exit(0)

    state = load_state(state_path)
    if not state:
        # Invalid state → graceful degradation, silent exit
        sys.exit(0)

    # 5. Get spec folder and task ID
    spec_folder = str(Path(state_path).parent.parent)
    task_id = state.get("task_id", "unknown")

    # 6. Load drift events (actual files produced)
    actual_files = load_drift_events(spec_folder)

    # 7. Get expected files from state
    expected_files = state.get("expected_files", [])

    # 8. Calculate fidelity metrics
    metrics = calculate_fidelity(expected_files, actual_files)

    # 9. Generate fidelity report
    try:
        generate_fidelity_report(spec_folder, task_id, state, metrics)
    except (OSError, IOError):
        # Graceful degradation: fail silently if report cannot be written
        sys.exit(0)

    # 10. Silent success (report generated)
    sys.exit(0)


if __name__ == "__main__":
    main()
