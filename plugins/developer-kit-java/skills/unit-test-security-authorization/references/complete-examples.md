# Complete Examples - Before and After

## Example 1: Adding Security Tests

### Input: Service Without Security Testing

```java
@Service
public class AdminService {
    public void deleteUser(Long userId) {
        // Delete logic without security check
        repository.deleteById(userId);
    }
}
```

### Output: Service With Security Test Coverage

```java
@Service
public class AdminService {
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(Long userId) {
        // Delete logic with security check
        repository.deleteById(userId);
    }
}

// Test
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminToDeleteUser() {
    assertThatCode(() -> adminService.deleteUser(1L))
        .doesNotThrowAnyException();
}

@Test
@WithMockUser(roles = "USER")
void shouldDenyUserFromDeletingUser() {
    assertThatThrownBy(() -> adminService.deleteUser(1L))
        .isInstanceOf(AccessDeniedException.class);
}
```

## Example 2: Replacing Manual Security Checks

### Input: Manual Security Check (Anti-Pattern)

```java
@Service
public class AdminService {
    private final UserRepository userRepository;

    public void deleteUser(Long userId, User currentUser) {
        // Manual security check in business logic
        if (currentUser.hasRole("ADMIN")) {
            repository.deleteById(userId);
        } else {
            throw new AccessDeniedException("Not authorized");
        }
    }
}
```

### Output: Declarative Security with Testing

```java
@Service
public class AdminService {
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(Long userId) {
        // Business logic only, security is declarative
        repository.deleteById(userId);
    }
}

// Test verifies security enforcement
@Test
@WithMockUser(roles = "ADMIN")
void shouldExecuteDelete() {
    service.deleteUser(1L);
    verify(repository).deleteById(1L);
}

@Test
@WithMockUser(roles = "USER")
void shouldNotExecuteDeleteDueToSecurity() {
    assertThatThrownBy(() -> service.deleteUser(1L))
        .isInstanceOf(AccessDeniedException.class);

    verify(repository, never()).deleteById(anyLong());
}
```

## Example 3: Controller Security Testing

### Input: Insecure Controller

```java
@RestController
@RequestMapping("/api")
public class UserController {

    @GetMapping("/users/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @DeleteMapping("/users/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        service.deleteUser(id);
        return ResponseEntity.ok().build();
    }
}
```

### Output: Secure Controller with Tests

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @GetMapping("/users/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @DeleteMapping("/users/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        service.deleteUser(id);
        return ResponseEntity.ok().build();
    }
}

