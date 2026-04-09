# MCP Integration Guide

Guide for integrating with NotebookLM and SonarQube through MCP servers.

## Overview

This plugin provides two MCP server integrations:

| MCP Server | Purpose | Requires |
|-----------|---------|----------|
| `notebooklm-mcp` | RAG capabilities, research notebooks, artifact generation | `uv`, Chrome browser |
| `sonarqube-mcp` | Quality gates, issue discovery, code analysis | Docker, SonarQube credentials |

## NotebookLM MCP Integration

### Setup

**1. Install Dependencies**

```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install notebooklm-mcp-cli
uv tool install notebooklm-mcp-cli

# Verify installation
nlm --version
```

**2. Authenticate**

```bash
# Login with Chrome browser (opens browser for cookie extraction)
nlm login

# Verify authentication
nlm login --check

# For multiple accounts, use profiles
nlm login --profile work
nlm login switch work
```

**3. Troubleshoot**

```bash
# Run diagnostics
nlm doctor
nlm doctor --verbose
```

### Available Tools

The NotebookLM MCP server provides the following tools:

**Notebook Management**
- `notebook_list` - List all notebooks
- `notebook_get` - Get notebook details
- `notebook_create` - Create a new notebook
- `notebook_query` - Query notebook sources with AI
- `notebook_rename` - Rename a notebook
- `notebook_delete` - Delete a notebook

**Source Management**
- `source_list` - List sources in a notebook
- `source_add` - Add URL, text, file, YouTube, or Drive source
- `source_get` - Get source content
- `source_delete` - Delete a source
- `source_rename` - Rename a source
- `source_stale` - Check for stale Drive sources
- `source_sync` - Sync stale Drive sources

**Studio Content**
- `studio_create` - Create audio, video, report, quiz, mind map, etc.
- `studio_status` - Check generation status
- `studio_revise` - Revise slides in an existing deck
- `studio_delete` - Delete a studio artifact

**Download**
- `download_artifact` - Download audio, video, report, etc.

**Research**
- `research_start` - Start web or Drive research
- `research_status` - Poll for research completion
- `research_import` - Import research results as sources

**Auth Management**
- `refresh_auth` - Refresh authentication tokens
- `server_info` - Check server version

### Workflow Examples

**Query a Research Notebook**

```bash
# 1. List notebooks
nlm notebook list

# 2. Set an alias for easy reference
nlm alias set myproject <notebook-id>

# 3. Query the notebook
nlm notebook query myproject "What are the login requirements?"
```

**Build a Documentation Notebook**

```bash
# 1. Create notebook
nlm notebook create "API Documentation"

# 2. Add sources (only user-provided URLs)
nlm source add myproject --url "https://docs.example.com/api" --wait
nlm source add myproject --file openapi.yaml --wait

# 3. Generate briefing document
nlm report create myproject --format "Briefing Doc" --confirm

# 4. Download when ready
nlm studio status myproject
nlm download report myproject <artifact-id> --output api-brief.md
```

**Generate a Podcast from Documentation**

```bash
# 1. Add user-provided sources
nlm source add myproject --url "<user-url>" --wait

# 2. Generate audio podcast
nlm audio create myproject --format deep_dive --length long --confirm

# 3. Poll for completion and download
nlm studio status myproject
nlm download audio myproject <artifact-id> --output podcast.mp3
```

### Important Notes

- **Authentication expires** every 2-4 weeks. Run `nlm login` again when operations fail.
- **Rate limits** apply on free tier (~50 queries/day).
- **Sources are user-controlled**: Never add URLs autonomously; only use URLs explicitly provided by the user.
- **Query results are untrusted**: Present results for user review before using to drive implementation.

---

## SonarQube MCP Integration

### Setup

**1. Install Docker**

SonarQube MCP runs as a Docker container. Ensure Docker is installed and running.

**2. Configure Credentials**

For **SonarQube Server** (self-hosted or remote):

```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="https://sonarqube.mycompany.com"
# For local Docker instances:
export SONARQUBE_URL="http://host.docker.internal:9000"
```

For **SonarCloud**:

```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_ORG="your-org-key"
# SONARQUBE_URL is not needed for SonarCloud
```

**3. Get Credentials**

1. SonarQube: Generate a token at `User > My Account > Security > Generate Tokens`
2. SonarCloud: Create an organization at sonarcloud.io, then generate a token

### Available Tools

The SonarQube MCP server provides the following tools:

**Quality Gates**
- `get_project_quality_gate_status` - Check if a project passes its quality gate

**Issue Management**
- `search_sonar_issues_in_projects` - Search for issues by severity, project, or PR
- `change_sonar_issue_status` - Mark issues as false positive, accepted, or reopen

**Code Analysis**
- `analyze_code_snippet` - Analyze a file or code snippet before committing (shift-left)
- `show_rule` - Get rule documentation with fix examples

**Metrics**
- `get_component_measures` - Retrieve project metrics (coverage, bugs, complexity, etc.)

### Workflow Examples

**Check Quality Gate Before Merge**

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "my-backend-api",
    "pullRequest": "234"
  }
}
```

**Find Critical Issues**

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-backend-api"],
    "severities": ["BLOCKER", "HIGH"],
    "ps": 50
  }
}
```

**Pre-Push Analysis (Shift-Left)**

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

**Understand a Rule**

```json
{
  "name": "show_rule",
  "arguments": {
    "key": "typescript:S1082"
  }
}
```

### Important Notes

- **Pagination is required** for large result sets. Check `paging.total` in responses.
- **Quality gate reflects last analysis**: Trigger a new analysis if code has changed.
- **Issue status changes require permissions**: User must have appropriate SonarQube roles.
- **Code snippet analysis is isolated**: Full project context may affect real CI results.

---

## MCP Server Wrapper Scripts

The plugin includes wrapper scripts that handle dependency checking:

### NotebookLM MCP Wrapper

**Location**: `scripts/wrap-notebooklm-mcp.sh`

The wrapper:
1. Checks if `uvx` is installed
2. Verifies `notebooklm-mcp-cli` is available
3. Runs the MCP server with passed arguments

**Manual test:**

```bash
# Test the wrapper directly
./scripts/wrap-notebooklm-mcp.sh --help
```

### SonarQube MCP Wrapper

**Location**: `scripts/wrap-sonarqube-mcp.sh`

The wrapper:
1. Checks if Docker is installed
2. Verifies Docker daemon is running
3. Checks for required environment variables (warns if missing)
4. Runs the `mcp/sonarqube` Docker image

**Manual test:**

```bash
# Test the wrapper directly
SONARQUBE_TOKEN="test" SONARQUBE_URL="http://localhost:9000" \
  ./scripts/wrap-sonarqube-mcp.sh --help
```

---

## Troubleshooting

### NotebookLM Issues

| Issue | Solution |
|-------|----------|
| "CLI not found" | Install with `uv tool install notebooklm-mcp-cli` |
| "Authentication failed" | Run `nlm login` again |
| "Rate limit exceeded" | Wait and retry; free tier has ~50 queries/day |
| "Source processing stuck" | Use `--wait` flag when adding sources |

### SonarQube Issues

| Issue | Solution |
|-------|----------|
| "Docker not found" | Install Docker Desktop |
| "Docker daemon not running" | Start Docker Desktop or Docker service |
| "Token not set" | Set `SONARQUBE_TOKEN` environment variable |
| "Organization not set" | Set `SONARQUBE_ORG` for SonarCloud |
| "Connection refused" | Check `SONARQUBE_URL`; use `host.docker.internal` for local |
