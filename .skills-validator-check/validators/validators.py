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
    RULE_PATTERN,
    MARKDOWN_FILE_PATTERN,
    SKILL_PACKAGE_PATTERN,
    PLUGIN_PATTERN,
    SKILL_SCHEMA,
    AGENT_SCHEMA,
    COMMAND_SCHEMA,
    RULE_SCHEMA,
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
    RULE_REQUIRED_SECTIONS,
    RULE_RECOMMENDED_SECTIONS,
    VALID_TOOLS,
    VALID_MODELS,
    AGENT_VALID_MODELS,
    RESERVED_WORDS,
    KEBAB_CASE_PATTERN,
    KEBAB_CASE_EXEMPT_FILES,
    SEMVER_PATTERN,
    MAX_NAME_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_COMPATIBILITY_LENGTH,
    MAX_SKILL_LINES,
    MAX_SKILL_CHARACTERS,
    MAX_RULE_LINES,
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

        # Validate compatibility if present
        if "compatibility" in frontmatter:
            self._validate_compatibility(frontmatter["compatibility"], result)

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

    def _validate_compatibility(self, compatibility: Any, result: ValidationResult) -> None:
        """Validate the compatibility field."""
        if not isinstance(compatibility, str):
            result.add_error(
                message=f"Compatibility must be a string, got {type(compatibility).__name__}",
                field_name="compatibility",
                suggestion="Ensure compatibility is a plain string value"
            )
            return

        # Check length (per spec: max 500 characters)
        if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            result.add_error(
                message=f"Compatibility too long: {len(compatibility)} characters (max {MAX_COMPATIBILITY_LENGTH})",
                field_name="compatibility",
                suggestion=f"Shorten compatibility to {MAX_COMPATIBILITY_LENGTH} characters or less"
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
        # Validate name matches parent directory
        if "name" in frontmatter:
            skill_name = frontmatter["name"]
            parent_dir_name = file_path.parent.name
            if skill_name != parent_dir_name:
                result.add_error(
                    message=f"Name mismatch: frontmatter has '{skill_name}' but directory is '{parent_dir_name}'",
                    field_name="name",
                    suggestion=f"Rename directory to '{skill_name}' or change name to '{parent_dir_name}'"
                )

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

        # Validate file references are max one level deep
        self._validate_file_references(content, result)

        # Validate progressive disclosure limits (file size)
        self._validate_progressive_disclosure(content, result)

    def _validate_progressive_disclosure(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate SKILL.md follows progressive disclosure limits.

        Per spec: Keep SKILL.md under 500 lines and ~5000 tokens
        (~20000 characters estimated).
        """
        # Count lines
        line_count = content.count('\n') + 1
        if line_count > MAX_SKILL_LINES:
            result.add_warning(
                message=f"SKILL.md is too long: {line_count} lines (max {MAX_SKILL_LINES})",
                suggestion="Move detailed content to separate files in references/"
            )

        # Count characters
        char_count = len(content)
        if char_count > MAX_SKILL_CHARACTERS:
            result.add_warning(
                message=f"SKILL.md is too large: {char_count} characters (max {MAX_SKILL_CHARACTERS}, ~5000 tokens)",
                suggestion="Move detailed content to separate files in references/"
            )

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

    def _validate_file_references(
        self,
        content: str,
        result: ValidationResult
    ) -> None:
        """Validate that file references are at most one level deep.

        Per spec: "Keep file references one level deep from SKILL.md.
        Avoid deeply nested reference chains."

        Valid:   scripts/extract.py, references/REFERENCE.md
        Invalid: references/subfolder/file.md, ../outside/file.md
        """
        # Find content after frontmatter
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return

        body = content[match.end():]

        # Pattern 1: Markdown links [text](path)
        md_link_pattern = re.compile(
            r'\[([^\]]+)\]\(([^)]+)\)',
            re.MULTILINE
        )

        # Pattern 2: Bare file paths (lines referencing files)
        # Match lines that look like file references
        bare_path_pattern = re.compile(
            r'^(?:[\s]*[-*]?[\s]*)?(?:See|Run|Use|Check|Load|Read|Execute)?[\s:]*'
            r'(scripts/|references/|assets/)(\S+)',
            re.MULTILINE | re.IGNORECASE
        )

        checked_paths = set()

        # Check markdown links
        for match in md_link_pattern.finditer(body):
            path = match.group(2).strip()
            # Skip URLs
            if path.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            # Skip absolute paths
            if path.startswith('/'):
                continue
            self._check_path_depth(path, checked_paths, result)

        # Check bare paths
        for match in bare_path_pattern.finditer(body):
            full_path = match.group(1) + match.group(2)
            self._check_path_depth(full_path, checked_paths, result)

    def _check_path_depth(
        self,
        path: str,
        checked_paths: set,
        result: ValidationResult
    ) -> None:
        """Check if a path exceeds one level of depth."""
        # Normalize path (remove leading ./)
        path = path.lstrip('./')

        if path in checked_paths:
            return
        checked_paths.add(path)

        # Split path into parts
        parts = path.split('/')

        # Path must start with allowed subdirs
        allowed_roots = {'scripts', 'references', 'assets'}
        if parts[0] not in allowed_roots:
            # Not a bundled resource path, skip
            return

        # Check depth: more than 2 parts means nested (subdir/file = 2 parts)
        if len(parts) > 2:
            result.add_warning(
                message=f"Deep file reference: '{path}' ({len(parts)-1} levels deep)",
                suggestion="Keep references one level deep (e.g., 'references/FILE.md', not 'references/subdir/file.md')"
            )

        # Check for parent directory traversal
        if '..' in parts:
            result.add_error(
                message=f"Invalid file reference: '{path}' references parent directory",
                field_name=None,
                suggestion="Use relative paths within the skill directory only"
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

    def _validate_version_matches_marketplace(
        self,
        skill_version: Any,
        file_path: Path,
        result: ValidationResult
    ) -> None:
        """Validate that skill version matches marketplace.json version.

        The skill version must match the main version in marketplace.json.
        """
        # First validate the skill_version is a string
        if not isinstance(skill_version, str):
            return  # Already handled by _validate_version

        # Find marketplace.json
        marketplace_path = self._find_marketplace_json(file_path)
        if not marketplace_path:
            result.add_warning(
                message="Cannot find marketplace.json for version alignment check",
                field_name="version",
                suggestion="Ensure marketplace.json exists in .claude-plugin/ directory at project root"
            )
            return

        # Read marketplace version
        marketplace_version = self._get_marketplace_version(marketplace_path)
        if not marketplace_version:
            result.add_warning(
                message="Cannot read version from marketplace.json",
                field_name="version",
                suggestion="Ensure marketplace.json has a valid 'version' field"
            )
            return

        # Compare versions
        if skill_version != marketplace_version:
            result.add_error(
                message=f"Version mismatch: skill '{skill_version}' != marketplace '{marketplace_version}'",
                field_name="version",
                suggestion=f"Update skill version to match marketplace version '{marketplace_version}'"
            )

    def _find_marketplace_json(self, file_path: Path) -> Optional[Path]:
        """Find marketplace.json by traversing up to project root."""
        current = file_path
        for _ in range(15):  # Allow deeper traversal for plugin-based skills
            # Check for .claude-plugin/marketplace.json
            marketplace = current / ".claude-plugin" / "marketplace.json"
            if marketplace.exists():
                return marketplace
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _get_marketplace_version(self, marketplace_path: Path) -> Optional[str]:
        """Read version from marketplace.json."""
        try:
            import json
            with open(marketplace_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('version')
        except (json.JSONDecodeError, KeyError, FileNotFoundError, IOError):
            return None


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


class RuleValidator(BaseValidator):
    """Validator for Claude Code Rules (.claude/rules/ format)."""

    @property
    def component_type(self) -> str:
        return "rule"

    @property
    def file_pattern(self) -> re.Pattern:
        return RULE_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return RULE_SCHEMA

    def _validate_fields(
        self,
        frontmatter: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Override: rules have no name/description fields."""
        pass

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Rule-specific validation."""
        # Validate globs field format
        if "globs" in frontmatter:
            self._validate_globs(frontmatter["globs"], result)

        # Validate file naming (kebab-case)
        self._validate_rule_filename(file_path, result)

        # Validate markdown sections
        self._validate_rule_sections(content, result)

        # Validate file size
        self._validate_rule_size(content, result)

    def _validate_globs(self, globs: Any, result: ValidationResult) -> None:
        """Validate the globs field."""
        if isinstance(globs, str):
            if not globs.strip():
                result.add_error(
                    message="Empty globs value",
                    field_name="globs",
                    suggestion="Provide a glob pattern (e.g., '**/*.java')"
                )
            elif not any(c in globs for c in ('*', '?', '{', '[')):
                result.add_warning(
                    message=f"Globs value '{globs}' contains no wildcard characters",
                    field_name="globs",
                    suggestion="Use glob patterns with wildcards (e.g., '**/*.java')"
                )
        elif isinstance(globs, list):
            result.add_error(
                message="Globs must be a string, not a list",
                field_name="globs",
                suggestion="Use a single string value (e.g., globs: \"**/*.java\"). "
                           "YAML arrays may cause loading issues with Claude Code rules."
            )
        else:
            result.add_error(
                message=f"Globs must be a string, got {type(globs).__name__}",
                field_name="globs",
                suggestion="Use a string value (e.g., globs: \"**/*.java\")"
            )

    def _validate_rule_filename(self, file_path: Path, result: ValidationResult) -> None:
        """Validate rule file uses kebab-case naming."""
        stem = file_path.stem
        if not KEBAB_CASE_PATTERN.match(stem):
            result.add_error(
                message=f"Rule filename must be kebab-case: '{file_path.name}'",
                field_name=None,
                suggestion="Rename to kebab-case (e.g., 'naming-conventions.md')"
            )

    def _validate_rule_sections(self, content: str, result: ValidationResult) -> None:
        """Validate required and recommended markdown sections."""
        match = re.search(r"\n---\s*\n", content)
        if not match:
            return

        body = content[match.end():]

        # Check required sections
        for section_key, pattern in RULE_REQUIRED_SECTIONS.items():
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                result.add_error(
                    message=f"Missing required section: '## {section_name}'",
                    suggestion=f"Add '## {section_name}' section to rule file"
                )

        # Check recommended sections
        for section_key in RULE_RECOMMENDED_SECTIONS:
            if section_key == "context":
                pattern = r"^#{1,3}\s+Context"
            elif section_key == "examples":
                pattern = r"^#{1,3}\s+Examples"
            else:
                pattern = rf"^#{{1,3}}\s+{section_key.replace('_', ' ').title()}"
            if not re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                section_name = section_key.replace("_", " ").title()
                result.add_warning(
                    message=f"Missing recommended section: '## {section_name}'",
                    suggestion=f"Consider adding '## {section_name}' section"
                )

    def _validate_rule_size(self, content: str, result: ValidationResult) -> None:
        """Validate rule file size."""
        line_count = content.count('\n') + 1
        if line_count > MAX_RULE_LINES:
            result.add_warning(
                message=f"Rule file is too long: {line_count} lines (max {MAX_RULE_LINES})",
                suggestion="Keep rule files concise and focused"
            )


class KebabCaseValidator(BaseValidator):
    """Validator for kebab-case naming convention in markdown files.

    Ensures all .md files (except exempted standard files like README.md)
    use kebab-case naming convention.
    """

    @property
    def component_type(self) -> str:
        return "naming"

    @property
    def file_pattern(self) -> re.Pattern:
        return MARKDOWN_FILE_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        # No schema needed for file naming validation
        return {"required": set(), "optional": set()}

    def can_validate(self, file_path: Path) -> bool:
        """Check if this validator can handle the given file."""
        # Only validate .md files
        if not file_path.suffix.lower() == ".md":
            return False
        # Skip exempt files
        if file_path.name in KEBAB_CASE_EXEMPT_FILES:
            return False
        # Check pattern
        return bool(self.file_pattern.search(str(file_path)))

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate that the filename follows kebab-case convention."""
        result = ValidationResult(
            file_path=file_path,
            component_type=self.component_type
        )

        # Get the filename without extension
        filename = file_path.stem

        # Check if filename follows kebab-case
        if not KEBAB_CASE_PATTERN.match(filename):
            result.add_error(
                message=f"Filename must use kebab-case: '{file_path.name}'",
                suggestion=f"Rename to '{self._to_kebab_case(filename)}.md' or similar"
            )

        return result

    def _to_kebab_case(self, name: str) -> str:
        """Convert a string to kebab-case (best effort)."""
        # Replace underscores with hyphens
        result = name.replace("_", "-")
        # Replace camelCase with kebab-case
        result = re.sub(r'([a-z])([A-Z])', r'\1-\2', result).lower()
        # Replace multiple hyphens with single
        result = re.sub(r'-+', '-', result)
        # Remove leading/trailing hyphens
        result = result.strip('-')
        return result

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Not used for kebab-case validation."""
        pass


class SkillPackageValidator(BaseValidator):
    """Validator to check for prohibited .skill package files.

    Ensures that no .skill package files exist in the project as they
    should not be committed (they are build outputs).
    """

    @property
    def component_type(self) -> str:
        return "prohibited"

    @property
    def file_pattern(self) -> re.Pattern:
        # Only match .skill files directly
        return SKILL_PACKAGE_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return {"required": set(), "optional": set()}

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate that the file is not a .skill package."""
        result = ValidationResult(
            file_path=file_path,
            component_type=self.component_type
        )

        # If this is a .skill file, it's an error
        if file_path.suffix == ".skill":
            result.add_error(
                message=f"Prohibited .skill package found: '{file_path.name}'",
                suggestion="Remove .skill files - they are build outputs and should not be committed"
            )

        return result

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Not used for skill package validation."""
        pass


class PluginVersionValidator(BaseValidator):
    """Validator for plugin manifest version alignment with marketplace.

    Ensures that plugin.json version matches marketplace.json version.
    """

    @property
    def component_type(self) -> str:
        return "plugin"

    @property
    def file_pattern(self) -> re.Pattern:
        return PLUGIN_PATTERN

    @property
    def schema(self) -> Dict[str, Set[str]]:
        return {"required": set(), "optional": set()}

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate that plugin version matches marketplace version."""
        result = ValidationResult(
            file_path=file_path,
            component_type=self.component_type
        )

        # Find marketplace.json
        marketplace_path = self._find_marketplace_json(file_path)
        if not marketplace_path:
            result.add_error(
                message="Cannot find marketplace.json for version alignment check",
                suggestion="Ensure marketplace.json exists in .claude-plugin/ directory"
            )
            return result

        # Read marketplace version
        marketplace_version = self._get_marketplace_version(marketplace_path)
        if not marketplace_version:
            result.add_error(
                message="Cannot read version from marketplace.json",
                suggestion="Ensure marketplace.json has a valid 'version' field"
            )
            return result

        # Read plugin version
        plugin_version = self._get_plugin_version(file_path)
        if not plugin_version:
            result.add_error(
                message="Cannot read version from plugin.json",
                suggestion="Ensure plugin.json has a valid 'version' field"
            )
            return result

        # Compare versions
        if plugin_version != marketplace_version:
            result.add_error(
                message=f"Version mismatch: plugin '{plugin_version}' != marketplace '{marketplace_version}'",
                suggestion=f"Align plugin version with marketplace version '{marketplace_version}'"
            )

        return result

    def _find_marketplace_json(self, file_path: Path) -> Optional[Path]:
        """Find marketplace.json by traversing up to project root."""
        current = file_path.parent
        for _ in range(10):  # Limit search depth
            marketplace = current / ".claude-plugin" / "marketplace.json"
            if marketplace.exists():
                return marketplace
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _get_marketplace_version(self, marketplace_path: Path) -> Optional[str]:
        """Read version from marketplace.json."""
        try:
            import json
            with open(marketplace_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('version')
        except (json.JSONDecodeError, KeyError, FileNotFoundError, IOError):
            return None

    def _get_plugin_version(self, plugin_path: Path) -> Optional[str]:
        """Read version from plugin.json."""
        try:
            import json
            with open(plugin_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('version')
        except (json.JSONDecodeError, KeyError, FileNotFoundError, IOError):
            return None

    def _validate_specific(
        self,
        file_path: Path,
        frontmatter: Dict[str, Any],
        content: str,
        result: ValidationResult
    ) -> None:
        """Not used for plugin version validation."""
        pass


class PluginJsonValidator:
    """Validator for plugin.json files - verifies component registration."""

    PLUGIN_JSON_PATTERN = re.compile(r"plugin\.json$")

    def can_validate(self, file_path: Path) -> bool:
        """Check if this validator can handle the given file."""
        return bool(self.PLUGIN_JSON_PATTERN.search(str(file_path)))

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate plugin.json and check component registration."""
        result = ValidationResult(
            file_path=file_path,
            component_type="plugin.json"
        )

        # Read plugin.json
        try:
            import json
            content = file_path.read_text(encoding="utf-8")
            plugin_data = json.loads(content)
        except FileNotFoundError:
            result.add_error(
                message=f"File not found: {file_path}",
                suggestion="Verify the file path is correct"
            )
            return result
        except json.JSONDecodeError as e:
            result.add_error(
                message=f"Invalid JSON: {e}",
                suggestion="Fix the JSON syntax error"
            )
            return result

        # Get plugin directory
        plugin_dir = file_path.parent.parent

        # Validate each component type
        self._validate_components(
            plugin_data, plugin_dir, "skills", result
        )
        self._validate_components(
            plugin_data, plugin_dir, "agents", result
        )
        self._validate_components(
            plugin_data, plugin_dir, "commands", result
        )
        self._validate_components(
            plugin_data, plugin_dir, "rules", result
        )

        # Check for unregistered components
        self._check_unregistered_components(
            plugin_data, plugin_dir, "skills", result
        )
        self._check_unregistered_components(
            plugin_data, plugin_dir, "agents", result
        )
        self._check_unregistered_components(
            plugin_data, plugin_dir, "commands", result
        )
        self._check_unregistered_components(
            plugin_data, plugin_dir, "rules", result
        )

        return result

    def _validate_components(
        self,
        plugin_data: dict,
        plugin_dir: Path,
        component_type: str,
        result: ValidationResult
    ) -> None:
        """Validate that registered components exist on filesystem."""
        components = plugin_data.get(component_type, [])

        for component_path in components:
            full_path = plugin_dir / component_path

            if component_type == "skills":
                # Skills point to directories containing SKILL.md
                skill_md = full_path / "SKILL.md"
                if not skill_md.exists():
                    result.add_error(
                        message=f"Skill not found: '{component_path}'",
                        field_name=component_type,
                        suggestion=f"Ensure '{component_path}/SKILL.md' exists or remove from plugin.json"
                    )
            else:
                # Agents and commands point directly to .md files
                if not full_path.exists():
                    result.add_error(
                        message=f"{component_type[:-1].title()} not found: '{component_path}'",
                        field_name=component_type,
                        suggestion=f"Ensure '{component_path}' exists or remove from plugin.json"
                    )
                elif not full_path.suffix == ".md":
                    result.add_error(
                        message=f"{component_type[:-1].title()} must be a .md file: '{component_path}'",
                        field_name=component_type,
                        suggestion="Use .md extension for agent/command files"
                    )

    def _check_unregistered_components(
        self,
        plugin_data: dict,
        plugin_dir: Path,
        component_type: str,
        result: ValidationResult
    ) -> None:
        """Check for components on filesystem that are not registered in plugin.json."""
        registered = set(plugin_data.get(component_type, []))

        # Get the directory for this component type
        component_dir = plugin_dir / component_type
        if not component_dir.exists():
            return

        if component_type == "skills":
            # Skills are directories with SKILL.md
            for item in component_dir.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    relative_path = f"./{component_type}/{item.name}"
                    if relative_path not in registered:
                        result.add_error(
                            message=f"Unregistered skill: '{item.name}'",
                            field_name=component_type,
                            suggestion=f"Add './{component_type}/{item.name}' to plugin.json skills array"
                        )
        else:
            # Agents and commands are .md files
            for item in component_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    relative_path = f"./{component_type}/{item.name}"
                    if relative_path not in registered:
                        result.add_error(
                            message=f"Unregistered {component_type[:-1]}: '{item.name}'",
                            field_name=component_type,
                            suggestion=f"Add './{component_type}/{item.name}' to plugin.json {component_type} array"
                        )


class ValidatorFactory:
    """Factory for creating appropriate validators."""

    _validators: List[Any] = [
        SkillValidator(),
        AgentValidator(),
        CommandValidator(),
        RuleValidator(),
        KebabCaseValidator(),
        SkillPackageValidator(),
        PluginVersionValidator(),
        PluginJsonValidator(),
    ]

    @classmethod
    def get_validator(cls, file_path: Path) -> Optional[Any]:
        """Get the appropriate validator for a file."""
        for validator in cls._validators:
            if validator.can_validate(file_path):
                return validator
        return None

    @classmethod
    def get_all_patterns(cls) -> List[re.Pattern]:
        """Get all file patterns for component files."""
        return [v.file_pattern for v in cls._validators if hasattr(v, 'file_pattern')]
