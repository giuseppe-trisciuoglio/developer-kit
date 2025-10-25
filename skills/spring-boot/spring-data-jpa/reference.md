# Spring Data JPA - Reference Documentation

## Repository Inheritance Hierarchy

```
Repository
├── CrudRepository
│   ├── PagingAndSortingRepository
│   │   └── JpaRepository
│   └── ListCrudRepository (Spring Data 3)
└── reactive variants
```

## CrudRepository API

Core CRUD operations for all repositories.

```java
public interface CrudRepository<T, ID extends Serializable> extends Repository<T, ID> {
    // CREATE/UPDATE
    <S extends T> S save(S entity);
    <S extends T> Iterable<S> saveAll(Iterable<S> entities);
    
    // READ
    Optional<T> findById(ID id);
    T getById(ID id);  // Always returns proxy, never null
    T getReferenceById(ID id);  // Like getById
    boolean existsById(ID id);
    Iterable<T> findAll();
    Iterable<T> findAllById(Iterable<ID> ids);
    
    // AGGREGATE
    long count();
    
    // DELETE
    void deleteById(ID id);
    void delete(T entity);
    void deleteAllById(Iterable<? extends ID> ids);
    void deleteAll(Iterable<? extends T> entities);
    void deleteAll();
}
```

## PagingAndSortingRepository API

Adds pagination and sorting capabilities.

```java
public interface PagingAndSortingRepository<T, ID extends Serializable>
    extends CrudRepository<T, ID> {
    
    Iterable<T> findAll(Sort sort);
    Page<T> findAll(Pageable pageable);
}
```

## JpaRepository API

JPA-specific operations including batch operations and flushing.

```java
public interface JpaRepository<T, ID extends Serializable>
    extends PagingAndSortingRepository<T, ID> {
    
    // Batch operations
    <S extends T> List<S> saveAll(Iterable<S> entities);
    List<T> findAll();
    List<T> findAllById(Iterable<ID> ids);
    <S extends T> List<S> saveAll(Iterable<S> entities);
    
    // Batch delete
    void deleteInBatch(Iterable<T> entities);
    void deleteAllInBatch(Iterable<ID> ids);
    void deleteAllInBatch();
    
    // Flush
    void flush();
    
    // Save and flush
    <S extends T> S saveAndFlush(S entity);
    <S extends T> List<S> saveAllAndFlush(Iterable<S> entities);
}
```

## Query Annotation

Execute custom queries at repository level.

```java
@Query(value = "...", nativeQuery = false)
// value: JPQL or SQL string
// nativeQuery: true for SQL, false (default) for JPQL
// countQuery: for pagination count query
// name: reference named query
// readOnly: optimization hint
```

## Modifying Annotation

Mark operations that modify data (INSERT, UPDATE, DELETE).

```java
@Modifying(flushAutomatically = false, clearAutomatically = false)
// flushAutomatically: flush changes before executing
// clearAutomatically: clear persistence context after executing
// Both typically used with @Transactional
```

## JPA Mapping Annotations

### Entity & Inheritance

| Annotation | Purpose |
|-----------|---------|
| `@Entity` | Mark class as JPA entity |
| `@Table(name=, schema=, ...)` | Specify table name and schema |
| `@Inheritance(strategy=)` | Define inheritance mapping (SINGLE_TABLE, TABLE_PER_CLASS, JOINED) |
| `@DiscriminatorColumn` | Column for discriminating entity type |
| `@DiscriminatorValue` | Value for discriminator column |
| `@MappedSuperclass` | Base class with shared attributes |

### Identifiers

| Annotation | Purpose |
|-----------|---------|
| `@Id` | Mark as primary key |
| `@GeneratedValue(strategy=, generator=)` | Auto-generate ID (AUTO, IDENTITY, SEQUENCE, TABLE, UUID) |
| `@SequenceGenerator` | Define sequence for ID generation |
| `@TableGenerator` | Define table-based ID generation |
| `@GenericGenerator` | Hibernate generic generator (deprecated in favor of specific annotations) |
| `@UuidGenerator(style=)` | Hibernate UUID generation (RANDOM for v4, TIME for v1, AUTO=RANDOM) |
| `@Version` | Optimistic locking version field |
| `@EmbeddedId` | Use composite key as embedded object |
| `@IdClass` | Use annotation on composite key fields |

