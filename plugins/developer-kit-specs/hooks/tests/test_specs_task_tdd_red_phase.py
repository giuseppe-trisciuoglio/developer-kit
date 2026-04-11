#!/usr/bin/env python3
"""Tests for specs-task-tdd-red-phase.py."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from unittest import mock


hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
red_phase_path = os.path.join(hooks_dir, "specs-task-tdd-red-phase.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_red_phase", red_phase_path)
task_tdd_red_phase = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_red_phase"] = task_tdd_red_phase
spec.loader.exec_module(task_tdd_red_phase)


def write_task_file(directory: str, content: str) -> str:
    path = Path(directory) / "TASK-010.md"
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return str(path)


def build_task(directory: str, lang: str) -> str:
    return write_task_file(
        directory,
        f"""
        ---
        id: TASK-010
        title: "RED Phase Verification"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: {lang}
        dependencies: [TASK-003]
        status: pending
        ---

        # TASK-010: RED Phase Verification

        ## Test Instructions
        **1. Mandatory Unit Tests:**
           - [ ] Verify that generated tests fail in RED phase.

        **2. Mandatory Integration Tests:**
           - [ ] Verify that complete RED verification flow succeeds.
        """,
    )


def create_generated_test(project_root: str, relative_path: str) -> None:
    path = Path(project_root) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("placeholder\n", encoding="utf-8")


def test_resolve_runner_uses_pytest_for_python_tasks():
    runner = task_tdd_red_phase.resolve_runner("python", ".", "tests/test_spec_behavior.py")

    assert runner.framework == "pytest"
    assert runner.command[0] in {"pytest", "python3"}
    assert "tests/test_spec_behavior.py" in runner.command


def test_resolve_runner_prefers_maven_wrapper_when_present():
    with tempfile.TemporaryDirectory() as temp_dir:
        mvnw = Path(temp_dir) / "mvnw"
        mvnw.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        mvnw.chmod(0o755)

        runner = task_tdd_red_phase.resolve_runner("spring", temp_dir, "src/test/java/com/example/FooTest.java")

    assert runner.framework == "maven"
    assert runner.command[0] == "./mvnw"
    assert "-Dtest=FooTest" in runner.command


def test_verify_red_phase_confirms_failing_tests_and_captures_artifacts():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, "python")
        create_generated_test(temp_dir, "tests/test_verification.py")

        generated = mock.Mock(language="python", output_path="tests/test_verification.py", warnings=[])
        completed = subprocess.CompletedProcess(
            args=["pytest"],
            returncode=1,
            stdout="FAIL tests/test_verification.py::test_red\n",
            stderr="AssertionError: RED expected\nTraceback (most recent call last):\n",
        )

        with mock.patch.object(
            task_tdd_red_phase, "load_generator_module"
        ) as load_generator, mock.patch.object(
            task_tdd_red_phase.subprocess, "run", return_value=completed
        ):
            load_generator.return_value.generate_from_task_file.return_value = generated
            result = task_tdd_red_phase.verify_red_phase(task_file, project_root=temp_dir)

    assert result.status == "red-confirmed"
    assert result.red_confirmed is True
    assert result.returncode == 1
    assert "AssertionError" in "\n".join(result.failure_artifacts)


def test_verify_red_phase_reports_unexpected_pass_warning():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, "python")
        create_generated_test(temp_dir, "tests/test_verification.py")

        generated = mock.Mock(language="python", output_path="tests/test_verification.py", warnings=[])
        completed = subprocess.CompletedProcess(
            args=["pytest"],
            returncode=0,
            stdout="1 passed\n",
            stderr="",
        )

        with mock.patch.object(
            task_tdd_red_phase, "load_generator_module"
        ) as load_generator, mock.patch.object(
            task_tdd_red_phase.subprocess, "run", return_value=completed
        ):
            load_generator.return_value.generate_from_task_file.return_value = generated
            result = task_tdd_red_phase.verify_red_phase(task_file, project_root=temp_dir)

    assert result.status == "unexpected-pass"
    assert result.red_confirmed is False
    assert any("passed unexpectedly" in warning for warning in result.warnings)


def test_verify_red_phase_returns_timeout_result():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, "python")
        create_generated_test(temp_dir, "tests/test_verification.py")

        generated = mock.Mock(language="python", output_path="tests/test_verification.py", warnings=[])
        timeout = subprocess.TimeoutExpired(cmd=["pytest"], timeout=5, output="running\n", stderr="still running\n")

        with mock.patch.object(
            task_tdd_red_phase, "load_generator_module"
        ) as load_generator, mock.patch.object(
            task_tdd_red_phase.subprocess, "run", side_effect=timeout
        ):
            load_generator.return_value.generate_from_task_file.return_value = generated
            result = task_tdd_red_phase.verify_red_phase(
                task_file,
                project_root=temp_dir,
                timeout_seconds=5,
            )

    assert result.status == "execution-timeout"
    assert result.returncode is None
    assert any("timed out" in warning for warning in result.warnings)


def test_resolve_runner_raises_e2_when_framework_is_missing():
    with mock.patch.object(task_tdd_red_phase, "command_exists", return_value=False):
        try:
            task_tdd_red_phase.resolve_runner("php", ".", "tests/SpecBehaviorTest.php")
            assert False, "Expected RedPhaseError"
        except task_tdd_red_phase.RedPhaseError as exc:
            assert exc.code == "E2"
            assert "PHPUnit" in str(exc)


def test_verify_red_phase_requires_generated_test_file_to_exist():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, "python")
        generated = mock.Mock(language="python", output_path="tests/test_verification.py", warnings=[])

        with mock.patch.object(task_tdd_red_phase, "load_generator_module") as load_generator:
            load_generator.return_value.generate_from_task_file.return_value = generated
            try:
                task_tdd_red_phase.verify_red_phase(task_file, project_root=temp_dir)
                assert False, "Expected RedPhaseError"
            except task_tdd_red_phase.RedPhaseError as exc:
                assert exc.code == "E1"
                assert "Generated test file not found" in str(exc)
