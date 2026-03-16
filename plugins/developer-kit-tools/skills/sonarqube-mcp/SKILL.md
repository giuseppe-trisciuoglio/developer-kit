---
name: sonarqube-mcp
description: Provides SonarQube and SonarCloud integration patterns via the Model Context Protocol (MCP) server. Enables quality gate monitoring, issue discovery and triaging, pre-push code analysis, and rule education directly in the agent workflow. Use when the user wants to check quality gates, search for Sonar issues, analyze code snippets before committing, or understand SonarQube rules. Triggers on "sonarqube", "sonarcloud", "quality gate", "sonar issues", "analyze with sonar", "check sonar", "sonar rule", "pre-push analysis".
allowed-tools: Read
---

# SonarQube MCP Integration

Leverage SonarQube and SonarCloud capabilities directly through the Model Context Protocol (MCP) server to enforce code quality, discover issues, and run pre-push analysis inside the agent workflow.

## Overview

This skill provides instructions and patterns for using the [SonarQube MCP Server](https://github.com/SonarSource/sonarqube-mcp-server) tools. It enables automated workflows for:

- Checking quality gate status before merges or deployments
- Discovering and triaging issues by severity and project
- Analyzing code snippets locally before committing (shift-left)
- Understanding SonarQube rules with full documentation

## When to Use

Use this skill when:

- The user wants to check if a project passes its quality gate before merging a PR
- The user wants to find critical or blocker issues in one or more SonarQube projects
- The user wants to analyze a code snippet for issues before pushing to CI
- The user wants to understand why a specific Sonar rule flagged their code
- The user asks for pre-commit or pre-push quality feedback

**Trigger phrases:** "check quality gate", "sonarqube quality gate", "find sonar issues", "search sonar issues", "analyze code with sonar", "check sonar rule", "sonarcloud issues", "pre-push sonar check", "sonar pre-commit"

## Prerequisites

The plugin includes a `.mcp.json` that starts the SonarQube MCP Server automatically via Docker. Before using this skill, set the required environment variables:

**SonarQube Server (remote):**
```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="https://sonarqube.mycompany.com"
```

**SonarQube Server (local Docker on macOS/Windows):**
```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="http://host.docker.internal:9000"
# Do NOT use localhost or 127.0.0.1 — Docker containers cannot reach them
```

**SonarCloud:**
```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_ORG="your-org-key"   # required for SonarCloud
# SONARQUBE_URL is not set for SonarCloud
```

**Configuration file (all platforms):** The MCP server reads credentials from `~/.sonarqube_mcp`. Create this file once:

```bash
# ~/.sonarqube_mcp
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="http://host.docker.internal:9000"  # local SonarQube
# export SONARQUBE_ORG="your-org-key"                   # SonarCloud only
```

> **Note for macOS:** Claude Code is a GUI application and does not inherit variables exported in `.zshrc`. The `~/.sonarqube_mcp` file is sourced directly by the MCP server launcher, so no `launchctl` or shell restart is needed.

**Requirements:**
- Docker must be installed and running
- `SONARQUBE_TOKEN` is always required
- `SONARQUBE_URL` is required for SonarQube Server (use `host.docker.internal` for local instances)
- `SONARQUBE_ORG` is required for SonarCloud (omit `SONARQUBE_URL` in that case)

Verify MCP tool availability before proceeding:
- Tool names follow the pattern: `mcp__sonarqube-mcp__<tool-name>`

If the MCP server fails to start, check that Docker is running and the environment variables (`SONARQUBE_TOKEN`, `SONARQUBE_URL` or `SONARQUBE_ORG`) are set. Reference: [mcp/sonarqube on Docker Hub](https://hub.docker.com/r/mcp/sonarqube)

## Reference Documents

- `references/metrics.md` — Common SonarQube metrics and their meaning
- `references/severity-levels.md` — Sonar severity levels and impact categories
- `references/best-practices.md` — Workflows for PR checks and pre-commit analysis
- `references/llm-context.md` — Tool selection guide and parameter mapping for LLM agents

## Instructions

### Step 1: Identify the Required Operation

Determine which operation the user needs:

| User Intent | Tool to Use |
|---|---|
| Check if project passes quality gate | `get_project_quality_gate_status` |
| Find critical issues in a project | `search_sonar_issues_in_projects` |
| Analyze code before committing | `analyze_code_snippet` |
| Understand a flagged rule | `show_rule` |
| Get detailed project metrics | `get_component_measures` |
| Mark an issue as false positive | `change_sonar_issue_status` |

If the user's intent is ambiguous, ask for the project key and the goal before proceeding.

### Step 2: Quality Gate Monitoring

Use `get_project_quality_gate_status` to verify a project meets its quality standards.

**Parameters:**
- `projectKey` (string) — Project key in SonarQube/SonarCloud
- `pullRequest` (string, optional) — Pull request ID for PR-specific gate check
- `analysisId` (string, optional) — Specific analysis ID

> Note: There is no `branch` parameter on this tool. Without a `pullRequest` or `analysisId`, the tool returns the quality gate status for the default branch.

**Pattern — Check default branch gate:**

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "my-application"
  }
}
```

**Pattern — Check PR gate before merge:**

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "backend-service",
    "pullRequest": "456"
  }
}
```