### Columns & Properties

| Annotation | Purpose |
|-----------|---------|
| `@Column(name=, nullable=, length=, unique=, precision=, scale=, ...)` | Map to column |
| `@Index(name=, columnList=, unique=)` | Define database index for performance |
| `@Basic(fetch=, optional=)` | Basic value mapping |
| `@Transient` | Exclude from persistence |
| `@Lob` | Large object (BLOB/CLOB) |
| `@Temporal(TemporalType.DATE/TIME/TIMESTAMP)` | Map java.util.Date |
| `@Enumerated(EnumType.STRING/ORDINAL)` | Map enum values |
| `@Convert` | Use AttributeConverter for custom types |
| `@Formula` | Computed column using SQL expression |

### Relationships

| Annotation | Purpose |
|-----------|---------|
| `@OneToOne(fetch=, cascade=, optional=, mappedBy=, orphanRemoval=)` | One-to-one relationship |
| `@OneToMany(fetch=, cascade=, mappedBy=, orphanRemoval=)` | One-to-many relationship |
| `@ManyToOne(fetch=, cascade=, optional=)` | Many-to-one relationship |
| `@ManyToMany(fetch=, cascade=, mappedBy=)` | Many-to-many relationship |
| `@JoinColumn(name=, referencedColumnName=, nullable=, ...)` | Foreign key column |
| `@JoinTable(name=, joinColumns=, inverseJoinColumns=)` | Join table for many-to-many |
| `@JoinColumns` | Multiple join columns for composite foreign key |

### Cascading

| CascadeType | Effect |
|-----------|---------|
| `PERSIST` | Cascade save/persist operations |
| `MERGE` | Cascade merge operations |
| `REMOVE` | Cascade delete operations |
| `REFRESH` | Cascade refresh operations |
| `DETACH` | Cascade detach operations |
| `ALL` | Cascade all operations |

### Fetch Strategies

| FetchType | Behavior |
|----------|----------|
| `EAGER` | Load immediately with parent (default for `@ManyToOne`, `@OneToOne`) |
| `LAZY` | Load on access (default for `@OneToMany`, `@ManyToMany`) |

### Embedded Objects

```java
@Entity
public class Address {
    @Embedded
    private Location location;
}

@Embeddable
public class Location {
    private BigDecimal latitude;
    private BigDecimal longitude;
}
```

## Derived Query Keywords

Spring Data automatically interprets method names to generate queries.

### Comparison Operators

| Keyword | SQL Equivalent |
|---------|---|
| `Is`, `Equals` | `=` |
| `IsNot`, `Not` | `!=` |
| `IsGreaterThan`, `GreaterThan` | `>` |
| `IsGreaterThanEqual`, `GreaterThanEqual` | `>=` |
| `IsLessThan`, `LessThan` | `<` |
| `IsLessThanEqual`, `LessThanEqual` | `<=` |
| `Between` | `BETWEEN` |

### String Operations

| Keyword | SQL Equivalent |
|---------|---|
| `Contains` | `LIKE '%...%'` |
| `StartingWith` | `LIKE '...%'` |
| `EndingWith` | `LIKE '%...'` |
| `Like` | `LIKE` |
| `IsNull` | `IS NULL` |
| `IsNotNull` | `IS NOT NULL` |
| `IgnoreCase` | Case-insensitive matching |

### Logical Operators

| Keyword | Meaning |
|---------|---------|
| `And` | Logical AND |
| `Or` | Logical OR |

### Collection

| Keyword | Purpose |
|---------|---------|
| `In` | `IN (...)` |
| `NotIn` | `NOT IN (...)` |

