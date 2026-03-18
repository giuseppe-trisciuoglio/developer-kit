# Commit Examples - Phase 7-8 Reference

Complete examples of commits and pull requests for GitHub Issue Resolution Workflow.

## Example 1: Feature Issue - Email Validation

**User request:** "Resolve issue #42"

### Phase 1 — Fetch issue metadata and display for user:

```bash
gh issue view 42 --json title,labels,assignees,state
# Returns: "Add email validation to registration form" (label: enhancement)

gh issue view 42
# Displays full issue for user to read
```

### Phase 2 — User confirms requirements:
- Add email format validation to the registration endpoint
- Return 400 with clear error message for invalid emails
- Acceptance criteria: RFC 5322 compliant validation

### Phase 3 — Verify docs:
Uses Context7 to retrieve documentation for:
- Email validation libraries
- RFC 5322 specification
- Framework best practices

### Phase 4 — Implement:
- Explores codebase for existing validation patterns
- Finds validation utilities
- Implements email validation following project conventions

### Phase 7 — Commit:

```bash
# Check status
git status --porcelain
git diff --stat

# Create branch
git checkout -b "feature/42-add-email-validation"

# Stage and commit
git add -A
git commit -m "feat(validation): add email validation to registration

- Implement RFC 5322 email format validation
- Return 400 with descriptive error for invalid emails
- Add unit tests for edge cases (empty, invalid format, valid emails)

Closes #42"

# Push
git push -u origin "feature/42-add-email-validation"
```

### Phase 8 — Pull Request:

```bash
gh pr create \
    --base main \
    --title "feat(validation): add email validation to registration" \
    --body "## Description

Adds email validation to the user registration endpoint to ensure only valid email addresses are accepted according to RFC 5322 standard.

## Changes

- **Email validation utility**: Implemented RFC 5322 compliant email format validator
- **Registration endpoint**: Added validation before user creation
- **Error handling**: Returns 400 status with clear error message for invalid emails
- **Unit tests**: Added comprehensive test coverage for edge cases
  - Empty email addresses
  - Invalid formats (missing @, invalid domain)
  - Valid email formats
  - Edge cases (trailing spaces, special characters)

## Related Issue

Closes #42

## Verification

- [x] All acceptance criteria met
- [x] Tests pass (15/15 passed)
- [x] Code review completed
- [x] No breaking changes
- [x] RFC 5322 compliance verified via Context7"
```

---

## Example 2: Bug Fix - Login Timeout

**User request:** "Work on issue #15 - login timeout bug"

### Phase 1 — Fetch issue metadata and display for user:

```bash
gh issue view 15 --json title,labels,assignees,state
# Returns: "Login times out after 5 seconds" (label: bug)

gh issue view 15
# Displays full issue for user to read
```

### Phase 2 — Analyze:
User describes the problem:
- JWT token verification times out after 5 seconds
- Should use 30 seconds like other auth operations
- Happens intermittently under load

### Phase 3-6 — Verify, implement, and review:
- Verifies JWT library documentation via Context7
- Traces bug to authentication module timeout configuration
- Finds timeout value in seconds instead of milliseconds
- Fixes timeout configuration
- Adds regression test
- Runs full test suite and linters
- Launches code review sub-agent

### Phase 7 — Commit:

```bash
# Create branch
git checkout -b "fix/15-login-timeout"

# Stage and commit
git add -A
git commit -m "fix(auth): resolve login timeout issue

JWT token verification was using a 5s timeout instead of 30s
due to config value being read in seconds instead of milliseconds.

Fixed timeout unit to milliseconds and added regression test.

Closes #15"

# Push
git push -u origin "fix/15-login-timeout"
```

### Phase 8 — Pull Request:

```bash
gh pr create \
    --base main \
    --title "fix(auth): resolve login timeout issue" \
    --body "## Description

Fixes login timeout caused by incorrect timeout unit in JWT verification configuration.

## Root Cause

The JWT token verification timeout was configured as 5 (seconds) instead of 5000 (milliseconds), causing authentication to timeout prematurely under load.

## Changes

- **Timeout configuration**: Fixed timeout unit from seconds to milliseconds (5s → 5000ms)
- **Consistency**: Aligned with other auth operations (30s timeout)
- **Regression test**: Added test to verify timeout doesn't occur within normal operation window
- **Documentation**: Updated config comments to clarify unit (milliseconds)

## Testing

- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing under load
- [x] Regression test added
- [x] No breaking changes

## Related Issue

Closes #15"
```

