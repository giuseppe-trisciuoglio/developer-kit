---
description: Provides comprehensive GitHub pull request review with code quality, security, and best practices analysis. Use when reviewing a PR before merging.
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob
argument-hint: "[pr-number] [review-focus] [output-format]"
---

# GitHub Pull Request Comprehensive Review

Perform comprehensive code review of a GitHub pull request including code quality, security, architecture, performance, and best practices analysis.

## Current Context

- **Current Branch**: !`git branch --show-current`
- **Remote Repository**: !`git config --get remote.origin.url`
- **Git Status**: !`git status --porcelain`

## Configuration

**Arguments received**: `$ARGUMENTS`

**$1**: PR number (required - e.g., `123`)
**$2**: Review focus (optional - defaults to `full`)
**$3**: Output format (optional - defaults to `summary`)

**Available review focuses**:
- `full` - Complete comprehensive review (default)
- `security` - Security vulnerabilities and risks only
- `performance` - Performance bottlenecks and optimizations
- `architecture` - Design patterns and architectural decisions
- `testing` - Test coverage and quality
- `style` - Code style and conventions

**Output formats**:
- `summary` - Concise executive summary (default)
- `detailed` - Comprehensive detailed report
- `checklist` - Review checklist format
- `issues` - GitHub issues-ready format

## Phase 1: PR Information Extraction

### 1.1 Fetch PR Details

```bash
# Validate PR number
if [ -z "$1" ]; then
    echo "Error: PR number is required"
    echo "Usage: /developer-kit:devkit.github.review-pr <pr-number> [review-focus] [output-format]"
    exit 1
fi

PR_NUMBER=$1
REVIEW_FOCUS=${2:-full}
OUTPUT_FORMAT=${3:-summary}

# Check GitHub CLI authentication
if ! gh auth status > /dev/null 2>&1; then
    echo "Error: GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Fetch PR information
echo "Fetching PR #$PR_NUMBER details..."

PR_TITLE=$(gh pr view $PR_NUMBER --json title -q .title)
PR_AUTHOR=$(gh pr view $PR_NUMBER --json author -q .author.login)
PR_STATE=$(gh pr view $PR_NUMBER --json state -q .state)
PR_BASE=$(gh pr view $PR_NUMBER --json baseRefName -q .baseRefName)
PR_HEAD=$(gh pr view $PR_NUMBER --json headRefName -q .headRefName)
PR_URL=$(gh pr view $PR_NUMBER --json url -q .url)
PR_CREATED=$(gh pr view $PR_NUMBER --json createdAt -q .createdAt)
PR_ADDITIONS=$(gh pr view $PR_NUMBER --json additions -q .additions)
PR_DELETIONS=$(gh pr view $PR_NUMBER --json deletions -q .deletions)
PR_CHANGED_FILES=$(gh pr view $PR_NUMBER --json changedFiles -q .changedFiles)

echo "PR Title: $PR_TITLE"
echo "Author: $PR_AUTHOR"
echo "State: $PR_STATE"
echo "Branch: $PR_HEAD -> $PR_BASE"
echo "Changes: +$PR_ADDITIONS -$PR_DELETIONS across $PR_CHANGED_FILES files"
```

### 1.2 Get Changed Files

```bash
# Get list of changed files with their status
gh pr diff $PR_NUMBER --name-only > changed_files.tmp

echo ""
echo "Changed files:"
cat changed_files.tmp
echo ""

# Categorize files by type
JAVA_FILES=$(grep '\.java$' changed_files.tmp | wc -l)
JS_FILES=$(grep -E '\.(js|jsx|ts|tsx)$' changed_files.tmp | wc -l)
PY_FILES=$(grep '\.py$' changed_files.tmp | wc -l)
CONFIG_FILES=$(grep -E '\.(xml|yml|yaml|json|properties)$' changed_files.tmp | wc -l)
TEST_FILES=$(grep -i 'test' changed_files.tmp | wc -l)
DOC_FILES=$(grep -E '\.(md|txt|adoc)$' changed_files.tmp | wc -l)

echo "File types:"
echo "- Java files: $JAVA_FILES"
echo "- JavaScript/TypeScript files: $JS_FILES"
echo "- Python files: $PY_FILES"
echo "- Configuration files: $CONFIG_FILES"
echo "- Test files: $TEST_FILES"
echo "- Documentation files: $DOC_FILES"
```

### 1.3 Fetch PR Diff

