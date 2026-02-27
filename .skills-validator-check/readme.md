# Skills Validator Check

A Python-based validation system for Claude Code plugin components (Skills, Agents, Commands) ensuring format compliance and quality standards.

## Quick Start

```bash
# Validate all staged files (from pre-commit hook)
python3 .skills-validator-check/validators/cli.py

# Validate all components in repository
python3 .skills-validator-check/validators/cli.py --all

# Validate specific files
python3 .skills-validator-check/validators/cli.py --files skills/spring-boot/spring-boot-actuator/SKILL.md

# JSON output for CI/CD pipelines
python3 .skills-validator-check/validators/cli.py --all --format json

# Quiet mode (errors only)
python3 .skills-validator-check/validators/cli.py -q
```

## What It Validates

### All Components
- YAML frontmatter with `---` delimiters
- Required fields presence and valid schema
- Name format (kebab-case, max 64 chars, no reserved words)
- Description quality (max 1024 chars, must contain WHAT and WHEN keywords)

### Skills (`SKILL.md`)
- Required fields: `name`, `description`, `allowed-tools`
- Required sections: Overview, When to Use, Instructions, Examples
- Directory structure validation
- Prohibited files and fields detection

### Agents (`*.md` in `agents/`)
- Required fields: `name`, `description`
- Optional fields: `tools`, `model`, `permissionMode`, `skills`

### Commands (`*.md` in `commands/`)
- Required fields: `description`
- Optional fields: `argument-hint`, `allowed-tools`, `model`, `disable-model-invocation`

## Command Line Options

| Option | Description |
|--------|-------------|
| `--version` | Show version information |
| `--files <paths>` | Validate specific file paths (comma-separated) |
| `--all` | Validate all component files in repository |
| `--format <format>` | Output format: `console`, `plain`, or `json` (default: console) |
| `-v, --verbose` | Show verbose output including valid files |
| `-q, --quiet` | Suppress warnings, show only errors |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed (no errors) |
| 1 | Validation errors found |
| 2 | System error (exception) |

## Supported Directory Structures

The validator supports both architectures:

```
Legacy:                          Multi-plugin:
├── skills/category/SKILL.md      ├── plugins/plugin-name/skills/category/SKILL.md
├── agents/name.md               ├── plugins/plugin-name/agents/name.md
└── .claude/commands/name.md    └── plugins/plugin-name/commands/name.md
```

## Installation

```bash
# Install as git pre-commit hook
./.skills-validator-check/install-hooks.sh
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=validators

# Format code
black .

# Type checking
mypy .
```

## Security Scanning

The validation system includes a security scanner powered by [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan) from Invariant Labs. It detects prompt injection attacks, malware payloads, sensitive data handling issues, and hard-coded secrets in skill definitions.

### Prerequisites

Install [uv](https://github.com/astral-sh/uv) (provides `uvx` runner):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Usage

```bash
# Scan all skills in all plugins
python3 .skills-validator-check/validators/mcp_scan_checker.py --all

# Scan a specific plugin
python3 .skills-validator-check/validators/mcp_scan_checker.py --plugin developer-kit-java

# Scan a specific skill directory
python3 .skills-validator-check/validators/mcp_scan_checker.py --path plugins/developer-kit-java/skills/spring-boot-actuator

# Verbose output
python3 .skills-validator-check/validators/mcp_scan_checker.py --all -v

# Via Makefile
make security-scan
```

### CI/CD Integration

Security scans run automatically via GitHub Actions (`.github/workflows/security-scan.yml`) on:
- Every push to `main` and `develop` branches
- Every pull request targeting `main` or `develop`

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No security issues (or only warnings) |
| 1 | Critical security issues found |
| 2 | System error (mcp-scan unavailable) |

### Known Limitations

- Requires `uvx` or `pipx` to run mcp-scan
- Scan timeout is set to 5 minutes
- False positives should be documented in issue tracker
