"""Pytest fixtures for validator tests."""

import pytest
from pathlib import Path
from typing import Callable


@pytest.fixture
def temp_skill_file(tmp_path: Path) -> Callable[[str], Path]:
    """Create a temporary skill file with given content."""
    def _create(content: str, skill_name: str = "test-skill") -> Path:
        skill_dir = tmp_path / "skills" / skill_name
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(content)
        return skill_file
    return _create


@pytest.fixture
def temp_agent_file(tmp_path: Path) -> Callable[[str], Path]:
    """Create a temporary agent file with given content."""
    def _create(content: str, agent_name: str = "test-agent") -> Path:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / f"{agent_name}.md"
        agent_file.write_text(content)
        return agent_file
    return _create


@pytest.fixture
def temp_command_file(tmp_path: Path) -> Callable[[str], Path]:
    """Create a temporary command file with given content."""
    def _create(content: str, command_name: str = "test-command") -> Path:
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        command_file = commands_dir / f"{command_name}.md"
        command_file.write_text(content)
        return command_file
    return _create


@pytest.fixture
def valid_skill_content() -> str:
    """Return valid skill content with all required sections."""
    return """---
name: test-skill
description: Validates files when committing code changes. Use when ensuring code quality.
allowed-tools: Read, Grep, Glob
---

# Test Skill

## Overview

This skill validates files during the commit process to ensure code quality standards are met.

## When to Use

Use this skill when:
- Preparing code for commit
- Running pre-commit hooks
- Validating code changes

## Instructions

1. Review the file changes
2. Run validation checks
3. Report any issues found

## Examples

### Input Example

```python
# Files to validate
files = ["src/main.py", "tests/test_main.py"]
```

### Output Example

```json
{
  "valid": true,
  "issues": []
}
```

## Best Practices

- Run validation before every commit
- Fix issues before proceeding
- Document any exceptions

## Constraints and Warnings

- Does not modify files automatically
- Requires Read access to all project files
"""


@pytest.fixture
def valid_agent_content() -> str:
    """Return valid agent content with all required sections."""
    return """---
name: valid-agent
description: Expert agent that helps with testing. Use PROACTIVELY when writing tests.
tools: Read, Grep, Glob
model: sonnet
---

## Role

You are an expert testing agent specializing in test automation.

## Process

1. Analyze the codebase for test coverage
2. Generate comprehensive tests
3. Validate test quality

## Guidelines

- Follow testing best practices
- Ensure high coverage
- Use descriptive test names
"""


@pytest.fixture
def temp_rule_file(tmp_path: Path) -> Callable[[str], Path]:
    """Create a temporary rule file with given content."""
    def _create(content: str, rule_name: str = "naming-conventions") -> Path:
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_file = rules_dir / f"{rule_name}.md"
        rule_file.write_text(content)
        return rule_file
    return _create


@pytest.fixture
def valid_rule_content() -> str:
    """Return valid rule content with all required and recommended sections."""
    return """---
globs: "**/*.java"
---
# Rule: Java Naming Conventions

## Context
Standardize naming across Java projects.

## Guidelines

### Classes
- Use PascalCase for class names

### Methods
- Use camelCase for method names

## Examples

### ✅ Good
```java
public class OrderService {
    public Order findById(Long id) { }
}
```

### ❌ Bad
```java
public class order_service {
    public Order GetById(Long id) { }
}
```
"""


@pytest.fixture
def valid_command_content() -> str:
    """Return valid command content with all required sections."""
    return """---
description: Run tests and report results when code changes. Use when running tests.
argument-hint: [test-pattern]
allowed-tools: Bash, Read
model: inherit
---

## Overview

This command runs tests matching a pattern and reports results.

## Usage

Run the command with a test pattern to execute specific tests.

## Arguments

- `test-pattern`: Pattern to match test files

## Examples

```bash
/test-command unit
```
"""
