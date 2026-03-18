# Performance Considerations - Knowledge Graph

Optimization strategies and performance characteristics for Knowledge Graph operations.

## Performance Characteristics

### Read Operations (read-knowledge-graph, query-knowledge-graph)

**Time Complexity:**
- JSON parsing: O(n) where n = file size
- Query filtering: O(m) where m = number of items in section
- Overall: O(n + m)

**Typical Performance:**
| KG Size | Read Time | Query Time |
|---------|-----------|------------|
| < 100 KB | < 10ms | < 5ms |
| 100-500 KB | 10-50ms | 5-20ms |
| 500 KB - 1 MB | 50-200ms | 20-100ms |
| > 1 MB | > 200ms | > 100ms |

**Optimization:**
- Cache parsed JSON in memory for session
- Use streaming JSON parser for large files
- Index frequently queried fields

---

### Write Operations (update-knowledge-graph)

**Time Complexity:**
- Read existing KG: O(n)
- Deep merge: O(m) where m = size of updates
- JSON serialization: O(n + m)
- File write: O(n + m)
- Overall: O(n + m)

**Typical Performance:**
| Update Size | Write Time |
|-------------|------------|
| < 10 KB | < 50ms |
| 10-50 KB | 50-200ms |
| 50-100 KB | 200-500ms |
| > 100 KB | > 500ms |

**Optimization:**
- Use atomic writes (temp file + rename)
- Compress JSON if very large
- Batch updates when possible

---

### Validation Operations (validate-against-knowledge-graph, validate-contract)

**Time Complexity:**
- Load KG: O(n)
- Check components: O(c) where c = components to check
- Check APIs: O(a) where a = APIs to check
- File system checks: O(f) where f = files to verify
- Overall: O(n + c + a + f)

**Typical Performance:**
| Validation Type | Time |
|-----------------|------|
| Component validation (10 items) | < 20ms |
| API validation (5 items) | < 15ms |
| Contract validation (5 files) | < 100ms |
| Full validation (100 items) | < 500ms |

**Optimization:**
- Batch file system checks
- Use glob patterns for file checks
- Cache file existence checks

---

### Extraction Operations (extract-provides)

**Time Complexity:**
- Read files: O(f) where f = number of files
- Parse files: O(s) where s = total file size
- Extract symbols: O(s)
- Overall: O(f + s)

**Typical Performance:**
| Files | Total Size | Time |
|-------|------------|------|
| 1-5 files | < 100 KB | < 100ms |
| 5-20 files | 100-500 KB | 100-500ms |
| 20-50 files | 500 KB - 1 MB | 500ms-2s |
| > 50 files | > 1 MB | > 2s |

**Optimization:**
- Parallel file reading
- Use language-specific parsers (not regex)
- Cache extraction results

---

## Optimization Strategies

### 1. Lazy Loading

**Strategy:** Only load KG when explicitly requested.

**Implementation:**
- Don't auto-load KG on skill invocation
- Load only when `read-knowledge-graph` called
- Close file handle immediately after reading

**Benefit:** Reduces memory usage and I/O for operations that don't need KG.

**Example:**
```python
# Bad: Load KG on skill init
class KnowledgeGraphSkill:
    def __init__(self):
        self.kg = self.load_kg()  # Always loads

# Good: Load on demand
class KnowledgeGraphSkill:
    def read(self, path):
        return self.load_kg(path)  # Only loads when called
```

---

### 2. Incremental Updates

**Strategy:** Merge changes, don't rewrite entire file.

**Implementation:**
- Use deep merge for updates
- Only write changed sections
- Track what changed

**Benefit:** Reduces I/O for small updates.

**Example:**
```python
# Bad: Replace entire KG
def update(path, updates):
    kg = {"metadata": {}, ...}  # New empty KG
    kg.update(updates)  # Only updates
    write(path, kg)  # Writes everything

# Good: Merge into existing
def update(path, updates):
    kg = read(path)  # Read existing
    merged = deep_merge(kg, updates)  # Merge
    write(path, merged)  # Write merged
```

