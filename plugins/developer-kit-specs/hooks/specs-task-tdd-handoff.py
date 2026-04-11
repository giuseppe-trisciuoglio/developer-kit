#!/usr/bin/env python3
"""Prepare implementation handoff artifacts for /specs:task-tdd."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

DRIFT_DIR_NAME = "_drift"
HANDOFF_FILE_PREFIX = "tdd-handoff-"


class TddHandoffError(ValueError):
    """Raised when TDD handoff preparation cannot complete safely."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class HandoffResult:
    task_path: str
    handoff_path: str
    implementation_command: str
    red_phase_confirmed: bool
    generated_test_count: int
    summary_lines: list[str]
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def load_sibling_module(filename: str, module_name: str):
    module_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise TddHandoffError(f"Unable to load module from {module_path}.", code="E3")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_parser_module():
    return load_sibling_module("specs-task-tdd-parser.py", "specs_task_tdd_parser")


def read_task_parts(task_path: str) -> tuple[Any, str]:
    parser_module = load_parser_module()
    try:
        task_data = parser_module.parse_task_file(task_path)
        content = parser_module.read_task_file(task_path)
        _, body = parser_module.split_frontmatter(content)
        return task_data, body
    except parser_module.TaskFileError as exc:
        raise TddHandoffError(str(exc), code=exc.code) from exc


def parse_frontmatter_values(task_path: str) -> dict[str, Any]:
    parser_module = load_parser_module()
    try:
        content = parser_module.read_task_file(task_path)
        frontmatter, _ = parser_module.split_frontmatter(content)
    except parser_module.TaskFileError as exc:
        raise TddHandoffError(str(exc), code=exc.code) from exc

    values: dict[str, Any] = {}
    for raw_line in frontmatter.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise TddHandoffError(
                f"Invalid frontmatter line: '{raw_line}'. Expected 'key: value' format.",
                code="E3",
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key in {"testReferences", "redPhase"}:
            try:
                values[key] = json.loads(value) if value else None
            except json.JSONDecodeError as exc:
                raise TddHandoffError(
                    f"Invalid JSON payload for frontmatter field '{key}'.",
                    code="E3",
                ) from exc
        else:
            values[key] = value.strip('"') if value else None

    return values


def extract_section(body: str, heading: str) -> str:
    lines = body.splitlines()
    capture = False
    collected: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture:
            collected.append(line.rstrip())

    return "\n".join(collected).strip()


def build_implementation_command(task_path: str, language: str | None) -> str:
    parts = ["/specs:task-implementation"]
    if language:
        parts.append(f"--lang={language}")
    parts.append(f'--task="{task_path}"')
    return " ".join(parts)


def render_handoff_markdown(
    task_data,
    *,
    body: str,
    task_path: str,
    handoff_generated_at: str,
    test_references: list[dict[str, Any]],
    red_phase: dict[str, Any],
    implementation_command: str,
    warnings: list[str],
) -> str:
    functional_description = ""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("**Functional Description**:"):
            functional_description = stripped.split(":", 1)[1].strip()
            break

    acceptance_criteria = extract_section(body, "## Acceptance Criteria")
    technical_context = extract_section(body, "## Technical Context (from Codebase Analysis)")

    lines = [
        f"# TDD Implementation Handoff — {task_data.metadata['id']}",
        "",
        f"**Generated**: {handoff_generated_at}",
        f"**Task**: {task_data.metadata['id']} — {task_data.metadata['title']}",
        f"**Task File**: `{task_path}`",
        f"**Spec**: `{task_data.metadata['spec']}`",
        "",
        "## RED Phase Status",
        "",
    ]

    if red_phase.get("verified"):
        lines.append(f"RED phase confirmed via `{red_phase.get('framework', 'unknown')}`.")
    else:
        lines.append("RED phase is not confirmed yet.")

    if red_phase.get("summary"):
        lines.append(f"Summary: {red_phase['summary']}")

    lines.extend(["", "## Generated Tests", ""])
    if test_references:
        for reference in test_references:
            path = reference.get("path", "unknown")
            test_type = reference.get("test_type", "unknown")
            language = reference.get("language", "unknown")
            scenario_count = reference.get("scenario_count", "unknown")
            lines.append(f"- `{path}` ({test_type}, {language}, scenarios: {scenario_count})")
    else:
        lines.append("- No generated tests were recorded in task metadata.")

    lines.extend(["", "## Implementation Focus", ""])
    if functional_description:
        lines.append(functional_description)
        lines.append("")
    if acceptance_criteria:
        lines.append(acceptance_criteria)
    else:
        lines.append("No acceptance criteria were extracted from the task body.")

    lines.extend(["", "## Context To Preserve", ""])
    if technical_context:
        lines.append(technical_context)
    else:
        lines.append(
            "Use the task specification and generated failing tests as the source of truth for GREEN phase work."
        )

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. Review the generated failing tests and confirm they still describe the intended behavior.",
            f"2. Start GREEN phase with `{implementation_command}`.",
            "3. Implement the minimum code required to make the generated tests pass, then proceed to REFACTOR.",
        ]
    )

    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines).rstrip() + "\n"


