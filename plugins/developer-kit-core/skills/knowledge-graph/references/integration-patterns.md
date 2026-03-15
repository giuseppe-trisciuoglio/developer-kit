# Knowledge Graph Integration Patterns

This document describes how to integrate the Knowledge Graph with Developer Kit commands.

## Pattern 1: spec-to-tasks Integration

### Phase 2.5: Check Knowledge Graph

**Location**: After Phase 2 (Requirement Extraction), Before Phase 3 (Codebase Analysis)

**Goal**: Check if cached codebase analysis exists from previous runs

**Implementation**:

```
1. Check if knowledge-graph.json exists in spec folder
2. If exists and recent (< 7 days old):
   - Load patterns, components, APIs from KG
   - Ask user via AskUserQuestion:
     "Found cached analysis from X days ago:
      - Y architectural patterns
      - Z components (N controllers, M services, K repositories)
      Use cached analysis or re-explore codebase?"
3. If user chooses cached:
   - Load full KG into context
   - Skip Phase 3 (Codebase Analysis)
   - Proceed directly to Phase 4 (Task Decomposition) with KG context
4. If user chooses re-explore or KG doesn't exist:
   - Proceed to Phase 3 (launch agents)
   - After agents complete, update KG (see Phase 3.5 below)
```

**User Interaction Example**:

```
Found cached codebase analysis from 3 days ago:
- 2 architectural patterns (Repository, Service Layer)
- 5 components (1 controller, 2 services, 2 repositories)
- 3 REST endpoints documented

The analysis is fresh and reliable.
Options:
- "Use cached analysis" (recommended - faster)
- "Re-explore codebase" (always get latest)
```

### Phase 3.5: Update Knowledge Graph

**Location**: After Phase 3 (Codebase Analysis), Before Phase 4 (Task Decomposition)

**Goal**: Persist agent discoveries into the Knowledge Graph for future reuse

**Implementation**:

```
1. Extract structured findings from agent analysis output:
   - Parse agent's comprehensive analysis
   - Map findings to KG schema sections:
     * patterns.architectural: Design patterns discovered
     * patterns.conventions: Coding conventions identified
     * components: Code components (controllers, services, repositories, etc.)
     * apis.internal: REST endpoints and API structure
     * apis.external: External service integrations
     * integration_points: Databases, caches, message queues, etc.

2. Construct KG update object following the schema:
   {
     "metadata": {
       "spec_id": "[from spec folder]",
       "updated_at": "[current ISO timestamp]",
       "analysis_sources": [
         {
           "agent": "[agent-type-used]",
           "timestamp": "[current ISO timestamp]",
           "focus": "codebase analysis for task generation"
         }
       ]
     },
     "patterns": { /* ... */ },
     "components": { /* ... */ },
     "apis": { /* ... */ }
   }

3. Call knowledge-graph skill to update:
   /knowledge-graph update [spec-folder] [update-object] "[agent-name]"

4. Log and report:
   "Knowledge Graph updated:
   - X architectural patterns documented
   - Y coding conventions identified
   - Z components catalogued (N controllers, M services, K repositories)
   - Q API endpoints documented
   - R integration points mapped

   Saved to: docs/specs/[ID]/knowledge-graph.json"

5. Verify update:
   - Read back updated KG to confirm write succeeded
   - Check metadata was updated correctly
   - If write failed, log warning but continue (non-blocking)
```

**Example Agent Output → KG Mapping**:

```
Agent Analysis:
"Found Repository Pattern: All repositories extend JpaRepository<EntityType, ID>
 Found Service Layer: Business logic in @Service classes
 Found: HotelService at src/main/java/.../HotelService.java
 Found: HotelRepository at src/main/java/.../HotelRepository.java
 Found: HotelController with 2 endpoints"

→ KG Update:
{
  "patterns": {
    "architectural": [
      {
        "id": "pat-001",
        "name": "Repository Pattern",
        "convention": "Extend JpaRepository<EntityType, ID>",
        "files": ["**/repository/*Repository.java"]
      },
      {
        "id": "pat-002",
        "name": "Service Layer",
        "convention": "@Service annotation on business logic"
      }
    ]
  },
  "components": {
    "services": [
      {
        "id": "comp-svc-001",
        "name": "HotelService",
        "location": "src/main/java/.../HotelService.java"
      }
    ],
    "repositories": [
      {
        "id": "comp-repo-001",
        "name": "HotelRepository",
        "location": "src/main/java/.../HotelRepository.java"
      }
    ]
  }
}
```

