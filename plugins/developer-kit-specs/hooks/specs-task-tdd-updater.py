#!/usr/bin/env python3
"""Update task files with TDD generation and RED-phase verification metadata."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

SUMMARY_START = "<!-- specs:task-tdd summary:start -->"
SUMMARY_END = "<!-- specs:task-tdd summary:end -->"
SUMMARY_HEADING = "## TDD Test Generation Summary"


class TaskUpdateError(ValueError):
    """Raised when task file updates cannot be completed safely."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class TaskUpdateResult:
    task_path: str
    status_before: str
    status_after: str
    test_references: list[dict[str, Any]]
    red_phase: dict[str, Any]
    summary_updated: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def load_sibling_module(filename: str, module_name: str):
    module_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise TaskUpdateError(
            f"Unable to load module from {module_path}.",
            code="E3",
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_parser_module():
    return load_sibling_module("specs-task-tdd-parser.py", "specs_task_tdd_parser")


def load_generator_module():
    return load_sibling_module("specs-task-tdd-generator.py", "specs_task_tdd_generator")


def load_red_phase_module():
    return load_sibling_module("specs-task-tdd-red-phase.py", "specs_task_tdd_red_phase")


def read_task_parts(task_path: str) -> tuple[str, str]:
    parser_module = load_parser_module()
    try:
        content = parser_module.read_task_file(task_path)
        return parser_module.split_frontmatter(content)
    except parser_module.TaskFileError as exc:
        raise TaskUpdateError(str(exc), code=exc.code) from exc


def parse_frontmatter_lines(frontmatter: str) -> tuple[list[dict[str, str]], dict[str, str]]:
    entries: list[dict[str, str]] = []
    values: dict[str, str] = {}

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            entries.append({"type": "blank", "raw": ""})
            continue
        if stripped.startswith("#"):
            entries.append({"type": "comment", "raw": line})
            continue
        if ":" not in line:
            raise TaskUpdateError(
                f"Invalid frontmatter line: '{line}'. Expected 'key: value' format.",
                code="E3",
            )

        key, raw_value = line.split(":", 1)
        normalized_key = key.strip()
        value = raw_value.strip()
        entries.append({"type": "field", "key": normalized_key, "value": value})
        values[normalized_key] = value

    return entries, values


def format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if value and all(ch.isalnum() or ch in {"-", "_", ".", "/"} for ch in value):
            return value
        return json.dumps(value)
    return json.dumps(value, ensure_ascii=True, separators=(",", ": "))


def merge_test_references(
    existing_value: str | None,
    new_reference: dict[str, Any],
) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    if existing_value:
        try:
            parsed = json.loads(existing_value)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, list):
            references = [item for item in parsed if isinstance(item, dict)]

    merged: list[dict[str, Any]] = []
    replaced = False
    for reference in references:
        if reference.get("path") == new_reference.get("path"):
            merged.append(new_reference)
            replaced = True
        else:
            merged.append(reference)

    if not replaced:
        merged.append(new_reference)
    return merged


def update_frontmatter(frontmatter: str, updates: dict[str, str]) -> str:
    entries, _ = parse_frontmatter_lines(frontmatter)
    seen: set[str] = set()
    output_lines: list[str] = []

    for entry in entries:
        entry_type = entry["type"]
        if entry_type == "field":
            key = entry["key"]
            value = updates.get(key, entry["value"])
            output_lines.append(f"{key}: {value}")
            seen.add(key)
            continue
        output_lines.append(entry["raw"])

    for key, value in updates.items():
        if key not in seen:
            output_lines.append(f"{key}: {value}")

    return "\n".join(output_lines).strip() + "\n"


def render_summary(
    generated,
    red_phase_result,
    *,
    generated_on: str,
) -> str:
    lines = [
        SUMMARY_START,
        SUMMARY_HEADING,
        "",
        f"**Generated On**: {generated_on}",
        f"**Test File**: `{generated.output_path}`",
        f"**Language**: `{generated.language}`",
        f"**Test Type**: `{generated.test_type}`",
        f"**RED Phase Status**: `{red_phase_result.status}`",
        f"**Verification Summary**: {red_phase_result.summary}",
        "",
        "### Generated Scenarios",
    ]

    for scenario in generated.scenarios:
        lines.append(f"- `{scenario.test_name}`: {scenario.description}")

    lines.extend(
        [
            "",
            "### Verification Details",
            f"- Framework: `{red_phase_result.framework}`",
            f"- Command: `{ ' '.join(red_phase_result.command) }`",
            f"- Return code: `{red_phase_result.returncode}`",
        ]
    )

    if red_phase_result.failure_artifacts:
        lines.append("- Failure artifacts:")
        for artifact in red_phase_result.failure_artifacts[:5]:
            lines.append(f"  - `{artifact}`")

    if red_phase_result.warnings:
        lines.append("- Warnings:")
        for warning in red_phase_result.warnings:
            lines.append(f"  - {warning}")

    lines.extend(["", SUMMARY_END])
    return "\n".join(lines).rstrip()


