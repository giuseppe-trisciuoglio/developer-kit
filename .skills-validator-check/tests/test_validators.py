"""Tests for validator classes."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.validators import (
    SkillValidator,
    AgentValidator,
    CommandValidator,
    ValidatorFactory,
)
from validators.models import Severity


class TestSkillValidator:
    """Tests for SkillValidator."""

    @pytest.fixture
    def validator(self):
        return SkillValidator()

    def test_can_validate_skill_file(self, validator):
        """Test validator recognizes skill files."""
        assert validator.can_validate(Path("skills/test/SKILL.md"))
        assert validator.can_validate(Path("path/skills/spring-boot/SKILL.md"))

    def test_cannot_validate_non_skill(self, validator):
        """Test validator rejects non-skill files."""
        assert not validator.can_validate(Path("agents/test.md"))
        assert not validator.can_validate(Path("skills/README.md"))

    def test_valid_skill_passes(self, validator, temp_skill_file, valid_skill_content):
        """Test that a valid skill with all required sections passes validation."""
        skill_file = temp_skill_file(valid_skill_content)
        result = validator.validate(skill_file)

        assert result.is_valid, f"Errors: {[str(e) for e in result.errors]}"
        assert len(result.errors) == 0

    def test_missing_name_fails(self, validator, temp_skill_file):
        """Test missing name field is reported as error."""
        content = """---
description: Some description with use case
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any(i.field_name == "name" and i.severity == Severity.ERROR
                   for i in result.issues)

    def test_missing_description_fails(self, validator, temp_skill_file):
        """Test missing description field is reported as error."""
        content = """---
name: test-skill
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any(i.field_name == "description" and i.severity == Severity.ERROR
                   for i in result.issues)

    def test_invalid_name_format(self, validator, temp_skill_file):
        """Test non-kebab-case names are rejected."""
        content = """---
name: Invalid_Skill_Name
description: Some description when using this skill
allowed-tools: Read
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        error = next((i for i in result.issues if i.field_name == "name"), None)
        assert error is not None
        assert "kebab-case" in error.suggestion.lower()

    def test_reserved_word_as_name(self, validator, temp_skill_file):
        """Test reserved words are rejected as names."""
        content = """---
name: help
description: Some description when needed
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("reserved" in i.message.lower() for i in result.issues)

    def test_name_too_long(self, validator, temp_skill_file):
        """Test overly long names are rejected."""
        long_name = "a" + "-b" * 40  # Over 64 characters
        content = f"""---
name: {long_name}
description: Some description when using this
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("too long" in i.message.lower() for i in result.issues)

    def test_invalid_yaml_syntax(self, validator, temp_skill_file):
        """Test invalid YAML is reported."""
        content = """---
name: test-skill
description: [invalid yaml
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("yaml" in i.message.lower() for i in result.issues)

    def test_missing_frontmatter(self, validator, temp_skill_file):
        """Test missing frontmatter is reported."""
        content = """# No Frontmatter

This skill has no frontmatter.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("frontmatter" in i.message.lower() for i in result.issues)

    def test_unclosed_frontmatter(self, validator, temp_skill_file):
        """Test unclosed frontmatter is reported."""
        content = """---
name: test-skill
description: Missing closing delimiter
# No closing ---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid

    def test_invalid_version_format_warning(self, validator, temp_skill_file):
        """Test invalid version format generates warning."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
version: 1.0
---

# Test Skill

## Overview

Overview content.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert result.is_valid  # Warnings don't fail validation
        assert any(i.field_name == "version" and i.severity == Severity.WARNING
                   for i in result.issues)

    def test_unknown_field_warning(self, validator, temp_skill_file):
        """Test unknown fields generate warnings."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
unknown_field: value
---

# Test Skill

## Overview

Overview content.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert result.is_valid  # Warnings don't fail validation
        assert any("unknown" in i.message.lower() and i.severity == Severity.WARNING
                   for i in result.issues)

    def test_prohibited_file_error(self, validator, temp_skill_file):
        """Test prohibited files in skill directory are reported."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---
"""
        skill_file = temp_skill_file(content)
        # Create prohibited README.md
        (skill_file.parent / "README.md").write_text("# README")

        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("README.md" in i.message for i in result.issues)

    def test_description_quality_warning(self, validator, temp_skill_file):
        """Test description without WHAT/WHEN generates warning."""
        content = """---
