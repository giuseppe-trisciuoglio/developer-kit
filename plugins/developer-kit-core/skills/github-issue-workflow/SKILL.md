---
name: github-issue-workflow
description: Implements a complete workflow for resolving GitHub issues directly from Claude Code. Guides through the full lifecycle from fetching issue details, analyzing requirements, implementing the solution, verifying correctness, performing code review, committing changes, and creating a pull request. Use when user asks to "resolve issue", "implement issue", "work on issue #N", "fix issue", "close issue", or references a GitHub issue number for implementation. Triggers on "github issue workflow", "resolve github issue", "implement issue #", "work on issue".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, AskUserQuestion, TodoWrite
---

# GitHub Issue Resolution Workflow

Implements a complete workflow for resolving GitHub issues directly from Claude Code. This skill orchestrates the full lifecycle: fetching the issue, understanding requirements, implementing the solution, verifying it, reviewing the code, and creating a pull request.

## Overview

This skill provides a structured 7-phase approach to resolving GitHub issues. It leverages the `gh` CLI for GitHub API interactions and coordinates sub-agents for code exploration, implementation, and review. The workflow ensures consistent, high-quality issue resolution with proper traceability.

## When to Use

Use this skill when:

- User asks to "resolve", "implement", "work on", or "fix" a GitHub issue
- User references a specific issue number (e.g., "issue #42")
- User wants to go from issue description to pull request in a guided workflow
- User pastes a GitHub issue URL
- User asks to "close an issue with code"

**Trigger phrases:** "resolve issue", "implement issue #N", "work on issue", "fix issue #N", "github issue workflow", "close issue with PR"

## Prerequisites

Before starting, verify that the following tools are available:

```bash
# Verify GitHub CLI is installed and authenticated
gh auth status

# Verify git is configured
git config --get user.name && git config --get user.email

# Verify we're in a git repository
git rev-parse --git-dir
```

If any prerequisite fails, inform the user and provide setup instructions.

## Instructions

### Phase 1: Fetch Issue Details

**Goal**: Retrieve and parse the GitHub issue information.

**Actions**:

1. Extract the issue number from the user's request (number, URL, or `#N` reference)
2. Determine the repository owner and name from the git remote:

```bash
# Get repository info from remote
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"
```

3. Fetch the issue details:

```bash
# Fetch issue details
gh issue view <ISSUE_NUMBER> --json title,body,labels,assignees,milestone,state,comments

# Also fetch issue comments for additional context
gh issue view <ISSUE_NUMBER> --comments
```

4. Parse and organize the following from the issue:
   - **Title**: The issue title
   - **Description**: The full issue body
   - **Labels**: Any assigned labels (bug, enhancement, etc.)
   - **Acceptance criteria**: Extract from the issue body if present
   - **Related context**: Comments, linked issues, or referenced PRs

5. Present a summary of the issue to the user for confirmation.

### Phase 2: Analyze Requirements

**Goal**: Ensure all required information is available before implementation.

**Actions**:

1. Analyze the issue description thoroughly:
   - Identify the type of change: feature, bug fix, refactor, docs, etc.
   - Extract explicit requirements and constraints
   - Identify acceptance criteria (if specified)
   - Note any referenced files, modules, or components

