---
name: spring-data-neo4j
description: Expert in Spring Data Neo4j integration patterns for graph database development. Use when working with Neo4j graph databases, node entities, relationships, Cypher queries, reactive Neo4j operations, or Spring Data Neo4j repositories. Essential for graph data modeling, relationship mapping, custom queries, and Neo4j testing strategies.
version: 1.0.1
allowed-tools: Read, Write, Bash
category: backend
tags: [spring-data, neo4j, graph-database, database]
---

# Spring Data Neo4j Integration Patterns

## When to Use This Skill

Use this skill when you need to:
- Set up Spring Data Neo4j in a Spring Boot application
- Create and map graph node entities and relationships
- Implement Neo4j repositories with custom queries
- Write Cypher queries using @Query annotations
- Configure Neo4j connections and dialects
- Test Neo4j repositories with embedded databases
- Work with both imperative and reactive Neo4j operations
- Map complex graph relationships with bidirectional or unidirectional directions
- Use Neo4j's internal ID generation or custom business keys

## Overview

Spring Data Neo4j is part of the Spring Data family and provides seamless integration with Neo4j graph databases. It offers three levels of abstraction:
- **Neo4j Client**: Low-level abstraction for direct database access
- **Neo4j Template**: Medium-level template-based operations
- **Neo4j Repositories**: High-level repository pattern with query derivation

Key features:
- Reactive and imperative operation modes
- Immutable entity mapping
- Custom query support via @Query annotation
- Spring's Conversion Service integration
- Full support for graph relationships and traversals

## Project Setup

### Dependencies

**Maven:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-neo4j</artifactId>
</dependency>
```

**Gradle:**
```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-neo4j'
}
```

### Configuration

**application.properties:**
```properties
spring.neo4j.uri=bolt://localhost:7687
spring.neo4j.authentication.username=neo4j
spring.neo4j.authentication.password=secret
```

**Configure Neo4j Cypher-DSL Dialect:**
```java
@Configuration
public class Neo4jConfig {
    
    @Bean
    Configuration cypherDslConfiguration() {
        return Configuration.newConfig()
            .withDialect(Dialect.NEO4J_5).build();
    }
}
```

**Key Points:**
- Default dialect targets Neo4j 4.4 LTS
- Neo4j 5 dialect provides optimized queries using `elementId()`
- Always explicitly define dialect for best compatibility
- SDN repositories are auto-enabled by the starter

## Entity Mapping

### Node Entity with Business Key

```java
@Node("Movie")
public class MovieEntity {

    @Id
    private final String title;  // Business key as ID

    @Property("tagline")
    private final String description;

    private final Integer year;

    @Relationship(type = "ACTED_IN", direction = Direction.INCOMING)
    private List<Roles> actorsAndRoles = new ArrayList<>();

    @Relationship(type = "DIRECTED", direction = Direction.INCOMING)
    private List<PersonEntity> directors = new ArrayList<>();

    public MovieEntity(String title, String description, Integer year) {
        this.title = title;
        this.description = description;
        this.year = year;
    }

    // Getters omitted for brevity
}
```

### Node Entity with Generated ID

```java
@Node("Movie")
public class MovieEntity {

    @Id @GeneratedValue
    private Long id;

    private final String title;

    @Property("tagline")
    private final String description;

    public MovieEntity(String title, String description) {
        this.id = null;  // Never set manually
        this.title = title;
        this.description = description;
    }

    // Wither method for immutability with generated IDs
    public MovieEntity withId(Long id) {
        if (this.id != null && this.id.equals(id)) {
            return this;
        } else {
            MovieEntity newObject = new MovieEntity(this.title, this.description);
            newObject.id = id;
            return newObject;
        }
    }
}
```

### Relationship Mapping

```java
@Node("Person")
public class Person {

    @Id @GeneratedValue 
    private Long id;

    private String name;

    @Relationship(type = "TEAMMATE", direction = Direction.UNDIRECTED)
    public Set<Person> teammates;

    public void worksWith(Person person) {
        if (teammates == null) {
            teammates = new HashSet<>();
        }
        teammates.add(person);
    }
}
```

**Relationship Directions:**
- `Direction.OUTGOING`: From this node to related nodes
- `Direction.INCOMING`: From related nodes to this node
- `Direction.UNDIRECTED`: Ignores direction when querying

### Annotation Reference

| Annotation | Purpose |
|------------|---------|
| `@Node` | Marks class as graph node entity (label defaults to class name) |
| `@Id` | Marks field as node identifier |
| `@GeneratedValue` | Uses Neo4j internal ID generation |
| `@Property` | Maps field to different property name in database |
| `@Relationship` | Defines relationship with type and direction |

## Repository Patterns

### Basic Repository Interface

```java
@Repository
public interface MovieRepository extends Neo4jRepository<MovieEntity, String> {
    
