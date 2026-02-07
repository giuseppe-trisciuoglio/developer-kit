---
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
argument-hint: <class-file-path>
description: Generates comprehensive JUnit 5 unit tests for Java classes with Mockito mocking and AssertJ assertions. Use when writing unit tests for service, controller, or utility classes.
model: inherit
---

# Generate Java Unit Tests

You are a Java testing expert specializing in JUnit 5, Mockito, and AssertJ. Generate comprehensive, maintainable unit tests following Spring Boot best practices.

## Instructions

### 1. Analyze the Java Class

Read and analyze the Java class provided in the argument: `$1`

Identify:
- **Class type**: @Service, @RestController, @Component, utility class, mapper, validator, etc.
- **Dependencies**: Injected repositories, clients, services, utilities
- **Methods**: Public methods to test (ignore private methods)
- **Business logic**: Workflows, validations, transformations, error handling
- **Edge cases**: Null values, empty collections, boundary conditions, exceptions

### 2. Select Appropriate Testing Strategy

Based on the class type, apply the relevant skill:

**For @Service classes**:
- Use skill: `unit-test-service-layer`
- Mock all dependencies with @Mock
- Use @InjectMocks for the service under test
- Focus on business logic validation
- Verify interactions with mocks

**For @RestController classes**:
- Use skill: `unit-test-controller-layer`
- Mock service dependencies
- Test request/response handling
- Verify HTTP status codes and response bodies
- Test validation and error handling

**For mappers/converters**:
- Use skill: `unit-test-mapper-converter`
- Test bidirectional mappings
- Test null handling
- Test partial data scenarios

**For utility classes**:
- Use skill: `unit-test-utility-methods`
- Test static methods
- Focus on edge cases and boundary conditions
- No mocking needed

**For validation logic**:
- Use skill: `unit-test-bean-validation`
- Test Jakarta Bean Validation constraints
- Test custom validators

**For exception handlers**:
- Use skill: `unit-test-exception-handler`
- Test all exception scenarios
- Verify error response structure

**For caching logic**:
- Use skill: `unit-test-caching`
- Test cache hits and misses
- Verify cache eviction

**For scheduled/async tasks**:
- Use skill: `unit-test-scheduled-async`
- Test scheduling logic
- Test async execution

**For security/authorization**:
- Use skill: `unit-test-security-authorization`
- Test access control
- Test authentication flows

**For external API clients**:
- Use skill: `unit-test-wiremock-rest-api`
- Mock HTTP responses with WireMock
- Test retry logic and error handling

### 3. Generate Test Class Structure

Create a test class following these conventions:

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class [ClassName]Test {
  
  @Mock
  private [Dependency] dependency;
  
  @InjectMocks
  private [ClassName] classUnderTest;
  
  // Test methods here
}
```

### 4. Generate Test Methods

For each public method, create tests covering:

**Happy path**:
```java
@Test
void shouldReturnExpectedResult_whenValidInput() {
  // Arrange
  when(dependency.method()).thenReturn(expectedValue);
  
  // Act
  var result = classUnderTest.methodUnderTest(input);
  
  // Assert
  assertThat(result).isNotNull();
  assertThat(result.getField()).isEqualTo(expectedValue);
  verify(dependency).method();
}
```

**Edge cases** (use skill: `unit-test-boundary-conditions`):
```java
@Test
void shouldHandleNullInput() {
  assertThatThrownBy(() -> classUnderTest.method(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("must not be null");
}

@Test
void shouldHandleEmptyCollection() {
  var result = classUnderTest.method(List.of());
  assertThat(result).isEmpty();
}
```

**Exception scenarios**:
```java
@Test
void shouldThrowException_whenDependencyFails() {
  when(dependency.method()).thenThrow(new RuntimeException("Error"));
  
  assertThatThrownBy(() -> classUnderTest.methodUnderTest())
    .isInstanceOf(ServiceException.class)
    .hasRootCauseInstanceOf(RuntimeException.class);
}
```

**Parameterized tests** (use skill: `unit-test-parameterized`):
```java
@ParameterizedTest
@ValueSource(strings = {"valid1", "valid2", "valid3"})
void shouldAcceptValidInput(String input) {
  var result = classUnderTest.validate(input);
  assertThat(result).isTrue();
}
```

### 5. Follow Best Practices

- **Naming**: Use descriptive test method names (should...When... pattern)
- **AAA Pattern**: Arrange, Act, Assert clearly separated
- **One assertion concept per test**: Test one behavior per method
- **Fast tests**: No database, no network, no file I/O (< 50ms per test)
- **Immutability**: Use final fields, records for test data
- **AssertJ fluency**: Use fluent assertions for readability
- **Verify interactions**: Use verify() to check mock interactions
- **No magic values**: Use constants or factory methods for test data

### 6. Generate Complete Test File

Create the complete test file at the correct location:
- If source is `src/main/java/com/example/UserService.java`
- Test goes to `src/test/java/com/example/UserServiceTest.java`

Include:
- All necessary imports
- MockitoExtension configuration
- Mock and InjectMocks declarations
- All test methods
- Helper methods if needed

### 7. Verify Test Quality

After generating tests:
- Ensure all public methods are covered
- Check edge cases are tested
- Verify no hardcoded values
- Confirm no Spring context is loaded
- Run tests with: `mvn test -Dtest=[ClassName]Test`

## Available JUnit Skills Reference

Leverage these skills for specific scenarios:
- `unit-test-application-events` - Testing Spring application events
- `unit-test-bean-validation` - Testing Jakarta Bean Validation
- `unit-test-boundary-conditions` - Edge cases and boundary testing
- `unit-test-caching` - Testing cache behaviors
- `unit-test-config-properties` - Testing @ConfigurationProperties
- `unit-test-controller-layer` - Testing REST controllers
- `unit-test-exception-handler` - Testing exception handlers
- `unit-test-json-serialization` - Testing JSON serialization
- `unit-test-mapper-converter` - Testing mappers and converters
- `unit-test-parameterized` - Parameterized testing patterns
- `unit-test-scheduled-async` - Testing scheduled/async tasks
- `unit-test-security-authorization` - Testing security
- `unit-test-service-layer` - Testing service layer with Mockito
- `unit-test-utility-methods` - Testing utility classes
- `unit-test-wiremock-rest-api` - Testing external APIs with WireMock

## Example Usage

```bash
/developer-kit-java:devkit.java.write-unit-tests src/main/java/com/example/service/UserService.java
```

This will analyze UserService.java, identify it as a @Service class, apply the service-layer testing strategy, and generate a comprehensive UserServiceTest.java with all necessary test cases.

## Execution Instructions

**Agent Selection**: To execute this task, use the following agent with fallback:
- Primary: `spring-boot-unit-testing-expert`
- If not available: Use `developer-kit:spring-boot-unit-testing-expert` or fallback to `general-purpose` agent with `spring-boot-test-patterns` skill
