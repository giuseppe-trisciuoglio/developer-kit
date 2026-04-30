#!/usr/bin/env python3
"""Tests for ts-quality-gate.py."""

import importlib.util
import os
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, hooks_dir)

spec = importlib.util.spec_from_file_location(
    "ts_quality_gate", os.path.join(hooks_dir, "ts-quality-gate.py")
)
ts_quality_gate = importlib.util.module_from_spec(spec)
sys.modules["ts_quality_gate"] = ts_quality_gate
spec.loader.exec_module(ts_quality_gate)


def test_run_eslint_falls_back_when_compact_formatter_is_missing():
    cwd = Path("/tmp/project")
    files = ["src/example.ts"]
    compact_failure = CompletedProcess(
        args=[],
        returncode=2,
        stdout="",
        stderr=(
            "The compact formatter is no longer part of core ESLint. "
            "Install it manually with `npm install -D eslint-formatter-compact`"
        ),
    )
    lint_failure = CompletedProcess(
        args=[],
        returncode=1,
        stdout="src/example.ts\n  1:1  error  Unexpected any  @typescript-eslint/no-explicit-any\n",
        stderr="",
    )

    with (
        patch.object(ts_quality_gate, "_find_eslint_config", return_value=cwd / "eslint.config.js"),
        patch.object(ts_quality_gate.shutil, "which", return_value="/usr/bin/npx"),
        patch.object(ts_quality_gate.subprocess, "run", side_effect=[compact_failure, lint_failure]) as run_mock,
    ):
        has_errors, output = ts_quality_gate._run_eslint(cwd, files)

    assert has_errors is True
    assert "Unexpected any" in output
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[0] == [
        "npx",
        "eslint",
        "--format",
        "compact",
        *files,
    ]
    assert run_mock.call_args_list[1].args[0] == ["npx", "eslint", *files]


def test_run_eslint_passes_when_fallback_run_succeeds():
    cwd = Path("/tmp/project")
    files = ["src/example.ts"]
    compact_failure = CompletedProcess(
        args=[],
        returncode=2,
        stdout="",
        stderr=(
            "The compact formatter is no longer part of core ESLint. "
            "Install it manually with `npm install -D eslint-formatter-compact`"
        ),
    )
    lint_success = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    with (
        patch.object(ts_quality_gate, "_find_eslint_config", return_value=cwd / "eslint.config.js"),
        patch.object(ts_quality_gate.shutil, "which", return_value="/usr/bin/npx"),
        patch.object(ts_quality_gate.subprocess, "run", side_effect=[compact_failure, lint_success]),
    ):
        has_errors, output = ts_quality_gate._run_eslint(cwd, files)

    assert has_errors is False
    assert output == ""
