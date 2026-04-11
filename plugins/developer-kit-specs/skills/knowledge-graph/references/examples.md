# Examples - Knowledge Graph

Practical examples of Knowledge Graph operations and workflows.

## Example 1: Cache Agent Discoveries

**Scenario:** spec-to-tasks Phase 3.5 - Agent discovers Repository Pattern

**Agent output:**
```
Found Repository Pattern with JpaRepository convention
All repositories extend JpaRepository<Entity, ID>
Located in: src/main/java/com/example/repository/
```

**Update KG:**
```
/knowledge-graph update docs/specs/001-hotel-search/ {
  patterns: {
    architectural: [
      {
        id: "pat-001",
        name: "Repository Pattern",
        category: "data-access",
        convention: "All repositories extend JpaRepository<Entity, ID>",
        location: "src/main/java/com/example/repository/",
        discovered_at: "2026-03-14T10:30:00Z"
      }
    ]
  }
} "general-software-architect agent"
```

**Result:**
- `docs/specs/001-hotel-search/knowledge-graph.json` updated with pattern discovery
- Metadata updated with new analysis source
- Pattern can be queried in future operations

---

## Example 2: Validate Task Dependencies

**Scenario:** task-implementation Task Mode - Task requires HotelRepository

**Task:** "Use HotelRepository to search hotels"

**Validate:**
```
/knowledge-graph validate docs/specs/001-hotel-search/ {
  components: ["comp-repo-001"]
}
```

