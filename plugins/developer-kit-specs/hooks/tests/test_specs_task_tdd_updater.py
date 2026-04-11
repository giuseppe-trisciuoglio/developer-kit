#!/usr/bin/env python3
"""Tests for specs-task-tdd-updater.py."""

import importlib.util
import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path
from unittest import mock


hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
updater_path = os.path.join(hooks_dir, "specs-task-tdd-updater.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_updater", updater_path)
task_tdd_updater = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_updater"] = task_tdd_updater
spec.loader.exec_module(task_tdd_updater)


def write_task_file(directory: str, content: str) -> str:
    path = Path(directory) / "TASK-011.md"
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return str(path)


def build_task(
    directory: str,
    *,
    extra_frontmatter: str = "",
    extra_body: str = "",
) -> str:
    return write_task_file(
        directory,
        f"""
        ---
        id: TASK-011
        title: "Task File Updates"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: python
        dependencies: [TASK-010]
        status: pending
        {extra_frontmatter}
        ---

        # TASK-011: Task File Updates

        ## Acceptance Criteria

        - [ ] Preserve task content.

        ## Test Instructions
        **1. Mandatory Unit Tests:**
           - [ ] Verify that task file is read and parsed correctly.
           - [ ] Verify that YAML frontmatter is updated with test references.

        {extra_body}
        """,
    )


def build_generated():
    return mock.Mock(
        language="python",
        test_type="both",
        output_path="tests/test_task_file_updates.py",
        scenarios=[
            mock.Mock(
                test_name="task_file_is_read_and_parsed_correctly",
                description="task file is read and parsed correctly",
            ),
            mock.Mock(
                test_name="yaml_frontmatter_is_updated_with_test_references",
                description="YAML frontmatter is updated with test references",
            ),
        ],
        warnings=[],
    )


def build_red_phase_result(status: str = "red-confirmed", *, red_confirmed: bool = True):
    return mock.Mock(
        status=status,
        language="python",
        framework="pytest",
        command=["pytest", "tests/test_task_file_updates.py", "-q"],
        test_file="tests/test_task_file_updates.py",
        project_root=".",
        returncode=1 if red_confirmed else 0,
        red_confirmed=red_confirmed,
        summary="RED phase confirmed: generated tests failed as expected."
        if red_confirmed
        else "Generated tests passed unexpectedly during RED verification.",
        stdout="",
        stderr="AssertionError: RED expected",
        warnings=[] if red_confirmed else ["Generated tests passed unexpectedly."],
        failure_artifacts=["AssertionError: RED expected"],
    )


def parse_test_references(task_file: str):
    content = Path(task_file).read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("testReferences: "):
            return json.loads(line.split(": ", 1)[1])
    raise AssertionError("testReferences line not found")


def test_update_task_file_adds_frontmatter_metadata_and_summary():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir)
        generated = build_generated()
        red_phase = build_red_phase_result()

        with mock.patch.object(task_tdd_updater, "load_generator_module") as load_generator, mock.patch.object(
            task_tdd_updater, "load_red_phase_module"
        ) as load_red_phase:
            load_generator.return_value.generate_from_task_file.return_value = generated
            load_red_phase.return_value.verify_red_phase.return_value = red_phase

            result = task_tdd_updater.update_task_file(task_file, project_root=temp_dir)

        updated = Path(task_file).read_text(encoding="utf-8")

    assert result.status_before == "pending"
    assert result.status_after == "red-phase"
    assert "status: red-phase" in updated
    assert "testReferences:" in updated
    assert "redPhase:" in updated
    assert "red_phase_completed_date:" in updated
    assert "## TDD Test Generation Summary" in updated
    assert "## Test Instructions" in updated
    assert updated.count("## TDD Test Generation Summary") == 1


def test_update_task_file_merges_existing_test_reference_by_path():
    existing_reference = json.dumps(
        [
            {
                "path": "tests/test_task_file_updates.py",
                "test_type": "unit",
                "language": "python",
                "generated_at": "2026-04-04",
                "scenario_count": 1,
            }
        ],
        separators=(",", ": "),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, extra_frontmatter=f"testReferences: {existing_reference}")
        generated = build_generated()
        red_phase = build_red_phase_result()

        with mock.patch.object(task_tdd_updater, "load_generator_module") as load_generator, mock.patch.object(
            task_tdd_updater, "load_red_phase_module"
        ) as load_red_phase:
            load_generator.return_value.generate_from_task_file.return_value = generated
            load_red_phase.return_value.verify_red_phase.return_value = red_phase

            task_tdd_updater.update_task_file(task_file, project_root=temp_dir)

        references = parse_test_references(task_file)

    assert len(references) == 1
    assert references[0]["path"] == "tests/test_task_file_updates.py"
    assert references[0]["test_type"] == "both"
    assert references[0]["scenario_count"] == 2


def test_update_task_file_replaces_existing_summary_block_instead_of_duplicating():
    existing_summary = """
    <!-- specs:task-tdd summary:start -->
    ## TDD Test Generation Summary

    stale summary
    <!-- specs:task-tdd summary:end -->
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir, extra_body=existing_summary)
        generated = build_generated()
        red_phase = build_red_phase_result()

        with mock.patch.object(task_tdd_updater, "load_generator_module") as load_generator, mock.patch.object(
            task_tdd_updater, "load_red_phase_module"
        ) as load_red_phase:
            load_generator.return_value.generate_from_task_file.return_value = generated
            load_red_phase.return_value.verify_red_phase.return_value = red_phase

            task_tdd_updater.update_task_file(task_file, project_root=temp_dir)

        updated = Path(task_file).read_text(encoding="utf-8")

    assert updated.count("## TDD Test Generation Summary") == 1
    assert "stale summary" not in updated


def test_update_task_file_preserves_status_when_red_phase_not_confirmed():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = build_task(temp_dir)
        generated = build_generated()
        red_phase = build_red_phase_result(status="unexpected-pass", red_confirmed=False)

        with mock.patch.object(task_tdd_updater, "load_generator_module") as load_generator, mock.patch.object(
            task_tdd_updater, "load_red_phase_module"
        ) as load_red_phase:
            load_generator.return_value.generate_from_task_file.return_value = generated
            load_red_phase.return_value.verify_red_phase.return_value = red_phase

            result = task_tdd_updater.update_task_file(task_file, project_root=temp_dir)

        updated = Path(task_file).read_text(encoding="utf-8")

    assert result.status_after == "pending"
    assert "status: pending" in updated
    assert "red_phase_completed_date:" not in updated


def test_update_task_file_rejects_malformed_frontmatter():
    with tempfile.TemporaryDirectory() as temp_dir:
        task_file = write_task_file(
            temp_dir,
            """
            ---
            id TASK-011
            status: pending
            ---

            # Broken
            """,
        )

        try:
            task_tdd_updater.update_task_file(task_file, project_root=temp_dir)
            assert False, "Expected TaskUpdateError"
        except task_tdd_updater.TaskUpdateError as exc:
            assert exc.code == "E3"
            assert "frontmatter" in str(exc).lower()
