# Basic Testing Patterns

## Testing `@PreAuthorize` with Role-Based Access Control

### Service with Security Annotations

```java
@Service
public class UserService {

  @PreAuthorize("hasRole('ADMIN')")
  public void deleteUser(Long userId) {
    // delete logic
  }

  @PreAuthorize("hasRole('USER')")
  public User getCurrentUser() {
    // get user logic
  }

  @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
  public List<User> listAllUsers() {
    // list logic
  }
}
```

### Unit Tests

```java
import org.junit.jupiter.api.Test;
import org.springframework.security.test.context.support.WithMockUser;
import static org.assertj.core.api.Assertions.*;

class UserServiceSecurityTest {

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminToDeleteUser() {
    UserService service = new UserService();

    assertThatCode(() -> service.deleteUser(1L))
      .doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(roles = "USER")
  void shouldDenyUserFromDeletingUser() {
    UserService service = new UserService();

    assertThatThrownBy(() -> service.deleteUser(1L))
      .isInstanceOf(AccessDeniedException.class);
  }

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminAndManagerToListUsers() {
    UserService service = new UserService();

    assertThatCode(() -> service.listAllUsers())
      .doesNotThrowAnyException();
  }

  @Test
  void shouldDenyAnonymousUserAccess() {
    UserService service = new UserService();

    assertThatThrownBy(() -> service.deleteUser(1L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## Testing `@Secured` Annotation

### Legacy Security Configuration

```java
@Service
public class OrderService {

  @Secured("ROLE_ADMIN")
  public Order approveOrder(Long orderId) {
    // approval logic
  }

  @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
  public List<Order> getOrders() {
    // get orders
  }
}
```

### Tests

```java
class OrderSecurityTest {

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminToApproveOrder() {
    OrderService service = new OrderService();

    assertThatCode(() -> service.approveOrder(1L))
      .doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(roles = "USER")
  void shouldDenyUserFromApprovingOrder() {
    OrderService service = new OrderService();

    assertThatThrownBy(() -> service.approveOrder(1L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## Testing Controller Security with MockMvc

### Secure REST Endpoints

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

  @GetMapping("/users")
  @PreAuthorize("hasRole('ADMIN')")
  public List<UserDto> listAllUsers() {
    // logic
  }

  @DeleteMapping("/users/{id}")
  @PreAuthorize("hasRole('ADMIN')")
  public void deleteUser(@PathVariable Long id) {
    // delete logic
  }
}
```

### Tests with MockMvc

```java
import org.springframework.security.test.context.support.WithMockUser;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

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
  void shouldAllowAdminToListUsers() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isOk());
  }

  @Test
  @WithMockUser(roles = "USER")
  void shouldDenyUserFromListingUsers() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isForbidden());
  }

  @Test
  void shouldDenyAnonymousAccessToAdminEndpoint() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isUnauthorized());
  }

  @Test
  @WithMockUser(roles = "ADMIN")
  void shouldAllowAdminToDeleteUser() throws Exception {
    mockMvc.perform(delete("/api/admin/users/1"))
      .andExpect(status().isOk());
  }
}
```

## Testing Multiple Roles with Parameterized Tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class RoleBasedAccessTest {

  private AdminService service;

  @BeforeEach
  void setUp() {
    service = new AdminService();
  }

  @ParameterizedTest
  @ValueSource(strings = {"ADMIN", "SUPER_ADMIN", "SYSTEM"})
  @WithMockUser(roles = "ADMIN")
  void shouldAllowPrivilegedRolesToDeleteUser(String role) {
    assertThatCode(() -> service.deleteUser(1L))
      .doesNotThrowAnyException();
  }

  @ParameterizedTest
  @ValueSource(strings = {"USER", "GUEST", "READONLY"})
  void shouldDenyUnprivilegedRolesToDeleteUser(String role) {
    assertThatThrownBy(() -> service.deleteUser(1L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## `@WithMockUser` Options

```java
// Basic usage
@WithMockUser
void testWithDefaultUser() { }

// With custom username
@WithMockUser(username = "alice")
void testWithCustomUsername() { }

// With roles
@WithMockUser(roles = "ADMIN")
void testWithRole() { }

// With multiple roles
@WithMockUser(roles = {"ADMIN", "USER"})
void testWithMultipleRoles() { }

// With authorities
@WithMockUser(authorities = "READ_PERMISSION")
void testWithAuthority() { }

// Complete configuration
@WithMockUser(
  username = "admin",
  password = "secret",
  roles = {"ADMIN", "USER"},
  authorities = {"READ", "WRITE"}
)
void testWithFullConfiguration() { }
```