### Results

| Keyword | Effect |
|---------|--------|
| `OrderBy` | Add `ORDER BY` clause |
| `First` | Limit to first N results |
| `Top` | Limit to top N results |
| `Distinct` | Add `DISTINCT` |

## Sort & Pageable

### Sort

```java
// Single sort
Sort sort = Sort.by("name").ascending();
Sort sort = Sort.by(Sort.Direction.DESC, "name");

// Multiple criteria
Sort sort = Sort.by("name").ascending()
    .and(Sort.by("createdDate").descending());

// With case-insensitive
Sort sort = Sort.by(
    Order.asc("name").ignoreCase(),
    Order.desc("createdDate")
);
```

### Pageable

```java
// Page with sort
Pageable pageable = PageRequest.of(0, 10, Sort.by("name"));

// Multiple sort
Pageable pageable = PageRequest.of(0, 10,
    Sort.by("name").ascending()
        .and(Sort.by("id").descending())
);

// Get next/previous
Pageable nextPage = pageable.next();
Pageable previousPage = pageable.previousOrFirst();
```

## Return Types

### Single Result

| Type | Behavior |
|------|----------|
| `T` | Return entity or throw exception if not found |
| `Optional<T>` | Return empty Optional if not found |
| `T getById(ID)` | Return proxy (no DB query initially) |

### Multiple Results

| Type | Behavior |
|------|----------|
| `List<T>` | Ordered collection |
| `Iterable<T>` | Unordered collection |
| `Set<T>` | Unordered unique collection |
| `Slice<T>` | Lightweight pagination (no total count) |
| `Page<T>` | Full pagination with total elements |
| `Stream<T>` | Lazy stream for memory efficiency |

## JPQL Syntax

### Basic Query Structure

```jpql
SELECT [DISTINCT] e FROM Entity e
[WHERE conditions]
[GROUP BY properties]
[HAVING group_conditions]
[ORDER BY properties]
```

### Common Functions

```jpql
-- String functions
UPPER(e.name), LOWER(e.name), LENGTH(e.name)
SUBSTRING(e.name, 1, 3), CONCAT(e.firstName, ' ', e.lastName)
TRIM(e.name), LTRIM(e.name), RTRIM(e.name)

-- Arithmetic
ABS(e.salary), MOD(e.salary, 1000)

-- Date functions
CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP
YEAR(e.birthDate), MONTH(e.birthDate), DAY(e.birthDate)

-- Collection functions
SIZE(e.items), INDEX(e)

-- Conditional
CASE WHEN ... THEN ... ELSE ... END
COALESCE(e.nickname, e.name)
NULLIF(e.salary, 0)
```

### Joins

```jpql
-- Inner join (implicit)
SELECT o FROM Order o WHERE o.customer.id = :id

-- Explicit join
SELECT DISTINCT o FROM Order o INNER JOIN o.items i

-- Left outer join
SELECT o FROM Order o LEFT JOIN o.items i

-- Join fetch (eager loading)
SELECT DISTINCT o FROM Order o JOIN FETCH o.items

-- Multiple joins
SELECT o FROM Order o 
JOIN FETCH o.items i 
JOIN FETCH o.customer c
```

### Subqueries

```jpql
SELECT o FROM Order o 
WHERE o.totalPrice > (SELECT AVG(o2.totalPrice) FROM Order o2)

SELECT c FROM Customer c 
WHERE c.id IN (SELECT DISTINCT o.customer.id FROM Order o WHERE o.status = 'COMPLETED')
```

## Configuration Properties

