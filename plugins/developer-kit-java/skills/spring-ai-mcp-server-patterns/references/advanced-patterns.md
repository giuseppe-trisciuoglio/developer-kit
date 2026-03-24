# Spring AI MCP Server — Advanced Patterns

Advanced implementation patterns for dynamic tools, multi-model support, caching, error handling, and security.

## Dynamic Tool Registration

Register tools at runtime based on external configuration or user requests:

```java
@Service
public class DynamicToolRegistry {

    private final McpServer mcpServer;
    private final Map<String, ToolRegistration> registeredTools = new ConcurrentHashMap<>();

    public void registerTool(ToolRegistration registration) {
        registeredTools.put(registration.getId(), registration);

        Tool tool = Tool.builder()
                .name(registration.getName())
                .description(registration.getDescription())
                .inputSchema(registration.getInputSchema())
                .function(args -> executeDynamicTool(registration.getId(), args))
                .build();

        mcpServer.addTool(tool);
    }

    public void unregisterTool(String toolId) {
        ToolRegistration registration = registeredTools.remove(toolId);
        if (registration != null) {
            mcpServer.removeTool(registration.getName());
        }
    }

    private Object executeDynamicTool(String toolId, Map<String, Object> args) {
        ToolRegistration registration = registeredTools.get(toolId);
        if (registration == null) throw new IllegalStateException("Tool not found: " + toolId);

        return switch (registration.getType()) {
            case GROOVY_SCRIPT -> executeGroovyScript(registration, args);
            case SPRING_BEAN -> executeSpringBeanMethod(registration, args);
            case HTTP_ENDPOINT -> callHttpEndpoint(registration, args);
        };
    }
}

@Data
@Builder
class ToolRegistration {
    private String id;
    private String name;
    private String description;
    private Map<String, Object> inputSchema;
    private ToolType type;
    private String target;
    private Map<String, String> metadata;
}

enum ToolType { GROOVY_SCRIPT, SPRING_BEAN, HTTP_ENDPOINT }
```

## Multi-Model Support

Configure and select between multiple AI models:

```java
@Configuration
public class MultiModelConfig {

    @Bean
    @Primary
    public ChatModel primaryChatModel(@Value("${spring.ai.primary.model}") String modelName) {
        return switch (modelName) {
            case "gpt-4" -> new OpenAiChatModel(OpenAiApi.builder()
                    .apiKey(System.getenv("OPENAI_API_KEY")).build());
            case "claude" -> new AnthropicChatModel(AnthropicApi.builder()
                    .apiKey(System.getenv("ANTHROPIC_API_KEY")).build());
            default -> throw new IllegalArgumentException("Unsupported model: " + modelName);
        };
    }

    @Bean
    public ModelSelector modelSelector(Map<String, ChatModel> models) {
        return new SpringAiModelSelector(models);
    }
}

@Component
public class SpringAiModelSelector implements ModelSelector {

    private final Map<String, ChatModel> models;

    @Override
    public ChatModel selectModel(Prompt prompt, Map<String, Object> context) {
        // Select based on complexity, cost, or latency constraints
        String modelName = determineBestModel(prompt, context);
        return models.get(modelName);
    }

    private String determineBestModel(Prompt prompt, Map<String, Object> context) {
        // Implement selection logic (prompt length, cost, latency)
        return "gpt-4";
    }
}
```

## Caching and Performance

```java
@Configuration
@EnableCaching
public class McpCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("tool-results", "prompt-templates");
    }
}

@Component
public class CachedToolExecutor {

    private final McpServer mcpServer;

    @Cacheable(
        value = "tool-results",
        key = "#toolName + '_' + #args.hashCode()",
        unless = "#result.isCacheable() == false"
    )
    public ToolResult executeTool(String toolName, Map<String, Object> args) {
        return mcpServer.executeTool(toolName, args);
    }

    @CacheEvict(value = "tool-results", allEntries = true)
    public void clearToolCache() { }

    @Cacheable(value = "prompt-templates", key = "#templateName")
    public PromptTemplate getPromptTemplate(String templateName) {
        return mcpServer.getPromptTemplate(templateName);
    }
}
```

## Secure Tool Execution

