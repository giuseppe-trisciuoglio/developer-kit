---
description: Provides Jira ticket details including summary, status, assignee, and description. Use when you need to view ticket information before starting work, check current status, or review ticket details during development.
allowed-tools: Bash, AskUserQuestion
argument-hint: "[TICKET-ID]"
---

# View Jira Ticket

## Overview

Retrieves and displays detailed information about a Jira ticket using the Atlassian MCP Server.

## Usage

```
/devkit.jira.ticket.view [TICKET-ID]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Jira ticket ID (e.g., TEST-123). Inferred from branch if omitted. | No |

## Execution

### Step 1: Infer Ticket ID

```bash
# Check if ticket ID provided
TICKET="${1:-}"

# If not provided, try to infer from branch name
if [ -z "$TICKET" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "")
    # Extract ticket ID from patterns like feature/TEST-123 or feature/TEST-123-desc
    TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)
fi

if [ -z "$TICKET" ]; then
    echo "Error: Could not infer ticket ID. Please provide it explicitly."
    echo "Usage: /devkit.jira.ticket.view TEST-123"
    exit 1
fi

echo "Fetching details for ticket: $TICKET"
```

### Step 2: Fetch Ticket via MCP

Use the `atlassian` MCP server to retrieve ticket details:

```json
{
  "tool": "jira_get_issue",
  "arguments": {
    "issueKey": "$TICKET"
  }
}
```

### Step 3: Display Results

Format and display the ticket information:

```
Ticket: $TICKET
Summary: [ticket summary]
Status: [current status]
Assignee: [assignee name or Unassigned]
Reporter: [reporter name]
Created: [creation date]
Updated: [last update date]

Description:
[formatted description]

Comments ([count]):
[latest comments]
```

## Examples

### View specific ticket

```
/devkit.jira.ticket.view PROJ-456
```

### View inferred ticket (from branch feature/PROJ-789-feature)

```
/devkit.jira.ticket.view
# Automatically uses PROJ-789
```

## Error Handling

- **MCP not connected**: Prompt user to configure Atlassian MCP Server
- **Ticket not found**: Verify ticket ID and permissions
- **Auth expired**: Request re-authentication
