# Slice Testing Patterns

## Repository Slice Tests

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
class UserRepositoryIntegrationTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUser() {
        // Arrange
        User user = new User();
        user.setEmail("test@example.com");
        user.setName("Test User");

        // Act
        User saved = userRepository.save(user);
        userRepository.flush();

        // Assert
        Optional<User> retrieved = userRepository.findByEmail("test@example.com");
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().getName()).isEqualTo("Test User");
    }

    @Test
    void shouldFindAllActiveUsers() {
        // Arrange
        User activeUser = new User();
        activeUser.setEmail("active@example.com");
        activeUser.setActive(true);

        User inactiveUser = new User();
        inactiveUser.setEmail("inactive@example.com");
        inactiveUser.setActive(false);

        userRepository.saveAll(List.of(activeUser, inactiveUser));

        // Act
        List<User> activeUsers = userRepository.findByActiveTrue();

        // Assert
        assertThat(activeUsers).hasSize(1);
        assertThat(activeUsers.get(0).getEmail()).isEqualTo("active@example.com");
    }

    @Test
    void shouldDeleteUser() {
        // Arrange
        User user = new User();
        user.setEmail("delete@example.com");
        User saved = userRepository.save(user);

        // Act
        userRepository.deleteById(saved.getId());
        userRepository.flush();

        // Assert
        assertThat(userRepository.findById(saved.getId())).isEmpty();
    }
}
```

## Controller Slice Tests

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private UserService userService;

    @Test
    void shouldGetUserById() throws Exception {
        // Arrange
        User user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        user.setName("Test User");

        when(userService.findById(1L)).thenReturn(Optional.of(user));

        // Act & Assert
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.email").value("test@example.com"))
            .andExpect(jsonPath("$.name").value("Test User"));
    }

    @Test
    void shouldReturn404WhenUserNotFound() throws Exception {
        // Arrange
        when(userService.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldCreateUser() throws Exception {
        // Arrange
        CreateUserRequest request = new CreateUserRequest();
        request.setEmail("new@example.com");
        request.setName("New User");

        User createdUser = new User();
        createdUser.setId(1L);
        createdUser.setEmail("new@example.com");
        createdUser.setName("New User");

        when(userService.createUser(any())).thenReturn(createdUser);

        // Act & Assert
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.email").value("new@example.com"));
    }

    @Test
    void shouldValidateRequest() throws Exception {
        // Arrange
        CreateUserRequest request = new CreateUserRequest();
        request.setEmail(""); // Invalid

        // Act & Assert
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest());
    }
}
```

## JSON Slice Tests

```java
@JsonTest
class UserJsonSerializationTest {

    @Autowired
    private JacksonTester<User> json;

    @Test
    void shouldSerializeUser() throws JsonProcessingException {
        // Arrange
        User user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");
        user.setName("Test User");

        // Act
        JsonContent<User> result = json.write(user);

        // Assert
        assertThat(result).hasJsonPathValue("$.id", 1);
        assertThat(result).hasJsonPathValue("$.email", "test@example.com");
        assertThat(result).hasJsonPathValue("$.name", "Test User");
    }

    @Test
    void shouldDeserializeUser() throws IOException {
        // Arrange
        String jsonContent = """
            {
                "id": 1,
                "email": "test@example.com",
                "name": "Test User"
            }
            """;

        // Act
        User result = json.parse(jsonContent).getObject();

        // Assert
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        assertThat(result.getName()).isEqualTo("Test User");
    }
}
```

## WebFlux Controller Tests

```java
@WebFluxTest(UserController.class)
class ReactiveUserControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private UserService userService;

    @Test
    void shouldGetUserById() {
        // Arrange
        User user = new User();
        user.setId(1L);
        user.setEmail("test@example.com");

        when(userService.findById(1L)).thenReturn(Mono.just(user));

        // Act & Assert
        webTestClient.get()
            .uri("/api/users/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody(User.class)
            .isEqualTo(user);
    }

    @Test
    void shouldReturn404WhenUserNotFound() {
        // Arrange
        when(userService.findById(999L)).thenReturn(Mono.empty());

        // Act & Assert
        webTestClient.get()
            .uri("/api/users/999")
            .exchange()
            .expectStatus().isNotFound();
    }
}
```

## Testing ControllerAdvice

```java
@WebMvcTest(UserController.class)
class UserControllerExceptionTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldHandleUserNotFoundException() throws Exception {
        // Arrange
        when(userService.findById(999L))
            .thenThrow(new UserNotFoundException("User not found"));

        // Act & Assert
        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.message").value("User not found"));
    }
}
```
