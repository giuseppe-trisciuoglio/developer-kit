# Exception Handler Test Examples

## Handler with Dependencies (using mocks)

When your `@ControllerAdvice` has dependencies injected via constructor, mock them in your test:

```java
@ControllerAdvice
public class GlobalExceptionHandler {
  private final MessageService messageService;

  public GlobalExceptionHandler(MessageService messageService) {
    this.messageService = messageService;
  }

  @ExceptionHandler(BusinessException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ErrorResponse handleBusiness(BusinessException ex) {
    return new ErrorResponse(400, "Business Error", messageService.getMessage(ex.getErrorCode()));
  }
}

class HandlerWithDepsTest {
  private MockMvc mockMvc;
  private MessageService messageService = mock(MessageService.class);

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders.standaloneSetup(new TestController())
        .setControllerAdvice(new GlobalExceptionHandler(messageService))
        .build();
  }

  @Test
  void shouldReturnLocalizedMessage() throws Exception {
    when(messageService.getMessage("USER_NOT_FOUND")).thenReturn("Utente non trovato");
    mockMvc.perform(get("/api/users/999"))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.message").value("Utente non trovato"));
    verify(messageService).getMessage("USER_NOT_FOUND");
  }
}
```

## Testing with Spring Security Context

When your exception handler evaluates `SecurityContextHolder`:

```java
@ExceptionHandler(AuthorizationException.class)
@ResponseStatus(HttpStatus.FORBIDDEN)
public ErrorResponse handleAuth(AuthorizationException ex) {
  Authentication auth = SecurityContextHolder.getContext().getAuthentication();
  return new ErrorResponse(403, "Forbidden", "Access denied for: " + auth.getName());
}

@Test
void shouldReturn403WhenNotAuthorized() throws Exception {
  SecurityContextHolder.getContext().setAuthentication(
      new UsernamePasswordAuthenticationToken("user", null, List.of())
  );
  mockMvc.perform(get("/api/admin"))
      .andExpect(status().isForbidden())
      .andExpect(jsonPath("$.message").value("Access denied for: user"));
}
```

## Testing with MessageSource (Localization)

```java
@ControllerAdvice
public class I18nExceptionHandler {
  private final MessageSource messageSource;

  public I18nExceptionHandler(MessageSource messageSource) {
    this.messageSource = messageSource;
  }

  @ExceptionHandler(ResourceNotFoundException.class)
  @ResponseStatus(HttpStatus.NOT_FOUND)
  public ErrorResponse handleNotFound(ResourceNotFoundException ex, Locale locale) {
    String message = messageSource.getMessage(ex.getMessage(), null, locale);
    return new ErrorResponse(404, "Not Found", message);
  }
}

@Test
void shouldReturnLocalizedMessageItalian() throws Exception {
  // Inject MessageSource into MockMvc
  mockMvc = MockMvcBuilders.standaloneSetup(new TestController())
      .setControllerAdvice(new I18nExceptionHandler(messageSource))
      .setLocaleResolver(() -> Locale.ITALIAN)
      .build();

  mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isNotFound())
      .andExpect(jsonPath("$.message").value("Utente non trovato"));
}
```
