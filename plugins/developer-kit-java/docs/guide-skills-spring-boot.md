# Spring Boot Skills Guide

Quick reference to 13 Spring Boot skills for production-ready applications. See individual skill files for complete details.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **spring-boot-dependency-injection** | Constructor injection patterns for testable services |
| **spring-boot-actuator** | Production monitoring, health checks, metrics |
| **spring-boot-cache** | Caching patterns, eviction, distributed caching |
| **spring-boot-crud-patterns** | REST CRUD API with DDD, feature-based architecture |
| **spring-boot-event-driven-patterns** | Event-driven architecture, Kafka, Spring Cloud Stream |
| **spring-boot-rest-api-standards** | REST API design, HTTP semantics, error handling |
| **spring-boot-test-patterns** | Integration testing with Testcontainers |
| **spring-boot-resilience4j** | Circuit breaker, retry, rate limiting patterns |
| **spring-boot-saga-pattern** | Distributed transactions, choreography, orchestration |
| **spring-boot-security-jwt** | JWT auth, OAuth2/OIDC, RBAC |
| **spring-boot-project-creator** | Project generation from specification |
| **spring-data-jpa** | Spring Data JPA patterns, custom queries |
| **spring-data-neo4j** | Neo4j graph database integration |
| **spring-boot-openapi-documentation** | OpenAPI/Swagger documentation |

---

## Core Spring Boot

### spring-boot-dependency-injection

**File**: `skills/spring-boot-dependency-injection/SKILL.md`

Master constructor-first DI for testable, framework-agnostic services.

**When to use:**
- Implementing `@Service`, `@Component`, `@Repository`
- Replacing field injection during modernization
- Auditing bean definitions

**Key pattern:**
```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    
    public User create(CreateUserRequest req) {
        return userRepository.save(User.of(req));
    }
}
```

---

### spring-boot-actuator

**File**: `skills/spring-boot-actuator/SKILL.md`

Production monitoring: health checks, metrics, custom endpoints.

**When to use:**
- Adding observability to Spring Boot apps
- Implementing custom health indicators
- Exposing metrics to Prometheus/Grafana

---

### spring-boot-cache

**File**: `skills/spring-boot-cache/SKILL.md`

Caching patterns: `@Cacheable`, eviction, distributed caches.

**When to use:**
- Reducing database queries
- Implementing cache eviction strategies
- Using Redis for distributed caching

---

### spring-boot-project-creator

**File**: `skills/spring-boot-project-creator/SKILL.md`

Project generation: create Spring Boot projects from specifications.

**When to use:**
- Starting a new Spring Boot application
- Generating project structure from requirements
- Creating scaffolded code from domain models

---

## Data & Persistence

### spring-data-jpa

**File**: `skills/spring-data-jpa/SKILL.md`

Spring Data JPA: query methods, custom repositories, performance.

**When to use:**
- Building CRUD operations
- Creating custom queries
- Optimizing N+1 queries

---

### spring-data-neo4j

**File**: `skills/spring-data-neo4j/SKILL.md`

Neo4j integration: graph modeling, Cypher queries, relationships.

**When to use:**
- Working with graph databases
- Modeling relationships and patterns
- Complex relationship traversals

---

## Architecture & Patterns

### spring-boot-crud-patterns

**File**: `skills/spring-boot-crud-patterns/SKILL.md`

REST CRUD with DDD, feature-based architecture, Lombok, Spring Data.

**When to use:**
- Generating CRUD REST APIs
- Organizing code by features not layers
- Using DTOs and mappers

---

### spring-boot-event-driven-patterns

**File**: `skills/spring-boot-event-driven-patterns/SKILL.md`

Event-driven architecture: domain events, Kafka, Spring Cloud Stream.

**When to use:**
- Decoupling services with async events
- Implementing event sourcing patterns
- Kafka message handling

---

### spring-boot-saga-pattern

**File**: `skills/spring-boot-saga-pattern/SKILL.md`

Distributed transactions: choreography, orchestration, compensations.

**When to use:**
- Coordinating multiple services
- Implementing compensating transactions
- Managing distributed consistency

---

### spring-boot-rest-api-standards

**File**: `skills/spring-boot-rest-api-standards/SKILL.md`

REST API design: HTTP semantics, error handling, pagination, headers.

**When to use:**
- Designing REST endpoints
- Implementing error responses
- Adding pagination and filtering

---

## Resilience & Security

### spring-boot-resilience4j

**File**: `skills/spring-boot-resilience4j/SKILL.md`

Fault tolerance: circuit breaker, retry, rate limiting, bulkhead.

**When to use:**
- Protecting against cascading failures
- Implementing retry policies
- Rate limiting API endpoints

---

### spring-boot-security-jwt

**File**: `skills/spring-boot-security-jwt/SKILL.md`

JWT authentication, OAuth2/OIDC, RBAC, permission-based access.

**When to use:**
- Implementing JWT authentication
- OAuth2/OIDC integration
- Role-based access control

---

## Testing

### spring-boot-test-patterns

**File**: `skills/spring-boot-test-patterns/SKILL.md`

Integration testing: Testcontainers, Spring slice tests, databases.

**When to use:**
- Writing integration tests
- Testing with real databases
- Spring context tests

---

## Documentation

### spring-boot-openapi-documentation

**File**: `skills/spring-boot-openapi-documentation/SKILL.md`

OpenAPI/Swagger documentation: API docs, schema generation, SpringDoc.

**When to use:**
- Documenting REST APIs
- Generating Swagger UI
- Creating OpenAPI schemas

---

## Common Workflows

### Building a Complete API

```
1. spring-boot-crud-patterns          → Generate REST CRUD operations
2. spring-boot-rest-api-standards     → Design proper responses
3. spring-boot-security-jwt           → Add authentication
4. spring-data-jpa                    → Optimize queries
5. spring-boot-actuator               → Add monitoring
6. spring-boot-test-patterns          → Write integration tests
```

### Adding Async Patterns

```
1. spring-boot-event-driven-patterns  → Design event architecture
2. spring-boot-saga-pattern           → Coordinate services
3. spring-boot-resilience4j           → Handle failures
4. spring-boot-cache                  → Cache results
```

### Production Ready

```
1. spring-boot-security-jwt           → Secure all endpoints
2. spring-boot-actuator               → Add health/metrics
3. spring-boot-resilience4j           → Add fault tolerance
4. spring-boot-test-patterns          → Integration tests
5. spring-boot-openapi-documentation → API documentation
```

---

## Stack & Versions

- **Spring Boot**: 3.5.x+
- **Java**: 17+ (records, sealed classes)
- **Spring Data**: JPA, Neo4j
- **Testing**: Testcontainers 1.19+, JUnit 5, Mockito
- **Resilience**: Resilience4j
- **Documentation**: OpenAPI 3.0, SpringDoc

---

**Note**: For complete patterns and examples, see individual skill files in `skills/`
