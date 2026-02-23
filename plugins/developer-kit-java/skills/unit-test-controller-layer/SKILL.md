---
name: unit-test-controller-layer
description: Provides patterns for unit testing REST controllers using MockMvc and @WebMvcTest. Validates request/response mapping, validation, and exception handling. Use when testing web layer endpoints in isolation.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing REST Controllers with MockMvc

## Overview

This skill defines fast, isolated patterns for controller tests in Spring Boot 3.x.
Use `@WebMvcTest` with mocked collaborators to validate HTTP contracts without starting full infrastructure.

## When to Use

Use this skill when:
- Testing request-to-response mapping in `@RestController` or `@Controller`
- Verifying HTTP status codes and response payload structure
- Testing request body validation and binding errors
- Validating exception translation via `@ControllerAdvice`

Trigger phrases:
- "test controller with mockmvc"
- "webmvctest for endpoint"
- "controller validation test"
- "unit test rest endpoint"

## Instructions

1. Use `@WebMvcTest` for controller-slice tests and mock every service dependency.
2. Use `MockMvc` for all requests and assert both status and payload fields.
3. Validate body, query parameter, path variable, and header binding paths.
4. Test invalid input and assert exact validation error responses.
5. Include `@ControllerAdvice` in the slice when testing exception mapping.
6. Verify service interactions with Mockito `verify`.

## Examples

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean UserService userService;

  @Test
  void shouldReturn200() throws Exception {
    when(userService.find(1L)).thenReturn(new UserDto(1L, "Alice"));
    mockMvc.perform(get("/users/1"))
      .andExpect(status().isOk())
      .andExpect(jsonPath("$.name").value("Alice"));
  }
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Prefer `@WebMvcTest` over full `@SpringBootTest` for controller unit scope.
- Assert explicit JSON fields with `jsonPath` instead of string matching.
- Cover success, validation failure, and domain error paths for each endpoint.

## Constraints and Warnings

- `@WebMvcTest` does not load full application beans; missing mocks will fail startup.
- Validation assertions depend on active Jakarta Validation annotations in request DTOs.
- Standalone MockMvc setup may bypass global `@ControllerAdvice` unless explicitly configured.
- Security filters can change status codes if not disabled or configured in test slice.

## Constraints

- Do not call real database, network, or filesystem dependencies in controller tests.
- Do not duplicate service-layer business logic assertions here.
- Keep tests deterministic and avoid timing-based assertions.

## References

- [Examples](references/examples.md) - Complete runnable test examples
