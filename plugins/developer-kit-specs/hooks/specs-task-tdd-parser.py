#!/usr/bin/env python3
"""Parse and validate task files for /specs:task-tdd.

Pure stdlib parser for spec task markdown files. It extracts YAML-like
frontmatter, validates required fields, and returns the Test Instructions
section for downstream test generation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

TASK_ID_PATTERN = re.compile(r"^TASK-\d{3}$")
FRONTMATTER_DELIMITER = "---"
TEST_INSTRUCTIONS_HEADING = "## Test Instructions"
VALID_TASK_STATUSES = {"pending", "red-phase", "completed"}


class TaskFileError(ValueError):
    """Raised when a task file cannot be parsed or validated."""

    def __init__(self, message: str, *, code: str = "E3") -> None:
        super().__init__(message)
        self.code = code


@dataclass
class ParseWarning:
    code: str
    message: str
    suggested_action: str | None = None


@dataclass
class TaskFileData:
    path: str
    metadata: dict[str, object]
    title_heading: str
    test_instructions: str | None
    warnings: list[ParseWarning] = field(default_factory=list)

    def to_json(self) -> str:
        payload = asdict(self)
        return json.dumps(payload, indent=2)


def read_task_file(task_path: str) -> str:
    """Read a task markdown file from disk."""
    path = Path(task_path)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TaskFileError(
            (
                f"Task file not found: {task_path}. "
                "Provide a valid task file path or run '/specs:spec-to-tasks' first."
            ),
            code="E1",
        ) from exc
    except PermissionError as exc:
        raise TaskFileError(
            f"Task file is not readable: {task_path}. Check file permissions.",
            code="E1",
        ) from exc


def parse_task_file(task_path: str) -> TaskFileData:
    """Parse task file content into structured data."""
    content = read_task_file(task_path)
    frontmatter, body = split_frontmatter(content)
    metadata = parse_frontmatter(frontmatter)
    validate_metadata(metadata)
    title_heading = extract_title_heading(body)
    test_instructions, warnings = extract_test_instructions(body)

    return TaskFileData(
        path=str(Path(task_path)),
        metadata=metadata,
        title_heading=title_heading,
        test_instructions=test_instructions,
        warnings=warnings,
    )


def split_frontmatter(content: str) -> tuple[str, str]:
    """Return frontmatter and markdown body."""
    if not content.startswith(FRONTMATTER_DELIMITER):
        raise TaskFileError(
            "Invalid task file structure: missing YAML frontmatter block at the top of the file.",
            code="E3",
        )

    try:
        _, frontmatter, body = content.split(FRONTMATTER_DELIMITER, 2)
    except ValueError as exc:
        raise TaskFileError(
            "Invalid task file structure: frontmatter must be wrapped in matching '---' delimiters.",
            code="E3",
        ) from exc

    if not body.strip():
        raise TaskFileError(
            "Invalid task file structure: markdown body is empty after frontmatter.",
            code="E3",
        )

    return frontmatter.strip(), body.lstrip("\n")


def parse_frontmatter(frontmatter: str) -> dict[str, object]:
    """Parse the limited frontmatter schema used by spec task files."""
    metadata: dict[str, object] = {
        "id": None,
        "title": None,
        "spec": None,
        "lang": None,
        "dependencies": [],
        "status": None,
    }

    for raw_line in frontmatter.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            raise TaskFileError(
                f"Invalid frontmatter line: '{raw_line}'. Expected 'key: value' format.",
                code="E3",
            )

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if key == "dependencies":
            metadata[key] = parse_dependencies(value)
            continue

        metadata[key] = strip_quotes(value) if value else None

    return metadata


def parse_dependencies(value: str) -> list[str]:
    """Parse dependencies from inline YAML list syntax."""
    if not value:
        return []
    if value == "[]":
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise TaskFileError(
            "Invalid frontmatter field 'dependencies': expected inline list syntax like [TASK-001, TASK-002].",
            code="E3",
        )

    items = []
    inner = value[1:-1].strip()
    if not inner:
        return items

    for item in inner.split(","):
        stripped = strip_quotes(item.strip())
        if stripped:
            items.append(stripped)
    return items


def strip_quotes(value: str) -> str:
    """Strip matching single or double quotes around a scalar."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def validate_metadata(metadata: dict[str, object]) -> None:
    """Validate required frontmatter fields and task ID format."""
    required_fields = ("id", "title", "spec", "lang", "dependencies", "status")
    missing = [field for field in required_fields if metadata.get(field) in (None, "")]
    if missing:
        joined = ", ".join(missing)
        raise TaskFileError(
            f"Invalid task file structure: missing required frontmatter field(s): {joined}.",
            code="E3",
        )

    task_id = metadata["id"]
    if not isinstance(task_id, str) or not TASK_ID_PATTERN.match(task_id):
        raise TaskFileError(
            (
                "Invalid task identifier format. Expected 'TASK-XXX' with a 3-digit number "
                f"(for example TASK-001), got: {task_id!r}."
            ),
            code="E3",
        )

    dependencies = metadata["dependencies"]
    if not isinstance(dependencies, list):
        raise TaskFileError(
            "Invalid frontmatter field 'dependencies': expected a list.",
            code="E3",
        )

    for dependency in dependencies:
        if not isinstance(dependency, str) or not TASK_ID_PATTERN.match(dependency):
            raise TaskFileError(
                (
                    "Invalid dependency identifier format. Dependencies must use "
                    "'TASK-XXX' with a 3-digit number."
                ),
                code="E3",
            )

    status = metadata["status"]
    if not isinstance(status, str) or status not in VALID_TASK_STATUSES:
        supported = ", ".join(sorted(VALID_TASK_STATUSES))
        raise TaskFileError(
            (
                "Invalid frontmatter field 'status'. Expected one of: "
                f"{supported}. Got: {status!r}."
            ),
            code="E3",
        )


def extract_title_heading(body: str) -> str:
    """Extract the first markdown heading from the task body."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    raise TaskFileError(
        "Invalid task file structure: missing task title heading in markdown body.",
        code="E3",
    )


def extract_test_instructions(body: str) -> tuple[str | None, list[ParseWarning]]:
    """Extract the Test Instructions section and return any warning state."""
    lines = body.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == TEST_INSTRUCTIONS_HEADING:
            start_index = index + 1
            break

    if start_index is None:
        return None, [
            ParseWarning(
                code="A3",
                message="Task file does not contain Test Instructions section.",
                suggested_action=(
                    "Prompt the user to generate Test Instructions or rerun '/specs:spec-to-tasks' "
                    "to regenerate the task file."
                ),
            )
        ]

    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)

    section = "\n".join(collected).strip()
    if not section:
        return None, [
            ParseWarning(
                code="A3",
                message="Task file contains an empty Test Instructions section.",
                suggested_action=(
                    "Prompt the user to add test guidance before running '/specs:task-tdd'."
                ),
            )
        ]

    return section, []


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse and validate a spec task file.")
    parser.add_argument("--task", required=True, help="Path to the task markdown file.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        result = parse_task_file(args.task)
    except TaskFileError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}, indent=2))
        return 1

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
