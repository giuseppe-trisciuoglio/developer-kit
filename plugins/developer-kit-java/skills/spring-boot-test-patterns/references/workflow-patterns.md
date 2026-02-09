# Spring Boot Testing Workflow Patterns

## Complete Database Integration Test Pattern

**Scenario**: Test a JPA repository with a real PostgreSQL database using Testcontainers.

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
public class UserRepositoryIntegrationTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUserFromDatabase() {
        // Arrange
        User user = new User();
        user.setEmail("test@example.com");
        user.setName("Test User");

        // Act
        User saved = userRepository.save(user);
        userRepository.flush();

        Optional<User> retrieved = userRepository.findByEmail("test@example.com");

        // Assert
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().getName()).isEqualTo("Test User");
    }

    @Test
    void shouldThrowExceptionForDuplicateEmail() {
        // Arrange
        User user1 = new User();
        user1.setEmail("duplicate@example.com");
        user1.setName("User 1");

        User user2 = new User();
        user2.setEmail("duplicate@example.com");
        user2.setName("User 2");

        userRepository.save(user1);

        // Act & Assert
        assertThatThrownBy(() -> {
            userRepository.save(user2);
            userRepository.flush();
        }).isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

## Complete REST API Integration Test Pattern

**Scenario**: Test REST controllers with full Spring context using MockMvc.

```java
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
public class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void shouldCreateUserAndReturn201() throws Exception {
        User user = new User();
        user.setEmail("newuser@example.com");
        user.setName("New User");

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(user)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.email").value("newuser@example.com"))
            .andExpect(jsonPath("$.name").value("New User"));
    }

    @Test
    void shouldReturnUserById() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("existing@example.com");
        user.setName("Existing User");
        User saved = userRepository.save(user);

        // Act & Assert
        mockMvc.perform(get("/api/users/" + saved.getId())
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("existing@example.com"))
            .andExpect(jsonPath("$.name").value("Existing User"));
    }

    @Test
    void shouldReturnNotFoundForMissingUser() throws Exception {
        mockMvc.perform(get("/api/users/99999")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldUpdateUserAndReturn200() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("update@example.com");
        user.setName("Original Name");
        User saved = userRepository.save(user);

        User updateData = new User();
        updateData.setName("Updated Name");

        // Act & Assert
        mockMvc.perform(put("/api/users/" + saved.getId())
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(updateData)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Updated Name"));
    }

    @Test
    void shouldDeleteUserAndReturn204() throws Exception {
        // Arrange
        User user = new User();
        user.setEmail("delete@example.com");
        user.setName("To Delete");
        User saved = userRepository.save(user);

        // Act & Assert
        mockMvc.perform(delete("/api/users/" + saved.getId()))
            .andExpect(status().isNoContent());

        assertThat(userRepository.findById(saved.getId())).isEmpty();
    }
}
```

## Service Layer Integration Test Pattern

**Scenario**: Test business logic with mocked repository.

```java
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void shouldFindUserByIdWhenExists() {
        // Arrange
        Long userId = 1L;
        User user = new User();
        user.setId(userId);
        user.setEmail("test@example.com");

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getEmail()).isEqualTo("test@example.com");
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        // Arrange
        Long userId = 999L;
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // Act
        Optional<User> result = userService.findById(userId);

        // Assert
        assertThat(result).isEmpty();
        verify(userRepository, times(1)).findById(userId);
    }

    @Test
    void shouldThrowExceptionWhenSavingInvalidUser() {
        // Arrange
        User invalidUser = new User();
        invalidUser.setEmail("invalid-email");

        when(userRepository.save(invalidUser))
            .thenThrow(new DataIntegrityViolationException("Invalid email"));

        // Act & Assert
        assertThatThrownBy(() -> userService.save(invalidUser))
            .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

## Reactive WebFlux Integration Test Pattern

**Scenario**: Test WebFlux controllers with WebTestClient.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
public class ReactiveUserControllerIntegrationTest {

    @Autowired
    private WebTestClient webTestClient;

    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void shouldReturnUserAsJsonReactive() {
        // Arrange
        User user = new User();
        user.setEmail("reactive@example.com");
        user.setName("Reactive User");
        User saved = userRepository.save(user);

        // Act & Assert
        webTestClient.get()
            .uri("/api/users/" + saved.getId())
            .exchange()
            .expectStatus().isOk()
            .expectBody()
            .jsonPath("$.email").isEqualTo("reactive@example.com")
            .jsonPath("$.name").isEqualTo("Reactive User");
    }

    @Test
    void shouldReturnArrayOfUsers() {
        // Arrange
        User user1 = new User();
        user1.setEmail("user1@example.com");
        user1.setName("User 1");

        User user2 = new User();
        user2.setEmail("user2@example.com");
        user2.setName("User 2");

        userRepository.saveAll(List.of(user1, user2));

        // Act & Assert
        webTestClient.get()
            .uri("/api/users")
            .exchange()
            .expectStatus().isOk()
            .expectBodyList(User.class)
            .hasSize(2);
    }
}
```

## Testcontainers Configuration Patterns

### @ServiceConnection Pattern (Spring Boot 3.5+)

```java
@TestConfiguration
public class TestContainerConfig {

    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"))
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
        // Do not call start(); Spring Boot will manage lifecycle for @ServiceConnection beans
    }
}
```

### @DynamicPropertySource Pattern (Legacy)

```java
public class SharedContainers {
    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(DockerImageName.parse("postgres:16-alpine"))
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @BeforeAll
    static void startAll() {
        POSTGRES.start();
    }

    @AfterAll
    static void stopAll() {
        POSTGRES.stop();
    }

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
    }
}
```

### Slice Tests with Testcontainers

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
public class MyRepositoryIntegrationTest {
    // repository tests
}
```