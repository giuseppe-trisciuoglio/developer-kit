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

# Check remote reachability for external HTTP(S) links
python3 .skills-validator-check/validators/cli.py --all --check-external-urls
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
| `--check-external-urls` | Enable remote reachability checks for external HTTP(S) links |

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

### Per-Component Allowlist (False Positive Suppression)

Some skills legitimately reference external content (e.g., RAG patterns, MCP server integrations, messaging queues). These trigger W011/W012 warnings that are false positives. The allowlist file `.skills-validator-check/mcp-scan-allowlist.json` provides **granular, per-component suppression** with **domain census validation**.

#### How It Works

1. Each allowlisted component specifies which warning codes (e.g., `W011`, `W012`) to suppress
2. Each component also declares the **external domains** it references
3. During the scan, the checker extracts all HTTP(S) URLs from the skill's files
4. If a skill references a domain **not listed** in the allowlist, the warning is **NOT suppressed** and the check fails
5. Placeholder domains (`localhost`, `example.com`, `myapp.com`, etc.) are automatically excluded from validation

#### Allowlist Entry Format

```json
{
  "path": "plugins/developer-kit-java/skills/qdrant",
  "allow": ["W011"],
  "domains": [
    "github.com",
    "qdrant.tech",
    "langchain4j.dev"
  ],
  "reason": "Qdrant RAG skill teaches document ingestion into vector stores."
}
```

| Field | Description |
|-------|-------------|
| `path` | Component path relative to repo root |
| `allow` | Warning codes to suppress (e.g., `W011`, `W012`) |
| `domains` | Censused external domains — new domains cause the check to fail |
| `reason` | Justification for why the warning is a false positive |

#### Adding a New Allowlist Entry

When a skill legitimately triggers W011/W012:

1. **Verify** the warning is a genuine false positive (the skill is documentation, not executable code)
2. **Collect domains** — extract all external URLs from the skill files:
   ```bash
   grep -roh 'https\?://[^ "'\''<>)}\]*' plugins/your-plugin/skills/your-skill/ | sort -u
   ```
3. **Add the entry** to `mcp-scan-allowlist.json` with the component path, allowed codes, domains, and reason
4. **Run the scan** to verify:
   ```bash
   python3 .skills-validator-check/validators/mcp_scan_checker.py --path plugins/your-plugin/skills/your-skill -v
   ```

#### Domain Census: Why It Matters

If someone modifies an allowlisted skill and adds a reference to a new external domain (e.g., `https://untrusted-site.com`), the domain won't be in the census. The checker will detect the uncensored domain and **refuse to suppress** the warning, causing the check to fail with a clear message:

```
✗ FAIL  [W011] Third-party content exposure detected
       ↳ Uncensored domain(s): untrusted-site.com
       ↳ Add to mcp-scan-allowlist.json to suppress
```

This ensures that every external domain referenced by an allowlisted skill is explicitly reviewed and approved.

### Known Limitations

- Requires `uvx` or `pipx` to run mcp-scan
- Scan timeout is set to 2 minutes per component
- URL extraction covers `.md`, `.txt`, `.yaml`, `.yml`, `.json` files only
- Template variables (`${...}`) in URLs are automatically excluded from domain extraction
