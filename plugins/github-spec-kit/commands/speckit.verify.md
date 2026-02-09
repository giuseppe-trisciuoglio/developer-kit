---
description: Validates implementation completion by checking tasks, logic, tests, and code quality against specifications. Use when you need to verify that all tasks are properly completed.
argument-hint: "[optional-focus-area]"
allowed-tools: Read, Glob, Grep, Bash
---

# Verify Feature Implementation - Comprehensive Validation

## Overview

Validates implementation completion by checking tasks, logic, tests, and code quality against specifications. Use when
you need to verify that all tasks are properly completed.

## Usage

```
/speckit.verify $ARGUMENTS
```

## Arguments

| Argument     | Description                              |
|--------------|------------------------------------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Execution Steps

## Execution Instructions

**Agent Selection**: To execute this task, use the following approach:

- Primary: Use `general-purpose` agent with appropriate domain expertise
- Or use specialized agent if available for the specific task type

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Perform comprehensive verification of the implemented feature against specifications, ensuring all
requirements are met, tests pass, and code quality standards are satisfied. This command runs AFTER `/speckit.implement`
completes.

**Critical Principle**: This is a READ-ONLY analysis command. The ONLY file that may be written is
`verification-report.md` in the feature directory. No other modifications are permitted.

### 1. Setup & Prerequisites

Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse JSON
for:

- FEATURE_DIR (absolute path)
- AVAILABLE_DOCS list
- Repository root

For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm
Groot").

Abort if implementation appears incomplete with guidance to run `/speckit.implement` first.

### 2. Load Verification Context

**Load artifacts in order** (progressive, on-demand):

**Required**:

- tasks.md: Verify all tasks marked completed [X]
- spec.md: Requirements, user stories, acceptance criteria
- plan.md: Tech stack, architecture, file structure

**Optional** (load if present):

- data-model.md: Entity definitions and relationships
- contracts/: API specifications
- research.md: Technical decisions and constraints
- quickstart.md: Integration scenarios
- checklists/: Quality validation items

**Codebase**:

- Implementation files referenced in tasks.md
- Test files (unit, integration, e2e)
- Configuration files
- Documentation updates

### 3. Task Completion Verification

**Check tasks.md**:

For each task in tasks.md:

- [ ] Task is marked [X] or [x] (completed)
- [ ] No tasks remain with [ ] (incomplete)
- [ ] All file paths mentioned exist in codebase
- [ ] Implementation addresses task description

**Output**:

```
TASK COMPLETION STATUS
Total tasks: X
Completed: X [X%]
Incomplete: X [X%]
Status: [PASS/FAIL]
```

**If incomplete tasks found**:

```
INCOMPLETE TASKS:
- [Task ID]: [Description] → [Reason not completed]
```

Verification FAILS if any task incomplete unless justified (explicitly marked as deferred/optional in tasks.md).

### 4. Requirements Coverage Analysis

**Map implementation to specification**:

For each requirement in spec.md:

#### A. Functional Requirements

- [ ] Implementation code exists
- [ ] Code logic matches requirement description
- [ ] All acceptance criteria satisfied
- [ ] Edge cases handled

#### B. Non-Functional Requirements

- [ ] Performance targets met (if specified)
- [ ] Security measures implemented
- [ ] Accessibility requirements satisfied
- [ ] Scalability considerations addressed

#### C. User Stories

- [ ] All user actions supported
- [ ] Success criteria demonstrable
- [ ] Error scenarios handled gracefully

**Output format**:

```
REQUIREMENT: [ID or description]
Status: [COVERED/PARTIAL/MISSING]
Implementation: [File paths]
Evidence: [Specific code references]
Acceptance Criteria Met: X/Y
Issues: [If any]
```

### 5. Architecture & Design Compliance

**Verify against plan.md**:

#### A. Tech Stack Compliance

- [ ] All specified libraries/frameworks used correctly
- [ ] No unauthorized dependencies introduced
- [ ] Version constraints respected

#### B. Project Structure

- [ ] Files in expected locations per plan.md
- [ ] Directory structure follows specification
- [ ] Naming conventions consistent

#### C. Architectural Patterns

- [ ] Separation of concerns maintained
- [ ] Design patterns correctly applied
- [ ] Component boundaries respected
- [ ] Integration points match contracts

