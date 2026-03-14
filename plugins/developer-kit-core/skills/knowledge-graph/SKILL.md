---
name: knowledge-graph
description: "Manage persistent Knowledge Graph for specifications. Provides read, query, update, and validation capabilities for codebase analysis caching. Use when: spec-to-tasks needs to cache/reuse codebase analysis, feature-development needs to validate task dependencies, or any command needs to query existing patterns/components/APIs. Reduces redundant codebase exploration by caching agent discoveries."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Knowledge Graph Skill

## Overview

The Knowledge Graph (KG) is a persistent JSON file that stores discoveries from codebase analysis, eliminating redundant exploration and enabling task validation.

**Location**: `docs/specs/[ID-feature]/knowledge-graph.json`

**Key Benefits:**
- ✅ Avoid re-exploring already-analyzed codebases
- ✅ Validate task dependencies against actual codebase state
- ✅ Share discoveries across team members
- ✅ Accelerate task generation with cached context

---

## When to Use

Use this skill when:

1. **spec-to-tasks needs to cache/reuse codebase analysis** - Store agent discoveries for future reuse
2. **feature-development needs to validate task dependencies** - Check if required components exist before implementing
3. **Any command needs to query existing patterns/components/APIs** - Retrieve cached codebase context
4. **Reducing redundant codebase exploration** - Avoid re-analyzing already-explored code

**Trigger phrases:**
- "Load knowledge graph"
- "Query knowledge graph"
- "Update knowledge graph"
- "Validate against knowledge graph"
- "Check if component exists"
- "Find existing patterns"

---

## Instructions

### 1. read-knowledge-graph

**Purpose**: Load and parse the Knowledge Graph for a specification.

**Usage:**
```
/knowledge-graph read [spec-folder]
```

**Parameters:**
- `spec-folder`: Path to spec folder (e.g., `docs/specs/001-feature/`)

**Behavior:**
- Looks for `knowledge-graph.json` in the spec folder
- Parses and validates JSON structure
- Returns empty KG structure if file doesn't exist
- Raises error if JSON is invalid

**Example:**
```
Input: docs/specs/001-hotel-search/
Output: {
  metadata: { spec_id: "001-hotel-search", version: "1.0" },
  patterns: { architectural: [...], conventions: [...] },
  components: { controllers: [...], services: [...], repositories: [...] }
}
```

**Implementation Steps:**
1. Parse spec folder path
2. Check if `knowledge-graph.json` exists
3. If exists: Read file, parse JSON, validate structure
4. If not exists: Return empty KG with metadata
5. Return parsed KG object

---

### 2. query-knowledge-graph

**Purpose**: Query specific sections of the Knowledge Graph.

**Usage:**
```
/knowledge-graph query [spec-folder] [query-type] [filters]
```

**Parameters:**
- `spec-folder`: Path to spec folder
- `query-type`: One of: `components`, `patterns`, `apis`, `integration-points`, `all`
- `filters`: Optional JSON filters (e.g., `{"category": "services"}`)

**Behavior:**
- Loads KG from spec folder
- Filters by query type
- Applies optional filters
- Returns matching results

**Example Queries:**

```
# Find all services
/knowledge-graph query docs/specs/001-hotel-search/ components {"category": "services"}
→ Returns: [{ id: "comp-svc-001", name: "HotelService", ... }]

# Find architectural patterns
/knowledge-graph query docs/specs/001-hotel-search/ patterns {"category": "architectural"}
→ Returns: [{ name: "Repository Pattern", convention: "..." }]

# Find REST endpoints
/knowledge-graph query docs/specs/001-hotel-search/ apis {"type": "internal"}
→ Returns: [{ path: "/api/v1/hotels", method: "GET" }]
```

**Implementation Steps:**
1. Call `read-knowledge-graph` to load KG
2. Navigate to requested section (e.g., `kg.components`)
3. Apply filters if provided
4. Return filtered results

---

### 3. update-knowledge-graph

**Purpose**: Update the Knowledge Graph with new discoveries from agents or analysis.

**Usage:**
```
/knowledge-graph update [spec-folder] [updates] [source]
```

**Parameters:**
- `spec-folder`: Path to spec folder
- `updates`: Partial KG object with new findings
- `source`: Description of what provided updates (e.g., "general-code-explorer agent")

**Behavior:**
- Loads existing KG (or creates new)
- Deep merges updates into existing KG
- Updates `metadata.updated_at` timestamp
- Adds entry to `metadata.analysis_sources`
- Writes updated KG back to file

**Example:**

```
Input:
  spec-folder: docs/specs/001-hotel-search/
  updates: {
    patterns: {
      architectural: [
        { name: "Service Locator Pattern", convention: "..." }
      ]
    }
  }
  source: "general-software-architect agent"

Behavior:
1. Load existing docs/specs/001-hotel-search/knowledge-graph.json
2. Merge new pattern into patterns.architectural array
3. Update metadata.updated_at to current timestamp
4. Add { agent: "general-software-architect", timestamp: "..." } to analysis_sources
5. Write back to file
```

