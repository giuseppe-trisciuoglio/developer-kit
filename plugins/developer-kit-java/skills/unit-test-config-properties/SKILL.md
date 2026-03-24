---
name: unit-test-config-properties
description: Provides patterns for unit testing `@ConfigurationProperties` classes with `@ConfigurationPropertiesTest`. Validates property binding, tests validation constraints, verifies default values, checks type conversions, and mocks property sources for Spring Boot configuration properties. Use when testing application configuration binding, validating YAML or application.properties files, verifying environment-specific settings, or testing nested property structures.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Configuration Properties and Profiles

## Overview

This skill provides patterns for unit testing `@ConfigurationProperties` bindings, environment-specific configurations, and property validation using JUnit 5. Covers testing property name mapping, type conversions, validation constraints, nested structures, and profile-specific configurations without full Spring context startup.

**Key validation checkpoints:**
- Property prefix matches between `@ConfigurationProperties` and test properties
- Validation triggers on `@Validated` classes with invalid values
- Type conversions work for Duration, DataSize, collections, and maps

## When to Use

- Testing `@ConfigurationProperties` property binding
- Testing property name mapping and type conversions
- Validating configuration with `@NotBlank`, `@Min`, `@Max`, `@Email` constraints
- Testing environment-specific configurations (dev, prod)
- Testing nested property structures and collections
- Verifying default values when properties are not specified
- Fast configuration tests without Spring context startup

## Instructions

1. **Set up test dependencies**: Add `spring-boot-starter-test` and AssertJ dependencies
2. **Use ApplicationContextRunner**: Test property bindings without starting full Spring context
3. **Define property prefixes**: Ensure `@ConfigurationProperties(prefix = "...")` matches test property paths
4. **Test all property paths**: Verify each property including nested structures and collections
5. **Test validation constraints**: Use `context.hasFailed()` to verify `@Validated` properties reject invalid values
6. **Test type conversions**: Verify Duration (`30s`), DataSize (`50MB`), collections, and maps convert correctly
7. **Test default values**: Verify properties have correct defaults when not specified in test properties
8. **Test profile-specific configs**: Use `@Profile` with `ApplicationContextRunner` for environment-specific configurations
9. **Test edge cases**: Include empty strings, null values, and type mismatches

**Troubleshooting flow:**
- If properties don't bind → Check prefix matches (kebab-case to camelCase conversion)
- If validation doesn't trigger → Verify `@Validated` annotation is present
- If context fails to start → Check dependencies and `@ConfigurationProperties` class structure

## Examples

### Setup: Test Dependencies

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
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Basic Pattern: Property Binding

```java
@ConfigurationProperties(prefix = "app.security")
@Data
public class SecurityProperties {
  private String jwtSecret;
  private long jwtExpirationMs;
  private int maxLoginAttempts;
  private boolean enableTwoFactor;
}

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

### Validation Testing

```java
@ConfigurationProperties(prefix = "app.server")
@Data
@Validated
public class ServerProperties {
  @NotBlank
  private String host;

  @Min(1)
  @Max(65535)
  private int port = 8080;

  @Positive
  private int threadPoolSize;
}

class ConfigurationValidationTest {

  @Test
  void shouldFailValidationWhenHostIsBlank() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=",
        "app.server.port=8080",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasFailed()
          .getFailure()
          .hasMessageContaining("host");
      });
  }

  @Test
  void shouldPassValidationWithValidConfiguration() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=localhost",
        "app.server.port=8080",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasNotFailed();
        assertThat(context.getBean(ServerProperties.class).getHost()).isEqualTo("localhost");
      });
  }
}
```

### Type Conversion Testing

```java
@ConfigurationProperties(prefix = "app.features")
@Data
public class FeatureProperties {
  private Duration cacheExpiry = Duration.ofMinutes(10);
  private DataSize maxUploadSize = DataSize.ofMegabytes(100);
  private List<String> enabledFeatures;
  private Map<String, String> featureFlags;
}

class TypeConversionTest {

  @Test
  void shouldConvertDurationFromString() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.cacheExpiry=30s")
      .withBean(FeatureProperties.class)
      .run(context -> {
        assertThat(context.getBean(FeatureProperties.class).getCacheExpiry())
          .isEqualTo(Duration.ofSeconds(30));
      });
  }

  @Test
  void shouldConvertCommaDelimitedList() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.enabledFeatures=feature1,feature2")
      .withBean(FeatureProperties.class)
      .run(context -> {
        assertThat(context.getBean(FeatureProperties.class).getEnabledFeatures())
          .containsExactly("feature1", "feature2");
      });
  }
}
```

For **nested properties**, **profile-specific configurations**, **collection binding**, and **advanced validation patterns**, see `references/advanced-examples.md`.

## Best Practices

- **Test all property bindings** including nested structures and collections
- **Test validation constraints** for all `@NotBlank`, `@Min`, `@Max`, `@Email`, `@Positive` annotations
- **Test both default and custom values** to verify fallback behavior
- **Use ApplicationContextRunner** for fast context-free testing
- **Test profile-specific configurations** separately with `@Profile`
- **Verify type conversions** for Duration, DataSize, collections, and maps
- **Test edge cases**: empty strings, null values, type mismatches, out-of-range values

## Constraints and Warnings

- **Kebab-case to camelCase**: Property `app.my-property` maps to `myProperty` in Java
- **Loose binding**: Spring Boot uses loose binding by default; use strict binding if needed
- **`@Validated` required**: Add `@Validated` annotation to enable constraint validation
- **`@ConstructorBinding`**: All parameters must be bindable when using constructor binding
- **List indexing**: Use `[0]`, `[1]` notation; ensure sequential indexing for lists
- **Duration format**: Accepts ISO-8601 (`PT30S`) or simple syntax (`30s`, `1m`, `2h`)
- **Context isolation**: Each `ApplicationContextRunner` creates a new context with no shared state
- **Profile activation**: Use `spring.profiles.active=profileName` in `withPropertyValues()` for profile tests

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Properties not binding | Prefix mismatch | Verify `@ConfigurationProperties(prefix="...")` matches property paths |
| Validation not triggered | Missing `@Validated` | Add `@Validated` annotation to configuration class |
| Context fails to start | Missing dependencies | Ensure `spring-boot-starter-test` is in test scope |
| Nested properties null | Inner class missing | Use `@Data` on nested classes or provide getters/setters |
| Collection binding fails | Wrong indexing | Use `[0]`, `[1]` notation, not `(0)`, `(1)` |
