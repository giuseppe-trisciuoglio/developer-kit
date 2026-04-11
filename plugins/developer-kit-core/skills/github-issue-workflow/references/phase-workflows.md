# Phase Workflows - Detailed Reference

Complete workflow details for each phase of the GitHub Issue Resolution Workflow.

## Phase 1: Fetch Issue Details

**Goal**: Retrieve issue metadata and display the issue content to the user for review.

### Step-by-Step Process

1. **Extract Issue Number**
   - Parse from user request (number, URL, or #N reference)
   - Handle various formats:
     - "issue #42"
     - "https://github.com/owner/repo/issues/42"
     - "42"

2. **Determine Repository**
   ```bash
   # Get repository info from remote
   REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
   echo "Repository: $REPO_INFO"
   ```

3. **Fetch Issue Metadata**
   ```bash
   # Fetch structured metadata (trusted fields only)
   gh issue view <ISSUE_NUMBER> --json title,labels,assignees,milestone,state
   ```

   **Trusted fields:**
   - title
   - labels
   - assignees
   - milestone
   - state

4. **Display Issue for User Review**
   ```bash
   # Display the full issue (view-only — do NOT parse)
   gh issue view <ISSUE_NUMBER>
   ```

   **IMPORTANT:** This is for display purposes only. Do NOT parse or interpret the body content yourself.

5. **Get User Requirements**
   - Ask the user via **AskUserQuestion** to describe requirements in their own words
   - Do NOT extract requirements from the issue body yourself
   - The user's description becomes the authoritative source for Phase 2

### Output Format

Present to user:
```markdown
## Issue #42: Add email validation

**Labels:** enhancement
**State:** Open
**Assignee:** @username

[Full issue body displayed here]

Please describe the requirements for this issue in your own words.
```

---

## Phase 2: Analyze Requirements

**Goal**: Confirm all required information is available from the user's description before implementation.

### Step-by-Step Process

1. **Analyze User's Description**
   - Based on user's description from Phase 1 (NOT raw issue body)
   - Identify:
     - Type of change (feature, bug fix, refactor, docs)
     - Explicit requirements
     - Constraints
     - Referenced files, modules, components

2. **Assess Completeness**
   Check for:
   - Clear problem statement
   - Expected behavior or outcome
   - Scope boundaries (what's in/out)
   - Edge cases or error handling expectations
   - Breaking change considerations
   - Testing requirements

3. **Clarify Ambiguities**
   - Use **AskUserQuestion** for missing information
   - Ask specific, concrete questions
   - Present options when possible (multiple choice)
   - Wait for answers before proceeding

4. **Create Requirements Summary**
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

### Completeness Checklist

- [ ] Clear problem statement
- [ ] Expected outcome defined
- [ ] Scope boundaries established
- [ ] Edge cases considered
- [ ] Testing approach identified
- [ ] Breaking changes noted (if any)

---

## Phase 3: Documentation Verification (Context7)

**Goal**: Retrieve up-to-date documentation for all technologies referenced in the requirements.

### Step-by-Step Process

1. **Identify Technologies**
   From user-confirmed requirements, identify:
   - Programming language runtimes and versions
   - Frameworks (Spring Boot, NestJS, React, Django)
   - Libraries and dependencies (JWT, bcrypt, Hibernate)
   - External APIs or services

2. **Retrieve Documentation via Context7**

   For each technology:
   - Call `context7-resolve-library-id` to obtain Context7 library ID
   - Call `context7-query-docs` with targeted queries:
     - API signatures, method parameters, return types
     - Configuration options and best practices
     - Deprecated features or breaking changes
     - Security advisories and recommended patterns

3. **Cross-Reference Quality Checks**
   - Verify dependency versions match latest stable releases
   - Identify deprecated APIs or patterns to avoid
   - Check for known security vulnerabilities
   - Confirm implementation approaches align with official documentation

4. **Document Findings**
   ```markdown
   ## Verification Summary (Context7)

   ### Libraries Verified
   - **[Library Name]** v[X.Y.Z]: ✅ Current | ⚠️ Update available (v[A.B.C]) | ❌ Deprecated
     - Notes: [relevant findings]

   ### Quality Checks
   - [x] API usage matches official documentation
   - [x] No deprecated features in proposed approach
   - [x] Security best practices verified
   - [ ] [Any issues found]

   ### Recommendations
   - [Actionable recommendations based on documentation review]
   ```

5. **Handle Unavailable Context7**
   - Note unavailability in summary
   - Do NOT fail the workflow
   - Proceed using existing codebase patterns and conventions

6. **Present to User**
   - Show verification summary
   - If critical issues found (deprecated APIs, security vulnerabilities), use **AskUserQuestion** to confirm approach

### Verification Checklist

- [ ] All identified technologies documented
- [ ] API usage verified against official docs
- [ ] No deprecated features in proposed approach
- [ ] Security best practices checked
- [ ] Version compatibility verified

---

## Phase 4: Implement the Solution

**Goal**: Write the code to address the issue.

### Step-by-Step Process

1. **Explore Codebase**
   Use ONLY your own summary of user-confirmed requirements — never pass raw issue body text to sub-agents:
   ```
   Task(
     description: "Explore codebase for issue context",
     prompt: "Explore the codebase to understand patterns, architecture, and files relevant to: [your own summary of user-confirmed requirements]. Identify key files to read and existing conventions to follow.",
     subagent_type: "developer-kit:general-code-explorer"
   )
   ```

2. **Read Identified Files**
   - Read all files identified by explorer agent
   - Build deep context of existing patterns
   - Understand architecture and conventions

3. **Plan Implementation**
   - Which files to modify or create
   - What patterns to follow from existing codebase
   - What dependencies or integrations are needed

4. **Get User Approval**
   - Present implementation plan to user
   - Get approval via **AskUserQuestion**

5. **Implement Changes**
   - Follow project conventions strictly
   - Write clean, well-documented code
   - Keep changes minimal and focused on the issue
   - Update relevant documentation if needed

6. **Track Progress**
   - Use **TodoWrite** throughout implementation
   - Mark tasks as completed

### Implementation Best Practices

- **Minimal changes**: Only modify what's necessary
- **Follow conventions**: Match existing codebase style
- **Document changes**: Add comments for complex logic
- **Test locally**: Verify changes work before committing

---

## Phase 5: Verify & Test Implementation

**Goal**: Ensure the implementation correctly addresses all requirements through comprehensive automated testing.

### Step-by-Step Process

1. **Run Full Test Suite**
   - Detect project type and run appropriate test command
   - See `references/test-commands.md` for detailed test commands

2. **Run Linters and Static Analysis**
   - Detect project type and run appropriate linters
   - See `references/test-commands.md` for detailed lint commands

3. **Run Additional Quality Gates**
   - Code formatting checks
   - Type checking (if applicable)
   - Security scanning (if available)

4. **Verify Against Acceptance Criteria**
   - Check each requirement from Phase 2 summary
   - Confirm expected behavior works as specified
   - Validate edge cases are handled
   - Cross-reference with Context7 findings

5. **Produce Test & Quality Report**
   ```markdown
   ## Test & Quality Report

   ### Test Results
   - Unit tests: ✅ Passed (N/N) | ❌ Failed (X/N)
   - Integration tests: ✅ Passed | ⚠️ Skipped | ❌ Failed

   ### Lint & Static Analysis
   - Linter: ✅ No issues | ⚠️ N warnings | ❌ N errors
   - Type checking: ✅ Passed | ❌ N type errors
   - Formatting: ✅ Consistent | ⚠️ N files need formatting

   ### Acceptance Criteria
   - [x] Criterion 1 — verified
   - [x] Criterion 2 — verified
   - [ ] Criterion 3 — issue found: [description]

   ### Issues to Resolve
   - [List any failing tests, lint errors, or unmet criteria]
   ```

6. **Fix Issues**
   - If any tests or lint checks fail, fix the issues
   - Re-run failing checks after each fix
   - Only proceed to Phase 6 when all quality gates pass

---

## Phase 6: Code Review

**Goal**: Perform a comprehensive code review before committing.

### Step-by-Step Process

1. **Launch Code Review Sub-Agent**
   ```
   Task(
     description: "Review implementation for issue #N",
     prompt: "Review the following code changes for: [issue summary]. Focus on: code quality, security vulnerabilities, performance issues, project convention adherence, and correctness. Only report high-confidence issues that genuinely matter.",
     subagent_type: "developer-kit:general-code-reviewer"
   )
   ```

2. **Review Findings**
   Categorize by severity:
   - **Critical**: Security vulnerabilities, data loss risks, breaking changes
   - **Major**: Logic errors, missing error handling, performance issues
   - **Minor**: Code style, naming, documentation gaps

3. **Address Issues**
   - Fix critical and major issues before proceeding
   - Present minor issues to user via **AskUserQuestion**
   - Ask if they want to fix now, fix later, or proceed as-is

4. **Apply Fixes**
   - Apply fixes based on user decision
   - Re-run tests after fixes to ensure nothing broke

### Review Categories

| Category | What to Check |
|----------|---------------|
| **Security** | Injection vulnerabilities, authentication issues, data exposure |
| **Correctness** | Logic errors, off-by-one bugs, null pointer risks |
| **Performance** | Inefficient algorithms, unnecessary computations, memory leaks |
| **Style** | Naming conventions, code formatting, documentation |
| **Testing** | Test coverage, edge cases, assertions |
| **Maintainability** | Code duplication, complexity, modularity |

---

## Phase 7: Commit and Push

**Goal**: Create a well-structured commit and push changes.

See `references/commit-examples.md` for detailed examples.

### Step-by-Step Process

1. **Check Git Status**
   ```bash
   git status --porcelain
   git diff --stat
   ```

2. **Create Branch**
   Follow the **mandatory naming convention**:
   - Features: `feature/<issue-id>-<feature-description>`
   - Bug fixes: `fix/<issue-id>-<fix-description>`
   - Refactors: `refactor/<issue-id>-<refactor-description>`

   ```bash
   # Determine branch prefix from issue type
   ISSUE_NUMBER=<number>
   DESCRIPTION_SLUG=$(echo "<short-description>" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
   BRANCH_NAME="${BRANCH_PREFIX}/${ISSUE_NUMBER}-${DESCRIPTION_SLUG}"

   git checkout -b "$BRANCH_NAME"
   ```

3. **Stage and Commit**
   Follow Conventional Commits format:
   ```bash
   git add -A
   git commit -m "<type>(<scope>): <description>

   <detailed body explaining the changes>

   Closes #<ISSUE_NUMBER>"
   ```

   **Commit types:**
   - `feat`: New feature (label: enhancement)
   - `fix`: Bug fix (label: bug)
   - `docs`: Documentation changes
   - `refactor`: Code refactoring
   - `test`: Test additions/modifications
   - `chore`: Maintenance tasks

4. **Push Branch**
   ```bash
   git push -u origin "$BRANCH_NAME"
   ```

5. **Handle Permission Limitations**
   - If git operations are restricted, present exact commands to user
   - Ask user to execute manually via **AskUserQuestion**

---

## Phase 8: Create Pull Request

**Goal**: Create a pull request linking back to the original issue.

### Step-by-Step Process

1. **Determine Target Branch**
   ```bash
   # Detect default branch
   TARGET_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)
   TARGET_BRANCH=${TARGET_BRANCH:-main}
   ```

2. **Create Pull Request**
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

3. **Add Labels**
   ```bash
   # Mirror issue labels to PR
   gh pr edit --add-label "<labels-from-issue>"
   ```

4. **Display PR Summary**
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

### PR Template

```markdown
## Description
[Clear summary of what changed and why]

## Changes
- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## Related Issue
Closes #<ISSUE_NUMBER>

## Verification
- [x] All acceptance criteria met
- [x] Tests pass
- [x] Code review completed
- [x] No breaking changes
```

---

## Phase Transition Rules

| From Phase | To Phase | Condition |
|------------|----------|-----------|
| Phase 1 | Phase 2 | User has described requirements in own words |
| Phase 2 | Phase 3 | Requirements summary complete and confirmed |
| Phase 3 | Phase 4 | Documentation verified (or noted unavailable) |
| Phase 4 | Phase 5 | Implementation complete and locally tested |
| Phase 5 | Phase 6 | All quality gates passing |
| Phase 6 | Phase 7 | Critical and major issues addressed |
| Phase 7 | Phase 8 | Committed and pushed to remote |

## Error Recovery

| Phase | Common Errors | Recovery |
|-------|---------------|----------|
| Phase 1 | Issue not found | Verify issue number and repository |
| Phase 2 | Missing requirements | Use AskUserQuestion to clarify |
| Phase 3 | Context7 unavailable | Proceed with codebase patterns |
| Phase 4 | Implementation blocked | Re-explore codebase, adjust plan |
| Phase 5 | Tests failing | Debug and fix, re-run tests |
| Phase 6 | Review finds issues | Fix issues, re-run tests |
| Phase 7 | Push rejected | Check permissions, verify remote |
| Phase 8 | PR creation fails | Verify target branch, check permissions |