**Important Note**: If user chose to use cached KG in Phase 2.5, **skip this phase** entirely and proceed directly to Phase 4.

---

## Pattern 2: task-implementation Integration

### T-3.5: Pre-load from Knowledge Graph

**Location**: After dependency checks, before implementation work starts

**Goal**: Check if existing specification has cached analysis to inform implementation

**For task execution (`--task=` parameter)**:

```
1. Load task file → extract spec_id from task frontmatter
2. Check if knowledge-graph.json exists in spec folder
3. If KG exists:
   a. Query KG for task-relevant information:
      /knowledge-graph query [spec-folder] components
      /knowledge-graph query [spec-folder] apis
      /knowledge-graph query [spec-folder] patterns

   b. Validate task dependencies against KG:
      /knowledge-graph validate [spec-folder] {
        components: [/* from task Technical Context */],
        apis: [/* from task Technical Context */]
      }

   c. Present validation results to user:
      "From previous analysis of related feature:
      - X services available
      - Y endpoints documented
      - Z patterns established

      Task validation: ✅ All dependencies exist
      Proceed with implementation?"

   d. Load KG context into working memory for implementation phase
```

**For spec-driven task generation (`devkit.spec-to-tasks`)**:

```
1. Resolve the spec folder
2. Check if knowledge-graph.json exists
3. If KG exists:
   a. Load and summarize key findings
   b. Reuse it automatically if fresh; ask only if borderline stale
   c. Feed patterns/components/APIs into task decomposition
4. If no KG exists or it is stale:
   - Run fresh codebase exploration
```

**User Interaction Example**:

```
Found related specification '001-hotel-search' with cached analysis:
- Repository Pattern (extend JpaRepository)
- Service Layer (@Service classes)
- 2 existing services
- 1 existing repository

Use these patterns for consistency?
Options:
- "Yes, use patterns" (recommended - consistency)
- "No, explore fresh" (different approach needed)
```

### Phase 3.5 / T-6.5: Update Knowledge Graph

**Location**:
- After `spec-to-tasks` codebase analysis
- After `task-implementation`, via `spec-quality`

**Goal**: Persist new discoveries from exploration into Knowledge Graph

**When to Execute**:
- During `spec-to-tasks` when a spec folder is being analyzed
- During `task-implementation` once files are implemented and `provides` can be extracted

**Implementation**:

```
1. Resolve the spec folder from the current command context
   - If no spec folder is available, skip this phase

2. Extract new findings from agent exploration:
   - Patterns discovered that weren't in KG
   - New components identified
   - New integration points found
   - Updates to existing patterns/conventions

3. Update Knowledge Graph:
   /knowledge-graph update [spec-folder] [update-object] "spec-to-tasks explorer agent"

   Map agent findings to KG schema sections

4. Log update:
   "Knowledge Graph updated with exploration findings:
   - X new patterns documented
   - Y new components catalogued
   - Z integration points mapped

   Updated: docs/specs/[ID]/knowledge-graph.json"

5. Handle failures gracefully:
   - If write fails: Log warning but continue (non-blocking)
   - Note: "Failed to update Knowledge Graph, continuing without caching"
```

**Example: New Discovery → KG Update**:

```
Agent Discovery:
"Found new PaymentController with 2 endpoints: /api/v1/payments, /api/v1/refunds
Found new integration: Stripe API for payment processing"

→ KG Update:
{
  "components": {
    "controllers": [
      {
        "id": "comp-ctrl-002",
        "name": "PaymentController",
        "location": "src/main/java/.../PaymentController.java",
        "endpoints": [
          { "method": "POST", "path": "/api/v1/payments" },
          { "method": "POST", "path": "/api/v1/refunds" }
        ]
      }
    ]
  },
  "apis": {
    "internal": [
      { "id": "api-int-003", "path": "/api/v1/payments", "method": "POST" },
      { "id": "api-int-004", "path": "/api/v1/refunds", "method": "POST" }
    ],
    "external": [
      {
        "id": "api-ext-002",
        "name": "Stripe API",
        "base_url": "https://api.stripe.com/v1",
        "authentication": "API Key"
      }
    ]
  },
  "integration_points": [
    {
      "id": "int-003",
      "name": "Stripe Integration",
      "type": "external-api",
      "technology": "Stripe",
      "used_by_components": ["PaymentController"]
    }
  ]
}
```

---

## Complete Data Flow

### Full Workflow: New Feature Development

```
1. User creates specification via devkit.brainstorm
   ↓
2. spec-to-tasks Phase 1-2: Analyze specification
   ↓
3. spec-to-tasks Phase 2.5: Check Knowledge Graph
   ├─ KG exists? → Load and present summary
   └─ KG missing/expired → Proceed to Phase 3
   ↓
4. spec-to-tasks Phase 3: Launch architect/explorer agents
   ↓
5. Agent Analysis → Structured Output
   ↓
6. spec-to-tasks Phase 3.5: Update Knowledge Graph
   ├─ Parse agent findings
   ├─ Map to KG schema
   └─ Write to docs/specs/[ID]/knowledge-graph.json
   ↓
7. spec-to-tasks Phase 4: Generate tasks with KG context
   ↓
8. Task files created with Technical Context from KG
   ↓
9. User runs: /devkit.task-implementation --task="docs/specs/[id]/tasks/TASK-001.md"
   ↓
10. task-implementation T-3.5: Pre-load from Knowledge Graph
    ├─ Load task dependencies
    ├─ Query KG for components/APIs
    └─ Validate: "UserService exists? API endpoint available?"
    ↓
11. task-implementation T-4: Implementation
    ↓
12. task-implementation T-6.5: spec-quality updates Knowledge Graph
    ├─ Extract provides from implemented files
    └─ Persist them to KG
    ↓
13. Implementation Complete
```

---

## Query Flow Examples

### Example 1: Task Validation

```
Task file says: "Use HotelRepository for database access"

task-implementation T-3.5: Validate against KG
→ Query: "components.repositories.HotelRepository"

KG Response:
{
  "id": "comp-repo-001",
  "name": "HotelRepository",
  "location": ".../HotelRepository.java",
  "extends": "JpaRepository<Hotel, Long>"
}

Validation: ✅ Component exists
→ Proceed with implementation
```

### Example 2: Pattern Discovery for Task Generation

```
spec-to-tasks Phase 4: Generate tasks for "Add booking feature"

Query KG: "patterns.architectural"

KG Response:
[
  { "name": "Repository Pattern", "convention": "Extend JpaRepository" },
  { "name": "Service Layer", "convention": "@Service classes" }
]

→ Generated Tasks:
  - TASK-001: Create BookingRepository (extend JpaRepository)
  - TASK-002: Create BookingService (@Service annotation)
```

### Example 3: API Integration

```
Task: "Integrate with payment gateway"

Query KG: "apis.external"

KG Response:
[
  {
    "name": "Stripe Integration",
    "base_url": "https://api.stripe.com/v1",
    "authentication": "API Key",
    "endpoints": [...]
  }
]

→ Technical Context in task:
  "Use existing Stripe integration pattern from PaymentService
   Follow same authentication: API Key in header
   Use endpoint: /v1/charges for creating payments"
```

---

## Error Handling and Edge Cases

### KG Not Found

```
User runs: /knowledge-graph query docs/specs/001/ components

Response: Empty result (graceful degradation)
Log: "No existing knowledge graph, will create on first update"

Action: Continue with empty KG structure
```

### Invalid JSON

```
User runs: /knowledge-graph read docs/specs/001/

Error: "Knowledge graph corrupted at docs/specs/001/knowledge-graph.json"

Ask User: "Recreate from codebase analysis?"
Options:
- "Yes, recreate" (run agent analysis)
- "No, cancel" (abort operation)
```

