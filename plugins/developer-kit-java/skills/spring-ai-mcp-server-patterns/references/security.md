# Spring AI MCP Server - Security Patterns

## Tool Security

Implement secure tool execution with Spring Security:

```java
@Component
public class SecureToolExecutor {

    private final McpServer mcpServer;

    public SecureToolExecutor(McpServer mcpServer) {
        this.mcpServer = mcpServer;
    }

    public ToolResult executeTool(String toolName, Map<String, Object> arguments) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        if (!(auth instanceof UserAuthentication userAuth)) {
            throw new AccessDeniedException("User not authenticated");
        }

        if (!hasToolPermission(userAuth.getUser(), toolName)) {
            throw new AccessDeniedException("Tool not allowed: " + toolName);
        }

        validateArguments(arguments);
        logToolExecution(userAuth.getUser(), toolName, arguments);

        try {
            ToolResult result = mcpServer.executeTool(toolName, arguments);
            logToolSuccess(userAuth.getUser(), toolName);
            return result;
        } catch (Exception e) {
            logToolFailure(userAuth.getUser(), toolName, e);
            throw new ToolExecutionException("Tool execution failed", e);
        }
    }

    private boolean hasToolPermission(User user, String toolName) {
        return user.getAuthorities().stream()
                .anyMatch(auth -> auth.getAuthority().equals("TOOL_" + toolName) ||
                                 auth.getAuthority().equals("ROLE_ADMIN"));
    }

    private void validateArguments(Map<String, Object> arguments) {
        arguments.forEach((key, value) -> {
            if (value instanceof String str) {
                if (str.contains(";") || str.contains("--")) {
                    throw new IllegalArgumentException("Invalid characters in argument: " + key);
                }
            }
        });
    }
}
```

## Input Validation

Use Spring's validation framework:

```java
@Component
public class ValidatedTools {

    @Tool(description = "Process user data with validation")
    @Validated
    public ProcessingResult processUserData(
            @ToolParam("User data to process") @Valid UserData data) {
        return new ProcessingResult("success", data);
    }
}

record UserData(
    @NotBlank(message = "Name is required")
    @Size(max = 100, message = "Name must be 100 characters or less")
    String name,

    @NotNull(message = "Age is required")
    @Min(value = 18, message = "Must be 18 or older")
    @Max(value = 120, message = "Age must be realistic")
    Integer age,

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    String email
) {}

@Component
public class SensitiveOperationValidator {

    public void validateOperation(String operation, User user, Map<String, Object> params) {
        if (isSensitiveOperation(operation)) {
            requireAdditionalAuthentication(user);
            validateOperationLimits(user, operation);
            logSensitiveOperation(user, operation, params);
        }
    }

    private boolean isSensitiveOperation(String operation) {
        return operation.startsWith("delete") || operation.startsWith("update");
    }
}
```

## Error Handling

```java
@ControllerAdvice
public class McpExceptionHandler {

    @ExceptionHandler(ToolExecutionException.class)
    public ResponseEntity<ErrorResponse> handleToolExecutionException(
            ToolExecutionException ex, WebRequest request) {
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .error("Tool Execution Failed")
                .message(ex.getMessage())
                .path(((ServletWebRequest) request).getRequest().getRequestURI())
                .build();
        log.error("Tool execution failed: {}", ex.getMessage(), ex);
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(
            AccessDeniedException ex, WebRequest request) {
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.FORBIDDEN.value())
                .error("Access Denied")
                .message("You do not have permission to execute this tool")
                .path(((ServletWebRequest) request).getRequest().getRequestURI())
                .build();
        return new ResponseEntity<>(error, HttpStatus.FORBIDDEN);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleValidationError(
            IllegalArgumentException ex, WebRequest request) {
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error("Validation Error")
                .message(ex.getMessage())
                .path(((ServletWebRequest) request).getRequest().getRequestURI())
                .build();
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    @Data
    @Builder
    static class ErrorResponse {
        private LocalDateTime timestamp;
        private int status;
        private String error;
        private String message;
        private String path;
    }
}
```
