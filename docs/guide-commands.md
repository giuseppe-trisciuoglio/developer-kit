# Complete Guide to Developer Kit Commands

This guide provides comprehensive documentation for all commands developed for Claude Code, organized by category with detailed explanations, use cases, and practical examples.

---

## Table of Contents

1. [Java/Spring Boot Commands](#javaspring-boot-commands)
2. [Security Commands](#security-commands)
3. [Testing Commands](#testing-commands)
4. [DevKit Management Commands](#devkit-management-commands)
5. [Utility Commands](#utility-commands)
6. [Feature Development Command](#feature-development-command)
7. [Best Practices](#best-practices)
8. [Complete Workflow Example](#complete-workflow-example)

---

## Java/Spring Boot Commands

### `/devkit.java.code-review`

**Description**: Performs comprehensive code review of Java/Spring Boot applications analyzing architecture, security, performance, and best practices.

**When to use:**
- Before creating a pull request
- After completing a feature
- To verify existing code quality
- During refactoring of critical components

**Arguments:**
```bash
/devkit.java.code-review [review-type] [file/directory-path] [options]
```

**Available review types:**
- `full` - Complete 360° review (default)
- `security` - Focus on vulnerabilities and security
- `performance` - Performance and scalability analysis
- `architecture` - Architectural patterns verification
- `testing` - Test coverage and quality analysis
- `best-practices` - Spring/Java conventions verification

**Practical examples:**

```bash
# Complete project review
/devkit.java.code-review full

# Security review of specific service
/devkit.java.code-review security src/main/java/com/example/service/UserService.java

# Performance review of a module
/devkit.java.code-review performance src/main/java/com/example/order

# Architecture review of entire project
/devkit.java.code-review architecture
```

**Output:**

The command generates a detailed report with:
- **Critical Issues (P0)**: Problems requiring immediate resolution
- **High Priority (P1)**: Issues to resolve in next release
- **Medium Priority (P2)**: Improvements for next sprint
- **Low Priority (P3)**: Optimizations and suggestions for backlog

**Real-world use case:**
```bash
# Scenario: Completed JWT authentication feature
# Want to verify security before creating PR

/devkit.java.code-review security src/main/java/com/example/auth

# Expected output:
# - Spring Security configuration verification
# - JWT token management analysis
# - Input validation checks
# - Session management verification
# - OWASP Top 10 vulnerability report
```

**Analysis areas:**
- SOLID principles compliance
- Spring Boot patterns (constructor injection, proper bean scoping)
- Clean Architecture layer separation
- Security (Spring Security, OWASP Top 10)
- Performance (caching, database queries, connection pooling)
- Code quality (cyclomatic complexity, maintainability)
- Testing strategy (unit, integration, coverage)

---

### `/devkit.java.generate-crud`

**Description**: Generates complete CRUD implementation for a domain class following Spring Boot patterns.

**When to use:**
- Creating new entities with standard CRUD operations
- Quick scaffolding of new modules
- Maintaining architectural consistency
- Saving time on boilerplate code

**Arguments:**
```bash
/devkit.java.generate-crud [domain-class-name]
```

**Practical examples:**

```bash
# Generate CRUD for Product entity
/devkit.java.generate-crud Product

# Generate CRUD for User entity
/devkit.java.generate-crud User

# Generate CRUD for Order entity
/devkit.java.generate-crud Order
```

**Generated structure:**
```
/$DomainClass/
├── domain/
│   ├── model/
│   │   └── Product.java              # Domain aggregate (if not exists)
│   └── repository/
│       └── ProductRepository.java     # Repository interface
├── application/
│   ├── service/
│   │   └── ProductService.java        # Service with business logic
│   └── dto/
│       ├── CreateProductRequest.java  # DTO for creation
│       ├── UpdateProductRequest.java  # DTO for updates
│       └── ProductResponse.java       # Response DTO
├── presentation/
│   └── rest/
│       ├── ProductController.java     # REST controller
│       └── ProductMapper.java         # DTO <-> Entity mapper
└── infrastructure/
    └── persistence/
        ├── ProductEntity.java         # JPA entity
        ├── ProductJpaRepository.java  # Spring Data repository
        └── ProductRepositoryAdapter.java # Adapter pattern
```

**Real-world use case:**
```bash
# Scenario: Need to implement product management module
# with standard CRUD operations

/devkit.java.generate-crud Product

# Output:
# ✅ ProductController.java - REST endpoints:
#    GET    /api/products          - List all products (paginated)
#    GET    /api/products/{id}     - Product details
#    POST   /api/products          - Create new product
#    PUT    /api/products/{id}     - Update product
#    DELETE /api/products/{id}     - Delete product
#
# ✅ ProductService.java - Business logic
# ✅ ProductRepository.java - Domain port
# ✅ ProductEntity.java - JPA entity
# ✅ DTO classes - Request/Response objects
# ✅ Test files - Unit and integration tests
```

**Applied patterns:**
- ✅ Constructor injection only
- ✅ Java records for immutable DTOs
- ✅ @Valid for input validation
- ✅ ResponseEntity with correct HTTP status codes
- ✅ @Transactional on service methods
- ✅ Pagination on list endpoints
- ✅ Error handling with ResponseStatusException

---

### `/devkit.java.architect-review`

**Description**: Comprehensive architectural review for Java applications focusing on Clean Architecture, DDD, and Spring Boot patterns.

**When to use:**
- Major refactoring initiatives
- Architecture quality assessment
- Identifying architectural debt
- Before major version releases

**Arguments:**
```bash
/devkit.java.architect-review [package-path] [focus-area]
```

**Focus areas:**
- `clean-architecture` - Clean Architecture layer separation
- `ddd` - Domain-Driven Design patterns
- `spring-boot` - Spring Boot specific patterns
- `security` - Security architecture
- `performance` - Performance and scalability
- `testing` - Test architecture
- `microservices` - Microservices architecture
- `all` - Complete architectural review (default)

**Practical examples:**

```bash
# Complete architecture review
/devkit.java.architect-review

# DDD patterns review for specific module
/devkit.java.architect-review com.example.users ddd

# Security architecture review
/devkit.java.architect-review security

# Performance architecture review for order module
/devkit.java.architect-review src/main/java/com/example/order performance
```

**Assessment output:**
- Overall architectural quality score (1-10 scale)
- SOLID principles compliance
- Clean Architecture layer separation
- DDD patterns implementation
- Spring Boot best practices
- Identified violations and anti-patterns
- Specific recommendations with priority (High/Medium/Low)
- Architecture improvement plan (short/medium/long-term)

---

### `/devkit.java.dependency-audit`

**Description**: Comprehensive dependency analysis for Java/Maven/Gradle projects identifying security vulnerabilities, licensing issues, outdated packages, and supply chain risks.

**When to use:**
- Regular security audits (weekly/monthly)
- Before production releases
- After dependency updates
- Security compliance requirements

**Arguments:**
```bash
/devkit.java.dependency-audit [scope] [focus] [format]
```

**Scopes:**
- `all` - Complete dependency audit (default)
- `security` - CVEs and security vulnerabilities only
- `licenses` - License compliance and compatibility
- `outdated` - Outdated dependencies with update recommendations
- `supply-chain` - Supply chain security risks
- `transitive` - Focus on transitive dependencies
- `<groupId:artifactId>` - Specific dependency analysis

**Focus areas:**
- `comprehensive` - All analysis categories (default)
- `critical-only` - Only critical and high severity issues
- `production` - Focus on production runtime dependencies
- `direct` - Only direct dependencies
- `cve` - CVE database cross-reference
- `compliance` - License and regulatory compliance

**Output formats:**
- `report` - Detailed markdown report (default)
- `summary` - Executive summary with metrics
- `json` - Machine-readable JSON format
- `sarif` - SARIF format for CI/CD integration
- `remediation` - Actionable fix commands

**Practical examples:**

```bash
# Complete dependency audit
/devkit.java.dependency-audit all comprehensive report

# Security vulnerabilities only
/devkit.java.dependency-audit security critical-only summary

# License compliance check
/devkit.java.dependency-audit licenses compliance report

# Outdated dependencies
/devkit.java.dependency-audit outdated

# Specific dependency analysis
/devkit.java.dependency-audit org.springframework.boot:spring-boot-starter-web
```

**Analysis includes:**
- **Vulnerability scanning**: OWASP Dependency-Check, Snyk, GitHub Advisory Database
- **License compliance**: Compatibility matrix, legal risk assessment
- **Outdated analysis**: Update priority scoring, maintenance status
- **Supply chain**: Typosquatting detection, maintainer changes, package health
- **Automated remediation**: Fix scripts, pull request generation

**Real-world use case:**
```bash
# Pre-production security audit
/devkit.java.dependency-audit security critical-only report

# Expected output:
# - 3 high-severity CVEs requiring immediate attention
# - jackson-databind: CVE-2024-XXXX (update to 2.15.3)
# - commons-collections: CVE-2015-YYYY (replace vulnerable version)
# - Automated fix script generated
# - Pull request template provided
```

---

### `/devkit.java.generate-docs`

**Description**: Generate comprehensive Java project documentation including API docs, architecture diagrams, and Javadoc.

**When to use:**
- Project onboarding documentation
- API documentation for external consumers
- Architecture documentation for team
- Release documentation preparation

**Arguments:**
```bash
/devkit.java.generate-docs [project-path] [doc-types] [output-format]
```

**Documentation types:**
- `api` - REST API documentation with OpenAPI/Swagger
- `architecture` - System architecture and design documentation
- `javadoc` - Comprehensive Javadoc generation
- `readme` - Project README and setup guides
- `full` - Complete documentation suite (default)

**Output formats:**
- `html` - HTML documentation site (default)
- `markdown` - Markdown files
- `asciidoc` - AsciiDoc format
- `confluence` - Confluence-compatible format

**Practical examples:**

```bash
# Generate all documentation
/devkit.java.generate-docs

# Generate API documentation only
/devkit.java.generate-docs . api html

# Generate architecture documentation in markdown
/devkit.java.generate-docs . architecture markdown

# Generate documentation for specific project
/devkit.java.generate-docs /path/to/project full asciidoc
```

**Generated documentation:**

1. **API Documentation:**
   - OpenAPI 3.0 specification
   - Interactive Swagger UI
   - Endpoint documentation with examples
   - Request/response schemas
   - Authentication documentation

2. **Architecture Documentation:**
   - System architecture diagrams (Mermaid)
   - Component architecture
   - Data flow diagrams
   - Sequence diagrams for key workflows
   - Technology stack overview

3. **Javadoc:**
   - Complete API reference
   - Package documentation
   - Class and method documentation
   - Cross-references to Spring documentation
   - Grouped by layer (web, service, data, config)

4. **README:**
   - Project overview with badges
   - Features list
   - Prerequisites and installation
   - Quick start guide
   - Testing instructions
   - Deployment guide
   - Configuration reference
   - Contributing guidelines

**Output structure:**
```
docs/
├── api/
│   ├── openapi.json
│   ├── swagger-ui.html
│   └── postman-collection.json
├── architecture/
│   ├── system-diagram.md
│   ├── data-flow.md
│   └── deployment-diagram.md
├── javadoc/
├── guides/
│   ├── user-guide.md
│   ├── developer-guide.md
│   └── deployment-guide.md
└── README.md
```

---

### `/devkit.java.refactor-class`

**Description**: Intelligent refactoring assistant for complex Java classes with architectural analysis and Spring Boot patterns.

**When to use:**
- Simplifying complex classes
- Improving testability
- Applying architectural patterns
- Performance optimization
- Security enhancements

**Arguments:**
```bash
/devkit.java.refactor-class [class-file-path] [refactoring-scope] [options]
```

**Refactoring scopes:**
- `cleanup` - Code cleanup and style improvements (default)
- `architecture` - Architectural pattern improvements
- `performance` - Performance optimizations
- `security` - Security enhancements
- `testing` - Testability improvements
- `comprehensive` - All improvements (full refactor)

**Options:**
- `dry-run` - Preview changes without applying
- `backup` - Create backup branch before refactoring
- `validate-only` - Only validate and report issues

**Practical examples:**

```bash
# Cleanup and style improvements
/devkit.java.refactor-class src/main/java/com/example/service/UserService.java cleanup

# Full architectural refactoring with backup
/devkit.java.refactor-class src/main/java/com/example/service/OrderService.java comprehensive backup

# Performance optimization only
/devkit.java.refactor-class src/main/java/com/example/repository/ProductRepository.java performance

# Dry run to preview changes
/devkit.java.refactor-class src/main/java/com/example/controller/UserController.java architecture dry-run

# Automatic complex class detection and refactoring
/devkit.java.refactor-class
```

**Refactoring patterns applied:**

1. **Extract Method/Service** - Breaking down complex methods
2. **Replace with Record/Value Object** - Immutable data structures
3. **Apply Repository Pattern** - Domain interfaces + infrastructure adapters
4. **Add Spring Security** - Method-level authorization
5. **Optimize Database Queries** - Eliminate N+1 problems
6. **Add Caching** - Spring Cache annotations
7. **Convert to Async** - @Async for non-blocking operations

**Quality metrics:**
- Cyclomatic complexity reduction
- Lines of code reduction
- Test coverage increase
- Dependency coupling reduction

### `/devkit.generate-refactoring-tasks`

**Description**: Generate a step-by-step refactoring plan for complex Java classes using the java-refactor-expert agent.

**When to use:**
- Planning a complex refactoring
- Breaking down large classes into manageable tasks
- Ensuring DDD compliance before coding
- Creating a roadmap for legacy code modernization

**Arguments:**
```bash
/devkit.generate-refactoring-tasks [class-file-path]
```

**Practical examples:**

```bash
# Generate refactoring tasks for a legacy service
/devkit.generate-refactoring-tasks src/main/java/com/example/legacy/MonolithicService.java

# Plan refactoring for a complex controller
/devkit.generate-refactoring-tasks src/main/java/com/example/controller/ComplexController.java
```

**Output:**
- A markdown file `docs/refactoring/[ClassName]-refactoring-tasks.md` containing:
    - Analysis of the current class
    - Step-by-step refactoring tasks
    - Verification steps for each task
    - DDD alignment checks

---

### `/devkit.java.security-review`

**Description**: Comprehensive security review for Java enterprise applications (Spring, Jakarta EE).

**When to use:**
- Pre-production security audits
- Compliance requirements (SOC2, PCI-DSS)
- After security incidents
- Regular security assessments

**Arguments:**
```bash
/devkit.java.security-review [scope] [options]
```

**Scopes:**
- `code` - Source code security analysis (default)
- `config` - Configuration security review
- `dependencies` - Dependency vulnerability scan
- `infrastructure` - Docker/K8s security
- `full` - Complete security audit

**Analysis areas:**

1. **OWASP Top 10 for Java:**
   - A01: Broken Access Control (@PreAuthorize, @Secured)
   - A02: Cryptographic Failures (BCrypt, PBKDF2)
   - A03: Injection (SQL, NoSQL, Command, LDAP)
   - A04: Insecure Design (architecture patterns)
   - A05: Security Misconfiguration (Spring Boot, Actuator)
   - A06: Vulnerable Components (OWASP Dependency-Check)
   - A07: Authentication Failures (Spring Security)
   - A08: Data Integrity (JAR signatures, deserialization)
   - A09: Logging/Monitoring (security events)
   - A10: SSRF (URL validation)

2. **Spring Security Analysis:**
   - Authentication providers
   - Authorization rules
   - Session management
   - JWT implementation
   - OAuth2/OpenID Connect

3. **Database Security:**
   - JPA/Hibernate security
   - SQL injection prevention
   - Connection security
   - Credential management

4. **API Security:**
   - Input validation
   - Rate limiting
   - API authentication
   - Response security headers

**Practical examples:**

```bash
# Complete security audit
/devkit.java.security-review full

# Code security analysis only
/devkit.java.security-review code

# Configuration security review
/devkit.java.security-review config

# Dependency vulnerabilities scan
/devkit.java.security-review dependencies
```

**Output priorities:**
- **Critical (P0)**: Remote code execution, authentication bypass, data exposure
- **High (P1)**: Outdated CVEs, insecure configurations, missing security headers
- **Medium (P2)**: Logging gaps, insufficient validation, access control improvements
- **Low (P3)**: Documentation, code style security, additional testing

---

### `/devkit.ts.security-review`

**Description**: Comprehensive security review for TypeScript/Node.js applications (Next.js, NestJS, Express, etc.).

**When to use:**
- Security audit of TypeScript applications
- Framework-specific security validation
- Pre-production security checks
- OWASP compliance verification
- npm/dependency vulnerability assessment

**Arguments:**
```bash
/devkit.ts.security-review [scope] [options]
```

**Scopes:**
- `code` - TypeScript code security analysis (default)
- `dependencies` - npm/yarn package vulnerability scan
- `config` - Framework configuration security
- `infrastructure` - Docker/K8s security
- `full` - Complete security audit

**Analysis areas:**

1. **OWASP Top 10 for TypeScript:**
   - A01: Broken Access Control (Express middleware, NestJS guards)
   - A02: Cryptographic Failures (Node.js crypto, bcryptjs)
   - A03: Injection (SQL in TypeORM/Prisma, Command injection)
   - A04: Insecure Design (missing security middleware)
   - A05: Security Misconfiguration (CORS, exposed endpoints)
   - A06: Vulnerable Components (npm audit, CVE detection)
   - A07: Authentication Failures (JWT, session management)
   - A08: Data Integrity (package-lock verification)
   - A09: Logging/Monitoring (Winston, security events)
   - A10: SSRF (axios, node-fetch URL validation)

2. **Framework-Specific Analysis:**
   - **Next.js**: API routes, SSR security, middleware
   - **NestJS**: Guards, interceptors, Passport strategies
   - **Express.js**: Middleware security, route protection
   - **Frontend**: React/Vue XSS prevention, CSP implementation

3. **Dependency Security:**
   - npm/yarn vulnerability scanning
   - Package integrity verification
   - Outdated package detection
   - Malicious package analysis

**Practical examples:**

```bash
# Complete TypeScript security audit
/devkit.ts.security-review full

# Code security analysis only
/devkit.ts.security-review code

# Dependency vulnerability scan
/devkit.ts.security-review dependencies

# Next.js specific security
/devkit.ts.security-review code --framework=nextjs
```

**Output includes:**
- Vulnerability severity classification (Critical/High/Medium/Low)
- Framework-specific security recommendations
- Automated fix suggestions for dependencies
- Configuration security improvements

---

### `/devkit.generate-security-assessment`

**Description**: Generate comprehensive security assessment document after security audit completion.

**When to use:**
- After running `/devkit.java.security-review` or `/devkit.ts.security-review`
- Creating security documentation for stakeholders
- Compliance reporting (GDPR, ISO 27001, PCI-DSS)
- Security architecture documentation
- Incident response planning

**Arguments:**
```bash
/devkit.generate-security-assessment [language] [output-format]
```

**Languages:**
- `en-US` - English documentation (default)
- `it-IT` - Italian documentation
- `es-ES` - Spanish documentation
- `fr-FR` - French documentation

**Output formats:**
- `markdown` - Structured Markdown document (default)
- `pdf` - Professional PDF document
- `docx` - Microsoft Word format
- `html` - Interactive HTML report

**Generated document structure:**

1. **Project Overview & Security Scope**
   - Application description and objectives
   - Security boundaries and scope definition
   - Technology stack identification

2. **Identity & Access Management**
   - Authentication mechanisms analysis
   - Authorization patterns (RBAC)
   - Session management security

3. **Data Protection**
   - Encryption analysis (in transit, at rest)
   - Data masking and PII protection
   - Backup and recovery strategies

4. **Threat Protection**
   - Firewall and WAF configuration
   - DDoS protection measures
   - Vulnerability monitoring procedures

5. **Code Security**
   - Secure coding practices
   - Code review processes
   - Security testing strategies

6. **Incident Management**
   - Response procedures and timelines
   - Reporting and documentation
   - Communication protocols

7. **Training & Awareness**
   - Security training programs
   - Attack simulations and drills

8. **Compliance & Regulations**
   - Regulatory framework compliance
   - Security audit procedures

9. **Maintenance & Updates**
   - Patch management processes
   - Continuous monitoring strategies

10. **Appendices**
    - Security glossary
    - Useful resources and references

**Practical examples:**

```bash
# Generate English security assessment in Markdown (default)
/devkit.generate-security-assessment en-US markdown

# Generate English assessment in PDF format
/devkit.generate-security-assessment en-US pdf

# Generate Italian assessment for stakeholders
/devkit.generate-security-assessment it-IT docx

# Generate Spanish assessment for stakeholders
/devkit.generate-security-assessment es-ES docx
```

**Key features:**
- Multi-language support for international teams
- Professional formatting for executive review
- Comprehensive security coverage based on audit findings
- Actionable recommendations with priority levels
- Compliance framework mapping
- Integration with previous security audit results

**Usage workflow:**
1. Run security audit: `/devkit.java.security-review` or `/devkit.ts.security-review`
2. Review findings and implement critical fixes
3. Generate assessment document: `/devkit.generate-security-assessment`
4. Share with stakeholders and track remediation progress

---

### `/devkit.java.upgrade-dependencies`

**Description**: Safe and incremental dependency upgrade strategy for Java/Maven/Gradle projects with breaking change detection and migration guides.

**When to use:**
- Regular dependency maintenance
- Security vulnerability patching
- Major framework upgrades (Spring Boot)
- Keeping dependencies current

**Arguments:**
```bash
/devkit.java.upgrade-dependencies [scope] [strategy] [version]
```

**Scopes:**
- `all` - Analyze all dependencies (default)
- `spring` - Spring Boot and Spring Framework
- `testing` - Test dependencies (JUnit, Mockito, Testcontainers)
- `security` - Prioritize security vulnerabilities
- `direct` - Only direct dependencies
- `<groupId:artifactId>` - Specific dependency

**Strategies:**
- `analyze` - Analyze and report available updates (default)
- `plan` - Create detailed upgrade plan
- `migrate` - Generate migration guide for major versions
- `execute` - Execute planned upgrades (requires confirmation)
- `rollback` - Create rollback strategy

**Target versions:**
- Version number (e.g., `3.2.0`, `5.3.31`)
- `latest` - Latest stable release
- `latest-minor` - Latest minor version
- `latest-patch` - Latest patch version

**Practical examples:**

```bash
# Analyze all dependencies
/devkit.java.upgrade-dependencies all analyze

# Plan Spring Boot upgrade
/devkit.java.upgrade-dependencies spring plan

# Generate migration guide for major Spring Boot upgrade
/devkit.java.upgrade-dependencies spring migrate 3.2.0

# Execute safe patch updates
/devkit.java.upgrade-dependencies all execute latest-patch

# Analyze specific dependency
/devkit.java.upgrade-dependencies org.springframework.boot:spring-boot-starter-web analyze
```

**Upgrade strategies:**

1. **Patch Updates (Safe)** - Same day, smoke tests
2. **Minor Updates (Careful)** - 1-2 days, full regression
3. **Major Updates (Planned)** - 3-7 days, comprehensive testing
4. **Spring Boot Upgrade (Strategic)** - 1-2 sprints, incremental path

**Risk assessment:**
- **PATCH** (Low risk): Bug fixes, no breaking changes
- **MINOR** (Medium risk): New features, backward compatible
- **MAJOR** (High risk): Breaking changes, API modifications
- **SECURITY** (Critical): Vulnerabilities requiring immediate action

**Migration guide includes:**
- Breaking changes documentation
- Step-by-step migration instructions
- Code examples (before/after)
- Testing checklist
- Rollback plan
- Estimated effort

---

## Testing Commands

### `/devkit.java.write-unit-tests`

**Description**: Generate comprehensive JUnit 5 unit tests for Java classes with Mockito mocking and AssertJ assertions.

**When to use:**
- Adding tests to new code
- Improving test coverage
- Refactoring with test safety net
- TDD (Test-Driven Development)

**Arguments:**
```bash
/devkit.java.write-unit-tests <class-file-path>
```

**Practical examples:**

```bash
# Generate unit tests for service class
/devkit.java.write-unit-tests src/main/java/com/example/service/UserService.java

# Generate unit tests for controller
/devkit.java.write-unit-tests src/main/java/com/example/controller/ProductController.java

# Generate unit tests for mapper
/devkit.java.write-unit-tests src/main/java/com/example/mapper/OrderMapper.java
```

**Automatically selects testing strategy based on class type:**

- **@Service classes**: Service layer testing with Mockito
- **@RestController**: Controller testing with MockMvc
- **Mappers/Converters**: Bidirectional mapping tests
- **Utility classes**: Static method testing
- **Validators**: Bean validation testing
- **Exception handlers**: @ControllerAdvice testing
- **Caching logic**: Cache behavior testing
- **Scheduled/Async**: @Scheduled and @Async testing
- **Security**: Authorization testing
- **External APIs**: WireMock testing

**Generated test structure:**

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
  void shouldCreateUser_whenValidRequest() {
    // Arrange
    when(userRepository.existsByEmail("test@example.com")).thenReturn(false);
    when(passwordEncoder.encode("password")).thenReturn("hashed");
    
    // Act
    var result = userService.createUser(new CreateUserRequest("test@example.com", "password"));
    
    // Assert
    assertThat(result).isNotNull();
    assertThat(result.email()).isEqualTo("test@example.com");
    verify(userRepository).save(any(User.class));
  }
}
```

**Test coverage includes:**
- ✅ Happy path scenarios
- ✅ Edge cases and boundary conditions
- ✅ Null value handling
- ✅ Empty collections
- ✅ Exception scenarios
- ✅ Validation failures
- ✅ Mock interaction verification

**Best practices applied:**
- AAA pattern (Arrange, Act, Assert)
- Descriptive test names (should...when... pattern)
- One assertion concept per test
- Fast tests (< 50ms per test)
- No Spring context loading (pure unit tests)
- AssertJ fluent assertions

---

### `/devkit.java.write-integration-tests`

**Description**: Generate comprehensive integration tests for Spring Boot classes using Testcontainers with `@ServiceConnection` pattern.

**When to use:**
- Testing with real database
- Testing complete workflows
- Integration with external systems
- End-to-end feature testing

**Arguments:**
```bash
/devkit.java.write-integration-tests [class-path]
```

**Practical examples:**

```bash
# Generate integration tests for controller
/devkit.java.write-integration-tests src/main/java/com/example/controller/UserController.java

# Generate integration tests for service with caching
/devkit.java.write-integration-tests src/main/java/com/example/service/ProductService.java

# Generate integration tests for repository
/devkit.java.write-integration-tests src/main/java/com/example/repository/OrderRepository.java
```

**Automatic container selection:**
- **@Repository/@DataJpaTest**: PostgreSQL/MySQL container
- **@Service with caching**: Redis container
- **@RestController**: MockMvc + backend containers
- **Message consumers**: RabbitMQ/Kafka container
- **MongoDB repositories**: MongoDB container

**Generated test with Testcontainers:**

```java
@SpringBootTest
@Testcontainers
class UserServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb");

    @Container
    @ServiceConnection
    static GenericContainer<?> redis = new GenericContainer<>(
        DockerImageName.parse("redis:7-alpine"))
        .withExposedPorts(6379);

    @Autowired
    private UserService userService;

    @Test
    void shouldCreateAndRetrieveUser() {
        // Test with real database and cache
        User created = userService.createUser("test@example.com", "Test User");
        User retrieved = userService.findById(created.getId());
        
        assertThat(retrieved).isNotNull();
        assertThat(retrieved.getEmail()).isEqualTo("test@example.com");
    }
}
```

**Key features:**
- ✅ `@ServiceConnection` for Spring Boot 3.5+ automatic wiring
- ✅ Static containers for JVM-level reuse
- ✅ Real dependencies (no mocks)
- ✅ Complete scenario testing
- ✅ Performance optimized (< 500ms per test)

**Required dependencies:**
- spring-boot-starter-test
- testcontainers:junit-jupiter (1.19.0+)
- testcontainers:postgresql (or other databases)

---

## DevKit Management Commands

### `/devkit.generate-changelog`

**Description**: Generate and maintain project changelog following Keep a Changelog standard with Git integration and Conventional Commits support.

**When to use:**
- Creating initial changelog
- Release preparation
- Version documentation
- Change tracking

**Arguments:**
```bash
/devkit.generate-changelog [action] [version] [format]
```

**Actions:**
- `init` - Create initial CHANGELOG.md
- `update` - Update changelog with changes since last tag
- `release` - Generate changelog entry for new release
- `preview` - Preview changes without writing
- `validate` - Validate existing CHANGELOG.md format

**Versions:**
- Version number (e.g., `1.2.3`, `2.0.0`)
- `auto` - Auto-detect from build files (default)
- `latest-tag` - Use latest Git tag
- `snapshot` - Mark as unreleased/snapshot

**Formats:**
- `keepachangelog` - Keep a Changelog format (default)
- `conventional` - Conventional Changelog format
- `github` - GitHub Release Notes format
- `json` - Structured JSON format

**Practical examples:**

```bash
# Initialize new changelog
/devkit.generate-changelog init

# Update changelog with auto-detected version
/devkit.generate-changelog update auto

# Preview changes without writing
/devkit.generate-changelog preview

# Create release entry for specific version
/devkit.generate-changelog release 1.2.0

# Validate existing changelog
/devkit.generate-changelog validate

# Generate in GitHub format
/devkit.generate-changelog update 1.2.0 github
```

**Automatic version detection:**
- Maven: `pom.xml` version
- Gradle: `build.gradle` or `build.gradle.kts` version
- npm: `package.json` version
- Python: `setup.py` or `pyproject.toml` version
- Rust: `Cargo.toml` version
- Git tags: Fallback to latest tag

**Conventional Commits support:**
- `feat:` → Added section
- `fix:` → Fixed section
- `security:` → Security section
- `refactor:`, `perf:`, `style:` → Changed section
- `remove:`, `delete:` → Removed section
- `deprecate:` → Deprecated section
- `BREAKING CHANGE` → Breaking Changes section

**Changelog format:**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features for next release

## [1.2.0] - 2024-01-15

### Added
- User authentication with JWT tokens
- Health check endpoints
- Redis caching for sessions

### Changed
- Upgraded dependencies to latest versions
- Improved error handling

### Fixed
- Memory leak in background task
- Security vulnerability in authentication

### Security
- Updated vulnerable dependencies
- Implemented CSRF protection

[Unreleased]: https://github.com/username/project/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/username/project/compare/v1.1.0...v1.2.0
```

**Build system integration:**
- Maven Changes Plugin
- Gradle Release Plugin
- npm version scripts
- GitHub Actions automated releases

---

### `/devkit.verify-skill`

**Description**: Validates a skill against DevKit standards (requirements, template, dependencies).

**When to use:**
- Before committing new skills
- After modifying existing skills
- Quality assurance checks
- CI/CD skill validation

**Arguments:**
```bash
/devkit.verify-skill [skill-name]
```

**Validation checks:**

1. **Existence Check**
   - Searches in `.claude/skills/`, `~/.claude/skills/`, and `./skills/` directories
   - Verifies SKILL.md file exists

2. **Requirements Conformance**
   - YAML frontmatter validation
   - Required fields: name, description, allowed-tools, category, tags, version
   - Field format validation (name: lowercase-hyphen, version: semver)
   - Description quality (includes WHAT and WHEN)

3. **Template Adherence**
   - Required sections present
   - Metadata alignment
   - Content organization
   - Progressive complexity in examples

4. **Dependency Validation** (Context7 or u2m)
   - Library versions current
   - Trust score adequate (≥ 7.0)
   - Breaking changes documented

**Practical examples:**

```bash
# Validate specific skill
/devkit.verify-skill spring-boot-crud-patterns

# Validate after modifications
/devkit.verify-skill langchain4j-rag-implementation-patterns
```

**Success output:**
```
✅ Validation completed: The skill 'spring-boot-crud-patterns' complies with all standards.

Details:
- ✅ SKILL.md file present and valid
- ✅ Frontmatter correct (name, description)
- ✅ Structure conforms to template
- ✅ All referenced files exist
- ✅ Dependencies validated
```

**Failure output:**
```
❌ Validation failed for the skill 'example-skill'.

Required actions:

* **Requirements:** The `name` field contains uppercase characters. Must use only lowercase letters, numbers, and hyphens.
* **Template:** The "When to Use This Skill" section is missing.
* **File:** The `reference.md` file is referenced but does not exist.
* **Dependencies:** The 'spring-boot' library uses version 2.7.x. Recommended: 3.2.x (Context7 Trust Score: 9.2).
* **Content:** Description does not specify WHEN to use the skill.
```

---

## Utility Commands

### `/devkit.prompt-optimize`

**Description**: Expert prompt optimization using advanced techniques (CoT, few-shot, constitutional AI) for LLM performance enhancement.

**When to use:**
- Improving prompt quality
- Reducing token usage
- Enhancing consistency
- Production prompt preparation

**Arguments:**
```bash
/devkit.prompt-optimize [prompt-text] [target-model] [optimization-level]
```

**Target models:**
- `claude-4.5-sonnet` (default)
- `claude-4-opus`
- `claude-4.5-haiku`
- `gpt-5`
- `gpt-5-mini`
- `gemini-2.5-pro`

**Optimization levels:**
- `basic` - Quick improvements (structure, clarity, basic CoT)
- `standard` - Comprehensive enhancement (CoT, few-shot, safety)
- `advanced` - Production-ready (full optimization with testing)

**Practical examples:**

```bash
# Optimize prompt file
/devkit.prompt-optimize prompts/code-review-prompt.txt

# Optimize inline prompt
/devkit.prompt-optimize "Generate unit tests for UserService" claude-3.5-sonnet standard

# Advanced optimization for production
/devkit.prompt-optimize "Analyze security vulnerabilities" gpt-4 advanced
```

**Optimization techniques applied:**
- **Chain-of-Thought (CoT)**: Step-by-step reasoning
- **Few-Shot Learning**: Strategic examples
- **Constitutional AI**: Self-critique and safety
- **Structured Output**: JSON/XML formats
- **Meta-Prompting**: Dynamic prompt generation

**Output includes:**
- Complete optimized prompt (saved to `optimized-prompt.md`)
- Optimization report (before/after analysis)
- Applied techniques with impact metrics
- Performance projections
- Implementation guidelines

---

### `/devkit.write-a-minute-of-a-meeting`

**Description**: Generate professional meeting minutes from transcripts or notes.

**When to use:**
- After team meetings
- Client meetings documentation
- Decision tracking
- Action item management

**Arguments:**
```bash
/devkit.write-a-minute-of-a-meeting [transcript-file] [meeting-title] [date]
```

**Practical examples:**

```bash
# Generate minutes from transcript
/devkit.write-a-minute-of-a-meeting meeting-transcript.txt "Sprint Planning" "2024-01-15"

# Generate from notes file
/devkit.write-a-minute-of-a-meeting notes.md "Architecture Review"
```

**Generated document structure:**

1. **Executive Summary** - Key outcomes and decisions (3-4 sentences)
2. **Agenda Items Discussed** - Summary per item with attributions
3. **Decisions Made** - Final decisions with approvers
4. **Action Items** - Table with tasks, responsible persons, deadlines
5. **Open Issues/Next Steps** - Unresolved topics
6. **Next Meeting** - Date and time if established

**Meeting minute format:**

```markdown
# Meeting Minutes: Sprint Planning

**Date**: 2024-01-15  
**Location**: Zoom  
**Attendees**: John Doe, Jane Smith, Bob Johnson  

## Executive Summary

The team reviewed sprint progress, identified blockers, and planned next sprint goals. Key decision: adopt new deployment strategy. Three action items assigned with deadlines.

## Agenda Items Discussed

### Sprint Progress Review
- Completed 8 of 10 user stories
- Integration tests delayed due to infrastructure issues
- **Jane Smith** reported database performance improvements

### Next Sprint Planning
- Focus on technical debt reduction
- Allocate 30% capacity to refactoring
- **John Doe** proposed new code review process

## Decisions Made

| Decision | Proposed By | Approved By |
|----------|-------------|-------------|
| Adopt blue-green deployment | John Doe | All attendees |
| Increase test coverage target to 85% | Jane Smith | Tech Lead |

## Action Items

| Action | Responsible | Deadline |
|--------|------------|----------|
| Setup blue-green deployment pipeline | DevOps Team | 2024-01-22 |
| Document new code review process | John Doe | 2024-01-20 |
| Refactor authentication module | Jane Smith | 2024-01-29 |

## Open Issues

- Infrastructure capacity planning needed
- Decision on microservices migration strategy pending

## Next Meeting

**Date**: 2024-01-22 at 10:00 AM  
**Agenda**: Deployment strategy review and Q1 planning
```

---

## Feature Development Command

### `/devkit.feature-development`

**Description**: Guided feature development with systematic 7-phase approach using specialized agents for comprehensive codebase analysis, architecture design, and quality review.

**When to use:**
- Building new features from scratch
- Complex feature requiring deep understanding of existing codebase
- When you need architectural guidance before implementation
- For systematic, well-documented feature development
- When working with unfamiliar codebases

**Arguments:**
```bash
/devkit.feature-development [feature-description]
```

**The 7 Phases:**

1. **Discovery** - Understand what needs to be built
2. **Codebase Exploration** - Analyze existing patterns and similar features
3. **Clarifying Questions** - Resolve all ambiguities before designing
4. **Architecture Design** - Design multiple approaches with trade-offs
5. **Implementation** - Build the feature following chosen architecture
6. **Quality Review** - Comprehensive code review with specialized agents
7. **Summary** - Document what was accomplished

**Specialized Agents Used:**
- **explorer** - Traces execution paths and maps architecture
- **architect** - Designs complete implementation blueprints
- **code-reviewer** - Reviews code with confidence-based filtering

**Practical examples:**

```bash
# Simple feature
/devkit.feature-development Add user authentication

# Complex feature with description
/devkit.feature-development Implement real-time notifications using WebSockets

# Integration feature
/devkit.feature-development Add payment processing with Stripe integration

# UI feature
/devkit.feature-development Create dashboard with charts and filters
```

**Key Benefits:**
- **Systematic Approach**: 7-phase methodology ensures comprehensive development
- **Codebase Understanding**: Deep analysis before making changes
- **Architecture Guidance**: Multiple design approaches with trade-off analysis
- **Quality Assurance**: Multi-perspective code review with specialized agents
- **Documentation**: Complete summary of decisions and implementation

**Execution Instructions with Fallback:**
The command uses agents with automatic fallback:
- Primary: `general-*` agents
- If not available: `developer-kit:general-*` agents
- Final fallback: `general-purpose` agent

---

## Best Practices

### Command Workflow Principles

1. **Progressive Quality Checks**
   - Generate code → Write tests → Code review → Security review
   - Small, incremental changes over big-bang refactoring
   - Always run tests before and after changes

2. **Documentation First**
   - Generate documentation alongside code
   - Keep README and API docs up-to-date
   - Document architectural decisions

3. **Security by Default**
   - Regular dependency audits
   - Security reviews before production
   - Follow OWASP Top 10 guidelines

4. **Test Coverage**
   - Aim for 80%+ unit test coverage
   - 60%+ integration test coverage
   - 85%+ total coverage target

### When to Use Which Command

**During Development:**
1. `/devkit.java.generate-crud` - Scaffold new entities
2. `/devkit.java.write-unit-tests` - Generate tests for new code
3. `/devkit.java.code-review` - Verify quality before commit

**Before Pull Request:**
1. `/devkit.java.code-review full` - Complete review
2. `/devkit.java.security-review` - Security check (Java)
3. `/devkit.ts.security-review` - Security check (TypeScript)
4. `/devkit.java.write-integration-tests` - Add integration tests

**Pre-Production:**
1. `/devkit.java.security-review full` - Complete Java security audit
2. `/devkit.ts.security-review full` - Complete TypeScript security audit
3. `/devkit.generate-security-assessment` - Generate security documentation
4. `/devkit.java.dependency-audit` - Vulnerability check
5. `/devkit.generate-changelog` - Generate release notes

**Maintenance:**
1. `/devkit.java.dependency-audit` - Weekly/monthly dependency checks
2. `/devkit.java.upgrade-dependencies` - Safe upgrades
3. `/devkit.java.architect-review` - Quarterly architecture review

---

## Complete Workflow Example

Real-world scenario: Implementing a complete user management feature

```bash
# 1. Create CRUD implementation
/devkit.java.generate-crud User

# 2. Implement custom business logic
# ... manual coding ...

# 3. Generate unit tests
/devkit.java.write-unit-tests src/main/java/com/example/service/UserService.java

# 4. Generate integration tests
/devkit.java.write-integration-tests src/main/java/com/example/controller/UserController.java

# 5. Code quality review
/devkit.java.code-review full src/main/java/com/example/user

# 6. Security review (Java)
/devkit.java.security-review code src/main/java/com/example/user

# 6b. Security review (TypeScript, if applicable)
/devkit.ts.security-review code

# 7. Generate security assessment documentation
/devkit.generate-security-assessment en-US markdown

# 8. Generate API documentation
/devkit.java.generate-docs . api html

# 9. Update changelog
/devkit.generate-changelog update

# 10. Validate and commit
git add .
git commit -m "feat: implement user management feature"

# 11. Create pull request (documented separately)
# Use GitHub Spec Kit commands for PR creation and review
```

---

## Troubleshooting

### Command Not Found
```bash
# Verify command exists
ls -la commands/

# Check YAML frontmatter syntax
cat commands/devkit.java.code-review.md | head -10

# List available commands
/help
```

### GitHub CLI Authentication
```bash
# Check authentication status
gh auth status

# Login if needed
gh auth login
```

### Test Failures
```bash
# Run tests manually
mvn test

# Run specific test class
mvn test -Dtest=UserServiceTest

# Check logs
tail -f target/surefire-reports/*.txt
```

### Build Failures
```bash
# Clean and rebuild
mvn clean install

# Skip tests if needed
mvn clean package -DskipTests

# Check for dependency conflicts
mvn dependency:tree
```

---

## Long-Running Agent (LRA) Commands

Commands for managing complex projects that span multiple context windows, based on [Anthropic's research on long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

### `/devkit.lra.init`

**Description**: Initialize LRA environment for multi-session projects by setting up feature list, progress tracking, and initialization script.

**When to use:**
- Starting a new complex project that will span multiple sessions
- When you need systematic progress tracking across days/weeks
- For large features that require multiple development sessions

**Arguments:**
```bash
/devkit.lra.init [project-description]
```

**Creates:**
- `features/` directory with feature backlog
- `progress.md` for tracking completion status
- `init.sh` for session initialization
- Project configuration and context

**Example initialization:**
```bash
/devkit.lra.init "E-commerce platform with user management, product catalog, and order processing"
```

### `/devkit.lra.start-session`

**Description**: Start a new coding session by reading progress, checking project health, and selecting the next feature to work on.

**When to use:**
- Beginning each development session
- After returning to a project after a break
- When you need to resume work on a multi-session project

**Features:**
- Automatic feature selection based on priorities
- Progress review and health check
- Context restoration from previous sessions
- Test suite verification

### `/devkit.lra.add-feature`

**Description**: Add new feature requirements to the feature backlog during development.

**When to use:**
- Discovering new requirements during implementation
- Adding edge cases or additional functionality
- When stakeholders request new features

**Arguments:**
```bash
/devkit.lra.add-feature [category] [priority] [description]
```

**Categories:**
- `feature` - New user-facing functionality
- `bug` - Bug fixes and corrections
- `tech` - Technical debt and improvements
- `docs` - Documentation updates

**Priorities:**
- `critical` - Blocks release or core functionality
- `high` - Important for next release
- `medium` - Nice to have
- `low` - Future consideration

### `/devkit.lra.mark-feature`

**Description**: Mark a feature as completed (passed) or failed after implementation and testing.

**When to use:**
- After completing feature implementation
- When tests pass and functionality is verified
- When a feature needs to be marked as failed for any reason

**Arguments:**
```bash
/devkit.lra.mark-feature [feature-id] [passed|failed] [optional-notes]
```

**Updates:**
- Feature status in progress tracking
- Test results and quality metrics
- Implementation notes and lessons learned

### `/devkit.lra.checkpoint`

**Description**: Create session checkpoint by committing changes, updating progress log, and ensuring clean state for the next session.

**When to use:**
- End of each development session
- Before taking a break from coding
- When handing off work to another developer

**Actions:**
- Commits all changes with descriptive messages
- Updates progress.md with current status
- Creates session summary
- Ensures clean, testable state

### `/devkit.lra.status`

**Description**: Display comprehensive project status including progress metrics, priorities, recent activity, and upcoming work.

**When to use:**
- Project status reviews with stakeholders
- Planning next development session
- When evaluating project health and timeline

**Shows:**
- Feature completion percentage
- Priority-based feature breakdown
- Recent commits and changes
- Upcoming features and estimated effort
- Test coverage and quality metrics

### `/devkit.lra.recover`

**Description**: Recover from broken state by diagnosing issues, reverting if needed, and restoring a clean working state.

**When to use:**
- When the project is in a broken or unbuildable state
- After failed experiments or refactoring
- When tests are failing and the cause is unclear

**Recovery steps:**
- Diagnostic analysis of current state
- Git history analysis to find last working state
- Selective revert or reset as needed
- Restoration of clean, testable state

**LRA Workflow Example:**
```bash
# First time setup
/devkit.lra.init "Customer management system with authentication and profiles"

# Start each session
/devkit.lra.start-session

# Add new requirements discovered during development
/devkit.lra.add-feature feature high "Two-factor authentication for security"

# Mark completed features
/devkit.lra.mark-feature user-registration passed "All tests passing"

# End of session
/devkit.lra.checkpoint "Implemented user registration and login functionality"

# Check project status anytime
/devkit.lra.status

# Recover if something goes wrong
/devkit.lra.recover
```

---

## Contributing

To add new commands:

1. Create `.md` file in `commands/` directory
2. Follow existing format with frontmatter
3. Test the command thoroughly
4. Update this documentation
5. Submit PR

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