### Validation Failures

```
Query: /knowledge-graph validate ... {
  components: ["UserService"]
}

Response:
{
  "valid": false,
  "errors": ["Component UserService not found"],
  "suggestions": ["Available: HotelService, BookingService"]
}

Action: Present to user, ask how to proceed
```

### Stale Knowledge Graph

```
Check: metadata.updated_at = "2026-02-01"
Current date: "2026-03-14"
Age: 41 days (> 30 day threshold)

Warning: "Knowledge graph is 41 days old and may be stale.
Consider refreshing with fresh codebase analysis."
```

---

## Performance Considerations

### Load Once, Query Multiple Times

**Bad Pattern**: Load KG for each query
```
/kg query ... components  (Reads file)
/kg query ... patterns    (Reads file again)
/kg query ... apis        (Reads file again)
```

**Good Pattern**: Load once, cache in memory
```
/kg read ...              (Reads file once)
→ Use cached KG for multiple queries
```

### Use Specific Filters

**Bad Pattern**: Query all, filter manually
```
/kg query ... all
→ Manually filter through 100 components
```

**Good Pattern**: Query with specific filter
```
/kg query ... components { category: "services" }
→ Returns only services (faster)
```

### Check Freshness Before Use

```
1. Read metadata.updated_at
2. Calculate age: now - updated_at
3. If > 7 days: Warn user "KG may be stale"
4. Offer: "Refresh analysis or proceed with cache?"
```

---

## Best Practices

1. **Always validate requirements** against KG before implementation
2. **Update KG incrementally** after each significant analysis
3. **Log all KG operations** for debugging and audit trail
4. **Handle failures gracefully** - never block on KG errors
5. **Document new discoveries** clearly when updating KG
6. **Review KG age** before relying on it for critical decisions

---

## Migration from Manual Documentation

### Before Knowledge Graph

**Task File (manual)**:
```markdown
## Technical Context
Based on codebase analysis:
- Use Repository pattern
- Extend JpaRepository
- Follow existing service structure
```

### After Knowledge Graph

**Task File (KG-powered)**:
```markdown
## Technical Context
From Knowledge Graph (docs/specs/001/knowledge-graph.json):
- Components: HotelRepository (exists), BookingService (exists)
- Patterns: Repository Pattern (extend JpaRepository), Service Layer (@Service)
- APIs: GET /api/v1/hotels (available)
- Validation: ✅ All dependencies verified
```

---

## Troubleshooting

### Issue: KG Not Loading

**Symptom**: Commands report "Knowledge graph not found"

**Diagnosis**:
1. Check file exists: `ls docs/specs/[ID]/knowledge-graph.json`
2. Check file is valid JSON: `cat docs/specs/[ID]/knowledge-graph.json | python3 -m json.tool`

**Solution**: If file doesn't exist, first update will create it. If invalid, recreate from analysis.

### Issue: Validation False Positives

**Symptom**: Validator reports component missing but it exists

**Diagnosis**:
1. Check KG age: `metadata.updated_at`
2. If KG is old (> 7 days), it may be outdated

**Solution**: Refresh KG by re-running codebase analysis

### Issue: Update Failures

**Symptom**: "Cannot write knowledge graph" error

**Diagnosis**:
1. Check file permissions: `ls -la docs/specs/[ID]/`
2. Check disk space: `df -h`

**Solution**: Fix permissions or free disk space. Operation continues without caching.

---

## See Also

- `../SKILL.md` - Main skill definition
- `schema.md` - Complete JSON schema reference
- `query-examples.md` - Query patterns and usage examples

For command integration, see:
- `/plugins/developer-kit-core/commands/specs/devkit.spec-to-tasks.md` (Phase 2.5, 3.5)
- `/plugins/developer-kit-core/commands/specs/devkit.task-implementation.md` (T-3.5, T-6.5)
- `/plugins/developer-kit-core/commands/specs/devkit.spec-quality.md` (Phase 4)