```bash
# Download full diff
gh pr diff $PR_NUMBER > pr_diff.tmp

# Get diff statistics
TOTAL_LINES=$(wc -l < pr_diff.tmp)
ADDED_LINES=$(grep '^+' pr_diff.tmp | grep -v '^+++' | wc -l)
REMOVED_LINES=$(grep '^-' pr_diff.tmp | grep -v '^---' | wc -l)

echo ""
echo "Diff statistics:"
echo "- Total lines in diff: $TOTAL_LINES"
echo "- Lines added: $ADDED_LINES"
echo "- Lines removed: $REMOVED_LINES"
echo ""
```

## Phase 2: Code Quality Analysis

### 2.1 Code Structure and Organization

Analyze:
- **Package/module structure**: Logical organization and naming
- **File organization**: Single responsibility principle adherence
- **Class/function size**: Manageable and focused components
- **Naming conventions**: Consistency and clarity
- **Code duplication**: DRY principle violations

### 2.2 Design Patterns and Best Practices

Review for:
- **Design patterns**: Appropriate pattern usage
- **SOLID principles**: Single responsibility, open/closed, etc.
- **Dependency management**: Proper injection and coupling
- **Error handling**: Comprehensive exception handling
- **Logging**: Appropriate logging levels and messages

### 2.3 Code Complexity

Evaluate:
- **Cyclomatic complexity**: Number of decision points
- **Cognitive complexity**: Mental effort to understand
- **Nesting depth**: Excessive nesting levels
- **Method/function length**: Overly long implementations
- **Parameter count**: Excessive parameters

## Phase 3: Security Review

### 3.1 Common Vulnerabilities

Check for:
- **SQL Injection**: Unsafe query construction
- **XSS (Cross-Site Scripting)**: Unescaped user input
- **CSRF**: Missing CSRF protection
- **Authentication/Authorization**: Insecure access controls
- **Sensitive Data Exposure**: Hardcoded secrets, logging sensitive data
- **Insecure Dependencies**: Known vulnerable libraries

### 3.2 Security Best Practices

Verify:
- **Input validation**: Proper sanitization and validation
- **Output encoding**: Preventing injection attacks
- **Cryptography**: Strong algorithms and key management
- **Session management**: Secure session handling
- **Error messages**: No sensitive information leakage
- **HTTPS usage**: Secure communication enforcement

### 3.3 Secrets Detection

```bash
# Check for potential secrets in diff
echo "Scanning for potential secrets..."

# Common secret patterns
grep -iE '(password|secret|api_key|access_key|private_key|token)\s*[:=]' pr_diff.tmp > secrets.tmp || true

if [ -s secrets.tmp ]; then
    echo "WARNING: Potential secrets found:"
    cat secrets.tmp
else
    echo "No obvious secrets detected"
fi
```

## Phase 4: Performance Analysis

### 4.1 Performance Concerns

Identify:
- **N+1 queries**: Database query inefficiencies
- **Memory leaks**: Unclosed resources, retained references
- **Inefficient algorithms**: O(n²) or worse complexity
- **Unnecessary computations**: Redundant calculations
- **Large data structures**: Excessive memory usage
- **Blocking operations**: Synchronous calls in async contexts

### 4.2 Optimization Opportunities

Look for:
- **Caching opportunities**: Repeated expensive operations
- **Lazy loading**: Deferred resource loading
- **Batch operations**: Combining multiple operations
- **Index usage**: Database query optimization
- **Resource pooling**: Connection and thread pools
- **Async processing**: Non-blocking operations

## Phase 5: Testing Review

### 5.1 Test Coverage Analysis

```bash
# Check for test files in PR
echo ""
echo "Test file analysis:"

TEST_FILES_IN_PR=$(grep -i 'test' changed_files.tmp | wc -l)
SRC_FILES_IN_PR=$(grep -v -i 'test' changed_files.tmp | wc -l)

TEST_RATIO=$(echo "scale=2; $TEST_FILES_IN_PR / $SRC_FILES_IN_PR" | bc 2>/dev/null || echo "N/A")

echo "- Test files: $TEST_FILES_IN_PR"
echo "- Source files: $SRC_FILES_IN_PR"
echo "- Test ratio: $TEST_RATIO"
```

### 5.2 Test Quality Assessment

Evaluate:
- **Test completeness**: Edge cases and boundary conditions
- **Test independence**: Tests don't depend on each other
- **Test clarity**: Clear test names and assertions
- **Mocking strategy**: Appropriate use of mocks/stubs
- **Integration tests**: Critical paths covered
- **Test data**: Realistic and varied test scenarios

