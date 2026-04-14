# AI Agent Workflow: Specification-Driven Development (SDD)

This document defines the mandatory workflow for AI coding agents interacting with this repository. To ensure high-quality, maintainable, and synchronized code, all agents **MUST** follow the Specification-Driven Development (SDD) process provided by the `developer-kit-specs` plugin.

## 1. Core Principles

- **Spec is Truth**: The functional specification in `docs/specs/` is the single source of truth for *WHAT* should be built.
- **SDD Triangle**: Always keep **Specification**, **Tests**, and **Code** aligned. Every change must update all three.
- **Atomic Tasks**: Implementation happens only through atomic tasks generated from a specification.
- **Living Deliverables**: Specifications are not static; they must be updated when implementation reveals new constraints or refinements.

## 2. The SDD Lifecycle

AI Agents must follow these three phases in order:

### Phase 1: Specification & Planning
Before writing any implementation code:
1. **Brainstorm**: Use `/specs:brainstorm "idea"` (complex) or `/specs:quick-spec "idea"` (simple) to create a functional specification in `docs/specs/[ID]/`.
2. **Quality Check**: Run `/specs:spec-quality-check docs/specs/[ID]/` to validate the requirements.
3. **Generate Tasks**: Convert the spec into executable tasks using `/specs:spec-to-tasks --lang=[lang] docs/specs/[ID]/`.
4. **Manage Scope**: If a task has complexity > 50, use `/specs:task-manage --action=split` to break it down.

### Phase 2: Implementation (Per-Task Loop)
For **each** task in `pending` status, follow this strict sequence:
1. **RED Phase (TDD)**: Run `/specs:task-tdd --task="..."` to generate failing tests first.
2. **GREEN Phase**: Run `/specs:task-implementation --task="..."` to implement the logic and make tests pass.
3. **Review**: Run `/specs:task-review --task="..."`. You **MUST** fix all findings until the review passes.
4. **Cleanup**: Run `/specs:code-cleanup --task="..."` to perform final code hygiene (no logic changes allowed here).

### Phase 3: Finalization & Sync
After completing one or more tasks:
1. **Spec Sync**: Run `/specs:spec-sync-with-code docs/specs/[ID]/`. This detects drift and updates the functional spec with decisions made during coding.
2. **Context Sync**: Run `/specs:spec-sync-context docs/specs/[ID]/` to update the Knowledge Graph and task metadata.

## 3. Automation with Ralph Loop

For long-running implementations or multiple tasks, use the **Ralph Loop** to manage context and state:
1. **Initialize**: `python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py --action=start --spec=docs/specs/[ID]/`
2. **Iterate**: Run `python3 .../ralph_loop.py --action=loop --spec=...` to get the next command, execute it, and repeat.

## 4. Mandatory Commands Reference

| Command | When to use |
|---------|-------------|
| `/specs:brainstorm` | Starting a new complex feature. |
| `/specs:quick-spec` | Bug fixes or small changes (<3 files). |
| `/specs:spec-to-tasks` | Bridge from WHAT (spec) to HOW (code). |
| `/specs:task-tdd` | Mandatory first step of implementation (RED). |
| `/specs:task-implementation` | Implementing the solution (GREEN). |
| `/specs:task-review` | Mandatory gate before cleanup. |
| `/specs:spec-sync-with-code` | Closing the loop by updating the spec. |

## 5. Prohibited Actions

- **DO NOT** implement features without a corresponding task in `docs/specs/`.
- **DO NOT** skip the `task-review` step.
- **DO NOT** modify functional logic during the `code-cleanup` phase.
- **DO NOT** leave the specification in a "drifted" state; always sync after implementation.

---
*Follow this workflow to maintain the integrity of the Developer Kit ecosystem.*
