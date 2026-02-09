# JUnit Testing Skills Guide

Quick reference to 15 JUnit testing skills for Spring Boot applications. See individual skill files for complete details.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **unit-test-service-layer** | Service layer unit testing with mocks |
| **unit-test-controller-layer** | Controller testing with MockMvc |
| **unit-test-parameterized** | Parameterized tests with `@ParameterizedTest` |
| **unit-test-exception-handler** | Exception handling and custom exceptions |
| **unit-test-bean-validation** | Jakarta Validation testing |
| **unit-test-security-authorization** | Spring Security with `@WithMockUser` |
| **unit-test-application-events** | Application event publishing and listeners |
| **unit-test-scheduled-async** | Testing `@Async`, `@Scheduled` tasks |
| **unit-test-json-serialization** | JSON serialization with `@JsonTest` |
| **unit-test-config-properties** | `@ConfigurationProperties` binding |
| **unit-test-mapper-converter** | Entity to DTO mapping tests |
| **unit-test-caching** | `@Cacheable` and cache eviction tests |
| **unit-test-boundary-conditions** | Edge cases, limits, null values |
| **unit-test-utility-methods** | Static methods, helpers, utilities |
| **unit-test-wiremock-rest-api** | REST API mocking with WireMock |

---

## Testing by Layer

### Controllers

#### unit-test-controller-layer

**File**: `skills/unit-test-controller-layer/SKILL.md`

MockMvc testing: request/response handling, status codes.

**When to use:**
- Testing REST endpoints
- Verifying request mappings
- Testing path variables and query params

**Pattern:**
```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired MockMvc mockMvc;
    
    @Test
    void shouldReturnUser() throws Exception {
        mockMvc.perform(get("/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1));
    }
}
```

---

### Services

#### unit-test-service-layer

**File**: `skills/unit-test-service-layer/SKILL.md`

Service testing: mocking, assertions, test organization.

**When to use:**
- Testing business logic
- Mocking dependencies
- Verifying service contracts

---

#### unit-test-exception-handler

**File**: `skills/unit-test-exception-handler/SKILL.md`

Testing custom exceptions and error scenarios.

**When to use:**
- Testing error cases
- Custom exception handling
- Exception messages

---

### Data Layer

#### unit-test-mapper-converter

**File**: `skills/unit-test-mapper-converter/SKILL.md`

Entity to DTO mapping and converter testing.

**When to use:**
- Testing entity mappers
- Custom converters
- Bi-directional mappings

---

### Cross-Cutting Concerns

#### unit-test-security-authorization

**File**: `skills/unit-test-security-authorization/SKILL.md`

Spring Security testing: `@WithMockUser`, roles, permissions.

**When to use:**
- Testing secured endpoints
- Verifying user roles
- Authorization checks

**Pattern:**
```java
@Test
@WithMockUser(roles = "ADMIN")
void adminCanDelete() throws Exception {
    mockMvc.perform(delete("/users/1"))
        .andExpect(status().isNoContent());
}
```

---

#### unit-test-caching

**File**: `skills/unit-test-caching/SKILL.md`

Testing `@Cacheable` and cache eviction.

**When to use:**
- Cache hit/miss scenarios
- Cache eviction
- Cache configuration

---

#### unit-test-application-events

**File**: `skills/unit-test-application-events/SKILL.md`

Testing `@EventListener` and event publishing.

**When to use:**
- Event publishing tests
- Listener verification
- Event ordering

---

#### unit-test-config-properties

**File**: `skills/unit-test-config-properties/SKILL.md`

Testing `@ConfigurationProperties` binding.

**When to use:**
- Property binding validation
- Configuration tests
- Environment-specific configs

---

## Specialized Testing

### Async & Scheduled

#### unit-test-scheduled-async

**File**: `skills/unit-test-scheduled-async/SKILL.md`

Testing `@Async` and `@Scheduled` tasks.

**When to use:**
- Async method execution
- Scheduled job testing
- TestScheduler usage

---

### Data Serialization

#### unit-test-json-serialization

**File**: `skills/unit-test-json-serialization/SKILL.md`

JSON serialization/deserialization with `@JsonTest`.

**When to use:**
- Testing JSON conversion
- Custom serializers
- Field naming and annotations

---

### Parameterized Tests

#### unit-test-parameterized

**File**: `skills/unit-test-parameterized/SKILL.md`

JUnit 5 `@ParameterizedTest` for multiple scenarios.

**When to use:**
- Testing multiple input cases
- Reducing test duplication
- Edge case coverage

**Pattern:**
```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void shouldProcess(int value) {
    assertTrue(service.isValid(value));
}
```

---

### Utilities & Boundary Conditions

#### unit-test-utility-methods

**File**: `skills/unit-test-utility-methods/SKILL.md`

Static methods, helpers, utility functions.

**When to use:**
- Testing utility classes
- Static factory methods
- Helper functions

---

#### unit-test-boundary-conditions

**File**: `skills/unit-test-boundary-conditions/SKILL.md`

Edge cases, limits, null values, boundary testing.

**When to use:**
- Boundary value analysis
- Null handling
- Limit testing

---

### External Integration

#### unit-test-wiremock-rest-api

**File**: `skills/unit-test-wiremock-rest-api/SKILL.md`

REST API mocking with WireMock for integration tests.

**When to use:**
- Mocking external APIs
- Stubbing HTTP responses
- Testing integration points

---

## Common Testing Workflows

### Testing REST Endpoint

```
1. unit-test-controller-layer      → Test request/response
2. unit-test-service-layer         → Test business logic
3. unit-test-exception-handler      → Test error cases
4. unit-test-parameterized          → Multiple scenarios
```

### Testing Secure Endpoint

```
1. unit-test-security-authorization → Mock user/roles
2. unit-test-controller-layer       → Test permission checks
3. unit-test-exception-handler      → Test authorization failures
```

### Testing Configuration

```
1. unit-test-config-properties      → Property binding
2. unit-test-service-layer          → Service uses config
3. unit-test-caching                → Cache config
```

### Testing Async Operations

```
1. unit-test-scheduled-async        → Async method execution
2. unit-test-application-events     → Event publishing
3. unit-test-parameterized          → Multiple timing scenarios
```

---

## Stack & Tools

- **JUnit**: 5.x (Jupiter)
- **Mocking**: Mockito, MockMvc
- **Assertions**: AssertJ
- **Spring Test**: Spring Boot Test
- **WireMock**: 3.0+
- **Testcontainers**: 1.19+

---

## Best Practices

- ✅ One assertion per test or related assertions
- ✅ Descriptive test method names
- ✅ Use `@ParameterizedTest` for multiple inputs
- ✅ Mock external dependencies
- ✅ Test edge cases and boundaries
- ✅ Keep tests isolated and independent
- ✅ Use builders for complex test data

---

**Note**: For complete patterns and examples, see individual skill files in `skills/`
