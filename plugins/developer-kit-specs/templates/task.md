---
id: ${TASK_ID}
title: "${TASK_TITLE}"
spec: ${SPEC_PATH}
lang: ${LANG}
status: pending
dependencies: ${DEPENDENCIES}
ac-mapping: [${AC_MAPPING}]
imp-requirements: [${IMP_REQUIREMENTS}]
---

# ${TASK_ID}: ${TASK_TITLE}

**Functional Description**: ${FUNCTIONAL_DESCRIPTION}

**Maps to Specification**: ${AC_MAPPING}

## ⚠️ Cross-Boundary Warning (if applicable)
<!-- Remove this section if not cross-boundary -->
- **Primary Context**: ${PRIMARY_BOUNDED_CONTEXT}
- **This Task Modifies**: ${CROSS_BOUNDARY_FILE} in ${CROSS_BOUNDARY_CONTEXT}
- **Risk**: HIGH / MEDIUM / LOW
- **Justification**: ${CROSS_BOUNDARY_JUSTIFICATION}

## ⚠️ External Dependency Risk (if applicable)
<!-- Remove this section if no external dependency -->
- **Depends on**: ${EXTERNAL_DEPENDENCY}
- **Status**: Verified / Unverified / At Risk
- **Mitigation**: ${MITIGATION}

## Acceptance Criteria

- [ ] ${ACCEPTANCE_CRITERION_1}
- [ ] ${ACCEPTANCE_CRITERION_2}
- [ ] ${ACCEPTANCE_CRITERION_3}

## Definition of Ready (DoR)

Before starting this task, ensure:
- [ ] Dependencies are completed or explicitly marked as not required.
- [ ] Technical context, patterns, and integration points are understood.
- [ ] Files to create/modify are identified and accessible.
- [ ] Required tooling, commands, and local prerequisites are available.
- [ ] Open questions or blockers have been resolved.

## Technical Context (from Codebase Analysis)

- **Existing Patterns to Follow**: ${EXISTING_PATTERNS}
- **APIs to Integrate With**: ${APIS_TO_INTEGRATE}
- **Shared Components**: ${SHARED_COMPONENTS}
- **Conventions**: ${CONVENTIONS}
- **Architecture Reference**: [relevant entries from docs/specs/architecture.md — stack, data layer, infrastructure]
- **Domain Terms**: [relevant terms from docs/specs/ontology.md — use canonical names consistently]

## Implementation Details (File names only, no code)

**Files to Create**:
- `${FILE_PATH_1}` - ${FILE_PURPOSE_1}
- `${FILE_PATH_2}` - ${FILE_PURPOSE_2}
- `${TEST_FILE_1}` - ${TEST_PURPOSE_1}
- `${TEST_FILE_2}` - ${TEST_PURPOSE_2}

**Files to Modify** (if applicable):
- `${EXISTING_FILE_1}` - ${MODIFICATION_DESCRIPTION}

## Test Instructions

This section describes **what** to test, not **how** to implement test code.

**1. Mandatory Unit Tests:**
   - `${SOURCE_CLASS_1}`:
     - [ ] Verify that [method/unit] correctly handles [success scenario].
     - [ ] Verify that [method/unit] throws an exception/error when [error scenario].
     - [ ] Verify that the [specific business rule] logic works as described in the specification.
   - `${SOURCE_CLASS_2}`:
     - [ ] Test validation of [specific field] with valid, invalid, and borderline values.

**2. Mandatory Integration Tests:**
   - `${FLOW_NAME}`:
     - [ ] Verify that the `${API_ENDPOINT}` endpoint with valid data correctly interacts with the database and returns the expected response.
     - [ ] Verify that a call to the `${API_ENDPOINT}` endpoint with invalid data **does not** modify the database state and returns an appropriate error.

**3. Edge Cases and Error Conditions to Test:**
   - [ ] Send missing or malformed data.
   - [ ] Simulate timeout or failure of an external service.
   - [ ] Test race conditions (if relevant).
   - [ ] Test with high data loads or boundary values.

**Test Acceptance Criteria**:
   - [ ] All tests described above are implemented and pass.
   - [ ] Test coverage for classes with business logic is >= 80%.

## Definition of Done (DoD)

This task is complete when:
- [ ] Functional description is implemented end-to-end.
- [ ] All acceptance criteria are met with evidence in code or tests.
- [ ] Tests in this task are implemented or updated and passing.
- [ ] Required files are created or modified following the documented technical context.
- [ ] Any handoff expectations for dependent tasks are documented.

**Dependencies**: ${DEPENDENCIES}

**Implementation Command**:
/developer-kit-specs:specs.task-implementation --lang=${LANG} --task="docs/specs/${SPEC_ID}/tasks/${TASK_ID}.md"
