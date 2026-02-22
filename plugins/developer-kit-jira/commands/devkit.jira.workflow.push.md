---
description: Handles git push operations with Jira ticket synchronization. Use when you need to push commits to remote and update associated Jira tickets.
allowed-tools: Bash(git *), AskUserQuestion
argument-hint: ""
---

# Push with Jira Integration

## Overview

Pushes the current branch to remote and adds a comment to the associated Jira ticket with push details.

## Usage

```
/devkit.jira.workflow.push
```

## Arguments

This command takes no arguments. It infers the ticket ID from the current branch name.

## Execution

### Step 1: Get Context

```bash
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)

# Get commit count ahead of main
AHEAD=$(git rev-list --count main..$BRANCH 2>/dev/null || echo "unknown")

# Get last commit message
LAST_COMMIT=$(git log -1 --pretty=%s)
```

### Step 2: Push to Remote

```bash
# Push with upstream tracking
git push -u origin "$BRANCH"

if [ $? -ne 0 ]; then
    echo "Error: Push failed"
    exit 1
fi

echo "Pushed to origin/$BRANCH"
```

### Step 3: Add Comment to Jira (if ticket found)

If `$TICKET` is not empty:

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "Pushed to branch \`$BRANCH\`\n\nCommits: $AHEAD\nLast commit: $LAST_COMMIT"
  }
}
```

### Step 4: Summary

```
Push successful!
Branch: origin/$BRANCH
Commits pushed: $AHEAD
[Ticket comment added if applicable]
```

## Examples

### Push with ticket

```
/devkit.jira.workflow.push
# Output:
# Pushed to origin/feature/PROJ-456-add-login
# Added comment to PROJ-456
```

### Push without ticket

```
/devkit.jira.workflow.push
# Output:
# Warning: Could not infer ticket ID from branch name
# Pushed to origin/feature/my-feature
```

## Error Handling

- **Push fails**: Show git error and exit
- **No remote**: Prompt to add remote
- **MCP error**: Push succeeds but comment may fail
