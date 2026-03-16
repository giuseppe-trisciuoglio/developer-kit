---
name: knowledge-graph
description: "Manage a persistent Knowledge Graph for specifications. Provides read, query, update, validation, contract-checking, and aggregation workflows so commands can save findings, remember previous analysis, reuse earlier work, and avoid re-analyzing the same codebase. Use when you need to store discovered patterns or components, check whether a dependency already exists, validate task contracts, synchronize `provides` after implementation, or reuse findings across specs."
allowed-tools: Read, Write, Bash
---

# Knowledge Graph

## Overview

Use this skill to maintain `docs/specs/[id-feature]/knowledge-graph.json` as the persistent memory for specification work.

The Knowledge Graph helps commands and agents:

- reuse previous findings instead of re-exploring the codebase
- look up existing patterns, components, APIs, and integrations
- validate task dependencies before implementation starts
- persist new discoveries after analysis or implementation
- compare expected outputs with what completed tasks actually provide

Use the main skill file for workflow and decision rules. Use the reference files for detailed schema and longer examples:

- `references/schema.md`
- `references/query-examples.md`
- `references/integration-patterns.md`

## When to Use

Use this skill when the user or workflow needs to:

- "reuse previous findings", "remember that analysis", or "avoid re-analyzing"
- "store discovered patterns", "save findings", or "save codebase analysis"
- "check if this component already exists"
- "validate against the knowledge graph"
- "confirm task dependencies before implementing"
- "extract provides from completed files"
- "compare expects vs provides"
- "aggregate patterns across specs"

Typical triggers:

- `spec-to-tasks` wants cached context before launching fresh exploration
- `task-implementation` needs to confirm components, APIs, or conventions
- `spec-quality` needs to merge new `provides` into the spec memory
- a user asks for existing services, endpoints, conventions, or integration points

## Instructions

### 1. Choose the correct operation

| Need | Operation | Result |
| --- | --- | --- |
| Load the full graph | `read` | Parsed Knowledge Graph or empty baseline |
| Find specific facts | `query` | Filtered patterns, components, APIs, or integrations |
| Save new discoveries | `update` | Merged Knowledge Graph with refreshed metadata |
| Check task dependencies | `validate` | Errors, warnings, and `valid` status |
| Check expects vs completed work | `validate-contract` | Satisfied and unsatisfied expectations |
| Infer `provides` from files | `extract-provides` | File-to-symbol mappings with inferred types |
| Build cross-spec memory | `aggregate` | Project-level summary across all spec graphs |

### 2. Resolve the target scope first

1. Resolve the spec folder before doing anything else.
2. Use `docs/specs/[id-feature]/knowledge-graph.json` for spec-local data.
3. Use `docs/specs/.global-knowledge-graph.json` only for cross-spec aggregation.
4. If the spec folder is unknown, stop and resolve it before reading or writing.

### 3. Read and query the graph

Use `read` when a command needs the whole document. Use `query` when it only needs a slice.

Command shapes:

```text
/knowledge-graph read [spec-folder]
/knowledge-graph query [spec-folder] [components|patterns|apis|integration-points|all] [optional-filters]
```

Query rules:

1. Prefer specific queries over `all`.
2. Check `metadata.updated_at` before relying on cached results.
3. If the graph is missing, return an empty baseline and explain that the first update will create it.
4. If the graph is stale, warn before using it for critical decisions.

### 4. Update the graph safely

Use `update` after analysis, task execution, or spec-quality synchronization.

Command shape:

```text
/knowledge-graph update [spec-folder] [updates] [source]
```

Update procedure:

1. Read the existing graph if present.
2. Validate that `updates` is well-formed JSON.
3. Deep-merge objects and append arrays without duplicating IDs.
4. Refresh `metadata.updated_at`.
5. Append a new `metadata.analysis_sources` entry describing the source.
6. Write the merged file back to the spec folder.
7. Read it back or validate JSON so the write is confirmed.

Persist these sections when available:

- `patterns`
- `components`
- `apis`
- `integration_points`
- `provides`
- `testing`
- `architecture_decisions`

### 5. Validate dependencies before implementation

Use `validate` before implementation or task generation when the workflow depends on existing code.

Command shape:

```text
/knowledge-graph validate [spec-folder] [requirements]
```

Validate at least:

- required component IDs or names
- required API IDs or paths
- expected architectural patterns or conventions
- integration points that the task assumes already exist

Return a structure like:

```json
{
  "valid": false,
  "errors": ["Component comp-svc-001 not found"],
  "warnings": ["Pattern differs from stored convention"],
  "suggestions": ["Available services: HotelService, BookingService"]
}
```

### 6. Validate contracts between tasks

Use `validate-contract` when a task expects files or symbols from completed dependencies.

Command shape:

```text
/knowledge-graph validate-contract [spec-folder] [expects] [completed-dependencies]
```

Procedure:

1. Read the current graph.
2. Compare each expected file and symbol against completed dependency `provides`.
3. If needed, verify the file exists and inspect symbols directly.
4. Return `satisfied`, `unsatisfied`, and `valid`.
5. Surface missing providers explicitly instead of silently continuing.

### 7. Extract `provides` from files

Use `extract-provides` after implementation to record what a task actually created.

Command shape:

```text
/knowledge-graph extract-provides [files]
```

Detection patterns:

```bash
# Java
grep -nE '^[[:space:]]*(public|protected|private)?[[:space:]]*(abstract[[:space:]]+|final[[:space:]]+)?(class|interface|enum|record)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' path/to/File.java

# TypeScript / JavaScript
grep -nE '^[[:space:]]*export[[:space:]]+(default[[:space:]]+)?(class|interface|function|const|type|enum)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' path/to/file.ts

# Python
grep -nE '^[[:space:]]*(class|def)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' path/to/file.py

# Go
grep -nE '^[[:space:]]*(type[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]+(struct|interface)|func[[:space:]]+([A-Za-z_][A-Za-z0-9_]*|\([^)]+\)[[:space:]]*[A-Za-z_][A-Za-z0-9_]*))' path/to/file.go
```

Inference rules:

1. Infer the type from file path and symbol shape when possible.
2. Favor repository-local relative paths.
3. Store every extracted item in `provides` with `task_id`, `file`, `symbols`, `type`, and `implemented_at`.

### 8. Aggregate across specifications

Use `aggregate` when the project needs a shared view of repeated patterns and conventions.

Command shape:

```text
/knowledge-graph aggregate [project-root]
```

Procedure:

1. Scan `docs/specs/*/knowledge-graph.json`.
2. Collect architectural patterns and conventions from each spec.
3. Deduplicate by stable name or ID.
4. Track which specs contributed each pattern.
5. Write the result to `docs/specs/.global-knowledge-graph.json`.

## Examples

### Example 1: Reuse cached analysis before exploration

```text
/knowledge-graph query docs/specs/001-hotel-search/ patterns {"category":"architectural"}
```

### Example 2: Save new discoveries after agent analysis

```text
/knowledge-graph update docs/specs/001-hotel-search/ {
  "patterns": {
    "architectural": [
      {
        "id": "pat-001",
        "name": "Repository Pattern",
        "convention": "Repositories extend JpaRepository"
      }
    ]
  },
  "components": {
    "services": [
      {
        "id": "comp-svc-001",
        "name": "HotelService",
        "location": "src/main/java/.../HotelService.java",
        "type": "service"
      }
    ]
  }
} "general-code-explorer agent"
```

### Example 3: Validate a task before implementing it

```text
/knowledge-graph validate docs/specs/001-hotel-search/ {
  "components": ["comp-repo-001"],
  "patterns": [{"name":"Repository Pattern"}],
  "apis": ["api-int-001"]
}
```

### Example 4: Compare expected outputs with completed dependencies

```text
/knowledge-graph validate-contract docs/specs/001-hotel-search/ [
  {
    "file": "src/main/java/.../Search.java",
    "symbols": ["Search", "SearchStatus"]
  }
] [
  {
    "task_id": "TASK-001",
    "provides": [
      {
        "file": "src/main/java/.../Search.java",
        "symbols": ["Search", "SearchStatus", "SearchCriteria"]
      }
    ]
  }
]
```

## Best Practices

- Prefer `query` over loading the whole graph when the workflow only needs one section.
- Check freshness before trusting cached information for critical implementation decisions.
- Update the graph immediately after meaningful discoveries so it does not drift behind the codebase.
- Keep identifiers stable so later validations and merges stay deterministic.
- Record `provides` from actual files, not from assumptions or task descriptions.
- Keep the graph structural: store patterns, components, APIs, and relationships, not secrets.
- Use the reference docs for large schema details instead of duplicating them in the main skill.

## Constraints and Warnings

- This skill manages Knowledge Graph artifacts only; it does not generate or modify application source code.
- Restrict reads and writes to the intended spec paths under `docs/specs/`.
- Treat missing or stale data as a signal to warn and refresh, not as proof that the codebase lacks the component.
- Never store credentials, tokens, passwords, or environment-specific secrets in the graph.
- If JSON is invalid or a write fails, surface the error clearly and stop the persistence step instead of hiding the failure.
- Large specs can produce large graphs; prefer focused queries and incremental updates.
- Cross-spec aggregation is optional and should not replace the spec-local graph used by active workflows.

For detailed schema and longer workflow examples, use:

- `references/schema.md`
- `references/query-examples.md`
- `references/integration-patterns.md`
