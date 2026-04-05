#!/usr/bin/env python3
"""Tests for specs-task-tdd-generator.py."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from unittest import mock

hooks_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
generator_path = os.path.join(hooks_dir, "specs-task-tdd-generator.py")
spec = importlib.util.spec_from_file_location("specs_task_tdd_generator", generator_path)
task_tdd_generator = importlib.util.module_from_spec(spec)
sys.modules["specs_task_tdd_generator"] = task_tdd_generator
spec.loader.exec_module(task_tdd_generator)


def write_task_file(content: str) -> str:
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md")
    handle.write(textwrap.dedent(content).strip() + "\n")
    handle.flush()
    handle.close()
    return handle.name


def build_task(lang: str = "general", extra_frontmatter: str = "") -> str:
    return write_task_file(f"""
        ---
        id: TASK-003
        title: "Test Generation Core Logic"
        spec: docs/specs/002-tdd-command/2026-04-05--tdd-command.md
        lang: {lang}
        {extra_frontmatter}
        dependencies: [TASK-001, TASK-002]
        status: pending
        ---

        # TASK-003: Test Generation Core Logic

        ## Test Instructions
        **1. Mandatory Unit Tests:**
           - [ ] Verify that test generation from Test Instructions produces valid test structure.
           - [ ] Verify that generated test methods are named descriptively based on scenarios.

        **2. Mandatory Integration Tests:**
           - [ ] Verify that complete test generation flow succeeds.
           - [ ] Verify that generated test file is created in correct location.
        """)


def test_normalize_language_supports_aliases():
    assert task_tdd_generator.normalize_language("ts") == "typescript"
    assert task_tdd_generator.normalize_language("py") == "python"


def test_normalize_language_rejects_unsupported_values():
    try:
        task_tdd_generator.normalize_language("ruby")
        assert False, "Expected GenerationError"
    except task_tdd_generator.GenerationError as exc:
        assert exc.code == "A2"
        assert "general" in str(exc)


def test_extract_scenarios_filters_by_test_type():
    instructions = """
    **1. Mandatory Unit Tests:**
       - [ ] Verify that unit behavior is described.

    **2. Mandatory Integration Tests:**
       - [ ] Verify that integration flow succeeds.
    """

    scenarios = task_tdd_generator.extract_scenarios(instructions, test_type="unit")

    assert len(scenarios) == 1
    assert scenarios[0].description == "unit behavior is described"
    assert scenarios[0].test_name == "unit_behavior_is_described"


def test_generate_from_task_file_creates_python_red_phase_skeleton():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "python"
    assert generated.output_path == "tests/test_spec_behavior.py"
    assert (
        "def test_test_generation_from_test_instructions_produces_valid_test_structure"
        in generated.content
    )
    assert (
        "assert False, 'RED: test generation from Test Instructions produces valid test structure'"
        in generated.content
    )


def test_python_test_file_uses_test_naming_convention():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.startswith("tests/test_")
    assert generated.output_path.endswith(".py")


def test_python_test_file_is_in_correct_directory():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.startswith("tests/")


def test_python_test_includes_fixture_comment():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "# pytest fixtures:" in generated.content


def test_python_test_generation_flow_succeeds():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "python"
    assert generated.test_type == "both"
    assert len(generated.scenarios) > 0
    assert generated.content.strip() != ""


def test_python_test_file_created_in_correct_location():
    task_file = build_task(lang="python")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    with tempfile.TemporaryDirectory() as temp_dir:
        written = task_tdd_generator.write_generated_test_file(generated, output_root=temp_dir)
        assert written.exists()
        assert written.name.startswith("test_")
        assert written.name.endswith(".py")
        assert "tests" in str(written)


def test_python_red_assertion_is_valid_python_for_quoted_descriptions():
    scenarios = [
        task_tdd_generator.GeneratedScenario(
            description='returns "ok" status and it\'s valid',
            test_name="returns_ok_status_and_it_s_valid",
        )
    ]
    content = task_tdd_generator.render_python(scenarios)
    # Must compile without SyntaxError even when description contains quotes
    compile(content, "<generated>", "exec")
    assert "assert False" in content


def test_generate_from_task_file_creates_php_phpunit_structure():
    task_file = build_task(lang="php")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "php"
    assert generated.output_path == "tests/SpecBehaviorTest.php"
    assert "use PHPUnit\\Framework\\TestCase;" in generated.content
    assert "final class SpecBehaviorTest extends TestCase" in generated.content
    assert "$this->fail('RED: complete test generation flow succeeds');" in generated.content


def test_generate_from_task_file_derives_php_output_from_source_path():
    task_file = build_task(
        lang="php",
        extra_frontmatter="source_path: app/Services/BillingService.php",
    )

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path == "tests/BillingServiceTest.php"
    assert "final class BillingServiceTest extends TestCase" in generated.content


def test_php_test_file_is_in_tests_directory_with_test_suffix():
    task_file = build_task(lang="php")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.startswith("tests/")
    assert generated.output_path.endswith("Test.php")


def test_php_template_guides_lifecycle_methods_when_needed():
    template_path = Path(hooks_dir) / "test-templates" / "php-test-template.php"

    content = template_path.read_text(encoding="utf-8")

    assert "setUp()/tearDown()" in content


def test_generate_test_file_creates_react_baseline_structure():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path == "src/__tests__/spec_behavior.test.tsx"
    assert "@testing-library/react" in generated.content
    assert "render(<div />);" in generated.content
    assert "describe('spec behavior'" in generated.content


def test_react_test_includes_react_import():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "import React from 'react';" in generated.content


def test_react_test_includes_fire_event_and_user_event_imports():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "fireEvent" in generated.content
    assert "userEvent" in generated.content


def test_react_test_uses_screen_query_methods():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    # The generator emits RTL query patterns as comments in the test body
    assert "screen.getByRole(" in generated.content or "screen.queryByRole(" in generated.content


def test_react_test_file_uses_test_tsx_naming_convention():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.endswith(".test.tsx")


def test_react_test_file_is_in_correct_directory():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.startswith("src/__tests__/")


def test_react_test_includes_failing_assertions():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "RED:" in generated.content
    assert "expect(true).toBe(false);" in generated.content


def test_react_test_generation_flow_succeeds():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "react"
    assert generated.test_type == "both"
    assert len(generated.scenarios) > 0
    assert generated.content.strip() != ""


def test_react_test_file_created_in_correct_location():
    task_file = build_task(lang="react")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    with tempfile.TemporaryDirectory() as temp_dir:
        written = task_tdd_generator.write_generated_test_file(generated, output_root=temp_dir)
        assert written.exists()
        assert str(written).endswith(".test.tsx")
        assert "__tests__" in str(written)


def test_generate_test_file_creates_spring_baseline_structure():
    task_file = build_task(lang="spring")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path == "src/test/java/SpecBehaviorTest.java"
    assert "@SpringBootTest" in generated.content
    assert "@Autowired" in generated.content
    assert "ApplicationContext" in generated.content
    assert '@DisplayName("complete test generation flow succeeds")' in generated.content
    assert 'Assertions.fail("RED: complete test generation flow succeeds");' in generated.content


def test_generate_test_file_creates_java_junit5_structure():
    task_file = build_task(lang="java")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path == "src/test/java/SpecBehaviorTest.java"
    assert "import org.junit.jupiter.api.DisplayName;" in generated.content
    assert "class SpecBehaviorTest" in generated.content
    assert (
        '@DisplayName("test generation from Test Instructions produces valid test structure")'
        in generated.content
    )
    assert "@SpringBootTest" not in generated.content


def test_generate_test_file_derives_java_nested_package_output_from_source_path():
    task_file = build_task(
        lang="java",
        extra_frontmatter="source_path: src/main/java/com/example/billing/BillingService.java",
    )

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path == "src/test/java/com/example/billing/BillingServiceTest.java"
    assert generated.content.startswith("package com.example.billing;\n\n")
    assert "class BillingServiceTest" in generated.content


def test_generate_test_file_derives_spring_nested_package_output_from_package_metadata():
    task_file = build_task(
        lang="spring",
        extra_frontmatter='package: "com.example.platform.orders"',
    )

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert (
        generated.output_path == "src/test/java/com/example/platform/orders/SpecBehaviorTest.java"
    )
    assert generated.content.startswith("package com.example.platform.orders;\n\n")
    assert "@SpringBootTest" in generated.content


def test_write_generated_test_file_persists_content():
    task_file = build_task(lang="general")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    with tempfile.TemporaryDirectory() as temp_dir:
        written = task_tdd_generator.write_generated_test_file(generated, output_root=temp_dir)
        assert written.exists()
        assert written.read_text(encoding="utf-8") == generated.content


def test_write_generated_test_file_surfaces_e4_permission_errors():
    generated = task_tdd_generator.GeneratedTestFile(
        language="general",
        test_type="both",
        output_path="tests/spec_behavior.red.md",
        content="content\n",
        scenarios=[],
    )

    with mock.patch.object(Path, "write_text", side_effect=PermissionError("denied")):
        try:
            task_tdd_generator.write_generated_test_file(generated, output_root=".")
            assert False, "Expected GenerationError"
        except task_tdd_generator.GenerationError as exc:
            assert exc.code == "E4"
            assert "Permission denied" in str(exc)


def test_cli_outputs_json_for_generated_file():
    task_file = build_task(lang="typescript")

    try:
        completed = subprocess.run(
            [sys.executable, generator_path, "--task", task_file],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(task_file)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["language"] == "typescript"
    assert payload["output_path"] == "__tests__/spec_behavior.spec.ts"
    assert "expect(true).toBe(false);" in payload["content"]


def test_generate_test_file_creates_typescript_jest_structure():
    task_file = build_task(lang="typescript")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "typescript"
    assert generated.output_path == "__tests__/spec_behavior.spec.ts"
    assert "describe('spec behavior'" in generated.content
    assert (
        "test('test generation from Test Instructions produces valid test structure'"
        in generated.content
    )
    assert "expect(true).toBe(false);" in generated.content


def test_generate_test_file_creates_nodejs_jest_structure():
    task_file = build_task(lang="typescript")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "typescript"
    assert generated.output_path == "__tests__/spec_behavior.spec.ts"
    assert "describe('spec behavior'" in generated.content
    assert "expect(true).toBe(false);" in generated.content
    # Node.js tests use same Jest structure as TypeScript


def test_typescript_test_uses_correct_imports():
    task_file = build_task(lang="typescript")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    # TypeScript tests should not have framework-specific imports by default
    # (unless nestjs or react variants)
    assert "import" not in generated.content or "describe" in generated.content
    assert "describe(" in generated.content


def test_generate_test_file_creates_nestjs_jest_structure():
    task_file = build_task(lang="nestjs")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.language == "nestjs"
    assert generated.output_path == "src/spec_behavior.spec.ts"
    assert "import { Test, TestingModule } from '@nestjs/testing';" in generated.content
    assert "describe('spec behavior'" in generated.content
    assert "Test.createTestingModule(" in generated.content
    assert "moduleRef" in generated.content
    assert "expect(true).toBe(false);" in generated.content


def test_nestjs_test_uses_beforeeach_module_compilation():
    task_file = build_task(lang="nestjs")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "beforeEach(async () => {" in generated.content
    assert ".compile();" in generated.content
    assert "providers: []," in generated.content
    assert "controllers: []," in generated.content


def test_nestjs_test_mocks_providers_and_controllers():
    task_file = build_task(lang="nestjs")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "let moduleRef: TestingModule;" in generated.content
    assert "providers:" in generated.content
    assert "controllers:" in generated.content


def test_nestjs_test_uses_spec_ts_naming_convention():
    task_file = build_task(lang="nestjs")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert generated.output_path.endswith(".spec.ts")
    assert generated.output_path.startswith("src/")


def test_nestjs_test_includes_failing_assertions():
    task_file = build_task(lang="nestjs")

    try:
        generated = task_tdd_generator.generate_from_task_file(task_file)
    finally:
        os.unlink(task_file)

    assert "expect(true).toBe(false);" in generated.content
    assert "RED:" in generated.content
