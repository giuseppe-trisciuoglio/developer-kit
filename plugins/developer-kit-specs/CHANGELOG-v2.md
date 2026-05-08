# Changelog — Skill Workflow Anti-Drift

**Version**: 2.0.0  
**Date**: 2026-05-08  
**Breaking Changes**: Yes — new status schema, new task metadata fields

---

## Summary

This release addresses 8 systemic drift patterns identified in spec-driven development workflows. The changes span all 4 primary skills and 5 secondary skills, introducing unified status schemas, acceptance criteria taxonomy, bounded context validation, and an escalation path for design-level problems.

---

## Primary Skills

### specs.brainstorm — v2.0

**Added**:
- **Phase 0: Input Mode Detection** — Detects if input is a structured document (ADR/RFC) and extracts architectural constraints
- **Acceptance Criteria Taxonomy `[IMP]`/`[SEF]`/`[EXT]`** — Classifies every criterion as implementable, side-effect, or external verification
- **60% Rule** — Ensures at least 60% of criteria are `[IMP]` (prescriptive)
- **Bounded Context Impact Statement (Section 6)** — Documents primary/secondary bounded contexts and cross-boundary risk
- **ADR Consistency Check** — Verifies spec does not silently contradict input ADR decisions

**Breaking**:
- Acceptance criteria MUST now include taxonomy tags in generated specs

### specs.spec-to-tasks — v2.0

**Added**:
- **Spec Fidelity Gate** — Verifies spec has taxonomy before task decomposition
- **`[IMP]`-only Task Decomposition** — Only `[IMP]` criteria generate implementation tasks
- **Bounded Context Boundary Check** — Flags tasks that modify files outside primary context
- **External Dependency Pre-Flight** — Flags tasks depending on unverified interfaces (e.g., ADR-038)
- **File Collision Detection** — Merges/splits tasks that create/modify the same file
- **Test Instructions Fidelity Check** — Removes test scenarios not in the functional spec
- **Traceability Matrix with `[I]`/`[S]`/`[E]` types** — Separate coverage tracking per criterion type

**Breaking**:
- Task template now requires `imp-requirements`, `ac-mapping`, `cross-boundary`, `external-dep-risk` frontmatter fields
- Tasks no longer generated for `[SEF]`/`[EXT]` criteria

### specs.task-implementation — v2.0

**Added**:
- **Unified Status Schema** — `passed`/`needs_fix`/`partial`/`escalate` (4 states)
- **Ralph Loop Circuit Breaker** — Escalates after 3 iterations on the same issue
- **Contract Renegotiation Protocol** — Contracts are proposals for first 3 tasks, stable after
- **Bounded Context Adherence Check (T-4.6)** — Validates file targets against bounded contexts
- **Escalation Path (T-7)** — Generates escalation reports and returns to spec-to-tasks
- **Spec Traceability Gate (T-1)** — Shows task position in overall feature context

**Breaking**:
- Review status `PASSED`/`FAILED` no longer accepted — must use unified schema
- Contract validation now allows renegotiation for early tasks

### specs.task-review — v2.0

**Added**:
- **Unified Status Schema** — `passed`/`needs_fix`/`partial`/`escalate` in output
- **Spec Fidelity Check (Phase 4.5)** — Verifies task covers declared `[IMP]` criteria only
- **Bounded Context Adherence Review (Phase 3.6)** — Checks cross-boundary modifications
- **Architecture Boundary Review (Phase 5.5)** — Detects feature scattering across contexts
- **Escalate state** — For design-level problems (undocumented cross-boundary, invented entities, etc.)

**Breaking**:
- Review output now uses 4-state schema instead of binary PASSED/FAILED
- New review sections for bounded context and architecture checks

---

## Secondary Skills

### specs.ralph-loop — v2.0

**Added**:
- State machine supports `escalate` as alternative to `fix`
- Circuit Breaker: forces `escalate` after 3 Ralph Loop iterations on same issue
- State transitions documented for all 4 review statuses

### specs.task-manage — v2.0

**Added**:
- Task templates include `imp-requirements`, `ac-mapping`, `cross-boundary`, `external-dep-risk`
- Action: Add populates new fields from spec automatically
- Action: Split redistributes AC-IDs among subtasks
- Complexity Score includes cross-boundary (+10) and external-dep-risk (+5) weights

### specs.task-tdd — v2.0

**Added**:
- Test generation filters for `[IMP]` criteria only
- `[SEF]` criteria get comments: "verified in e2e"
- `[EXT]` criteria get comments: "verified externally"
- Backward compatibility: generates tests for all ACs if `ac-mapping` is missing

### specs.spec-quality-check — v2.0

**Added**:
- Quality Scan checks: AC taxonomy tags, 60% rule, Bounded Context Impact Statement
- Coverage summary includes "AC Taxonomy" and "Bounded Context Impact" dimensions
- Priority boost: missing taxonomy is the first question asked

### specs.spec-sync-with-code — v2.0

**Added**:
- Architecture Deviations category in deviation report
- Automatic task creation checks for escalation reports before proceeding
- Taxonomy compliance verification in sync validation

---

## Migration Guide

### For existing specs without taxonomy

Run `specs.spec-quality-check` on existing specs. It will detect missing taxonomy as the first issue and guide you through tagging.

### For existing tasks without new metadata

Tasks without `imp-requirements`/`ac-mapping` are treated as "legacy" — backward compatibility is maintained. Run `specs.spec-sync-context --task=TASK-XXX` to enrich existing tasks.

### For ralph-loop state files

Existing `fix_plan.json` files without `iteration_count` are treated as iteration 0. The Circuit Breaker will start counting from the next review.

---

## Files Changed

| File | Change Type |
|------|-------------|
| `specs.brainstorm.md` | Major — Phase 0 added, AC taxonomy, BC Impact Statement |
| `specs.spec-to-tasks.md` | Major — 7 new gates/checks, updated templates |
| `specs.task-implementation.md` | Major — Unified schema, Circuit Breaker, Escalation Path |
| `specs.task-review.md` | Major — 4-state schema, Spec Fidelity, Architecture Review |
| `specs.ralph-loop.md` | Minor — State machine updated for escalate |
| `specs.task-manage.md` | Minor — New metadata fields, complexity update |
| `specs.task-tdd.md` | Minor — [IMP] filter for test generation |
| `specs.spec-quality-check.md` | Minor — Taxonomy checks added |
| `specs.spec-sync-with-code.md` | Minor — Architecture deviations, escalation handling |
| `specs.quick-spec.md` | No change — out of scope for this release |
| `specs.spec-sync-context.md` | No change — Phase 5.5 handles drift detection |
| `specs.ralph-loop-status.md` | No change — display only |
| `specs.ralph-loop-cancel.md` | No change |
