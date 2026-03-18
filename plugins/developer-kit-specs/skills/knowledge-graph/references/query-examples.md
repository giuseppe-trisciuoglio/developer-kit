# Knowledge Graph Query Examples

This document provides practical examples of querying the Knowledge Graph for common use cases.

## Query Patterns

### Pattern 1: Find All Components by Type

**Use Case**: Need to know what services exist in the codebase.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ components
Filter: { category: "services" }

Result:
[
  {
    "id": "comp-svc-001",
    "name": "HotelService",
    "location": "src/main/java/.../HotelService.java",
    "methods": [
      { "name": "searchHotels", "returns": "List<HotelDTO>" }
    ],
    "dependencies": ["HotelRepository"]
  },
  {
    "id": "comp-svc-002",
    "name": "BookingService",
    "location": "src/main/java/.../BookingService.java",
    "dependencies": ["BookingRepository", "HotelService"]
  }
]

Usage in task generation:
"Use existing HotelService.searchHotels() method for searching"
```

### Pattern 2: Find Architectural Patterns

**Use Case**: Generate tasks following existing patterns.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ patterns
Filter: { category: "architectural" }

Result:
[
  {
    "id": "pat-001",
    "name": "Repository Pattern",
    "convention": "All repositories extend JpaRepository<EntityType, ID>",
    "examples": [
      {
        "file": "src/main/java/.../HotelRepository.java",
        "line": 8,
        "snippet": "public interface HotelRepository extends JpaRepository<Hotel, Long>"
      }
    ]
  },
  {
    "id": "pat-002",
    "name": "Service Layer Pattern",
    "convention": "Business logic in @Service classes",
    "files": ["src/main/java/**/service/*Service.java"]
  }
]

Usage in task generation:
Generate tasks:
- TASK-001: Create BookingRepository extending JpaRepository
- TASK-002: Create BookingService with @Service annotation
```

### Pattern 3: Find REST Endpoints

**Use Case**: Need to integrate with existing API.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ apis
Filter: { type: "internal" }

Result:
[
  {
    "id": "api-int-001",
    "path": "/api/v1/hotels",
    "method": "GET",
    "controller": "HotelController",
    "parameters": [
      { "name": "city", "type": "String", "required": true }
    ],
    "response": "List<HotelDTO>"
  },
  {
    "id": "api-int-002",
    "path": "/api/v1/hotels/{id}",
    "method": "GET",
    "controller": "HotelController",
    "response": "HotelDTO"
  }
]

Usage in task:
"Integration: Call GET /api/v1/hotels?city={city} to search hotels"
```

### Pattern 4: Validate Component Existence

**Use Case**: Task references a component, verify it exists.

```
Query: /knowledge-graph validate docs/specs/001-hotel-search/
Requirements: {
  components: ["comp-repo-001", "comp-svc-missing"],
  apis: ["api-int-001"]
}

Result:
{
  "valid": false,
  "errors": [
    "Component comp-svc-missing not found in codebase"
  ],
  "warnings": [
    "API api-int-001 not found, may need implementation"
  ]
}

Action: Alert user before implementing task
"Warning: Task references UserService but it doesn't exist. Create first?"
```

### Pattern 5: Find Naming Conventions

**Use Case**: Generate code following project conventions.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ patterns
Filter: { category: "conventions", subcategory: "naming" }

Result:
[
  {
    "id": "conv-001",
    "category": "naming",
    "rule": "Controller classes end with 'Controller'",
    "examples": ["HotelController", "BookingController"]
  },
  {
    "id": "conv-002",
    "category": "naming",
    "rule": "Service classes end with 'Service'",
    "examples": ["HotelService", "BookingService"]
  },
  {
    "id": "conv-003",
    "category": "naming",
    "rule": "Repository interfaces end with 'Repository'",
    "examples": ["HotelRepository", "BookingRepository"]
  }
]

Usage in task:
"Create PaymentService (naming convention: *Service)"
"Create PaymentRepository interface (naming convention: *Repository)"
```

### Pattern 6: Find Integration Points

**Use Case**: Need to know external systems integrated.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ integration-points

Result:
[
  {
    "id": "int-001",
    "name": "Database Integration",
    "type": "database",
    "technology": "PostgreSQL",
    "used_by_components": ["HotelRepository", "BookingRepository"]
  },
  {
    "id": "int-002",
    "name": "Cache Layer",
    "type": "cache",
    "technology": "Redis",
    "purpose": "Cache hotel search results",
    "used_by_components": ["HotelService"]
  }
]

