#!/usr/bin/env python3
"""Tests for task_lifecycle.py — covers status detection, validation, and lifecycle transitions."""

import os
import sys
import tempfile
import pytest

# Import the module under test
hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, hooks_dir)
from task_lifecycle import (
    TaskStatus,
    FIELD_SCHEMA,
    detect_status_from_body,
    _all_dod_complete,
    read_task_file,
    write_task_file,
    update_status,
    validate_task,
    _is_task_document,
    _filepath_from_hook_input,
    main,
)


# --- Helpers ---

def _make_task(frontmatter: dict, body: str) -> str:
    """Write a temporary task file and return its path."""
    import yaml
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write("---\n")
    tmp.write(yaml.dump(frontmatter, sort_keys=False))
    tmp.write("---\n")
    tmp.write(body)
    tmp.close()
    return tmp.name


def _cleanup(path: str):
    try:
        os.unlink(path)
    except OSError:
        pass


# --- Hook payload resolution (PostToolUse stdin JSON) ---

class TestHookPayloadResolution:
    """task_lifecycle.py must resolve the file from the hook payload on stdin."""

    def test_is_task_document_accepts_task_file(self):
        assert _is_task_document("/some/dir/TASK-042.md") is True

    def test_is_task_document_rejects_other_files(self):
        assert _is_task_document("/some/dir/README.md") is False
        assert _is_task_document("/some/dir/TASK-042.txt") is False
        assert _is_task_document("/some/dir/task-042.md") is False

    def test_filepath_from_hook_input_extracts_path(self, monkeypatch):
        import io
        import json
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/abs/path/TASK-007.md"},
        }
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
        assert _filepath_from_hook_input() == "/abs/path/TASK-007.md"

    def test_filepath_from_hook_input_invalid_json(self, monkeypatch):
        import io
        monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
        assert _filepath_from_hook_input() is None

    def test_filepath_from_hook_input_missing_path(self, monkeypatch):
        import io
        import json
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"tool_name": "Write"})))
        assert _filepath_from_hook_input() is None

    def test_main_silent_for_non_task_file_via_payload(self, monkeypatch, capsys):
        import io
        import json
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "/tmp/notes.md"},
        }
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
        monkeypatch.setattr("sys.argv", ["task_lifecycle.py", "auto-status"])
        main()  # must not raise and must not print anything
        assert capsys.readouterr().out == ""

    def test_main_runs_auto_status_for_task_file_via_payload(self, monkeypatch, tmp_path, capsys):
        import io
        import json
        fm = {
            "id": "TASK-009",
            "title": "Hook payload task",
            "spec": "spec-001",
            "status": "pending",
        }
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [x] DoD1\n"
        )
        task_file = tmp_path / "TASK-009.md"
        task_file.write_text(
            "---\n" + __import__("yaml").dump(fm, sort_keys=False) + "---\n" + body
        )
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(task_file)},
        }
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
        monkeypatch.setattr("sys.argv", ["task_lifecycle.py", "auto-status"])
        main()
        updated_fm, _, _ = read_task_file(task_file)
        assert updated_fm["status"] == "implemented"
        assert "Status updated" in capsys.readouterr().out

    def test_main_validate_explicit_file_still_works(self, monkeypatch, tmp_path, capsys):
        fm = {
            "id": "TASK-010",
            "title": "Explicit file task",
            "spec": "spec-001",
            "status": "pending",
        }
        body = (
            "## Acceptance Criteria\n"
            "- [ ] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [ ] DoD1\n"
        )
        task_file = tmp_path / "TASK-010.md"
        task_file.write_text(
            "---\n" + __import__("yaml").dump(fm, sort_keys=False) + "---\n" + body
        )
        monkeypatch.setattr("sys.argv", ["task_lifecycle.py", "validate", str(task_file)])
        main()
        assert "Validation passed" in capsys.readouterr().out


# --- P2: superseded is a valid status ---

