---
allowed-tools: Read, Bash, Edit, Write, Grep, Glob
argument-hint: [scope] [strategy] [version]
description: Safe and incremental dependency upgrade strategy for Java/Maven/Gradle projects with breaking change detection and migration guides
---

# Java Dependency Upgrade Strategy

Plan and execute safe, incremental upgrades of Java project dependencies with minimal risk, proper testing, and clear migration paths for breaking changes.

## Context

- Build system: !`ls -la | grep -E "(pom\.xml|build\.gradle|build\.gradle\.kts)"`
- Current dependencies: !`if [ -f pom.xml ]; then mvn dependency:tree | head -30; elif [ -f build.gradle ]; then ./gradlew dependencies --configuration compileClasspath | head -30; fi`
- Outdated dependencies: !`if [ -f pom.xml ]; then mvn versions:display-dependency-updates 2>/dev/null | grep -E "\\->" | head -20; elif [ -f build.gradle ]; then ./gradlew dependencyUpdates 2>/dev/null | grep -E "\\->" | head -20; fi`

## Arguments

$1 specifies the scope (optional - defaults to `all`):
- `all` - Analyze all dependencies
- `spring` - Focus on Spring Boot and Spring Framework dependencies
- `testing` - Focus on test dependencies (JUnit, Mockito, AssertJ, Testcontainers)
- `security` - Prioritize security vulnerabilities
- `direct` - Only direct dependencies (not transitive)
- `<groupId:artifactId>` - Specific dependency (e.g., `org.springframework.boot:spring-boot-starter-web`)

$2 specifies the strategy (optional - defaults to `analyze`):
- `analyze` - Analyze and report available updates with risk assessment
- `plan` - Create detailed upgrade plan with incremental steps
- `migrate` - Generate migration guide for major version upgrades
- `execute` - Execute planned upgrades (requires confirmation)
- `rollback` - Create rollback strategy and backup current state

$3 specifies target version for specific dependency upgrades (optional):
- Version number (e.g., `3.2.0`, `5.3.31`)
- `latest` - Latest stable release
- `latest-minor` - Latest minor version
- `latest-patch` - Latest patch version

## Upgrade Analysis Process

### 1. Dependency Inventory
Analyze current state:
- List all dependencies (direct and transitive)
- Identify outdated dependencies
- Check for known security vulnerabilities
- Detect dependency conflicts

### 2. Risk Assessment
Categorize updates by risk level:
- **PATCH** (Low risk): Bug fixes, no breaking changes
- **MINOR** (Medium risk): New features, backward compatible
- **MAJOR** (High risk): Breaking changes, API modifications
- **SECURITY** (Critical): Security vulnerabilities requiring immediate action

### 3. Breaking Change Detection
For each major version update:
- Fetch release notes and changelogs
- Identify deprecated APIs
- Detect removed features
- Find renamed packages/classes
- Check compatibility with other dependencies

### 4. Framework-Specific Patterns

#### Spring Boot Upgrades
When upgrading Spring Boot:
- Check Spring Boot migration guide
- Update parent POM version
- Review breaking changes in Auto-configuration
- Update application.properties/yml if needed
- Verify starter dependencies compatibility
- Check for deprecated @Configuration patterns
- Test Actuator endpoint changes

#### JUnit 4 to JUnit 5
When upgrading JUnit:
- Replace `@Test` imports
- Convert `@Before/@After` to `@BeforeEach/@AfterEach`
- Update assertions (AssertJ recommended)
- Migrate test runners to `@ExtendWith`
- Replace `@RunWith(SpringRunner.class)` with `@ExtendWith(SpringExtension.class)`

#### Mockito Upgrades
When upgrading Mockito:
- Update import statements
- Replace deprecated methods
- Check ArgumentMatchers changes
- Verify BDDMockito compatibility
- Update MockitoJUnitRunner usage

### 5. Compatibility Matrix
Check peer dependencies:
- Spring Boot → Spring Framework version
- Spring Framework → Java version
- JUnit 5 → Mockito version
- Hibernate → Java Persistence API version
- Testcontainers → Docker Java version

## Upgrade Strategies

### Strategy 1: Patch Updates (Safe)
```bash
# Maven: Update all patch versions
mvn versions:use-latest-releases -DallowMajorUpdates=false -DallowMinorUpdates=false

# Gradle: Update patch versions
./gradlew useLatestVersions --update-dependency-locks
```

**Testing**: Smoke tests + unit tests
**Risk**: Very low
**Timeline**: Same day

### Strategy 2: Minor Updates (Careful)
```bash
# Maven: Update minor versions
mvn versions:use-latest-releases -DallowMajorUpdates=false

# Gradle with version catalog
./gradlew versionCatalogUpdate --no-major
```

**Testing**: Full regression suite
**Risk**: Low to medium
**Timeline**: 1-2 days

### Strategy 3: Major Updates (Planned)
Individual upgrade with migration:
1. Create feature branch
2. Update single dependency
3. Fix breaking changes
4. Run comprehensive tests
5. Code review
6. Merge after validation

**Testing**: Full test suite + manual QA
**Risk**: Medium to high
**Timeline**: 3-7 days per major dependency

