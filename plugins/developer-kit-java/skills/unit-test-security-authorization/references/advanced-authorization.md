# Advanced Authorization Testing

## Testing Expression-Based Authorization

### Complex Permission Expressions

```java
@Service
public class DocumentService {

  @PreAuthorize("hasRole('ADMIN') or authentication.principal.username == #owner")
  public Document getDocument(String owner, Long docId) {
    // get document
  }

  @PreAuthorize("hasPermission(#docId, 'Document', 'WRITE')")
  public void updateDocument(Long docId, String content) {
    // update logic
  }

  @PreAuthorize("#userId == authentication.principal.id")
  public UserProfile getUserProfile(Long userId) {
    // get profile
  }
}
```

### Tests

```java
class ExpressionBasedSecurityTest {

  @Test
  @WithMockUser(username = "alice", roles = "ADMIN")
  void shouldAllowAdminToAccessAnyDocument() {
    DocumentService service = new DocumentService();

    assertThatCode(() -> service.getDocument("bob", 1L))
      .doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(username = "alice")
  void shouldAllowOwnerToAccessOwnDocument() {
    DocumentService service = new DocumentService();

    assertThatCode(() -> service.getDocument("alice", 1L))
      .doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(username = "alice")
  void shouldDenyUserAccessToOtherUserDocument() {
    DocumentService service = new DocumentService();

    assertThatThrownBy(() -> service.getDocument("bob", 1L))
      .isInstanceOf(AccessDeniedException.class);
  }

  @Test
  @WithMockUser(username = "alice", id = "1")
  void shouldAllowUserToAccessOwnProfile() {
    DocumentService service = new DocumentService();

    assertThatCode(() -> service.getUserProfile(1L))
      .doesNotThrowAnyException();
  }

  @Test
  @WithMockUser(username = "alice", id = "1")
  void shouldDenyUserAccessToOtherProfile() {
    DocumentService service = new DocumentService();

    assertThatThrownBy(() -> service.getUserProfile(999L))
      .isInstanceOf(AccessDeniedException.class);
  }
}
```

## Testing Custom Permission Evaluator

### Custom Permission Evaluator Implementation

```java
@Component
public class DocumentPermissionEvaluator implements PermissionEvaluator {

  private final DocumentRepository documentRepository;

  public DocumentPermissionEvaluator(DocumentRepository documentRepository) {
    this.documentRepository = documentRepository;
  }

  @Override
  public boolean hasPermission(Authentication authentication,
                               Object targetDomainObject,
                               Object permission) {
    if (authentication == null) return false;

    Document document = (Document) targetDomainObject;
    String userUsername = authentication.getName();

    return document.getOwner().getUsername().equals(userUsername) ||
           userHasRole(authentication, "ADMIN");
  }

  @Override
  public boolean hasPermission(Authentication authentication,
                               Serializable targetId,
                               String targetType,
                               Object permission) {
    if (authentication == null) return false;
    if (!"Document".equals(targetType)) return false;

    Document document = documentRepository.findById((Long) targetId).orElse(null);
    if (document == null) return false;

    return hasPermission(authentication, document, permission);
  }

  private boolean userHasRole(Authentication authentication, String role) {
    return authentication.getAuthorities().stream()
      .anyMatch(auth -> auth.getAuthority().equals("ROLE_" + role));
  }
}
```

### Unit Tests for Custom Evaluator