## Phase 6: Architecture Review

### 6.1 Architectural Patterns

Assess:
- **Layered architecture**: Proper separation of concerns
- **Dependency direction**: Dependencies flow correctly
- **Module boundaries**: Clear module responsibilities
- **API design**: RESTful principles, consistent endpoints
- **Data flow**: Clean data transformation pipeline
- **State management**: Proper state handling

### 6.2 Scalability and Maintainability

Consider:
- **Horizontal scalability**: Stateless design
- **Configuration management**: Externalized configuration
- **Feature flags**: Gradual rollout capability
- **Backward compatibility**: Breaking changes identification
- **Technical debt**: Accumulation vs resolution
- **Documentation**: Code comments and API docs

## Phase 7: Code Style and Conventions

### 7.1 Style Consistency

Check:
- **Formatting**: Consistent indentation and spacing
- **Naming conventions**: Consistent naming patterns
- **Import organization**: Organized and minimal imports
- **Comment quality**: Meaningful comments, no dead code
- **File structure**: Consistent file organization

### 7.2 Language-Specific Conventions

#### Java/Spring Boot
- Constructor injection over field injection
- Java records for DTOs (Java 16+)
- Proper use of Optional
- Stream API usage
- Exception handling patterns

#### JavaScript/TypeScript
- Modern ES6+ syntax
- Async/await over callbacks
- Type safety (TypeScript)
- Immutability patterns
- Error boundaries

#### Python
- PEP 8 compliance
- Type hints usage
- Context managers
- List comprehensions
- Pythonic idioms

## Phase 8: Review Summary and Recommendations

### 8.1 Critical Issues (Blockers)

Issues that must be fixed before merge:
- Security vulnerabilities
- Breaking changes without migration path
- Data loss or corruption risks
- Critical performance issues
- Test failures

### 8.2 Major Issues (High Priority)

Issues that should be addressed:
- Significant code quality problems
- Missing essential tests
- Performance bottlenecks
- Architectural violations
- Incomplete error handling

### 8.3 Minor Issues (Medium Priority)

Issues to consider:
- Code style inconsistencies
- Minor optimization opportunities
- Documentation gaps
- Refactoring suggestions
- Test coverage improvements

### 8.4 Suggestions (Low Priority)

Nice-to-have improvements:
- Alternative implementation approaches
- Additional test scenarios
- Code simplification opportunities
- Documentation enhancements
- Future refactoring considerations

## Phase 9: Generate Review Report

### 9.1 Summary Format

```markdown
# Pull Request Review: #$PR_NUMBER

## Overview
- **Title**: $PR_TITLE
- **Author**: $PR_AUTHOR
- **Branch**: $PR_HEAD → $PR_BASE
- **Changes**: +$PR_ADDITIONS -$PR_DELETIONS across $PR_CHANGED_FILES files
- **Review Focus**: $REVIEW_FOCUS

## Summary
[High-level assessment of the PR]

## Findings

### Critical Issues (Must Fix)
- Issue 1: Description and location
- Issue 2: Description and location

### Major Issues (Should Fix)
- Issue 1: Description and location
- Issue 2: Description and location

### Minor Issues (Consider Fixing)
- Issue 1: Description and suggestion
- Issue 2: Description and suggestion

### Suggestions
- Suggestion 1: Enhancement idea
- Suggestion 2: Alternative approach

## Code Quality Metrics
- Test Coverage: [Percentage or assessment]
- Code Complexity: [Assessment]
- Security: [Assessment]
- Performance: [Assessment]

## Recommendation
[APPROVE | REQUEST CHANGES | COMMENT]

## Next Steps
1. Address critical issues
2. Consider major issues
3. Respond to questions and suggestions
```

### 9.2 Detailed Format

Comprehensive report with:
- File-by-file review
- Line-by-line comments where applicable
- Code snippets with suggestions
- Before/after examples
- References to best practices
- Links to relevant documentation

### 9.3 Checklist Format