Usage in task:
"Store search results in Redis cache (existing integration)"
"Use PostgreSQL for persistence (existing integration)"
```

### Pattern 7: Find External APIs

**Use Case**: Task needs to call external service.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ apis
Filter: { type: "external" }

Result:
[
  {
    "id": "api-ext-001",
    "name": "Supplier Integration API",
    "base_url": "https://api.supplier.com/v1",
    "authentication": "API Key",
    "endpoints": [
      {
        "method": "POST",
        "path": "/hotels/availability",
        "purpose": "Check real-time availability",
        "used_by": "SupplierService"
      }
    ]
  }
]

Usage in task:
"Use existing SupplierService pattern for payment gateway integration"
"Follow same authentication pattern: API Key in header"
```

## Integration Examples

### Example 1: spec-to-tasks - Load Cached Analysis

```yaml
# Phase 2.5 of spec-to-tasks

Action: Check if knowledge graph exists
Command: /knowledge-graph read docs/specs/001-hotel-search/

If KG exists and recent (< 7 days):
  Present to user:
  "Found cached analysis from 3 days ago:
   - 3 services discovered
   - 2 architectural patterns
   - 5 REST endpoints
   Use cached analysis or re-explore codebase?"

If user chooses cached:
  Query KG for all patterns and components
  Skip Phase 3 (Codebase Analysis)
  Proceed directly to Phase 4 (Task Decomposition)

If user chooses re-explore or KG doesn't exist:
  Proceed to Phase 3 (launch agents)
```

### Example 2: spec-to-tasks - Update After Analysis

```yaml
# Phase 3.5 of spec-to-tasks

Agent completed analysis:
  "Found Repository Pattern: All repositories extend JpaRepository
   Found Service Layer: Business logic in @Service classes
   Components: HotelService, HotelRepository, HotelController"

Action: Update knowledge graph
Command: /knowledge-graph update docs/specs/001-hotel-search/ {
  patterns: {
    architectural: [
      {
        id: "pat-001",
        name: "Repository Pattern",
        convention: "Extend JpaRepository<Entity, ID>"
      },
      {
        id: "pat-002",
        name: "Service Layer",
        convention: "@Service annotation on business logic"
      }
    ]
  },
  components: {
    services: [
      {
        id: "comp-svc-001",
        name": "HotelService",
        location: "src/main/java/.../HotelService.java"
      }
    ],
    repositories: [
      {
        id: "comp-repo-001",
        name": "HotelRepository",
        location: "src/main/java/.../HotelRepository.java"
      }
    ],
    controllers: [
      {
        id: "comp-ctrl-001",
        name": "HotelController",
        location: "src/main/java/.../HotelController.java"
      }
    ]
  }
} "general-software-architect agent"

Result: knowledge-graph.json updated with discoveries
Log: "Knowledge graph updated: 2 patterns, 3 components added"
```

### Example 3: task-implementation - Validate Task

```yaml
# T-3.5 of task-implementation

Task file specifies:
  Technical Context:
    - Use HotelRepository for database access
    - Call HotelService.searchHotels()
    - Follow Repository pattern

Action: Validate against knowledge graph
Command: /knowledge-graph validate docs/specs/001-hotel-search/ {
  components: ["comp-repo-001", "comp-svc-001"],
  patterns: [{ name: "Repository Pattern" }]
}

Result:
{
  valid: true,
  errors: [],
  warnings: []
}

→ Proceed with implementation, all dependencies exist

Alternative if validation fails:
{
  valid: false,
  errors: ["Component comp-svc-001 not found"],
  warnings: []
}

→ Alert user: "HotelService not found in codebase. Create it first or update task?"
```

### Example 4: spec-to-tasks - Enrich Task Generation Context

```yaml
# Phase 2.5 of spec-to-tasks

Spec folder: `docs/specs/001-hotel-search/`

Action: Check if existing spec has KG
Query: /knowledge-graph query docs/specs/001-hotel-search/ all

Result summary:
  "From previous analysis of hotel-search:
   Components: 2 controllers, 3 services, 2 repositories
   Patterns: Repository, Service Layer, DTO
   APIs: 5 endpoints, 1 external integration
   Conventions: Naming, testing with JUnit, Mockito for mocks"

Use this summary to enrich task generation:
  "Found related feature 'hotel-search' with cached analysis.
   Use existing patterns (Repository, Service) for consistency?"

If yes:
  Generate tasks following discovered patterns
  Technical Context: "Follow HotelService pattern for BookingService"

If no:
  Proceed with full codebase exploration
```

## Query Syntax Reference

### Basic Syntax

```
/knowledge-graph [action] [spec-folder] [parameters]

Actions:
  read - Load entire KG
  query - Search KG with filters
  update - Add/merge findings
  validate - Check requirements against KG
```

