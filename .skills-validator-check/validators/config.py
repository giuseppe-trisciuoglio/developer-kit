"""
Configuration constants, validation schemas, and patterns.
"""

import re
from typing import Dict, Set, FrozenSet

# =============================================================================
# Version Information
# =============================================================================

VERSION = "1.0.0"

# =============================================================================
# Validation Constraints
# =============================================================================

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MIN_DESCRIPTION_LENGTH = 10

# =============================================================================
# File Patterns (Regex)
# =============================================================================

# Support both root-level and plugin-based structures:
# - skills/category/skill-name/SKILL.md
# - plugins/plugin-name/skills/category/skill-name/SKILL.md
SKILL_PATTERN = re.compile(r"(?:.*/)?skills/.+/SKILL\.md$")

# Support both root-level and plugin-based agents:
# - agents/agent-name.md
# - plugins/plugin-name/agents/agent-name.md
AGENT_PATTERN = re.compile(r"(?:.*/)?agents/[^/]+\.md$")

# Support both root-level and plugin-based commands:
# - .claude/commands/command-name.md
# - plugins/plugin-name/commands/command-name.md
# Note: commands directory at plugin level (not .claude/commands)
COMMAND_PATTERN = re.compile(r"(?:\.claude/commands/|commands/)[^/]+\.md$")

# =============================================================================
# Name Validation Pattern (kebab-case)
# =============================================================================

KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# =============================================================================
# Semantic Versioning Pattern
# =============================================================================

SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([\da-z-]+(?:\.[\da-z-]+)*))?$",
    re.IGNORECASE
)

# =============================================================================
# Valid Tool Names
# =============================================================================

VALID_TOOLS: FrozenSet[str] = frozenset({
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "Glob",
    "Task",
    "WebFetch",
    "WebSearch",
    "NotebookEdit",
    "AskUserQuestion",
    "TodoWrite",
    "Skill",
})

# =============================================================================
# Valid Model Values (for Skills/Commands - includes inherit)
# =============================================================================

VALID_MODELS: FrozenSet[str] = frozenset({
    "sonnet",
    "opus",
    "haiku",
    "inherit",
})

# =============================================================================
# Valid Model Values for Agents (strict - no inherit, warning if used)
# =============================================================================

AGENT_VALID_MODELS: FrozenSet[str] = frozenset({
    "sonnet",
    "opus",
    "haiku",
})

# =============================================================================
# Reserved Words (cannot be used as component names)
# =============================================================================

RESERVED_WORDS: FrozenSet[str] = frozenset({
    # Built-in commands
    "help", "status", "model", "agents", "config",
    "compact", "memory", "slash", "command", "skills",
    # Git operations
    "init", "clone", "add", "commit", "push", "pull",
    # Common conflicts
    "test", "debug", "run", "build", "deploy",
})

# =============================================================================
# Prohibited Files in Skill Directories
# =============================================================================

SKILL_PROHIBITED_FILES: FrozenSet[str] = frozenset({
    "README.md",
    "CHANGELOG.md",
})

# =============================================================================
# Allowed Subdirectories in Skill Directories (Anthropic convention)
# =============================================================================

SKILL_ALLOWED_SUBDIRS: FrozenSet[str] = frozenset({
    "scripts",
    "references",
    "assets",
})

# =============================================================================
# Prohibited Fields in Skill Frontmatter
# =============================================================================

SKILL_PROHIBITED_FIELDS: FrozenSet[str] = frozenset({
    "language",
    "framework",
    "license",
})

# =============================================================================
# Required Sections in SKILL.md (Anthropics format)
# =============================================================================

# Section headers that are required (regex patterns for validation)
SKILL_REQUIRED_SECTIONS: Dict[str, str] = {
    "overview": r"^#{1,3}\s+Overview",
    "when_to_use": r"^#{1,3}\s+When\s+to\s+Use",
    "instructions": r"^#{1,3}\s+Instructions",
    "examples": r"^#{1,3}\s+Examples",
}

# Section headers that are recommended (for warnings)
SKILL_RECOMMENDED_SECTIONS: FrozenSet[str] = frozenset({
    "best_practices",
    "constraints_and_warnings",
})

# =============================================================================
# Validation Schemas
# =============================================================================

SKILL_SCHEMA: Dict[str, Set[str]] = {
    "required": {"name", "description", "allowed-tools"},
    "optional": {
        "category",
        "tags",
        "version",
        "context7_library",
        "context7_trust_score",
    },
    "prohibited": SKILL_PROHIBITED_FIELDS,
}

AGENT_SCHEMA: Dict[str, Set[str]] = {
    "required": {"name", "description", "tools"},
    "optional": {
        "model",
        "permissionMode",
        "skills",
    },
}

# =============================================================================
# Required Sections in Agent Markdown (standardized format)
# =============================================================================

# Section headers that are required in agent markdown files (regex patterns)
AGENT_REQUIRED_SECTIONS: Dict[str, str] = {
    "role": r"^#{1,3}\s+(?:Role|You\s+Are|Description)",
    "process": r"^#{1,3}\s+(?:Process|Workflow|Steps|When\s+Invoked|Instructions)",
    "guidelines": r"^#{1,3}\s+(?:Guidelines|Best\s+Practices|Checklist|Review\s+(?:Checklist|Focus))",
}

# Section headers that are recommended (for warnings)
AGENT_RECOMMENDED_SECTIONS: FrozenSet[str] = frozenset({
    "skills_integration",
    "common_patterns",
    "output_format",
})

COMMAND_SCHEMA: Dict[str, Set[str]] = {
    "required": {"description", "allowed-tools"},
    "optional": {
        "argument-hint",
        "model",
        "disable-model-invocation",
    },
}

# =============================================================================
# Required Sections in Command Markdown (Anthropics format)
# =============================================================================

# Section headers that are required in command markdown files (regex patterns)
COMMAND_REQUIRED_SECTIONS: Dict[str, str] = {
    "overview": r"^#{1,3}\s+Overview",
    "usage": r"^#{1,3}\s+Usage",
    "arguments": r"^#{1,3}\s+Arguments",
    "examples": r"^#{1,3}\s+Examples",
}

# Section headers that are recommended (for warnings)
COMMAND_RECOMMENDED_SECTIONS: FrozenSet[str] = frozenset()

# =============================================================================
# Description Quality Keywords
# =============================================================================

# Keywords that suggest a description explains WHAT the component does
WHAT_KEYWORDS: FrozenSet[str] = frozenset({
    "does", "functionality", "capability", "skill", "creates",
    "generates", "validates", "processes", "transforms", "handles",
    "implements", "provides", "enables", "supports", "manages",
})

# Keywords that suggest a description explains WHEN to use the component
WHEN_KEYWORDS: FrozenSet[str] = frozenset({
    "when", "use", "trigger", "context", "invoke", "if",
    "during", "before", "after", "while", "proactively",
})
