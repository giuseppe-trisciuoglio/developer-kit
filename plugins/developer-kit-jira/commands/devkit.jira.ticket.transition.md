---
description: Manages Jira ticket status transitions through workflow states. Use when you need to change ticket status from one state to another (e.g., To Do to In Progress).
allowed-tools: Bash, AskUserQuestion
argument-hint: "[TICKET-ID] [TARGET-STATUS]"
---

# Transition Jira Ticket

## Overview

Transitions a Jira ticket to a new status using the Atlassian MCP Server. Shows available transitions if target status is not specified.

## Usage

```
/devkit.jira.ticket.transition [TICKET-ID] [TARGET-STATUS]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Jira ticket ID (e.g., TEST-123). Inferred from branch if omitted when providing status. | No |
| `$2` | Target status name (e.g., "In Progress", "Done"). If omitted, shows available transitions. | No |

## Execution

### Step 1: Parse Arguments

```bash
# Determine ticket ID and target status
if [ $# -eq 0 ]; then
    # No arguments, infer from branch
    TICKET=$(git branch --show-current 2>/dev/null | grep -oE '[A-Z]+-[0-9]+' | head -1)
    TARGET_STATUS=""
elif [ $# -eq 1 ]; then
    # Could be ticket ID or status
    if [[ "$1" =~ ^[A-Z]+-[0-9]+$ ]]; then
        TICKET="$1"
        TARGET_STATUS=""
    else
        TICKET=$(git branch --show-current 2>/dev/null | grep -oE '[A-Z]+-[0-9]+' | head -1)
        TARGET_STATUS="$1"
    fi
else
    TICKET="$1"
    TARGET_STATUS="$2"
fi

if [ -z "$TICKET" ]; then
    echo "Error: Could not determine ticket ID"
    exit 1
fi
```

### Step 2: Get Current Status and Available Transitions

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_get_transitions",
  "arguments": {
    "issueKey": "$TICKET"
  }
}
```

### Step 3: Show or Execute Transition

**If TARGET_STATUS is empty:**
- Display current status
- List available transitions with numbers
- Ask user to select

**If TARGET_STATUS is provided:**
- Find matching transition
- Confirm with user: "Transition $TICKET to '$TARGET_STATUS'?"
- Execute transition via MCP:

```json
{
  "tool": "jira_transition_issue",
  "arguments": {
    "issueKey": "$TICKET",
    "transitionName": "$TARGET_STATUS"
  }
}
```

## Examples

### Show available transitions

```
/devkit.jira.ticket.transition PROJ-456
# Output:
# Current status: In Progress
# Available transitions:
# 1. In Review
# 2. Blocked
# 3. Done
```

### Transition to specific status

```
/devkit.jira.ticket.transition PROJ-456 "In Review"
# Output: Transitioned PROJ-456 to "In Review"
```

### Transition inferred ticket

```
/devkit.jira.ticket.transition "Done"
# Uses ticket from branch, transitions to Done
```

## Error Handling

- **Invalid transition**: Show available transitions
- **Permission denied**: Check workflow permissions
- **Ticket not found**: Verify ticket ID
