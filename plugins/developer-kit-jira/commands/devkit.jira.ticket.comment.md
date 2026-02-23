---
description: Provides functionality to add comments to Jira tickets. Use when you need to document progress, add notes, or update tickets with development information.
allowed-tools: Bash, AskUserQuestion
argument-hint: "[TICKET-ID] \"comment message\""
---

# Add Comment to Jira Ticket

## Overview

Adds a comment to a Jira ticket using the Atlassian MCP Server.

## Usage

```
/devkit.jira.ticket.comment [TICKET-ID] "comment message"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Jira ticket ID (e.g., TEST-123). Inferred from branch if omitted. | No |
| `$2` | Comment message to add | Yes |

## Execution

### Step 1: Parse Arguments

```bash
# Determine ticket ID and message
if [ $# -eq 1 ]; then
    # Only message provided, infer ticket
    MESSAGE="$1"
    TICKET=$(git branch --show-current 2>/dev/null | grep -oE '[A-Z]+-[0-9]+' | head -1)
elif [ $# -ge 2 ]; then
    TICKET="$1"
    MESSAGE="$2"
else
    echo "Error: Insufficient arguments"
    echo "Usage: /devkit.jira.ticket.comment [TICKET-ID] \"message\""
    exit 1
fi

if [ -z "$TICKET" ]; then
    echo "Error: Could not infer ticket ID. Please provide it explicitly."
    exit 1
fi

echo "Adding comment to $TICKET..."
echo "Comment: $MESSAGE"
```

### Step 2: Confirm with User

```bash
# Ask for confirmation before adding comment
# Use AskUserQuestion tool for confirmation
```

### Step 3: Add Comment via MCP

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "$MESSAGE"
  }
}
```

### Step 4: Confirm Success

```
Comment added successfully to $TICKET
```

## Examples

### Add comment to specific ticket

```
/devkit.jira.ticket.comment PROJ-456 "Started working on the authentication fix"
```

### Add comment to inferred ticket

```
/devkit.jira.ticket.comment "Fixed the login validation bug"
# Uses ticket ID from current branch
```

## Error Handling

- **Empty message**: Prompt user to provide a comment
- **Ticket not found**: Verify ticket ID exists
- **Permission denied**: Check Jira permissions for commenting