```properties
# Hibernate dialect
spring.jpa.database-platform=org.hibernate.dialect.MySQL8Dialect
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQL10Dialect

# DDL generation
spring.jpa.hibernate.ddl-auto=validate|update|create|create-drop

# Show SQL
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.properties.hibernate.use_sql_comments=true

# Batch processing
spring.jpa.properties.hibernate.jdbc.batch_size=20
spring.jpa.properties.hibernate.jdbc.fetch_size=50
spring.jpa.properties.hibernate.jdbc.batch_versioned_data=true
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true

# Connection pooling
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000

# Query timeout
spring.jpa.properties.hibernate.jdbc.query_timeout=60

# Lazy loading
spring.jpa.properties.hibernate.enable_lazy_load_no_trans=true

# Performance hints
spring.jpa.properties.hibernate.use_transactional_write_scope=true
spring.jpa.properties.hibernate.generate_statistics=true
```

## Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `EntityNotFoundException` | Entity not found | Use `Optional` and check presence |
| `DataIntegrityViolationException` | Constraint violation | Validate data before saving |
| `PersistenceException` | JPA operation error | Check entity mapping and queries |
| `OptimisticLockingFailureException` | Version conflict | Retry or reload entity |
| `LazyInitializationException` | Lazy collection accessed outside session | Use eager loading or JOIN FETCH |
| `PropertyValueException` | Non-nullable property is null | Initialize all required fields |
| `QueryTimeoutException` | Query execution timeout | Optimize query or increase timeout |

## Performance Tips

1. **Use pagination** - Load data in chunks, not all at once
2. **Eager fetch relationships** - Use `JOIN FETCH` or `@EntityGraph` to avoid N+1 queries
3. **Use projections** - Select only needed columns instead of full entities
4. **Batch operations** - Use `saveAll()`, `deleteInBatch()` for better performance
5. **Index columns** - Add indexes on frequently searched columns
6. **Use read-only transactions** - Set `@Transactional(readOnly = true)` for queries
7. **Avoid lazy loading in loops** - Initialize collections before returning to client
8. **Use second-level cache** - Cache frequently accessed entities
9. **Monitor N+1 queries** - Enable `hibernate.generate_statistics`
10. **Use native queries for complex reports** - JPQL may not generate optimal SQL

## UUID Primary Key Strategies

| Strategy | Pros | Cons | Use When |
|----------|------|------|----------|
| `GenerationType.IDENTITY` | Simple, sequential IDs | Not ideal for distributed systems | Single database, URL-friendly IDs |
| `GenerationType.UUID` | Globally unique, distributed-safe | Larger ID size, clustering impact | Microservices, distributed systems |
| `GenerationType.SEQUENCE` | Good performance, portable | Database dependency | Oracle, PostgreSQL preferred |
| `@UuidGenerator(RANDOM)` | UUID v4, truly random | Same size as UUID | High-volume concurrent inserts |
| `@UuidGenerator(TIME)` | UUID v1, time-ordered, better clustering | Timestamp-based | Time-ordered requirements |

## Index Best Practices

| Scenario | Index Type | Example |
|----------|-----------|---------|
| **Search/Filter** | Single column | `@Index(name = "idx_status", columnList = "status")` |
| **Range queries** | Ordered single column | `@Index(name = "idx_created_desc", columnList = "created_date DESC")` |
| **Composite lookup** | Multi-column ordered | `@Index(name = "idx_user_date", columnList = "user_id, created_date DESC")` |
| **Unique constraint** | Unique index | `@Index(name = "idx_email", columnList = "email", unique = true)` |
| **Foreign keys** | On join columns | `@Index(name = "idx_article_id", columnList = "article_id")` |
| **Sorting** | Order-specific | `@Index(name = "idx_price_desc", columnList = "price DESC")` |
| **Multi-column unique** | Composite unique | `@Index(name = "idx_sku", columnList = "category_id, code", unique = true)` |

## UUID vs ID Generation

```java
// UUID: Distributed systems
@Id
@GeneratedValue(strategy = GenerationType.UUID)
private UUID id;  // Size: 16 bytes, Globally unique

// IDENTITY: Single database
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;  // Size: 8 bytes, Locally sequential

// SEQUENCE: Portable, high performance
@Id
@SequenceGenerator(name = "seq", sequenceName = "entity_seq")
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seq")
private Long id;  // Size: 8 bytes, Database-native
```
