---
name: junit-mockito-unit-testing
description: Practical guide for writing unit tests in Java using JUnit 5 (Jupiter) and Mockito. Includes best practices, examples, and build snippets for Maven/Gradle.
category: testing
tags: [junit-5, mockito, unit-testing, java, testing, mocking, assertions, testcontainers]
version: 1.0.0
language: en
license: See LICENSE
context7_library: /junit-team/junit5
context7_trust_score: 8.0
---

# JUnit 5 + Mockito — Unit Testing Guide

This guide provides a practical, up-to-date reference for writing unit tests in Java using JUnit 5 (Jupiter) and Mockito. It focuses on idiomatic test design, tooling configuration, Mockito integration with JUnit Jupiter, and recommended patterns for maintainable tests.

Sources: official JUnit 5 and Mockito documentation (resolved via Context7: `/junit-team/junit5` and `/mockito/mockito`). The content below summarizes and curates the most relevant guidance for day-to-day unit testing.

## When to Use This Skill

Use this skill when:
- Writing isolated unit tests for Java classes with external dependencies
- Integrating with JUnit 5 (Jupiter) test framework in new or existing projects
- Creating fast, deterministic tests that avoid external services and containers
- Mocking dependencies using Mockito with best practices
- Building comprehensive test suites for Spring Boot applications
- Handling complex test scenarios with multiple collaborators and assertions
- Testing services, repositories, and business logic in isolation
- Implementing parameterized tests and custom test behaviors
- Troubleshooting flaky tests or test isolation issues
- Following SOLID principles in test design and architecture

## Goals / Contract
- Inputs: Java classes (plain JVM code) under test and their dependencies
- Outputs: Fast, deterministic unit tests that run in the JVM (no Docker/containers)
- Error modes: flaky tests, slow tests, hidden dependencies (file system, env, static state)
- Success criteria: tests are isolated, readable, fast (<50ms typical), and easily run by IDE/CI

## Core Concepts

### Test Foundation: Setting Up JUnit 5 and Mockito

Before writing tests, ensure you have the right dependencies configured in your project.

## Recommended dependencies
- JUnit 5 (Jupiter) — use the JUnit 5 BOM or explicit artifacts
- Mockito (latest stable 4.x/5.x depending on project compatibility)
- AssertJ — expressive assertions
- (Optional) Mockito JUnit Jupiter integration artifact: `mockito-junit-jupiter`

Maven (examples)
```xml
<!-- Use dependencyManagement or BOM in your parent pom to lock versions -->
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.mockito</groupId>
  <artifactId>mockito-core</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.mockito</groupId>
  <artifactId>mockito-junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

Gradle (Kotlin DSL)
```kotlin
dependencies {
  testImplementation("org.junit.jupiter:junit-jupiter")
  testImplementation("org.mockito:mockito-core")
  testImplementation("org.mockito:mockito-junit-jupiter")
  testImplementation("org.assertj:assertj-core")
}
```

### Test Structure, Organization & Naming

Proper test organization ensures maintainability and clarity.

## Test structure & naming
- Place test classes in the same package as the class under test: `src/test/java/...` mirrors `src/main/java/...`.
- Test class name: append `Test` (e.g., `UserServiceTest`). For integration-style unit tests you may use `IT` suffix, but prefer `Test` for unit tests.
- Method names: use descriptive camelCase methods beginning with `should` or `test` (e.g., `shouldReturnEmptyListWhenNoUsers()`).
- Use `@DisplayName` for human-readable names in reports.

### JUnit 5 Essentials

Master the core annotations and patterns of the Jupiter framework.

## JUnit 5 essentials
- Annotations: `@Test`, `@BeforeEach`, `@AfterEach`, `@BeforeAll`, `@AfterAll`, `@Tag`, `@Disabled`, `@DisplayName`.
- Assertions: prefer AssertJ (`assertThat(...)`) for fluent, readable assertions. JUnit's `Assertions.assertThrows()` is useful for exception checks.
- Test lifecycle: by default test instance is per-method. Use `@TestInstance(Lifecycle.PER_CLASS)` if you need non-static `@BeforeAll`.
- Parameterized tests: use `@ParameterizedTest` with `@ValueSource`, `@MethodSource`, `@CsvSource`.
- Filtering: use `@Tag("unit")` to mark unit tests and filter them in CI or locally.

Example minimal JUnit 5 test (with AssertJ):
```java
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class CalculatorTest {
  @Test
  void shouldAddTwoNumbers() {
    Calculator calculator = new Calculator();
    int sumResult = calculator.add(2, 3);
    assertThat(sumResult).isEqualTo(5);
  }
}
```

### Mockito Fundamentals & Mocking Strategies

Learn to isolate code under test with powerful mocking capabilities.

## Mockito fundamentals
- Use Mockito to create isolated test doubles for dependencies.
- Prefer `MockitoExtension` for JUnit 5 integration — it initializes fields annotated with `@Mock` and injects them into `@InjectMocks` instances.
- Common annotations: `@Mock`, `@Spy`, `@InjectMocks`, and `@Captor`.
- Stubbing: `when(...).thenReturn(...)`, or BDD style `given(...).willReturn(...)`.
- Verification: `verify(mock).someMethod(...)`, with `times(n)`, `never()`, `atLeastOnce()`.
- Argument matchers: `any()`, `anyString()`, `eq(...)` — mixing raw values and matchers requires wrapping raw values with `eq()`.

Example with MockitoExtension + AssertJ
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

  @Mock
  private UserRepository userRepository;

  @InjectMocks
  private UserService userService; // constructor injection recommended in production

  @Test
  void shouldReturnEmptyWhenNoUsers() {
    when(userRepository.findAll()).thenReturn(List.of());

    List<User> users = userService.getAllUsers();

    assertThat(users).isEmpty();
    verify(userRepository, times(1)).findAll();
  }
}
```