2. Assess completeness — check for:
   - Clear problem statement
   - Expected behavior or outcome
   - Scope boundaries (what's in/out)
   - Edge cases or error handling expectations
   - Breaking change considerations
   - Testing requirements

3. If information is missing or ambiguous, use **AskUserQuestion** to clarify:
   - Ask specific, concrete questions (not vague ones)
   - Present options when possible (multiple choice)
   - Wait for answers before proceeding

4. Create a requirements summary:

```markdown
## Requirements Summary

**Type**: [Feature / Bug Fix / Refactor / Docs]
**Scope**: [Brief scope description]

### Must Have
- Requirement 1
- Requirement 2

### Nice to Have
- Optional requirement 1

### Out of Scope
- Item explicitly excluded
```

### Phase 3: Implement the Solution

**Goal**: Write the code to address the issue.

**Actions**:

1. Explore the codebase to understand existing patterns:

```
Task(
  description: "Explore codebase for issue context",
  prompt: "Explore the codebase to understand patterns, architecture, and files relevant to: [issue summary]. Identify key files to read and existing conventions to follow.",
  subagent_type: "developer-kit:general-code-explorer"
)
```

2. Read all files identified by the explorer agent to build deep context
3. Plan the implementation approach:
   - Which files to modify or create
   - What patterns to follow from the existing codebase
   - What dependencies or integrations are needed

4. Present the implementation plan to the user and get approval via **AskUserQuestion**

5. Implement the changes:
   - Follow project conventions strictly
   - Write clean, well-documented code
   - Keep changes minimal and focused on the issue
   - Update relevant documentation if needed

6. Track progress using **TodoWrite** throughout implementation

### Phase 4: Verify Implementation

**Goal**: Ensure the implementation correctly addresses all requirements.

**Actions**:

1. Run existing project tests (if available):

```bash
# Detect and run test suite
# Look for common test runners
if [ -f "package.json" ]; then
    npm test 2>&1 || true
elif [ -f "pom.xml" ]; then
    mvn test 2>&1 || true
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    ./gradlew test 2>&1 || true
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    python -m pytest 2>&1 || true
elif [ -f "Makefile" ]; then
    make test 2>&1 || true
fi
```

2. Verify against acceptance criteria:
   - Check each acceptance criterion from the issue
   - Confirm expected behavior works as specified
   - Validate edge cases are handled

3. Run linters/formatters if available:

```bash
# Detect and run linters
if [ -f "package.json" ]; then
    npm run lint 2>&1 || true
elif [ -f "pom.xml" ]; then
    mvn checkstyle:check 2>&1 || true
elif [ -f "pyproject.toml" ]; then
    python -m ruff check . 2>&1 || true
fi
```

4. Report verification results to the user. If tests fail, fix the issues before proceeding.

### Phase 5: Code Review

**Goal**: Perform a comprehensive code review before committing.

**Actions**:

1. Launch a code review sub-agent:

```
Task(
  description: "Review implementation for issue #N",
  prompt: "Review the following code changes for: [issue summary]. Focus on: code quality, security vulnerabilities, performance issues, project convention adherence, and correctness. Only report high-confidence issues that genuinely matter.",
  subagent_type: "developer-kit:general-code-reviewer"
)
```

2. Review the findings and categorize by severity:
   - **Critical**: Security vulnerabilities, data loss risks, breaking changes
   - **Major**: Logic errors, missing error handling, performance issues
   - **Minor**: Code style, naming, documentation gaps

3. Address critical and major issues before proceeding
4. Present remaining minor issues to the user via **AskUserQuestion**:
   - Ask if they want to fix now, fix later, or proceed as-is
5. Apply fixes based on user decision

### Phase 6: Commit and Push

**Goal**: Create a well-structured commit and push changes.

**Actions**:

1. Check the current git status:

```bash
git status --porcelain
git diff --stat
```

2. Create a feature branch from the current branch:

```bash
# Generate branch name from issue
ISSUE_NUMBER=<number>
ISSUE_TITLE_SLUG=$(echo "<issue-title>" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
BRANCH_NAME="issue-${ISSUE_NUMBER}/${ISSUE_TITLE_SLUG}"

git checkout -b "$BRANCH_NAME"
```

3. Stage and commit changes following Conventional Commits:

```bash
# Stage all changes
git add -A

# Commit with conventional format referencing the issue
git commit -m "<type>(<scope>): <description>

<detailed body explaining the changes>

Closes #<ISSUE_NUMBER>"
```

**Commit type selection**:
- `feat`: New feature (label: enhancement)
- `fix`: Bug fix (label: bug)
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

4. Push the branch:

```bash
git push -u origin "$BRANCH_NAME"
```

**Important**: If the skill does not have permissions to run `git add`, `git commit`, or `git push`, present the exact commands to the user and ask them to execute manually using **AskUserQuestion**.

### Phase 7: Create Pull Request

**Goal**: Create a pull request linking back to the original issue.

**Actions**:

1. Determine the target branch:

```bash
# Detect default branch
TARGET_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)
TARGET_BRANCH=${TARGET_BRANCH:-main}
echo "Target branch: $TARGET_BRANCH"
```

2. Create the pull request using `gh`:

```bash
gh pr create \
    --base "$TARGET_BRANCH" \
    --title "<type>(<scope>): <description>" \
    --body "## Description

<Summary of changes and motivation from the issue>

## Changes

- Change 1
- Change 2
- Change 3

## Related Issue

Closes #<ISSUE_NUMBER>

## Verification

- [ ] All acceptance criteria met
- [ ] Tests pass
- [ ] Code review completed
- [ ] No breaking changes"
```

3. Add relevant labels to the PR:

```bash
# Mirror issue labels to PR
gh pr edit --add-label "<labels-from-issue>"
```

4. Display the PR summary:

```bash
PR_URL=$(gh pr view --json url -q .url)
PR_NUMBER=$(gh pr view --json number -q .number)

echo ""
echo "Pull Request Created Successfully"
echo "PR: #$PR_NUMBER"
echo "URL: $PR_URL"
echo "Issue: #<ISSUE_NUMBER>"
echo "Branch: $BRANCH_NAME -> $TARGET_BRANCH"
```

## Examples

### Example 1: Resolve a Feature Issue

**User request:** "Resolve issue #42"

**Phase 1 — Fetch issue:**
```bash
gh issue view 42 --json title,body,labels,assignees,state
# Returns: "Add email validation to registration form" (label: enhancement)
```

**Phase 2 — Requirements confirmed:**
- Add email format validation to the registration endpoint
- Return 400 with clear error message for invalid emails
- Acceptance criteria: RFC 5322 compliant validation

**Phase 3 — Implement:** Explores codebase, finds existing validation patterns, implements email validation following project conventions.

**Phase 6–7 — Commit and PR:**
```bash
git checkout -b "issue-42/add-email-validation"
git add -A
git commit -m "feat(validation): add email validation to registration

- Implement RFC 5322 email format validation
- Return 400 with descriptive error for invalid emails
- Add unit tests for edge cases

Closes #42"
git push -u origin "issue-42/add-email-validation"
gh pr create --base main --title "feat(validation): add email validation" \
    --body "## Description
Adds email validation to the registration endpoint.

## Changes
- Email format validator (RFC 5322)
- Error response for invalid emails
- Unit tests

## Related Issue
Closes #42"
```

### Example 2: Fix a Bug Issue

**User request:** "Work on issue #15 - login timeout bug"

**Phase 1 — Fetch issue:**
```bash
gh issue view 15 --json title,body,labels,comments
# Returns: "Login times out after 5 seconds" (label: bug)
```

**Phase 2 — Analyze:** Identifies missing reproduction steps, asks user for browser/environment details via AskUserQuestion.

**Phase 3–5 — Implement and review:** Traces bug to authentication module, fixes timeout configuration, adds regression test, launches code review sub-agent.

**Phase 6–7 — Commit and PR:**
```bash
git checkout -b "issue-15/fix-login-timeout-bug"
git add -A
git commit -m "fix(auth): resolve login timeout issue

JWT token verification was using a 5s timeout instead of 30s
due to config value being read in seconds instead of milliseconds.

Closes #15"
git push -u origin "issue-15/fix-login-timeout-bug"
gh pr create --base main --title "fix(auth): resolve login timeout issue" \
    --body "## Description
Fixes login timeout caused by incorrect timeout unit in JWT verification.

## Changes
- Fix timeout config to use milliseconds
- Add regression test

## Related Issue
Closes #15"
```

### Example 3: Issue with Missing Information

**User request:** "Implement issue #78"

**Phase 1 — Fetch issue:**
```bash
gh issue view 78 --json title,body,labels
# Returns: "Improve search performance" (label: enhancement) — vague description
```

**Phase 2 — Clarify:** Identifies gaps (no metrics, no target, no scope). Asks user via AskUserQuestion:
- "What search functionality should be optimized? (product search / user search / full-text search)"
- "What is the current response time and what's the target?"
- "Should this include database query optimization, caching, or both?"

**Phase 3+:** Proceeds with implementation after receiving answers, following the same commit and PR workflow.

## Best Practices

1. **Always confirm understanding**: Present issue summary to user before implementing
2. **Ask early, ask specific**: Identify ambiguities in Phase 2, not during implementation
3. **Keep changes focused**: Only modify what's necessary to resolve the issue
4. **Reference the issue**: Every commit and PR must reference the issue number
5. **Run existing tests**: Never skip verification — catch regressions early
6. **Review before committing**: Code review prevents shipping bugs
7. **Use conventional commits**: Maintain consistent commit history

## Constraints and Warnings

1. **Never modify code without understanding the issue first**: Always complete Phase 1 and 2 before Phase 3
2. **Don't skip user confirmation**: Get approval before implementing and before creating the PR
3. **Handle permission limitations gracefully**: If git operations are restricted, provide commands for the user
4. **Don't close issues directly**: Let the PR merge close the issue via "Closes #N"
5. **Respect branch protection rules**: Create feature branches, never commit to protected branches
6. **Keep PRs atomic**: One issue per PR unless issues are tightly coupled