**Result:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "found": [
    {
      "id": "comp-repo-001",
      "name": "HotelRepository",
      "type": "repository",
      "location": "src/main/java/com/hotels/search/repository/HotelRepository.java"
    }
  ]
}
```

**Outcome:** Task validated, proceed with implementation

---

## Example 3: Query for Context

**Scenario:** spec-to-tasks Phase 4 - Generate tasks for new feature

**Need:** Generate tasks for "Add booking feature" using existing patterns

**Query KG:**
```
/knowledge-graph query docs/specs/001-hotel-search/ patterns
```

**Result:**
```json
[
  {
    "name": "Repository Pattern",
    "convention": "Extend JpaRepository with Entity and ID types"
  },
  {
    "name": "Service Layer",
    "convention": "@Service classes with business logic"
  },
  {
    "name": "DTO Pattern",
    "convention": "Data Transfer Objects for API layer"
  }
]
```

**Usage:** Generate tasks following discovered patterns

---

## Example 4: Contract Validation Failure

**Scenario:** Task expects SearchId value object, but no dependency provides it

**Task Expects:**
```json
{
  "expects": [
    {
      "file": "src/main/java/com/hotels/search/domain/valueobject/SearchId.java",
      "symbols": ["SearchId"]
    }
  ]
}
```

**Completed Dependencies:**
```json
[
  {
    "task_id": "TASK-001",
    "provides": [
      {
        "file": "src/main/java/com/hotels/search/domain/entity/Search.java",
        "symbols": ["Search", "SearchStatus", "SearchCriteria"]
      }
    ]
  }
]
```

**Validate Contract:**
```
/knowledge-graph validate-contract docs/specs/001-hotel-search/ expects completed_dependencies
```

**Result:**
```json
{
  "satisfied": [
    {
      "expectation": "Search entity with symbols [Search, SearchStatus]",
      "provided_by": "TASK-001"
    }
  ],
  "unsatisfied": [
    {
      "expectation": "SearchId value object",
      "provided_by": "None",
      "reason": "No completed dependency provides SearchId"
    }
  ],
  "valid": false
}
```

**Action:** Implement SearchId in current task or reorder dependencies

---

## Example 5: Extract Provides from Implementation

**Scenario:** Task completed, extract what was implemented

**Files implemented:**
```json
[
  "src/main/java/com/hotels/search/domain/entity/Search.java",
  "src/main/java/com/hotels/search/domain/valueobject/SearchId.java"
]
```

**Extract:**
```
/knowledge-graph extract-provides files
```

**Result:**
```json
{
  "provides": [
    {
      "file": "src/main/java/com/hotels/search/domain/entity/Search.java",
      "symbols": ["Search", "SearchStatus"],
      "type": "entity"
    },
    {
      "file": "src/main/java/com/hotels/search/domain/valueobject/SearchId.java",
      "symbols": ["SearchId"],
      "type": "value-object"
    }
  ]
}
```

**Usage:** Persist to KG for future contract validation

---

## Example 6: Aggregate Multiple KGs

**Scenario:** Create project-wide knowledge graph from all specs

**Aggregate:**
```
/knowledge-graph aggregate /path/to/project/root
```

**Process:**
1. Scan all `docs/specs/*/knowledge-graph.json` files
2. Extract patterns.architectural and patterns.conventions
3. Deduplicate by pattern name
4. Write to `docs/specs/.global-knowledge-graph.json`

**Result:**
```json
{
  "metadata": {
    "aggregated_at": "2026-03-14T15:00:00Z",
    "project_root": "/path/to/project",
    "contributing_specs": ["001-hotel-search", "002-booking", "003-payment"],
    "total_patterns": 15
  },
  "patterns": {
    "architectural": [
      {
        "name": "Repository Pattern",
        "sources": ["001-hotel-search", "002-booking"],
        "frequency": 2,
        "first_seen": "2026-03-01T10:00:00Z",
        "convention": "Extend JpaRepository<Entity, ID>"
      },
      {
        "name": "Service Layer",
        "sources": ["001-hotel-search", "002-booking", "003-payment"],
        "frequency": 3,
        "first_seen": "2026-03-01T10:00:00Z",
        "convention": "@Service classes with @Transactional methods"
      }
    ],
    "conventions": [
      {
        "name": "Naming Convention",
        "sources": ["001-hotel-search"],
        "frequency": 1,
        "examples": ["Repository suffix for repositories", "Service suffix for services"]
      }
    ]
  }
}
```

---

## Example 7: Query Specific Component Types

**Scenario:** Find all services in the codebase

**Query:**
```
/knowledge-graph query docs/specs/001-hotel-search/ components {"category": "services"}
```

**Result:**
```json
[
  {
    "id": "comp-svc-001",
    "name": "HotelSearchService",
    "type": "service",
    "location": "src/main/java/com/hotels/search/service/HotelSearchService.java",
    "annotations": ["@Service"],
    "methods": ["searchHotels", "getHotelById"]
  },
  {
    "id": "comp-svc-002",
    "name": "BookingService",
    "type": "service",
    "location": "src/main/java/com/hotels/booking/service/BookingService.java",
    "annotations": ["@Service"],
    "methods": ["createBooking", "cancelBooking"]
  }
]
```

---

## Example 8: Validate API Existence

**Scenario:** Task needs to call internal API `/api/v1/hotels`

**Validate:**
```
/knowledge-graph query docs/specs/001-hotel-search/ apis {
  "type": "internal",
  "path": "/api/v1/hotels"
}
```

**Result:**
```json
[
  {
    "id": "api-int-001",
    "path": "/api/v1/hotels",
    "method": "GET",
    "type": "internal",
    "controller": "HotelController",
    "description": "Search hotels by criteria"
  }
]
```

**Outcome:** API exists, task can proceed

---

## Example 9: Full Workflow Integration

**Scenario:** Complete spec-to-tasks workflow with KG

### Phase 1: Exploration
```
Agent: Explore codebase for "hotel search aggregation"
Discovers:
- Repository Pattern
- Service Layer Pattern
- DTO Pattern
```

### Phase 2: Update KG (after exploration)
```
/knowledge-graph update docs/specs/001-hotel-search/ {
  patterns: {
    architectural: [
      { "name": "Repository Pattern", "convention": "..." },
      { "name": "Service Layer", "convention": "..." },
      { "name": "DTO Pattern", "convention": "..." }
    ]
  }
} "general-software-architect agent"
```

### Phase 3: Generate Tasks
```
Query KG for patterns → Generate tasks following patterns
```

### Phase 4: Validate Task Dependencies
```
/knowledge-graph validate docs/specs/001-hotel-search/ {
  components: ["comp-repo-001", "comp-svc-001"]
}
```

### Phase 5: Implement Task
```
Implement feature following discovered patterns
```

### Phase 6: Extract Provides
```
/knowledge-graph extract-provides [
  "src/main/java/.../HotelAggregateService.java",
  "src/main/java/.../HotelAggregateRepository.java"
]
```

### Phase 7: Update KG with New Components
```
/knowledge-graph update docs/specs/001-hotel-search/ {
  components: {
    services: [...],
    repositories: [...]
  },
  provides: [...]
} "task-implementation agent"
```

---

## Example 10: Stale Knowledge Detection

**Scenario:** KG is 45 days old, may be stale

**Check:**
```
/knowledge-graph read docs/specs/001-hotel-search/
```

**Result:**
```json
{
  "metadata": {
    "updated_at": "2026-02-01T10:00:00Z"
  }
}
```

**Calculate age:** 45 days old (> 30 day threshold)

**Warning:**
```
⚠️  Warning: Knowledge graph is stale (45 days old)
Codebase may have changed since last analysis.
Recommend regenerating from codebase.

Would you like to:
1. Proceed with stale knowledge (may have outdated info)
2. Regenerate knowledge graph from codebase (recommended)
```

---

## Example 11: Merge Conflict Resolution

**Scenario:** Two agents update KG concurrently

**Agent A updates:**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Repository Pattern", "convention": "JpaRepository" }
    ]
  }
}
```

**Agent B updates:**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Service Layer", "convention": "@Service" }
    ]
  }
}
```

**Merge result (deep merge):**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Repository Pattern", "convention": "JpaRepository" },
      { "name": "Service Layer", "convention": "@Service" }
    ]
  },
  "metadata": {
    "updated_at": "2026-03-14T15:30:00Z",
    "analysis_sources": [
      { "agent": "Agent A", "timestamp": "2026-03-14T15:00:00Z" },
      { "agent": "Agent B", "timestamp": "2026-03-14T15:30:00Z" }
    ]
  }
}
```

**Message:** "Merged 2 new findings into existing knowledge graph"

---

## Example 12: Incremental Learning

**Scenario:** KG grows as project evolves

**Day 1 (Initial):**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Repository Pattern" }
    ]
  }
}
```

**Day 7 (After feature additions):**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Repository Pattern" },
      { "name": "Service Layer" },
      { "name": "DTO Pattern" }
    ]
  }
}
```

**Day 30 (After new features):**
```json
{
  "patterns": {
    "architectural": [
      { "name": "Repository Pattern" },
      { "name": "Service Layer" },
      { "name": "DTO Pattern" },
      { "name": "Factory Pattern" },
      { "name": "Strategy Pattern" }
    ]
  }
}
```

**Benefit:** KG becomes more comprehensive over time, improving task generation and validation.

---

## Example 13: Cross-Spec Learning

**Scenario:** Learn patterns across multiple specifications

**Spec 001 (Hotel Search):**
- Uses Repository Pattern
- Uses Service Layer

**Spec 002 (Booking):**
- Uses Repository Pattern
- Uses Service Layer
- Uses Unit of Work Pattern

**Aggregated:**
```json
{
  "patterns": {
    "architectural": [
      {
        "name": "Repository Pattern",
        "sources": ["001-hotel-search", "002-booking"],
        "frequency": 2
      },
      {
        "name": "Service Layer",
        "sources": ["001-hotel-search", "002-booking"],
        "frequency": 2
      },
      {
        "name": "Unit of Work Pattern",
        "sources": ["002-booking"],
        "frequency": 1
      }
    ]
  }
}
```

**Usage:** When generating tasks for Spec 003, recommend following most common patterns (Repository, Service Layer).

---

## Example 14: Error Recovery

**Scenario:** KG file corrupted

**Read attempt:**
```
/knowledge-graph read docs/specs/001-hotel-search/
```

**Error:**
```
❌ Error: Knowledge graph corrupted at docs/specs/001-hotel-search/knowledge-graph.json
Invalid JSON: Expecting ',' delimiter: line 42 column 5 (char 1023)
```

**Recovery options:**
```
🔧 Recovery options:

1. Recreate from codebase analysis
   - Re-run codebase exploration
   - Generate new KG from scratch
   - Estimated time: 2-5 minutes

2. Restore from backup (if available)
   - Check git history for previous version
   - Restore last known good version

3. Manual repair
   - Edit JSON file to fix syntax
   - Advanced users only

Which option would you like?
```

---

## Example 15: Performance Optimization

**Scenario:** KG file is 1.5 MB (too large)

**Detection:**
```
⚠️  Warning: Knowledge graph is large (1.5 MB)
Recommend splitting by feature area for better performance.

Current structure:
docs/specs/001-hotel-search/knowledge-graph.json (1.5 MB)

Suggested split:
docs/specs/001-hotel-search/kg-auth.json (300 KB)
docs/specs/001-hotel-search/kg-database.json (400 KB)
docs/specs/001-hotel-search/kg-api.json (500 KB)
docs/specs/001-hotel-search/kg-services.json (300 KB)

Would you like to split the knowledge graph?
```

---

## Summary

**Common operations:**
1. **Cache discoveries**: Update KG with agent findings
2. **Validate dependencies**: Check if components exist
3. **Query patterns**: Retrieve conventions for task generation
4. **Validate contracts**: Check if dependencies provide what's needed
5. **Extract provides**: Analyze implementation to capture what was built
6. **Aggregate KGs**: Create project-wide pattern summary
7. **Detect staleness**: Check if KG needs refresh

**Key workflows:**
- spec-to-tasks: Explore → Update KG → Query KG for patterns
- task-implementation: Validate dependencies → Implement → Extract provides → Update KG
- spec-quality: Sync provides from completed tasks

**Error handling:**
- File not found → Create new KG
- Invalid JSON → Offer to recreate
- Stale KG → Warn user, offer refresh
- Validation failure → Report errors, continue
