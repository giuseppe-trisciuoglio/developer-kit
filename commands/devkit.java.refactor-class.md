---
allowed-tools: Read, Write, Bash, Edit, Grep, Glob
argument-hint: [class-file-path] [refactoring-scope] [options]
description: Intelligent refactoring assistant for complex Java classes with architectural analysis and Spring Boot patterns
model: inherit
---

# Java Class Refactoring Assistant

Intelligently refactor complex Java classes following Clean Architecture, DDD patterns, and Spring Boot best practices.

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Commits**: !`git log --oneline -5`
- **Test Coverage**: !`find . -name "*Test.java" -type f | wc -l` test files found

## Refactoring Configuration

Analyzing: **$ARGUMENTS**

**Parameters:**
- `$1` - Class file path (required): Path to Java class to refactor
- `$2` - Refactoring scope (optional):
  - `cleanup` - Code cleanup and style improvements (default)
  - `architecture` - Architectural pattern improvements
  - `performance` - Performance optimizations
  - `security` - Security enhancements
  - `testing` - Testability improvements
  - `comprehensive` - All improvements (full refactor)
- `$3` - Options (optional): `dry-run`, `backup`, `validate-only`

## Pre-Refactoring Analysis

### 1. Class Identification and Context
IF "$1" is empty OR not provided
THEN Analyze the most complex class in the codebase automatically
ELSE Analyze specific class: $1
ENDIF

### 2. Architecture Pattern Detection
```
Expected Clean Architecture Structure:
feature/
├── domain/
│   ├── model/           # Domain entities (Spring-free)
│   ├── repository/      # Domain ports (interfaces)
│   └── service/         # Domain services
├── application/
│   ├── service/         # Use cases (@Service beans)
│   └── dto/             # Immutable DTOs/records
├── presentation/
│   └── rest/            # Controllers and mappers
└── infrastructure/
    └── persistence/     # JPA adapters
```

## Refactoring Strategy by Scope

### Cleanup Refactoring ($2 = "cleanup")
- **Code Style**: Apply consistent formatting, naming conventions
- **Dead Code**: Remove unused imports, methods, variables
- **Complexity**: Simplify complex methods (< 10 cyclomatic complexity)
- **Documentation**: Add missing JavaDoc and inline comments
- **Immutability**: Convert to immutable structures where possible

### Architecture Refactoring ($2 = "architecture")
- **Layer Separation**: Ensure proper dependency direction
- **DDD Patterns**: Apply aggregates, value objects, domain events
- **Spring Patterns**: Constructor injection, proper bean scoping
- **Repository Pattern**: Domain interfaces + infrastructure adapters
- **DTO Pattern**: Replace JPA entities with records in APIs

### Performance Refactoring ($2 = "performance")
- **Database Queries**: Optimize JPA queries, eliminate N+1 problems
- **Caching**: Add @Cacheable, @CachePut, @CacheEvict where appropriate
- **Async Processing**: Convert blocking operations to @Async
- **Memory Management**: Identify and fix memory leaks
- **Algorithm Optimization**: Improve computational complexity

### Security Refactoring ($2 = "security")
- **Input Validation**: Add Jakarta Bean Validation
- **Authentication**: Ensure proper @PreAuthorize usage
- **Data Exposure**: Prevent sensitive data leakage in DTOs
- **SQL Injection**: Verify safe JPA usage
- **XSS Prevention**: Input sanitization and output encoding

### Testing Refactoring ($2 = "testing")
- **Testability**: Extract dependencies for better mocking
- **Test Coverage**: Add missing unit/integration tests
- **Test Structure**: Apply AAA pattern (Arrange, Act, Assert)
- **Mocking**: Proper Mockito usage without static mocks
- **Testcontainers**: Real database testing for persistence layer

## Refactoring Process

### Phase 1: Analysis and Planning
1. **Read and analyze target class** for current patterns and violations
2. **Identify dependencies** and usage patterns across codebase
3. **Assess test coverage** - if missing, create tests BEFORE refactoring
4. **Create refactoring plan** based on selected scope
5. **Backup strategy** - create branch if not `dry-run`

### Phase 2: Safety Checks
```bash
# Run existing tests
./gradlew test || mvn test

# Create backup branch if not dry-run
if [ "$3" != "dry-run" ]; then
  git checkout -b refactor/$(basename "$1" .java)-$(date +%Y%m%d-%H%M%S)
fi
```

