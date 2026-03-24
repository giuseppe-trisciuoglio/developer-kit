# Spring AI MCP Server — Implementation Patterns

Detailed patterns for creating tools, prompt templates, and configuring Spring Boot MCP servers.

## Tool Creation Patterns

### Database Tool

```java
@Component
public class DatabaseTools {

    private final JdbcTemplate jdbcTemplate;

    public DatabaseTools(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Tool(description = "Execute a safe read-only SQL query")
    public List<Map<String, Object>> executeQuery(
            @ToolParam("SQL SELECT query") String query,
            @ToolParam(value = "Query parameters", required = false) Map<String, Object> params) {

        if (!query.trim().toUpperCase().startsWith("SELECT")) {
            throw new IllegalArgumentException("Only SELECT queries are allowed");
        }
        return jdbcTemplate.queryForList(query, params);
    }

    @Tool(description = "Get table schema information")
    public TableSchema getTableSchema(@ToolParam("Table name") String tableName) {
        String sql = "SELECT column_name, data_type " +
                     "FROM information_schema.columns WHERE table_name = ?";
        List<Map<String, Object>> columns = jdbcTemplate.queryForList(sql, tableName);
        return new TableSchema(tableName, columns);
    }
}

record TableSchema(String tableName, List<Map<String, Object>> columns) {}
```

### API Integration Tool

```java
@Component
public class ApiTools {

    private final WebClient webClient;

    public ApiTools(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }

    @Tool(description = "Make HTTP GET request to an API")
    public ApiResponse callApi(
            @ToolParam("API URL") String url,
            @ToolParam(value = "Headers as JSON string", required = false) String headersJson) {

        try { new URL(url); } catch (MalformedURLException e) {
            throw new IllegalArgumentException("Invalid URL format");
        }

        HttpHeaders headers = new HttpHeaders();
        if (headersJson != null && !headersJson.isBlank()) {
            try {
                Map<String, String> map = new ObjectMapper().readValue(headersJson, Map.class);
                map.forEach(headers::add);
            } catch (JsonProcessingException e) {
                throw new IllegalArgumentException("Invalid headers JSON");
            }
        }

        return webClient.get()
                .uri(url)
                .headers(h -> h.addAll(headers))
                .retrieve()
                .bodyToMono(ApiResponse.class)
                .block();
    }
}

record ApiResponse(int status, Map<String, Object> body, HttpHeaders headers) {}
```

### File System Tool

```java
@Component
public class FileSystemTools {

    private final Path basePath;

    public FileSystemTools(@Value("${mcp.file.base-path:/tmp}") String basePath) {
        this.basePath = Paths.get(basePath).normalize();
    }

    @Tool(description = "List files in a directory")
    public List<FileInfo> listFiles(
            @ToolParam(value = "Directory path (relative to base)", required = false) String directory) {

        Path targetPath = resolvePath(directory != null ? directory : "");
        validatePath(targetPath);

        try (Stream<Path> stream = Files.list(targetPath)) {
            return stream.filter(Files::isRegularFile).map(this::toFileInfo).toList();
        } catch (IOException e) {
            throw new RuntimeException("Failed to list files", e);
        }
    }

    @Tool(description = "Read file contents")
    public FileContent readFile(
            @ToolParam("File path (relative to base)") String filePath,
            @ToolParam(value = "Maximum lines to read", required = false) Integer maxLines) {

        Path targetPath = resolvePath(filePath);
        validatePath(targetPath);

        try {
            List<String> lines = maxLines != null
                    ? Files.lines(targetPath).limit(maxLines).toList()
                    : Files.readAllLines(targetPath);
            return new FileContent(targetPath.toString(), lines);
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }
    }

    private Path resolvePath(String relativePath) {
        return basePath.resolve(relativePath).normalize();
    }

    private void validatePath(Path path) {
        if (!path.startsWith(basePath)) {
            throw new SecurityException("Path traversal not allowed");
        }
    }

    private FileInfo toFileInfo(Path path) {
        try {
            return new FileInfo(basePath.relativize(path).toString(),
                    Files.size(path), Files.getLastModifiedTime(path).toInstant());
        } catch (IOException e) {
            return new FileInfo(path.toString(), 0, Instant.now());
        }
    }
}

record FileInfo(String path, long size, Instant lastModified) {}
record FileContent(String path, List<String> lines) {}
```

## Prompt Template Patterns