---

## Example 3: Refactor - Search Performance

**User request:** "Implement issue #78"

### Phase 1 — Fetch issue metadata and display for user:

```bash
gh issue view 78 --json title,labels
# Returns: "Improve search performance" (label: enhancement)

gh issue view 78
# Displays full issue for user to read
```

### Phase 2 — Clarify:
User describes the goal. Agent identifies gaps and asks via AskUserQuestion:
- "What search functionality should be optimized?"
  - User: "Product search API endpoint"
- "What is the current response time and what's the target?"
  - User: "Currently ~2s, target < 200ms"
- "Should this include database query optimization, caching, or both?"
  - User: "Both - optimize queries and add Redis caching"

### Phase 3+ — Verify and implement:
- Verifies Redis and PostgreSQL best practices via Context7
- Implements database query optimization (indexes, query rewrite)
- Adds Redis caching layer with TTL
- Runs full test suite
- Code review
- Commit and PR

### Phase 7 — Commit:

```bash
# Create branch
git checkout -b "refactor/78-improve-search-performance"

# Stage and commit
git add -A
git commit -m "refactor(search): improve product search performance

Optimized product search API from ~2s to <200ms through database
query optimization and Redis caching.

Database optimization:
- Added composite index on (name, category, price)
- Rewrote query to use index efficiently
- Reduced N+1 query problem

Caching:
- Added Redis cache layer for popular searches
- Implemented cache-aside pattern with 5min TTL
- Added cache invalidation on product updates

Performance:
- Cold cache: ~180ms (from ~2000ms)
- Warm cache: ~20ms
- 91% reduction in average response time

Closes #78"

# Push
git push -u origin "refactor/78-improve-search-performance"
```

### Phase 8 — Pull Request:

```bash
gh pr create \
    --base main \
    --title "refactor(search): improve product search performance" \
    --body "## Description

Optimized product search API endpoint, reducing response time from ~2 seconds to <200ms through database query optimization and Redis caching.

## Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Cold cache | ~2000ms | ~180ms | 91% reduction |
| Warm cache | ~2000ms | ~20ms | 99% reduction |
| Database queries | ~15 | ~3 | 80% reduction |

## Changes

### Database Optimization
- **Composite index**: Added index on (name, category, price) columns
- **Query rewrite**: Optimized query to use index efficiently
- **N+1 elimination**: Reduced multiple queries to single optimized query

### Caching Layer
- **Redis integration**: Implemented cache-aside pattern
- **Cache key**: \`search:{query_hash}\`
- **TTL**: 5 minutes with automatic invalidation on product updates
- **Fallback**: Graceful degradation if Redis unavailable

### Code Quality
- **Abstraction**: Separated cache logic into dedicated service
- **Testability**: Added cache mocking for unit tests
- **Monitoring**: Added cache hit/miss metrics

## Breaking Changes

None - API contract unchanged, only performance improved.

## Related Issue

Closes #78

## Verification

- [x] Performance benchmarks meet targets
- [x] Unit tests pass (including cache tests)
- [x] Integration tests pass
- [x] Load testing confirms improvements
- [x] Code review completed
- [x] Documentation updated"
```

---

## Example 4: Documentation - API Docs Update

**User request:** "Fix issue #103"

### Phase 1-2 — Fetch and analyze:
Issue: "API documentation is outdated for user endpoints"

### Phase 3-6 — Implement:
- Verifies OpenAPI specification via Context7
- Updates API documentation
- Adds missing endpoint descriptions
- Runs linters

### Phase 7 — Commit:

```bash
git checkout -b "docs/103-update-api-docs"

git add -A
git commit -m "docs(api): update user endpoint documentation

- Added missing endpoint descriptions for user APIs
- Updated request/response examples
- Fixed authentication requirements
- Added error response documentation

Closes #103"

git push -u origin "docs/103-update-api-docs"
```

### Phase 8 — Pull Request:

