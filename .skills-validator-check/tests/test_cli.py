"""Tests for CLI module."""

import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.cli import ValidationCLI, main
from validators.reporter import ConsoleReporter, JsonReporter
from validators.models import Severity


class TestValidationCLI:
    """Tests for ValidationCLI class."""

    @pytest.fixture
    def cli(self):
        return ValidationCLI()

    def test_cli_creation(self, cli):
        """Test CLI can be created."""
        assert cli is not None
        assert cli.repo_root is not None

    def test_filter_component_files(self, cli, tmp_path):
        """Test filtering component files."""
        # Create test files
        skill_path = tmp_path / "skills" / "test" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.touch()

        readme_path = tmp_path / "README.md"
        readme_path.touch()

        files = [skill_path, readme_path]
        filtered = cli._filter_component_files(files)

        assert skill_path in filtered
        assert readme_path not in filtered

    def test_run_with_no_files(self, cli):
        """Test CLI with no staged files."""
        with patch.object(cli, '_get_staged_files', return_value=[]):
            exit_code = cli.run([])
            assert exit_code == 0

    def test_run_with_specific_files(self, cli, tmp_path):
        """Test CLI with specific files argument."""
        # Create a valid skill with new structure
        skill_dir = tmp_path / "skills" / "sample-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: sample-skill
description: Test skill that helps when testing features. Use when testing new functionality.
allowed-tools: Read, Write, Bash
---

# Test Skill

## Overview

This is a test skill for CLI testing.

## When to Use

Use this skill when testing the CLI.

## Instructions

1. Run the test
2. Verify the result

## Examples

### Example 1

```python
print("test")
```

## Best Practices

Follow test-driven development.

## Constraints and Warnings

This is a test skill with no real constraints.
""")

        exit_code = cli.run(["--files", str(skill_file)])
        assert exit_code == 0

    def test_run_with_specific_skill_expands_bundled_markdown(self, cli, tmp_path):
        """Test CLI validates bundled markdown when only SKILL.md is passed."""
        skill_dir = tmp_path / "skills" / "sample-skill"
        references_dir = skill_dir / "references"
        references_dir.mkdir(parents=True)

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: sample-skill
description: Test skill that helps when testing features. Use when testing new functionality.
allowed-tools: Read
---

# Test Skill

## Overview

See [Examples](references/example-doc.md).

## When to Use

Use this skill when testing the CLI.

## Instructions

1. Run the test

## Examples

```python
print("test")
```
""")

        bundled_md = references_dir / "example-doc.md"
        bundled_md.write_text("##Invalid Heading\n")

        exit_code = cli.run(["--files", str(skill_file)])
        assert exit_code == 1

    def test_run_with_invalid_file(self, cli, tmp_path):
        """Test CLI with invalid file reports errors."""
        # Create an invalid skill (invalid name format)
        skill_dir = tmp_path / "skills" / "test"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: Invalid_Name
description: Test skill that helps when testing features. Use when testing new functionality.
allowed-tools: Read, Write, Bash
---

# Test Skill

## Overview

This is a test skill.

## When to Use

Use this skill.

## Instructions

Step 1: Test.

## Examples

### Example 1

```python
print("test")
```
""")

        exit_code = cli.run(["--files", str(skill_file)])
        assert exit_code == 1  # Should fail due to errors

    def test_run_with_json_format(self, cli, tmp_path, capsys):
        """Test CLI with JSON output format."""
        skill_dir = tmp_path / "skills" / "test"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: Test skill that helps when testing. Use when testing JSON output format.
allowed-tools: Read, Write
---

# Test Skill

## Overview

This is a test skill for JSON format testing.

## When to Use

Use when testing JSON output.

## Instructions

1. Run command
2. Check output

## Examples

### Example 1

```json
{"test": true}
```
""")

        exit_code = cli.run(["--files", str(skill_file), "--format", "json"])

        captured = capsys.readouterr()
        assert '"results"' in captured.out
        assert '"summary"' in captured.out

    def test_run_all_flag(self, cli, tmp_path):
        """Test CLI with --all flag."""
        # Mock find_all_component_files
        skill_dir = tmp_path / "skills" / "sample-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: sample-skill
