"""
Validation logic for Claude Code components.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

import yaml

from .config import (
    SKILL_PATTERN,
    AGENT_PATTERN,
    COMMAND_PATTERN,
    SKILL_SCHEMA,
    AGENT_SCHEMA,
    COMMAND_SCHEMA,
    SKILL_PROHIBITED_FILES,
    SKILL_ALLOWED_SUBDIRS,
    SKILL_REQUIRED_SECTIONS,
    SKILL_RECOMMENDED_SECTIONS,
    COMMAND_REQUIRED_SECTIONS,
    COMMAND_RECOMMENDED_SECTIONS,
    COMMAND_SECTIONS_ORDER,
    COMMAND_SECTION_PATTERNS,
    AGENT_REQUIRED_SECTIONS,
    AGENT_RECOMMENDED_SECTIONS,
    VALID_TOOLS,
    VALID_MODELS,
    AGENT_VALID_MODELS,
    RESERVED_WORDS,
    KEBAB_CASE_PATTERN,
    SEMVER_PATTERN,
    MAX_NAME_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    WHAT_KEYWORDS,
    WHEN_KEYWORDS,
)
from .models import ValidationResult, Severity


class BaseValidator(ABC):
    """Abstract base class for all component validators."""

    @property
    @abstractmethod
    def component_type(self) -> str:
        """Return the type of component this validator handles."""
        pass

    @property
    @abstractmethod
    def file_pattern(self) -> re.Pattern:
        """Return the regex pattern for matching files."""
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Set[str]]:
        """Return the validation schema with required/optional fields."""
        pass

    def can_validate(self, file_path: Path) -> bool:
        """Check if this validator can handle the given file."""
        return bool(self.file_pattern.search(str(file_path)))

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate a file and return the result."""
        result = ValidationResult(
            file_path=file_path,
            component_type=self.component_type
        )

        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            result.add_error(
                message=f"File not found: {file_path}",
                suggestion="Verify the file path is correct"
            )
            return result
        except UnicodeDecodeError:
            result.add_error(
                message="File is not valid UTF-8",
                suggestion="Ensure the file uses UTF-8 encoding"
            )
            return result

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content, result)
        if frontmatter is None:
            return result  # Critical error, can't continue

        # Validate schema
        self._validate_schema(frontmatter, result)

        # Validate fields
        self._validate_fields(frontmatter, result)

        # Component-specific validation
        self._validate_specific(file_path, frontmatter, content, result)

        return result

    def _parse_frontmatter(
        self,
        content: str,
        result: ValidationResult
    ) -> Optional[Dict[str, Any]]:
        """Extract and parse YAML frontmatter from markdown content."""
        # Check for frontmatter delimiters
        if not content.startswith("---"):
            result.add_error(
                message="Missing YAML frontmatter",
                line_number=1,
                suggestion="Add YAML frontmatter at the beginning: ---\\nname: ...\\n---"
            )
            return None

        # Find the closing delimiter (blank line after --- is optional)
        end_match = re.search(r"\n---\s*\n?", content[3:])
        if not end_match:
            result.add_error(
                message="Unclosed YAML frontmatter",
                line_number=1,
                suggestion="Add closing '---' after frontmatter"
            )
            return None

        # Extract YAML content
        yaml_content = content[3:end_match.start() + 3]

        # Run enhanced YAML validation BEFORE parsing
        yaml_issues = self._validate_yaml_syntax_enhanced(yaml_content, result)
        if yaml_issues:
            return None  # Critical YAML syntax errors found

        try:
            frontmatter = yaml.safe_load(yaml_content)
            if frontmatter is None:
                frontmatter = {}
            if not isinstance(frontmatter, dict):
                result.add_error(
                    message="Frontmatter must be a YAML mapping",
                    line_number=1,
                    suggestion="Ensure frontmatter contains key-value pairs"
                )
                return None
            return frontmatter
        except yaml.YAMLError as e:
            line = e.problem_mark.line + 1 if hasattr(e, "problem_mark") and e.problem_mark else 1
            result.add_error(
                message=f"Invalid YAML syntax: {e.problem if hasattr(e, 'problem') else str(e)}",
                line_number=line,
                suggestion="Fix the YAML syntax error"
            )
            return None

    def _validate_yaml_syntax_enhanced(self, yaml_content: str, result: ValidationResult) -> bool:
        """Enhanced YAML validation to catch common syntax issues before parsing.

        Returns True if critical issues found (parsing should stop).
        """
        issues_found = False
        lines = yaml_content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue

            # Skip lines that are clearly keys (ending with colon)
            if stripped.endswith(':'):
                continue

            # Check for unquoted strings with problematic patterns
            # Pattern 1: String containing (N): where N is a number - common YAML error
            # e.g., "including: (1) one, (2) two" - the (2): is interpreted as a key
            unquoted_match = re.search(r'\([^)]+\):', stripped)
            if unquoted_match:
                # Check if this line is NOT part of a quoted string continuation
                # by counting quotes before the match
                before_match = stripped[:unquoted_match.start()]
                quote_count = before_match.count('"') + before_match.count("'")
                # If quote count is odd, we're inside a quoted string (continuation) - OK
                if quote_count % 2 == 0:
                    result.add_error(
                        message=f"Potential YAML syntax error: '{unquoted_match.group()}' in unquoted string",
                        line_number=line_num,
                        suggestion="Use single quotes instead of double quotes for strings containing '):' patterns (e.g., '(1):'). YAML interprets '):' as a key-value separator in unquoted strings."
                    )
                    issues_found = True

            # Pattern 2: Detect potential flow-style mapping issues
            # Lines with multiple colons in unquoted context
            if ':' in stripped and not stripped.startswith('- '):
                # Check if quotes are balanced
                if stripped.startswith('"') or stripped.startswith("'"):
                    single_quotes = stripped.count("'") % 2
                    double_quotes = stripped.count('"') % 2
                    if single_quotes or double_quotes:
                        result.add_error(
                            message=f"Unbalanced quotes in YAML value at line {line_num}",
                            line_number=line_num,
                            suggestion="Ensure all quotes are properly closed"
                        )
                        issues_found = True

            # Pattern 3: Double-quoted strings with ): patterns - suggest single quotes
            # Some YAML parsers (like Codex) may have issues with "..." containing (N):
            if '"' in stripped:
                # Check for ): pattern anywhere in the line
                if re.search(r'\):', stripped) or re.search(r'\([0-9]+\)', stripped):
                    if stripped.count('"') >= 2:
                        result.add_warning(
                            message="Double-quoted string contains '):' pattern which may cause issues with some YAML parsers",
                            line_number=line_num,
                            suggestion="Consider using single quotes instead of double quotes for strings containing '):' patterns (e.g., '(1):', '(2):')"
                        )

        return issues_found

    def _validate_schema(
        self,
        frontmatter: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate that required fields are present and warn about unknown fields."""
        # Check prohibited fields first
        if "prohibited" in self.schema:
            for field in self.schema["prohibited"]:
                if field in frontmatter:
                    result.add_error(
                        message=f"Prohibited field: '{field}'",
                        field_name=field,
                        suggestion=f"Remove '{field}' from frontmatter"
                    )

        # Check required fields
        for field in self.schema.get("required", set()):
            if field not in frontmatter:
                result.add_error(
                    message=f"Missing required field: '{field}'",
                    field_name=field,
                    suggestion=f"Add '{field}: value' to frontmatter"
                )

        # Check for unknown fields (exclude prohibited since already handled)
        known = self.schema.get("required", set()) | self.schema.get("optional", set())
        prohibited = self.schema.get("prohibited", set())
        for field in frontmatter:
            if field not in known and field not in prohibited:
                result.add_warning(
                    message=f"Unknown field: '{field}'",
                    field_name=field,
                    suggestion=f"Remove '{field}' or verify it's needed"
                )

    def _validate_fields(
        self,
        frontmatter: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate individual field values."""
        # Validate name if present
        if "name" in frontmatter:
            self._validate_name(frontmatter["name"], result)

        # Validate description if present
        if "description" in frontmatter:
            self._validate_description(frontmatter["description"], result)

    def _validate_name(self, name: Any, result: ValidationResult) -> None:
        """Validate the name field."""
        if not isinstance(name, str):
            result.add_error(
                message=f"Name must be a string, got {type(name).__name__}",
                field_name="name",
                suggestion="Ensure name is a plain string value"
            )
            return

        # Check length
        if len(name) > MAX_NAME_LENGTH:
            result.add_error(
                message=f"Name too long: {len(name)} characters (max {MAX_NAME_LENGTH})",
                field_name="name",
                suggestion=f"Shorten name to {MAX_NAME_LENGTH} characters or less"
            )

        # Check kebab-case format
        if not KEBAB_CASE_PATTERN.match(name):
            result.add_error(
                message=f"Invalid name format: '{name}'",
                field_name="name",
                suggestion="Use kebab-case (e.g., 'my-component-name')"
            )

        # Check reserved words
        if name.lower() in RESERVED_WORDS:
            result.add_error(
                message=f"Reserved word used as name: '{name}'",
                field_name="name",
                suggestion=f"Choose a different name (reserved: {', '.join(sorted(RESERVED_WORDS)[:5])}...)"
            )

    def _validate_description(self, description: Any, result: ValidationResult) -> None:
        """Validate the description field."""
        if not isinstance(description, str):
            result.add_error(
                message=f"Description must be a string, got {type(description).__name__}",
                field_name="description",
                suggestion="Ensure description is a plain string value"
            )
            return

        # Check length
        if len(description) > MAX_DESCRIPTION_LENGTH:
            result.add_warning(
                message=f"Description too long: {len(description)} characters (max {MAX_DESCRIPTION_LENGTH})",
                field_name="description",
                suggestion=f"Shorten description to {MAX_DESCRIPTION_LENGTH} characters"
            )

        # Check for WHAT and WHEN content
        desc_lower = description.lower()
        has_what = any(kw in desc_lower for kw in WHAT_KEYWORDS)
        has_when = any(kw in desc_lower for kw in WHEN_KEYWORDS)

        if not (has_what and has_when):
            missing = []
            if not has_what:
                missing.append("WHAT")
            if not has_when:
                missing.append("WHEN")
            result.add_warning(
                message=f"Description may be missing: {', '.join(missing)} information",
                field_name="description",
                suggestion="Include what the component does AND when to use it"
            )

    def _validate_tools_field(
        self,
        tools: Any,
        field_name: str,
        result: ValidationResult
    ) -> None:
        """Validate tool names (shared implementation for all validators)."""
        if isinstance(tools, str):
            tool_list = [t.strip() for t in tools.split(",")]
        elif isinstance(tools, list):
            tool_list = tools
        else:
            result.add_warning(
                message=f"{field_name} should be a string or list, got {type(tools).__name__}",
                field_name=field_name,
                suggestion="Use comma-separated string or YAML list"
            )
            return

        for tool in tool_list:
            if not isinstance(tool, str):
                continue
            # Handle tools with arguments like "Bash(git add:*, git status:*)"
            base_tool = tool.split("(")[0].strip()
            if base_tool and base_tool not in VALID_TOOLS:
                result.add_warning(
                    message=f"Unknown tool: '{base_tool}'",
                    field_name=field_name,
                    suggestion=f"Valid tools: {', '.join(sorted(VALID_TOOLS)[:5])}..."
                )

    def _validate_model_field(
        self,
        model: Any,
        field_name: str,
        result: ValidationResult,
        allow_full_model_names: bool = False
    ) -> None:
        """Validate model value (shared implementation).

        Args:
            model: The model value to validate
            field_name: Name of the field being validated
            result: ValidationResult to add issues to
            allow_full_model_names: If True, also accepts 'claude-*' style model names
        """
        if not isinstance(model, str):
            result.add_warning(
                message=f"{field_name} should be a string, got {type(model).__name__}",
                field_name=field_name,
                suggestion=f"Use one of: {', '.join(sorted(VALID_MODELS))}"
            )
            return

        is_valid = model.lower() in VALID_MODELS
        if allow_full_model_names:
            is_valid = is_valid or model.startswith("claude-")

        if not is_valid:
            result.add_warning(
                message=f"Invalid model value: '{model}'",
                field_name=field_name,
                suggestion=f"Use one of: {', '.join(sorted(VALID_MODELS))}"
            )

    @abstractmethod
    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Component-specific validation logic."""
        pass


class SkillValidator(BaseValidator):
    """Validator for Claude Code Skills."""

    @property
    def component_type(self) -> str:
        return "skill"

    @property
    def file_pattern(self) -> re.Pattern:
        return SKILL_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return SKILL_SCHEMA

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Skill-specific validation."""
        # Validate allowed-tools is present (now required)
        if "allowed-tools" not in frontmatter:
            result.add_error(
                message="Missing required field: 'allowed-tools'",
                field_name="allowed-tools",
                suggestion="Add 'allowed-tools' to specify which tools this skill requires"
            )

        # Validate version if present
        if "version" in frontmatter:
            self._validate_version(frontmatter["version"], result)

        # Validate allowed-tools if present
        if "allowed-tools" in frontmatter:
            self._validate_tools_field(frontmatter["allowed-tools"], "allowed-tools", result)

        # Validate context7_trust_score if present
        if "context7_trust_score" in frontmatter:
            self._validate_trust_score(frontmatter["context7_trust_score"], result)

        # Validate markdown structure
        self._validate_markdown_structure(content, result)

        # Validate I/O examples
        self._validate_io_examples(content, result)

        # Check for prohibited files in skill directory
        self._check_prohibited_files(file_path.parent, result)

        # Validate directory structure (Anthropic convention)
        self._validate_directory_structure(file_path.parent, result)

    def _validate_markdown_structure(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate markdown sections are present."""
        # Find content after frontmatter
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return  # Already caught by frontmatter validation

        body = content[match.end():]

        # Check required sections
        for section_key, pattern in SKILL_REQUIRED_SECTIONS.items():
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                if section_key == "when_to_use":
                    section_name = "When to Use"
                result.add_error(
                    message=f"Missing required section: '## {section_name}'",
                    suggestion=f"Add '## {section_name}' section to SKILL.md"
                )

        # Check recommended sections
        for section_key in SKILL_RECOMMENDED_SECTIONS:
            # Convert to hyphenated format for regex matching
            pattern = SKILL_REQUIRED_SECTIONS.get(section_key)
            if not pattern:
                # Create pattern for recommended sections
                section_name_hyphen = section_key.replace("_", "-")
                section_name_title = section_name_hyphen.title()
                if section_name_hyphen == "best-practices":
                    section_name_title = "Best Practices"
                elif section_name_hyphen == "constraints-and-warnings":
                    section_name_title = "Constraints and Warnings"
                pattern = rf"^#{{1,3}}\s+{section_name_title}"
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                if section_key == "best_practices":
                    section_name = "Best Practices"
                elif section_key == "constraints_and_warnings":
                    section_name = "Constraints and Warnings"
                result.add_warning(
                    message=f"Missing recommended section: '## {section_name}'",
                    suggestion=f"Consider adding '## {section_name}' section"
                )

    def _validate_io_examples(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate Input/Output examples format."""
        # Check for Input/Output pattern in examples (subsections like ### Input, ### Output)
        io_pattern = re.compile(
            r"^#{2,3}\s+(?:Input|Output|Example\s+\d+|Example:)",
            re.MULTILINE | re.IGNORECASE
        )

        # Also check for code blocks in examples section which indicate I/O
        code_block_pattern = re.compile(
            r"```[a-zA-Z0-9]*\n[\s\S]*?\n```",
            re.MULTILINE
        )

        # Check if Examples section exists first
        examples_match = re.search(r"^#{1,3}\s+Examples", content, re.IGNORECASE | re.MULTILINE)

        if examples_match:
            # If Examples section exists, check for I/O patterns
            examples_section = content[examples_match.start():]
            has_io = io_pattern.search(examples_section) or code_block_pattern.search(examples_section)
            if not has_io:
                result.add_warning(
                    message="Missing Input/Output examples in Examples section",
                    suggestion="Add concrete Input/Output examples with code blocks to demonstrate usage"
                )

    def _validate_version(self, version: Any, result: ValidationResult) -> None:
        """Validate semantic versioning format."""
        if not isinstance(version, str):
            result.add_warning(
                message=f"Version should be a string, got {type(version).__name__}",
                field_name="version",
                suggestion="Use semantic versioning (e.g., '1.0.0')"
            )
            return

        if not SEMVER_PATTERN.match(version):
            result.add_warning(
                message=f"Invalid version format: '{version}'",
                field_name="version",
                suggestion="Use semantic versioning (e.g., '1.0.0', '2.1.0-beta')"
            )

    def _validate_trust_score(self, score: Any, result: ValidationResult) -> None:
        """Validate context7_trust_score value."""
        if not isinstance(score, (int, float)):
            result.add_warning(
                message=f"context7_trust_score should be numeric, got {type(score).__name__}",
                field_name="context7_trust_score",
                suggestion="Use a number between 0 and 10"
            )
            return

        if not 0 <= score <= 10:
            result.add_warning(
                message=f"context7_trust_score out of range: {score}",
                field_name="context7_trust_score",
                suggestion="Use a value between 0 and 10"
            )

    def _check_prohibited_files(self, skill_dir: Path, result: ValidationResult) -> None:
        """Check for prohibited files in the skill directory."""
        for filename in SKILL_PROHIBITED_FILES:
            prohibited = skill_dir / filename
            if prohibited.exists():
                result.add_error(
                    message=f"Prohibited file found: {filename}",
                    suggestion=f"Remove {filename} from skill directory"
                )

    def _validate_directory_structure(self, skill_dir: Path, result: ValidationResult) -> None:
        """Validate skill directory follows the Anthropic convention.

        Expected structure:
            skill-name/
            ├── SKILL.md (required)
            └── Bundled Resources (optional)
                ├── scripts/
                ├── references/
                └── assets/
        """
        if not skill_dir.exists():
            return

        for entry in sorted(skill_dir.iterdir()):
            name = entry.name

            # SKILL.md is allowed
            if name == "SKILL.md":
                continue

            # Hidden files (.gitkeep, etc.) are allowed
            if name.startswith("."):
                continue

            if entry.is_dir():
                if name not in SKILL_ALLOWED_SUBDIRS:
                    result.add_error(
                        message=f"Non-standard directory found: '{name}/'",
                        suggestion=f"Move contents to one of the allowed subdirectories: {', '.join(sorted(SKILL_ALLOWED_SUBDIRS))}/"
                    )
            else:
                # Any file other than SKILL.md at root level is not allowed
                result.add_error(
                    message=f"Non-standard file at skill root: '{name}'",
                    suggestion=f"Move '{name}' into scripts/, references/, or assets/"
                )


class AgentValidator(BaseValidator):
    """Validator for Claude Code Agents."""

    @property
    def component_type(self) -> str:
        return "agent"

    @property
    def file_pattern(self) -> re.Pattern:
        return AGENT_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return AGENT_SCHEMA

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Agent-specific validation."""
        # Validate tools (now required via schema, but still validate content if present)
        if "tools" in frontmatter:
            self._validate_tools_field(frontmatter["tools"], "tools", result)

        # Validate model if present (agents only accept opus, sonnet, haiku)
        if "model" in frontmatter:
            self._validate_agent_model_field(frontmatter["model"], result)

        # Validate markdown structure (required sections)
        self._validate_markdown_structure(content, result)

    def _validate_agent_model_field(
        self,
        model: Any,
        result: ValidationResult
    ) -> None:
        """Validate model value for agents (strict: only opus, sonnet, haiku)."""
        if not isinstance(model, str):
            result.add_warning(
                message=f"model should be a string, got {type(model).__name__}",
                field_name="model",
                suggestion=f"Use one of: {', '.join(sorted(AGENT_VALID_MODELS))}"
            )
            return

        # Check for 'inherit' - generate warning
        if model.lower() == "inherit":
            result.add_warning(
                message="'inherit' model value is not recommended for agents",
                field_name="model",
                suggestion=f"Explicitly specify model for better control: {', '.join(sorted(AGENT_VALID_MODELS))}"
            )
            return

        # Check against strict valid models (opus, sonnet, haiku only)
        if model.lower() not in AGENT_VALID_MODELS:
            result.add_warning(
                message=f"Invalid model value: '{model}'",
                field_name="model",
                suggestion=f"Use one of: {', '.join(sorted(AGENT_VALID_MODELS))}"
            )

    def _validate_markdown_structure(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate agent markdown sections are present."""
        # Find content after frontmatter
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return  # Already caught by frontmatter validation

        body = content[match.end():]

        # Check required sections
        for section_key, pattern in AGENT_REQUIRED_SECTIONS.items():
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                result.add_error(
                    message=f"Missing required section matching: '{section_name}'",
                    suggestion=f"Add a section like '## Role', '## Process', or '## Guidelines' to the agent"
                )

        # Check recommended sections
        for section_key in AGENT_RECOMMENDED_SECTIONS:
            section_name_hyphen = section_key.replace("_", "-")
            section_name_title = section_name_hyphen.title()
            if section_name_hyphen == "skills-integration":
                section_name_title = "Skills Integration"
            elif section_name_hyphen == "common-patterns":
                section_name_title = "Common Patterns"
            elif section_name_hyphen == "output-format":
                section_name_title = "Output Format"
            pattern = rf"^#{{1,3}}\s+{section_name_title}"
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                result.add_warning(
                    message=f"Missing recommended section: '## {section_name}'",
                    suggestion=f"Consider adding '## {section_name}' section"
                )


class CommandValidator(BaseValidator):
    """Validator for Claude Code Slash Commands."""

    @property
    def component_type(self) -> str:
        return "command"

    @property
    def file_pattern(self) -> re.Pattern:
        return COMMAND_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return COMMAND_SCHEMA

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Command-specific validation."""
        # Validate allowed-tools (now required, validated in schema)
        if "allowed-tools" in frontmatter:
            self._validate_tools_field(frontmatter["allowed-tools"], "allowed-tools", result)

        # Validate model if present (commands can also use 'claude-*' style names)
        if "model" in frontmatter:
            self._validate_model_field(
                frontmatter["model"],
                "model",
                result,
                allow_full_model_names=True
            )

        # Validate disable-model-invocation if present
        if "disable-model-invocation" in frontmatter:
            self._validate_boolean(
                frontmatter["disable-model-invocation"],
                "disable-model-invocation",
                result
            )

        # Validate markdown structure (required sections and order)
        self._validate_markdown_structure(content, result)
        self._validate_section_order(content, result)

    def _validate_markdown_structure(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate command markdown sections are present."""
        # Find content after frontmatter
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return  # Already caught by frontmatter validation

        body = content[match.end():]

        # Check required sections
        for section_key, pattern in COMMAND_REQUIRED_SECTIONS.items():
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                result.add_error(
                    message=f"Missing required section: '## {section_name}'",
                    suggestion=f"Add '## {section_name}' section to command file"
                )

        # Check recommended sections
        for section_key in COMMAND_RECOMMENDED_SECTIONS:
            section_name_hyphen = section_key.replace("_", "-")
            section_name_title = section_name_hyphen.title()
            if section_name_hyphen == "best-practices":
                section_name_title = "Best Practices"
            pattern = rf"^#{{1,3}}\s+{section_name_title}"
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                if section_key == "best_practices":
                    section_name = "Best Practices"
                result.add_warning(
                    message=f"Missing recommended section: '## {section_name}'",
                    suggestion=f"Consider adding '## {section_name}' section"
                )

    def _validate_section_order(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate that command sections appear in the correct order.

        Sections must follow the order defined in COMMAND_SECTIONS_ORDER.
        Any section not in the order list can appear after the last defined section.
        """
        # Find content after frontmatter
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return  # Already caught by frontmatter validation

        body = content[match.end():]

        # Map section names to their expected order index
        section_order_indices: Dict[str, int] = {
            name: idx for idx, name in enumerate(COMMAND_SECTIONS_ORDER)
        }

        # Find all ordered sections in the document with their positions
        found_ordered_sections: List[tuple] = []

        for order_key, pattern in COMMAND_SECTION_PATTERNS.items():
            for match in re.finditer(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_title = match.group(0).strip()
                section_pos = match.start()
                order_index = section_order_indices[order_key]
                found_ordered_sections.append((order_index, section_pos, order_key, section_title))

        # Sort by position in document
        found_ordered_sections.sort(key=lambda x: x[1])

        # Check if sections are in correct order
        last_order_index = -1
        last_section_key = None

        for order_index, section_pos, section_key, section_title in found_ordered_sections:
            if order_index < last_order_index:
                # This section is out of order
                expected_before_key = None
                expected_before_title = None

                # Find which section this should come before
                for prev_order_index, prev_pos, prev_key, prev_title in found_ordered_sections:
                    if prev_pos < section_pos and prev_order_index > order_index:
                        expected_before_key = prev_key
                        expected_before_title = prev_title.lstrip("#").strip()
                        break

                # Find which section this should come after
                expected_after_key = None
                for order_idx, section_name in enumerate(COMMAND_SECTIONS_ORDER):
                    if order_idx < order_index:
                        # Check if this section exists in the document
                        for prev_order_idx, prev_pos, prev_key, prev_title in found_ordered_sections:
                            if prev_key == section_name and prev_pos < section_pos:
                                expected_after_key = section_name

                current_name = section_key.replace("_", " ").title()

                if expected_before_key:
                    expected_name = expected_before_key.replace("_", " ").title()
                    result.add_error(
                        message=f"Section '## {current_name}' is out of order",
                        suggestion=f"Move '## {current_name}' before '## {expected_name}' (correct order: Overview → Usage → Arguments → Current Context → Execution Steps → Execution Instructions → Integration with Sub-agents → Examples)"
                    )
                elif expected_after_key:
                    expected_name = expected_after_key.replace("_", " ").title()
                    result.add_error(
                        message=f"Section '## {current_name}' is out of order",
                        suggestion=f"Move '## {current_name}' after '## {expected_name}' (correct order: Overview → Usage → Arguments → Current Context → Execution Steps → Execution Instructions → Integration with Sub-agents → Examples)"
                    )
                else:
                    result.add_error(
                        message=f"Section '## {current_name}' is out of order",
                        suggestion=f"Correct order: Overview → Usage → Arguments → Current Context → Execution Steps → Execution Instructions → Integration with Sub-agents → Examples"
                    )
            else:
                last_order_index = order_index
                last_section_key = section_key

    def _validate_boolean(
        self,
        value: Any,
        field_name: str,
        result: ValidationResult
    ) -> None:
        """Validate boolean field."""
        if not isinstance(value, bool):
            result.add_warning(
                message=f"{field_name} should be a boolean, got {type(value).__name__}",
                field_name=field_name,
                suggestion="Use 'true' or 'false'"
            )


class ValidatorFactory:
    """Factory for creating appropriate validators."""

    _validators: List[BaseValidator] = [
        SkillValidator(),
        AgentValidator(),
        CommandValidator(),
    ]

    @classmethod
    def get_validator(cls, file_path: Path) -> Optional[BaseValidator]:
        """Get the appropriate validator for a file."""
        for validator in cls._validators:
            if validator.can_validate(file_path):
                return validator
        return None

    @classmethod
    def get_all_patterns(cls) -> List[re.Pattern]:
        """Get all file patterns for component files."""
        return [v.file_pattern for v in cls._validators]
