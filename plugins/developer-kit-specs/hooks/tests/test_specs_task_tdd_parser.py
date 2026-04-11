#!/usr/bin/env python3
"""Tests for specs-task-tdd-parser.py."""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import importlib.util


hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parser_path = os.path.join(hooks_dir, "specs-task-tdd-parser.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_parser", parser_path)
task_tdd_parser = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_parser"] = task_tdd_parser
spec.loader.exec_module(task_tdd_parser)


def write_task_file(content: str) -> str:
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md")
    handle.write(textwrap.dedent(content).strip() + "\n")
    handle.flush()
    handle.close()
    return handle.name


def test_parse_valid_task_file_extracts_frontmatter_and_test_instructions():
    task_file = write_task_file(
        """
        ---
        id: TASK-002
        title: "Task File Parsing and Validation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: general
        dependencies: [TASK-001]
        status: pending
        ---

        # TASK-002: Task File Parsing and Validation

        ## Acceptance Criteria
        - [ ] Task file is parsed

        ## Test Instructions
        Verify parser behavior.

        ## Definition of Done (DoD)
        - [ ] Done
        """
    )

    try:
        result = task_tdd_parser.parse_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert result.metadata["id"] == "TASK-002"
    assert result.metadata["title"] == "Task File Parsing and Validation"
    assert result.metadata["lang"] == "general"
    assert result.metadata["dependencies"] == ["TASK-001"]
    assert result.metadata["status"] == "pending"
    assert result.title_heading == "TASK-002: Task File Parsing and Validation"
    assert result.test_instructions == "Verify parser behavior."
    assert result.warnings == []


def test_validate_metadata_rejects_invalid_task_identifier():
    metadata = {
        "id": "TASK-2",
        "title": "Invalid task",
        "spec": "docs/specs/example.md",
        "lang": "general",
        "dependencies": [],
        "status": "pending",
    }

    try:
        task_tdd_parser.validate_metadata(metadata)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "TASK-XXX" in str(exc)


def test_validate_metadata_accepts_supported_status_values():
    metadata = {
        "id": "TASK-002",
        "title": "Valid task",
        "spec": "docs/specs/example.md",
        "lang": "general",
        "dependencies": ["TASK-001"],
        "status": "red-phase",
    }

    task_tdd_parser.validate_metadata(metadata)


def test_validate_metadata_rejects_missing_status():
    metadata = {
        "id": "TASK-002",
        "title": "Invalid task",
        "spec": "docs/specs/example.md",
        "lang": "general",
        "dependencies": [],
        "status": None,
    }

    try:
        task_tdd_parser.validate_metadata(metadata)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "status" in str(exc)


def test_validate_metadata_rejects_unsupported_status():
    metadata = {
        "id": "TASK-002",
        "title": "Invalid task",
        "spec": "docs/specs/example.md",
        "lang": "general",
        "dependencies": [],
        "status": "in-progress",
    }

    try:
        task_tdd_parser.validate_metadata(metadata)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "status" in str(exc)


def test_parse_task_file_rejects_missing_frontmatter():
    task_file = write_task_file(
        """
        # TASK-002: Task File Parsing and Validation

        ## Test Instructions
        Verify parser behavior.
        """
    )

    try:
        task_tdd_parser.parse_task_file(task_file)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "frontmatter" in str(exc)
    finally:
        os.unlink(task_file)


def test_parse_task_file_rejects_missing_required_frontmatter_fields():
    task_file = write_task_file(
        """
        ---
        id: TASK-002
        lang: general
        dependencies: []
        ---

        # TASK-002: Task File Parsing and Validation

        ## Test Instructions
        Verify parser behavior.
        """
    )

    try:
        task_tdd_parser.parse_task_file(task_file)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "title, spec" in str(exc)
    finally:
        os.unlink(task_file)


def test_parse_task_file_rejects_malformed_frontmatter_line():
    task_file = write_task_file(
        """
        ---
        id TASK-002
        title: "Task File Parsing and Validation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: general
        dependencies: []
        ---

        # TASK-002: Task File Parsing and Validation

        ## Test Instructions
        Verify parser behavior.
        """
    )

    try:
        task_tdd_parser.parse_task_file(task_file)
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E3"
        assert "Invalid frontmatter line" in str(exc)
    finally:
        os.unlink(task_file)


def test_parse_task_file_flags_missing_test_instructions_for_a3_flow():
    task_file = write_task_file(
        """
        ---
        id: TASK-002
        title: "Task File Parsing and Validation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: general
        dependencies: [TASK-001]
        status: pending
        ---

        # TASK-002: Task File Parsing and Validation

        ## Acceptance Criteria
        - [ ] Task file is parsed
        """
    )

    try:
        result = task_tdd_parser.parse_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert result.test_instructions is None
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "A3"
    assert "Test Instructions" in result.warnings[0].message


def test_parse_task_file_flags_empty_test_instructions_for_a3_flow():
    task_file = write_task_file(
        """
        ---
        id: TASK-002
        title: "Task File Parsing and Validation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: general
        dependencies: [TASK-001]
        status: pending
        ---

        # TASK-002: Task File Parsing and Validation

        ## Test Instructions

        ## Definition of Done (DoD)
        - [ ] Done
        """
    )

    try:
        result = task_tdd_parser.parse_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert result.test_instructions is None
    assert result.warnings[0].code == "A3"
    assert "empty Test Instructions section" in result.warnings[0].message


def test_parse_task_file_reports_missing_file_as_e1():
    try:
        task_tdd_parser.parse_task_file("/nonexistent/TASK-002.md")
        assert False, "Expected TaskFileError"
    except task_tdd_parser.TaskFileError as exc:
        assert exc.code == "E1"
        assert "spec-to-tasks" in str(exc)


def test_cli_outputs_json_for_valid_task_file():
    task_file = write_task_file(
        """
        ---
        id: TASK-002
        title: "Task File Parsing and Validation"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: general
        dependencies: [TASK-001]
        status: pending
        ---

        # TASK-002: Task File Parsing and Validation

        ## Test Instructions
        Verify parser behavior.
        """
    )

    try:
        completed = subprocess.run(
            [sys.executable, parser_path, "--task", task_file],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(task_file)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["metadata"]["id"] == "TASK-002"
    assert payload["test_instructions"] == "Verify parser behavior."


def test_cli_outputs_error_json_for_invalid_task_file():
    completed = subprocess.run(
        [sys.executable, parser_path, "--task", "/nonexistent/TASK-002.md"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["error"]["code"] == "E1"