### Phase 3: Incremental Refactoring
For each refactoring step:

1. **Make small, focused change**
2. **Run tests** to verify no regressions
3. **Commit change** with descriptive message
4. **Document improvement** and rationale

### Phase 4: Validation
```bash
# Full test suite
./gradlew test || mvn test

# Static analysis
./gradlew spotbugsMain || ./gradlew checkstyleMain

# Performance validation
./gradlew bench || echo "No performance tests configured"
```

## Common Refactoring Patterns

### Extract Method/Service
```java
// Before: Complex method doing too much
@Service
@RequiredArgsConstructor
public class OrderService {
    public OrderDto createOrder(CreateOrderRequest request) {
        // Validation logic (20+ lines)
        // Business logic (30+ lines)
        // Notification logic (15+ lines)
        // Audit logic (10+ lines)
    }
}

// After: Extracted responsibilities
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderValidator validator;
    private final OrderProcessor processor;
    private final NotificationService notificationService;
    private final AuditService auditService;

    public OrderDto createOrder(CreateOrderRequest request) {
        validator.validate(request);
        var order = processor.process(request);
        notificationService.sendOrderCreated(order);
        auditService.logOrderCreation(order);
        return order;
    }
}
```

### Replace with Record/Value Object
```java
// Before: Mutable entity exposed
public class UserDto {
    private String name;
    private String email;
    // getters/setters
}

// After: Immutable record
public record UserDto(String id, String name, String email, Instant createdAt) {}
```

### Apply Repository Pattern
```java
// Domain port (interface)
public interface UserRepository {
    User save(User user);
    Optional<User> findById(UserId id);
    List<User> findByEmail(String email);
}

// Infrastructure adapter
@Repository
@RequiredArgsConstructor
public class UserRepositoryAdapter implements UserRepository {
    private final UserJpaRepository jpaRepository;
    private final UserMapper mapper;

    @Override
    public User save(User user) {
        var entity = mapper.toEntity(user);
        var saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }
}
```

### Add Spring Security
```java
// Before: No authorization
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/api/admin/users")
public ResponseEntity<List<UserDto>> getAllUsers() {
    // Implementation
}

// After: Method-level security
@PreAuthorize("hasRole('ADMIN') or hasAuthority('USERS_READ')")
@GetMapping("/api/admin/users")
public ResponseEntity<List<UserDto>> getAllUsers() {
    // Implementation
}
```

## Output and Reporting

### Refactoring Summary
- **Files Modified**: List of changed files with line counts
- **Patterns Applied**: Specific patterns and improvements made
- **Test Impact**: New tests added, existing tests updated
- **Performance Changes**: Before/after metrics if available

### Quality Metrics
- **Cyclomatic Complexity**: Reduced from X to Y
- **Lines of Code**: Reduced by X%
- **Test Coverage**: Increased from X% to Y%
- **Dependencies**: Reduced coupling between components

### Next Steps
1. **Review changes** with team
2. **Run integration tests** in staging environment
3. **Monitor performance** after deployment
4. **Update documentation** for changed APIs

## Usage Examples

```bash
# Cleanup and style improvements
/devkit.java.refactor-class src/main/java/com/example/service/UserService.java cleanup

# Full architectural refactoring with backup
/devkit.java.refactor-class src/main/java/com/example/service/OrderService.java comprehensive backup

# Performance optimization only
/devkit.java.refactor-class src/main/java/com/example/repository/ProductRepository.java performance

# Dry run to see what would change
/devkit.java.refactor-class src/main/java/com/example/controller/UserController.java architecture dry-run

# Automatic complex class detection
/devkit.java.refactor-class
```

## Integration with Skills

This command works best with these skills:
- **spring-boot-crud-patterns**: For CRUD refactoring
- **spring-boot-test-patterns**: For test improvements
- **spring-boot-rest-api-standards**: For API refactoring
- **unit-test-service-layer**: For service layer testing

## Safety and Validation

- **Always preserve external behavior** while improving internal structure
- **Maintain backward compatibility** for public APIs
- **Create comprehensive tests** before refactoring critical paths
- **Use feature flags** for large, risky refactoring
- **Monitor production metrics** after deployment
