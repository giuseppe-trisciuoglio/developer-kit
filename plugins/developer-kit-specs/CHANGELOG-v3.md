# Changelog — Migration v3.0

**Version**: 3.0.0  
**Date**: 2026-05-08  
**Breaking Changes**: Yes — removal of non-essential features

---

## Summary

This release streamlines the SDD workflow by removing non-essential features and consolidating core functionality. The focus is on a lean, high-performance workflow centered around the SDD loop (Spec <-> Code).

---

## Changes

### Core Workflow Simplification
- **SDD Loop**: Replaced the "SDD Triangle" (Spec <-> Test <-> Code) with the "SDD Loop" (Spec <-> Code), focusing on direct alignment between specifications and implementation.
- **Workflow Position**: Updated all command documentation to reflect the streamlined 3-phase lifecycle: Constitution -> Specification -> Implementation -> Finalization.

### Feature Removals
- **Drift Guard**: Removed real-time monitoring of spec-to-implementation drift (`specs.drift-guard`). Drift detection is now handled by `specs.spec-sync-with-code`.
- **TDD Workflow**: Removed the explicit TDD command (`specs.task-tdd`) and related test templates. Testing is now integrated directly into the `task-implementation` and `task-review` phases.
- **KPI Evaluation**: Removed objective quality metrics and the Evaluator Agent.
- **Session Tracking**: Removed the Session Tracking Agent and related hooks.

### Command Updates
- **specs.brainstorm**: Updated to focus on functional specifications without TDD or Drift references.
- **specs.spec-to-tasks**: Streamlined task generation, removing TDD-specific instructions and task count limits related to TDD.
- **specs.task-implementation**: Updated to include verification steps directly, replacing the separate TDD phase.
- **specs.task-review**: Simplified review process, focusing on spec compliance and code quality without KPI dependencies.
- **specs.spec-sync-with-code**: Updated to handle deviation detection and spec updates as the primary synchronization mechanism.
- **specs.spec-sync-context**: Simplified technical context synchronization, removing Drift Guard integration.

### Metadata and Documentation
- **plugin.json**: Updated to remove deleted commands, agents, and skills.
- **README.md**: Completely rewritten to reflect the v3.0 workflow and command set.
- **sdd-workflow.md**: Updated to document the new streamlined lifecycle.

---

## Files Removed

- `commands/specs.task-tdd.md`
- `docs/tdd-workflow.md`
- `agents/evaluator-agent.md`
- `agents/session-tracking-agent.md`
- `hooks/drift-init.py`, `hooks/drift-monitor.py`, `hooks/drift-report.py`
- `hooks/specs-task-tdd-*.py`
- `hooks/task-kpi-analyzer.py`
- `hooks/test-templates/*`
- `skills/task-quality-kpi/`

---

## Migration Guide

### For existing projects
Existing specifications and tasks remain compatible. The `specs.task-tdd` command is no longer available; use `specs.task-implementation` directly for all coding tasks.

### For automated loops
Ralph Loop remains fully functional but will no longer attempt to run TDD or KPI evaluation steps.