### Query Parameters

```
Query Types:
  components - Search for code components
  patterns - Search for patterns and conventions
  apis - Search for API endpoints
  integration-points - Search for integrations
  all - Search everything

Filters: JSON object with key-value pairs
  { category: "services" }
  { type: "internal" }
  { name: "Hotel*" }  (wildcard search)
```

### Update Parameters

```
Updates: Partial KG object to merge
  {
    patterns: { architectural: [...] }
  }

Source: Description of what provided updates
  "general-code-explorer agent"
  "Manual update after implementation"
```

## Performance Tips

### 1. Load Once, Query Multiple Times

```
Bad: Load KG for each query
/kg query ... components
/kg query ... patterns
/kg query ... apis

Good: Load KG once, query in-memory
/kg read ...
→ Use cached KG for multiple queries
```

### 2. Use Specific Filters

```
Bad: Query all then filter manually
/kg query ... all
→ Manually filter through 100 components

Good: Query with specific filter
/kg query ... components { category: "services" }
→ Returns only services
```

### 3. Check Freshness First

```
Before using KG:
1. Read metadata.updated_at
2. Calculate age: now - updated_at
3. If > 7 days: Warn user "KG may be stale"
4. Offer to refresh analysis
```

## Error Handling

### File Not Found

```
Query: /knowledge-graph read docs/specs/999-missing/

Result:
{
  error: "Knowledge graph not found",
  message: "No existing knowledge graph at docs/specs/999-missing/knowledge-graph.json",
  action: "Will create new KG on first update"
}

Handling: Continue with empty KG, will be created on update
```

### Invalid JSON

```
Query: /knowledge-graph read docs/specs/001-corrupted/

Result:
{
  error: "Invalid JSON",
  message: "Knowledge graph file is corrupted",
  action: "Offer to recreate from codebase analysis"
}

Handling: Ask user "Recreate KG from codebase analysis?"
```

### Validation Failures

```
Query: /knowledge-graph validate ... { components: ["missing-id"] }

Result:
{
  valid: false,
  errors: ["Component missing-id not found"],
  warnings: [],
  suggestions: [
    "Available components: comp-001, comp-002, comp-003"
  ]
}

Handling: Alert user, suggest available alternatives
```

## Advanced Queries

### Pattern 8: Find Component Dependencies

**Goal**: Find all components that depend on a specific component.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ components
Filter: { depends_on: "HotelRepository" }

Result:
[
  {
    "id": "comp-svc-001",
    "name": "HotelService",
    "dependencies": ["HotelRepository"]
  },
  {
    "id": "comp-svc-002",
    "name": "BookingService",
    "dependencies": ["HotelRepository"]
  }
]

Usage: "If modifying HotelRepository, also update HotelService and BookingService"
```

### Pattern 9: Find Similar Features

**Goal**: Find other features that used similar patterns.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ patterns
Filter: { name: "Repository Pattern" }

Result: Pattern found in hotel-search spec

Then: Search other specs for same pattern
For each spec in docs/specs/*/:
  /knowledge-graph query docs/specs/[ID]/ patterns
  Filter: { name: "Repository Pattern" }

Usage: "See how other features implemented Repository Pattern"
```

### Pattern 10: Trace API Usage

**Goal**: Find which components use a specific API.

```
Query: /knowledge-graph query docs/specs/001-hotel-search/ apis
Filter: { path: "/api/v1/hotels" }

Result: API endpoint found

Then: Find components using it
/kg query ... components
Filter: { uses_apis: ["api-int-001"] }

Usage: "If changing /api/v1/hotels endpoint, update HotelController"
```

## Best Practices

1. **Always check freshness** before using KG for critical decisions
2. **Validate requirements** against KG before implementation
3. **Query specific sections** rather than loading entire KG
4. **Update KG incrementally** after each analysis, not in one batch
5. **Log all KG operations** for debugging and audit trail

## Troubleshooting

### KG Returns Empty Results

**Cause**: KG not yet populated or query too specific

**Solution**:
1. Check if KG exists: `/knowledge-graph read [spec-folder]`
2. If empty, run codebase analysis first
3. If query-specific, try broader filter

### Validation Shows False Positives

**Cause**: KG out of sync with actual codebase

**Solution**:
1. Check KG age: `metadata.updated_at`
2. If > 7 days old, refresh with agent analysis
3. After code changes, update KG

### KG Too Large

**Cause**: Accumulated too much data over time

**Solution**:
1. Archive old KG versions
2. Split by feature area
3. Remove outdated/discovered components
