# Task Review Report: ${TASK_ID}

**Task**: ${TASK_ID} — ${TASK_TITLE}
**Spec**: ${SPEC_PATH}
**Reviewed**: ${REVIEW_DATE}
**Reviewer**: AI Code Reviewer
**Review Status**: ${REVIEW_STATUS}

> **Status Legend**:
> - `passed` ✅ — All ACs and DoD met, no critical issues, no architectural drift
> - `needs_fix` ⚠️ — Minor issues in ACs, DoD, or code quality
> - `partial` 🔶 — Some ACs met, major functionality missing or incorrect
> - `escalate` 🚨 — Critical architectural drift, spec contradiction, or impossible requirement

---

## Review Summary

| Aspect | Status | Details |
|--------|--------|---------|
| Acceptance Criteria | ✅/⚠️/🔶/🚨 | [N/M met] |
| Definition of Done | ✅/⚠️/🔶/🚨 | [N/M met] |
| Code Quality | ✅/⚠️/🔶/🚨 | [summary] |
| Spec Compliance | ✅/⚠️/🔶/🚨 | [summary] |
| Architectural Alignment | ✅/⚠️/🔶/🚨 | [summary] |

**Overall Status**: **${REVIEW_STATUS}**

---

## Acceptance Criteria & DoD Results

### Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC-1 | ${CRITERION_TEXT} | ✅ Met / ❌ Not Met / ⚠️ Partial | [file:line or test name] |
| AC-2 | ${CRITERION_TEXT} | ✅ Met / ❌ Not Met / ⚠️ Partial | [file:line or test name] |

### Definition of Done

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | ${DOD_ITEM} | ✅ Met / ❌ Not Met | [evidence] |
| 2 | ${DOD_ITEM} | ✅ Met / ❌ Not Met | [evidence] |

### Definition of Ready (validated post-implementation)

- [x] / [ ] Dependencies were completed before starting
- [x] / [ ] Technical context was understood
- [x] / [ ] Files were identified and accessible
- [x] / [ ] Tooling was available

---

## Code Review Findings

| # | Severity | File | Line(s) | Category | Description | Recommendation |
|---|----------|------|---------|----------|-------------|----------------|
| 1 | 🔴 Critical / 🟡 Warning / 🔵 Info | `${FILE_PATH}` | L${LINE} | Security / Performance / Maintainability / Convention | ${DESCRIPTION} | ${RECOMMENDATION} |
| 2 | ... | | | | | |

<!-- If no findings, state: "No code review findings." -->

---

## Spec Compliance & Architectural Alignment

### Spec Fidelity Check

| AC-ID | Taxonomy | Task Claims | Implementation Matches | Notes |
|-------|----------|-------------|----------------------|-------|
| ${AC_ID} | [IMP]/[SEF]/[EXT] | Yes/No | ✅/❌/⚠️ | ${NOTE} |

### Cross-Boundary Adherence

| File | Expected Context | Actual Context | Status |
|------|-----------------|---------------|--------|
| `${FILE_PATH}` | ${EXPECTED_CONTEXT} | ${ACTUAL_CONTEXT} | ✅ OK / ⚠️ Warning / 🚨 Blocking |

<!-- If no cross-boundary issues, state: "All changes within expected bounded context." -->

### Decision Log Check

| DEC-ID | Relevant to Task | Honored in Implementation |
|--------|-----------------|--------------------------|
| ${DEC_ID} | Yes/No | ✅ Yes / ❌ No |

<!-- If no DEC entries, state: "No decision-log entries relevant to this task." -->

### Traceability Matrix Update

- [ ] Test Files column updated in `traceability-matrix.md`
- [ ] Code Files column updated in `traceability-matrix.md`
- [ ] Status updated to "Implemented" for covered REQ-IDs

---

## Required Fixes

> If review status is `passed`, state: "No required fixes."

### Critical (must fix before proceeding)

| # | Issue | File | Action Required |
|---|-------|------|-----------------|
| 1 | ${CRITICAL_ISSUE} | `${FILE_PATH}` | ${ACTION} |

### Warnings (should fix)

| # | Issue | File | Action Required |
|---|-------|------|-----------------|
| 1 | ${WARNING_ISSUE} | `${FILE_PATH}` | ${ACTION} |

### Suggestions (optional improvements)

| # | Suggestion | File | Notes |
|---|-----------|------|-------|
| 1 | ${SUGGESTION} | `${FILE_PATH}` | ${NOTES} |

---

## Next Steps

| If Status | Action |
|-----------|--------|
| `passed` | Run Phase T-7 cleanup in `task-implementation`, then proceed to next task |
| `needs_fix` | Fix required items, then re-run `/developer-kit-specs:specs.task-review --task="${TASK_PATH}"` |
| `partial` | Re-implement missing functionality, then re-run task-implementation and task-review |
| `escalate` | Discuss with user — may require spec update or ADR before proceeding |

**Implementation Command** (for re-review after fixes):
```bash
/developer-kit-specs:specs.task-review --lang=${LANG} --task="${TASK_PATH}"
```

**Cleanup Command** (if passed):
```bash
/developer-kit-specs:specs.task-implementation --lang=${LANG} --task="${TASK_PATH}"
```
