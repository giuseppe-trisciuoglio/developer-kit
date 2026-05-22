# Bug Fix Specification: ${BUG_TITLE}

**Type**: Bug Fix
**Date**: YYYY-MM-DD
**Status**: Draft
**Severity**: CRITICAL/HIGH/MEDIUM/LOW
**Parent Spec**: [link to parent spec]

### Bug Summary

- **Title**: [Concise bug description]
- **Component**: [Affected component]
- **Severity**: [CRITICAL/HIGH/MEDIUM/LOW]
- **Reported By**: [Reporter/Discovered by]
- **Report Date**: [YYYY-MM-DD]

---

## Current Behavior (Incorrect)

[Detailed description of how the system currently behaves]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step N]

**Expected Behavior**: [How the system SHOULD behave]

---

## Root Cause Analysis

**Location**: [File, class, method]

**Root Cause**: [Why this bug exists]

**Category**:
- [ ] Logic Error
- [ ] Missing Validation
- [ ] Race Condition
- [ ] Type Error
- [ ] Concurrency Issue
- [ ] Edge Case Not Handled
- [ ] Configuration Issue
- [ ] Wrong Assumption

**Code Location**:
```
[File path]:[line numbers]
[Relevant code snippet]
```

**Why It Happened**: [One paragraph explaining the chain of events that caused the bug]

---

## Expected Behavior (After Fix)

[Detailed description of how the system will behave after the fix]

---

## Unchanged Behavior (CRITICAL)

**This section documents what MUST remain the same to prevent regressions.**

The following behaviors MUST NOT change:
- [ ] [Behavior 1 — e.g., "Login page still requires password"]
- [ ] [Behavior 2 — e.g., "API response format unchanged"]
- [ ] [Behavior 3 — e.g., "User session still expires after 30 minutes"]

**Reason**: These behaviors are used by other components and changing them would break integration.

### Functional Invariants

- [ ] [Core behavior that must remain identical]

### API Contracts

- [ ] [Response format, status codes, headers must remain unchanged]

### Data Integrity

- [ ] [Validation rules, constraints, data relationships]

### Integration Points

- [ ] [How it interacts with other systems — must preserve interfaces]

### Performance

- [ ] [Response time, throughput expectations]

---

## Solution Approach

**Implementation Strategy**: [Brief approach]

**Changes Required**:
- [File 1]: [Change description]
- [File 2]: [Change description]

**Test Plan**:
1. Verify bug is fixed (reproduce and confirm)
2. Verify unchanged behaviors are preserved
3. Run regression tests

---

## Acceptance Criteria

- [ ] Bug is fixed (steps to reproduce now work correctly)
- [ ] Unchanged behaviors are preserved (all invariants pass)
- [ ] Regression tests pass
- [ ] No new warnings or errors introduced

---

## Rollback Plan

[How to revert if the fix causes issues]
