# Spring Security Authorization - Detailed Examples

## Setup: Security Testing Dependencies

### Maven

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.springframework.security</groupId>
  <artifactId>spring-security-test</artifactId>
  <scope>test</scope>
</dependency>
```

### Method Security Configuration (Spring Security 6+)

```java
@Configuration
@EnableMethodSecurity
class MethodSecurityConfig {
}
```

## Testing @Secured

```java
@Service
class OrderService {

  @Secured("ROLE_ADMIN")
  void approveOrder(Long orderId) {
    // business logic
  }
}

class OrderServiceSecurityTest {

  private final OrderService service = new OrderService();

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminToApproveOrder() {
    assertThatCode(() -> service.approveOrder(1L)).doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(roles = "USER")
  void shouldDenyUserFromApprovingOrder() {
    assertThatThrownBy(() -> service.approveOrder(1L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## Testing Expression-Based Authorization

```java
@Service
class DocumentService {

  @PreAuthorize("hasRole('ADMIN') or authentication.name == #owner")
  Document getDocument(String owner, Long docId) {
    return new Document(docId, owner);
  }
}

class DocumentServiceSecurityTest {

  private final DocumentService service = new DocumentService();

  @Test
  @WithMockUser(username = "alice", roles = "USER")
  void shouldAllowOwner() {
    assertThatCode(() -> service.getDocument("alice", 1L)).doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(username = "alice", roles = "USER")
  void shouldDenyNonOwner() {
    assertThatThrownBy(() -> service.getDocument("bob", 1L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## Testing Controller Security with MockMvc

```java
@RestController
@RequestMapping("/api/admin")
class AdminController {

  @GetMapping("/users")
  @PreAuthorize("hasRole('ADMIN')")
  List<String> listUsers() {
    return List.of("alice", "bob");
  }
}

class AdminControllerSecurityTest {

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders
      .standaloneSetup(new AdminController())
      .apply(springSecurity())
      .build();
  }

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminAccess() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isOk());
  }

  @Test
  @WithMockUser(roles = "USER")
  void shouldDenyUserAccess() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isForbidden());
  }
}
```

## Parameterized Multi-Role Checks

```java
class RoleMatrixTest {

  @ParameterizedTest
  @ValueSource(strings = {"ADMIN", "MANAGER"})
  void shouldAllowPrivilegedRoles(String role) {
    Authentication auth = new UsernamePasswordAuthenticationToken(
      "u", null, List.of(new SimpleGrantedAuthority("ROLE_" + role)));
    assertThat(hasAdminLikeRole(auth)).isTrue();
  }

  @ParameterizedTest
  @ValueSource(strings = {"USER", "GUEST"})
  void shouldDenyNonPrivilegedRoles(String role) {
    Authentication auth = new UsernamePasswordAuthenticationToken(
      "u", null, List.of(new SimpleGrantedAuthority("ROLE_" + role)));
    assertThat(hasAdminLikeRole(auth)).isFalse();
  }

  private boolean hasAdminLikeRole(Authentication auth) {
    return auth.getAuthorities().stream()
      .map(GrantedAuthority::getAuthority)
      .anyMatch(a -> a.equals("ROLE_ADMIN") || a.equals("ROLE_MANAGER"));
  }
}
```
