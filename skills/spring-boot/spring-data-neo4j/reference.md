# Spring Data Neo4j - Reference Guide

This document provides detailed reference information for Spring Data Neo4j, including annotations, query language syntax, configuration options, and API documentation.

## Table of Contents

1. [Annotations Reference](#annotations-reference)
2. [Cypher Query Language](#cypher-query-language)
3. [Configuration Properties](#configuration-properties)
4. [Repository Methods](#repository-methods)
5. [Projections and DTOs](#projections-and-dtos)
6. [Transaction Management](#transaction-management)
7. [Performance Tuning](#performance-tuning)

## Annotations Reference

### Entity Annotations

#### @Node

Marks a class as a Neo4j node entity.

```java
@Node                    // Label defaults to class name
@Node("CustomLabel")     // Explicit label
@Node({"Label1", "Label2"})  // Multiple labels
public class MyEntity {
    // ...
}
```

**Properties:**
- `value` or `labels`: String or String array for node labels
- `primaryLabel`: Specify which label is primary (when using multiple labels)

#### @Id

Marks a field as the entity identifier.

```java
@Id
private String businessKey;  // Custom business key

@Id @GeneratedValue
private Long id;  // Auto-generated internal ID
```

**Important:**
- Required on every @Node entity
- Can be used with business keys or generated values
- Must be unique within the node type

#### @GeneratedValue

Configures ID generation strategy.

```java
@Id @GeneratedValue
private Long id;  // Uses Neo4j internal ID

@Id @GeneratedValue(generatorClass = UUIDStringGenerator.class)
private String uuid;  // Custom UUID generator

@Id @GeneratedValue(generatorClass = MyCustomGenerator.class)
private String customId;
```

**Built-in Generators:**
- `InternalIdGenerator` (default for Long): Uses Neo4j's internal ID
- `UUIDStringGenerator`: Generates UUID strings

#### @Property

Maps a field to a different property name in Neo4j.

```java
@Property("graph_property_name")
private String javaFieldName;
```

**When to use:**
- Field name differs from graph property name
- Property names contain special characters
- Following different naming conventions

#### @Relationship

Defines relationships between nodes.

```java
@Relationship(type = "RELATIONSHIP_TYPE", direction = Direction.OUTGOING)
private RelatedEntity related;

@Relationship(type = "RELATED_TO", direction = Direction.INCOMING)
private List<RelatedEntity> incoming;

@Relationship(type = "CONNECTED", direction = Direction.UNDIRECTED)
private Set<RelatedEntity> connections;
```

**Properties:**
- `type` (required): Relationship type in Neo4j
- `direction`: OUTGOING, INCOMING, or UNDIRECTED
- Default direction is OUTGOING if not specified

**Direction Guidelines:**
- `OUTGOING`: This node → target node
- `INCOMING`: Target node → this node
- `UNDIRECTED`: Ignores direction when querying

#### @RelationshipProperties

Marks a class as relationship properties container.

```java
@RelationshipProperties
public class ActedIn {
    
    @Id @GeneratedValue
    private Long id;
    
    @TargetNode
    private Movie movie;
    
    private List<String> roles;
    private Integer screenTime;
}
```

**Required Fields:**
- `@Id` field (can be generated)
- `@TargetNode` field pointing to target entity

### Repository Annotations

#### @Query

Defines custom Cypher query for a repository method.

```java
@Query("MATCH (n:Node) WHERE n.property = $param RETURN n")
List<Node> customQuery(@Param("param") String param);

@Query("MATCH (n:Node) WHERE n.id = $0 RETURN n")
Node findById(String id);  // Positional parameter
```

**Parameter Binding:**
- Use `$paramName` for named parameters with `@Param`
- Use `$0`, `$1`, etc. for positional parameters
- SpEL expressions supported: `#{#entityName}`

#### @Param

Binds method parameter to query parameter.

```java
@Query("MATCH (n) WHERE n.name = $customName RETURN n")
List<Node> find(@Param("customName") String name);
```

**When required:**
- Parameter name in query differs from method parameter
- Making intent explicit and clear

### Configuration Annotations

#### @EnableNeo4jRepositories

Enables Neo4j repository support.

```java
@Configuration
@EnableNeo4jRepositories(basePackages = "com.example.repositories")
public class Neo4jConfiguration {
    // ...
}
```

**Properties:**
- `basePackages`: Packages to scan for repositories
- `basePackageClasses`: Type-safe package specification
- `repositoryImplementationPostfix`: Custom implementation suffix (default: "Impl")

**Note:** Auto-enabled by Spring Boot starter, manual configuration rarely needed.

#### @DataNeo4jTest

Test slice annotation for Neo4j tests.

```java
@DataNeo4jTest
class MyRepositoryTest {
    @Autowired
    private MyRepository repository;
}
```

**What it does:**
- Configures test slice for Spring Data Neo4j
- Loads only Neo4j-related beans
- Configures embedded test database when available
- Enables transaction rollback for tests

## Cypher Query Language

### Basic Patterns

#### MATCH - Find Patterns

```cypher
// Find all nodes with label
MATCH (n:Label) RETURN n

// Find node with property
MATCH (n:Label {property: 'value'}) RETURN n

// Find nodes with WHERE clause
MATCH (n:Label) WHERE n.property > 100 RETURN n

// Multiple labels
MATCH (n:Label1:Label2) RETURN n
```

#### Relationship Patterns

```cypher
// Outgoing relationship
MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a, b

// Incoming relationship
MATCH (a:Person)<-[:KNOWS]-(b:Person) RETURN a, b

// Undirected relationship
MATCH (a:Person)-[:KNOWS]-(b:Person) RETURN a, b

// Relationship with properties
MATCH (a)-[r:KNOWS {since: 2020}]->(b) RETURN a, r, b

// Variable length relationships
MATCH (a)-[:KNOWS*1..3]->(b) RETURN a, b
```

#### CREATE - Create Patterns

```cypher
// Create single node
CREATE (n:Person {name: 'John', age: 30})

// Create node and relationship
CREATE (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'})

// Create relationship between existing nodes
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS {since: 2020}]->(b)
```

#### MERGE - Find or Create

```cypher
// Find or create node
MERGE (n:Person {email: 'john@example.com'})
ON CREATE SET n.created = timestamp()
ON MATCH SET n.accessed = timestamp()

// Find or create relationship
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
MERGE (a)-[r:KNOWS]->(b)
ON CREATE SET r.since = 2020
```

#### SET - Update Properties

```cypher
// Set single property
MATCH (n:Person {name: 'John'})
SET n.age = 31

// Set multiple properties
MATCH (n:Person {name: 'John'})
SET n.age = 31, n.city = 'London'

// Set from map
MATCH (n:Person {name: 'John'})
SET n += {age: 31, city: 'London'}

// Add label
MATCH (n:Person {name: 'John'})
SET n:Premium
```

#### DELETE and REMOVE

```cypher
// Delete node (must have no relationships)
MATCH (n:Person {name: 'John'})
DELETE n

// Delete node and relationships
MATCH (n:Person {name: 'John'})
DETACH DELETE n

// Delete relationship
MATCH (a)-[r:KNOWS]->(b)
WHERE a.name = 'Alice' AND b.name = 'Bob'
DELETE r

// Remove property
MATCH (n:Person {name: 'John'})
REMOVE n.age

// Remove label
MATCH (n:Person {name: 'John'})
REMOVE n:Premium
```

### Advanced Patterns

#### Collections and List Functions

```cypher
// Collect results
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p.name, collect(m.title) AS movies

// Unwind collection
UNWIND [1, 2, 3] AS number
RETURN number

// List comprehension
MATCH (p:Person)
RETURN [x IN p.skills WHERE x STARTS WITH 'Java'] AS javaSkills

// Size of collection
MATCH (p:Person)
RETURN p.name, size(p.skills) AS skillCount
```

#### Aggregation Functions

```cypher
// Count
MATCH (p:Person) RETURN count(p)

// Sum
MATCH (p:Product) RETURN sum(p.price)

// Average
MATCH (p:Product) RETURN avg(p.price)

// Min/Max
MATCH (p:Product) RETURN min(p.price), max(p.price)

// Group by with aggregation
MATCH (p:Person)-[:LIVES_IN]->(c:City)
RETURN c.name, count(p) AS population
ORDER BY population DESC
```

#### Conditional Logic

```cypher
// CASE expression
MATCH (p:Person)
RETURN p.name,
  CASE
    WHEN p.age < 18 THEN 'Minor'
    WHEN p.age < 65 THEN 'Adult'
    ELSE 'Senior'
  END AS category

// COALESCE - first non-null value
MATCH (p:Person)
RETURN coalesce(p.nickname, p.name) AS displayName
```

#### Pattern Comprehension

```cypher
// Pattern comprehension
MATCH (p:Person)
RETURN p.name,
  [(p)-[:KNOWS]->(friend) | friend.name] AS friends

// With filtering
MATCH (p:Person)
RETURN p.name,
  [(p)-[:KNOWS]->(friend) WHERE friend.age > 30 | friend.name] AS olderFriends
```

### Query Optimization

#### Using Indexes

```cypher
// Create index (admin query, not in @Query)
CREATE INDEX person_name FOR (n:Person) ON (n.name)

// Composite index
CREATE INDEX person_name_age FOR (n:Person) ON (n.name, n.age)

// Use index hint
MATCH (p:Person)
USING INDEX p:Person(name)
WHERE p.name = 'John'
RETURN p
```

#### PROFILE and EXPLAIN

```cypher
// Analyze query performance
PROFILE
MATCH (p:Person)-[:KNOWS*1..3]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name

// Dry run without execution
EXPLAIN
MATCH (p:Person)-[:KNOWS]->(friend)
RETURN p, friend
```

#### Limiting Results

```cypher
// Limit results
MATCH (n:Person) RETURN n LIMIT 10

// Skip and limit (pagination)
MATCH (n:Person)
RETURN n
ORDER BY n.name
SKIP 20 LIMIT 10
```

## Configuration Properties

### Connection Properties

```properties
# Neo4j URI
spring.neo4j.uri=bolt://localhost:7687
spring.neo4j.uri=neo4j://localhost:7687
spring.neo4j.uri=neo4j+s://production.server:7687

# Authentication
spring.neo4j.authentication.username=neo4j
spring.neo4j.authentication.password=secret
spring.neo4j.authentication.realm=native
spring.neo4j.authentication.kerberos-ticket=...

# Connection pool
spring.neo4j.pool.max-connection-pool-size=50
spring.neo4j.pool.idle-time-before-connection-test=PT30S
spring.neo4j.pool.max-connection-lifetime=PT1H
spring.neo4j.pool.connection-acquisition-timeout=PT60S
spring.neo4j.pool.metrics-enabled=true
```

### Advanced Configuration

```properties
# Logging
spring.neo4j.logging.level=WARN
spring.neo4j.logging.log-leaked-sessions=true

# Connection timeout
spring.neo4j.connection-timeout=PT30S

# Max transaction retry time
spring.neo4j.max-transaction-retry-time=PT30S

# Encrypted connection
spring.neo4j.security.encrypted=true
spring.neo4j.security.trust-strategy=TRUST_ALL_CERTIFICATES
spring.neo4j.security.hostname-verification-enabled=true
```

### Neo4j Driver Configuration Bean

```java
@Configuration
public class Neo4jConfiguration {
    
    @Bean
    org.neo4j.driver.Config neo4jDriverConfig() {
        return org.neo4j.driver.Config.builder()
            .withMaxConnectionPoolSize(50)
            .withConnectionAcquisitionTimeout(60, TimeUnit.SECONDS)
            .withConnectionLivenessCheckTimeout(30, TimeUnit.SECONDS)
            .withMaxConnectionLifetime(1, TimeUnit.HOURS)
            .withLogging(Logging.slf4j())
            .withEncryption()
            .build();
    }
    
    @Bean
    Configuration cypherDslConfiguration() {
        return Configuration.newConfig()
            .withDialect(Dialect.NEO4J_5)
            .build();
    }
}
```

## Repository Methods

### Query Derivation Keywords

| Keyword | Cypher Equivalent |
|---------|------------------|
| `findBy` | `MATCH ... RETURN` |
| `existsBy` | `MATCH ... RETURN count(*) > 0` |
| `countBy` | `MATCH ... RETURN count(*)` |
| `deleteBy` | `MATCH ... DETACH DELETE` |
| `And` | `AND` |
| `Or` | `OR` |
| `Between` | `>= $lower AND <= $upper` |
| `LessThan` | `<` |
| `LessThanEqual` | `<=` |
| `GreaterThan` | `>` |
| `GreaterThanEqual` | `>=` |
| `Before` | `<` (for dates) |
| `After` | `>` (for dates) |
| `IsNull` | `IS NULL` |
| `IsNotNull` | `IS NOT NULL` |
| `Like` | `=~ '.*pattern.*'` |
| `NotLike` | `NOT =~ '.*pattern.*'` |
| `StartingWith` | `STARTS WITH` |
| `EndingWith` | `ENDS WITH` |
| `Containing` | `CONTAINS` |
| `In` | `IN` |
| `NotIn` | `NOT IN` |
| `True` | `= true` |
| `False` | `= false` |
| `OrderBy...Asc` | `ORDER BY ... ASC` |
| `OrderBy...Desc` | `ORDER BY ... DESC` |

### Method Return Types

| Return Type | Description |
|------------|-------------|
| `Entity` | Single result or null |
| `Optional<Entity>` | Single result wrapped in Optional |
| `List<Entity>` | Multiple results |
| `Stream<Entity>` | Results as Java Stream |
| `Page<Entity>` | Paginated results |
| `Slice<Entity>` | Slice of results |
| `Mono<Entity>` | Reactive single result |
| `Flux<Entity>` | Reactive stream of results |
| `boolean` | Existence check |
| `long` | Count query |

### Examples

```java
public interface UserRepository extends Neo4jRepository<User, String> {
    
    // Simple query derivation
    Optional<User> findByEmail(String email);
    
    List<User> findByAgeGreaterThan(Integer age);
    
    List<User> findByAgeBetween(Integer minAge, Integer maxAge);
    
    List<User> findByNameStartingWith(String prefix);
    
    // Boolean queries
    boolean existsByEmail(String email);
    
    // Count queries
    long countByAgeGreaterThan(Integer age);
    
    // Delete queries
    long deleteByAgeLessThan(Integer age);
    
    // Sorting
    List<User> findByAgeGreaterThanOrderByNameAsc(Integer age);
    
    // Pagination
    Page<User> findByAgeGreaterThan(Integer age, Pageable pageable);
    
    // Stream
    Stream<User> findByAgeBetween(Integer min, Integer max);
    
    // Multiple conditions
    List<User> findByNameAndAge(String name, Integer age);
    
    List<User> findByNameOrEmail(String name, String email);
    
    // Null checks
    List<User> findByNicknameIsNull();
    
    List<User> findByNicknameIsNotNull();
    
    // Collection queries
    List<User> findByRolesContaining(String role);
    
    List<User> findByIdIn(Collection<String> ids);
}
```

## Projections and DTOs

### Interface-based Projections

```java
// Closed projection - only declared properties
public interface UserSummary {
    String getUsername();
    String getEmail();
}

// Open projection - with SpEL
public interface UserWithFullName {
    @Value("#{target.firstName + ' ' + target.lastName}")
    String getFullName();
}

// Nested projection
public interface UserWithPosts {
    String getUsername();
    List<PostSummary> getPosts();
    
    interface PostSummary {
        String getTitle();
        LocalDateTime getCreatedAt();
    }
}

// Usage
public interface UserRepository extends Neo4jRepository<User, String> {
    List<UserSummary> findAllBy();
    Optional<UserWithFullName> findByUsername(String username);
}
```

### Class-based DTOs

```java
public record UserDTO(
    String username,
    String email,
    LocalDateTime joinedAt
) {}

// Repository usage
public interface UserRepository extends Neo4jRepository<User, String> {
    List<UserDTO> findAllBy();
}
```

### Dynamic Projections

```java
public interface UserRepository extends Neo4jRepository<User, String> {
    <T> T findByUsername(String username, Class<T> type);
}

// Usage
UserSummary summary = repository.findByUsername("john", UserSummary.class);
UserDTO dto = repository.findByUsername("john", UserDTO.class);
User full = repository.findByUsername("john", User.class);
```

## Transaction Management

### Declarative Transactions

```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    
    @Transactional
    public User createUser(CreateUserRequest request) {
        User user = new User(request.username(), request.email());
        return userRepository.save(user);
    }
    
    @Transactional(readOnly = true)
    public Optional<User> getUser(String username) {
        return userRepository.findByUsername(username);
    }
    
    @Transactional(
        propagation = Propagation.REQUIRES_NEW,
        isolation = Isolation.READ_COMMITTED,
        timeout = 30
    )
    public void complexOperation() {
        // Multiple repository calls in single transaction
        // ...
    }
}
```

### Programmatic Transactions

```java
@Service
public class TransactionalService {
    
    private final Neo4jTransactionManager transactionManager;
    
    public void executeInTransaction() {
        TransactionTemplate template = new TransactionTemplate(transactionManager);
        template.execute(status -> {
            try {
                // Your transactional code here
                return someResult;
            } catch (Exception e) {
                status.setRollbackOnly();
                throw e;
            }
        });
    }
}
```

### Reactive Transactions

```java
@Service
public class ReactiveUserService {
    
    private final ReactiveUserRepository repository;
    private final ReactiveNeo4jTransactionManager transactionManager;
    
    public Mono<User> createUser(CreateUserRequest request) {
        return transactionManager.getReactiveTransaction()
            .flatMap(status -> {
                User user = new User(request.username(), request.email());
                return repository.save(user)
                    .doOnError(e -> status.setRollbackOnly());
            });
    }
}
```

## Performance Tuning

### Index Creation

Create indexes on frequently queried properties:

```cypher
// Single property index
CREATE INDEX user_email FOR (u:User) ON (u.email);

// Composite index
CREATE INDEX user_name_age FOR (u:User) ON (u.name, u.age);

// Full-text index
CREATE FULLTEXT INDEX user_search FOR (u:User) ON EACH [u.name, u.bio];

// Show indexes
SHOW INDEXES;

// Drop index
DROP INDEX user_email;
```

### Query Optimization Tips

1. **Use specific labels:**
   ```cypher
   // Good
   MATCH (u:User {email: $email}) RETURN u
   
   // Bad
   MATCH (n {email: $email}) RETURN n
   ```

2. **Filter early:**
   ```cypher
   // Good
   MATCH (u:User)
   WHERE u.age > 18
   MATCH (u)-[:POSTED]->(p:Post)
   RETURN p
   
   // Bad
   MATCH (u:User)-[:POSTED]->(p:Post)
   WHERE u.age > 18
   RETURN p
   ```

3. **Use projections to fetch only needed data:**
   ```java
   // Good
   List<UserSummary> findAllBy();
   
   // Bad (when you only need summary)
   List<User> findAll();
   ```

4. **Limit result sets:**
   ```java
   // Use pagination
   Page<User> findAll(Pageable pageable);
   
   // Or explicit limits
   @Query("MATCH (u:User) RETURN u LIMIT $limit")
   List<User> findTopUsers(@Param("limit") int limit);
   ```

### Connection Pooling

```java
@Bean
org.neo4j.driver.Config driverConfig() {
    return org.neo4j.driver.Config.builder()
        .withMaxConnectionPoolSize(50)
        .withConnectionAcquisitionTimeout(60, TimeUnit.SECONDS)
        .withIdleTimeBeforeConnectionTest(30, TimeUnit.SECONDS)
        .build();
}
```

### Batch Operations

```java
// Save in batches
@Service
public class BatchService {
    
    private final UserRepository repository;
    
    public void saveUsersInBatches(List<User> users) {
        int batchSize = 1000;
        for (int i = 0; i < users.size(); i += batchSize) {
            int end = Math.min(i + batchSize, users.size());
            List<User> batch = users.subList(i, end);
            repository.saveAll(batch);
        }
    }
}
```

### Monitoring and Metrics

```properties
# Enable driver metrics
spring.neo4j.pool.metrics-enabled=true

# Log slow queries (if using Neo4j Enterprise)
# Set in neo4j.conf:
# dbms.logs.query.enabled=true
# dbms.logs.query.threshold=1s
```

## Additional Resources

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Spring Data Neo4j Reference](https://docs.spring.io/spring-data/neo4j/reference/)
- [Neo4j Java Driver Documentation](https://neo4j.com/docs/java-manual/current/)
- [Graph Data Modeling Guide](https://neo4j.com/developer/data-modeling/)
