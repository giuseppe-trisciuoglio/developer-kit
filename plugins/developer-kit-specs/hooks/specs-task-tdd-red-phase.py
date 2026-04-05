#!/usr/bin/env python3
"""Verify RED-phase test execution for /specs:task-tdd.

This hook executes the generated test file for a task and determines whether the
project is still in the RED phase of TDD:
- failing tests => RED confirmed
- passing tests => unexpected pass (A4 flow)
- missing framework / missing test file => structured error
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 30
FAILURE_KEYWORDS = (
    "assert",
    "assertionerror",
    "error",
    "exception",
    "fail",
    "failed",
    "traceback",
)


class RedPhaseError(ValueError):
    """Raised when RED-phase verification cannot be completed."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class RunnerSpec:
    language: str
    framework: str
    command: list[str]
    test_file: str


@dataclass
class RedPhaseResult:
    status: str
    language: str
    framework: str
    command: list[str]
    test_file: str
    project_root: str
    returncode: int | None
    red_confirmed: bool
    summary: str
    stdout: str = ""
    stderr: str = ""
    warnings: list[str] = field(default_factory=list)
    failure_artifacts: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def load_generator_module():
    """Load the sibling generator hook without requiring package installation."""
    generator_path = Path(__file__).with_name("specs-task-tdd-generator.py")
    module_name = "specs_task_tdd_generator"
    spec = importlib.util.spec_from_file_location(module_name, generator_path)
    if spec is None or spec.loader is None:
        raise RedPhaseError(
            f"Unable to load generator module from {generator_path}.",
            code="E3",
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def ensure_file_exists(path: Path, *, label: str, code: str = "E1") -> None:
    if not path.exists():
        raise RedPhaseError(f"{label} not found: {path}", code=code)


def command_exists(command: str, project_root: Path) -> bool:
    candidate = project_root / command
    if candidate.exists() and os.access(candidate, os.X_OK):
        return True
    return shutil.which(command) is not None


def resolve_test_target(language: str, test_file: str) -> str:
    path = Path(test_file)
    if language in {"java", "spring"}:
        return path.stem
    return test_file


def build_runner_candidates(language: str, test_file: str) -> list[tuple[str, list[str]]]:
    target = resolve_test_target(language, test_file)
    if language in {"java", "spring"}:
        return [
            ("maven", ["./mvnw", "test", f"-Dtest={target}"]),
            ("maven", ["mvn", "test", f"-Dtest={target}"]),
            ("gradle", ["./gradlew", "test", "--tests", target]),
            ("gradle", ["gradle", "test", "--tests", target]),
        ]
    if language in {"typescript", "nestjs", "react"}:
        return [
            ("npm", ["npm", "test", "--", "--runInBand", "--runTestsByPath", test_file]),
        ]
    if language == "python":
        return [
            ("pytest", ["pytest", test_file, "-q"]),
            ("pytest", ["python3", "-m", "pytest", test_file, "-q"]),
        ]
    if language == "php":
        return [
            ("phpunit", ["vendor/bin/phpunit", test_file]),
            ("phpunit", ["phpunit", test_file]),
        ]
    if language == "general":
        raise RedPhaseError(
            "General mode generates a RED-phase plan, not an executable test file. "
            "Use a concrete language to run RED verification.",
            code="E2",
        )
    raise RedPhaseError(
        f"Language '{language}' does not have a registered RED-phase runner.",
        code="A2",
    )


def resolve_runner(language: str, project_root: str, test_file: str) -> RunnerSpec:
    root = Path(project_root)
    for framework, command in build_runner_candidates(language, test_file):
        if command_exists(command[0], root):
            return RunnerSpec(
                language=language,
                framework=framework,
                command=command,
                test_file=test_file,
            )

    framework_hint = {
        "java": "Maven or Gradle",
        "spring": "Maven or Gradle",
        "typescript": "npm/Jest",
        "nestjs": "npm/Jest",
        "react": "npm/Jest",
        "python": "pytest",
        "php": "PHPUnit",
    }.get(language, "test framework")
    raise RedPhaseError(
        (
            f"Test framework {framework_hint} not found in project. "
            f"Install/configure the {language} test framework before RED verification."
        ),
        code="E2",
    )


def extract_failure_artifacts(stdout: str, stderr: str) -> list[str]:
    artifacts: list[str] = []
    for stream in (stderr, stdout):
        for raw_line in stream.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lowered = line.lower()
            if any(keyword in lowered for keyword in FAILURE_KEYWORDS):
                artifacts.append(line)
        if artifacts:
            break

    if not artifacts:
        combined_lines = [line.strip() for line in (stderr or stdout).splitlines() if line.strip()]
        artifacts.extend(combined_lines[:5])

    return artifacts[:10]


def verify_red_phase(
    task_path: str,
    *,
    language: str | None = None,
    project_root: str = ".",
    test_type: str = "both",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> RedPhaseResult:
    root = Path(project_root)
    ensure_file_exists(root, label="Project root", code="E1")

    generator = load_generator_module()
    try:
        generated = generator.generate_from_task_file(
            task_path,
            language=language,
            test_type=test_type,
        )
    except generator.GenerationError as exc:
        raise RedPhaseError(str(exc), code=exc.code) from exc

    test_file_path = root / generated.output_path
    ensure_file_exists(test_file_path, label="Generated test file", code="E1")

    runner = resolve_runner(generated.language, str(root), generated.output_path)
    try:
        completed = subprocess.run(
            runner.command,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return RedPhaseResult(
            status="execution-timeout",
            language=generated.language,
            framework=runner.framework,
            command=runner.command,
            test_file=generated.output_path,
            project_root=str(root),
            returncode=None,
            red_confirmed=False,
            summary=f"RED verification timed out after {timeout_seconds}s.",
            stdout=stdout,
            stderr=stderr,
            warnings=["Test execution timed out before RED status could be confirmed."],
            failure_artifacts=extract_failure_artifacts(stdout, stderr),
        )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    artifacts = extract_failure_artifacts(stdout, stderr)

    if completed.returncode == 0:
        warnings = [
            "Generated tests passed unexpectedly. This may indicate existing implementation, "
            "incorrect assertions, or incomplete test setup."
        ]
        return RedPhaseResult(
            status="unexpected-pass",
            language=generated.language,
            framework=runner.framework,
            command=runner.command,
            test_file=generated.output_path,
            project_root=str(root),
            returncode=completed.returncode,
            red_confirmed=False,
            summary="Generated tests passed unexpectedly during RED verification.",
            stdout=stdout,
            stderr=stderr,
            warnings=warnings,
            failure_artifacts=artifacts,
        )

    warnings = list(generated.warnings)
    if not artifacts:
        warnings.append("Test runner failed without obvious failure artifacts; verification used exit code.")

    return RedPhaseResult(
        status="red-confirmed",
        language=generated.language,
        framework=runner.framework,
        command=runner.command,
        test_file=generated.output_path,
        project_root=str(root),
        returncode=completed.returncode,
        red_confirmed=True,
        summary="RED phase confirmed: generated tests failed as expected.",
        stdout=stdout,
        stderr=stderr,
        warnings=warnings,
        failure_artifacts=artifacts,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify RED-phase test execution for a spec task.")
    parser.add_argument("--task", required=True, help="Path to the task markdown file.")
    parser.add_argument("--lang", help="Override language from task frontmatter.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to locate the generated test file and execute the test runner.",
    )
    parser.add_argument(
        "--test-type",
        default="both",
        help="unit, integration, or both (default: both).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Maximum seconds to wait for test execution (default: {DEFAULT_TIMEOUT_SECONDS}).",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        result = verify_red_phase(
            args.task,
            language=args.lang,
            project_root=args.project_root,
            test_type=args.test_type,
            timeout_seconds=args.timeout_seconds,
        )
    except RedPhaseError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}, indent=2))
        return 1

    print(result.to_json())
    return 0 if result.status in {"red-confirmed", "unexpected-pass"} else 1


if __name__ == "__main__":
    sys.exit(main())