**Merge Logic:**
- **Arrays**: Append new items (check for duplicates by ID)
- **Objects**: Deep merge, preserve existing keys
- **Metadata**: Always update timestamps and sources

**Implementation Steps:**
1. Call `read-knowledge-graph` to load existing KG
2. Parse `updates` parameter
3. Deep merge updates into KG (preserve existing, add new)
4. Update `metadata.updated_at` to current ISO timestamp
5. Add entry to `metadata.analysis_sources`
6. Write updated KG to `docs/specs/[ID]/knowledge-graph.json`
7. Log summary of changes (e.g., "Added 2 patterns, 1 component")

---

### 4. validate-against-knowledge-graph

**Purpose**: Validate task requirements against actual codebase state stored in KG.

**Usage:**
```
/knowledge-graph validate [spec-folder] [requirements]
```

**Parameters:**
- `spec-folder`: Path to spec folder
- `requirements`: Object with task dependencies (components, APIs, patterns)

**Behavior:**
- Loads KG from spec folder
- Checks if required components/APIs exist
- Compares pattern usage against KG conventions
- Returns validation report with errors and warnings

**Example:**

```
Input:
  spec-folder: docs/specs/001-hotel-search/
  requirements: {
    components: ["comp-repo-001", "comp-svc-missing"],
    apis: ["api-int-001"],
    patterns: [{ name: "Repository Pattern" }]
  }

Output:
  {
    errors: [
      "Component comp-svc-missing not found in codebase"
    ],
    warnings: [
      "API api-int-001 not found, may need implementation"
    ],
    valid: false
  }
```

**Validation Rules:**

| Check | Severity | Message |
|-------|----------|---------|
| Component missing | Error | "Component {id} not found" |
| API missing | Warning | "API {id} not found, may need implementation" |
| Pattern mismatch | Warning | "Pattern {name} differs from convention" |
| Convention violated | Warning | "Naming convention violation: {component}" |

**Implementation Steps:**
1. Call `read-knowledge-graph` to load KG
2. Parse `requirements` parameter
3. Check each required component exists in `kg.components`
4. Check each required API exists in `kg.apis`
5. Check pattern usage matches `kg.patterns`
6. Return validation report with errors/warnings

---

## KG Schema Reference

The Knowledge Graph follows this structure:

```
knowledge-graph.json
├── metadata
│   ├── spec_id (string)
│   ├── feature_name (string)
│   ├── created_at (ISO timestamp)
│   ├── updated_at (ISO timestamp)
│   ├── version (string)
│   └── analysis_sources (array of {agent, timestamp, focus})
├── codebase_context
│   ├── project_structure
│   └── technology_stack
├── patterns
│   ├── architectural (array)
│   └── conventions (array)
├── components
│   ├── controllers (array)
│   ├── services (array)
│   ├── repositories (array)
│   ├── entities (array)
│   └── dtos (array)
├── apis
│   ├── internal (array)
│   └── external (array)
└── integration_points (array)
```

For detailed schema with examples, see `references/schema.md`.

---

## Integration Patterns

The Knowledge Graph integrates with Developer Kit commands through specific phases in the spec-to-tasks and feature-development workflows.

**Key Integration Points:**

- **spec-to-tasks Phase 2.5**: Check/load cached analysis before exploring
- **spec-to-tasks Phase 3.5**: Persist agent discoveries after analysis
- **feature-development Phase 1.5**: Pre-load and validate task dependencies
- **feature-development Phase 2.5**: Update KG with new discoveries

For detailed integration patterns, data flows, and examples, see `references/integration-patterns.md`.

---

## Error Handling

### File Not Found
- **Behavior**: Return empty KG structure
- **Message**: "No existing knowledge graph, will create new"
- **Action**: Continue with empty KG, will be created on first update

### Invalid JSON
- **Behavior**: Raise error
- **Message**: "Knowledge graph corrupted at {path}"
- **Action**: Ask user: "Recreate from codebase analysis?"

### Merge Conflicts
- **Behavior**: Preserve existing values, add new with timestamps
- **Message**: "Merged X new findings into existing knowledge graph"

### Write Failure
- **Behavior**: Log error, continue without caching
- **Message**: "Cannot write knowledge graph, continuing without cache"

---

## Performance Considerations

- **Lazy loading**: Only load KG when explicitly requested
- **Incremental updates**: Merge changes, don't rewrite entire file
- **Cache invalidation**: Check timestamp, re-explore if KG > 7 days old
- **File size**: Monitor KG size; if > 1MB, suggest splitting by feature

---

## Security

- **Path validation**: Only read KG from `docs/specs/[ID]/` paths
- **JSON injection**: Validate all updates before merging
- **Secrets exclusion**: KG should NOT contain passwords, API keys, tokens
- **Git safety**: KG files can be committed (no sensitive data by design)

---

## Best Practices

### When to Query KG
- ✅ Before launching expensive codebase analysis
- ✅ When generating tasks to enrich technical context
- ✅ When validating task dependencies
- ✅ When checking if patterns/components exist

