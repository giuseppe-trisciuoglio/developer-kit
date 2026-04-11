#!/usr/bin/env python3
"""Error handling and alternative flows for /specs:task-tdd (TASK-012).

Provides small, testable helpers that consolidate common error checks used by
other specs hooks (parser, generator, red-phase, updater). The module raises
SpecsTddError with structured codes for programmatic handling.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


class SpecsTddError(ValueError):
    """Structured error used across specs/task-tdd hooks.

    Attributes:
        code: Short error code (E1-E5, A1-A4) per spec.
    """

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class ExistingFileChoices:
    path: str
    exists: bool
    suggested_actions: List[str]


SUPPORTED_LANGUAGES = {
    "java",
    "spring",
    "typescript",
    "nestjs",
    "react",
    "python",
    "php",
    "general",
}


def ensure_task_file_exists(task_path: str) -> None:
    path = Path(task_path)
    if not path.exists():
        raise SpecsTddError(
            (
                f"Task file not found: {task_path}. "
                "Provide a valid task file path or run '/specs:spec-to-tasks' first."
            ),
            code="E1",
        )
    if not os.access(str(path), os.R_OK):
        raise SpecsTddError(f"Task file not readable: {task_path}. Check file permissions.", code="E4")


def ensure_project_root(project_root: str) -> None:
    root = Path(project_root)
    if not root.exists() or not root.is_dir():
        raise SpecsTddError(f"Project root not found: {project_root}", code="E1")


def validate_language_supported(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise SpecsTddError(f"Language '{language}' is not supported for RED verification.", code="A2")


def ensure_test_framework(language: str, project_root: str) -> None:
    """Detect likely test framework presence for the given language.

    Raises E2 when a likely test framework cannot be found.
    """
    root = Path(project_root)

    if language == "general":
        raise SpecsTddError(
            "General mode is non-executable: RED verification requires a concrete language.",
            code="E2",
        )

    # Language-specific heuristic checks
    if language in {"python"}:
        # Check for pytest on PATH or pyproject/pytest.ini present
        if shutil.which("pytest") or (root / "pyproject.toml").exists() or (root / "pytest.ini").exists():
            return
        raise SpecsTddError(
            "Pytest not found in project or PATH. Install/configure pytest before RED verification.",
            code="E2",
        )

    if language in {"typescript", "nestjs", "react"}:
        # Check for package.json and node_modules or npm availability
        if (root / "package.json").exists() or shutil.which("npm"):
            return
        raise SpecsTddError(
            "Node/Jest not detected. Ensure package.json or npm is available for RED verification.",
            code="E2",
        )

    if language in {"java", "spring"}:
        # Check for maven/gradle wrapper or mvn/gradle in PATH
        if (root / "mvnw").exists() or (root / "gradlew").exists() or shutil.which("mvn") or shutil.which("gradle"):
            return
        raise SpecsTddError(
            "Maven/Gradle not detected. Install or add build wrapper (mvnw/gradlew) for RED verification.",
            code="E2",
        )

    if language == "php":
        if (root / "composer.json").exists() or shutil.which("phpunit"):
            return
        raise SpecsTddError(
            "PHPUnit not detected. Install or configure PHPUnit before RED verification.",
            code="E2",
        )

    # Fallback: unknown but treated as missing framework
    raise SpecsTddError("Test framework not found for specified language.", code="E2")


def detect_existing_test_file(test_path: str) -> ExistingFileChoices:
    path = Path(test_path)
    if path.exists():
        return ExistingFileChoices(
            path=str(path), exists=True, suggested_actions=["overwrite", "skip", "cancel"]
        )
    return ExistingFileChoices(path=str(path), exists=False, suggested_actions=["create"])


def detect_missing_test_instructions(warnings: Iterable[object]) -> bool:
    """Return True when parser warnings indicate missing test instructions (A3)."""
    for w in warnings:
        # Accept both ParseWarning-like objects or simple dicts
        code = getattr(w, "code", None) if not isinstance(w, dict) else w.get("code")
        if code == "A3":
            return True
    return False


def analyze_unexpected_pass(red_result: object) -> str | None:
    """Given a RedPhaseResult-like object or dict, return an actionable warning when tests pass.

    Returns a short message or None.
    """
    status = getattr(red_result, "status", None) if not isinstance(red_result, dict) else red_result.get("status")
    if status == "unexpected-pass":
        return (
            "Generated tests passed unexpectedly. Consider confirming if the implementation already exists, "
            "reviewing assertions, or reverting test generation."
        )
    return None


def format_error_json(exc: SpecsTddError) -> str:
    payload = {"error": {"code": exc.code, "message": str(exc)}}
    return json.dumps(payload, indent=2)
