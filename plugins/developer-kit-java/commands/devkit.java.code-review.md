---
allowed-tools: Read, Write, Bash, Edit, Grep, Glob
argument-hint: [review-type] [file/directory-path] [options]
description: Comprehensive Java code review for enterprise Spring applications with security, performance, architecture and best practices analysis
model: inherit
---

# Java Enterprise Code Review - Spring Framework

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Commits**: !`git log --oneline -5`
- **Modified Files**: !`git diff --name-only HEAD~1`

## Review Configuration

The review will analyze: **$ARGUMENTS**

**Available review types:**
- `full` - Complete 360° review (default)
- `security` - Focus on vulnerabilities and security
- `performance` - Performance and scalability analysis
- `architecture` - Architectural patterns and design review
- `testing` - Test coverage and quality analysis
- `best-practices` - Spring/Java best practices verification

## Phase 1: Preliminary Analysis and Context

### 1.1 Identify Review Scope

IF "$1" CONTAINS ".java" OR "$1" CONTAINS "src/"
THEN Analyze specific file/directory: $ARGUMENTS
ELSE Analyze entire recently modified codebase
ENDIF

### 1.2 Base Project Metrics

- **Detected Technology**: Spring Boot (Boot 3.5.x preferred)
- **Java Version**: Verify Java 16+ for records, Java 21+ LTS
- **Spring Framework**: Spring Boot, Spring Security, Spring Data JPA, etc.
- **Build System**: Maven or Gradle
- **Database**: PostgreSQL, MySQL, H2 for testing

## Phase 2: Architecture and Design Patterns Review

### 2.1 Project Structure Analysis

Verify feature vs layer organization:
```
feature/
├── domain/           # Domain entities (Spring-free)
│   ├── model/
│   ├── repository/  # Domain ports (interfaces)
│   └── service/     # Domain services
├── application/     # Use cases (@Service)
│   ├── service/
│   └── dto/         # Immutable DTOs/records
├── presentation/    # Controllers and mappers
│   └── rest/
└── infrastructure/  # JPA adapters
    └── persistence/
```

### 2.2 SOLID Principles and Clean Architecture

- **Single Responsibility**: Each class has one responsibility
- **Open/Closed**: Extensible without modifying existing code
- **Liskov Substitution**: Subtypes substitutable with supertypes
- **Interface Segregation**: Specific, not generic interfaces
- **Dependency Inversion**: Depend on abstractions, not implementations

### 2.3 Spring Architectural Patterns

Verify correct pattern usage:
- **Constructor Injection**: `@RequiredArgsConstructor` (never field injection)
- **Repository Pattern**: Domain interfaces + infrastructure adapters
- **Service Layer**: Business logic in @Service separated from controllers
- **DTO Pattern**: Java 16+ records for immutable transfer objects
- **Configuration Management**: Spring profiles and @ConfigurationProperties

## Phase 3: Security and Vulnerabilities

### 3.1 OWASP Top 10 - Java Applications

- **A01: Broken Access Control**: Verify @PreAuthorize, @Secured
- **A02: Cryptographic Failures**: Password hashing, JWT validation
- **A03: Injection**: SQL injection with JPA, input validation
- **A04: Insecure Design**: Security-by-design architecture
- **A05: Security Misconfiguration**: Security headers, CORS
- **A06: Vulnerable Components**: Dependency scanning
- **A07: Authentication Failures**: Spring Security configuration
- **A08: Software/Data Integrity**: Signed JWT, checksum validation
- **A09: Logging/Monitoring**: Security logging, audit trail
- **A10: Server-Side Request Forgery**: SSRF prevention

### 3.2 Spring Security Best Practices

```java
// Correct SecurityFilterChain configuration
@Bean
public SecurityFilterChain applicationSecurity(HttpSecurity http) throws Exception {
    http
        .csrf(csrf -> csrf.disable()) // Only for stateless APIs
        .sessionManagement(session ->
            session.sessionCreationPolicy(STATELESS))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/public/**").permitAll()
            .requestMatchers("/api/admin/**").hasRole(ADMIN)
            .anyRequest().authenticated())
        .oauth2ResourceServer(oauth2 ->
            oauth2.jwt(Customizer.withDefaults()))
        .headers(headers -> headers
            .contentSecurityPolicy(csp -> csp
                .policyDirectives("default-src 'self'")));

    return http.build();
}
```

### 3.3 Input Validation and Sanitization

- **Bean Validation**: Proper use of @Valid, @NotNull, @Min, @Max
- **Custom Validators**: Validators for complex business logic
- **Input Sanitization**: Anti-XSS, SQL injection prevention
- **File Upload Security**: File type validation, size limits, virus scanning

## Phase 4: Performance and Scalability

### 4.1 Code Performance Analysis

- **Database Queries**: N+1 problems, missing indexes, query optimization
- **Caching Strategy**: Spring Cache @Cacheable, @CachePut, @CacheEvict
- **Async Processing**: @Async, CompletableFuture, WebFlux reactive
- **Memory Management**: Memory leaks, garbage collection optimization
- **Connection Pooling**: HikariCP configuration tuning