### Spies and partial mocks
- Use `@Spy` to wrap a real object while allowing selective stubbing. Prefer plain `mock()` unless you need partial real behavior.

### Mocking final classes or static methods
- Modern Mockito supports inline mocking (mockito-inline) for final classes and methods. Add the `mockito-inline` dependency if you need that feature.

## API Reference

### Core JUnit 5 Annotations

**Lifecycle and Structure:**
- `@Test` — Mark a method as a test method
- `@BeforeEach` — Execute before each test method (formerly @Before)
- `@AfterEach` — Execute after each test method (formerly @After)
- `@BeforeAll` — Execute once before all test methods in a class (static method)
- `@AfterAll` — Execute once after all test methods in a class (static method)
- `@DisplayName` — Set human-readable test name in reports
- `@Disabled` — Skip test execution
- `@Tag` — Mark test with a tag for filtering (e.g., `@Tag("unit")`)

**Test Configuration:**
- `@TestInstance(Lifecycle.PER_CLASS)` — Create one test instance per class (allows non-static @BeforeAll)
- `@ExtendWith` — Register custom extensions for lifecycle and behavior
- `@Nested` — Mark inner class as nested test group
- `@ParameterizedTest` — Run test with multiple parameters

**Parameterized Test Sources:**
- `@ValueSource` — Provide simple values (primitives or strings)
- `@MethodSource` — Provide values from a factory method
- `@CsvSource` — Provide values in CSV format
- `@EnumSource` — Provide enum values

### Core Mockito Annotations

- `@Mock` — Create a mock instance of a class or interface
- `@Spy` — Create a spy (partial mock) of a real object
- `@InjectMocks` — Inject mocks into the system under test
- `@Captor` — Capture arguments passed to mock methods
- `@ExtendWith(MockitoExtension.class)` — Enable Mockito integration with JUnit 5

### Common Assertions (AssertJ)

**Core Assertions:**
- `assertThat(...).isEqualTo(expected)` — Assert equality
- `assertThat(...).isNotNull()` — Assert not null
- `assertThat(...).isNull()` — Assert is null
- `assertThat(...).isEmpty()` — Assert collection is empty
- `assertThat(...).hasSize(n)` — Assert collection size

**Collection Assertions:**
- `assertThat(...).contains(element)` — Contains an element
- `assertThat(...).doesNotContain(element)` — Does not contain element
- `assertThat(...).containsAll(elements)` — Contains all elements
- `assertThat(...).hasSize(n).contains(element)` — Chain assertions

**Throwable Assertions:**
- `assertThat(...).isInstanceOf(Exception.class)` — Assert exception type
- `assertThatThrownBy(() -> {...}).isInstanceOf(CustomException.class)` — Assert exception from code block

### Mockito Verification & Stubbing