name: test-skill
description: A simple skill
allowed-tools: Read
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        # Should have warning about missing WHEN/WHAT
        assert any(i.severity == Severity.WARNING and "description" in str(i).lower()
                   for i in result.issues)

    @pytest.mark.parametrize("name,expected_valid", [
        ("valid-skill", True),
        ("skill-123", True),
        ("a-b-c", True),
        ("Invalid", False),
        ("invalid_skill", False),
        ("invalid skill", False),
        ("-invalid", False),
        ("invalid-", False),
        ("123-skill", False),
    ])
    def test_name_format_cases(self, validator, temp_skill_file, name, expected_valid):
        """Test various name format cases."""
        content = f"""---
name: {name}
description: Some description when using this skill
allowed-tools: Read
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        name_errors = [i for i in result.issues
                       if i.field_name == "name" and i.severity == Severity.ERROR]
        has_name_error = len(name_errors) > 0

        if expected_valid:
            assert not has_name_error, f"Expected '{name}' to be valid"
        else:
            assert has_name_error, f"Expected '{name}' to be invalid"

    def test_missing_allowed_tools_fails(self, validator, temp_skill_file):
        """Test missing allowed-tools field is reported as error."""
        content = """---
name: test-skill
description: Some description when using this skill
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any(i.field_name == "allowed-tools" and i.severity == Severity.ERROR
                   for i in result.issues)

    @pytest.mark.parametrize("prohibited_field", ["language", "framework", "license"])
    def test_prohibited_fields_fail(self, validator, temp_skill_file, prohibited_field):
        """Test prohibited fields are rejected."""
        content = f"""---
name: test-skill
description: Some description when using this skill
allowed-tools: Read, Write
{prohibited_field}: python3
---
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any(i.field_name == prohibited_field and i.severity == Severity.ERROR
                   for i in result.issues)

    def test_missing_overview_section_fails(self, validator, temp_skill_file):
        """Test missing Overview section is reported as error."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## When to Use

Use this skill when needed.

## Instructions

Step 1: Do something.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("Overview" in i.message for i in result.issues)

    def test_missing_when_to_use_section_fails(self, validator, temp_skill_file):
        """Test missing When to Use section is reported as error."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

This is an overview.

## Instructions

Step 1: Do something.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("When to Use" in i.message for i in result.issues)

    def test_missing_instructions_section_fails(self, validator, temp_skill_file):
        """Test missing Instructions section is reported as error."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

This is an overview.

## When to Use

Use this skill.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("Instructions" in i.message for i in result.issues)

    def test_missing_examples_section_fails(self, validator, temp_skill_file):
        """Test missing Examples section is reported as error."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

This is an overview.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert not result.is_valid
        assert any("Examples" in i.message for i in result.issues)

    def test_missing_best_practices_warns(self, validator, temp_skill_file):
        """Test missing Best Practices section generates warning."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

This is an overview.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.

## Examples

Example content.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert result.is_valid  # Warnings don't fail
        assert any(i.severity == Severity.WARNING and "Best Practices" in i.message
                   for i in result.issues)

    def test_missing_constraints_warnings_warns(self, validator, temp_skill_file):
        """Test missing Constraints and Warnings section generates warning."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

This is an overview.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.

## Examples

Example content.

## Best Practices

Some best practices.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert result.is_valid  # Warnings don't fail
        assert any(i.severity == Severity.WARNING and "Constraints" in i.message
                   for i in result.issues)

    def test_io_examples_warning(self, validator, temp_skill_file):
        """Test missing I/O examples in Examples section generates warning."""
        content = """---
name: test-skill
description: Some description when using this skill
allowed-tools: Read
---

# Test Skill

## Overview

Overview content.

## When to Use

Use this skill.

## Instructions

Step 1: Do something.

## Examples