// Tests
@SpringBootTest
@AutoConfigureMockMvc
class AdminControllerSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminToGetUser() throws Exception {
        mockMvc.perform(get("/api/admin/users/1"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldDenyUserFromGettingUser() throws Exception {
        mockMvc.perform(get("/api/admin/users/1"))
            .andExpect(status().isForbidden());
    }

    @Test
    void shouldDenyAnonymousAccess() throws Exception {
        mockMvc.perform(get("/api/admin/users/1"))
            .andExpect(status().isUnauthorized());
    }
}
```

## Example 4: Custom Permission Evaluator

### Input: Inline Permission Check

```java
@Service
public class DocumentService {
    private final DocumentRepository repository;

    public Document getDocument(Long docId, User currentUser) {
        Document doc = repository.findById(docId)
            .orElseThrow(() -> new NotFoundException());

        // Inline permission check
        if (!doc.getOwner().equals(currentUser.getUsername()) &&
            !currentUser.hasRole("ADMIN")) {
            throw new AccessDeniedException("Access denied");
        }

        return doc;
    }
}
```

### Output: Declarative Security with Custom Evaluator

```java
@Service
public class DocumentService {

    @PreAuthorize("hasPermission(#docId, 'Document', 'READ')")
    public Document getDocument(Long docId) {
        return repository.findById(docId)
            .orElseThrow(() -> new NotFoundException());
    }
}

// Custom Permission Evaluator
@Component
public class DocumentPermissionEvaluator implements PermissionEvaluator {

    @Override
    public boolean hasPermission(Authentication authentication,
                               Serializable targetId,
                               String targetType,
                               Object permission) {
        // Permission logic extracted and reusable
        Document doc = repository.findById(targetId).orElse(null);
        if (doc == null) return false;

        return doc.getOwner().equals(authentication.getName()) ||
               hasRole(authentication, "ADMIN");
    }
}

// Test
@SpringBootTest
class DocumentServiceSecurityTest {

    @Autowired
    private DocumentService service;

    @Test
    @WithMockUser(username = "alice")
    void shouldAllowOwnerToReadDocument() {
        Document doc = service.getDocument(1L);
        assertThat(doc.getOwner()).isEqualTo("alice");
    }

    @Test
    @WithMockUser(username = "alice")
    void shouldDenyNonOwnerFromReadingDocument() {
        assertThatThrownBy(() -> service.getDocument(2L))
            .isInstanceOf(AccessDeniedException.class);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminToReadAnyDocument() {
        Document doc = service.getDocument(2L);
        assertThat(doc).isNotNull();
    }
}
```

## Example 5: Complex Expression-Based Security

### Input: Multiple Manual Checks

```java
@Service
public class ProfileService {

    public UserProfile updateProfile(Long userId, ProfileUpdate update, User currentUser) {
        // Multiple manual checks
        if (!currentUser.getId().equals(userId) &&
            !currentUser.hasRole("ADMIN") &&
            !currentUser.hasRole("MODERATOR")) {
            throw new AccessDeniedException("Access denied");
        }

        if (update.isPublic() && !currentUser.isVerified()) {
            throw new AccessDeniedException("Verified users only");
        }

        return repository.update(userId, update);
    }
}
```

### Output: Declarative Expression-Based Security

```java
@Service
public class ProfileService {

    @PreAuthorize("#userId == authentication.principal.id or " +
                  "hasAnyRole('ADMIN', 'MODERATOR')")
    public UserProfile updateProfile(Long userId, ProfileUpdate update) {
        return repository.update(userId, update);
    }

    @PreAuthorize("isVerified() and hasRole('USER')")
    public void makePublic(Long userId) {
        repository.setPublic(userId, true);
    }
}

// Test
@SpringBootTest
class ProfileServiceSecurityTest {

    @Autowired
    private ProfileService service;

    @Test
    @WithMockUser(username = "alice", id = "1")
    void shouldAllowUserToUpdateOwnProfile() {
        ProfileUpdate update = new ProfileUpdate("Alice Updated");
        assertThatCode(() -> service.updateProfile(1L, update))
            .doesNotThrowAnyException();
    }

    @Test
    @WithMockUser(username = "alice", id = "1")
    void shouldDenyUserFromUpdatingOtherProfile() {
        ProfileUpdate update = new ProfileUpdate("Hacked");
        assertThatThrownBy(() -> service.updateProfile(2L, update))
            .isInstanceOf(AccessDeniedException.class);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAllowAdminToUpdateAnyProfile() {
        ProfileUpdate update = new ProfileUpdate("Admin Update");
        assertThatCode(() -> service.updateProfile(2L, update))
            .doesNotThrowAnyException();
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldDenyUnverifiedUserFromMakingProfilePublic() {
        assertThatThrownBy(() -> service.makePublic(1L))
            .isInstanceOf(AccessDeniedException.class);
    }
}
```

## Key Takeaways

1. **Move from imperative to declarative security** - Use annotations instead of manual checks
2. **Separate security logic from business logic** - Keep code focused on business requirements
3. **Test both positive and negative cases** - Verify both access granted and denied scenarios
4. **Use appropriate test annotations** - `@WithMockUser` for most cases, custom setup for complex scenarios
5. **Test with MockMvc for controllers** - Verifies security filters are properly configured
6. **Create reusable permission evaluators** - Extract complex permission logic into dedicated components