---

### 3. Cache Invalidation

**Strategy:** Check timestamp, re-explore if KG is stale.

**Freshness thresholds:**
- **< 7 days**: Consider KG fresh, use cached analysis
- **7-30 days**: KG getting stale, warn user
- **> 30 days**: KG very stale, offer to regenerate

**Implementation:**
```python
def is_kg_fresh(kg_path):
    kg = read_kg(kg_path)
    if not kg['metadata']['updated_at']:
        return False

    updated = datetime.fromisoformat(kg['metadata']['updated_at'])
    age = (datetime.now() - updated).days

    if age < 7:
        return True  # Fresh
    elif age < 30:
        logger.warning(f"KG is {age} days old, consider updating")
        return True  # Still usable
    else:
        logger.error(f"KG is very stale ({age} days)")
        return False  # Should regenerate
```

**Benefit:** Prevents using outdated analysis.

---

### 4. File Size Monitoring

**Strategy:** Monitor KG size, split if too large.

**Thresholds:**
- **< 500 KB**: Normal size, no action needed
- **500 KB - 1 MB**: Consider optimization
- **> 1 MB**: Should split by feature area

**Implementation:**
```python
def check_kg_size(kg_path):
    size_kb = os.path.getsize(kg_path) / 1024

    if size_kb > 1024:  # > 1 MB
        logger.warning(f"KG is large ({size_kb:.0f} KB), consider splitting")
        return False

    return True
```

**Splitting strategy:**
- Split by feature area
- Create sub-KGs for each area
- Use aggregation for cross-feature queries

---

### 5. Memory Management

**Strategy:** Don't keep KG in memory when not needed.

**Implementation:**
- Load KG, process, unload
- Don't cache between operations
- Use streaming for large files

**Example:**
```python
# Bad: Keep KG in memory
class KnowledgeGraphSkill:
    def __init__(self):
        self.cached_kg = None

    def get_kg(self, path):
        if not self.cached_kg:
            self.cached_kg = load(path)
        return self.cached_kg

# Good: Load on demand, don't cache
class KnowledgeGraphSkill:
    def get_kg(self, path):
        return load(path)  # Always fresh
```

---

### 6. Parallel Processing

**Strategy:** Use parallel operations for independent tasks.

**Use cases:**
- Extract provides from multiple files
- Validate multiple components
- Aggregate multiple KGs

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor

def extract_provides_parallel(files):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(extract_provides, files)
    return list(results)
```

**Benefit:** Reduces wall-clock time for multi-file operations.

---

## Performance Monitoring

### Metrics to Track

| Metric | How to Measure | Target |
|--------|---------------|--------|
| Read latency | Time from request to parsed KG | < 100ms |
| Write latency | Time from update to disk write | < 500ms |
| Query latency | Time for filtered query | < 50ms |
| Validation time | Time for full validation | < 1s |
| File size | KB on disk | < 1000 KB |
| Cache hit rate | Queries served from cache | > 80% |

### Monitoring Implementation

```python
import time
from functools import wraps

def timed(operation):
    @wraps(operation)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = operation(*args, **kwargs)
        elapsed = (time.time() - start) * 1000  # ms
        logger.info(f"{operation.__name__} took {elapsed:.0f}ms")
        return result
    return wrapper

@timed
def read_knowledge_graph(path):
    # ... implementation
    pass
```

---

## Performance Best Practices

### 1. Choose the Right Operation

| Need | Best Operation |
|------|----------------|
| Get everything | `read-knowledge-graph` |
| Get specific items | `query-knowledge-graph` |
| Add findings | `update-knowledge-graph` |
| Check dependencies | `validate-against-knowledge-graph` |
| Get what code provides | `extract-provides` |

### 2. Batch Operations

**Bad:**
```python
for component in components:
    kg = query_kg(path, "components", component)  # N reads
```

**Good:**
```python
kg = read_kg(path)  # 1 read
for component in components:
    result = find_in_kg(kg, component)  # Memory lookup