**Interpreting the response:**
- `status: "OK"` — Gate passed, safe to merge/deploy
- `status: "ERROR"` — Gate failed; check `conditions` array for failing metrics
- Each condition shows: `metricKey`, `actualValue`, `errorThreshold`, `comparator`

For more on metric keys, see `references/metrics.md`.

### Step 3: Issue Discovery and Triaging

Use `search_sonar_issues_in_projects` to find and prioritize issues.

**Parameters:**
- `projects` (array, optional) — List of project keys; omit to search all accessible projects
- `severities` (array, optional) — Filter: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
- `pullRequestId` (string, optional) — Limit search to a specific PR
- `p` (integer, optional) — Page number (default: 1)
- `ps` (integer, optional) — Page size (default: 100, max: 500)

**Pattern — Find blockers and critical issues:**

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-backend", "my-frontend"],
    "severities": ["BLOCKER", "HIGH"],
    "p": 1,
    "ps": 50
  }
}
```

**Pattern — Search issues in a PR:**

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-service"],
    "pullRequestId": "123",
    "severities": ["HIGH", "MEDIUM"],
    "p": 1,
    "ps": 100
  }
}
```

**Managing issues with `change_sonar_issue_status`:**

Use this to mark false positives or accepted technical debt:

```json
{
  "name": "change_sonar_issue_status",
  "arguments": {
    "key": "AY1234",
    "status": "falsepositive",
    "comment": "This pattern is safe in our context because..."
  }
}
```

Valid statuses: `falsepositive` (not a real issue), `accept` (acknowledged technical debt), `reopen` (reset to open)

> Always present the list of issues to the user before changing their status. Never autonomously mark issues as false positives without explicit user confirmation.

### Step 4: Pre-Push Analysis (Shift Left)

Use `analyze_code_snippet` to run SonarQube analysis on code before committing.

**Parameters:**
- `projectKey` (string) — Project key for context
- `fileContent` (string, **required**) — Full content of the file to analyze
- `language` (string, optional) — Language hint for better accuracy
- `codeSnippet` (string, optional) — Narrow results to a specific sub-range within `fileContent`

**Supported languages:** `javascript`, `typescript`, `python`, `java`, `go`, `php`, `cs`, `cpp`, `kotlin`, `ruby`, `scala`, `swift`

**Pattern — Analyze TypeScript file before commit:**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-typescript-app",
    "fileContent": "async function fetchUser(id: string) {\n  const query = `SELECT * FROM users WHERE id = ${id}`;\n  return db.execute(query);\n}",
    "language": "typescript"
  }
}
```

**Pattern — Analyze Python file:**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-python-service",
    "fileContent": "import pickle\n\ndef load_model(path):\n    with open(path, 'rb') as f:\n        return pickle.load(f)",
    "language": "python"
  }
}
```

**Response interpretation:**
- Each issue includes: `ruleKey`, severity, clean code attribute, impact category, line number, quick fix availability
- Address `CRITICAL` and `HIGH` severity issues before committing
- Use `show_rule` with the `ruleKey` value for any unfamiliar rule

### Step 5: Rule Education

Use `show_rule` to understand why a rule exists and how to fix flagged code.