```java
@Component
public class CodeReviewPrompts {

    @PromptTemplate(
        name = "java-code-review",
        description = "Review Java code for best practices and issues"
    )
    public Prompt createJavaCodeReviewPrompt(
            @PromptParam("code") String code,
            @PromptParam(value = "focusAreas", required = false) List<String> focusAreas) {

        String focus = focusAreas != null ? String.join(", ", focusAreas) : "general best practices";
        return Prompt.builder()
                .system("You are an expert Java code reviewer with 20 years of experience.")
                .user("""
                    Review the following Java code for %s:
                    ```java
                    %s
                    ```
                    Format: ## Critical Issues | ## Warnings | ## Suggestions | ## Positive Aspects
                    """.formatted(focus, code))
                .build();
    }

    @PromptTemplate(
        name = "generate-unit-tests",
        description = "Generate comprehensive unit tests for Java code"
    )
    public Prompt createTestGenerationPrompt(
            @PromptParam("code") String code,
            @PromptParam("className") String className,
            @PromptParam(value = "testingFramework", required = false) String framework) {

        String testFramework = framework != null ? framework : "JUnit 5";
        return Prompt.builder()
                .system("You are an expert in test-driven development.")
                .user("""
                    Generate comprehensive unit tests for class %s using %s:
                    ```java
                    %s
                    ```
                    Requirements: test all public methods, include edge cases, use AAA pattern, mock dependencies.
                    """.formatted(className, testFramework, code))
                .build();
    }
}
```

## FunctionCallback (Low-Level Pattern)

For low-level function calling without annotations:

```java
@Configuration
public class FunctionConfig {

    @Bean
    public FunctionCallback weatherFunction() {
        return FunctionCallback.builder()
                .function("getCurrentWeather", new WeatherService())
                .description("Get the current weather for a location")
                .inputType(WeatherRequest.class)
                .build();
    }

    @Bean
    public FunctionCallback calculatorFunction() {
        return FunctionCallbackWrapper.builder(new Calculator())
                .withName("calculate")
                .withDescription("Perform mathematical calculations")
                .build();
    }
}

class WeatherService implements Function<WeatherRequest, WeatherResponse> {
    @Override
    public WeatherResponse apply(WeatherRequest request) {
        return new WeatherResponse(request.location(), 72, "Sunny");
    }
}

record WeatherRequest(String location) {}
record WeatherResponse(String location, double temperature, String condition) {}
```

## Spring Boot Auto-Configuration

```java
@Configuration
@AutoConfigureAfter({WebMvcAutoConfiguration.class})
@ConditionalOnClass({McpServer.class, ChatModel.class})
@ConditionalOnProperty(name = "spring.ai.mcp.enabled", havingValue = "true", matchIfMissing = true)
public class McpAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public McpServer mcpServer(
            List<FunctionCallback> functionCallbacks,
            List<PromptTemplate> promptTemplates,
            McpServerProperties properties) {

        McpServer.Builder builder = McpServer.builder()
                .serverInfo("spring-ai-mcp", "1.0.0")
                .transport(properties.getTransport().create());

        functionCallbacks.forEach(cb -> builder.tool(Tool.fromFunctionCallback(cb)));
        promptTemplates.forEach(t -> builder.prompt(Prompt.fromTemplate(t)));

        return builder.build();
    }

    @Bean
    @ConditionalOnProperty(name = "spring.ai.mcp.actuator.enabled", havingValue = "true")
    public McpHealthIndicator mcpHealthIndicator(McpServer mcpServer) {
        return new McpHealthIndicator(mcpServer);
    }
}
```

## Application Properties Reference

### application.yml (complete)

```yaml
spring:
  application:
    name: my-mcp-server
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.7
    mcp:
      enabled: true
      server:
        name: my-mcp-server
        version: 1.0.0
      transport:
        type: stdio          # stdio | http | sse
        http:
          port: 8080
          path: /mcp
          cors:
            enabled: true
            allowed-origins: "*"
      security:
        enabled: true
        authorization:
          mode: role-based   # none | role-based | permission-based | attribute-based
          default-deny: true
        audit:
          enabled: true
      tools:
        package-scan: com.example.mcp.tools
        validation:
          enabled: true
          max-execution-time: 30s
        caching:
          enabled: true
          ttl: 5m
      prompts:
        package-scan: com.example.mcp.prompts
        caching:
          enabled: true
          ttl: 1h
      actuator:
        enabled: true
      rate-limiter:
        enabled: true
        requests-per-minute: 100

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true

logging:
  level:
    com.example.mcp: DEBUG
    org.springframework.ai: INFO
```

### Custom Server Configuration (Interceptors)

```java
@Configuration
public class CustomMcpConfig {

    @Bean
    public McpServerCustomizer mcpServerCustomizer(MeterRegistry meterRegistry) {
        return server -> {
            server.addToolInterceptor((tool, args, chain) -> {
                long start = System.currentTimeMillis();
                Object result = chain.execute(tool, args);
                long duration = System.currentTimeMillis() - start;
                meterRegistry.timer("mcp.tool.duration", "tool", tool.name())
                        .record(duration, TimeUnit.MILLISECONDS);
                return result;
            });
        };
    }
}
```
