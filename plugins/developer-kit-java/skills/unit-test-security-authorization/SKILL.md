---
name: unit-test-security-authorization
description: Provides patterns for unit testing Spring Security with @PreAuthorize, @Secured, @RolesAllowed. Validates role-based access control and authorization policies. Use when testing security configurations and access control logic.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Security and Authorization

## Overview

Patterns for unit testing Spring Security authorization logic using @PreAuthorize, @Secured, @RolesAllowed, and custom permission evaluators. Covers testing RBAC, expression-based authorization, and verifying access denied scenarios.

## When to Use

Use this skill when:
- Testing @PreAuthorize and @Secured method-level security
- Testing role-based access control (RBAC)
- Testing custom permission evaluators
- Verifying access denied scenarios
- Want fast authorization tests without full Spring Security context

Trigger phrases:
- "test spring security authorization"
- "test preauthorize"
- "test secured annotation"
- "test permission evaluator"

## Instructions

1. **Add spring-security-test** to test dependencies
2. **Enable method security** with @EnableMethodSecurity
   > **Note**: `@EnableGlobalMethodSecurity` is deprecated in Spring Security 6+.
   > Use `@EnableMethodSecurity` which enables `@PreAuthorize` by default.
3. **Use @WithMockUser** to simulate authenticated users with specific roles
4. **Test both allow and deny** for each security rule
5. **Test expression-based authorization** (e.g., `authentication.principal.username == #owner`)
6. **Test custom permission evaluators** by creating Authentication objects directly
7. **Verify method interactions** with mocked dependencies

## Examples

### Testing @PreAuthorize

```java
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminToDeleteUser() {
    assertThatCode(() -> service.deleteUser(1L)).doesNotThrowAnyException();
}

@Test
@WithMockUser(roles = "USER")
void shouldDenyUserFromDeletingUser() {
    assertThatThrownBy(() -> service.deleteUser(1L))
        .isInstanceOf(AccessDeniedException.class);
}
```

### Testing Controller Security with MockMvc

```java
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminToListUsers() throws Exception {
    mockMvc.perform(get("/api/admin/users")).andExpect(status().isOk());
}

@Test
@WithMockUser(roles = "USER")
void shouldDenyUserFromListingUsers() throws Exception {
    mockMvc.perform(get("/api/admin/users")).andExpect(status().isForbidden());
}

@Test
void shouldDenyAnonymousAccess() throws Exception {
    mockMvc.perform(get("/api/admin/users")).andExpect(status().isUnauthorized());
}
```

### Testing Custom Permission Evaluator

```java
@BeforeEach
void setUp() {
    evaluator = new DocumentPermissionEvaluator(documentRepository);
    adminAuth = new UsernamePasswordAuthenticationToken("admin", null,
        List.of(new SimpleGrantedAuthority("ROLE_ADMIN")));
    userAuth = new UsernamePasswordAuthenticationToken("alice", null,
        List.of(new SimpleGrantedAuthority("ROLE_USER")));
}

@Test
void shouldGrantPermissionToDocumentOwner() {
    assertThat(evaluator.hasPermission(userAuth, document, "WRITE")).isTrue();
}

@Test
void shouldDenyPermissionToNonOwner() {
    Authentication otherUser = new UsernamePasswordAuthenticationToken("bob", null,
        List.of(new SimpleGrantedAuthority("ROLE_USER")));
    assertThat(evaluator.hasPermission(otherUser, document, "WRITE")).isFalse();
}
```

For detailed examples covering dependency setup, @Secured testing, expression-based authorization, and parameterized multi-role tests, see [Examples](references/examples.md).

## Best Practices

- **Test both allow and deny cases** for each security rule
- **Test with different roles** to verify role-based decisions
- **Test anonymous access separately** from authenticated access
- **Use @WithMockUser** for setting authenticated user context

## Constraints and Warnings

- @PreAuthorize works via proxies; direct method calls bypass security
- @EnableMethodSecurity (or @EnableGlobalMethodSecurity deprecated) must be enabled for @PreAuthorize/@Secured
- Spring adds "ROLE_" prefix automatically; use hasRole('ADMIN') not hasRole('ROLE_ADMIN')
- Security context is thread-local; be careful with async tests
- @WithMockUser creates simple Authentication; complex auth needs custom setup

## References

- [Spring Security Method Security](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#jc-method)
- [Spring Security Testing](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#test)