def prepare_handoff(
    task_path: str,
    *,
    language: str | None = None,
    project_root: str = ".",
) -> HandoffResult:
    task_data, body = read_task_parts(task_path)
    frontmatter_values = parse_frontmatter_values(task_path)

    test_references = frontmatter_values.get("testReferences") or []
    if not isinstance(test_references, list):
        raise TddHandoffError(
            "Invalid task metadata: testReferences must be a JSON array.",
            code="E3",
        )

    red_phase = frontmatter_values.get("redPhase") or {}
    if not isinstance(red_phase, dict):
        raise TddHandoffError(
            "Invalid task metadata: redPhase must be a JSON object.",
            code="E3",
        )

    effective_language = language or task_data.metadata.get("lang")
    implementation_command = build_implementation_command(task_path, effective_language)

    warnings: list[str] = []
    if not test_references:
        warnings.append("No generated test references were found in the task metadata.")
    if not red_phase.get("verified"):
        warnings.append("RED phase is not confirmed in task metadata.")

    spec_path = Path(str(task_data.metadata["spec"]))
    drift_dir = (Path(project_root) / spec_path.parent / DRIFT_DIR_NAME).resolve()
    try:
        drift_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        raise TddHandoffError(
            f"Permission denied: cannot create handoff directory {drift_dir}",
            code="E4",
        ) from exc

    handoff_path = drift_dir / f"{HANDOFF_FILE_PREFIX}{str(task_data.metadata['id']).lower()}.md"
    generated_at = datetime.now().isoformat(timespec="seconds")
    content = render_handoff_markdown(
        task_data,
        body=body,
        task_path=task_path,
        handoff_generated_at=generated_at,
        test_references=test_references,
        red_phase=red_phase,
        implementation_command=implementation_command,
        warnings=warnings,
    )

    try:
        handoff_path.write_text(content, encoding="utf-8")
    except PermissionError as exc:
        raise TddHandoffError(
            f"Permission denied: cannot write handoff file {handoff_path}",
            code="E4",
        ) from exc

    summary_lines = [
        f"Generated tests: {len(test_references)}",
        f"RED phase confirmed: {'yes' if red_phase.get('verified') else 'no'}",
        f"Implementation command: {implementation_command}",
    ]

    return HandoffResult(
        task_path=task_path,
        handoff_path=str(handoff_path),
        implementation_command=implementation_command,
        red_phase_confirmed=bool(red_phase.get("verified")),
        generated_test_count=len(test_references),
        summary_lines=summary_lines,
        warnings=warnings,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare TDD implementation handoff documentation."
    )
    parser.add_argument("--task", required=True, help="Path to the task markdown file.")
    parser.add_argument("--lang", help="Override language from task frontmatter.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to resolve the spec folder for handoff artifacts.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        result = prepare_handoff(
            args.task,
            language=args.lang,
            project_root=args.project_root,
        )
    except TddHandoffError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}, indent=2))
        return 1

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