```

### 3. Use Appropriate Granularity

**Too coarse:** Read entire KG for one component (slow)
**Too fine:** Query KG 100 times for 100 components (slow)
**Just right:** Read KG once, filter in memory

### 4. Optimize File I/O

- Use buffered I/O
- Minimize file system calls
- Use atomic writes
- Cache file reads when appropriate

### 5. Profile Before Optimizing

**Don't guess, measure:**
```python
import cProfile

def profile_operation():
    cProfile.run('knowledge_graph.update(path, data)')
```

---

## Performance Anti-Patterns

### ❌ Reading KG Multiple Times

```python
# Bad: Read KG in a loop
for component in components:
    kg = read_kg(path)  # N reads
    process(kg, component)
```

### ✅ Read Once, Process Many

```python
# Good: Read once, process many
kg = read_kg(path)  # 1 read
for component in components:
    process(kg, component)  # Memory operations
```

---

### ❌ Writing KG on Every Change

```python
# Bad: Write after every small update
for item in items:
    update_kg(path, item)  # N writes
```

### ✅ Batch Updates

```python
# Good: Collect updates, write once
updates = collect_updates(items)
update_kg(path, updates)  # 1 write
```

---

### ❌ Not Caching File Checks

```python
# Bad: Check file existence every time
def validate(file_path):
    if not os.path.exists(file_path):  # System call
        raise Error(f"File not found: {file_path}")
```

### ✌ Cache File Checks

```python
# Good: Cache existence checks
_file_cache = {}

def validate(file_path):
    if file_path not in _file_cache:
        _file_cache[file_path] = os.path.exists(file_path)
    if not _file_cache[file_path]:
        raise Error(f"File not found: {file_path}")
```

---

## Scaling Considerations

### When KG Grows Large

**Symptoms:**
- Read/write operations > 1s
- Memory usage high
- File size > 1 MB

**Solutions:**
1. **Split by feature**: Create separate KGs per feature area
2. **Compress data**: Use JSON compression
3. **Use database**: Move to SQLite/PostgreSQL
4. **Incremental loading**: Load only needed sections

### Splitting Strategy

```python
# Instead of one large KG:
docs/specs/001-feature/knowledge-graph.json  # 2 MB

# Split into feature-specific KGs:
docs/specs/001-feature/kg-auth.json        # 300 KB
docs/specs/001-feature/kg-database.json    # 400 KB
docs/specs/001-feature/kg-api.json         # 500 KB
```

### Aggregation for Cross-Feature Queries

Use `aggregate-knowledge-graphs` to create project-wide summary:

```python
# Creates: docs/specs/.global-knowledge-graph.json
# Contains: Patterns and conventions from all specs
# Updates: Run periodically (daily/weekly)
```

---

## Performance Testing

### Test Cases

1. **Cold read**: Read KG from disk (not cached)
2. **Warm read**: Read KG from memory cache
3. **Small update**: Update < 10 items
4. **Large update**: Update > 100 items
5. **Query**: Filter 1000 items to 10
6. **Validate**: Check 100 components
7. **Extract**: Parse 50 files

### Performance Benchmarks

**Target performance:**
- Read: < 100ms
- Write: < 500ms
- Query: < 50ms
- Validate: < 1s
- Extract: < 2s (50 files)

---

## Summary

**Key performance principles:**
1. Lazy load KG (don't auto-load)
2. Incremental updates (merge, don't replace)
3. Cache invalidation (check freshness)
4. Monitor file size (split if > 1 MB)
5. Memory management (don't keep in memory)
6. Parallel processing (for independent tasks)
7. Batch operations (reduce I/O)
8. Profile before optimizing

**Performance targets:**
- Read: < 100ms
- Write: < 500ms
- Query: < 50ms
- Validate: < 1s
- Extract: < 2s (50 files)
- File size: < 1 MB

**When to optimize:**
- Operations exceed targets
- KG size > 1 MB
- User reports slowness
- Memory usage high
