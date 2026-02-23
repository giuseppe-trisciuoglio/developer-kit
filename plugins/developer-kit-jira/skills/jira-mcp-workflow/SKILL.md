---
name: jira-mcp-workflow
description: Integrates Jira with Git workflows using the official Atlassian MCP Server. Use when working with Jira tickets, managing ticket states based on git actions, or synchronizing development progress with Jira. Handles ticket inference from branch names, commits, and PRs with user confirmations before state changes.
allowed-tools: Bash, AskUserQuestion
---

# Jira MCP Workflow Integration

## Overview

This skill provides seamless integration between Git workflows and Jira using the official Atlassian MCP Server. It enables automatic inference of Jira tickets from git context (branch names, commits, PRs) and manages ticket state transitions with user confirmation.

## When to Use

- Starting work on a Jira ticket: "Start working on TEST-123"
- Creating commits that should update Jira: "Commit changes and update ticket"
- Creating PRs that should transition tickets: "Create PR for this ticket"
- Checking ticket status: "What's the status of my Jira ticket?"
- Transitioning tickets: "Move ticket to In Review"

## Instructions

### Ticket Inference

1. Extract ticket ID from the current context:
   - Check branch name for pattern `feature/PROJECT-123`
   - Check commit messages for `PROJECT-123: message`
   - Check PR title for `PROJECT-123: title`
   - If no ticket found, ask user to provide it

2. Validate ticket ID format (e.g., `PROJECT-123`)

### MCP Server Operations

1. **View Ticket**: Use `atlassian` MCP server with `jira_get_issue` tool
2. **Add Comment**: Use `atlassian` MCP server with `jira_add_comment` tool
3. **Transition**: Use `atlassian` MCP server with `jira_get_transitions` then `jira_transition_issue`

### Workflow Commands

1. **Start**: `devkit.jira.workflow.start [TICKET]`
   - Fetch ticket details via MCP
   - Confirm with user
   - Execute git commands (checkout main, pull, create branch)
   - Add comment to Jira

2. **Commit**: `devkit.jira.workflow.commit "message"`
   - Stage and commit with ticket prefix
   - Add comment to Jira

3. **Push**: `devkit.jira.workflow.push`
   - Push branch to remote
   - Add comment to Jira

4. **PR Create**: `devkit.jira.workflow.pr-create [title]`
   - Create PR via GitHub CLI
   - Transition ticket to "In Review" (with confirmation)

5. **PR Ready**: `devkit.jira.workflow.pr-ready`
   - Mark PR as ready
   - Transition ticket to "Reviewing" (with confirmation)

6. **PR Merge**: `devkit.jira.workflow.pr-merge`
   - Merge PR via GitHub CLI
   - Transition ticket to "Done" (with confirmation)

### Confirmation Prompts

Always ask user confirmation before:
- Creating branches
- Transitioning ticket states
- Merging PRs

## Prerequisites

### Atlassian MCP Server Configuration

Add to your MCP settings (`claude_mcp_settings.json`):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote", "https://mcp.atlassian.com/v1/mcp"],
      "env": {}
    }
  }
}
```

### Authentication

The Atlassian MCP Server uses OAuth 2.1 (3LO) flow:
1. First connection will prompt for Atlassian login
2. Grant permissions for Jira access
3. Session-based tokens are managed automatically

## Ticket Inference Rules

The skill automatically extracts Jira ticket IDs from:

| Source | Pattern | Example |
|--------|---------|---------|
| Branch name | `feature/PROJECT-123` or `feature/PROJECT-123-description` | `feature/TEST-456-login-fix` |
| Commit message | `PROJECT-123: message` or `[PROJECT-123] message` | `TEST-456: Fix authentication` |
| PR title | `PROJECT-123: title` | `TEST-456: Fix login bug` |
| Current branch | Extracted from `git branch --show-current` | - |

### Inference Priority

1. Explicit argument provided by user
2. Current git branch name
3. Recent commit messages
4. Ask user for ticket ID

## Workflow Commands

### 1. Start Workflow

```bash
/devkit.jira.workflow.start [TICKET]
```

**Actions:**
1. Infers ticket ID from argument or current context
2. Fetches ticket details from Jira (via MCP)
3. Confirms with user: "Start work on TEST-123: 'Fix login bug'?"
4. Executes:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/TEST-123-fix-login-bug
   ```
5. Adds comment to Jira: "Started development on branch feature/TEST-123-fix-login-bug"
6. Optionally transitions ticket to "In Progress"

### 2. Commit Workflow

```bash
/devkit.jira.workflow.commit "commit message"
```

**Actions:**
1. Infers ticket ID from branch name or commit message
2. Formats commit: `TEST-123: commit message`
3. Executes:
   ```bash
   git add -A
   git commit -m "TEST-123: commit message"
   ```
4. Adds comment to Jira: "Committed: commit message"

### 3. Push Workflow

```bash
/devkit.jira.workflow.push
```

**Actions:**
1. Infers ticket ID from current branch
2. Executes:
   ```bash
   git push -u origin $(git branch --show-current)
   ```
3. Adds comment to Jira with push details and commit count

### 4. PR Create Workflow

```bash
/devkit.jira.workflow.pr-create [title]
```

**Actions:**
1. Infers ticket ID from branch name
2. Fetches ticket details for PR description
3. Creates PR using `devkit.github.create-pr`
4. Confirms: "Transition TEST-123 to 'In Review'?"
5. If confirmed, transitions Jira ticket via MCP
6. Adds comment with PR link

