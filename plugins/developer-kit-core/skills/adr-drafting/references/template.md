# Default ADR Template

Use this template when the repository does not already provide an ADR structure.

```markdown
# ADR-NNNN: Decision Title

## Status
Proposed

## Context
Describe the problem, constraints, trade-offs, and any alternatives that influenced this decision.

## Decision
Describe the architectural choice that was made.

## Consequences
Describe what becomes easier, harder, riskier, or more expensive because of this decision.
```

## Default Conventions

- Directory: `docs/architecture/adr`
- Filename: `NNNN-short-kebab-title.md`
- Title format: `ADR-NNNN: Decision Title`
- Starting number: `0001` if no prior ADR exists

## Status Guidance

- `Proposed` — The change is being considered or prepared
- `Accepted` — The team has agreed to the decision
- `Rejected` — The proposed decision was considered and declined

Keep status values simple unless the repository already uses a richer ADR lifecycle.
