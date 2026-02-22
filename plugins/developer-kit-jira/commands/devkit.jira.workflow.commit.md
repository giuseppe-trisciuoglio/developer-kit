---
description: Creates git commits with Jira ticket references and updates tickets with comments. Use when committing changes related to Jira tickets to maintain traceability between code and issue tracking.
allowed-tools: Bash(git *), AskUserQuestion
argument-hint: '"commit message"'
---

# Commit with Jira Integration

## Overview

Commits changes with proper Jira ticket reference and optionally adds a comment to the ticket.

## Usage

```
/devkit.jira.workflow.commit "commit message"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | Commit message | Yes |

## Execution

### Step 1: Get Ticket ID from Branch

```bash
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)

if [ -z "$TICKET" ]; then
    echo "Warning: Could not infer ticket ID from branch name"
    echo "Branch: $BRANCH"
    echo "Continuing with commit only..."
    COMMIT_FORMAT="$1"
else
    COMMIT_FORMAT="$TICKET: $1"
fi
```

### Step 2: Stage and Commit

```bash
# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Stage all changes
git add -A

# Create commit
git commit -m "$COMMIT_FORMAT"

echo "Committed: $COMMIT_FORMAT"
```

### Step 3: Add Comment to Jira (if ticket found)

If `$TICKET` is not empty:

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "Committed: $1"
  }
}
```

### Step 4: Summary

```
Changes committed successfully!
Commit: $COMMIT_FORMAT
[Ticket comment added if applicable]
```

## Examples

### Commit with inferred ticket

```
/devkit.jira.workflow.commit "Fix email validation bug"
# Output:
# Committed: PROJ-456: Fix email validation bug
# Added comment to PROJ-456
```

### Commit without ticket (warning)

```
/devkit.jira.workflow.commit "Update README"
# Output:
# Warning: Could not infer ticket ID from branch name
# Committed: Update README
```

## Error Handling

- **No changes**: Exit with message
- **Commit fails**: Show git error
- **MCP error**: Commit succeeds but comment may fail
