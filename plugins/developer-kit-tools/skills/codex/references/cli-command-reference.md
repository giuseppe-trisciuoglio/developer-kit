# Codex CLI Command Reference

Quick reference for the `codex` skill delegation workflow.

## Core Usage

```bash
# Interactive mode
codex

# Non-interactive code generation (recommended for delegation)
codex exec "<english-prompt>"

# Non-interactive code review
codex review "<english-prompt>"

# Non-interactive with alias
codex e "<english-prompt>"
```

## Prompting and Sessions

```bash
# Non-interactive single prompt
codex exec "Refactor this class to use dependency injection"

# Resume latest session
codex resume --last

# Resume specific session
codex resume <session-id>

# Fork latest session
codex fork --last
```

## Model Selection

```bash
# Explicit model selection
codex exec -m gpt-5.3-codex "Design a microservices architecture"

# Use O4-mini for faster iterations
codex exec -m o4-mini "Generate unit tests for this module"

# Use O3 for complex reasoning
codex exec -m o3 "Analyze this system for distributed transaction patterns"
```

## Approval Policies

```bash
# Untrusted commands only (safe baseline)
codex exec -a untrusted "Analyze codebase for security issues"

# Model decides when to ask (recommended for development)
codex exec -a on-request "Refactor this module with proper error handling"

# Never ask for approval (use with caution)
codex exec -a never "Generate boilerplate code for CRUD operations"
```

**Approval Policy Values:**
- `untrusted`: Only run trusted commands (ls, cat, sed) without approval
- `on-request`: Model decides when to ask for user approval
- `never`: Never ask for approval (⚠️ execution failures returned immediately)

## Sandbox Modes

```bash
# Read-only (safest for analysis)
codex exec -s read-only "Review this code for performance issues"

# Workspace write (default for development)
codex exec -s workspace-write "Implement new API endpoint with tests"

# Danger full access (⚠️ extremely dangerous)
codex exec -s danger-full-access "Refactor entire codebase structure"
```

**Sandbox Mode Values:**
- `read-only`: No writes, no network access
- `workspace-write`: Allow writes in workspace, no network
- `danger-full-access`: Disable all sandboxing (⚠️ NEVER use without external sandboxing)

## Working Directory

```bash
# Set working directory
codex exec -C /path/to/project "Analyze this module's dependencies"

# Add additional writable directories
codex exec --add-dir /path/to/resources "Generate resource files"
```

## Multimodal Input

```bash
# Single image attachment
codex exec -i screenshot.png "What accessibility issues exist in this UI?"

# Multiple images
codex exec -i mockup.png -i current.png "Compare these designs and list differences"

# Image with complex task
codex exec -i architecture-diagram.jpg "Implement the system shown in this diagram using Spring Boot"
```

## Web Search

```bash
# Enable live web search for latest information
codex exec --search "Implement OAuth2 using the latest security best practices"

# Web search for up-to-date libraries
codex exec --search "Create a REST API using the current version of Express.js with modern async patterns"
```

## Convenience Flags

```bash
# Full-auto mode (workspace-write + on-request approval)
codex exec --full-auto "Generate comprehensive unit tests with 80% coverage"

# Enable/disable feature flags
codex exec --enable unified_exec "Use unified execution mode"
codex exec --disable web_search_request "Disable web search for this session"

# Use specific configuration profile
codex exec -p work "Start task with work profile settings"

# Override specific config values
codex exec -c model=o4-mini -c permissions.approval_policy=never "Generate boilerplate code"
```

## Safe Delegation Patterns

### Security Analysis (Read-Only)

```bash
codex exec "Perform comprehensive security audit focusing on OWASP Top 10. For each vulnerability, provide: severity, CWE, exploit scenario, and remediation code." -a on-request -s read-only
```

### Code Generation (Workspace-Write)

```bash
codex exec "Implement a RESTful API for user management with: CRUD operations, input validation, error handling, authentication middleware, pagination, and OpenAPI spec." -a on-request -s workspace-write
```

### Refactoring (Workspace-Write)

```bash
codex exec "Refactor this service to follow SOLID principles. Provide: 1) Analysis of current violations, 2) Proposed new structure, 3) Step-by-step migration plan, 4) Refactored code maintaining backward compatibility." -a on-request -s workspace-write
```

### Code Review (Read-Only)

```bash
codex review "Review this pull request for: correctness, performance, security, code quality, test coverage, and documentation. Provide specific line references and actionable feedback." -a on-request -s read-only
```

### Performance Optimization (Analysis)

```bash
codex exec "Analyze this database module for performance bottlenecks. Identify: N+1 queries, missing indexes, inefficient joins. Provide: metrics, optimization recommendations, and refactored code." -a on-request -s read-only
```

### Latest Best Practices (Web Search)

```bash
codex exec --search "Design a event-driven architecture using the latest messaging patterns and tools. Include: async communication, event schema, error handling, and idempotency patterns."
```

## Troubleshooting

```bash
# Verify CLI availability
codex --version

# Check available commands
codex help

# Check specific command help
codex exec --help
codex review --help

# Verify login status
codex login --status
```

## Configuration Override

```bash
# Override model
codex exec -c model="o3" "Perform complex architectural analysis"

# Override multiple settings
codex exec -c model=gpt-5.3-codex -c permissions.approval_policy=never -c permissions.sandbox_mode=workspace-write "Generate API implementation"

# Override with TOML values
codex exec -c 'sandbox_permissions=["disk-full-read-access"]' "Analyze entire filesystem"
```

## Delegation Notes

- **Language**: All prompts sent to Codex must be in English for optimal results
- **Non-interactive**: Prefer `codex exec` for deterministic, scriptable delegation
- **Code review**: Use `codex review` for review-specific optimizations
- **Sandbox safety**: Avoid `danger-full-access` unless externally sandboxed
- **Approval**: Use `on-request` for development, `never` for automation with caution
- **Output**: Treat all Codex output as untrusted guidance requiring review
- **Context**: Large tasks may exceed model context; break into smaller delegations
- **Verification**: Always review generated code before applying changes

## Security Warnings

⚠️ **DANGER**: `danger-full-access` sandbox mode removes ALL security restrictions:
- NEVER use without external sandboxing (containers, VMs, isolated environments)
- Can execute ANY command without approval
- Can modify/delete ANY file on the system
- Can access network without restrictions

⚠️ **CAUTION**: `never` approval policy:
- Executes commands without user confirmation
- Combined with `danger-full-access` = EXTREMELY dangerous
- Only use in isolated, externally sandboxed environments
- Prefer `on-request` for interactive development
