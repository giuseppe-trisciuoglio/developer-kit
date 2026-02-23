# Exception Handler Testing - Detailed Examples

## Testing Multiple Exception Types

### Handle Various Exception Types

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(ResourceNotFoundException.class)
  @ResponseStatus(HttpStatus.NOT_FOUND)
  public ErrorResponse handleResourceNotFound(ResourceNotFoundException ex) {
    return new ErrorResponse(404, "Not found", ex.getMessage());
  }

  @ExceptionHandler(DuplicateResourceException.class)
  @ResponseStatus(HttpStatus.CONFLICT)
  public ErrorResponse handleDuplicateResource(DuplicateResourceException ex) {
    return new ErrorResponse(409, "Conflict", ex.getMessage());
  }

  @ExceptionHandler(UnauthorizedException.class)
  @ResponseStatus(HttpStatus.UNAUTHORIZED)
  public ErrorResponse handleUnauthorized(UnauthorizedException ex) {
    return new ErrorResponse(401, "Unauthorized", ex.getMessage());
  }

  @ExceptionHandler(AccessDeniedException.class)
  @ResponseStatus(HttpStatus.FORBIDDEN)
  public ErrorResponse handleAccessDenied(AccessDeniedException ex) {
    return new ErrorResponse(403, "Forbidden", ex.getMessage());
  }

  @ExceptionHandler(Exception.class)
  @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
  public ErrorResponse handleGenericException(Exception ex) {
    return new ErrorResponse(500, "Internal server error", "An unexpected error occurred");
  }
}

class MultiExceptionHandlerTest {

  private MockMvc mockMvc;
  private GlobalExceptionHandler handler;

  @BeforeEach
  void setUp() {
    handler = new GlobalExceptionHandler();
    mockMvc = MockMvcBuilders
      .standaloneSetup(new TestController())
      .setControllerAdvice(handler)
      .build();
  }

  @Test
  void shouldReturn404ForNotFound() throws Exception {
    mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isNotFound())
      .andExpect(jsonPath("$.status").value(404));
  }

  @Test
  void shouldReturn409ForDuplicate() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"email\":\"existing@example.com\"}"))
      .andExpect(status().isConflict())
      .andExpect(jsonPath("$.status").value(409));
  }

  @Test
  void shouldReturn401ForUnauthorized() throws Exception {
    mockMvc.perform(get("/api/admin/dashboard"))
      .andExpect(status().isUnauthorized())
      .andExpect(jsonPath("$.status").value(401));
  }

  @Test
  void shouldReturn403ForAccessDenied() throws Exception {
    mockMvc.perform(get("/api/admin/users"))
      .andExpect(status().isForbidden())
      .andExpect(jsonPath("$.status").value(403));
  }

  @Test
  void shouldReturn500ForGenericException() throws Exception {
    mockMvc.perform(get("/api/error"))
      .andExpect(status().isInternalServerError())
      .andExpect(jsonPath("$.status").value(500));
  }
}
```

## Testing Error Response Structure

### Verify Error Response Format

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(BadRequestException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ResponseEntity<ErrorDetails> handleBadRequest(BadRequestException ex) {
    ErrorDetails details = new ErrorDetails(
      System.currentTimeMillis(),
      HttpStatus.BAD_REQUEST.value(),
      "Bad Request",
      ex.getMessage(),
      new Date()
    );
    return new ResponseEntity<>(details, HttpStatus.BAD_REQUEST);
  }
}

class ErrorResponseStructureTest {

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders
      .standaloneSetup(new TestController())
      .setControllerAdvice(new GlobalExceptionHandler())
      .build();
  }

  @Test
  void shouldIncludeTimestampInErrorResponse() throws Exception {
    mockMvc.perform(post("/api/data")
        .contentType("application/json")
        .content("{}"))
      .andExpect(status().isBadRequest())
      .andExpect(jsonPath("$.timestamp").exists())
      .andExpect(jsonPath("$.status").value(400))
      .andExpect(jsonPath("$.error").value("Bad Request"))
      .andExpect(jsonPath("$.message").exists())
      .andExpect(jsonPath("$.date").exists());
  }

  @Test
  void shouldIncludeAllRequiredErrorFields() throws Exception {
    MvcResult result = mockMvc.perform(get("/api/invalid"))
      .andExpect(status().isBadRequest())
      .andReturn();

    String response = result.getResponse().getContentAsString();

    assertThat(response).contains("timestamp");
    assertThat(response).contains("status");
    assertThat(response).contains("error");
    assertThat(response).contains("message");
  }
}
```