Example content without code blocks.
"""
        skill_file = temp_skill_file(content)
        result = validator.validate(skill_file)

        assert any(i.severity == Severity.WARNING and "Missing" in i.message and "examples" in i.message
                   for i in result.issues)

    def test_valid_skill_with_all_sections_passes(
        self, validator, temp_skill_file, valid_skill_content
    ):
        """Test that valid skill with all sections passes validation."""
        skill_file = temp_skill_file(valid_skill_content)
        result = validator.validate(skill_file)

        assert result.is_valid, f"Errors: {[str(e) for e in result.errors]}"
        assert len(result.errors) == 0

    # ---- Directory structure tests ----

    def test_allowed_subdirs_pass(self, validator, temp_skill_file, valid_skill_content):
        """Test that scripts/, references/, assets/ subdirs are accepted."""
        skill_file = temp_skill_file(valid_skill_content)
        skill_dir = skill_file.parent
        (skill_dir / "scripts").mkdir()
        (skill_dir / "references").mkdir()
        (skill_dir / "assets").mkdir()

        result = validator.validate(skill_file)
        dir_errors = [i for i in result.issues
                      if "Non-standard directory" in i.message]
        assert len(dir_errors) == 0

    def test_non_standard_directory_fails(self, validator, temp_skill_file, valid_skill_content):
        """Test that non-standard directories are reported as errors."""
        skill_file = temp_skill_file(valid_skill_content)
        skill_dir = skill_file.parent
        (skill_dir / "templates").mkdir()

        result = validator.validate(skill_file)
        assert any("Non-standard directory" in i.message and "templates" in i.message
                    for i in result.issues)

    def test_non_standard_file_at_root_fails(self, validator, temp_skill_file, valid_skill_content):
        """Test that extra files at skill root are reported as errors."""
        skill_file = temp_skill_file(valid_skill_content)
        skill_dir = skill_file.parent
        (skill_dir / "reference.md").write_text("# Reference")
        (skill_dir / "examples.md").write_text("# Examples")

        result = validator.validate(skill_file)
        file_errors = [i for i in result.issues
                       if "Non-standard file at skill root" in i.message]
        assert len(file_errors) == 2

    def test_hidden_files_are_allowed(self, validator, temp_skill_file, valid_skill_content):
        """Test that hidden files like .gitkeep are accepted."""
        skill_file = temp_skill_file(valid_skill_content)
        skill_dir = skill_file.parent
        (skill_dir / ".gitkeep").write_text("")

        result = validator.validate(skill_file)
        hidden_errors = [i for i in result.issues
                         if ".gitkeep" in i.message]
        assert len(hidden_errors) == 0

    def test_multiple_non_standard_entries(self, validator, temp_skill_file, valid_skill_content):
        """Test that multiple violations are all reported."""
        skill_file = temp_skill_file(valid_skill_content)
        skill_dir = skill_file.parent
        (skill_dir / "templates").mkdir()
        (skill_dir / "docs").mkdir()
        (skill_dir / "extra.md").write_text("# Extra")

        result = validator.validate(skill_file)
        structure_errors = [i for i in result.issues
                            if "Non-standard" in i.message]
        assert len(structure_errors) == 3


class TestAgentValidator:
    """Tests for AgentValidator."""

    @pytest.fixture
    def validator(self):
        return AgentValidator()

    def test_can_validate_agent_file(self, validator):
        """Test validator recognizes agent files."""
        assert validator.can_validate(Path("agents/test.md"))
        assert validator.can_validate(Path("path/agents/my-agent.md"))

    def test_cannot_validate_non_agent(self, validator):
        """Test validator rejects non-agent files."""
        assert not validator.can_validate(Path("skills/test/SKILL.md"))
        assert not validator.can_validate(Path("agents/nested/test.md"))

    def test_valid_agent_passes(self, validator, temp_agent_file, valid_agent_content):
        """Test that a valid agent passes validation."""
        agent_file = temp_agent_file(valid_agent_content)
        result = validator.validate(agent_file)

        assert result.is_valid, f"Errors: {[str(e) for e in result.errors]}"

    def test_invalid_model_warning(self, validator, temp_agent_file):
        """Test invalid model generates warning."""
        content = """---
name: test-agent
description: Test agent that helps when testing
tools: Read, Grep
model: gpt-4
---

## Role

You are a test agent.

## Process

1. Run tests
2. Report results

## Guidelines

- Follow best practices
"""
        agent_file = temp_agent_file(content)
        result = validator.validate(agent_file)

        assert result.is_valid  # Warnings don't fail
        assert any(i.field_name == "model" for i in result.issues)


class TestCommandValidator:
    """Tests for CommandValidator."""

    @pytest.fixture
    def validator(self):
        return CommandValidator()

    def test_can_validate_command_file(self, validator):
        """Test validator recognizes command files."""
        assert validator.can_validate(Path(".claude/commands/test.md"))
        assert validator.can_validate(Path("path/.claude/commands/my-cmd.md"))

    def test_cannot_validate_non_command(self, validator):
        """Test validator rejects non-command files."""
        assert not validator.can_validate(Path("agents/test.md"))
        assert not validator.can_validate(Path(".claude/test.md"))

    def test_valid_command_passes(self, validator, temp_command_file, valid_command_content):
        """Test that a valid command passes validation."""
        command_file = temp_command_file(valid_command_content)
        result = validator.validate(command_file)

        assert result.is_valid, f"Errors: {[str(e) for e in result.errors]}"

    def test_missing_description_fails(self, validator, temp_command_file):
        """Test missing description fails for commands."""
        content = """---