### 5. PR Ready Workflow

```bash
/devkit.jira.workflow.pr-ready
```

**Actions:**
1. Infers ticket ID from branch/PR
2. Marks PR as ready for review (removes draft)
3. Confirms: "Transition TEST-123 to 'Reviewing'?"
4. If confirmed, transitions Jira ticket via MCP

### 6. PR Merge Workflow

```bash
/devkit.jira.workflow.pr-merge
```

**Actions:**
1. Infers ticket ID from PR
2. Merges PR using `gh pr merge`
3. Confirms: "Transition TEST-123 to 'Done'?"
4. If confirmed, transitions Jira ticket via MCP
5. Adds comment: "Merged to main via PR #XXX"

### 7. Status Workflow

```bash
/devkit.jira.workflow.status
```

**Actions:**
1. Shows git status (branch, commits ahead/behind)
2. Infers ticket ID from branch
3. Fetches and displays Jira ticket status via MCP
4. Shows available transitions

## Individual Ticket Commands

### View Ticket

```bash
/devkit.jira.ticket.view [TICKET]
```

Displays ticket details: summary, status, assignee, description, comments.

### Add Comment

```bash
/devkit.jira.ticket.comment [TICKET] "message"
```

Adds a comment to the specified ticket.

### Transition Ticket

```bash
/devkit.jira.ticket.transition [TICKET] [STATUS]
```

Shows available transitions if status not specified, otherwise transitions ticket.

## MCP Tool Usage

This skill uses the following Atlassian MCP tools:

| Tool | Purpose |
|------|---------|
| `jira_search` | Find tickets by JQL query |
| `jira_get_issue` | Retrieve ticket details |
| `jira_create_issue` | Create new tickets |
| `jira_update_issue` | Update ticket fields |
| `jira_add_comment` | Add comments to tickets |
| `jira_get_transitions` | Get available status transitions |
| `jira_transition_issue` | Change ticket status |

## Confirmation Prompts

All state-changing operations require explicit user confirmation:

**Before state transitions:**
```
Transition TEST-123 from "To Do" to "In Progress"?
[Yes] [No] [Always for this session]
```

**Before branch creation:**
```
Create branch feature/TEST-123-fix-login-bug from main?
Current ticket: TEST-123 - "Fix login bug"
[Yes] [No]
```

## Best Practices

1. **Always use ticket IDs in branch names**: `feature/PROJECT-123-short-desc`
2. **Include ticket ID in commits**: `PROJECT-123: Fix authentication bug`
3. **Review transitions before confirming**: Verify the target state is correct
4. **Keep comments descriptive**: Explain what was done, not just "updated"

## Error Handling

| Error | Resolution |
|-------|------------|
| MCP server not connected | Check `claude_mcp_settings.json` configuration |
| OAuth session expired | Re-authenticate via browser prompt |
| Ticket not found | Verify ticket ID and Jira permissions |
| Transition not allowed | Check workflow permissions in Jira |
| Git not in repo | Ensure you're in a git repository |

## Constraints and Warnings

### Critical Constraints

- **MCP Server Required**: Requires Atlassian MCP Server to be configured and authenticated
- **OAuth Session**: User must complete OAuth 2.1 (3LO) flow with Atlassian before first use
- **Git Repository Required**: Workflow commands require a git repository with remote origin configured
- **GitHub CLI Required**: PR commands require `gh` CLI to be installed and authenticated

### State Change Confirmations

All ticket state transitions require explicit user confirmation. The skill will NOT:
- Automatically transition tickets without confirmation
- Bulk update multiple tickets at once
- Override Jira workflow constraints or permissions

### Security Considerations

- Ticket IDs are inferred from branch names using regex pattern `[A-Z]+-[0-9]+`
- Comments added to Jira tickets are permanent and visible to all project members
- PR merge operations are irreversible (use with caution)

### Limitations

- Ticket inference works only with standard branch naming patterns (`feature/PROJECT-123`)
- Cannot create Jira tickets (only view, comment, and transition existing ones)
- Requires active internet connection for MCP server communication

## Examples

### Example 1: Complete Feature Workflow

```bash
# Start work
/devkit.jira.workflow.start TEST-123
# Output: Created branch feature/TEST-123-add-login, ticket transitioned to In Progress

# Make changes and commit
/devkit.jira.workflow.commit "Add email validation"
# Output: Committed as "TEST-123: Add email validation", comment added to Jira

# Push changes
/devkit.jira.workflow.push
# Output: Pushed to origin, comment added

# Create PR
/devkit.jira.workflow.pr-create "Add user login feature"
# Output: Created PR #45, transition TEST-123 to In Review? [Yes] -> Done
```

### Example 2: Check Status

```bash
/devkit.jira.workflow.status
# Output:
# Git: On branch feature/TEST-123-add-login, 2 commits ahead
# Jira: TEST-123 - "Add login feature" - Status: In Progress
# Available transitions: In Review, Blocked, Done
```

### Example 3: Manual Transition

```bash
/devkit.jira.ticket.transition TEST-123
# Output: Available transitions:
# 1. To Do
# 2. In Progress
# 3. In Review
# 4. Done
# Select: 3
# Transition TEST-123 to "In Review"? [Yes] -> Done
```

## Integration with GitHub Workflow

This skill complements the existing `github-issue-workflow` skill:

- Use `github-issue-workflow` for GitHub-centric workflows
- Use `jira-mcp-workflow` when Jira is your primary project management tool
- Both can be used together for GitHub-Jira integrated workflows