    // Query derivation from method name
    MovieEntity findOneByTitle(String title);
    
    List<MovieEntity> findAllByYear(Integer year);
    
    List<MovieEntity> findByYearBetween(Integer startYear, Integer endYear);
}
```

### Reactive Repository

```java
@Repository
public interface MovieRepository extends ReactiveNeo4jRepository<MovieEntity, String> {
    
    Mono<MovieEntity> findOneByTitle(String title);
    
    Flux<MovieEntity> findAllByYear(Integer year);
}
```

**Imperative vs Reactive:**
- Use `Neo4jRepository` for blocking, imperative operations
- Use `ReactiveNeo4jRepository` for non-blocking, reactive operations
- **Do not mix imperative and reactive in the same application**
- Reactive requires Neo4j 4+ on the database side

### Custom Queries with @Query

```java
@Repository
public interface AuthorRepository extends Neo4jRepository<Author, Long> {
    
    @Query("MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) " +
           "WHERE a.name = $name AND b.year > $year " +
           "RETURN b")
    List<Book> findBooksAfterYear(@Param("name") String name, 
                                   @Param("year") Integer year);
    
    @Query("MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) " +
           "WHERE a.name = $name " +
           "RETURN b ORDER BY b.year DESC")
    List<Book> findBooksByAuthorOrderByYearDesc(@Param("name") String name);
}
```

**Custom Query Best Practices:**
- Use `$parameterName` for parameter placeholders
- Use `@Param` annotation when parameter name differs from method parameter
- MATCH specifies node patterns and relationships
- WHERE filters results
- RETURN defines what to return

### Query Keywords Support

Spring Data Neo4j supports standard query derivation keywords:
- `findBy`, `findAllBy`, `existsBy`, `countBy`, `deleteBy`
- `And`, `Or`, `Between`, `LessThan`, `GreaterThan`
- `Like`, `StartingWith`, `EndingWith`, `Containing`
- `OrderBy`, `Asc`, `Desc`
- `IsNull`, `IsNotNull`
- `In`, `NotIn`

## Testing Strategies

### Neo4j Harness for Integration Testing

**Maven Dependency:**
```xml
<dependency>
    <groupId>org.neo4j.test</groupId>
    <artifactId>neo4j-harness</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>
```

**Test Configuration:**
```java
@DataNeo4jTest
class BookRepositoryIntegrationTest {

    private static Neo4j embeddedServer;

    @BeforeAll
    static void initializeNeo4j() {
        embeddedServer = Neo4jBuilders.newInProcessBuilder()
            .withDisabledServer()  // No HTTP access needed
            .withFixture(
                "CREATE (b:Book {isbn: '978-0547928210', " +
                "name: 'The Fellowship of the Ring', year: 1954})" +
                "-[:WRITTEN_BY]->(a:Author {id: 1, name: 'J. R. R. Tolkien'}) " +
                "CREATE (b2:Book {isbn: '978-0547928203', " +
                "name: 'The Two Towers', year: 1956})" +
                "-[:WRITTEN_BY]->(a)"
            )
            .build();
    }

    @AfterAll
    static void stopNeo4j() {
        embeddedServer.close();
    }

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.neo4j.uri", embeddedServer::boltURI);
        registry.add("spring.neo4j.authentication.username", () -> "neo4j");
        registry.add("spring.neo4j.authentication.password", () -> "null");
    }

    @Autowired
    private BookRepository bookRepository;

    @Test
    void givenBookExists_whenFindOneByTitle_thenBookIsReturned() {
        Book book = bookRepository.findOneByTitle("The Fellowship of the Ring");
        assertThat(book.getIsbn()).isEqualTo("978-0547928210");
    }

    @Test
    void givenOneBookExistsForYear_whenFindAllByYear_thenOneBookIsReturned() {
        List<Book> books = bookRepository.findAllByYear(1954);
        assertThat(books).hasSize(1);
    }
}
```

**Test Configuration Best Practices:**
- Use `@DataNeo4jTest` to configure test slice for Neo4j
- Create embedded server in `@BeforeAll` static method
- Use `withDisabledServer()` for in-process testing without HTTP
- Provide test data with `withFixture()` using Cypher
- Override properties with `@DynamicPropertySource`
- Always close server in `@AfterAll`

## Architecture Patterns

### Feature-Based Structure

```
feature/
├── domain/
│   ├── model/
│   │   ├── MovieNode.java          # @Node entities
│   │   └── PersonNode.java
│   ├── repository/
│   │   ├── MovieRepository.java    # Domain interfaces
│   │   └── PersonRepository.java
│   └── service/
│       └── GraphDomainService.java
├── application/
│   ├── service/
│   │   └── MovieSearchService.java # Use cases
│   └── dto/
│       └── MovieDTO.java           # Immutable records
└── infrastructure/
    └── neo4j/
        └── config/
            └── Neo4jConfiguration.java
