---
description: Handles PR merging and ticket completion workflow. Use when you need to merge approved pull requests and mark associated Jira tickets as complete.
allowed-tools: Bash(gh *), Bash(git *), AskUserQuestion
argument-hint: ""
---

# Merge PR with Jira Integration

## Overview

Merges a GitHub PR and transitions the Jira ticket to "Done" status.

## Usage

```
/devkit.jira.workflow.pr-merge
```

## Arguments

This command takes no arguments. It infers the ticket ID from the current branch and PR.

## Execution

### Step 1: Get PR and Ticket Info

```bash
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)

# Get PR info
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
PR_URL=$(gh pr view --json url -q .url 2>/dev/null || echo "")

if [ -z "$PR_NUMBER" ]; then
    echo "Error: No PR found for current branch"
    exit 1
fi
```

### Step 2: Check PR Status

```bash
# Check if PR is mergeable
PR_STATE=$(gh pr view --json state -q .state)
if [ "$PR_STATE" != "OPEN" ]; then
    echo "Error: PR #$PR_NUMBER is not open (state: $PR_STATE)"
    exit 1
fi
```

### Step 3: Confirm Merge

Ask user:
```
Merge PR #$PR_NUMBER to main?
[Yes] [No]
```

### Step 4: Merge PR

```bash
gh pr merge "$PR_NUMBER" --squash --delete-branch

if [ $? -ne 0 ]; then
    echo "Error: Merge failed"
    exit 1
fi

echo "Merged PR #$PR_NUMBER"
```

### Step 5: Add Comment to Jira

Use the `atlassian` MCP server:

```json
{
  "tool": "jira_add_comment",
  "arguments": {
    "issueKey": "$TICKET",
    "body": "Merged to main via PR #$PR_NUMBER"
  }
}
```

### Step 6: Confirm Transition to Done

Ask user:
```
Transition $TICKET to "Done"?
[Yes] [No]
```

If yes:

```json
{
  "tool": "jira_transition_issue",
  "arguments": {
    "issueKey": "$TICKET",
    "transitionName": "Done"
  }
}
```

### Step 7: Cleanup

```bash
# Switch to main
git checkout main
git pull origin main

echo "Switched to main and pulled latest changes"
```

### Step 8: Summary

```
Merge completed successfully!
PR: #$PR_NUMBER merged to main
[Ticket transitioned to Done if confirmed]
```

## Examples

```
/devkit.jira.workflow.pr-merge
# Output:
# Merge PR #45 to main? [Yes]
# Merged PR #45
# Transition PROJ-456 to "Done"? [Yes]
# Done
# Switched to main
```

## Error Handling

- **No PR found**: Exit with error
- **PR not mergeable**: Show checks status
- **Merge fails**: Exit with git error
- **Transition fails**: PR merged, ticket not changed