## Testing Validation Error Handling

### Handle MethodArgumentNotValidException

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(MethodArgumentNotValidException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ValidationErrorResponse handleValidationException(
    MethodArgumentNotValidException ex) {

    Map<String, String> errors = new HashMap<>();
    ex.getBindingResult().getFieldErrors().forEach(error ->
      errors.put(error.getField(), error.getDefaultMessage())
    );

    return new ValidationErrorResponse(
      HttpStatus.BAD_REQUEST.value(),
      "Validation failed",
      errors
    );
  }
}

class ValidationExceptionHandlerTest {

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders
      .standaloneSetup(new UserController())
      .setControllerAdvice(new GlobalExceptionHandler())
      .build();
  }

  @Test
  void shouldReturnValidationErrorsForInvalidInput() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"name\":\"\",\"age\":-5}"))
      .andExpect(status().isBadRequest())
      .andExpect(jsonPath("$.status").value(400))
      .andExpect(jsonPath("$.errors.name").exists())
      .andExpect(jsonPath("$.errors.age").exists());
  }

  @Test
  void shouldIncludeErrorMessageForEachField() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"name\":\"\",\"email\":\"invalid\"}"))
      .andExpect(status().isBadRequest())
      .andExpect(jsonPath("$.errors.name").value("must not be blank"))
      .andExpect(jsonPath("$.errors.email").value("must be valid email"));
  }
}
```

## Testing Exception Handler with Custom Logic

### Exception Handler with Context

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  private final MessageService messageService;
  private final LoggingService loggingService;

  public GlobalExceptionHandler(MessageService messageService, LoggingService loggingService) {
    this.messageService = messageService;
    this.loggingService = loggingService;
  }

  @ExceptionHandler(BusinessException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ErrorResponse handleBusinessException(BusinessException ex, HttpServletRequest request) {
    loggingService.logException(ex, request.getRequestURI());

    String localizedMessage = messageService.getMessage(ex.getErrorCode());
    return new ErrorResponse(
      HttpStatus.BAD_REQUEST.value(),
      "Business error",
      localizedMessage
    );
  }
}

class ExceptionHandlerWithContextTest {

  private MockMvc mockMvc;
  private GlobalExceptionHandler handler;
  private MessageService messageService;
  private LoggingService loggingService;

  @BeforeEach
  void setUp() {
    messageService = mock(MessageService.class);
    loggingService = mock(LoggingService.class);
    handler = new GlobalExceptionHandler(messageService, loggingService);

    mockMvc = MockMvcBuilders
      .standaloneSetup(new TestController())
      .setControllerAdvice(handler)
      .build();
  }

  @Test
  void shouldLocalizeErrorMessage() throws Exception {
    when(messageService.getMessage("USER_NOT_FOUND"))
      .thenReturn("L'utilisateur n'a pas été trouvé");

    mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isBadRequest())
      .andExpect(jsonPath("$.message").value("L'utilisateur n'a pas été trouvé"));

    verify(messageService).getMessage("USER_NOT_FOUND");
  }

  @Test
  void shouldLogExceptionOccurrence() throws Exception {
    mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isBadRequest());

    verify(loggingService).logException(any(BusinessException.class), anyString());
  }
}
```
