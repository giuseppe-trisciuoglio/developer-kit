# Error Handling - Knowledge Graph

Comprehensive error handling strategies and behaviors for Knowledge Graph operations.

## Error Types

### 1. File Not Found

**Scenario:** KG file doesn't exist at expected path.

**Behavior:**
- Return empty KG structure
- Message: "No existing knowledge graph, will create new"
- Action: Continue with empty KG, will be created on first update

**Empty KG Structure:**
```json
{
  "metadata": {
    "spec_id": null,
    "feature_name": null,
    "created_at": null,
    "updated_at": null,
    "version": "1.0",
    "analysis_sources": []
  },
  "codebase_context": {
    "project_structure": {},
    "technology_stack": []
  },
  "patterns": {
    "architectural": [],
    "conventions": []
  },
  "components": {
    "controllers": [],
    "services": [],
    "repositories": [],
    "entities": [],
    "dtos": []
  },
  "provides": [],
  "apis": {
    "internal": [],
    "external": []
  },
  "integration_points": []
}
```

**When this occurs:**
- First time running spec-to-tasks for a spec
- KG was deleted
- Incorrect path provided

**User impact:** None (normal operation)

---

### 2. Invalid JSON

**Scenario:** KG file exists but contains invalid JSON.

**Behavior:**
- Raise error
- Message: "Knowledge graph corrupted at {path}"
- Action: Ask user: "Recreate from codebase analysis?"

**Detection:**
```python
try:
    kg_data = json.load(kg_file)
except json.JSONDecodeError as e:
    raise KnowledgeGraphError(
        f"Knowledge graph corrupted at {path}: {str(e)}"
    )
```

**Recovery options:**
1. Recreate from codebase analysis
2. Restore from backup (if available)
3. Manual repair (advanced users)

**User impact:** High (cannot use existing KG)

---

### 3. Merge Conflicts

**Scenario:** Concurrent updates to KG cause merge conflicts.

**Behavior:**
- Preserve existing values, add new with timestamps
- Message: "Merged X new findings into existing knowledge graph"

**Merge Strategy:**
- **Arrays**: Append new items (check for duplicates by ID)
- **Objects**: Deep merge, preserve existing keys
- **Metadata**: Always update timestamps and sources

**Example merge:**
```python
def merge_kg(existing, updates):
    # Arrays: append if not duplicate
    for key in ['patterns', 'components', 'apis']:
        for item in updates[key]:
            if item not in existing[key]:
                existing[key].append(item)

    # Objects: deep merge
    for key in ['codebase_context']:
        existing[key].update(updates[key])

    # Metadata: always update
    existing['metadata']['updated_at'] = datetime.now().isoformat()

    return existing
```

**Detection:**
- Duplicate IDs in arrays
- Conflicting values for same key

**Prevention:**
- Use atomic file writes
- Add source tracking to updates
- Use optimistic locking

---

### 4. Write Failure

**Scenario:** Cannot write KG file (permissions, disk full, etc.).

**Behavior:**
- Log error, continue without caching
- Message: "Cannot write knowledge graph, continuing without cache"

**Detection:**
```python
try:
    with open(kg_path, 'w') as f:
        json.dump(kg_data, f, indent=2)
except (IOError, OSError) as e:
    logger.error(f"Cannot write knowledge graph: {str(e)}")
    # Continue without caching
    return None
```

**Impact:**
- No caching benefits
- Must re-explore codebase next time
- Performance degradation

**Recovery:**
- Fix permissions
- Free disk space
- Retry write operation

---

### 5. Path Validation Errors

**Scenario:** Invalid path provided for KG operations.

**Behavior:**
- Raise error
- Message: "Invalid knowledge graph path: {path}"

**Validation rules:**
- Path must start with `docs/specs/`
- Path must not contain `..` (parent directory)
- Path must be within project root

**Example:**
```python
def validate_kg_path(path):
    # Must start with docs/specs/
    if not path.startswith("docs/specs/"):
        raise ValueError(f"Invalid KG path: {path}")

    # No path traversal
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")

    # Must resolve within project
    real_path = Path(path).resolve()
    project_root = Path.cwd()
    if not str(real_path).startswith(str(project_root)):
        raise ValueError(f"Path outside project: {path}")

    return real_path
```

---

### 6. Validation Errors

**Scenario:** Validation requirements reference non-existent components.

**Behavior:**
- Return validation report with errors
- Message: "Validation failed: {errors}"

**Error types:**
- Component missing (Error)
- API missing (Warning)
- Pattern mismatch (Warning)
- Convention violation (Warning)

**Example:**
```json
{
  "errors": [
    "Component comp-svc-missing not found in codebase"
  ],
  "warnings": [
    "API api-int-001 not found, may need implementation"
  ],
  "valid": false
}
```

**Recovery:**
- Implement missing components
- Update requirements to match existing code
- Update KG with new components after implementation

---

### 7. Contract Validation Errors

**Scenario:** Expected symbols not found in completed dependencies.

**Behavior:**
- Return validation report with unsatisfied expectations
- Message: "Contract validation failed: N unsatisfied expectations"

**Example:**
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

**Recovery:**
- Implement missing provides in current task
- Reorder tasks to satisfy dependencies
- Update expectations to match actual provides

---

### 8. Extraction Errors

**Scenario:** Cannot extract symbols from source files.

**Behavior:**
- Log warning, continue with partial extraction
- Message: "Could not extract symbols from {file}: {error}"

**Causes:**
- Unsupported file type
- Parse errors (malformed code)
- File permission issues

**Example:**
```python
try:
    symbols = extract_symbols_from_file(file_path)
except ParseError as e:
    logger.warning(f"Could not extract symbols from {file_path}: {e}")
    symbols = []
```