**Parameters:**
- `key` (string) — Rule key in format `<language>:<rule-id>` (e.g., `typescript:S1082`, `java:S2068`)

**Pattern — Get rule documentation:**

```json
{
  "name": "show_rule",
  "arguments": {
    "key": "typescript:S1082"
  }
}
```

**Response includes:** rule name, type, severity, full description, tags (e.g., `cwe`, `owasp-a2`), language, remediation effort estimate, code examples (non-compliant vs compliant).

### Step 6: Get Component Measures

Use `get_component_measures` to retrieve detailed metrics for a project, directory, or file.

**Parameters:**
- `projectKey` (string) — Project key in SonarQube/SonarCloud
- `pullRequest` (string, optional) — PR ID for PR-scoped metrics
- `metricKeys` (array) — List of metric keys to retrieve

**Common metric keys:** `coverage`, `bugs`, `vulnerabilities`, `code_smells`, `complexity`, `cognitive_complexity`, `ncloc`, `duplicated_lines_density`, `new_coverage`, `new_bugs`

**Pattern — Project health dashboard:**

```json
{
  "name": "get_component_measures",
  "arguments": {
    "projectKey": "my-project-key",
    "metricKeys": ["coverage", "bugs", "vulnerabilities", "code_smells", "ncloc"]
  }
}
```

For full metric reference, see `references/metrics.md`.

### Step 7: Present Results to User

After each tool call:
- Summarize findings in human-readable form
- Flag issues that require attention (BLOCKER, HIGH severity)
- Propose next actions based on findings
- Wait for user confirmation before taking remediation steps (e.g., changing issue status, modifying code)

## Examples

### Example 1: Pre-Merge Quality Gate Check

**User request:** "Check if the quality gate passes for project `backend-api` on PR #234"

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "backend-api",
    "pullRequest": "234"
  }
}
```

**If gate fails:** Extract failing conditions, present them to the user, then use `search_sonar_issues_in_projects` filtered by the same PR to show the actual issues.

### Example 2: Shift-Left Analysis Before Push

**User request:** "Analyze this Go function before I push it"

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-go-service",
    "fileContent": "func handler(w http.ResponseWriter, r *http.Request) {\n  id := r.URL.Query().Get(\"id\")\n  query := fmt.Sprintf(\"SELECT * FROM orders WHERE id = %s\", id)\n  rows, _ := db.Query(query)\n  // ...\n}",
    "language": "go"
  }
}
```

Present findings → for each issue, optionally call `show_rule` with the `ruleKey` value to explain the fix.

### Example 3: Triage BLOCKER Issues in a Project

**User request:** "Show me all blocker issues in `payment-service`"

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["payment-service"],
    "severities": ["BLOCKER"],
    "p": 1,
    "ps": 50
  }
}
```

Group results by category (Security, Reliability, Maintainability) and present to user. Offer to call `show_rule` for unfamiliar rules.

## Best Practices

1. **Always check quality gate before merge** — Run `get_project_quality_gate_status` as part of any PR review workflow
2. **Shift left on security issues** — Use `analyze_code_snippet` during development, not only in CI
3. **Prioritize by severity** — Address BLOCKER and HIGH issues first; document decisions for MEDIUM and LOW
4. **Use `show_rule` for unfamiliar keys** — Never dismiss a rule without understanding its intent
5. **Paginate large result sets** — Use `p` and `ps` parameters; handle multi-page responses for complete coverage
6. **Never change issue status autonomously** — Always present issues to the user and get explicit confirmation before calling `change_sonar_issue_status`
7. **Provide language hints** — Specify `language` in `analyze_code_snippet` for more accurate analysis

## Constraints and Warnings

- MCP server must be configured and running; verify tool availability before use
- `analyze_code_snippet` analyzes snippets in isolation — full project context may affect results in CI
- Issue status changes (false positive, won't fix) require appropriate SonarQube permissions
- SonarCloud and SonarQube Server APIs are mostly compatible but some features differ; check `references/llm-context.md`
- Pagination is required for projects with many issues; check `paging.total` and `paging.pageSize` in the response to determine whether to iterate further pages
- Quality gate status reflects the last completed analysis — trigger a new analysis if the code has changed
