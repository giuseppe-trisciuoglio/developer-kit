# Functional Specification: ${SPEC_TITLE}

**Spec ID**: ${SPEC_ID}
**Date**: ${SPEC_DATE}
**Status**: Draft
**Version**: 1.0

---

## Business Context

### Problem Statement

[What problem does this feature solve? What is the pain point or opportunity?]

### Target Users

| User Type | Description | Primary Goal |
|-----------|-------------|--------------|
| [e.g., End User] | [e.g., Customer using the web app] | [e.g., Complete a purchase quickly] |
| [e.g., Admin] | [e.g., Internal operator] | [e.g., Manage product catalog] |

### System Fit

[How does this feature fit into the overall system purpose? What is its role in the broader product?]

---

## Functional Requirements

### ${Requirement Group 1 — e.g., Authentication}

**Context**: [Brief context for this group of requirements]

| ID | Requirement | Trigger Type |
|----|-------------|--------------|
| REQ-001 | The system SHALL [action] | [Event / State / Generic / Feature / Negative] |
| REQ-002 | WHEN [event] THEN the system SHALL [action] | Event |
| REQ-003 | IF [condition] THEN the system SHALL [action] | Feature |
| REQ-004 | The system SHALL NOT [unsafe behavior] | Negative |

### ${Requirement Group 2 — e.g., Data Management}

**Context**: [Brief context]

| ID | Requirement | Trigger Type |
|----|-------------|--------------|
| REQ-005 | [EARS-formatted requirement] | [Trigger type] |
| REQ-006 | [EARS-formatted requirement] | [Trigger type] |

<!-- Add more requirement groups as needed -->

### Data Requirements

| Data Entity | Purpose | Lifecycle | Constraints |
|-------------|---------|-----------|-------------|
| [e.g., User Session] | [e.g., Track active user] | [e.g., Created on login, destroyed on logout/timeout] | [e.g., Expires after 30 min inactivity] |
| [e.g., Audit Log] | [e.g., Record actions] | [e.g., Append-only, retained 90 days] | [e.g., Immutable once written] |

---

## User Interactions

### Primary User Flow: ${Flow Name}

```
User → [Step 1] → [Step 2] → [Step 3] → [Outcome]
```

1. **[Step 1]**: [Description of what the user does and what the system shows]
2. **[Step 2]**: [Description]
3. **[Step 3]**: [Description]
4. **[Outcome]**: [What the user sees/confirms at the end]

### Alternative Paths

| Path | Trigger | Behavior |
|------|---------|----------|
| [e.g., Invalid input] | [e.g., User submits form with errors] | [e.g., System highlights errors, keeps form data] |
| [e.g., Session expired] | [e.g., User idle > 30 min] | [e.g., System redirects to login, preserves work] |

### Error Scenarios

| Error Condition | System Response | User Message |
|----------------|----------------|--------------|
| [e.g., Network failure] | [e.g., Queue action for retry] | [e.g., "Connection lost. Your work will be saved when reconnected."] |
| [e.g., Validation failure] | [e.g., Reject with details] | [e.g., "Please correct the highlighted fields."] |

---

## Acceptance Criteria

> **Taxonomy**: Every criterion MUST be tagged with `[IMP]`, `[SEF]`, or `[EXT]`.
> - **`[IMP]`** Implementable — Requires new code/configuration. Only these generate implementation tasks.
> - **`[SEF]`** Side-Effect — Automatic consequence of an `[IMP]` criterion. No standalone task.
> - **`[EXT]`** External Verification — Verified externally. No standalone task.
>
> **60% Rule**: At least 60% of criteria MUST be `[IMP]`.

### ${AC Group 1 — e.g., Authentication}

| ID | Criterion | Taxonomy |
|----|-----------|----------|
| AC-001 | [Testable criterion] | [IMP] |
| AC-002 | [Testable criterion] | [SEF] |
| AC-003 | [Testable criterion] | [EXT] |

### ${AC Group 2}

| ID | Criterion | Taxonomy |
|----|-----------|----------|
| AC-004 | [Testable criterion] | [IMP] |
| AC-005 | [Testable criterion] | [IMP] |

---

## Integration Requirements

| External System | Capability Needed | Data Exchanged | Frequency |
|----------------|-------------------|----------------|-----------|
| [e.g., Payment Provider] | [e.g., Process transactions] | [e.g., Amount, currency, confirmation] | [e.g., Per transaction] |
| [e.g., Email Service] | [e.g., Send notifications] | [e.g., Recipient, subject, body] | [e.g., On event] |

---

## Negative Requirements

The system SHALL NOT:

### Security
- REQ-NR001: [EARS negative requirement — e.g., "IF user input is used in SQL query THEN the system SHALL NOT concatenate directly"]
- REQ-NR002: [EARS negative requirement — e.g., "The system SHALL NOT store passwords in plain text"]

### Data Integrity
- REQ-NR003: [EARS negative requirement — e.g., "The system SHALL NOT allow concurrent updates to overwrite each other without detection"]

### Reliability
- REQ-NR004: [EARS negative requirement — e.g., "The system SHALL NOT silently fail without logging the error"]

<!-- Add more as needed — minimum 3 total -->

---

## Non-Goals

This feature does NOT include:

- **${Excluded Feature 1}**: [Why excluded — e.g., "Social login providers are out of scope for the initial release"]
- **${Excluded Feature 2}**: [Why excluded]
- **${Excluded Feature 3}**: [Why excluded]
- **${Excluded Feature 4}**: [Why excluded]

<!-- Minimum 3 non-goals required -->

---

## Assumptions

- [Assumption 1 — e.g., "Users have a valid email address"]
- [Assumption 2 — e.g., "The system is accessed via modern browsers only"]
- [Assumption 3 — e.g., "Default payment provider is Stripe unless specified otherwise"]

---

## Open Questions

| # | Question | Impact if Unresolved | Default Assumption |
|---|----------|---------------------|-------------------|
| 1 | [NEEDS CLARIFICATION: specific question?] | [Scope/Security/UX] | [Best-guess default] |
| 2 | [Question without marker] | [Impact] | [Default] |

<!-- Maximum 3 [NEEDS CLARIFICATION] markers total.
     Only mark questions where NO reasonable default exists.
     See brainstorm command for marker rules. -->
