#!/usr/bin/env python3
"""Generate RED-phase test skeletons for /specs:task-tdd.

This module builds on the task parser hook. It reads Test Instructions from a
parsed task file, derives behavior-focused scenarios, and renders minimal test
files with intentionally failing assertions for the supported languages.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

CHECKBOX_PATTERN = re.compile(r"^\s*[-*]\s+\[ \]\s+(?P<text>.+?)\s*$")
CODE_LABEL_PATTERN = re.compile(r"`([^`]+)`")
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
CAMEL_BOUNDARY_PATTERN = re.compile(r"([a-z0-9])([A-Z])")
TEMPLATE_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([A-Z_]+)\s*\}\}")
JAVA_SOURCE_PATH_PATTERN = re.compile(
    r"(?:^|/)(?:src/main|src/test)/java/(?P<package>.+)/[^/]+\.java$"
)

LANGUAGE_ALIASES = {
    "java": "java",
    "spring": "spring",
    "typescript": "typescript",
    "ts": "typescript",
    "nestjs": "nestjs",
    "react": "react",
    "python": "python",
    "py": "python",
    "php": "php",
    "general": "general",
}

SUPPORTED_LANGUAGES = tuple(sorted(set(LANGUAGE_ALIASES.values())))
SUPPORTED_TEST_TYPES = {"unit", "integration", "both"}


class GenerationError(ValueError):
    """Raised when generation cannot continue."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class GeneratedScenario:
    description: str
    test_name: str


