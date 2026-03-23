# Complete Workflow Examples

## Example 1: Resolve a Feature Issue

**User request:** "Resolve issue #42"

### Phase 1 — Fetch Issue

```bash
# Get issue metadata
gh issue view 42 --json title,labels,assignees,state
# Returns: { "title": "Add email validation to registration form", "labels": [{"name": "enhancement"}], "state": "open" }

# Display full issue for user to read
gh issue view 42
# Shows title, body, comments for user review
```

### Phase 2 — User Confirms Requirements

After reading the issue, user describes requirements:
- Add email format validation to the registration endpoint
- Return 400 with clear error message for invalid emails
- Acceptance criteria: RFC 5322 compliant validation

**Requirements Summary created:**
```markdown
## Requirements Summary

**Type**: Feature
**Scope**: Add email validation to user registration

### Must Have
- Email format validation (RFC 5322 compliant)
- Return 400 with descriptive error for invalid emails
- Unit tests for validation logic

### Out of Scope
- Email verification via SMTP
- Email normalization
```

### Phase 3 — Documentation Verification

Uses Context7 to retrieve:
- Email validation libraries for the project's language
- RFC 5322 specification details
- Framework-specific validation patterns

**Verification Summary:**
```markdown
## Verification Summary

### Libraries Verified
- **validator.js** v13.11.0: ✅ Current
  - Notes: Provides `isEmail()` with RFC 5322 compliance

### Quality Checks
- [x] API usage matches official documentation
- [x] No deprecated features in proposed approach
```

### Phase 4 — Implement

**Explore codebase:**
```bash
# Find existing validation patterns
grep -r "validation" src/
# Locate registration endpoint
find src -name "*registration*"
```

**Implementation plan presented to user:**
1. Add validator library dependency
2. Create email validator utility
3. Integrate validator in registration endpoint
4. Add error handling for invalid emails
5. Write unit tests

User approves → Implementation proceeds.

### Phase 5 — Verify & Test

```bash
# Run test suite
npm test
# PASS: All 127 tests passed

# Run linter
npm run lint
# PASS: No linting errors

# Type checking
npx tsc --noEmit
# PASS: No type errors

# Verify acceptance criteria
- [x] Email validation implemented
- [x] Returns 400 for invalid emails
- [x] Unit tests added and passing
```

**Test & Quality Report:**
```markdown
## Test & Quality Report

### Test Results
- Unit tests: ✅ Passed (132/132)
- Integration tests: ✅ Passed (45/45)

### Lint & Static Analysis
- Linter: ✅ No issues
- Type checking: ✅ Passed
- Formatting: ✅ Consistent

### Acceptance Criteria
- [x] Email validation (RFC 5322) — verified
- [x] Returns 400 for invalid emails — verified
- [x] Unit tests added — verified
```

### Phase 6 — Code Review

Launch code review agent → No critical or major issues found.

### Phase 7 — Commit and Push

```bash
# Check status
git status --porcelain
# M src/controllers/auth.ts
# M src/utils/validators.ts
# A src/tests/validators.test.ts

# Create branch
git checkout -b "feature/42-add-email-validation"

# Commit
git add -A
git commit -m "feat(validation): add email validation to registration

- Implement RFC 5322 email format validation using validator.js
- Return 400 with descriptive error for invalid emails
- Add unit tests for edge cases (empty string, malformed, valid formats)

Closes #42"

# Push
git push -u origin "feature/42-add-email-validation"
```

### Phase 8 — Create Pull Request

```bash
# Detect default branch
TARGET_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
# main

# Create PR
gh pr create \
    --base main \
    --title "feat(validation): add email validation to registration" \
    --body "## Description

Adds email format validation to the user registration endpoint to prevent invalid email addresses from being stored in the database.

## Changes

- Email format validator using validator.js (RFC 5322 compliant)
- Error response for invalid emails (400 with descriptive message)
- Unit tests covering edge cases (empty, malformed, valid formats)

## Related Issue

Closes #42

## Verification

- [x] All acceptance criteria met
- [x] Tests pass (132/132)
- [x] Code review completed
- [x] No breaking changes"

# Add label
gh pr edit --add-label "enhancement"

# Display PR URL
PR_URL=$(gh pr view --json url -q .url)
# https://github.com/org/repo/pull/145
```

---

## Example 2: Fix a Bug Issue

**User request:** "Work on issue #15 - login timeout bug"

### Phase 1 — Fetch Issue

```bash
gh issue view 15 --json title,labels,state
# Returns: { "title": "Login times out after 5 seconds", "labels": [{"name": "bug"}], "state": "open" }

gh issue view 15
# Displays full issue for user review
```

### Phase 2 — Analyze & Clarify

