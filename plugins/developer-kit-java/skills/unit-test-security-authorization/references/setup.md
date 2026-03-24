# Setup - Security Testing Dependencies

## Maven Configuration

Add the following dependencies to your `pom.xml`:

```xml
<dependencies>
  <!-- Spring Security -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
  </dependency>

  <!-- Spring Boot Test (includes JUnit 5) -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>

  <!-- Spring Security Test -->
  <dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-test</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

## Gradle Configuration

Add the following dependencies to your `build.gradle.kts`:

```kotlin
dependencies {
  // Spring Security
  implementation("org.springframework.boot:spring-boot-starter-security")

  // Spring Boot Test (includes JUnit 5)
  testImplementation("org.springframework.boot:spring-boot-starter-test")

  // Spring Security Test
  testImplementation("org.springframework.security:spring-security-test")
}
```

## Enable Method Security

Add the `@EnableGlobalMethodSecurity` annotation to your configuration:

```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class SecurityConfig {

    // Other security configuration
}
```

**Configuration Options:**
- `prePostEnabled = true` — Enables `@PreAuthorize` and `@PostAuthorize` annotations
- `securedEnabled = true` — Enables `@Secured` annotation
- `jsr250Enabled = true` — Enables `@RolesAllowed` annotation (JSR-250)

## Test Dependencies Included

When you add `spring-boot-starter-test`, you automatically get:
- **JUnit 5** (Jupiter) - Testing framework
- **AssertJ** - Fluent assertion library
- **Mockito** - Mocking framework
- **Hamcrest** - Matcher objects
- **JsonPath** - JSON path expressions
- **JsonAssert** - JSON assertions

## Verify Setup

Create a simple test to verify everything is configured:

```java
import org.junit.jupiter.api.Test;
import org.springframework.security.test.context.support.WithMockUser;
import static org.assertj.core.api.Assertions.*;

class SecuritySetupTest {

    @Test
    @WithMockUser
    void shouldLoadSpringSecurityContext() {
        // If this test runs, Spring Security Test is properly configured
        assertThat(true).isTrue();
    }
}
```