@dataclass
class GeneratedTestFile:
    language: str
    test_type: str
    output_path: str
    content: str
    scenarios: list[GeneratedScenario]
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def load_parser_module():
    """Load the sibling parser module without requiring package installation."""
    parser_path = Path(__file__).with_name("specs-task-tdd-parser.py")
    module_name = "specs_task_tdd_parser"
    spec = importlib.util.spec_from_file_location(module_name, parser_path)
    if spec is None or spec.loader is None:
        raise GenerationError(
            f"Unable to load parser module from {parser_path}.",
            code="E3",
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def normalize_language(language: str) -> str:
    canonical = LANGUAGE_ALIASES.get(language.strip().lower())
    if canonical is None:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        raise GenerationError(
            (
                f"Language '{language}' not supported. Supported languages: {supported}. "
                "Use 'general' for generic test structure or select a supported language."
            ),
            code="A2",
        )
    return canonical


def normalize_test_type(test_type: str) -> str:
    normalized = test_type.strip().lower()
    if normalized not in SUPPORTED_TEST_TYPES:
        supported = ", ".join(sorted(SUPPORTED_TEST_TYPES))
        raise GenerationError(
            f"Unsupported test type '{test_type}'. Supported values: {supported}.",
            code="E3",
        )
    return normalized


def derive_subject_name(task_data) -> str:
    raw_title = str(task_data.metadata.get("title") or task_data.title_heading)
    cleaned = CODE_LABEL_PATTERN.sub(r"\1", raw_title)
    cleaned = cleaned.lower()
    cleaned = NON_ALNUM_PATTERN.sub(" ", cleaned)

    ignored = {
        "task",
        "red",
        "phase",
        "tdd",
        "command",
        "implementation",
        "core",
        "logic",
        "generation",
        "test",
        "tests",
    }
    tokens = [token for token in cleaned.split() if token and token not in ignored]
    if not tokens:
        return "spec_behavior"
    return "_".join(tokens[:4])


def to_snake_case(value: str) -> str:
    collapsed = CAMEL_BOUNDARY_PATTERN.sub(r"\1_\2", value)
    collapsed = NON_ALNUM_PATTERN.sub("_", collapsed.lower()).strip("_")
    return collapsed or "scenario"


def to_pascal_case(value: str) -> str:
    parts = [part for part in NON_ALNUM_PATTERN.split(value) if part]
    if not parts:
        return "GeneratedSpec"
    return "".join(part.capitalize() for part in parts)


def normalize_java_package_path(raw_value: object) -> str | None:
    if not isinstance(raw_value, str):
        return None

    value = raw_value.strip().replace("\\", "/")
    if not value:
        return None

    source_match = JAVA_SOURCE_PATH_PATTERN.search(value)
    if source_match:
        value = source_match.group("package")
    elif value.endswith(".java"):
        parent = Path(value).parent.as_posix().strip("/")
        if parent:
            value = parent

    value = value.strip("/").replace(".", "/")
    segments = [segment for segment in value.split("/") if segment]
    if not segments:
        return None
    return "/".join(segments)


def clean_scenario_text(line: str) -> str:
    cleaned = CODE_LABEL_PATTERN.sub(r"\1", line)
    cleaned = cleaned.replace("Verify that", "").replace("Verify", "")
    cleaned = cleaned.strip(" .:")
    return cleaned or "scenario is covered"


def extract_scenarios(test_instructions: str, *, test_type: str) -> list[GeneratedScenario]:
    """Extract behavior-focused scenarios from checkbox items."""
    scenarios: list[GeneratedScenario] = []
    active_section = "both"

    for raw_line in test_instructions.splitlines():
        line = raw_line.rstrip()
        lowered = line.lower()
        if "mandatory unit tests" in lowered:
            active_section = "unit"
            continue
        if "mandatory integration tests" in lowered:
            active_section = "integration"
            continue
        if "edge cases" in lowered:
            active_section = "both"
            continue

        match = CHECKBOX_PATTERN.match(line)
        if not match:
            continue

        if test_type != "both" and active_section not in {test_type, "both"}:
            continue

        description = clean_scenario_text(match.group("text"))
        test_name = to_snake_case(description)
        scenarios.append(GeneratedScenario(description=description, test_name=test_name))

    if not scenarios:
        raise GenerationError(
            "Task file does not contain actionable Test Instructions for test generation.",
            code="A3",
        )

    return scenarios


def render_scenario_comment(scenario: GeneratedScenario) -> str:
    return f"RED: {scenario.description}"


def derive_java_test_metadata(task_data, subject_name: str) -> tuple[str, str | None]:
    metadata = getattr(task_data, "metadata", {}) or {}

    package_path = None
    for key in ("package", "source_package", "package_path", "source_path", "source_file"):
        package_path = normalize_java_package_path(metadata.get(key))
        if package_path:
            break

    class_name = None
    for key in ("source_class", "class_name"):
        raw_value = metadata.get(key)
        if isinstance(raw_value, str) and raw_value.strip():
            class_name = raw_value.strip()
            break

    if class_name is None:
        source_path = metadata.get("source_path") or metadata.get("source_file")
        if isinstance(source_path, str) and source_path.strip().endswith(".java"):
            class_name = Path(source_path.strip()).stem

    if class_name is None:
        class_name = to_pascal_case(subject_name)

    return f"{class_name}Test", package_path


def derive_php_test_class_name(task_data, subject_name: str) -> str:
    metadata = getattr(task_data, "metadata", {}) or {}

    for key in ("source_class", "class_name"):
        raw_value = metadata.get(key)
        if isinstance(raw_value, str) and raw_value.strip():
            return f"{raw_value.strip()}Test"

    for key in ("source_path", "source_file"):
        raw_value = metadata.get(key)
        if isinstance(raw_value, str):
            source_path = raw_value.strip()
            if source_path.endswith(".php"):
                return f"{Path(source_path).stem}Test"

    return f"{to_pascal_case(subject_name)}Test"


def build_output_path(language: str, subject_name: str, task_data=None) -> str:
    pascal = to_pascal_case(subject_name)
    if language == "java":
        class_name, package_path = derive_java_test_metadata(task_data, subject_name)
        prefix = f"src/test/java/{package_path}" if package_path else "src/test/java"
        return f"{prefix}/{class_name}.java"
    if language == "spring":
        class_name, package_path = derive_java_test_metadata(task_data, subject_name)
        prefix = f"src/test/java/{package_path}" if package_path else "src/test/java"
        return f"{prefix}/{class_name}.java"
    if language == "typescript":
        return f"__tests__/{subject_name}.spec.ts"
    if language == "nestjs":
        return f"src/{subject_name}.spec.ts"
    if language == "react":
        return f"src/__tests__/{subject_name}.test.tsx"
    if language == "python":
        return f"tests/test_{subject_name}.py"
    if language == "php":
        class_name = derive_php_test_class_name(task_data, subject_name)
        return f"tests/{class_name}.php"
    return f"tests/{subject_name}.red.md"


def render_general(subject_name: str, scenarios: list[GeneratedScenario], *, test_type: str) -> str:
    lines = [
        f"# RED Test Plan: {subject_name}",
        "",
        f"Test type: {test_type}",
        "",
        "These are intentionally failing behavior checks for the RED phase.",
        "",
    ]
    for scenario in scenarios:
        lines.extend(
            [
                f"## {scenario.test_name}",
                f"- Expectation: {scenario.description}",
                f"- Failure condition: {render_scenario_comment(scenario)}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def load_template(template_name: str) -> str:
    template_path = Path(__file__).with_name("test-templates") / template_name
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise GenerationError(
            f"Missing test template: {template_path}",
            code="E3",
        ) from exc


def render_template(template_name: str, replacements: dict[str, str]) -> str:
    template = load_template(template_name)

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return replacements.get(key, "")

    rendered = TEMPLATE_PLACEHOLDER_PATTERN.sub(replace, template)
    return rendered.rstrip() + "\n"


def render_java(
    task_data, subject_name: str, scenarios: list[GeneratedScenario], *, spring: bool
) -> str:
    class_name, package_path = derive_java_test_metadata(task_data, subject_name)
    methods = []
    for scenario in scenarios:
        methods.extend(
            [
                "    @Test",
                f'    @DisplayName("{scenario.description}")',
                f"    void {scenario.test_name}() {{",
                f'        Assertions.fail("{render_scenario_comment(scenario)}");',
                "    }",
                "",
            ]
        )

    template_name = "spring-test-template.java" if spring else "java-test-template.java"
    support_members = ""
    if spring:
        support_members = "\n".join(
            [
                "    @Autowired",
                "    private ApplicationContext applicationContext;",
                "",
            ]
        )

    return render_template(
        template_name,
        {
            "CLASS_NAME": class_name,
            "PACKAGE_DECLARATION": (
                f"package {package_path.replace('/', '.')};\n\n" if package_path else ""
            ),
            "SUPPORT_MEMBERS": support_members.rstrip(),
            "TEST_METHODS": "\n".join(methods).rstrip(),
        },
    )


def render_typescript(
    subject_name: str,
    scenarios: list[GeneratedScenario],
    *,
    nestjs: bool,
    react: bool,
) -> str:
    title = subject_name.replace("_", " ")
    lines: list[str] = []
    if nestjs:
        lines.extend(
            [
                "import { Test, TestingModule } from '@nestjs/testing';",
                "",
            ]
        )
    elif react:
        lines.extend(
            [
                "import React from 'react';",
                "import { render, screen, fireEvent } from '@testing-library/react';",
                "import userEvent from '@testing-library/user-event';",
                "",
            ]
        )

    lines.append(f"describe('{title}', () => {{")
    if nestjs:
        lines.extend(
            [
                "  let moduleRef: TestingModule;",
                "",
                "  beforeEach(async () => {",
                "    moduleRef = await Test.createTestingModule({",
                "      providers: [],",
                "      controllers: [],",
                "    }).compile();",
                "  });",
                "",
            ]
        )

    for scenario in scenarios:
        lines.extend(
            [
                f"  test('{scenario.description}', () => {{",
            ]
        )
        if react:
            lines.extend(
                [
                    "    render(<div />);",
                    "    // RTL queries: screen.getByRole('button'), screen.getByText('label'), screen.queryByRole('heading')",
                    "    // Interaction: await userEvent.click(element) or fireEvent.click(element)",
                    "    expect(true).toBe(false);",
                ]
            )
        else:
            lines.append("    expect(true).toBe(false);")
        lines.extend(
            [
                f"    // {render_scenario_comment(scenario)}",
                "  });",
                "",
            ]
        )

    lines.append("});")
    return "\n".join(lines).rstrip() + "\n"


def render_python(scenarios: list[GeneratedScenario]) -> str:
    lines: list[str] = [
        "# pytest fixtures: use @pytest.fixture for setup/teardown if needed",
        "",
    ]
    for scenario in scenarios:
        lines.extend(
            [
                f"def test_{scenario.test_name}():",
                f"    assert False, {repr(render_scenario_comment(scenario))}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_php(task_data, subject_name: str, scenarios: list[GeneratedScenario]) -> str:
    class_name = derive_php_test_class_name(task_data, subject_name)
    methods = []
    for scenario in scenarios:
        methods.extend(
            [
                f"    public function test{to_pascal_case(scenario.test_name)}(): void",
                "    {",
                f"        $this->fail('{render_scenario_comment(scenario)}');",
                "    }",
                "",
            ]
        )

    return render_template(
        "php-test-template.php",
        {
            "CLASS_NAME": class_name,
            "TEST_METHODS": "\n".join(methods).rstrip(),
        },
    )


def render_test_content(
    language: str, subject_name: str, scenarios: list[GeneratedScenario], *, test_type: str
) -> str:
    if language == "general":
        return render_general(subject_name, scenarios, test_type=test_type)
    if language == "java":
        return render_java(
            task_data=None, subject_name=subject_name, scenarios=scenarios, spring=False
        )
    if language == "spring":
        return render_java(
            task_data=None, subject_name=subject_name, scenarios=scenarios, spring=True
        )
    if language == "typescript":
        return render_typescript(subject_name, scenarios, nestjs=False, react=False)
    if language == "nestjs":
        return render_typescript(subject_name, scenarios, nestjs=True, react=False)
    if language == "react":
        return render_typescript(subject_name, scenarios, nestjs=False, react=True)
    if language == "python":
        return render_python(scenarios)
    if language == "php":
        return render_php(None, subject_name, scenarios)
    raise GenerationError(f"No renderer registered for language '{language}'.", code="A2")


def generate_test_file(
    task_data, *, language: str | None = None, test_type: str = "both"
) -> GeneratedTestFile:
    """Generate a RED-phase test skeleton from parsed task data."""
    canonical_language = normalize_language(language or str(task_data.metadata["lang"]))
    normalized_test_type = normalize_test_type(test_type)

    if not getattr(task_data, "test_instructions", None):
        raise GenerationError(
            "Task file does not contain Test Instructions section.",
            code="A3",
        )

    scenarios = extract_scenarios(task_data.test_instructions, test_type=normalized_test_type)
    subject_name = derive_subject_name(task_data)
    output_path = build_output_path(canonical_language, subject_name, task_data)
    if canonical_language == "java":
        content = render_java(task_data, subject_name, scenarios, spring=False)
    elif canonical_language == "spring":
        content = render_java(task_data, subject_name, scenarios, spring=True)
    elif canonical_language == "php":
        content = render_php(task_data, subject_name, scenarios)
    else:
        content = render_test_content(
            canonical_language,
            subject_name,
            scenarios,
            test_type=normalized_test_type,
        )

    warnings = []
    if canonical_language == "general":
        warnings.append(
            "General mode generates a portable RED-phase plan instead of runnable code."
        )

    return GeneratedTestFile(
        language=canonical_language,
        test_type=normalized_test_type,
        output_path=output_path,
        content=content,
        scenarios=scenarios,
        warnings=warnings,
    )


def generate_from_task_file(
    task_path: str, *, language: str | None = None, test_type: str = "both"
) -> GeneratedTestFile:
    parser_module = load_parser_module()
    try:
        task_data = parser_module.parse_task_file(task_path)
    except parser_module.TaskFileError as exc:
        raise GenerationError(str(exc), code=exc.code) from exc

    return generate_test_file(task_data, language=language, test_type=test_type)


def write_generated_test_file(generated: GeneratedTestFile, *, output_root: str = ".") -> Path:
    destination = Path(output_root) / generated.output_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.write_text(generated.content, encoding="utf-8")
    except PermissionError as exc:
        raise GenerationError(
            f"Permission denied: Cannot create test file at {destination}",
            code="E4",
        ) from exc
    return destination


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate RED-phase tests from a spec task file.")
    parser.add_argument("--task", required=True, help="Path to the task markdown file.")
    parser.add_argument("--lang", help="Override language from task frontmatter.")
    parser.add_argument(
        "--test-type",
        default="both",
        help="unit, integration, or both (default: both).",
    )
    parser.add_argument(
        "--output-root",
        default=".",
        help="Base directory used when writing generated test files.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the generated file to disk instead of printing JSON only.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        generated = generate_from_task_file(
            args.task,
            language=args.lang,
            test_type=args.test_type,
        )
        payload = asdict(generated)
        if args.write:
            payload["written_to"] = str(
                write_generated_test_file(generated, output_root=args.output_root)
            )
    except GenerationError as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}, indent=2))
        return 1

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