**Output**:

```
ARCHITECTURE COMPLIANCE
Tech Stack: [COMPLIANT/VIOLATIONS]
- [Package]: [Expected version] → [Actual version] [Status]

Structure: [COMPLIANT/VIOLATIONS]
- [Expected pattern] → [Actual implementation] [Status]

Design Patterns: [COMPLIANT/VIOLATIONS]
- [Pattern]: [Assessment]
```

### 6. Data Model Validation

**If data-model.md exists**:

For each entity:

- [ ] Entity class/model exists
- [ ] All fields present with correct types
- [ ] Relationships implemented correctly
- [ ] Validations in place
- [ ] State transitions (if any) handled

**Check**:

- Foreign key constraints
- Cascade behaviors
- Index definitions
- Migration files (if applicable)

**Output**:

```
DATA MODEL VERIFICATION
Entity: [Name]
- Fields: [X/Y present, types correct]
- Relationships: [X/Y implemented]
- Validations: [List]
- Status: [PASS/FAIL]
```

### 7. Contract Compliance

**If contracts/ exists**:

For each contract file:

#### A. API Endpoints

- [ ] Route/path matches contract
- [ ] HTTP methods correct
- [ ] Request schema validation implemented
- [ ] Response schema matches contract
- [ ] Status codes per specification

#### B. Error Handling

- [ ] All error cases from contract covered
- [ ] Error response format matches contract
- [ ] Appropriate HTTP status codes used

#### C. Business Logic

- [ ] Implements contract behavior precisely
- [ ] Edge cases from contract handled
- [ ] Validation rules enforced

**Output**:

```
CONTRACT: [Filename]
Endpoint: [Method] [Path]
- Route: [MATCH/MISMATCH]
- Request Schema: [VALID/INVALID]
- Response Schema: [VALID/INVALID]
- Error Handling: [COMPLETE/INCOMPLETE]
- Logic Compliance: [PASS/FAIL]
Status: [PASS/FAIL]
```

### 8. Test Execution & Coverage

**Run test suites**:

#### A. Execute Tests

```bash
# Run all test commands from plan.md or infer from project type
npm test              # or pytest, cargo test, etc.
npm run test:coverage # or equivalent
```

#### B. Analyze Results

- [ ] All tests pass (100% success rate)
- [ ] No skipped tests (unless explicitly documented)
- [ ] No test warnings or errors
- [ ] Coverage meets threshold (from plan.md or ≥90% default)

#### C. Test Quality

- [ ] Tests cover positive scenarios
- [ ] Tests cover negative/error scenarios
- [ ] Tests cover edge cases and boundaries
- [ ] Tests validate business logic
- [ ] Integration tests verify component interactions
- [ ] E2E tests (if specified) validate user flows

**Output**:

```
TEST EXECUTION RESULTS
Total Tests: X
Passed: X [100%/less]
Failed: X
Skipped: X
Duration: Xs

COVERAGE METRICS
Lines: X%
Branches: X%
Functions: X%
Statements: X%
Threshold: Y% [MET/NOT MET]

TEST QUALITY
Positive Scenarios: [COVERED/GAPS]
Negative Scenarios: [COVERED/GAPS]
Edge Cases: [COVERED/GAPS]
Integration: [COVERED/GAPS]
```

**If tests fail**:

```
FAILED TESTS:
[Test suite] → [Test name]
Error: [Message]
File: [Path:Line]
Expected: [Value]
Actual: [Value]
```

### 9. Code Quality Assessment

**Static Analysis**:

#### A. Linting

Run project linter (ESLint, Pylint, Clippy, etc.):

- [ ] Zero errors
- [ ] Zero warnings (or all justified)
- [ ] Style guide compliance

#### B. Type Checking

If TypeScript/typed language:

- [ ] No type errors
- [ ] Strict mode compliance
- [ ] No 'any' types (unless justified)

#### C. Formatting

- [ ] Code formatted consistently
- [ ] Follows project style guide
- [ ] No formatting inconsistencies

**Output**:

```
CODE QUALITY SCAN
Linter: [Tool name]
- Errors: X
- Warnings: X
- Status: [PASS/FAIL]

Type Checker:
- Errors: X
- Status: [PASS/FAIL]

Formatter:
- Violations: X
- Status: [PASS/FAIL]
```

