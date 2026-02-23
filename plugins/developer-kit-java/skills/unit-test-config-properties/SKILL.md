---
name: unit-test-config-properties
description: Provides patterns for unit testing @ConfigurationProperties classes using ApplicationContextRunner. Use when testing Spring Boot configuration property binding, validation, and profile-specific configurations without full context startup.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Configuration Properties and Profiles

## Overview

This skill provides patterns for unit testing @ConfigurationProperties bindings, environment-specific configurations, and property validation using JUnit 5. It covers testing property name mapping, type conversions, validation constraints, nested structures, and profile-specific configurations without full Spring context startup.

## When to Use

Use this skill when:
- Testing @ConfigurationProperties property binding
- Testing property name mapping and type conversions
- Verifying configuration validation
- Testing environment-specific configurations
- Testing nested property structures
- Want fast configuration tests without Spring context

Trigger phrases:
- "test configuration properties"
- "test applicationcontextrunner"
- "validate spring boot property binding"
- "test profile-specific configuration"

## Instructions

1. **Use ApplicationContextRunner**: Test property bindings without starting full Spring context
2. **Test all property paths**: Verify each property including nested structures and collections
3. **Test validation constraints**: Ensure @Validated properties fail with invalid values
4. **Test type conversions**: Verify Duration, DataSize, and other special types convert correctly
5. **Test default values**: Verify properties have correct defaults when not specified
6. **Test profile-specific configs**: Use @Profile to test environment-specific configurations
7. **Verify property prefixes**: Ensure the prefix in @ConfigurationProperties matches test properties
8. **Test edge cases**: Include empty strings, null values, and type mismatches

## Examples

## Setup: Configuration Testing

### Maven
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-configuration-processor</artifactId>
  <scope>provided</scope>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle
```kotlin
dependencies {
  annotationProcessor("org.springframework.boot:spring-boot-configuration-processor")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
  testImplementation("org.junit.jupiter:junit-jupiter")
  testImplementation("org.assertj:assertj-core")
}
```

## Basic Pattern: Testing ConfigurationProperties

### Simple Property Binding

```java
// Configuration properties class
@ConfigurationProperties(prefix = "app.security")
@Data
public class SecurityProperties {
  private String jwtSecret;
  private long jwtExpirationMs;
  private int maxLoginAttempts;
  private boolean enableTwoFactor;
}

// Unit test
import org.junit.jupiter.api.Test;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import static org.assertj.core.api.Assertions.*;

class SecurityPropertiesTest {

  @Test
  void shouldBindPropertiesFromEnvironment() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.security.jwtSecret=my-secret-key",
        "app.security.jwtExpirationMs=3600000",
        "app.security.maxLoginAttempts=5",
        "app.security.enableTwoFactor=true"
      )
      .withBean(SecurityProperties.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);

        assertThat(props.getJwtSecret()).isEqualTo("my-secret-key");
        assertThat(props.getJwtExpirationMs()).isEqualTo(3600000L);
        assertThat(props.getMaxLoginAttempts()).isEqualTo(5);
        assertThat(props.isEnableTwoFactor()).isTrue();
      });
  }

  @Test
  void shouldUseDefaultValuesWhenPropertiesNotProvided() {
    new ApplicationContextRunner()
      .withPropertyValues("app.security.jwtSecret=key")
      .withBean(SecurityProperties.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);

        assertThat(props.getJwtSecret()).isEqualTo("key");
        assertThat(props.getMaxLoginAttempts()).isZero();
      });
  }
}
```

For detailed examples covering nested properties, property validation, profile-specific configurations, type conversion (Duration, DataSize, Lists), and default value testing, see [Examples](references/examples.md).

## Best Practices

- **Test all property bindings** including nested structures
- **Test validation constraints** thoroughly
- **Test both default and custom values**
- **Use ApplicationContextRunner** for context-free testing
- **Test profile-specific configurations** separately
- **Verify type conversions** work correctly
- **Test edge cases** (empty strings, null values, type mismatches)

## Common Pitfalls

- Not testing validation constraints
- Forgetting to test default values
- Not testing nested property structures
- Testing with wrong property prefix
- Not handling type conversion properly

## Constraints and Warnings

- **Property name matching**: Kebab-case in properties (app.my-prop) maps to camelCase in Java (myProp)
- **Loose binding by default**: Spring Boot supports loose binding; enable strict binding if needed
- **Validation requires @Validated**: Add @Validated to enable validation on configuration properties
- **@ConstructorBinding limitations**: When using @ConstructorBinding, all parameters must be bindable
- **List indexing**: List properties use [0], [1] notation; ensure sequential indexing
- **Duration format**: Duration properties accept standard ISO-8601 format or simple syntax (10s, 1m)
- **ApplicationContextRunner isolation**: Each ApplicationContextRunner creates a new context; there's no shared state

## Troubleshooting

**Properties not binding**: Verify prefix and property names match exactly (including kebab-case to camelCase conversion).

**Validation not triggered**: Ensure `@Validated` is present and validation dependencies are on classpath.

**ApplicationContextRunner not found**: Verify `spring-boot-starter-test` is in test dependencies.

## References

- [Spring Boot ConfigurationProperties](https://docs.spring.io/spring-boot/docs/current/reference/html/configuration-metadata.html)
- [ApplicationContextRunner Testing](https://docs.spring.io/spring-boot/docs/current/api/org/springframework/boot/test/context/runner/ApplicationContextRunner.html)
- [Spring Profiles](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.profiles)
