---
description: Manages PR ready status and ticket review workflow. Use when you need to mark draft PRs as ready for review and update ticket status.
allowed-tools: Bash(gh *), AskUserQuestion
argument-hint: ""
---

# Mark PR Ready with Jira Integration

## Overview

Marks a GitHub PR as ready for review (removes draft status) and transitions the Jira ticket to "Reviewing" status.

## Usage

```
/devkit.jira.workflow.pr-ready
```

## Arguments

This command takes no arguments. It infers the ticket ID from the current branch name and PR.

## Execution

### Step 1: Get PR and Ticket Info

```bash
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' | head -1)

# Get PR info
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
PR_IS_DRAFT=$(gh pr view --json isDraft -q .isDraft 2>/dev/null || echo "false")

if [ -z "$PR_NUMBER" ]; then
    echo "Error: No PR found for current branch"
    exit 1
fi
```

### Step 2: Mark PR Ready

```bash
if [ "$PR_IS_DRAFT" = "true" ]; then
    gh pr ready "$PR_NUMBER"
    echo "Marked PR #$PR_NUMBER as ready for review"
else
    echo "PR #$PR_NUMBER is already ready for review"
fi
```

### Step 3: Confirm Transition

Ask user:
```
Transition $TICKET to "Reviewing"?
[Yes] [No]
```

If yes:

```json
{
  "tool": "jira_transition_issue",
  "arguments": {
    "issueKey": "$TICKET",
    "transitionName": "Reviewing"
  }
}
```

### Step 4: Summary

```
PR ready for review!
PR: #$PR_NUMBER
[Ticket transitioned to Reviewing if confirmed]
```

## Examples

```
/devkit.jira.workflow.pr-ready
# Output:
# Marked PR #45 as ready for review
# Transition PROJ-456 to "Reviewing"? [Yes]
# Done
```

## Error Handling

- **No PR found**: Exit with error
- **Already ready**: Continue to transition
- **Transition fails**: PR updated, ticket not changed