### 4.2 Spring Boot Performance Tuning

```yaml
# application.yml for production
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
        generate_statistics: false
  cache:
    type: redis
    redis:
      time-to-live: 600000
server:
  tomcat:
    threads:
      max: 200
      min-spare: 10
```

### 4.3 Monitoring and Observability

- **Spring Boot Actuator**: Health checks, metrics, info endpoints
- **Micrometer**: Metrics collection for Prometheus, Graphite
- **Distributed Tracing**: Spring Cloud Sleuth, Zipkin
- **APM Integration**: New Relic, DataDog, Dynatrace

## Phase 5: Code Quality and Best Practices

### 5.1 Modern Java Best Practices

- **Java 16+ Features**: Records, pattern matching, switch expressions
- **Immutability**: Final fields, immutable collections
- **Optional Usage**: Correct usage for absent values
- **Stream API**: Functional operations without side effects
- **Exception Handling**: Try-with-resources, custom exceptions

```java
// Best practices example
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public UserDto createUser(@Valid CreateUserRequest request) {
        // Business logic validation
        if (userRepository.existsByEmail(request.email())) {
            throw new UserAlreadyExistsException(request.email());
        }

        // Mapping with record pattern
        var user = new User(
            request.name(),
            request.email(),
            passwordEncoder.encode(request.password())
        );

        var saved = userRepository.save(user);

        return new UserDto(
            saved.getId(),
            saved.getName(),
            saved.getEmail(),
            saved.getCreatedAt()
        );
    }
}
```

### 5.2 Spring Boot Specific Patterns

- **Configuration Properties**: Type-safe configuration with @ConfigurationProperties
- **Profile Management**: Environment-specific configurations
- **Bean Lifecycle**: @PostConstruct, @PreDestroy usage
- **Event-Driven Architecture**: ApplicationEvent, @EventListener
- **Testing Strategy**: Slice tests, Testcontainers integration

## Phase 6: Testing and Quality

### 6.1 Testing Pyramid Strategy

- **Unit Tests** (70%): Fast isolated tests with Mockito
- **Integration Tests** (20%): Testcontainers for real dependencies
- **E2E Tests** (10%): Full application tests

### 6.2 JUnit 5 + Spring Boot Testing

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @Test
    @DisplayName("Should create user with hashed password")
    void shouldCreateUserWithHashedPassword() {
        // Given
        var request = new CreateUserRequest("test@example.com", "password");
        when(passwordEncoder.encode("password")).thenReturn("hashed");
        when(userRepository.save(any())).thenAnswer(i -> i.getArgument(0));

        // When
        var result = userService.createUser(request);

        // Then
        assertThat(result.email()).isEqualTo("test@example.com");
        verify(passwordEncoder).encode("password");
        verify(userRepository).save(argThat(user ->
            user.getPassword().equals("hashed")));
    }
}
```

### 6.3 Testcontainers Integration

```java
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldSaveAndRetrieveUser() {
        // Test with real database
    }
}
```

## Final Review Report

### Critical Issues (P0 - Fix Immediately)

- Security vulnerabilities CVSS > 7.0
- Authentication/authorization bypass
- Data loss or corruption risks
- Production instability
- Compliance violations (GDPR, PCI DSS)

### High Priority (P1 - Next Release)

- Performance bottlenecks impacting UX
- Missing critical test coverage
- Architectural anti-patterns
- Known vulnerable dependencies
- Code quality maintainability issues

### Medium Priority (P2 - Next Sprint)

- Non-critical performance optimizations
- Documentation gaps
- Refactoring opportunities
- Test quality improvements
- DevOps automation enhancements

### Low Priority (P3 - Backlog)

- Code style violations
- Minor code smells
- Documentation updates
- Cosmetic improvements

## Quality Metrics

### Test Coverage Targets
- **Unit Tests**: > 80%
- **Integration Tests**: > 60%
- **Total Coverage**: > 85%

### Code Quality Metrics
- **Cyclomatic Complexity**: < 10 per method
- **Maintainability Index**: > 70
- **Technical Debt Ratio**: < 5%
- **Code Duplication**: < 3%

### Performance Targets
- **Response Time**: < 200ms (95th percentile)
- **Throughput**: > 1000 req/sec
- **Memory Usage**: < 512MB steady state
- **Database Connections**: < 80% pool utilization

## Recommended Actions

1. **Immediate** (P0): Fix critical security vulnerabilities
2. **Current Sprint** (P1): Address performance and test gaps
3. **Next Sprint** (P2): Architectural refactoring
4. **Backlog** (P3): Technical debt reduction

## Integrated Support Tools

- **SonarQube**: Static analysis and quality gates
- **OWASP Dependency Check**: Vulnerability scanning
- **JaCoCo**: Code coverage reporting
- **Spring Boot Actuator**: Production monitoring
- **Testcontainers**: Real integration testing

---

## Execution Instructions

**Agent Selection**: To execute this code review, use the following agent with fallback:
- Primary: `spring-boot-code-review-expert`
- If not available: Use `developer-kit:spring-boot-code-review-expert` or fallback to `general-purpose` agent with `spring-boot-crud-patterns` skill