class TestSupersededStatus:
    """superseded must be accepted by the schema and preserved by update_status."""

    def test_superseded_in_task_status_class(self):
        assert TaskStatus.SUPERSEDED == "superseded"

    def test_superseded_in_field_schema_values(self):
        assert "superseded" in FIELD_SCHEMA["status"]["values"]

    def test_validate_accepts_superseded(self):
        fm = {
            "id": "TASK-001",
            "title": "Test task",
            "spec": "spec-001",
            "status": "superseded",
        }
        body = "## Acceptance Criteria\n- [ ] AC1\n\n## Definition of Done\n- [ ] DoD1\n"
        path = _make_task(fm, body)
        try:
            assert validate_task(path) is True
        finally:
            _cleanup(path)

    def test_auto_status_preserves_superseded(self):
        fm = {
            "id": "TASK-001",
            "title": "Test task",
            "spec": "spec-001",
            "status": "superseded",
        }
        body = "## Acceptance Criteria\n- [x] AC1\n\n## Definition of Done\n- [x] DoD1\n"
        path = _make_task(fm, body)
        try:
            update_status(path)
            updated_fm, _, _ = read_task_file(__import__("pathlib").Path(path))
            assert updated_fm["status"] == "superseded"
        finally:
            _cleanup(path)


# --- P3: implemented -> reviewed -> completed transitions ---

class TestStatusPromotion:
    """detect_status_from_body must promote implemented -> reviewed when DoD is complete."""

    def test_implemented_promoted_to_reviewed_when_dod_complete(self):
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [x] DoD1\n"
        )
        result = detect_status_from_body(body, old_status="implemented")
        assert result == TaskStatus.REVIEWED

    def test_implemented_stays_when_dod_incomplete(self):
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [ ] DoD1\n"
        )
        result = detect_status_from_body(body, old_status="implemented")
        assert result == TaskStatus.IMPLEMENTED

    def test_reviewed_preserved(self):
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [x] DoD1\n"
        )
        result = detect_status_from_body(body, old_status="reviewed")
        assert result == TaskStatus.REVIEWED

    def test_all_checked_new_task_gets_implemented(self):
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [x] DoD1\n"
        )
        result = detect_status_from_body(body, old_status="pending")
        assert result == TaskStatus.IMPLEMENTED

    def test_partial_gets_in_progress(self):
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "- [ ] AC2\n"
        )
        result = detect_status_from_body(body, old_status="pending")
        assert result == TaskStatus.IN_PROGRESS

    def test_no_checkboxes_gets_pending(self):
        result = detect_status_from_body("No checkboxes here", old_status="in_progress")
        assert result == TaskStatus.PENDING


class TestAllDodComplete:
    """Unit tests for _all_dod_complete helper."""

    def test_all_dod_checked(self):
        body = "## Definition of Done\n- [x] DoD1\n- [x] DoD2\n"
        assert _all_dod_complete(body) is True

    def test_some_dod_unchecked(self):
        body = "## Definition of Done\n- [x] DoD1\n- [ ] DoD2\n"
        assert _all_dod_complete(body) is False

    def test_no_dod_section(self):
        body = "## Acceptance Criteria\n- [x] AC1\n"
        assert _all_dod_complete(body) is False

    def test_dod_empty(self):
        body = "## Definition of Done\n"
        assert _all_dod_complete(body) is True


class TestUpdateStatusDates:
    """Auto-set date fields on promotion."""

    def test_reviewed_date_set_on_promotion(self):
        fm = {
            "id": "TASK-001",
            "title": "Test task",
            "spec": "spec-001",
            "status": "implemented",
        }
        body = (
            "## Acceptance Criteria\n"
            "- [x] AC1\n"
            "\n"
            "## Definition of Done\n"
            "- [x] DoD1\n"
        )
        path = _make_task(fm, body)
        try:
            update_status(path)
            updated_fm, _, _ = read_task_file(__import__("pathlib").Path(path))
            assert updated_fm["status"] == "reviewed"
            assert updated_fm.get("reviewed_date") is not None
        finally:
            _cleanup(path)


# --- P1-related: ensure test_session_tracker is gone ---

class TestOrphanedTestRemoved:
    """Verify the orphaned test file for session-tracker.py has been removed."""

    def test_session_tracker_test_not_present(self):
        scripts_test_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scripts", "tests",
        )
        test_file = os.path.join(scripts_test_dir, "test_session_tracker.py")
        assert not os.path.exists(test_file), (
            "test_session_tracker.py still exists but session-tracker.py was deleted"
        )
