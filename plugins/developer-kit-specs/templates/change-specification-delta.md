# Change Specification: ${CHANGE_TITLE}

**Type**: Delta
**Date**: YYYY-MM-DD
**Status**: Draft
**Parent Spec**: [link to parent spec]

### Summary

[Brief description of why this change is needed]

### Change Summary

| Classification | Count |
|---------------|-------|
| ADDED | N |
| MODIFIED | N |
| REMOVED | N |

---

## ADDED

### ${Feature/Requirement Name}

**Description**: [What is being added]

**Requirements**:
- REQ-CHG-001: [EARS formatted requirement]
- REQ-CHG-002: [EARS formatted requirement]

**Acceptance Criteria**:
- [ ] [AC-001]
- [ ] [AC-002]

**Impact**: [What other components are affected]

---

## MODIFIED

### ${Component/Feature Name}

**Previous Behavior**: [Old implementation description]

**New Behavior**: [New implementation description]

**Requirements**:
- REQ-CHG-003: [EARS formatted requirement]

**Acceptance Criteria**:
- [ ] [AC-003]

**Impact**:
- Affected: [list components]
- Breaking: [YES/NO — if YES, detail migration path]

---

## REMOVED

### ${Feature/Component Name}

**Reason**: [Why this is being removed]

**Migration Path**: [How to transition away from this]

**Cutover Date**: [When this will be fully removed]

**Impact**: [What breaks]

---

## Affected Components

| Component | Change Type | Risk |
|-----------|-------------|------|
| [Component] | ADDED/MODIFIED/REMOVED | HIGH/MEDIUM/LOW |

## Testing Strategy

- Unit tests for new functionality
- Regression tests for modified functionality
- Cleanup tests for removed functionality

## Rollback Plan

[How to revert if needed]

---

<!-- Template: bug-fix-specification.md — use for type=bugfix instead -->
