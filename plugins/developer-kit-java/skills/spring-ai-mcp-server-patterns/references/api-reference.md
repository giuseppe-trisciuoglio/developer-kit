# Spring AI MCP Server API Reference

Complete API documentation for Spring AI MCP server implementations.

## Table of Contents

1. [Core Annotations](#core-annotations)
2. [Functional Interfaces](#functional-interfaces)
3. [Configuration Classes](#configuration-classes)
4. [Transport Implementations](#transport-implementations)
5. [Security Interfaces](#security-interfaces)
6. [Utility Classes](#utility-classes)
7. [Property Bindings](#property-bindings)
8. [Event System](#event-system)

## Core Annotations

### @Tool

Marks a method as an MCP tool that can be invoked by AI models.

**Target**: Method
**Retention**: Runtime

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Tool {
    /**
     * Description of what this tool does.
     * Used by AI models to understand when to invoke the tool.
     */
    String description() default "";

    /**
     * Whether this tool requires confirmation before execution.
     */
    boolean requiresConfirmation() default false;

    /**
     * Maximum execution time in milliseconds.
     */
    long maxExecutionTime() default 30000;

    /**
     * Whether execution time should be monitored.
     */
    boolean monitorExecution() default true;
}
```

**Example**:
```java
@Tool(
    description = "Get current weather for a city",
    requiresConfirmation = false,
    maxExecutionTime = 5000
)
public WeatherData getWeather(@ToolParam("City name") String city) {
    // Implementation
}
```

### @ToolParam

Documents a parameter for tool methods.

**Target**: Parameter
**Retention**: Runtime

```java
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface ToolParam {
    /**
     * Description of the parameter purpose.
     */
    String value() default "";

    /**
     * Whether this parameter is required.
     */
    boolean required() default true;

    /**
     * Example value for documentation.
     */
    String example() default "";

    /**
     * Default value if not provided.
     */
    String defaultValue() default "";
}
```

### @PromptTemplate

Marks a method as a prompt template provider.

**Target**: Method
**Retention**: Runtime

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface PromptTemplate {
    /**
     * Unique name of the prompt template.
     */
    String name() default "";

    /**
     * Description of when to use this template.
     */
    String description() default "";

    /**
     * The template string with placeholders.
     * Use {placeholder} syntax for parameters.
     */
    String template() default "";

    /**
     * Model to use for this prompt.
     */
    String model() default "";

    /**
     * Temperature for model generation.
     */
    double temperature() default 0.7;
}
```

**Example**:
```java
@PromptTemplate(
    name = "code-review-java",
    description = "Review Java code for best practices",
    template = """
        Review the following Java code:
        ```java
        {code}
        ```
        Focus on: {focusAreas}
        """,
    temperature = 0.3
)
public Prompt createCodeReviewPrompt(@PromptParam("code") String code) {
    // Return populated prompt
}
```

### @PromptParam

Documents a parameter for prompt template methods.

**Target**: Parameter
**Retention**: Runtime

```java
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface PromptParam {
    /**
     * Name of the parameter in the template.
     */
    String value();

    /**
     * Description of the parameter.
     */
    String description() default "";

    /**
     * Whether this parameter is required.
     */
    boolean required() default true;

    /**
     * Example value.
     */
    String example() default "";
}
```

### @EnableMcpServer

Enables MCP server auto-configuration.

**Target**: Type
**Retention**: Runtime

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Import(McpServerAutoConfiguration.class)
public @interface EnableMcpServer {
    /**
     * Base packages to scan for tools and prompts.
     */
    String[] basePackages() default {};

    /**
     * Whether to enable automatic tool discovery.
     */
    boolean autoDiscovery() default true;

    /**
     * Configuration class to use.
     */
    Class<?>[] configuration() default {};
}
```

## Functional Interfaces

### ToolExecutor

Functional interface for tool execution.

```java
@FunctionalInterface
public interface ToolExecutor {
    /**
     * Execute a tool with the given arguments.
     *
     * @param toolName Name of the tool to execute
     * @param arguments Arguments as a map
     * @return Execution result
     * @throws ToolExecutionException if execution fails
     */
    ToolResult execute(String toolName, Map<String, Object> arguments)
            throws ToolExecutionException;
}
```

### ToolFilter

Filter for tool execution.

```java
@FunctionalInterface
public interface ToolFilter {
    /**
     * Determine if a tool should be allowed to execute.
     *
     * @param tool The tool being requested
     * @param context Execution context
     * @return true if tool should be allowed
     */
    boolean isAllowed(Tool tool, ToolExecutionContext context);
}
```

**Default Implementation**:
```java
public class DefaultToolFilter implements ToolFilter {
    @Override
    public boolean isAllowed(Tool tool, ToolExecutionContext context) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        // Admin tools require admin role
        if (tool.getName().startsWith("admin_")) {
            return auth != null && auth.getAuthorities().stream()
                    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        }

        return true;
    }
}
```

### PromptRenderer

Renders prompt templates with parameters.

```java
@FunctionalInterface
public interface PromptRenderer {
    /**
     * Render a prompt template with parameters.
     *
     * @param template The prompt template
     * @param parameters Parameters to substitute
     * @return Rendered prompt
     */
    Prompt render(PromptTemplate template, Map<String, Object> parameters);
}
```

## Configuration Classes

### McpServerAutoConfiguration

Auto-configuration for MCP servers.

```java
@Configuration
@AutoConfigureAfter({WebMvcAutoConfiguration.class})
@ConditionalOnClass({McpServer.class})
@ConditionalOnProperty(name = "spring.ai.mcp.enabled", havingValue = "true", matchIfMissing = true)
public class McpServerAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public McpServerProperties mcpProperties() {
        return new McpServerProperties();
    }

    @Bean
    @ConditionalOnMissingBean
    public McpServer mcpServer(
            McpServerProperties properties,
            ObjectProvider<List<Tool>> tools,
            ObjectProvider<List<PromptTemplate>> prompts
    ) {
        McpServer.Builder builder = McpServer.builder()
                .serverInfo(properties.getServer().getName(), properties.getServer().getVersion())
                .transport(createTransport(properties.getTransport()));

        tools.ifAvailable(toolList -> toolList.forEach(builder::tool));
        prompts.ifAvailable(promptList -> promptList.forEach(builder::prompt));

        return builder.build();
    }

    private Transport createTransport(TransportConfig config) {
        // Create transport based on configuration
        return switch (config.getType()) {
            case STDIO -> new StdioTransport();
            case HTTP -> new HttpTransport(config.getHttp().getPort());
            case SSE -> new SseTransport(config.getHttp().getPort(), config.getHttp().getPath());
        };
    }

    @Bean
    @ConditionalOnMissingBean
    public ToolRegistry toolRegistry(ApplicationContext context) {
        ToolRegistry registry = new ToolRegistry();

        Map<String, Object> toolBeans = context.getBeansWithAnnotation(Component.class);
        toolBeans.values().forEach(bean -> {
            Method[] methods = bean.getClass().getMethods();
            for (Method method : methods) {
                if (method.isAnnotationPresent(Tool.class)) {
                    registry.register(Tool.fromMethod(method, bean));
                }
            }
        });

        return registry;
    }
}
```

### McpServerProperties

Configuration properties for MCP server.

```java
@ConfigurationProperties(prefix = "spring.ai.mcp")
public class McpServerProperties {
    private ServerProperties server = new ServerProperties();
    private TransportProperties transport = new TransportProperties();
    private SecurityProperties security = new SecurityProperties();
    private ToolsProperties tools = new ToolsProperties();
    private PromptsProperties prompts = new PromptsProperties();
    private LoggingProperties logging = new LoggingProperties();
    private MetricsProperties metrics = new MetricsProperties();

    @Data
    public static class ServerProperties {
        private String name = "spring-ai-mcp-server";
        private String version = "1.0.0";
        private String description = "Spring AI MCP Server";
    }

    @Data
    public static class TransportProperties {
        private TransportType type = TransportType.STDIO;
        private HttpProperties http = new HttpProperties();

        @Data
        public static class HttpProperties {
            private int port = 8080;
            private String path = "/mcp";
            private CorsProperties cors = new CorsProperties();

            @Data
            public static class CorsProperties {
                private boolean enabled = true;
                private List<String> allowedOrigins = List.of("*");
                private List<String> allowedMethods = List.of("GET", "POST");
                private List<String> allowedHeaders = List.of("*");
            }
        }
    }

    @Data
    public static class SecurityProperties {
        private boolean enabled = false;
        private AuthorizationProperties authorization = new AuthorizationProperties();
        private AuditProperties audit = new AuditProperties();

        @Data
        public static class AuthorizationProperties {
            private AuthorizationMode mode = AuthorizationMode.ROLE_BASED;
            private boolean defaultDeny = true;
            private List<String> allowedTools = List.of();
            private List<String> adminTools = List.of("admin_*");
        }

        @Data
        public static class AuditProperties {
            private boolean enabled = true;
            private List<String> auditedOperations = List.of("*");
        }

        public enum AuthorizationMode {
            NONE, ROLE_BASED, PERMISSION_BASED, ATTRIBUTE_BASED
        }
    }

    @Data
    public static class ToolsProperties {
        private String packageScan = "com.example.mcp.tools";
        private ValidationProperties validation = new ValidationProperties();
        private CachingProperties caching = new CachingProperties();

        @Data
        public static class ValidationProperties {
            private boolean enabled = true;
            private Duration maxExecutionTime = Duration.ofSeconds(30);
            private int maxArgumentsSize = 1000000; // 1MB
        }

        @Data
        public static class CachingProperties {
            private boolean enabled = true;
            private Duration ttl = Duration.ofMinutes(5);
            private int maxSize = 100;
        }
    }

    @Data
    public static class PromptsProperties {
        private String packageScan = "com.example.mcp.prompts";
        private CachingProperties caching = new CachingProperties();

        @Data
        public static class CachingProperties {
            private boolean enabled = true;
            private Duration ttl = Duration.ofHours(1);
            private int maxSize = 1000;
        }
    }

    // Additional nested properties...
}
```

## Transport Implementations

### Transport Interface

```java
public interface Transport {
    /**
     * Start the transport.
     */
    void start() throws IOException;

    /**
     * Stop the transport.
     */
    void stop() throws IOException;

    /**
     * Send a message.
     *
     * @param message The message to send
     */
    void send(Message message) throws IOException;

    /**
     * Receive a message.
     *
     * @return The received message
     */
    Message receive() throws IOException;

    /**
     * Check if transport is connected.
     */
    boolean isConnected();
}
```

### StdioTransport

Standard input/output transport for local process communication.

```java
public class StdioTransport implements Transport {
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
    private final PrintWriter writer = new PrintWriter(System.out, true);
    private volatile boolean running = false;

    @Override
    public void start() throws IOException {
        running = true;
        log.info("STDIO transport started");
    }

    @Override
    public void stop() throws IOException {
        running = false;
        reader.close();
        writer.close();
        log.info("STDIO transport stopped");
    }

    @Override
    public void send(Message message) throws IOException {
        String json = objectMapper.writeValueAsString(message);
        writer.println(json);
        writer.flush();
    }

    @Override
    public Message receive() throws IOException {
        String line = reader.readLine();
        if (line == null) {
            throw new EOFException("End of stream");
        }
        return objectMapper.readValue(line, Message.class);
    }

    @Override
    public boolean isConnected() {
        return running;
    }
}
```

### HttpTransport

HTTP transport for remote communication.

```java
public class HttpTransport implements Transport {
    private final int port;
    private final String path;
    private final HttpServer server;
    private final List<Consumer<Message>> messageHandlers = new CopyOnWriteArrayList<>();
    private volatile boolean running = false;

    public HttpTransport(int port, String path) throws IOException {
        this.port = port;
        this.path = path;
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
    }

    @Override
    public void start() throws IOException {
        server.createContext(path, exchange -> {
            if ("POST".equals(exchange.getRequestMethod())) {
                String requestBody = new String(exchange.getRequestBody().readAllBytes());
                Message message = objectMapper.readValue(requestBody, Message.class);

                messageHandlers.forEach(handler -> handler.accept(message));

                String response = "{\"status\":\"acknowledged\"}";
                exchange.sendResponseHeaders(200, response.getBytes().length);
                exchange.getResponseBody().write(response.getBytes());
            }
            exchange.close();
        });

        server.start();
        running = true;
        log.info("HTTP transport started on port {} path {}", port, path);
    }

    @Override
    public void stop() throws IOException {
        server.stop(0);
        running = false;
        log.info("HTTP transport stopped");
    }

    @Override
    public void send(Message message) throws IOException {
        // HTTP transport is request-response based
        throw new UnsupportedOperationException("Use HTTP client for sending");
    }

    @Override
    public Message receive() throws IOException {
        // HTTP transport receives via POST requests
        throw new UnsupportedOperationException("HTTP transport is async");
    }

    public void addMessageHandler(Consumer<Message> handler) {
        messageHandlers.add(handler);
    }

    @Override
    public boolean isConnected() {
        return running;
    }
}
```

### SseTransport

Server-Sent Events transport for real-time communication.

```java
public class SseTransport implements Transport {
    private final int port;
    private final String path;
    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final HttpServer server;
    private volatile boolean running = false;

    public SseTransport(int port, String path) throws IOException {
        this.port = port;
        this.path = path;
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
    }

    @Override
    public void start() throws IOException {
        // SSE endpoint for receiving messages
        server.createContext(path + "/sse", exchange -> {
            if ("GET".equals(exchange.getRequestMethod())) {
                handleSseConnection(exchange);
            }
        });

        // POST endpoint for sending messages
        server.createContext(path, exchange -> {
            if ("POST".equals(exchange.getRequestMethod())) {
                handleMessage(exchange);
            }
        });

        server.start();
        running = true;
        log.info("SSE transport started on port {} path {}", port, path);
    }

    private void handleSseConnection(HttpExchange exchange) throws IOException {
        Headers headers = exchange.getResponseHeaders();
        headers.add("Content-Type", "text/event-stream");
        headers.add("Cache-Control", "no-cache");
        headers.add("Connection", "keep-alive");

        exchange.sendResponseHeaders(200, 0);

        // Keep connection open
        OutputStream os = exchange.getResponseBody();
        emitters.add(new SseEmitter(os, exchange));
    }

    private void handleMessage(HttpExchange exchange) throws IOException {
        String requestBody = new String(exchange.getRequestBody().readAllBytes());
        Message message = objectMapper.readValue(requestBody, Message.class);

        // Send to all SSE clients
        broadcast(message);

        String response = "{\"status\":\"broadcasted\"}";
        exchange.sendResponseHeaders(200, response.getBytes().length);
        exchange.getResponseBody().write(response.getBytes());
        exchange.close();
    }

    private void broadcast(Message message) {
        String data = "data: " + toJson(message) + "\n\n";
        emitters.removeIf(emitter -> !emitter.send(data));
    }

    @Override
    public void send(Message message) throws IOException {
        broadcast(message);
    }

    @Override
    public Message receive() throws IOException {
        // SSE transport is async, use event-driven approach
        throw new UnsupportedOperationException("SSE transport is async");
    }

    // Additional methods...
}
```

## Security Interfaces

### ToolValidator

Validates tool arguments and execution context.

```java
public interface ToolValidator {
    /**
     * Validate tool arguments before execution.
     *
     * @param tool The tool being executed
     * @param arguments The provided arguments
     * @throws ValidationException if validation fails
     */
    void validateArguments(Tool tool, Map<String, Object> arguments)
            throws ValidationException;

    /**
     * Validate execution context.
     *
     * @param tool The tool being executed
     * @param context The execution context
     * @throws ValidationException if validation fails
     */
    void validateContext(Tool tool, ToolExecutionContext context)
            throws ValidationException;
}
```

**Implementation Example**:
```java
@Component
public class DefaultToolValidator implements ToolValidator {

    private final McpServerProperties properties;

    @Override
    public void validateArguments(Tool tool, Map<String, Object> arguments)
            throws ValidationException {

        // Check argument size
        int size = arguments.toString().getBytes().length;
        if (size > properties.getTools().getValidation().getMaxArgumentsSize()) {
            throw new ValidationException("Arguments too large: " + size + " bytes");
        }

        // Validate based on tool parameter annotations
        Arrays.stream(tool.getMethod().getParameters())
                .filter(param -> param.isAnnotationPresent(ToolParam.class))
                .forEach(param -> validateParameter(param, arguments));
    }

    private void validateParameter(Parameter param, Map<String, Object> arguments) {
        ToolParam annotation = param.getAnnotation(ToolParam.class);
        String paramName = param.getName();

        if (annotation.required() && !arguments.containsKey(paramName)) {
            throw new ValidationException("Required parameter missing: " + paramName);
        }

        Object value = arguments.get(paramName);
        if (value != null) {
            validateParameterType(param.getType(), value, paramName);
            validateParameterContent(value, paramName);
        }
    }

    private void validateParameterType(Class<?> expectedType, Object value, String paramName) {
        if (!expectedType.isAssignableFrom(value.getClass())) {
            throw new ValidationException(
                    String.format("Parameter %s: expected %s, got %s",
                            paramName, expectedType.getSimpleName(), value.getClass().getSimpleName()));
        }
    }

    private void validateParameterContent(Object value, String paramName) {
        if (value instanceof String str) {
            // Check for injection patterns
            if (str.contains(";") || str.contains("&") || str.contains("|")) {
                throw new ValidationException("Invalid characters in parameter: " + paramName);
            }
        }
    }

    @Override
    public void validateContext(Tool tool, ToolExecutionContext context)
            throws ValidationException {

        // Check authentication if required
        if (tool.requiresAuthentication() && !context.isAuthenticated()) {
            throw new ValidationException("Authentication required for tool: " + tool.getName());
        }

        // Check rate limits
        if (exceedsRateLimit(context.getUser(), tool)) {
            throw new ValidationException("Rate limit exceeded for tool: " + tool.getName());
        }
    }

    private boolean exceedsRateLimit(User user, Tool tool) {
        // Implement rate limiting logic
        return false;
    }
}
```

### SecurityContext

Provides security context for tool execution.

```java
public interface SecurityContext {
    /**
     * Get the current authentication.
     */
    Optional<Authentication> getAuthentication();

    /**
     * Check if current user has permission.
     */
    boolean hasPermission(String permission);

    /**
     * Check if current user has any of the given roles.
     */
    boolean hasAnyRole(String... roles);

    /**
     * Get user details if authenticated.
     */
    Optional<UserDetails> getUserDetails();

    /**
     * Validate MFA token if required.
     */
    boolean validateMfaToken(String token);
}
```

## Utility Classes

### ToolRegistry

Manages tool registration and lookup.

```java
@Component
public class ToolRegistry {
    private final Map<String, Tool> tools = new ConcurrentHashMap<>();
    private final List<ToolRegistrationListener> listeners = new CopyOnWriteArrayList<>();

    /**
     * Register a tool.
     */
    public void register(Tool tool) {
        tools.put(tool.getName(), tool);
        notifyListeners(tool, ToolEvent.Type.REGISTERED);
    }

    /**
     * Unregister a tool.
     */
    public void unregister(String toolName) {
        Tool removed = tools.remove(toolName);
        if (removed != null) {
            notifyListeners(removed, ToolEvent.Type.UNREGISTERED);
        }
    }

    /**
     * Get a tool by name.
     */
    public Optional<Tool> getTool(String name) {
        return Optional.ofNullable(tools.get(name));
    }

    /**
     * List all tools.
     */
    public List<Tool> listTools() {
        return List.copyOf(tools.values());
    }

    /**
     * Add registration listener.
     */
    public void addListener(ToolRegistrationListener listener) {
        listeners.add(listener);
    }

    private void notifyListeners(Tool tool, ToolEvent.Type type) {
        ToolEvent event = new ToolEvent(tool, type);
        listeners.forEach(listener -> listener.onToolEvent(event));
    }
}
```

### McpMessage

Represents MCP protocol messages.

```java
public final class McpMessage {
    private final String jsonrpc = "2.0";
    private final String id;
    private final String method;
    private final Map<String, Object> params;
    private final Object result;
    private final McpError error;

    private McpMessage(Builder builder) {
        this.id = builder.id;
        this.method = builder.method;
        this.params = builder.params;
        this.result = builder.result;
        this.error = builder.error;
    }

    public static class Builder {
        private String id;
        private String method;
        private Map<String, Object> params;
        private Object result;
        private McpError error;

        public Builder id(String id) {
            this.id = id;
            return this;
        }

        public Builder method(String method) {
            this.method = method;
            return this;
        }

        public Builder params(Map<String, Object> params) {
            this.params = params;
            return this;
        }

        public Builder result(Object result) {
            this.result = result;
            return this;
        }

        public Builder error(McpError error) {
            this.error = error;
            return this;
        }

        public McpMessage build() {
            return new McpMessage(this);
        }
    }

    // Getters and utility methods...
}
```

### McpError

Represents errors in MCP communication.

```java
public class McpError {
    private final int code;
    private final String message;
    private final Map<String, Object> data;

    // Error codes
    public static final int PARSE_ERROR = -32700;
    public static final int INVALID_REQUEST = -32600;
    public static final int METHOD_NOT_FOUND = -32601;
    public static final int INVALID_PARAMS = -32602;
    public static final int INTERNAL_ERROR = -32603;

    public McpError(int code, String message) {
        this.code = code;
        this.message = message;
        this.data = null;
    }

    public McpError(int code, String message, Map<String, Object> data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    // Static factory methods...
}
```

## Property Bindings

### spring.ai.mcp.*

Main configuration properties.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `spring.ai.mcp.enabled` | boolean | true | Enable MCP server |
| `spring.ai.mcp.server.name` | string | spring-ai-mcp-server | Server name |
| `spring.ai.mcp.server.version` | string | 1.0.0 | Server version |
| `spring.ai.mcp.transport.type` | enum | stdio | Transport type (stdio, http, sse) |
| `spring.ai.mcp.transport.http.port` | int | 8080 | HTTP port |
| `spring.ai.mcp.transport.http.path` | string | /mcp | HTTP path |
| `spring.ai.mcp.security.enabled` | boolean | false | Enable security |
| `spring.ai.mcp.security.authorization.mode` | enum | role-based | Authorization mode |
| `spring.ai.mcp.security.audit.enabled` | boolean | true | Enable auditing |
| `spring.ai.mcp.tools.package-scan` | string | com.example.mcp.tools | Package to scan for tools |
| `spring.ai.mcp.prompts.package-scan` | string | com.example.mcp.prompts | Package to scan for prompts |

### Rate Limiting Properties

```yaml
spring:
  ai:
    mcp:
      rate-limiting:
        enabled: true
        requests-per-minute: 100
        burst-capacity: 150
        limit-by: user  # user, ip, global
        redis:
          enabled: true
          host: localhost
          port: 6379
```

### Threading Properties

```yaml
spring:
  ai:
    mcp:
      threading:
        executor:
          core-pool-size: 10
          max-pool-size: 50
          queue-capacity: 100
          keep-alive-time: 60s
          thread-name-prefix: mcp-
      timeout:
        default: 30s
        per-tool:
          long-running-tool: 5m
          admin-tool: 1m
```

## Event System

### McpEvent

Base class for MCP events.

```java
public abstract class McpEvent extends ApplicationEvent {
    private final Instant timestamp;
    private final String source;

    protected McpEvent(Object source, String eventSource) {
        super(source);
        this.timestamp = Instant.now();
        this.source = eventSource;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public String getSource() {
        return source;
    }
}
```

### ToolEvent

Events related to tool lifecycle.

```java
public class ToolEvent extends McpEvent {
    public enum Type {
        REGISTERED,
        UNREGISTERED,
        EXECUTED,
        FAILED,
        TIMEOUT
    }

    private final Type type;
    private final Tool tool;
    private final Map<String, Object> metadata;

    public ToolEvent(Tool tool, Type type) {
        this(tool, type, Map.of());
    }

    public ToolEvent(Tool tool, Type type, Map<String, Object> metadata) {
        super(tool, "tool-registry");
        this.type = type;
        this.tool = tool;
        this.metadata = metadata;
    }

    // Getters...
}
```

### PromptEvent

Events related to prompt operations.

```java
public class PromptEvent extends McpEvent {
    public enum Type {
        RENDERED,
        CACHED,
        FAILED
    }

    private final Type type;
    private final PromptTemplate template;
    private final Map<String, Object> parameters;

    public PromptEvent(PromptTemplate template, Type type, Map<String, Object> parameters) {
        super(template, "prompt-renderer");
        this.type = type;
        this.template = template;
        this.parameters = parameters;
    }

    // Getters...
}
```

### Event Listeners

```java
@Component
public class McpEventListener implements ApplicationListener<McpEvent> {

    private final MetricsService metricsService;
    private final AuditService auditService;

    @Override
    public void onApplicationEvent(McpEvent event) {
        switch (event) {
            case ToolEvent toolEvent -> handleToolEvent(toolEvent);
            case PromptEvent promptEvent -> handlePromptEvent(promptEvent);
            default -> log.debug("Unhandled event: {}", event.getClass());
        }
    }

    private void handleToolEvent(ToolEvent event) {
        metricsService.recordToolEvent(
                event.getTool().getName(),
                event.getType(),
                event.getTimestamp()
        );

        if (event.getType() == ToolEvent.Type.FAILED) {
            auditService.logToolFailure(
                    event.getTool(),
                    event.getMetadata()
            );
        }
    }

    private void handlePromptEvent(PromptEvent event) {
        if (event.getType() == PromptEvent.Type.CACHED) {
            metricsService.incrementPromptCacheHit();
        }
    }
}
```

## Async Execution

### AsyncToolExecutor

Asynchronous tool execution support.

```java
public class AsyncToolExecutor {
    private final ExecutorService executor;
    private final ToolExecutor delegate;

    public AsyncToolExecutor(ToolExecutor delegate, ExecutorService executor) {
        this.delegate = delegate;
        this.executor = executor;
    }

    public CompletableFuture<ToolResult> executeAsync(
            String toolName,
            Map<String, Object> arguments) {

        return CompletableFuture.supplyAsync(() -> {
            try {
                return delegate.execute(toolName, arguments);
            } catch (ToolExecutionException e) {
                throw new CompletionException(e);
            }
        }, executor);
    }

    public ToolExecutionFuture executeWithTimeout(
            String toolName,
            Map<String, Object> arguments,
            Duration timeout) {

        CompletableFuture<ToolResult> future = executeAsync(toolName, arguments);

        return new ToolExecutionFuture(future, timeout);
    }
}

public class ToolExecutionFuture {
    private final CompletableFuture<ToolResult> future;
    private final Duration timeout;

    public Optional<ToolResult> getResult() throws TimeoutException {
        try {
            return Optional.ofNullable(
                    future.get(timeout.toMillis(), TimeUnit.MILLISECONDS)
            );
        } catch (InterruptedException | ExecutionException e) {
            return Optional.empty();
        }
    }

    public boolean cancel() {
        return future.cancel(true);
    }

    public boolean isDone() {
        return future.isDone();
    }
}
```

## Health Checks

### McpHealthIndicator

Spring Boot actuator health check for MCP server.

```java
@Component
public class McpHealthIndicator implements HealthIndicator {

    private final McpServer mcpServer;
    private final ToolRegistry toolRegistry;

    @Override
    public Health health() {
        Health.Builder builder = new Health.Builder();

        try {
            // Check transport
            Transport transport = mcpServer.getTransport();
            builder.withDetail("transport", transport.getClass().getSimpleName());
            builder.withDetail("connected", transport.isConnected());

            // Check tools
            List<Tool> tools = toolRegistry.listTools();
            builder.withDetail("tools.count", tools.size());

            // Sample tool execution
            testToolExecution(builder, tools);

            builder.status(Status.UP);
        } catch (Exception e) {
            builder.status(Status.DOWN)
                    .withDetail("error", e.getMessage());
        }

        return builder.build();
    }

    private void testToolExecution(Health.Builder builder, List<Tool> tools) {
        if (!tools.isEmpty()) {
            Tool sampleTool = tools.get(0);
            try {
                ToolResult result = sampleTool.execute(Map.of());
                builder.withDetail("sampleTool.status", "success");
            } catch (Exception e) {
                builder.withDetail("sampleTool.status", "failed");
                builder.withDetail("sampleTool.error", e.getMessage());
            }
        }
    }
}
```

## Performance Metrics

### McpMetrics

Micrometer-based metrics for MCP server.

```java
@Component
public class McpMetrics {

    private final MeterRegistry meterRegistry;

    private Counter toolExecutionsCounter;
    private Timer toolExecutionTimer;
    private DistributionSummary toolArgumentSize;
    private Counter toolFailuresCounter;
    private Counter promptRenderCounter;

    @PostConstruct
    public void initialize() {
        toolExecutionsCounter = Counter.builder("mcp.tool.executions")
                .description("Number of tool executions")
                .register(meterRegistry);

        toolExecutionTimer = Timer.builder("mcp.tool.execution.time")
                .description("Time taken for tool execution")
                .register(meterRegistry);

        toolArgumentSize = DistributionSummary.builder("mcp.tool.arguments.size")
                .description("Size of tool arguments")
                .register(meterRegistry);

        toolFailuresCounter = Counter.builder("mcp.tool.failures")
                .description("Number of tool failures")
                .register(meterRegistry);

        promptRenderCounter = Counter.builder("mcp.prompt.renders")
                .description("Number of prompt renders")
                .register(meterRegistry);
    }

    public void recordToolExecution(String toolName, long durationMs, boolean success) {
        toolExecutionsCounter.increment();
        toolExecutionTimer.record(durationMs, TimeUnit.MILLISECONDS);

        if (!success) {
            toolFailuresCounter.increment();
        }

        Tags tags = Tags.of("tool", toolName, "success", String.valueOf(success));
        meterRegistry.counter("mcp.tool.executions.byTool", tags).increment();
    }

    public void recordPromptRender(String templateName) {
        promptRenderCounter.increment();

        Tags tags = Tags.of("template", templateName);
        meterRegistry.counter("mcp.prompt.renders.byTemplate", tags).increment();
    }

    public void recordArgumentSize(int size) {
        toolArgumentSize.record(size);
    }
}
```