**Impact:**
- Incomplete provides extraction
- May miss dependencies
- Manual intervention may be needed

---

## Error Recovery Strategies

### Retry Logic

**When to retry:**
- Transient failures (network, file locks)
- Write failures
- Temporary permission issues

**Retry configuration:**
```python
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

def retry_on_failure(func):
    for attempt in range(MAX_RETRIES):
        try:
            return func()
        except TransientError as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff
```

### Fallback Behavior

**When KG is unavailable:**
1. Log warning
2. Continue without caching
3. Inform user of degraded performance
4. Offer to recreate KG

**Example:**
```
⚠️  Warning: Knowledge graph unavailable
Continuing without caching (performance may be degraded)
Would you like to recreate the knowledge graph from codebase analysis?
```

### Graceful Degradation

**Principle:** Fail gracefully, don't block workflow.

**Examples:**
- Context7 unavailable → Use codebase patterns
- KG stale → Warn user, continue with verification
- Validation fails → Report errors, don't stop workflow
- Write fails → Continue without caching

---

## Error Messages

### User-Friendly Messages

| Error | Message | Action |
|-------|---------|--------|
| File not found | "No existing knowledge graph, will create new" | Continue (normal) |
| Invalid JSON | "Knowledge graph corrupted at {path}. Recreate from codebase?" | Ask user |
| Write failed | "Cannot write knowledge graph, continuing without cache" | Log and continue |
| Invalid path | "Invalid knowledge graph path: {path}" | Raise error |
| Validation failed | "Validation failed: N errors, M warnings" | Report and continue |
| Contract failed | "N unsatisfied expectations" | Report and continue |
| Extraction failed | "Could not extract symbols from {file}" | Log warning |

### Error Severity Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| **Info** | Normal operation | "Created new knowledge graph" |
| **Warning** | Non-critical issue | "Knowledge graph is stale (30 days old)" |
| **Error** | Operation failed | "Cannot write knowledge graph" |
| **Critical** | System broken | "Knowledge graph corrupted beyond repair" |

---

## Logging Strategy

### What to Log

**Always log:**
- All errors with context
- File operations (read, write, update)
- Validation results
- Merge operations

**Sometimes log:**
- Debug info in verbose mode
- Performance metrics
- Cache hit/miss ratios

**Never log:**
- Sensitive data (shouldn't be in KG anyway)
- User credentials
- Internal system details

### Log Format

```python
logger.info(f"Knowledge graph operation: {operation} on {path}")
logger.warning(f"Stale knowledge graph: {days} days old")
logger.error(f"Failed to write KG: {error}", exc_info=True)
logger.debug(f"KG validation result: {validation}")
```

---

## Error Prevention

### Input Validation

**Validate paths:**
- Must start with `docs/specs/`
- No path traversal (`..`)
- Within project root

**Validate data:**
- JSON structure valid
- Required fields present
- Data types correct
- Arrays don't have duplicates

**Validate operations:**
- User has read permissions
- User has write permissions (for updates)
- Disk space available

### Atomic Operations

**File writes:**
- Write to temporary file first
- Rename to actual path (atomic on Unix)
- Cleanup temp files on failure

**Example:**
```python
import tempfile
import os

def atomic_write(path, data):
    # Write to temp file
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(path)
    )
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(data, f, indent=2)
        # Atomic rename
        os.replace(temp_path, path)
    except:
        # Cleanup on failure
        os.unlink(temp_path)
        raise
```

### Idempotent Operations

**Design operations to be idempotent:**
- Running update twice should not duplicate data
- Reading non-existent file returns empty KG (not error)
- Validation can be run multiple times safely

**Example:**
```python
def update_kg(path, updates):
    kg = read_kg(path)  # Returns empty KG if not exists
    merged = merge(kg, updates)  # Idempotent merge
    write_kg(path, merged)
```

---

## Error Handling Best Practices

### 1. Fail Fast, Fail Gracefully

- Detect errors early (input validation)
- Provide clear error messages
- Offer recovery options
- Don't crash the workflow

### 2. Log Context

- Always include context in error messages
- Log what operation was attempted
- Log what input was provided
- Log system state if relevant

### 3. Provide Recovery Options

- For transient errors: retry
- For user errors: provide guidance
- For system errors: offer workaround
- For data errors: suggest repair

### 4. Preserve Data

- Never lose existing data on error
- Use atomic writes
- Create backups before destructive operations
- Validate before overwriting

### 5. Inform User

- Always inform user of errors
- Explain impact of error
- Suggest next steps
- Don't hide errors silently

---

## Testing Error Handling

### Test Cases

1. **File not found**: Read non-existent KG → Returns empty KG
2. **Invalid JSON**: Read corrupted KG → Raises error
3. **Write failure**: Mock write failure → Continues without caching
4. **Invalid path**: Provide `../../etc/passwd` → Raises error
5. **Validation failure**: Validate missing components → Returns errors
6. **Concurrent updates**: Simulate merge conflict → Merges correctly

### Error Injection

```python
def test_write_failure():
    # Mock file write to fail
    with mock.patch('builtins.open', side_effect=IOError):
        result = write_kg(path, data)
        # Should return None, not raise
        assert result is None
```

---

## Summary

**Error handling principles:**
1. Validate inputs early
2. Provide clear error messages
3. Fail gracefully, don't block workflow
4. Offer recovery options
5. Log all errors with context
6. Use atomic operations
7. Preserve user data
8. Inform user of all errors

**Key behaviors:**
- File not found → Return empty KG (normal)
- Invalid JSON → Raise error, offer recovery
- Write failure → Log and continue
- Merge conflict → Deep merge, preserve both
- Validation failure → Report errors, continue
- Contract failure → Report unsatisfied expectations