```markdown
## Code Review Checklist

### Functionality
- [ ] Changes implement the intended feature
- [ ] Edge cases are handled
- [ ] Error scenarios are covered
- [ ] Business logic is correct

### Code Quality
- [ ] Code is readable and maintainable
- [ ] Naming is clear and consistent
- [ ] No code duplication
- [ ] Proper abstraction levels

### Security
- [ ] No security vulnerabilities introduced
- [ ] Input validation is present
- [ ] Authentication/authorization is correct
- [ ] No secrets in code

### Performance
- [ ] No obvious performance issues
- [ ] Efficient algorithms used
- [ ] Resources are properly managed
- [ ] Database queries are optimized

### Testing
- [ ] Unit tests are present
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests are meaningful

### Documentation
- [ ] Code is self-documenting or commented
- [ ] API documentation is updated
- [ ] README is updated if needed
- [ ] Breaking changes are documented
```

## Phase 10: Submit Review

### 10.1 Post Review Comment

```bash
# Generate review summary
REVIEW_SUMMARY="# PR Review Summary

**Review Focus**: $REVIEW_FOCUS
**Date**: $(date +%Y-%m-%d)

## Assessment
[Your assessment here]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Recommendation
[Your recommendation]
"

# Post review comment
gh pr comment $PR_NUMBER --body "$REVIEW_SUMMARY"

echo ""
echo "Review comment posted to PR #$PR_NUMBER"
```

### 10.2 Optional: Request Changes

```bash
# If critical issues found
# gh pr review $PR_NUMBER --request-changes --body "Critical issues found that must be addressed before merge"

# If approved
# gh pr review $PR_NUMBER --approve --body "LGTM! Great work on this PR."

# If just commenting
# gh pr review $PR_NUMBER --comment --body "Review completed. See comments for details."
```

## Best Practices for PR Reviews

### Constructive Feedback

**Good examples**:
- "Consider using a repository pattern here for better testability"
- "This method could be simplified using Java Streams API"
- "Missing null check on line 45 could cause NPE"
- "Great use of design patterns! One suggestion: consider extracting this to a separate class"

**Bad examples**:
- "This is wrong"
- "Why did you do it this way?"
- "I would have done it differently"
- "This code is messy"

### Review Etiquette

1. **Be specific**: Reference exact files and line numbers
2. **Be constructive**: Offer solutions, not just problems
3. **Be respectful**: Professional and courteous tone
4. **Be timely**: Review within 24-48 hours
5. **Be thorough**: Don't rush through the review
6. **Ask questions**: When unclear, ask for clarification
7. **Acknowledge good work**: Praise well-done implementations

### Review Priorities

1. **Correctness**: Does the code work as intended?
2. **Security**: Are there security vulnerabilities?
3. **Performance**: Are there performance issues?
4. **Maintainability**: Is the code maintainable?
5. **Testing**: Is there adequate test coverage?
6. **Style**: Does it follow project conventions?

## Cleanup

```bash
# Remove temporary files
rm -f changed_files.tmp pr_diff.tmp secrets.tmp

echo ""
echo "Review completed for PR #$PR_NUMBER"
echo "View PR: $PR_URL"
```

## Examples

### Example 1: Full Review

```bash
# Comprehensive review of PR #123
/developer-kit:devkit.github.review-pr 123
```

### Example 2: Security-Focused Review

```bash
# Security-only review of PR #456
/developer-kit:devkit.github.review-pr 456 security
```

### Example 3: Detailed Report

```bash
# Detailed review report for PR #789
/developer-kit:devkit.github.review-pr 789 full detailed
```

### Example 4: Performance Review with Checklist

```bash
# Performance review in checklist format
/developer-kit:devkit.github.review-pr 321 performance checklist
```

## Integration with CI/CD

The review can be enhanced by checking:
- CI/CD pipeline status
- Test coverage reports
- Code quality metrics (SonarQube)
- Security scan results (Snyk, OWASP)
- Build artifacts and logs

## Your Task

Based on the provided PR number and review focus:

1. Extract PR information and changed files
2. Analyze code quality and structure
3. Review for security vulnerabilities
4. Assess performance implications
5. Evaluate test coverage and quality
6. Check architectural decisions
7. Verify code style and conventions
8. Generate comprehensive review report
9. Provide actionable recommendations
10. Post review comments to GitHub

**Remember**: Be thorough, constructive, and professional. Focus on helping the author improve their code while maintaining high quality standards.

## Execution Instructions

**Agent Selection**: To execute this GitHub task, use the following approach:
- Primary: Use `general-purpose` agent with GitHub CLI expertise and code analysis capabilities

## Usage

```
/devkit.github.review-pr $ARGUMENTS
```

## Arguments

| Argument | Description |
|----------|-------------|
| `$ARGUMENTS` | Combined arguments passed to the command |
