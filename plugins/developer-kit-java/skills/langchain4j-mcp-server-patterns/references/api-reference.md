# LangChain4j MCP Server API Reference

This document provides comprehensive API documentation for implementing MCP servers with LangChain4j.

## Core MCP Classes

### McpClient Interface

Primary interface for communicating with MCP servers.

**Key Methods:**
```java
// Tool Management
List<ToolSpecification> listTools();
String executeTool(ToolExecutionRequest request);

// Resource Management
List<McpResource> listResources();
String getResource(String uri);
List<McpResourceTemplate> listResourceTemplates();

// Prompt Management
List<Prompt> listPrompts();
String getPrompt(String name);

// Lifecycle Management
void close();
```

### DefaultMcpClient.Builder

Builder for creating MCP clients with configuration options.

**Configuration Methods:**
```java
McpClient client = new DefaultMcpClient.Builder()
    .key("unique-client-id")                    // Unique identifier
    .transport(transport)                        // Transport mechanism
    .cacheToolList(true)                         // Enable tool caching
    .logMessageHandler(handler)                 // Custom logging
    .build();
```

### McpToolProvider.Builder

Builder for creating tool providers that bridge MCP servers to LangChain4j AI services.

**Configuration Methods:**
```java
McpToolProvider provider = McpToolProvider.builder()
    .mcpClients(client1, client2)               // Add MCP clients
    .failIfOneServerFails(false)                // Configure failure handling
    .filterToolNames("tool1", "tool2")           // Filter by names
    .filter((client, tool) -> logic)             // Custom filtering
    .build();
```

## Transport Configuration

### StdioMcpTransport.Builder

For local process communication with npm packages or Docker containers.

```java
McpTransport transport = new StdioMcpTransport.Builder()
    .command(List.of("npm", "exec", "@modelcontextprotocol/server-everything@0.6.2"))
    .logEvents(true)
    .build();
```

### HttpMcpTransport.Builder

For HTTP-based communication with remote MCP servers.

```java
McpTransport transport = new HttpMcpTransport.Builder()
    .sseUrl("http://localhost:3001/sse")
    .logRequests(true)
    .logResponses(true)
    .build();
```

### StreamableHttpMcpTransport.Builder

For streamable HTTP transport with enhanced performance.

```java
McpTransport transport = new StreamableHttpMcpTransport.Builder()
    .url("http://localhost:3001/mcp")
    .logRequests(true)
    .logResponses(true)
    .build();
```

## AI Service Integration

### AiServices.builder()

Create AI services integrated with MCP tool providers.

**Integration Methods:**
```java
AIAssistant assistant = AiServices.builder(AIAssistant.class)
    .chatModel(chatModel)
    .toolProvider(toolProvider)
    .chatMemoryProvider(memoryProvider)
    .build();
```

## Error Handling and Management

### Exception Handling

Handle MCP-specific exceptions gracefully:

```java
try {
    String result = mcpClient.executeTool(request);
} catch (McpException e) {
    log.error("MCP execution failed: {}", e.getMessage());
    // Implement fallback logic
}
```

### Retry and Resilience

Implement retry logic for unreliable MCP servers:

```java
RetryTemplate retryTemplate = RetryTemplate.builder()
    .maxAttempts(3)
    .exponentialBackoff(1000, 2, 10000)
    .build();

String result = retryTemplate.execute(context ->
    mcpClient.executeTool(request));
```

## Configuration Properties

### Application Configuration

```yaml
mcp:
  fail-if-one-server-fails: false
  cache-tools: true
  servers:
    github:
      type: docker
      command: ["/usr/local/bin/docker", "run", "-e", "GITHUB_TOKEN", "-i", "mcp/github"]
      log-events: true
    database:
      type: stdio
      command: ["/usr/bin/npm", "exec", "@modelcontextprotocol/server-sqlite@0.6.2"]
      log-events: false
```

### Spring Boot Configuration

```java
@Configuration
@EnableConfigurationProperties(McpProperties.class)
public class McpConfiguration {

    @Bean
    public List<McpClient> mcpClients(McpProperties properties) {
        return properties.getServers().entrySet().stream()
            .map(entry -> createMcpClient(entry.getKey(), entry.getValue()))
            .collect(Collectors.toList());
    }

    @Bean
    public McpToolProvider mcpToolProvider(List<McpClient> mcpClients, McpProperties properties) {
        return McpToolProvider.builder()
            .mcpClients(mcpClients)
            .failIfOneServerFails(properties.isFailIfOneServerFails())
            .build();
    }
}
```

## Tool Specification and Execution

### Tool Specification

Define tools with proper schema:

```java
ToolSpecification toolSpec = ToolSpecification.builder()
    .name("database_query")
    .description("Execute SQL queries against the database")
    .inputSchema(Map.of(
        "type", "object",
        "properties", Map.of(
            "sql", Map.of(
                "type", "string",
                "description", "SQL query to execute"
            )
        )
    ))
    .build();
```