argument-hint: [arg]
---
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        assert not result.is_valid
        assert any(i.field_name == "description" for i in result.issues)

    def test_section_order_valid(self, validator, temp_command_file):
        """Test that sections in correct order pass validation."""
        content = """---
description: Test command
allowed-tools: Read
---

# Test Command

## Overview

Overview content.

## Usage

Usage content.

## Arguments

Arguments content.

## Examples

Examples content.
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        # Should not have section order errors
        order_errors = [i for i in result.errors if "out of order" in i.message]
        assert len(order_errors) == 0, f"Unexpected order errors: {order_errors}"

    def test_section_order_invalid_examples_before_usage(self, validator, temp_command_file):
        """Test that Examples before Usage fails validation."""
        content = """---
description: Test command
allowed-tools: Read
---

# Test Command

## Overview

Overview content.

## Examples

Examples content.

## Usage

Usage content.
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        # Should have section order error
        order_errors = [i for i in result.errors if "out of order" in i.message]
        assert len(order_errors) > 0, "Expected section order error but found none"
        assert any("Usage" in e.message for e in order_errors)

    def test_section_order_invalid_arguments_before_overview(self, validator, temp_command_file):
        """Test that Arguments before Overview fails validation."""
        content = """---
description: Test command
allowed-tools: Read
---

# Test Command

## Arguments

Arguments content.

## Overview

Overview content.

## Usage

Usage content.

## Examples

Examples content.
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        # Should have section order error
        order_errors = [i for i in result.errors if "out of order" in i.message]
        assert len(order_errors) > 0, "Expected section order error but found none"
        assert any("Overview" in e.message for e in order_errors)

    def test_section_order_with_optional_sections(self, validator, temp_command_file):
        """Test that optional sections in correct order pass validation."""
        content = """---
description: Test command
allowed-tools: Read
---

# Test Command

## Overview

Overview content.

## Usage

Usage content.

## Arguments

Arguments content.

## Current Context

Context content.

## Execution Steps

Steps content.

## Execution Instructions

Instructions content.

## Integration with Sub-agents

Integration content.

## Examples

Examples content.

## Additional Notes

Notes content.
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        # Should not have section order errors
        order_errors = [i for i in result.errors if "out of order" in i.message]
        assert len(order_errors) == 0, f"Unexpected order errors: {order_errors}"

    def test_section_order_execution_steps_before_arguments(self, validator, temp_command_file):
        """Test that Execution Steps before Arguments fails validation."""
        content = """---
description: Test command
allowed-tools: Read
---

# Test Command

## Overview

Overview content.

## Usage

Usage content.

## Execution Steps

Steps content.

## Arguments

Arguments content.

## Examples

Examples content.
"""
        command_file = temp_command_file(content)
        result = validator.validate(command_file)

        # Should have section order error
        order_errors = [i for i in result.errors if "out of order" in i.message]
        assert len(order_errors) > 0, "Expected section order error but found none"


class TestValidatorFactory:
    """Tests for ValidatorFactory."""

    def test_get_skill_validator(self):
        """Test factory returns skill validator for skill files."""
        validator = ValidatorFactory.get_validator(Path("skills/test/SKILL.md"))
        assert isinstance(validator, SkillValidator)

    def test_get_agent_validator(self):
        """Test factory returns agent validator for agent files."""
        validator = ValidatorFactory.get_validator(Path("agents/test.md"))
        assert isinstance(validator, AgentValidator)

    def test_get_command_validator(self):
        """Test factory returns command validator for command files."""
        validator = ValidatorFactory.get_validator(Path(".claude/commands/test.md"))
        assert isinstance(validator, CommandValidator)

    def test_get_none_for_unknown(self):
        """Test factory returns None for unknown files."""
        validator = ValidatorFactory.get_validator(Path("README.md"))
        assert validator is None

    def test_get_all_patterns(self):
        """Test factory returns all patterns."""
        patterns = ValidatorFactory.get_all_patterns()
        assert len(patterns) == 3