**Stubbing:**
- `when(mock.method(...)).thenReturn(value)` — Return a value
- `when(mock.method(...)).thenThrow(exception)` — Throw an exception
- `when(mock.method(...)).thenAnswer(invocation -> {...})` — Custom behavior
- `given(mock.method(...)).willReturn(value)` — BDD-style stubbing

**Verification:**
- `verify(mock).method(...)` — Verify method was called
- `verify(mock, times(n)).method(...)` — Verify called exactly n times
- `verify(mock, never()).method(...)` — Verify never called
- `verify(mock, atLeastOnce()).method(...)` — Verify called at least once
- `verify(mock, atMostOnce()).method(...)` — Verify called at most once

**Argument Matchers:**
- `any()` — Match any argument
- `anyString()` — Match any String
- `anyInt()` — Match any int
- `eq(value)` — Match exact value
- `contains(substring)` — Match String containing substring
- `argThat(predicate)` — Custom matcher with predicate

## Best practices and patterns
- Arrange-Act-Assert: keep tests structured and short.
- One assertion focus per test (or clearly related assertions).
- Avoid unnecessary test logic and branching inside tests.
- Make tests deterministic: avoid random numbers, fixed system time unless controlled by a clock abstraction.
- Avoid static state; reset singletons between tests if unavoidable.
- Prefer constructor injection in production code — makes unit testing straightforward via `@InjectMocks` or manual construction with mocks.
- Use `@Tag("unit")` for all unit tests and configure your build tool/CI to run them quickly.

## Spring Boot and mocking notes (unit vs integration)
- For pure unit tests avoid starting the Spring context. Construct the SUT (system under test) manually and inject mocks.
- If you need Spring context and want to replace beans, prefer a `@TestConfiguration` with `@Bean` returning `Mockito.mock(...)` instead of `@MockBean` when working with Spring Boot 3.4+ deprecations or when you need explicit control.

## Performance & parallelism
- JUnit 5 supports parallel execution via `junit.jupiter.execution.parallel.*` properties. Measure and only enable parallelism when tests are thread-safe and do not mutate shared state.
- Keep unit tests fast (sub-50ms) to allow quick feedback loops.

## Running & filtering
- Maven: `mvn -Dtest=*Test test` and use Surefire/Failsafe profiles to control which tags run. Use `maven-surefire-plugin` configuration to pass `-Dgroups` / JUnit Platform properties.
- Gradle: `./gradlew test --tests "**/*Test"` and configure `useJUnitPlatform()` in the `test` task.

## Troubleshooting common Mockito issues
- Unfinished stubbing errors: ensure all stubbing calls are complete (`when(...).thenReturn(...)`) and not left dangling.
- Mixing matchers and real values: wrap real values with `eq(...)` or use matchers for all args.
- Flaky tests when using real static or environmental state: inject abstractions (e.g., Clock, EnvProvider) and mock them.

## Workflow Patterns

### Core Testing Recipes

**Quick Reference Patterns:**
- Use `@ExtendWith(MockitoExtension.class)` to auto-init mocks.
- Use `@TestInstance(Lifecycle.PER_CLASS)` if factory methods for `@MethodSource` are non-static.
- Use `assertThrows` for exception testing or `assertThatThrownBy` from AssertJ.

### Mocking External APIs & Complex Dependencies

This pattern is essential for testing services that depend on external APIs or multiple collaborators.
When your SUT interacts with an external HTTP API or with multiple collaborators, prefer to:
- keep the external interaction behind a small interface/adapter you can mock, or
- use a lightweight HTTP stub (e.g. WireMock) for end-to-end behaviour without starting the full application.

Below are concise examples showing both approaches.

**Pattern 1: Mockito with Multiple Mocked Dependencies (repository + external client)**
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class EnrichmentServiceTest {

  @Mock
  private UserRepository userRepository;

  @Mock
  private ExternalApiClient externalApiClient;

  @InjectMocks
  private EnrichmentService enrichmentService;

  @Test
  void shouldReturnEnrichedUsersWhenExternalApiReturnsData() {
    List<User> storedUsers = List.of(new User(1, "Alice"));
    when(userRepository.findAll()).thenReturn(storedUsers);
    when(externalApiClient.fetchDetails(eq(1))).thenReturn(new ExternalDetails("extra-info"));

    List<EnrichedUser> enrichedUsers = enrichmentService.getEnrichedUsers();

    assertThat(enrichedUsers).hasSize(1);
    assertThat(enrichedUsers.get(0).getDetails().getInfo()).isEqualTo("extra-info");
    verify(userRepository).findAll();
    verify(externalApiClient).fetchDetails(1);
  }
}
```
This pattern keeps tests fast and focused: the `ExternalApiClient` is just an interface/adapter you control and mock.

**Pattern 2: Using WireMock to Stub External HTTP APIs (Higher-Fidelity Tests)**
Add dependency (Maven):
```xml
<dependency>
  <groupId>org.wiremock</groupId>
  <artifactId>wiremock</artifactId>
  <scope>test</scope>
