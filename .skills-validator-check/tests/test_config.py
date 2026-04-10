"""Tests for configuration module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.config import (
    SKILL_PATTERN,
    AGENT_PATTERN,
    COMMAND_PATTERN,
    KEBAB_CASE_PATTERN,
    SEMVER_PATTERN,
    VALID_TOOLS,
    VALID_MODELS,
    RESERVED_WORDS,
    SKILL_SCHEMA,
    AGENT_SCHEMA,
    COMMAND_SCHEMA,
)


class TestFilePatterns:
    """Tests for file matching patterns."""

    def test_skill_pattern_matches(self):
        """Test skill pattern matches correct paths."""
        assert SKILL_PATTERN.search("skills/spring-boot/SKILL.md")
        assert SKILL_PATTERN.search("skills/my-skill/SKILL.md")
        assert SKILL_PATTERN.search("path/to/skills/test/SKILL.md")

    def test_skill_pattern_rejects(self):
        """Test skill pattern rejects incorrect paths."""
        assert not SKILL_PATTERN.search("skills/SKILL.md")  # No subdirectory
        assert not SKILL_PATTERN.search("agents/test.md")
        assert not SKILL_PATTERN.search("skills/test/README.md")

    def test_skill_pattern_accepts_nested(self):
        """Test skill pattern accepts nested paths (e.g., spring-boot/spring-boot-actuator)."""
        assert SKILL_PATTERN.search("skills/nested/deep/SKILL.md")
        assert SKILL_PATTERN.search("skills/spring-boot/spring-boot-actuator/SKILL.md")

    def test_agent_pattern_matches(self):
        """Test agent pattern matches correct paths."""
        assert AGENT_PATTERN.search("agents/my-agent.md")
        assert AGENT_PATTERN.search("agents/spring-boot-expert.md")
        assert AGENT_PATTERN.search("path/to/agents/test.md")

    def test_agent_pattern_rejects(self):
        """Test agent pattern rejects incorrect paths."""
        assert not AGENT_PATTERN.search("agents/nested/test.md")
        assert not AGENT_PATTERN.search("skills/test/SKILL.md")
        assert not AGENT_PATTERN.search("agents/")

    def test_command_pattern_matches(self):
        """Test command pattern matches correct paths."""
        assert COMMAND_PATTERN.search(".claude/commands/my-command.md")
        assert COMMAND_PATTERN.search(".claude/commands/devkit.feature.md")
        assert COMMAND_PATTERN.search("path/to/.claude/commands/test.md")

    def test_command_pattern_rejects(self):
        """Test command pattern rejects incorrect paths."""
        assert not COMMAND_PATTERN.search(".claude/commands/nested/test.md")
        # Note: commands/ prefix is valid (with or without leading dot)
        assert not COMMAND_PATTERN.search(".claude/test.md")


class TestKebabCasePattern:
    """Tests for kebab-case validation pattern."""

    @pytest.mark.parametrize("name", [
        "valid",
        "valid-name",
        "a-b-c",
        "skill-123",
        "my-long-skill-name",
        "a1-b2-c3",
        "devkit.lra.add-feature",  # Dotted namespace style
        "my.plugin.command",
        "a.b.c",
    ])
    def test_valid_kebab_case(self, name):
        """Test valid kebab-case names."""
        assert KEBAB_CASE_PATTERN.match(name), f"'{name}' should be valid"

    @pytest.mark.parametrize("name", [
        "Invalid",
        "invalid_name",
        "invalid name",
        "-invalid",
        "invalid-",
        "123-invalid",
        "UPPERCASE",
        "camelCase",
        "with--double",
        "",
    ])
    def test_invalid_kebab_case(self, name):
        """Test invalid kebab-case names."""
        assert not KEBAB_CASE_PATTERN.match(name), f"'{name}' should be invalid"


class TestSemverPattern:
    """Tests for semantic versioning pattern."""

    @pytest.mark.parametrize("version", [
        "1.0.0",
        "0.1.0",
        "10.20.30",
        "1.0.0-alpha",
        "1.0.0-beta.1",
        "2.1.0-rc1",
    ])
    def test_valid_semver(self, version):
        """Test valid semantic versions."""
        assert SEMVER_PATTERN.match(version), f"'{version}' should be valid"

    @pytest.mark.parametrize("version", [
        "1.0",
        "1",
        "v1.0.0",
        "1.0.0.0",
        "01.0.0",
        "1.00.0",
    ])
    def test_invalid_semver(self, version):
        """Test invalid semantic versions."""
        assert not SEMVER_PATTERN.match(version), f"'{version}' should be invalid"


class TestValidTools:
    """Tests for valid tools list."""

    def test_common_tools_present(self):
        """Test common tools are in the list."""
        assert "Read" in VALID_TOOLS
        assert "Write" in VALID_TOOLS
        assert "Edit" in VALID_TOOLS
        assert "Bash" in VALID_TOOLS
        assert "Grep" in VALID_TOOLS
        assert "Glob" in VALID_TOOLS
        assert "Task" in VALID_TOOLS

    def test_tools_is_frozen(self):
        """Test that tools set is immutable."""
        with pytest.raises(AttributeError):
            VALID_TOOLS.add("NewTool")


class TestValidModels:
    """Tests for valid models list."""

    def test_models_present(self):
        """Test all expected models are present."""
        assert "sonnet" in VALID_MODELS
        assert "opus" in VALID_MODELS
        assert "haiku" in VALID_MODELS
        assert "inherit" in VALID_MODELS

    def test_models_is_frozen(self):
        """Test that models set is immutable."""
        with pytest.raises(AttributeError):
            VALID_MODELS.add("new-model")


class TestReservedWords:
    """Tests for reserved words list."""

    def test_common_reserved_words(self):
        """Test common reserved words are present."""
        assert "help" in RESERVED_WORDS
        assert "status" in RESERVED_WORDS
        assert "config" in RESERVED_WORDS
        assert "commit" in RESERVED_WORDS

    def test_reserved_is_frozen(self):
        """Test that reserved words set is immutable."""
        with pytest.raises(AttributeError):
            RESERVED_WORDS.add("new-word")


class TestSchemas:
    """Tests for validation schemas."""

    def test_skill_schema_required(self):
        """Test skill schema required fields."""
        assert "name" in SKILL_SCHEMA["required"]
        assert "description" in SKILL_SCHEMA["required"]
        # allowed-tools is now required for security
        assert "allowed-tools" in SKILL_SCHEMA["required"]

    def test_skill_schema_prohibited(self):
        """Test skill schema prohibited fields."""
        assert "language" in SKILL_SCHEMA["prohibited"]
        assert "framework" in SKILL_SCHEMA["prohibited"]
        assert "context7_library" in SKILL_SCHEMA["prohibited"]
        assert "context7_trust_score" in SKILL_SCHEMA["prohibited"]

    def test_skill_schema_optional(self):
        """Test skill schema optional fields per agentskills.io specification."""
        # Per spec: license, compatibility, metadata are optional
        assert "license" in SKILL_SCHEMA["optional"]
        assert "compatibility" in SKILL_SCHEMA["optional"]
        assert "metadata" in SKILL_SCHEMA["optional"]

    def test_agent_schema_required(self):
        """Test agent schema required fields."""
        assert "name" in AGENT_SCHEMA["required"]
        assert "description" in AGENT_SCHEMA["required"]
        # tools is now required for better control
        assert "tools" in AGENT_SCHEMA["required"]

    def test_agent_schema_optional(self):
        """Test agent schema optional fields."""
        # tools is now required (moved from optional)
        assert "model" in AGENT_SCHEMA["optional"]
        assert "permissionMode" in AGENT_SCHEMA["optional"]
        assert "skills" in AGENT_SCHEMA["optional"]

    def test_command_schema_required(self):
        """Test command schema required fields."""
        assert "description" in COMMAND_SCHEMA["required"]
        assert "allowed-tools" in COMMAND_SCHEMA["required"]  # Now required for security
        assert "name" not in COMMAND_SCHEMA["required"]

    def test_command_schema_optional(self):
        """Test command schema optional fields."""
        # allowed-tools is now required (moved from optional)
        assert "argument-hint" in COMMAND_SCHEMA["optional"]
        assert "model" in COMMAND_SCHEMA["optional"]
        assert "disable-model-invocation" in COMMAND_SCHEMA["optional"]