```bash
gh pr create \
    --base main \
    --title "docs(api): update user endpoint documentation" \
    --body "## Description

Updates outdated API documentation for user management endpoints.

## Changes

- Added descriptions for 5 previously undocumented endpoints
- Updated request/response examples to match current implementation
- Fixed authentication requirement descriptions
- Added error response documentation for 4xx and 5xx errors
- Clarified rate limiting behavior

## Related Issue

Closes #103"
```

---

## Conventional Commit Reference

### Commit Message Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add JWT refresh tokens` |
| `fix` | Bug fix | `fix(database): resolve connection leak` |
| `docs` | Documentation | `docs(api): update endpoint examples` |
| `style` | Code style (no logic change) | `style: fix indentation` |
| `refactor` | Code refactoring | `refactor(services): extract base class` |
| `perf` | Performance improvement | `perf(cache): add Redis layer` |
| `test` | Test additions/changes | `test(auth): add token validation tests` |
| `chore` | Maintenance tasks | `chore: update dependencies` |

### Scopes

Common scopes by layer:
- `auth` - Authentication/authorization
- `database` - Database operations
- `api` - API endpoints
- `services` - Business logic
- `controllers` - Request handling
- `models` - Data models
- `utils` - Utility functions
- `config` - Configuration
- `ci` - CI/CD

### Subject Line

- Use imperative mood ("add" not "added" or "adds")
- Keep under 72 characters
- Don't end with period
- Reference issue in body, not subject

**Examples:**
- ✅ `feat(auth): add JWT refresh token support`
- ❌ `feat(auth): Added JWT refresh token support.`
- ❌ `feat(auth): add JWT refresh token support Closes #42`

### Body

- Explain **what** and **why** (not **how**)
- Wrap at 72 characters
- Use bullet points for multiple changes

**Example:**
```
Add JWT refresh token support to improve user experience
by allowing seamless session renewal without re-authentication.

- Implemented refresh token rotation for security
- Added token revocation on logout
- Configurable token expiration times
```

### Footer

- Reference breaking changes
- Reference issue numbers
- Closes format: `Closes #<issue_number>`

**Example:**
```
Closes #42

BREAKING CHANGE: Token endpoint now requires client_id.
```

---

## Branch Naming Reference

### Feature Branches

Format: `feature/<issue-id>-<short-description>`

Examples:
- `feature/42-add-email-validation`
- `feature/78-user-dashboard`
- `feature/156-dark-mode`

### Bug Fix Branches

Format: `fix/<issue-id>-<short-description>`

Examples:
- `fix/15-login-timeout`
- `fix/89-memory-leak`
- `fix/231-null-pointer`

### Refactor Branches

Format: `refactor/<issue-id>-<short-description>`

Examples:
- `refactor/78-improve-search-performance`
- `refactor/201-extract-base-service`
- `refactor/345-clean-architecture`

### Documentation Branches

Format: `docs/<issue-id>-<short-description>`

Examples:
- `docs/103-update-api-docs`
- `docs/250-add-deployment-guide`
- `docs/312-security-checklist`

### Other Branches

| Type | Prefix | Example |
|------|--------|---------|
| Test | `test/` | `test/77-coverage-reports` |
| Chore | `chore/` | `chore/99-update-dependencies` |
| Style | `style/` | `style/55-formatting` |

---

## Pull Request Template

```markdown
## Description
[Clear summary of what changed and why]

## Changes
- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## Breaking Changes
[List any breaking changes or "None"]

## Related Issue
Closes #<ISSUE_NUMBER>

## Verification
- [x] All acceptance criteria met
- [x] Tests pass
- [x] Code review completed
- [x] No breaking changes
- [x] Documentation updated (if applicable)
```

---

## Git Hooks Integration

### Pre-commit Hook

```bash
#!/bin/bash
# Run tests before commit
npm test || {
    echo "Tests failed. Commit aborted."
    exit 1
}

# Run linter
npm run lint || {
    echo "Lint errors found. Commit aborted."
    exit 1
}
```

### Pre-push Hook

```bash
#!/bin/bash
# Run full test suite before push
npm run test:coverage || {
    echo "Coverage below threshold. Push aborted."
    exit 1
}
```
