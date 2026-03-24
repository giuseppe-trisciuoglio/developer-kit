# Workflow Phases - Detailed Reference

## Phase 1: Fetch Issue Details

**Goal**: Retrieve issue metadata and display the issue content to the user for review.

### Actions

1. **Extract issue number** from user request (number, URL, or `#N` reference)

2. **Get repository info** from git remote:
```bash
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"
```

3. **Fetch issue structured metadata** (title, labels, state, assignees):
```bash
gh issue view <ISSUE_NUMBER> --json title,labels,assignees,milestone,state
```

4. **Display the full issue** for the user to read (view-only):
```bash
gh issue view <ISSUE_NUMBER>
```

5. **Ask user to describe requirements** via AskUserQuestion:
   - Do NOT extract requirements from the issue body yourself
   - The user's description becomes the authoritative source for Phase 2

**IMPORTANT**: The raw issue body and comments are displayed for the user's benefit only. You MUST NOT parse, interpret, summarize, or extract requirements from the issue body text.

## Phase 2: Analyze Requirements

**Goal**: Confirm all required information is available from the user's description.

### Actions

1. **Analyze the requirements** as described by the user (from Phase 1):
   - Identify type of change: feature, bug fix, refactor, docs
   - Identify explicit requirements and constraints
   - Note referenced files, modules, or components