</dependency>
```
JUnit 5 example with WireMock extension:
```java
import com.github.tomakehurst.wiremock.junit5.WireMockExtension;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.web.client.RestTemplate;
import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static org.assertj.core.api.Assertions.*;

class ExternalApiWireMockTest {

  @RegisterExtension
  static WireMockExtension wireMock = WireMockExtension.newInstance()
    .options(wireMockConfig().dynamicPort())
    .build();

  @Test
  void shouldFetchDataFromExternalApi() {
    wireMock.stubFor(get(urlEqualTo("/api/data"))
      .willReturn(aResponse()
        .withStatus(200)
        .withHeader("Content-Type", "application/json")
        .withBody("{\"value\":\"hello\"}")));

    String baseUrl = wireMock.getRuntimeInfo().getHttpBaseUrl();
    RestTemplate restTemplate = new RestTemplate();

    String response = restTemplate.getForObject(baseUrl + "/api/data", String.class);

    assertThat(response).contains("hello");
  }
}
```
WireMock is great for tests that need a realistic HTTP surface without calling real external services.

**Pattern 3: Mocking Java HttpClient via Adapter Pattern**
When using Java 11+ HttpClient, prefer a thin `HttpClientAdapter` interface that your code depends on. Tests then mock the adapter rather than trying to mock the final HttpClient class directly.
```java
interface HttpClientAdapter {
  String get(String url);
}

class DefaultHttpClientAdapter implements HttpClientAdapter {
  // ...impl uses java.net.http.HttpClient...
}

// Test
@ExtendWith(MockitoExtension.class)
class RemoteDataServiceTest {
  @Mock
  private HttpClientAdapter httpClientAdapter;

  @InjectMocks
  private RemoteDataService remoteDataService;

  @Test
  void shouldReturnParsedDataWhenRemoteResponds() {
    when(httpClientAdapter.get("https://api.example.com/data"))
      .thenReturn("{\"value\":\"x\"}");

    Data parsed = remoteDataService.fetchData();

    assertThat(parsed.getValue()).isEqualTo("x");
    verify(httpClientAdapter).get("https://api.example.com/data");
  }
}
```

Notes on naming: prefer spoken/descriptive names in tests — e.g. `userRepository`, `externalApiClient`, `enrichmentService`, `sumResult`, `storedUsers`, `enrichedUsers`. They improve readability and make verification lines (verify/when) self-explanatory.

## Summary

This JUnit 5 + Mockito unit testing skill covers:

1. **Test Setup & Dependencies**: Configuring JUnit 5, Mockito, and AssertJ in Maven/Gradle
2. **Test Organization**: Proper naming conventions, package structure, and test lifecycle
3. **JUnit 5 Essentials**: Annotations, assertions, parameterized tests, and test filtering
4. **Mockito Fundamentals**: Mocking, stubbing, verification, and argument matchers
5. **Best Practices**: Arrange-Act-Assert pattern, test isolation, determinism, and performance
6. **Advanced Patterns**: Mocking external APIs, using WireMock, adapter patterns, and complex scenarios
7. **Spring Boot Integration**: Unit testing strategies that avoid the Spring context for speed
8. **API Reference**: Comprehensive annotation and method reference for quick lookup
9. **Performance & Parallelism**: Keeping tests fast (<50ms) and enabling parallel execution
10. **Troubleshooting**: Common issues like flaky tests, stubbing errors, and matcher problems

The patterns and examples are based on official JUnit 5 and Mockito documentation and represent modern Java testing best practices for maintaining fast, deterministic, and maintainable test suites.

## References
- JUnit 5 user guide and API (resolved via Context7 `/junit-team/junit5`)
- Mockito docs and wiki (resolved via Context7 `/mockito/mockito`)
- AssertJ: fluent assertions