User describes the problem:
- Login request times out after 5 seconds
- Happens intermittently, not always
- No specific error message, just timeout

Agent identifies gaps and asks via AskUserQuestion:
- "What browser and version are you using?"
- "What region/server is this hitting?"
- "Can you reproduce consistently or is it random?"

User provides answers → Requirements complete.

### Phase 3 — Documentation Verification

Context7 retrieves:
- JWT library timeout configuration
- Framework session timeout defaults
- Best practices for authentication timeouts

### Phase 4 — Implement

**Explore codebase:**
```bash
# Find authentication module
find src -name "*auth*" -o -name "*login*"
# Locate timeout configuration
grep -r "timeout" src/auth/
```

**Root cause identified:** JWT token verification using 5s timeout instead of 30s (config value in seconds not milliseconds).

**Implementation:**
```typescript
// Before
const token = await jwt.verify(token, secret, { timeout: 5000 });

// After
const token = await jwt.verify(token, secret, { timeout: config.timeout * 1000 });
```

### Phase 5 — Verify & Test

```bash
# Run tests
npm test
# PASS: All tests passed

# Add regression test
# Test verifies timeout uses milliseconds, not seconds

# Run full suite
npm test
# PASS: 130/130 tests passed
```

### Phase 6 — Code Review

Review finds no issues.

### Phase 7 — Commit and Push

```bash
git checkout -b "fix/15-login-timeout"

git add -A
git commit -m "fix(auth): resolve login timeout issue

JWT token verification was using a 5s timeout instead of 30s
due to config value being read in seconds instead of milliseconds.

Root cause: Config timeout (30) was passed directly to jwt.verify()
which expects milliseconds, not seconds.

Fix: Multiply config timeout by 1000 to convert to milliseconds.

Closes #15"

git push -u origin "fix/15-login-timeout"
```

### Phase 8 — Create Pull Request

```bash
gh pr create \
    --base main \
    --title "fix(auth): resolve login timeout issue" \
    --body "## Description

Fixes login timeout caused by incorrect timeout unit in JWT verification.

## Root Cause

JWT token verification was configured with a 5-second timeout instead
of the expected 30 seconds because the configuration value (30) was
interpreted as milliseconds instead of seconds.

## Changes

- Fix timeout config to multiply by 1000 (convert seconds to milliseconds)
- Add regression test for timeout configuration
- Add comment explaining timeout unit conversion

## Related Issue

Closes #15

## Verification

- [x] Timeout now uses correct unit (30s instead of 5s)
- [x] Regression test added
- [x] All tests pass (130/130)"
```

---

## Example 3: Issue with Missing Information

**User request:** "Implement issue #78"

### Phase 1 — Fetch Issue

```bash
gh issue view 78 --json title,labels
# Returns: { "title": "Improve search performance", "labels": [{"name": "enhancement"}] }

gh issue view 78
# Issue body is vague: "Search is slow, make it faster"
```

### Phase 2 — Clarify Requirements

User describes the goal: "The product search page takes too long to load."

Agent identifies gaps and asks via AskUserQuestion:

**Question 1:** "What search functionality should be optimized?"
- Options: Product search / User search / Full-text search / All search
- User selects: Product search

**Question 2:** "What is the current response time and what's the target?"
- User provides: "Currently 3-5 seconds, target is <1 second"

**Question 3:** "Should this include database query optimization, caching, or both?"
- Options: Database only / Caching only / Both
- User selects: Both

**Requirements Summary:**
```markdown
## Requirements Summary

**Type**: Enhancement
**Scope**: Optimize product search performance

### Must Have
- Reduce product search response time from 3-5s to <1s
- Implement database query optimization
- Add caching layer for search results

### Nice to Have
- Search analytics to track slow queries
- Performance monitoring dashboard

### Out of Scope
- User search optimization (separate issue)
- Full-text search reindexing
```

### Phase 3+ — Proceed with Implementation

Verifies documentation via Context7, explores codebase, implements query optimization and caching, follows same test/review/commit/PR workflow as previous examples.

---

## Summary of Patterns

All examples follow the same 8-phase workflow:

1. **Fetch** - Get issue, display to user
2. **Analyze** - User describes requirements, clarify gaps
3. **Verify** - Check documentation via Context7
4. **Implement** - Explore, plan, code changes
5. **Test** - Run full test suite, lint, type checking
6. **Review** - Code review, fix issues
7. **Commit** - Branch with naming convention, conventional commit
8. **PR** - Create PR with issue reference, labels

**Key principles:**
- User confirms requirements (not parsed from issue)
- Comprehensive testing before commit
- Code review prevents shipping bugs
- Conventional commits and branch naming
- PR references issue for automatic closure on merge
