---
description: Provides a unified view of git repository state and Jira ticket status. Use when you need to check the current state of development work across both git and Jira.
allowed-tools: Bash(git *), Bash(gh *)
argument-hint: "[TICKET-ID]"
---

# Workflow Status

## Overview

Displays combined status of git repository and associated Jira ticket.

## Usage

```
/devkit.jira.workflow.status [TICKET-ID]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Jira ticket ID. Inferred from branch if omitted. | No |

## Execution

### Step 1: Gather Git Info

```bash
# Git status
BRANCH=$(git branch --show-current)
IS_REPO=$([ -d .git ] && echo "yes" || echo "no")

if [ "$IS_REPO" = "yes" ]; then
    MODIFIED=$(git status --porcelain | wc -l | tr -d ' ')
    AHEAD=$(git rev-list --count main..$BRANCH 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count $BRANCH..main 2>/dev/null || echo "0")

    # Check for PR
    PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
    PR_STATUS=$(gh pr view --json state -q .state 2>/dev/null || echo "No PR")
fi
```

### Step 2: Infer Ticket ID

```bash
TICKET="${1:-}"
if [ -z "$TICKET" ]; then
    TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)
fi
```

### Step 3: Fetch Jira Status (if ticket found)

If `$TICKET` is not empty:

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_get_issue",
  "arguments": {
    "issueKey": "$TICKET"
  }
}
```

Then get available transitions:

```json
{
  "tool": "jira_get_transitions",
  "arguments": {
    "issueKey": "$TICKET"
  }
}
```

### Step 4: Display Status

```
═══════════════════════════════════════════════════════════
                    WORKFLOW STATUS
═══════════════════════════════════════════════════════════

Git Repository:
  Branch:      feature/PROJ-456-add-login
  Modified:    3 files
  Commits:     +2 ahead, -1 behind main
  PR:          #45 (OPEN) [or No PR]

Jira Ticket:
  Ticket:      PROJ-456
  Summary:     Add user login feature
  Status:      In Progress
  Assignee:    John Doe

Available Transitions:
  1. In Review
  2. Blocked
  3. Done

═══════════════════════════════════════════════════════════
```

## Examples

### Status with inferred ticket

```
/devkit.jira.workflow.status
# Output:
# Git: On feature/PROJ-456-add-login, 2 commits ahead
# Jira: PROJ-456 - In Progress
# Available transitions: In Review, Blocked, Done
```

### Status for specific ticket

```
/devkit.jira.workflow.status PROJ-789
# Output:
# Git: Not on a feature branch
# Jira: PROJ-789 - To Do
```

## Error Handling

- **Not in git repo**: Show Jira status only
- **No ticket found**: Show git status only
- **MCP error**: Show git status, note Jira unavailable
