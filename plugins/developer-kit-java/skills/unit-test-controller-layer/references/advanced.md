# Advanced Controller Testing Patterns

## Multiple Status Code Scenarios

```java
@Test
void shouldReturnDifferentStatusCodesForDifferentScenarios() throws Exception {
  // Successful response
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));
  mockMvc.perform(get("/api/users/1"))
    .andExpect(status().isOk());

  // Not found
  when(userService.getUserById(999L))
    .thenThrow(new UserNotFoundException("Not found"));
  mockMvc.perform(get("/api/users/999"))
    .andExpect(status().isNotFound());

  // Unauthorized
  mockMvc.perform(get("/api/admin/users"))
    .andExpect(status().isUnauthorized());
}
```

## Security Testing

### Testing Role-Based Access

```java
@Test
void shouldReturn403WhenUserLacksRole() throws Exception {
  mockMvc.perform(delete("/api/admin/users/1"))
    .andExpect(status().isForbidden());
}
```

### Testing Authentication

```java
@Test
void shouldReturn401WhenNoTokenProvided() throws Exception {
  mockMvc.perform(get("/api/protected"))
    .andExpect(status().isUnauthorized());
}

@Test
void shouldReturn200WhenValidTokenProvided() throws Exception {
  when(authService.validateToken("valid-token")).thenReturn(true);
  when(userService.getCurrentUser()).thenReturn(new UserDto(1L, "Alice"));

  mockMvc.perform(get("/api/protected")
      .header("Authorization", "Bearer valid-token"))
    .andExpect(status().isOk());
}
```

## File Upload Testing

### MockMultipartFile

```java
@Test
void shouldUploadFileSuccessfully() throws Exception {
  byte[] fileContent = "test file content".getBytes();
  MockMultipartFile file = new MockMultipartFile(
    "file", "test.txt", "text/plain", fileContent);

  when(fileService.store(any())).thenReturn("stored-file-id");

  mockMvc.perform(multipart("/api/files/upload").file(file))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.fileId").value("stored-file-id"));

  verify(fileService).store(any(MultipartFile.class));
}
```

## Pagination

### Testing Paginated Responses

```java
@Test
void shouldReturnPaginatedUsers() throws Exception {
  Page<UserDto> page = new PageImpl<>(
    List.of(new UserDto(1L, "Alice"), new UserDto(2L, "Bob")),
    PageRequest.of(0, 10), 2);

  when(userService.getUsers(any(Pageable.class))).thenReturn(page);

  mockMvc.perform(get("/api/users")
      .param("page", "0")
      .param("size", "10"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.content").isArray())
    .andExpect(jsonPath("$.content.length()").value(2))
    .andExpect(jsonPath("$.totalElements").value(2))
    .andExpect(jsonPath("$.totalPages").value(1));
}
```

## Exception Handling

### Custom Exception Handlers

```java
@Test
void shouldHandleValidationException() throws Exception {
  when(userService.createUser(any()))
    .thenThrow(new MethodArgumentNotValidException(
      null, new BeanPropertyBindingResult(null, "user")));

  mockMvc.perform(post("/api/users")
      .contentType("application/json")
      .content("{\"invalid\":\"data\"}"))
    .andExpect(status().isBadRequest())
    .andExpect(jsonPath("$.errors").isArray());
}
```

## Testing Async Endpoints

```java
@Test
void shouldHandleAsyncResponses() throws Exception {
  CompletableFuture<UserDto> futureUser = CompletableFuture.completedFuture(
    new UserDto(1L, "Alice"));
  when(userService.getUserAsync(1L)).thenReturn(futureUser);

  MvcResult result = mockMvc.perform(get("/api/users/async/1"))
    .andExpect(status().isOk())
    .andReturn();

  // For actual async testing, use withAsyncDispatch()
  String content = result.getResponse().getContentAsString();
  assertThat(content).contains("Alice");
}
```
