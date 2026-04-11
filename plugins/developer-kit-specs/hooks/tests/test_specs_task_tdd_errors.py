#!/usr/bin/env python3
"""Tests for specs-task-tdd-errors.py."""

import importlib.util
import os
import sys
import tempfile
import textwrap
import shutil


hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
module_path = os.path.join(hooks_dir, "specs-task-tdd-errors.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_errors", module_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_errors"] = mod
spec.loader.exec_module(mod)


def test_ensure_task_file_reports_e1_for_missing_file():
    try:
        mod.ensure_task_file_exists("/nonexistent/TASK-012.md")
        assert False, "Expected SpecsTddError"
    except mod.SpecsTddError as exc:
        assert exc.code == "E1"
        assert "spec-to-tasks" in str(exc) or "Task file not found" in str(exc)


def test_detect_existing_test_file_triggers_choices(tmp_path):
    p = tmp_path / "test_example.py"
    p.write_text("# existing test")
    info = mod.detect_existing_test_file(str(p))
    assert info.exists is True
    assert "overwrite" in info.suggested_actions


def test_detect_missing_test_instructions_from_warnings():
    fake_warning = type("W", (), {"code": "A3", "message": "missing"})()
    assert mod.detect_missing_test_instructions([fake_warning]) is True


def test_validate_language_rejects_unsupported():
    try:
        mod.validate_language_supported("brainfuck")
        assert False, "Expected SpecsTddError"
    except mod.SpecsTddError as exc:
        assert exc.code == "A2"


def test_ensure_test_framework_reports_e2_for_missing_python(tmp_path, monkeypatch):
    # Simulate no pytest available
    monkeypatch.setenv("PATH", "")
    # project dir without pyproject or pytest.ini
    project = str(tmp_path)
    try:
        mod.ensure_test_framework("python", project)
        assert False, "Expected SpecsTddError"
    except mod.SpecsTddError as exc:
        assert exc.code == "E2"


def test_analyze_unexpected_pass_returns_message():
    red = {"status": "unexpected-pass"}
    msg = mod.analyze_unexpected_pass(red)
    assert msg and "Generated tests passed" in msg