### When to Update KG
- ✅ After agent analysis completes (new discoveries)
- ✅ After implementing new components (add to graph)
- ✅ After discovering new patterns (document conventions)
- ❌ NOT during every operation (update in batches)

### KG Freshness
- **7 days**: Consider KG fresh, use cached analysis
- **30 days**: KG getting stale, warn user
- **Never updated**: Offer to regenerate from codebase

---

## Examples

### Example 1: Cache Agent Discoveries

```
# spec-to-tasks Phase 3.5
Agent output: "Found Repository Pattern with JpaRepository convention"

Update KG:
/knowledge-graph update docs/specs/001-feature/ {
  patterns: {
    architectural: [
      {
        id: "pat-001",
        name: "Repository Pattern",
        convention: "All repositories extend JpaRepository"
      }
    ]
  }
} "general-software-architect agent"

Result: knowledge-graph.json updated with pattern discovery
```

### Example 2: Validate Task Dependencies

```
# feature-development Task Mode
Task: "Use HotelRepository to search hotels"

Validate:
/knowledge-graph validate docs/specs/001-hotel-search/ {
  components: ["comp-repo-001"]
}

Result:
{
  valid: true,
  errors: [],
  warnings: []
}

→ Task validated, proceed with implementation
```

### Example 3: Query for Context

```
# spec-to-tasks Phase 4
Need to generate tasks for "Add booking feature"

Query KG:
/knowledge-graph query docs/specs/001-hotel-search/ patterns

Result:
[
  { name: "Repository Pattern", convention: "Extend JpaRepository" },
  { name: "Service Layer", convention: "@Service classes" }
]

→ Generate tasks following discovered patterns
```

---

## Constraints and Warnings

### Critical Constraints

- **Read-Only Operations**: The knowledge-graph skill performs read-only operations on the codebase. It does NOT modify source code files, only creates/updates `knowledge-graph.json` files.
- **Path Validation**: The skill only reads/writes KG files from `docs/specs/[ID]/` paths. It will NOT access files outside this structure.
- **No Automatic Code Generation**: This skill caches analysis results, it does NOT generate implementation code automatically.

### Limitations

- **Validation Scope**: The `validate-against-knowledge-graph` function checks if components exist in the KG, but cannot verify if they exist in the actual codebase if the KG is outdated.
- **Freshness Dependency**: KG accuracy depends on how recently it was updated. A KG older than 7 days may be stale.
- **Single-Spec Scope**: Each KG is specific to a single specification (`docs/specs/[ID]/`). It does NOT provide cross-spec knowledge aggregation.
- **File Size**: KG files can grow large (>1MB) for complex specifications. Monitor size and consider splitting if needed.

### Warnings

- **Stale Knowledge**: If KG `updated_at` is >30 days old, the analysis may not reflect current codebase state. Consider re-running codebase analysis.
- **Validation False Positives**: The validator may report "component not found" if the KG was created before the component was implemented. Always verify with actual codebase.
- **Merge Conflicts**: If KG is under version control, merge conflicts may occur. The skill uses deep-merge strategy to preserve existing data.
- **Manual Edits**: Manual edits to `knowledge-graph.json` are supported but may be overwritten if agents update the file. Document manual changes clearly.

### Security Considerations

- **No Secrets Storage**: KG should NOT contain passwords, API keys, tokens, or other sensitive data. It only stores structural information (patterns, components, APIs).
- **Git Safe**: KG files are designed to be committed to git (no sensitive data by design).
- **Path Traversal Protection**: All file operations are restricted to `docs/specs/` subdirectories to prevent path traversal attacks.
- **JSON Injection Prevention**: All updates are validated as proper JSON before merging into KG.

### Performance Considerations

- **Lazy Loading**: KG is only loaded when explicitly requested (not automatically on every operation).
- **Incremental Updates**: Updates use deep-merge to preserve existing data, not full rewrites.
- **Cache Invalidation**: Check `metadata.updated_at` before using KG; re-explore if >7 days old.
- **File Size Monitoring**: Monitor KG file size; if >1MB, consider splitting by feature area.

### Best Practices

- **Update Regularly**: Refresh KG after significant codebase changes or new feature implementations.
- **Validate First**: Always use `validate-against-knowledge-graph` before implementing tasks that depend on specific components.
- **Review Before Use**: Check KG age and contents before relying on cached analysis for critical decisions.
- **Document Discoveries**: Add clear descriptions when updating KG to help future users understand findings.
- **Team Coordination**: Communicate with team when updating KG to avoid conflicting updates.

---

## See Also

- `references/schema.md` - Complete JSON schema with examples
- `references/query-examples.md` - Query patterns and examples

For integration with commands, see:
- `/plugins/developer-kit-core/commands/devkit.spec-to-tasks.md` (Phase 2.5, 3.5)
- `/plugins/developer-kit-core/commands/devkit.feature-development.md` (Phase 1.5, 2.5)
