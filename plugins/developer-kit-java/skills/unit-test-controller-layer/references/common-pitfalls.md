# Common Pitfalls in Controller Testing

## Testing Business Logic in Controller

**Don't**: Test business logic in controller tests

**Do**: Keep controller tests focused on HTTP handling only

```java
// BAD - Testing business logic
@Test
void shouldCalculateTotalCorrectly() throws Exception {
  // This should be in service tests
  mockMvc.perform(get("/api/orders/1/total"))
    .andExpect(jsonPath("$.total").value(150.00));
}

// GOOD - Testing HTTP response
@Test
void shouldReturnOrderTotalAsJson() throws Exception {
  when(orderService.getOrderTotal(1L)).thenReturn(150.00);

  mockMvc.perform(get("/api/orders/1/total"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.total").exists());

  verify(orderService).getOrderTotal(1L);
}
```

## Not Mocking Service Layer

**Don't**: Leave service layer unmocked

**Do**: Always mock service dependencies

```java
// BAD - Unmocked service
@InjectMocks
private UserController userController;  // userService is null!

// GOOD - Mocked service
@Mock
private UserService userService;

@InjectMocks
private UserController userController;
```

## Testing Framework Behavior

**Don't**: Test Spring MVC framework internals

**Do**: Test your controller code only

```java
// BAD - Testing Spring behavior
mockMvc.perform(get("/api/users"))
  .andExpect(handler().methodName("getUsers"))  // Don't test this
  .andExpect(handler().controllerClass(UserController.class));

// GOOD - Testing your code
mockMvc.perform(get("/api/users"))
  .andExpect(status().isOk())
  .andExpect(jsonPath("$").isArray());
```

## Hardcoding URLs

**Don't**: Use string URLs throughout tests

**Do**: Use controller's `@RequestMapping` values or constants

```java
// BAD
mockMvc.perform(get("/users/1")).andExpect(status().isOk());
mockMvc.perform(post("/users")).andExpect(status().isCreated());

// GOOD - Extract to constants
private static final String BASE_URL = "/api/users";

@Test
void shouldGetUser() throws Exception {
  mockMvc.perform(get(BASE_URL + "/1")).andExpect(status().isOk());
}
```

## Not Verifying Mock Interactions

**Don't**: Forget to verify service was called

**Do**: Always verify mock interactions

```java
// BAD - No verification
@Test
void shouldReturnUser() throws Exception {
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));
  mockMvc.perform(get("/api/users/1"))
    .andExpect(status().isOk());
  // Service might not have been called at all!
}

// GOOD - With verification
@Test
void shouldReturnUser() throws Exception {
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));
  mockMvc.perform(get("/api/users/1"))
    .andExpect(status().isOk());

  verify(userService).getUserById(1L);  // Verify it was called
}
```

## Missing Error Path Tests

**Don't**: Only test happy paths

**Do**: Test error scenarios too

```java
// BAD - Only happy path
@Test
void shouldReturnUser() throws Exception {
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));
  mockMvc.perform(get("/api/users/1"))
    .andExpect(status().isOk());
}

// GOOD - Happy path AND error path
@Test
void shouldReturnUser() throws Exception {
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));
  mockMvc.perform(get("/api/users/1"))
    .andExpect(status().isOk());
}

@Test
void shouldReturn404WhenUserNotFound() throws Exception {
  when(userService.getUserById(999L))
    .thenThrow(new UserNotFoundException("Not found"));
  mockMvc.perform(get("/api/users/999"))
    .andExpect(status().isNotFound());
}
```

## Incorrect JSON Comparison

**Don't**: Use exact string comparison for JSON

**Do**: Use JsonPath for flexible assertions

```java
// BAD - Brittle
.andExpect(content().string(containsString("{\"id\":1,\"name\":\"Alice\"}")));

// GOOD - Flexible
.andExpect(jsonPath("$.id").value(1))
.andExpect(jsonPath("$.name").value("Alice"));
```

## Forgotten Setup Method

**Don't**: Initialize MockMvc in each test

**Do**: Use `@ BeforeEach` for shared setup

```java
// BAD - Repetitive
@Test
void shouldGetUser() throws Exception {
  MockMvc mockMvc = MockMvcBuilders.standaloneSetup(userController).build();
  ...
}

// GOOD - Shared setup
private MockMvc mockMvc;

@BeforeEach
void setUp() {
  mockMvc = MockMvcBuilders.standaloneSetup(userController).build();
}
```