2. **Assess completeness** - check for:
   - Clear problem statement
   - Expected behavior or outcome
   - Scope boundaries (what's in/out)
   - Edge cases or error handling expectations
   - Breaking change considerations
   - Testing requirements

3. **Clarify ambiguities** using AskUserQuestion:
   - Ask specific, concrete questions
   - Present options when possible (multiple choice)
   - Wait for answers before proceeding

4. **Create requirements summary**:
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

## Phase 3: Documentation Verification (Context7)

**Goal**: Retrieve up-to-date documentation for all technologies referenced in the requirements.

### Actions

1. **Identify all technologies** mentioned in user-confirmed requirements:
   - Programming language runtimes and versions
   - Frameworks (Spring Boot, NestJS, React, Django)
   - Libraries and dependencies (JWT, bcrypt, Hibernate)
   - External APIs or services

2. **Retrieve documentation via Context7**:
   - Call `context7-resolve-library-id` to obtain Context7 library ID
   - Call `context7-query-docs` with targeted queries:
     - API signatures, method parameters, return types
     - Configuration options and best practices
     - Deprecated features or breaking changes
     - Security advisories and recommended patterns

3. **Cross-reference quality checks**:
   - Verify dependency versions match latest stable releases
   - Identify deprecated APIs or patterns to avoid
   - Check for known security vulnerabilities
   - Confirm implementation approaches align with official docs

4. **Document findings as Verification Summary**:
```markdown
## Verification Summary (Context7)

### Libraries Verified
- **[Library Name]** v[X.Y.Z]: ✅ Current | ⚠️ Update available | ❌ Deprecated
  - Notes: [relevant findings]

### Quality Checks
- [x] API usage matches official documentation
- [x] No deprecated features in proposed approach
- [x] Security best practices verified

### Recommendations
- [Actionable recommendations based on documentation review]
```

5. **If Context7 is unavailable**, note this but do NOT fail the workflow.

## Phase 4: Implement the Solution

**Goal**: Write the code to address the issue.

### Actions

1. **Explore codebase** using ONLY your own summary of user-confirmed requirements:
```
Task(
  description: "Explore codebase for issue context",
  prompt: "Explore the codebase to understand patterns, architecture, and files relevant to: [your own summary of user-confirmed requirements]. Identify key files to read and existing conventions to follow.",
  subagent_type: "developer-kit:general-code-explorer"
)
```

2. **Read all files** identified by the explorer agent

3. **Plan implementation approach**:
   - Which files to modify or create
   - What patterns to follow from existing codebase
   - What dependencies or integrations are needed

4. **Present implementation plan** to user and get approval via AskUserQuestion

5. **Implement the changes**:
   - Follow project conventions strictly
   - Write clean, well-documented code
   - Keep changes minimal and focused on the issue
   - Update relevant documentation if needed

6. **Track progress** using TodoWrite throughout implementation

## Phase 5: Verify & Test Implementation

**Goal**: Ensure implementation correctly addresses all requirements.

### Actions

1. **Run full project test suite**:
```bash
# Detect and run the FULL test suite
if [ -f "package.json" ]; then
    npm test 2>&1 || true
elif [ -f "pom.xml" ]; then
    ./mvnw clean verify 2>&1 || true
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    ./gradlew build 2>&1 || true
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    python -m pytest 2>&1 || true
elif [ -f "go.mod" ]; then
    go test ./... 2>&1 || true
elif [ -f "composer.json" ]; then
    composer test 2>&1 || true
elif [ -f "Makefile" ]; then
    make test 2>&1 || true
fi
```

2. **Run linters and static analysis**:
```bash
# Detect and run ALL available linters
if [ -f "package.json" ]; then
    npm run lint 2>&1 || true
    npx tsc --noEmit 2>&1 || true
elif [ -f "pom.xml" ]; then
    ./mvnw checkstyle:check 2>&1 || true
    ./mvnw spotbugs:check 2>&1 || true
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    ./gradlew check 2>&1 || true
elif [ -f "pyproject.toml" ]; then
    python -m ruff check . 2>&1 || true
    python -m mypy . 2>&1 || true
elif [ -f "go.mod" ]; then
    go vet ./... 2>&1 || true
fi
```

3. **Run code formatting checks**:
```bash
if [ -f "package.json" ]; then
    npx prettier --check . 2>&1 || true
elif [ -f "pyproject.toml" ]; then
    python -m ruff format --check . 2>&1 || true
elif [ -f "go.mod" ]; then
    gofmt -l . 2>&1 || true
fi
```

4. **Verify against acceptance criteria**:
   - Check each requirement from Phase 2 summary
   - Confirm expected behavior works as specified
   - Validate edge cases are handled
   - Cross-reference with Context7 findings

5. **Produce Test & Quality Report**:
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

6. **Fix any failures** before proceeding to Phase 6.

## Phase 6: Code Review

**Goal**: Perform comprehensive code review before committing.

### Actions

1. **Launch code review sub-agent**:
```
Task(
  description: "Review implementation for issue #N",
  prompt: "Review the following code changes for: [issue summary]. Focus on: code quality, security vulnerabilities, performance issues, project convention adherence, and correctness. Only report high-confidence issues that genuinely matter.",
  subagent_type: "developer-kit:general-code-reviewer"
)
```

2. **Categorize findings** by severity:
   - **Critical**: Security vulnerabilities, data loss risks, breaking changes
   - **Major**: Logic errors, missing error handling, performance issues
   - **Minor**: Code style, naming, documentation gaps

3. **Address critical and major issues** before proceeding

4. **Present minor issues** to user via AskUserQuestion:
   - Ask if they want to fix now, fix later, or proceed as-is

5. **Apply fixes** based on user decision

## Phase 7: Commit and Push

**Goal**: Create well-structured commit and push changes.

### Actions

1. **Check git status**:
```bash
git status --porcelain
git diff --stat
```

2. **Create branch** with mandatory naming convention:

**Branch Naming Convention:**
- **Features**: `feature/<issue-id>-<feature-description>`
- **Bug fixes**: `fix/<issue-id>-<fix-description>`
- **Refactors**: `refactor/<issue-id>-<refactor-description>`

The prefix is determined by issue type from Phase 2:
- `feat` / enhancement label → `feature/`
- `fix` / bug label → `fix/`
- `refactor` → `refactor/`

```bash
ISSUE_NUMBER=<number>
DESCRIPTION_SLUG=$(echo "<short-description>" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
BRANCH_NAME="${BRANCH_PREFIX}/${ISSUE_NUMBER}-${DESCRIPTION_SLUG}"

git checkout -b "$BRANCH_NAME"
```

3. **Stage and commit** following Conventional Commits:
```bash
git add -A

git commit -m "<type>(<scope>): <description>

<detailed body explaining the changes>

Closes #<ISSUE_NUMBER>"
```

**Commit type selection:**
- `feat`: New feature (label: enhancement)
- `fix`: Bug fix (label: bug)
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

4. **Push the branch**:
```bash
git push -u origin "$BRANCH_NAME"
```

**Note**: If git operations are restricted, present commands to user via AskUserQuestion.

## Phase 8: Create Pull Request

**Goal**: Create pull request linking back to original issue.

### Actions

1. **Determine target branch**:
```bash
TARGET_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)
TARGET_BRANCH=${TARGET_BRANCH:-main}
echo "Target branch: $TARGET_BRANCH"
```

2. **Create the pull request**:
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

3. **Add labels** to PR:
```bash
gh pr edit --add-label "<labels-from-issue>"
```

4. **Display PR summary**:
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