### Tool Execution

Execute tools with structured requests:

```java
ToolExecutionRequest request = ToolExecutionRequest.builder()
    .name("database_query")
    .arguments("{\"sql\": \"SELECT * FROM users LIMIT 10\"}")
    .build();

String result = mcpClient.executeTool(request);
```

## Resource Handling

### Resource Access

Access and utilize MCP resources:

```java
// List available resources
List<McpResource> resources = mcpClient.listResources();

// Get specific resource content
String content = mcpClient.getResource("resource://schema/database");

// Work with resource templates
List<McpResourceTemplate> templates = mcpClient.listResourceTemplates();
```

### Resource as Tools

Convert MCP resources to tools automatically:

```java
DefaultMcpResourcesAsToolsPresenter presenter =
    new DefaultMcpResourcesAsToolsPresenter();
mcpToolProvider.provideTools(presenter);

// Adds 'list_resources' and 'get_resource' tools automatically
```

## Security and Filtering

### Tool Filtering

Implement security-conscious tool filtering:

```java
McpToolProvider secureProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .filter((client, tool) -> {
        // Check user permissions
        if (tool.name().startsWith("admin_") && !currentUser.hasRole("ADMIN")) {
            return false;
        }
        return true;
    })
    .build();
```

### Resource Security

Apply security controls to resource access:

```java
public boolean canAccessResource(String uri, User user) {
    if (uri.contains("sensitive/") && !user.hasRole("ADMIN")) {
        return false;
    }
    return true;
}
```

## Performance Optimization

### Caching Strategy

Implement intelligent caching:

```java
// Enable tool caching for performance
McpClient client = new DefaultMcpClient.Builder()
    .transport(transport)
    .cacheToolList(true)
    .build();

// Periodic cache refresh
@Scheduled(fixedRate = 300000) // 5 minutes
public void refreshToolCache() {
    mcpClients.forEach(client -> {
        try {
            client.invalidateCache();
            client.listTools(); // Preload cache
        } catch (Exception e) {
            log.warn("Cache refresh failed: {}", e.getMessage());
        }
    });
}
```

### Connection Pooling

Optimize connection management:

```java
@Bean
public Executor mcpExecutor() {
    return Executors.newFixedThreadPool(10); // Dedicated thread pool
}
```

## Testing and Validation

### Mock Configuration

Setup for testing:

```java
@TestConfiguration
public class MockMcpConfiguration {

    @Bean
    @Primary
    public McpClient mockMcpClient() {
        McpClient mock = Mockito.mock(McpClient.class);

        when(mock.listTools()).thenReturn(List.of(
            ToolSpecification.builder()
                .name("test_tool")
                .description("Test tool")
                .build()
        ));

        when(mock.executeTool(any(ToolExecutionRequest.class)))
            .thenReturn("Mock result");

        return mock;
    }
}
```

### Integration Testing

Test MCP integrations:

```java
@SpringBootTest
class McpIntegrationTest {

    @Autowired
    private AIAssistant assistant;

    @Test
    void shouldExecuteToolsSuccessfully() {
        String response = assistant.chat("Execute test tool");

        assertThat(response).contains("Mock result");
    }
}
```

## Monitoring and Observability

### Health Checks

Monitor MCP server health:

```java
@Component
public class McpHealthChecker {

    @EventListener
    @Async
    public void checkHealth() {
        mcpClients.forEach(client -> {
            try {
                client.listTools(); // Simple health check
                healthRegistry.markHealthy(client.key());
            } catch (Exception e) {
                healthRegistry.markUnhealthy(client.key(), e.getMessage());
            }
        });
    }
}
```

### Metrics Collection

Collect execution metrics:

```java
@Bean
public Counter toolExecutionCounter(MeterRegistry meterRegistry) {
    return meterRegistry.counter("mcp.tool.execution", "type", "total");
}

@Bean
public Timer toolExecutionTimer(MeterRegistry meterRegistry) {
    return meterRegistry.timer("mcp.tool.execution.time");
}
```

## Migration and Versioning

### Version Compatibility

Handle version compatibility:

```java
public class VersionedMcpClient {

    public boolean isCompatible(String serverVersion) {
        return semanticVersionChecker.isCompatible(
            REQUIRED_MCP_VERSION, serverVersion);
    }

    public McpClient createClient(ServerConfig config) {
        if (!isCompatible(config.getVersion())) {
            throw new IncompatibleVersionException(
                "Server version " + config.getVersion() +
                " is not compatible with required " + REQUIRED_MCP_VERSION);
        }

        return new DefaultMcpClient.Builder()
            .transport(createTransport(config))
            .build();
    }
}
```

This API reference provides the complete foundation for implementing MCP servers and clients with LangChain4j, covering all major aspects from basic setup to advanced enterprise patterns.