Full secure tool executor with Spring Security:

```java
@Component
public class SecureToolExecutor {

    private final McpServer mcpServer;

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
                .anyMatch(a -> a.getAuthority().equals("TOOL_" + toolName) ||
                               a.getAuthority().equals("ROLE_ADMIN"));
    }

    private void validateArguments(Map<String, Object> arguments) {
        arguments.forEach((key, value) -> {
            if (value instanceof String str && (str.contains(";") || str.contains("--"))) {
                throw new IllegalArgumentException("Invalid characters in argument: " + key);
            }
        });
    }
}
```

## Input Validation with Bean Validation

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
    @Size(max = 100)
    String name,

    @NotNull
    @Min(18) @Max(120)
    Integer age,

    @NotBlank @Email
    String email
) {}
```

## Error Handling

Consistent error handling via `@ControllerAdvice`:

```java
@ControllerAdvice
public class McpExceptionHandler {

    @ExceptionHandler(ToolExecutionException.class)
    public ResponseEntity<ErrorResponse> handleToolExecutionException(
            ToolExecutionException ex, WebRequest request) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ErrorResponse.builder()
                        .timestamp(LocalDateTime.now())
                        .status(500)
                        .error("Tool Execution Failed")
                        .message(ex.getMessage())
                        .build());
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDenied(AccessDeniedException ex) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(ErrorResponse.builder()
                        .timestamp(LocalDateTime.now())
                        .status(403)
                        .error("Access Denied")
                        .message("You do not have permission to execute this tool")
                        .build());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleValidation(IllegalArgumentException ex) {
        return ResponseEntity.badRequest()
                .body(ErrorResponse.builder()
                        .timestamp(LocalDateTime.now())
                        .status(400)
                        .error("Validation Error")
                        .message(ex.getMessage())
                        .build());
    }

    @Data
    @Builder
    static class ErrorResponse {
        private LocalDateTime timestamp;
        private int status;
        private String error;
        private String message;
    }
}
```

## Async Tool Execution

For long-running operations that should return immediately:

```java
@Tool(description = "Execute long-running task asynchronously")
public AsyncResult executeAsyncTask(
        @ToolParam("Task name") String taskName,
        @ToolParam(value = "Task parameters", required = false) String paramsJson) {

    String taskId = UUID.randomUUID().toString();

    CompletableFuture.supplyAsync(() -> performLongRunningTask(taskName, paramsJson), asyncExecutor)
            .thenAccept(result -> taskResults.put(taskId, result));

    return new AsyncResult(taskId, "pending", null);
}

@Tool(description = "Check status of an async task")
public AsyncResult getTaskStatus(@ToolParam("Task ID") String taskId) {
    Object result = taskResults.get(taskId);
    if (result == null) return new AsyncResult(taskId, "pending", null);
    return new AsyncResult(taskId, "completed", result);
}

record AsyncResult(String taskId, String status, Object result) {}
```

## Health Check

```java
@Component
public class McpHealthIndicator implements HealthIndicator {

    private final McpServer mcpServer;
    private final ToolRegistry toolRegistry;

    @Override
    public Health health() {
        try {
            Transport transport = mcpServer.getTransport();
            List<Tool> tools = toolRegistry.listTools();

            return Health.up()
                    .withDetail("transport", transport.getClass().getSimpleName())
                    .withDetail("connected", transport.isConnected())
                    .withDetail("tools.count", tools.size())
                    .build();
        } catch (Exception e) {
            return Health.down().withDetail("error", e.getMessage()).build();
        }
    }
}
```

## Micrometer Metrics

```java
@Component
public class McpMetrics {

    private final MeterRegistry meterRegistry;

    public void recordToolExecution(String toolName, long durationMs, boolean success) {
        meterRegistry.counter("mcp.tool.executions",
                "tool", toolName, "success", String.valueOf(success)).increment();
        meterRegistry.timer("mcp.tool.execution.time", "tool", toolName)
                .record(durationMs, TimeUnit.MILLISECONDS);
    }

    public void recordPromptRender(String templateName) {
        meterRegistry.counter("mcp.prompt.renders", "template", templateName).increment();
    }
}
```