### Strategy 4: Spring Boot Upgrade (Strategic)
```bash
# Check Spring Boot compatibility
curl -s https://spring.io/projects/spring-boot | grep -A 5 "supported versions"

# Incremental upgrade path
# Example: 2.7.x → 3.0.x → 3.1.x → 3.2.x
```

**Testing**: Integration tests with Testcontainers
**Risk**: High
**Timeline**: 1-2 sprints

## Maven Commands

### Analysis
```bash
# Check for updates
mvn versions:display-dependency-updates

# Check for plugin updates
mvn versions:display-plugin-updates

# Security vulnerabilities
mvn org.owasp:dependency-check-maven:check

# Dependency tree
mvn dependency:tree -Dverbose
```

### Execution
```bash
# Update specific dependency
mvn versions:use-dep-version -Dincludes=groupId:artifactId -DdepVersion=1.2.3

# Update all dependencies to latest
mvn versions:use-latest-versions

# Update parent POM
mvn versions:update-parent

# Revert changes if needed
mvn versions:revert
```

## Gradle Commands

### Analysis
```bash
# Check for updates (with plugin)
./gradlew dependencyUpdates

# Show dependency tree
./gradlew dependencies --configuration compileClasspath

# Security scan
./gradlew dependencyCheckAnalyze
```

### Execution
```bash
# Update version catalog
./gradlew versionCatalogUpdate

# Refresh dependencies
./gradlew build --refresh-dependencies

# Clean and rebuild
./gradlew clean build
```

## Migration Guide Template

For each major upgrade, generate:

```markdown
## Migration: [Dependency] [Old Version] → [New Version]

### Breaking Changes
- API change 1: `oldMethod()` → `newMethod()`
- Removed class: `com.example.OldClass`
- Configuration change: `old.property` → `new.property`

### Migration Steps

#### Step 1: Update Dependency
```xml
<!-- Maven -->
<dependency>
    <groupId>group.id</groupId>
    <artifactId>artifact-id</artifactId>
    <version>NEW_VERSION</version>
</dependency>
```

#### Step 2: Fix Compilation Errors
- Replace deprecated imports
- Update method calls
- Adjust configuration

#### Step 3: Update Tests
- Fix test compilation
- Update mocks and stubs
- Adjust test configurations

#### Step 4: Runtime Verification
- Start application
- Check logs for warnings
- Test critical paths

### Testing Checklist
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Application starts successfully
- [ ] Health checks pass
- [ ] Manual smoke tests completed

### Rollback Plan
```bash
git revert HEAD
mvn clean install
```

### Estimated Effort
- Compilation fixes: X hours
- Test updates: Y hours
- Testing & validation: Z hours
**Total**: W hours
```

## Post-Upgrade Validation

### Automated Checks
```bash
# Compile
mvn clean compile
./gradlew compileJava

# Run tests
mvn test
./gradlew test

# Integration tests
mvn verify
./gradlew integrationTest

# Code quality
mvn checkstyle:check spotbugs:check
./gradlew check

# Generate dependency report
mvn project-info-reports:dependencies
```

### Runtime Verification
- Application startup time
- Memory footprint comparison
- API response times
- Error rate monitoring
- Health check status

## Rollback Strategy

### Create Rollback Point
```bash
# Git tag before upgrade
git tag -a "pre-upgrade-$(date +%Y%m%d)" -m "Pre-upgrade snapshot"

# Backup POM/Gradle files
cp pom.xml pom.xml.backup
cp build.gradle build.gradle.backup
cp gradle/libs.versions.toml gradle/libs.versions.toml.backup
```

### Execute Rollback
```bash
# Restore from backup
git checkout pom.xml build.gradle gradle/libs.versions.toml

# Or revert to tag
git reset --hard pre-upgrade-YYYYMMDD

# Clean rebuild
mvn clean install
./gradlew clean build
```

## Common Java Dependency Upgrades

### Spring Boot
- Check [Spring Boot Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- Review breaking changes in Auto-configuration
- Update Java version if required (Spring Boot 3 requires Java 17+)

### Hibernate/JPA
- Review JPA specification changes
- Check for deprecated methods
- Test lazy loading behavior
- Verify transaction management

### Jackson
- Check for breaking changes in serialization
- Test date/time handling
- Verify custom serializers/deserializers

### Lombok
- Update IDE plugin
- Check annotation processing configuration
- Verify generated code compatibility

### Testcontainers
- Update Docker dependencies
- Check container image versions
- Verify network configuration

## Your Task

Based on the specified scope and strategy, provide:

1. **Dependency Analysis Report**
   - Current versions vs. available versions
   - Risk assessment for each update
   - Security vulnerability status
   - Dependency conflicts

2. **Prioritized Upgrade Plan**
   - Critical security updates (immediate)
   - Safe patch updates (batch)
   - Minor version updates (incremental)
   - Major version updates (planned)

3. **Migration Guides** (for major upgrades)
   - Breaking changes
   - Step-by-step migration
   - Code examples
   - Testing strategy

4. **Execution Commands**
   - Maven/Gradle commands to execute
   - Testing commands
   - Rollback procedures

5. **Timeline & Effort Estimation**
   - Realistic schedule
   - Resource requirements
   - Risk mitigation steps

Focus on **safe, incremental upgrades** that maintain system stability while keeping dependencies current and secure. Always provide rollback strategies and comprehensive testing approaches.