def upsert_summary(body: str, summary_block: str) -> tuple[str, bool]:
    if SUMMARY_START in body and SUMMARY_END in body:
        start = body.index(SUMMARY_START)
        end = body.index(SUMMARY_END) + len(SUMMARY_END)
        updated = body[:start].rstrip() + "\n\n" + summary_block + body[end:]
        return updated.rstrip() + "\n", True

    insertion = "\n\n" + summary_block + "\n"
    if "## Implementation Summary" in body:
        marker = body.index("## Implementation Summary")
        updated = body[:marker].rstrip() + insertion + "\n" + body[marker:].lstrip("\n")
        return updated.rstrip() + "\n", True

    return body.rstrip() + insertion, True


def build_test_reference(generated, *, generated_on: str) -> dict[str, Any]:
    return {
        "path": generated.output_path,
        "test_type": generated.test_type,
        "language": generated.language,
        "generated_at": generated_on,
        "scenario_count": len(generated.scenarios),
    }


def build_red_phase_payload(red_phase_result, *, verified_on: str) -> dict[str, Any]:
    return {
        "status": red_phase_result.status,
        "verified": bool(red_phase_result.red_confirmed),
        "verified_at": verified_on,
        "framework": red_phase_result.framework,
        "test_file": red_phase_result.test_file,
        "summary": red_phase_result.summary,
        "command": red_phase_result.command,
        "warnings": red_phase_result.warnings,
    }


def update_task_file(
    task_path: str,
    *,
    language: str | None = None,
    project_root: str = ".",
    test_type: str = "both",
) -> TaskUpdateResult:
    frontmatter, body = read_task_parts(task_path)
    _, existing_values = parse_frontmatter_lines(frontmatter)

    generator_module = load_generator_module()
    red_phase_module = load_red_phase_module()

    try:
        generated = generator_module.generate_from_task_file(
            task_path,
            language=language,
            test_type=test_type,
        )
    except generator_module.GenerationError as exc:
        raise TaskUpdateError(str(exc), code=exc.code) from exc

    try:
        red_phase_result = red_phase_module.verify_red_phase(
            task_path,
            language=language,
            project_root=project_root,
            test_type=test_type,
        )
    except red_phase_module.RedPhaseError as exc:
        raise TaskUpdateError(str(exc), code=exc.code) from exc

    today = date.today().isoformat()
    status_before = existing_values.get("status", "pending").strip('"')
    status_after = "red-phase" if red_phase_result.red_confirmed else status_before

    test_reference = build_test_reference(generated, generated_on=today)
    test_references = merge_test_references(existing_values.get("testReferences"), test_reference)
    red_phase_payload = build_red_phase_payload(red_phase_result, verified_on=today)

    updates = {
        "status": format_scalar(status_after),
        "testReferences": format_scalar(test_references),
        "redPhase": format_scalar(red_phase_payload),
    }
    if red_phase_result.red_confirmed:
        updates["red_phase_completed_date"] = format_scalar(today)

    updated_frontmatter = update_frontmatter(frontmatter, updates)
    summary_block = render_summary(generated, red_phase_result, generated_on=today)
    updated_body, summary_updated = upsert_summary(body, summary_block)

    task_file = Path(task_path)
    try:
        task_file.write_text(
            f"---\n{updated_frontmatter}---\n\n{updated_body.lstrip()}",
            encoding="utf-8",
        )
    except PermissionError as exc:
        raise TaskUpdateError(
            f"Permission denied: cannot update task file {task_path}",
            code="E4",
        ) from exc

    return TaskUpdateResult(
        task_path=str(task_file),
        status_before=status_before,
        status_after=status_after,
        test_references=test_references,
        red_phase=red_phase_payload,
        summary_updated=summary_updated,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update a task file with TDD metadata.")
    parser.add_argument("--task", required=True, help="Path to the task markdown file.")
    parser.add_argument("--lang", help="Override language from task frontmatter.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to resolve generated test files and execute verification.",
    )
    parser.add_argument(
        "--test-type",
        default="both",
        help="unit, integration, or both (default: both).",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        result = update_task_file(
            args.task,
            language=args.lang,
            project_root=args.project_root,
            test_type=args.test_type,
        )
    except TaskUpdateError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}, indent=2))
        return 1

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