```

### Constructor Injection Pattern

```java
@Service
public class MovieService {
    
    private final MovieRepository movieRepository;
    private final PersonRepository personRepository;
    
    // Constructor injection - preferred over field injection
    public MovieService(MovieRepository movieRepository,
                       PersonRepository personRepository) {
        this.movieRepository = movieRepository;
        this.personRepository = personRepository;
    }
    
    public MovieDTO findMovieByTitle(String title) {
        MovieEntity movie = movieRepository.findOneByTitle(title);
        return MovieMapper.toDTO(movie);
    }
}
```

### Using Java Records for DTOs

```java
public record MovieDTO(
    String title,
    String description,
    Integer year,
    List<String> directors,
    List<String> actors
) {
    // Compact constructor for validation
    public MovieDTO {
        Objects.requireNonNull(title, "Title cannot be null");
        if (year != null && year < 1888) {
            throw new IllegalArgumentException("Year must be 1888 or later");
        }
    }
}
```

## Advanced Patterns

### Bi-directional Relationships

```java
@Node("Author")
public class Author {
    @Id @GeneratedValue
    private Long id;
    
    private String name;
    
    @Relationship(type = "WRITTEN_BY", direction = Direction.INCOMING)
    private List<Book> books;
}

@Node("Book")
public class Book {
    @Id
    private String isbn;
    
    private String title;
    
    @Relationship(type = "WRITTEN_BY", direction = Direction.OUTGOING)
    private Author author;
}
```

**Note:** Neo4j doesn't have true bi-directional relationships. Direction is ignored when `Direction.UNDIRECTED` is used.

### Custom ID Generation

```java
@Node("Product")
public class Product {
    
    @Id
    @GeneratedValue(generatorClass = UUIDStringGenerator.class)
    private String id;
    
    private String name;
    private BigDecimal price;
}
```

### Projections

Spring Data Neo4j supports projections for retrieving partial data:

```java
public interface MovieTitleProjection {
    String getTitle();
    Integer getYear();
}

@Repository
public interface MovieRepository extends Neo4jRepository<Movie, String> {
    List<MovieTitleProjection> findAllByYear(Integer year);
}
```

## Performance Considerations

### Repository Method Optimization

- Use projections to fetch only required fields
- Leverage query derivation for simple queries
- Use `@Query` for complex graph traversals
- Consider pagination with `Pageable` parameter
- Use `existsBy` instead of `findBy` when checking existence

### Connection Pooling

Default Neo4j Driver configuration provides connection pooling. Customize if needed:

```properties
spring.neo4j.pool.max-connection-pool-size=50
spring.neo4j.pool.connection-acquisition-timeout=60s
spring.neo4j.pool.max-connection-lifetime=1h
```

## Common Patterns and Examples

See [examples.md](./examples.md) for comprehensive code examples.

See [reference.md](./reference.md) for detailed API reference and Cypher query patterns.

## Best Practices

1. **Entity Design:**
   - Use immutable entities with final fields
   - Choose between business keys (@Id) or generated IDs (@Id @GeneratedValue)
   - Keep entities focused on graph structure, not business logic
   - Use proper relationship directions (INCOMING, OUTGOING, UNDIRECTED)

2. **Repository Design:**
   - Extend `Neo4jRepository` for imperative or `ReactiveNeo4jRepository` for reactive
   - Use query derivation for simple queries
   - Write custom @Query for complex graph patterns
   - Don't mix imperative and reactive in same application

3. **Configuration:**
   - Always configure Cypher-DSL dialect explicitly
   - Use environment-specific properties for credentials
   - Never hardcode credentials in source code
   - Configure connection pooling based on load

4. **Testing:**
   - Use Neo4j Harness for integration tests
   - Provide test data via `withFixture()` Cypher queries
   - Use `@DataNeo4jTest` for test slicing
   - Test both successful and edge-case scenarios

5. **Architecture:**
   - Use constructor injection exclusively
   - Separate domain entities from DTOs
   - Follow feature-based package structure
   - Keep domain layer framework-agnostic

6. **Security:**
   - Use Spring Boot property overrides for credentials
   - Configure proper authentication and authorization
   - Validate input parameters in service layer
   - Use parameterized queries to prevent Cypher injection

## Version History

- **1.0.0** (2025-01-25): Initial skill with Spring Data Neo4j 7.x patterns, Neo4j 5 dialect support, reactive and imperative modes, testing with Neo4j Harness

## References

- [Spring Data Neo4j Official Documentation](https://docs.spring.io/spring-data/neo4j/reference/)
- [Neo4j Developer Guide](https://neo4j.com/developer/)
- [Spring Data Commons Documentation](https://docs.spring.io/spring-data/commons/reference/)
