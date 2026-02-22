---
description: Creates GitHub pull requests and transitions Jira tickets to "In Review" status. Use when submitting completed work for code review and linking PRs to Jira tickets.
allowed-tools: Bash(git *), Bash(gh *), AskUserQuestion
argument-hint: '"[PR title]"'
---

# Create PR with Jira Integration

## Overview

Creates a GitHub pull request and transitions the associated Jira ticket to "In Review" status.

## Usage

```
/devkit.jira.workflow.pr-create "[PR title]"
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `$1` | PR title. Defaults to ticket summary if available. | No |

## Execution

### Step 1: Get Ticket Info

```bash
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)

if [ -n "$TICKET" ]; then
    # Fetch ticket details via MCP
    # Extract SUMMARY from response
    SUMMARY="[ticket summary]"
fi
```

### Step 2: Determine PR Title

```bash
if [ -n "$1" ]; then
    PR_TITLE="$1"
elif [ -n "$SUMMARY" ]; then
    PR_TITLE="$TICKET: $SUMMARY"
else
    PR_TITLE="$TICKET: Changes from $BRANCH"
fi
```

### Step 3: Create PR

Use GitHub CLI:

```bash
# Create PR
gh pr create \
    --title "$PR_TITLE" \
    --body "$(cat <<'EOF'
## Summary

Implements changes for $TICKET.

## Changes

- [Describe changes]

## Testing

- [Testing performed]

Closes $TICKET
EOF
)" \
    --base main

PR_URL=$(gh pr view --json url -q .url)
PR_NUMBER=$(gh pr view --json number -q .number)

echo "Created PR: $PR_URL"
```

### Step 4: Add Comment to Jira

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "Created PR #$PR_NUMBER: $PR_URL"
  }
}
```

### Step 5: Confirm Transition

Ask user:
```
Transition $TICKET to "In Review"?
[Yes] [No]
```

If yes:

```json
{
  "tool": "jira_transition_issue",
  "arguments": {
    "issueKey": "$TICKET",
    "transitionName": "In Review"
  }
}
```

### Step 6: Summary

```
PR created successfully!
PR: $PR_URL
[Ticket transitioned to In Review if confirmed]
```

## Examples

### Create PR with custom title

```
/devkit.jira.workflow.pr-create "Add user login feature"
# Output:
# Created PR: https://github.com/org/repo/pull/45
# Transition PROJ-456 to "In Review"? [Yes]
# Done
```

### Create PR with ticket summary

```
/devkit.jira.workflow.pr-create
# Uses ticket summary as PR title
```

## Error Handling

- **No ticket found**: Create PR without Jira integration
- **PR creation fails**: Exit with error
- **Transition fails**: PR created, transition reported separately
