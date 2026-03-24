# Troubleshooting Controller Tests

## Common Issues and Solutions

### Content Type Mismatch

**Symptom**: `415 Unsupported Media Type` error

**Solution**: Ensure `contentType()` matches controller's `@PostMapping(consumes=...)`

```java
// Wrong
mockMvc.perform(post("/api/users").content("{}"));

// Correct
mockMvc.perform(post("/api/users")
    .contentType("application/json")
    .content("{}"));
```

### JsonPath Not Matching

**Symptom**: JsonPath assertions fail without clear reason

**Solution**: Use `.andDo(print())` to see actual response

```java
mockMvc.perform(get("/api/users/1"))
  .andDo(print())  // Add this to debug
  .andExpect(jsonPath("$.name").value("Alice"));
```

### Status Code Assertions Fail

**Symptom**: Expected 200 but got 404/500

**Solution**:
1. Check controller `@RequestMapping` paths match test URLs
2. Verify error handling returns expected status
3. Ensure service mocks are set up before request

```java
// Verify controller path
@RequestMapping("/api/users")  // Matches "/api/users" not "/users"

// Verify mock setup order
when(userService.getUserById(1L)).thenReturn(user);  // Before perform
mockMvc.perform(get("/api/users/1"))...
```

### Mock Not Being Called

**Symptom**: `verify()` fails with "never invoked"

**Solution**:
1. Check mock setup happens before `perform()`
2. Verify mock parameters match actual call parameters
3. Use `any()` for flexible matching

```java
// Use any() for flexible matching
when(userService.createUser(any())).thenReturn(user);
verify(userService).createUser(any());  // Not exact argument
```

### Response Body Empty

**Symptom**: JsonPath finds nothing in response

**Solution**:
1. Verify controller returns response body
2. Check `@ResponseBody` or `@RestController` annotation
3. Ensure object serialization works

```java
// Controller should return the object
@GetMapping("/{id}")
public UserDto getUser(@PathVariable Long id) {
  return userService.getUserById(id);  // Return, not void
}
```

### ObjectMapper Issues

**Symptom**: JSON serialization errors or null values

**Solution**: Configure ObjectMapper in standalone setup

```java
Jackson2ObjectMapperBuilder mapperBuilder = Jackson2ObjectMapperBuilder.json();
mockMvc = MockMvcBuilders.standaloneSetup(controller)
  .setMessageConverters(new MappingJackson2HttpMessageConverter(mapperBuilder.build()))
  .build();
```

### Validation Not Working

**Symptom**: Validation constraints ignored, 500 instead of 400

**Solution**: Add validator to standalone setup

```java
@BeforeEach
void setUp() {
  MockitoAnnotations.openMocks(this);
  mockMvc = MockMvcBuilders.standaloneSetup(userController)
    .setValidator(validator)  // Add local validator
    .build();
}
```

### NullPointerException in Controller

**Symptom**: Tests pass locally but fail in CI

**Solution**: Ensure all controller dependencies are mocked

```java
@Mock
private UserService userService;

@Mock
private ValidationService validationService;  // Don't forget this one

@InjectMocks
private UserController userController;
```