description: Test skill that helps when testing. Use when testing the --all flag.
allowed-tools: Read
---

# Test Skill

## Overview

Test skill for --all flag testing.

## When to Use

Use when testing --all flag.

## Instructions

Run validation on all files.

## Examples

### Example 1

```bash
python -m pytest
```
""")

        with patch.object(cli, '_find_all_component_files', return_value=[skill_file]):
            exit_code = cli.run(["--all"])
            assert exit_code == 0

    def test_run_skips_external_url_check_by_default(self, cli, tmp_path):
        """Test CLI skips remote checks for external HTTP(S) links by default."""
        skill_dir = tmp_path / "skills" / "sample-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: sample-skill
description: Test skill that helps when testing URL checks. Use when testing CLI flags.
allowed-tools: Read
---

# Test Skill

## Overview

See [Remote Doc](https://example.com/missing).

## When to Use

Use this skill when testing the CLI.

## Instructions

1. Run the test

## Examples

```text
ok
```
""")

        with patch("validators.validators.urlopen", side_effect=AssertionError("urlopen should not be called")):
            exit_code = cli.run(["--files", str(skill_file)])

        assert exit_code == 0

    def test_run_with_check_external_urls(self, cli, tmp_path):
        """Test CLI can enable remote checks for external HTTP(S) links explicitly."""
        skill_dir = tmp_path / "skills" / "sample-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: sample-skill
description: Test skill that helps when testing URL checks. Use when testing CLI flags.
allowed-tools: Read
---

# Test Skill

## Overview

See [Remote Doc](https://example.com/missing).

## When to Use

Use this skill when testing the CLI.

## Instructions

1. Run the test

## Examples

```text
ok
```
""")

        from urllib.error import HTTPError

        with patch(
            "validators.validators.urlopen",
            side_effect=HTTPError(
                "https://example.com/missing",
                404,
                "Not Found",
                hdrs=None,
                fp=None,
            ),
        ):
            exit_code = cli.run(["--files", str(skill_file), "--check-external-urls"])

        assert exit_code == 1


class TestConsoleReporter:
    """Tests for ConsoleReporter."""

    def test_reporter_creation(self):
        """Test reporter can be created."""
        reporter = ConsoleReporter()
        assert reporter is not None

    def test_reporter_no_colors(self):
        """Test reporter with colors disabled."""
        reporter = ConsoleReporter(use_colors=False)
        colored = reporter._color("\033[91m", "test")
        assert "\033[91m" not in colored

    def test_reporter_verbose_mode(self):
        """Test reporter in verbose mode."""
        reporter = ConsoleReporter(verbose=True)
        assert reporter.verbose is True

    def test_reporter_ascii_fallback_symbols(self):
        """Test reporter falls back to ASCII-safe symbols when stdout is ASCII-only."""
        reporter = ConsoleReporter(use_colors=False)
        reporter.supports_unicode = False

        assert reporter._success_symbol() == "v"
        assert reporter._symbol(Severity.ERROR) == "x"
        assert reporter._arrow() == "->"
        assert reporter._separator() == "-" * 60


class TestJsonReporter:
    """Tests for JsonReporter."""

    def test_reporter_creation(self):
        """Test JSON reporter can be created."""
        reporter = JsonReporter()
        assert reporter is not None

    def test_reporter_output(self, capsys):
        """Test JSON reporter output format."""
        from validators.models import ValidationResult

        reporter = JsonReporter()
        results = [
            ValidationResult(
                file_path=Path("test.md"),
                component_type="skill"
            )
        ]

        reporter.report(results)

        captured = capsys.readouterr()
        import json
        output = json.loads(captured.out)

        assert "summary" in output
        assert "results" in output
        assert output["summary"]["total_files"] == 1


class TestMain:
    """Tests for main entry point."""

    def test_main_function_exists(self):
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_returns_int(self):
        """Test main returns an integer."""
        with patch.object(ValidationCLI, 'run', return_value=0):
            result = main()
            assert isinstance(result, int)
