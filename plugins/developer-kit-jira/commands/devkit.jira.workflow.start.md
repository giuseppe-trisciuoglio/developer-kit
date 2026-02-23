---
description: Start working on a Jira ticket - creates branch, updates Jira with comment, and optionally transitions status. Initiates the development workflow by setting up the git environment and notifying Jira. Use when beginning development on a ticket.
allowed-tools: Bash(git *), AskUserQuestion
argument-hint: "[TICKET-ID]"
---

# Start Jira Workflow

## Overview

Initiates development work on a Jira ticket by:
1. Fetching ticket details from Jira
2. Confirming with the user
3. Creating a feature branch
4. Adding a comment to the ticket
5. Optionally transitioning to "In Progress"

## Usage

```
/devkit.jira.workflow.start [TICKET-ID]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Jira ticket ID (e.g., TEST-123). Inferred from branch if omitted. | No |

## Execution

### Step 1: Infer or Get Ticket ID

```bash
# Check if ticket ID provided
TICKET="${1:-}"

# If not provided, try to infer from branch name
if [ -z "$TICKET" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "")
    TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)
fi

if [ -z "$TICKET" ]; then
    echo "Error: Could not infer ticket ID. Please provide it explicitly."
    echo "Usage: /devkit.jira.workflow.start TEST-123"
    exit 1
fi
```

### Step 2: Fetch Ticket Details via MCP

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_get_issue",
  "arguments": {
    "issueKey": "$TICKET"
  }
}
```

Extract: `summary`, `status`

### Step 3: Confirm with User

Ask confirmation:
```
Start work on $TICKET: "$SUMMARY"?
Current status: $STATUS
This will:
- Checkout and pull main
- Create branch feature/$TICKET-[slug]
- Add comment to Jira

[Yes] [No]
```

### Step 4: Execute Git Commands

```bash
# Stash any current changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Stashing current changes..."
    git stash push -m "Auto-stash before starting $TICKET"
fi

# Checkout main and pull
git checkout main
git pull origin main

# Create branch name from ticket
SLUG=$(echo "$SUMMARY" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
BRANCH_NAME="feature/$TICKET-${SLUG}"

# Create branch
git checkout -b "$BRANCH_NAME"

echo "Created branch: $BRANCH_NAME"
```

### Step 5: Add Comment to Jira

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "Started development on branch \`$BRANCH_NAME\`"
  }
}
```

### Step 6: Optional - Transition to In Progress

Ask user:
```
Transition $TICKET to "In Progress"?
[Yes] [No] [Skip]
```

If yes:
```json
{
  "tool": "jira_transition_issue",
  "arguments": {
    "issueKey": "$TICKET",
    "transitionName": "In Progress"
  }
}
```

### Step 7: Summary

```
Workflow started successfully!
Ticket: $TICKET
Branch: $BRANCH_NAME
Status: [Updated/Not updated]
```

## Examples

### Start work on specific ticket

```
/devkit.jira.workflow.start PROJ-456
# Output:
# Start work on PROJ-456: "Add user authentication"? [Yes]
# Created branch: feature/PROJ-456-add-user-authentication
# Added comment to Jira
# Transition to In Progress? [Yes]
```

### Continue on inferred ticket

```
/devkit.jira.workflow.start
# Uses ticket ID from current branch
```

## Error Handling

- **Uncommitted changes**: Stash them automatically
- **Branch exists**: Switch to existing branch
- **MCP error**: Report and continue with git operations