### 10. Security & Performance Audit

**Security Checks**:

- [ ] No hardcoded secrets/credentials
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection (if web app)
- [ ] Authentication/authorization correct
- [ ] Dependency vulnerabilities scan

**Performance Checks**:

- [ ] No obvious performance anti-patterns
- [ ] Database queries optimized (indexes, N+1 prevention)
- [ ] No memory leaks
- [ ] Resource cleanup (connections, files)
- [ ] Efficient algorithms (no O(n²) where O(n) possible)

**Output**:

```
SECURITY AUDIT
- Hardcoded Secrets: [NONE/FOUND]
- Input Validation: [COMPLETE/GAPS]
- Injection Prevention: [PROTECTED/VULNERABLE]
- Auth/Authz: [CORRECT/ISSUES]
- Dependencies: [SECURE/VULNERABILITIES]
Status: [PASS/FAIL]

PERFORMANCE AUDIT
- Algorithm Efficiency: [OPTIMAL/CONCERNS]
- Database Queries: [OPTIMIZED/ISSUES]
- Resource Management: [PROPER/LEAKS]
Status: [PASS/FAIL]
```

### 11. Documentation Verification

**Check documentation quality**:

- [ ] README updated with new feature (if significant)
- [ ] API documentation matches implementation
- [ ] Complex code has inline comments
- [ ] Public APIs have docstrings/JSDoc
- [ ] quickstart.md reflects current state (if exists)
- [ ] Migration guides (if breaking changes)

**Output**:

```
DOCUMENTATION REVIEW
README: [UPDATED/OUTDATED/N/A]
API Docs: [ACCURATE/OUTDATED/MISSING]
Code Comments: [ADEQUATE/SPARSE]
Public APIs: [DOCUMENTED/UNDOCUMENTED]
Status: [PASS/FAIL]
```

### 12. Constitution Compliance

**If .specify/memory/constitution.md exists**:

Check implementation against project principles:

- [ ] Follows mandated practices
- [ ] Respects constraints
- [ ] Adheres to quality standards
- [ ] Meets governance requirements

**Output**:

```
CONSTITUTION COMPLIANCE
Principle: [Name]
- Status: [COMPLIANT/VIOLATION]
- Evidence: [Description]

Overall: [COMPLIANT/VIOLATIONS]
```

### 13. Checklist Validation

**If FEATURE_DIR/checklists/ exists**:

For each checklist file:

- Count total items
- Count completed [X] or [x] items
- Count incomplete [ ] items
- Calculate completion percentage

**Output**:

```
CHECKLIST STATUS
| Checklist | Total | Completed | Incomplete | %    | Status |
|-----------|-------|-----------|------------|------|--------|
| ux.md     | 12    | 12        | 0          | 100% | ✓ PASS |
| api.md    | 15    | 14        | 1          | 93%  | ✗ FAIL |

Overall: [PASS if all 100% / FAIL if any incomplete]
```

### 14. Generate Verification Report

Create structured report at `FEATURE_DIR/verification-report.md`:

```markdown
# Feature Verification Report

**Feature**: [Name from spec.md]
**Verification Date**: [ISO date]
**Verification Status**: [PASS/FAIL]

---

## Executive Summary

[Overall pass/fail with key metrics]

**Quick Stats**:

- Tasks Completed: X/Y (Z%)
- Requirements Covered: X/Y (Z%)
- Tests Passed: X/Y (Z%)
- Code Quality: [PASS/FAIL]
- Overall Status: [PASS/FAIL]

---

## Task Completion

[Results from step 3]

---

## Requirements Coverage

[Results from step 4]

**Coverage Summary**:

- Functional Requirements: X/Y covered
- Non-Functional Requirements: X/Y covered
- User Stories: X/Y implemented
- Acceptance Criteria: X/Y met

---

## Architecture Compliance

[Results from step 5]

---

## Data Model Validation

[Results from step 6 if applicable]

---

## Contract Compliance

[Results from step 7 if applicable]

---

## Test Results

[Results from step 8]

---

## Code Quality

[Results from step 9]

---

## Security & Performance

[Results from step 10]

---

## Documentation

[Results from step 11]

---

## Constitution Compliance

[Results from step 12 if applicable]

---

## Checklist Status

[Results from step 13 if applicable]

---

## Issues Found

[If FAIL, list all issues with severity]

### Critical Issues

[Must fix before merge]

### High Priority

[Should fix before merge]

### Medium Priority

[Can fix post-merge if needed]

### Low Priority

[Optional improvements]

---

## Remediation Steps

[If FAIL, provide specific actions]

1. **[Issue category]**:
    - File: [Path]
    - Problem: [Description]
    - Fix: [Specific steps]
    - Verification: [How to confirm fixed]

---

## Sign-Off

- [ ] All critical issues resolved
- [ ] All high priority issues resolved
- [ ] Tests pass at 100%
- [ ] Code quality meets standards
- [ ] Documentation updated
- [ ] Ready for review/merge

---

## Next Steps

[If PASS]: Feature ready for [code review/staging/production]
[If FAIL]: Fix issues listed above and re-run `/speckit.verify`

---

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Task Completion | 100% | X% | [✓/✗] |
| Requirements Coverage | 100% | X% | [✓/✗] |
| Test Pass Rate | 100% | X% | [✓/✗] |
| Test Coverage | ≥90% | X% | [✓/✗] |
| Code Quality | 0 errors | X errors | [✓/✗] |
| Security Issues | 0 | X | [✓/✗] |
```

### 15. Output to User

**If PASS**:

```
✅ VERIFICATION PASSED

Feature implementation successfully verified!

Summary:
- All tasks completed
- All requirements covered
- All tests passing (X% coverage)
- Code quality standards met
- No security issues found

Report: [path to verification-report.md]

Suggested commit message:
feat: complete [feature name] implementation

Next steps:
- Create pull request for review
- Deploy to staging environment
- Update project documentation
```

**If FAIL**:

```
❌ VERIFICATION FAILED

Implementation has issues requiring attention.

Critical Issues: X
High Priority: X
Medium Priority: X

Top Issues:
1. [Issue summary]
2. [Issue summary]
3. [Issue summary]

Full details: [path to verification-report.md]

Next steps:
1. Review verification report
2. Fix critical and high priority issues
3. Re-run `/speckit.verify`

Do NOT proceed to merge until verification passes.
```

## Verification Principles

### Strictness Levels

**CRITICAL** (Must Pass):

- All tasks completed
- All requirements covered
- All tests passing
- No security vulnerabilities
- No contract violations

**HIGH** (Should Pass):

- Code quality standards
- Documentation completeness
- Performance optimization
- Constitution compliance

**MEDIUM** (Nice to Pass):

- Code comments
- Optimization opportunities
- Style improvements

**LOW** (Optional):

- Minor refactoring suggestions
- Additional test scenarios

### Pass/Fail Criteria

**PASS** requires:

- 100% task completion (or justified deferrals)
- 100% requirements covered
- 100% test pass rate
- ≥90% test coverage (or plan.md threshold)
- 0 critical security issues
- 0 linting errors (warnings acceptable if justified)
- Contract compliance (if applicable)
- Architecture compliance

**FAIL** if any:

- Incomplete tasks without justification
- Uncovered requirements
- Failing tests
- Coverage below threshold
- Critical security issues
- Linting errors
- Contract violations
- Architecture violations

### Evidence Requirements

**Every finding must include**:

- Specific file path and line numbers
- Concrete evidence (code snippets, test output)
- Expected vs actual comparison
- Remediation guidance

**No speculation allowed**:

- Don't assume code exists if not found
- Don't guess at intent
- Don't hallucinate test results
- Quote actual output/errors

### Token Efficiency

**Progressive analysis**:

- Load files on-demand
- Analyze in phases
- Stop on critical failures (optional)
- Summarize verbose output

**Compact reporting**:

- Use tables for metrics
- Group similar issues
- Link to full details
- Prioritize actionable items

## Context

$ARGUMENTS

## Notes

- This command is READ-ONLY except for writing `verification-report.md`
- Verification should be deterministic (same code → same result)
- Re-run after fixes until PASS achieved
- Can be run multiple times safely
- Integrates with CI/CD pipelines
- Provides audit trail of verification

---

## Examples

```bash
/speckit.verify example-input
```