```java
class DocumentPermissionEvaluatorTest {

  private DocumentPermissionEvaluator evaluator;
  private DocumentRepository documentRepository;
  private Authentication adminAuth;
  private Authentication userAuth;
  private Document document;

  @BeforeEach
  void setUp() {
    documentRepository = mock(DocumentRepository.class);
    evaluator = new DocumentPermissionEvaluator(documentRepository);

    document = new Document(1L, "Test Doc", new User("alice"));

    adminAuth = new UsernamePasswordAuthenticationToken(
      "admin",
      null,
      List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))
    );

    userAuth = new UsernamePasswordAuthenticationToken(
      "alice",
      null,
      List.of(new SimpleGrantedAuthority("ROLE_USER"))
    );
  }

  @Test
  void shouldGrantPermissionToDocumentOwner() {
    boolean hasPermission = evaluator.hasPermission(userAuth, document, "WRITE");

    assertThat(hasPermission).isTrue();
  }

  @Test
  void shouldDenyPermissionToNonOwner() {
    Authentication otherUserAuth = new UsernamePasswordAuthenticationToken(
      "bob",
      null,
      List.of(new SimpleGrantedAuthority("ROLE_USER"))
    );

    boolean hasPermission = evaluator.hasPermission(otherUserAuth, document, "WRITE");

    assertThat(hasPermission).isFalse();
  }

  @Test
  void shouldGrantPermissionToAdmin() {
    boolean hasPermission = evaluator.hasPermission(adminAuth, document, "WRITE");

    assertThat(hasPermission).isTrue();
  }

  @Test
  void shouldDenyNullAuthentication() {
    boolean hasPermission = evaluator.hasPermission(null, document, "WRITE");

    assertThat(hasPermission).isFalse();
  }

  @Test
  void shouldHandleDocumentNotFound() {
    when(documentRepository.findById(1L)).thenReturn(Optional.empty());

    boolean hasPermission = evaluator.hasPermission(adminAuth, 1L, "Document", "WRITE");

    assertThat(hasPermission).isFalse();
  }
}
```

## Common SpEL Expressions

### Authentication-Based Expressions

```java
// Check if user is authenticated
@PreAuthorize("isAuthenticated()")

// Check if user is anonymous
@PreAuthorize("isAnonymous()")

// Check if user is fully authenticated (not remember-me)
@PreAuthorize("isFullyAuthenticated()")

// Check if user has remember-me authentication
@PreAuthorize("hasPermission(#userId, 'read')")
```

### Role-Based Expressions

```java
// Has specific role (ROLE_ prefix added automatically)
@PreAuthorize("hasRole('ADMIN')")

// Has any of the specified roles
@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'SUPERVISOR')")

// Does not have role
@PreAuthorize("!hasRole('GUEST')")
```

### Principal-Based Expressions

```java
// Access principal username
@PreAuthorize("authentication.principal.username == #username")

// Access principal properties
@PreAuthorize("authentication.principal.accountNonLocked")

// Check principal ID
@PreAuthorize("authentication.principal.id == #userId")
```

### Permission-Based Expressions

```java
// Check custom permission
@PreAuthorize("hasPermission(#objectId, 'READ')")

// Check permission with type
@PreAuthorize("hasPermission(#objectId, 'Document', 'WRITE')")

// Multiple permission checks
@PreAuthorize("hasPermission(#docId, 'READ') and hasPermission(#docId, 'WRITE')")
```

### Complex Expressions

```java
// OR condition
@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")

// AND condition
@PreAuthorize("hasRole('ADMIN') and hasPermission(#docId, 'WRITE')")

// NOT condition
@PreAuthorize("hasRole('ADMIN') and !isBanned(#username)")

// Complex expression with parentheses
@PreAuthorize("(hasRole('ADMIN') or #isOwner) and !isLocked(#userId)")
```

## Testing `@PostAuthorize`

```java
@Service
public class MessageService {

  @PostAuthorize("returnObject.owner == authentication.principal.username")
  public Message getMessage(Long messageId) {
    // fetch and return message
  }
}

@Test
@WithMockUser(username = "alice")
void shouldAllowAccessToOwnMessage() {
  MessageService service = new MessageService();

  Message message = service.getMessage(1L);
  assertThat(message.getOwner()).isEqualTo("alice");
}

@Test
@WithMockUser(username = "alice")
void shouldDenyAccessToOtherMessage() {
  MessageService service = new MessageService();

  assertThatThrownBy(() -> service.getMessage(2L))
    .isInstanceOf(AccessDeniedException.class);
}
```

## Testing `@PostFilter` and `@PreFilter`

```java
@Service
public class DataService {

  @PreFilter("hasPermission(filterObject, 'READ')")
  public void processData(List<Data> items) {
    // items filtered before method execution
  }

  @PostFilter("hasPermission(filterObject, 'READ')")
  public List<Data> getAllData() {
    // results filtered after method execution
    return repository.findAll();
  }
}

@Test
@WithMockUser(roles = "ADMIN")
void shouldFilterDataBasedOnPermissions() {
  List<Data> input = List.of(data1, data2, data3);

  service.processData(input);

  // Verify only permitted items were processed
  verify(repository).saveAll(List.of(data1, data3));
}
```
