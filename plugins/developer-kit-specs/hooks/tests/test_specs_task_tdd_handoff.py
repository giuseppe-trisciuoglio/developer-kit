#!/usr/bin/env python3
"""Tests for specs-task-tdd-handoff.py."""

import importlib.util
import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path
from unittest import mock

hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
handoff_path = os.path.join(hooks_dir, "specs-task-tdd-handoff.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_handoff", handoff_path)
task_tdd_handoff = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_handoff"] = task_tdd_handoff
spec.loader.exec_module(task_tdd_handoff)


def write_task_file(directory: str, content: str) -> str:
    path = Path(directory) / "tasks" / "TASK-013.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return str(path)


def build_task(
    directory: str,
    *,
    test_references: str | None = None,
    red_phase: str | None = None,
) -> str:
    extra_frontmatter = []
    if test_references is not None:
        extra_frontmatter.append(f"testReferences: {test_references}")
    if red_phase is not None:
        extra_frontmatter.append(f"redPhase: {red_phase}")

    return write_task_file(
        directory,
        f"""
        ---
        id: TASK-013
        title: "Implementation Handoff Preparation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: python
        dependencies: [TASK-011]
        status: pending
        {'\n'.join(extra_frontmatter)}
        ---

        # TASK-013: Implementation Handoff Preparation

        **Functional Description**: Prepare documentation and context for smooth transition to task-implementation phase.

        ## Acceptance Criteria

        - [ ] Summary of generated tests is created and displayed
        - [ ] Next steps for implementation are clearly documented

        ## Technical Context (from Codebase Analysis)

        - Existing patterns: command completion summaries
        - Shared components: summary generator and handoff creator
        """,
    )


def test_prepare_handoff_creates_markdown_summary_with_next_steps():
    test_references = json.dumps(
        [
            {
                "path": "tests/test_task_file_updates.py",
                "test_type": "both",
                "language": "python",
                "generated_at": "2026-04-05",
                "scenario_count": 2,
            }
        ],
        separators=(",", ": "),
    )
    red_phase = json.dumps(
        {
            "status": "red-confirmed",
            "verified": True,
            "verified_at": "2026-04-05",
            "framework": "pytest",
            "test_file": "tests/test_task_file_updates.py",
            "summary": "RED phase confirmed: generated tests failed as expected.",
            "command": ["pytest", "tests/test_task_file_updates.py", "-q"],
            "warnings": [],
        },
        separators=(",", ": "),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(
            temp_dir,
            test_references=test_references,
            red_phase=red_phase,
        )

        result = task_tdd_handoff.prepare_handoff(task_file, project_root=temp_dir)
        handoff_doc = Path(result.handoff_path).read_text(encoding="utf-8")

    assert result.generated_test_count == 1
    assert result.red_phase_confirmed is True
    assert result.handoff_path.endswith("_drift/tdd-handoff-task-013.md")
    assert "RED phase confirmed via `pytest`." in handoff_doc
    assert "`tests/test_task_file_updates.py` (both, python, scenarios: 2)" in handoff_doc
    assert "/specs:task-implementation --lang=python" in handoff_doc
    assert "## Context To Preserve" in handoff_doc


def test_prepare_handoff_warns_when_no_test_references_exist():
    red_phase = json.dumps(
        {
            "status": "unexpected-pass",
            "verified": False,
            "verified_at": "2026-04-05",
            "framework": "pytest",
            "test_file": "tests/test_task_file_updates.py",
            "summary": "Generated tests passed unexpectedly during RED verification.",
            "command": ["pytest", "tests/test_task_file_updates.py", "-q"],
            "warnings": ["Generated tests passed unexpectedly."],
        },
        separators=(",", ": "),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, red_phase=red_phase)

        result = task_tdd_handoff.prepare_handoff(task_file, project_root=temp_dir)
        handoff_doc = Path(result.handoff_path).read_text(encoding="utf-8")

    assert result.generated_test_count == 0
    assert result.red_phase_confirmed is False
    assert "No generated tests were recorded in task metadata." in handoff_doc
    assert "RED phase is not confirmed yet." in handoff_doc
    assert any("No generated test references" in warning for warning in result.warnings)


def test_prepare_handoff_raises_e4_when_write_fails():
    test_references = json.dumps([], separators=(",", ": "))
    red_phase = json.dumps({}, separators=(",", ": "))

    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(
            temp_dir,
            test_references=test_references,
            red_phase=red_phase,
        )

        with mock.patch.object(Path, "write_text", side_effect=PermissionError("no write")):
            try:
                task_tdd_handoff.prepare_handoff(task_file, project_root=temp_dir)
                assert False, "Expected TddHandoffError"
            except task_tdd_handoff.TddHandoffError as exc:
                assert exc.code == "E4"
                assert "handoff file" in str(exc)
