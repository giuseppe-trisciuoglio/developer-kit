---
name: langchain4j-mcp-server-patterns
description: Model Context Protocol (MCP) server implementation patterns with LangChain4j. Use when building MCP servers to extend AI capabilities with custom tools and resources.
category: ai-integration
tags: [langchain4j, mcp, model-context-protocol, tools, ai-services, java, spring-boot]
version: 1.0.1
context7_library: /langchain4j/langchain4j
context7_trust_score: 7.8
allowed-tools: Read, Write, Bash
---

# LangChain4j MCP Server Integration Patterns

This skill provides comprehensive guidance for integrating LangChain4j applications with Model Context Protocol (MCP) servers, enabling AI applications to connect seamlessly with external data sources, tools, and services through standardized protocols.

## When to Use This Skill

Use this skill when:
- Building AI applications that need to access external tools and data sources
- Creating dynamic tool providers that can adapt based on context
- Integrating with multiple MCP servers for different domains (GitHub, databases, APIs)
- Implementing resource-based data access for AI models
- Building scalable AI agents with standardized tool interfaces
- Creating enterprise AI solutions with secure tool execution
- Developing context-aware AI applications with real-time data access
- Implementing fail-safe tool execution with graceful degradation
- Building AI services that require dynamic tool discovery and filtering
- Creating multi-modal AI applications with diverse data sources

## Core Concepts

### Model Context Protocol (MCP)

MCP is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It acts like "USB-C for AI" - providing a universal way to connect AI models to data sources and tools.

**Key MCP Components:**
- **Tools**: Executable functions that AI can call (e.g., database queries, API calls)
- **Resources**: Static or dynamic data sources (e.g., files, schemas, documentation)
- **Prompts**: Pre-configured templates for specific tasks
- **Transport**: Communication layer (stdio, HTTP, WebSocket)

**MCP Architecture:**
```java
// Client-Server Architecture
AI Application (LangChain4j) ←→ MCP Client ←→ Transport ←→ MCP Server ←→ External Service
```

### LangChain4j MCP Integration

LangChain4j provides native MCP support through several key components:

**Core MCP Classes:**
- `McpClient`: Interface for communicating with MCP servers
- `DefaultMcpClient`: Default implementation with caching and configuration
- `McpTransport`: Communication layer abstraction
- `McpToolProvider`: Bridges MCP tools to LangChain4j AI services
- `McpToolExecutor`: Executes MCP tools and handles responses

### MCP Transport Configuration

Configure how LangChain4j connects to MCP servers through various transport mechanisms.

**Stdio Transport (Local Processes):**
```java
// NPM package server
McpTransport transport = new StdioMcpTransport.Builder()
    .command(List.of("/usr/bin/npm", "exec", "@modelcontextprotocol/server-everything@0.6.2"))
    .logEvents(true)  // Enable debugging
    .build();

// Docker container server
McpTransport transport = new StdioMcpTransport.Builder()
    .command(List.of("/usr/local/bin/docker", "run", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "-i", "mcp/github"))
    .logEvents(true)
    .build();
```

**HTTP Transport (Remote Servers):**
```java
// Server-Sent Events (SSE) based transport
McpTransport transport = new HttpMcpTransport.Builder()
    .sseUrl("http://localhost:3001/sse")
    .logRequests(true)
    .logResponses(true)
    .build();

// Streamable HTTP transport
McpTransport transport = new StreamableHttpMcpTransport.Builder()
    .url("http://localhost:3001/mcp")
    .logRequests(true)
    .logResponses(true)
    .build();
```

### MCP Client Configuration

Create and configure MCP clients for server communication and tool management.

**Basic Client Setup:**
```java
McpClient mcpClient = new DefaultMcpClient.Builder()
    .key("MyMCPClient")  // Unique identifier
    .transport(transport)
    .build();
```

**Advanced Client Configuration:**
```java
McpClient mcpClient = new DefaultMcpClient.Builder()
    .key("DatabaseMCPClient")
    .transport(transport)
    .cacheToolList(true)  // Cache tools for performance
    .logMessageHandler(new CustomLogMessageHandler())  // Custom logging
    .build();
```

**Client Resource Management:**
```java
// Always close clients properly
try (McpClient mcpClient = new DefaultMcpClient.Builder()
        .transport(transport)
        .build()) {

    // Use client for operations
    List<ToolSpecification> tools = mcpClient.listTools();

} // Auto-closed
```

### MCP Tool Provider Patterns

Bridge MCP servers to LangChain4j AI services through tool providers.

**Basic Tool Provider:**
```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .build();
```

**Multi-Server Tool Provider:**
```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(githubClient, databaseClient, apiClient)
    .failIfOneServerFails(false)  // Continue if one server fails
    .build();
```

**Tool Filtering by Name:**
```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .filterToolNames("get_issue", "get_issue_comments", "list_issues")
    .build();
```

**Advanced Tool Filtering:**
```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient1, mcpClient2)
    .filter((mcpClient, tool) -> {
        // Complex filtering logic
        if (tool.name().startsWith("admin_") && !isAdminUser()) {
            return false;
        }
        // Resolve naming conflicts between servers
        if (tool.name().equals("search") && mcpClient.key().equals("primary-search")) {
            return true;
        }
        return !tool.name().startsWith("deprecated_");
    })
    .build();
```

### AI Service Integration

Integrate MCP tool providers with LangChain4j AI services for seamless tool execution.

**Basic AI Service with MCP Tools:**
```java
interface AIAssistant {
    String chat(String message);
}

ChatModel model = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName("gpt-4")
    .build();

AIAssistant assistant = AiServices.builder(AIAssistant.class)
    .chatModel(model)
    .toolProvider(toolProvider)
    .build();

String response = assistant.chat("Get the latest issues from the repository");
```

**Spring Boot Service Integration:**
```java
@Service
public class AIAssistantService {

    private final AIAssistant assistant;

    public AIAssistantService(ChatModel chatModel, McpToolProvider toolProvider) {
        this.assistant = AiServices.builder(AIAssistant.class)
            .chatModel(chatModel)
            .toolProvider(toolProvider)
            .build();
    }

    public String processQuery(String userQuery) {
        return assistant.chat(userQuery);
    }
}
```

**Advanced AI Service with Memory and Error Handling:**
```java
@Component
public class EnterpriseAIService {

    private final ChatModel chatModel;
    private final McpToolProvider toolProvider;
    private final ChatMemoryProvider memoryProvider;

    public EnterpriseAIService(ChatModel chatModel,
                              List<McpClient> mcpClients,
                              ChatMemoryProvider memoryProvider) {
        this.chatModel = chatModel;
        this.memoryProvider = memoryProvider;
        this.toolProvider = McpToolProvider.builder()
            .mcpClients(mcpClients)
            .failIfOneServerFails(false)
            .build();
    }

    public String chat(@MemoryId String sessionId, String message) {
        AIAssistant assistant = AiServices.builder(AIAssistant.class)
            .chatModel(chatModel)
            .toolProvider(toolProvider)
            .chatMemoryProvider(memoryProvider)
            .build();

        return assistant.chat(sessionId, message);
    }
}
```

### Resource Handling Patterns

Work with MCP resources to provide context and data to AI models.

**Resource as Synthetic Tools:**
```java
// Automatically expose MCP resources as tools
DefaultMcpResourcesAsToolsPresenter presenter = new DefaultMcpResourcesAsToolsPresenter();
mcpToolProvider.provideTools(presenter);

// This adds 'list_resources' and 'get_resource' tools automatically
```

**Custom Resource Access:**
```java
@Component
public class McpResourceService {

    private final McpClient mcpClient;

    public McpResourceService(McpClient mcpClient) {
        this.mcpClient = mcpClient;
    }

    public List<McpResource> getAvailableResources() {
        return mcpClient.listResources();
    }

    public String getResourceContent(String uri) {
        return mcpClient.getResource(uri);
    }

    public List<McpResourceTemplate> getResourceTemplates() {
        return mcpClient.listResourceTemplates();
    }
}
```

### Low-Level Tool Execution

Execute MCP tools directly without AI service abstraction for fine-grained control.

**Manual Tool Execution:**
```java
// List available tools
List<ToolSpecification> toolSpecifications = mcpClient.listTools();

// Build chat request with tools
ChatRequest chatRequest = ChatRequest.builder()
    .messages(UserMessage.from("What's the weather in London?"))
    .toolSpecifications(toolSpecifications)
    .build();

ChatResponse response = chatModel.chat(chatRequest);
AiMessage aiMessage = response.aiMessage();

// Handle tool execution requests
if (aiMessage.hasToolExecutionRequests()) {
    for (ToolExecutionRequest request : aiMessage.toolExecutionRequests()) {
        String result = mcpClient.executeTool(request);
        ToolExecutionResultMessage resultMessage =
            ToolExecutionResultMessage.from(request.id(), request.name(), result);
        // Process result or add to conversation memory
    }
}
```

**Programmatic Tool Execution:**
```java
ToolExecutionRequest request = ToolExecutionRequest.builder()
    .name("database_query")
    .arguments("{\"sql\": \"SELECT * FROM users LIMIT 10\"}")
    .build();

String result = mcpClient.executeTool(request);
```

### Configuration Management

Manage MCP client and server configurations in enterprise applications.

**Spring Boot Configuration:**
```java
@Configuration
@EnableConfigurationProperties(McpProperties.class)
public class McpConfiguration {

    @ConfigurationProperties(prefix = "mcp")
    public static class McpProperties {
        private Map<String, ServerConfig> servers = new HashMap<>();
        private boolean failIfOneServerFails = false;
        private boolean cacheTools = true;

        // Getters and setters

        public static class ServerConfig {
            private String type; // "stdio", "http", "docker"
            private List<String> command;
            private String url;
            private boolean logEvents = false;

            // Getters and setters
        }
    }

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

    private McpClient createMcpClient(String key, McpProperties.ServerConfig config) {
        McpTransport transport = createTransport(config);

        return new DefaultMcpClient.Builder()
            .key(key)
            .transport(transport)
            .cacheToolList(config.isCacheTools())
            .build();
    }

    private McpTransport createTransport(McpProperties.ServerConfig config) {
        switch (config.getType()) {
            case "stdio":
                return new StdioMcpTransport.Builder()
                    .command(config.getCommand())
                    .logEvents(config.isLogEvents())
                    .build();
            case "http":
                return new HttpMcpTransport.Builder()
                    .sseUrl(config.getUrl())
                    .logRequests(config.isLogEvents())
                    .logResponses(config.isLogEvents())
                    .build();
            default:
                throw new IllegalArgumentException("Unsupported transport type: " + config.getType());
        }
    }
}
```

**Application Properties:**
```yaml
mcp:
  fail-if-one-server-fails: false
  cache-tools: true
  servers:
    github:
      type: docker
      command: ["/usr/local/bin/docker", "run", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "-i", "mcp/github"]
      log-events: true
    database:
      type: stdio
      command: ["/usr/bin/npm", "exec", "@modelcontextprotocol/server-sqlite"]
      log-events: false
    weather:
      type: http
      url: "http://weather-mcp-server:3001/sse"
      log-events: true
```

## API Reference

### Core MCP Classes

**McpClient Interface:**
- `listTools()`: Get available tool specifications
- `executeTool(ToolExecutionRequest)`: Execute a specific tool
- `listResources()`: Get available resources
- `getResource(String uri)`: Retrieve resource content
- `listResourceTemplates()`: Get resource templates
- `listPrompts()`: Get available prompts
- `close()`: Close the client connection

**DefaultMcpClient.Builder:**
- `key(String)`: Set unique client identifier
- `transport(McpTransport)`: Set transport mechanism
- `cacheToolList(boolean)`: Enable/disable tool caching
- `logMessageHandler(McpLogMessageHandler)`: Set custom logging
- `build()`: Create the client instance

**McpToolProvider.Builder:**
- `mcpClients(McpClient...)`: Add MCP clients
- `mcpClients(List<McpClient>)`: Add MCP client list
- `failIfOneServerFails(boolean)`: Configure failure behavior
- `filterToolNames(String...)`: Filter tools by name
- `filter(BiPredicate<McpClient, ToolSpecification>)`: Custom tool filtering
- `build()`: Create the tool provider

**Transport Builders:**
- `StdioMcpTransport.Builder()`: For local process communication
- `HttpMcpTransport.Builder()`: For HTTP/SSE communication
- `StreamableHttpMcpTransport.Builder()`: For streamable HTTP

### Transport Configuration Methods

**StdioMcpTransport.Builder:**
- `command(List<String>)`: Set process command and arguments
- `logEvents(boolean)`: Enable event logging
- `build()`: Create transport

**HttpMcpTransport.Builder:**
- `sseUrl(String)`: Set Server-Sent Events URL
- `logRequests(boolean)`: Enable request logging
- `logResponses(boolean)`: Enable response logging
- `build()`: Create transport

### AI Service Integration Methods

**AiServices.builder():**
- `chatModel(ChatModel)`: Set the chat model
- `toolProvider(ToolProvider)`: Set MCP tool provider
- `tools(Map<ToolSpecification, ToolExecutor>)`: Set tool map directly
- `chatMemoryProvider(ChatMemoryProvider)`: Set memory provider
- `build()`: Create the AI service

## Workflow Patterns

### Enterprise MCP Integration Pattern

**Complete enterprise setup with multiple MCP servers:**
```java
@Configuration
public class EnterpriseAIConfiguration {

    @Bean
    @ConditionalOnProperty("mcp.github.enabled")
    public McpClient githubMcpClient() {
        McpTransport transport = new StdioMcpTransport.Builder()
            .command(List.of("/usr/local/bin/docker", "run",
                           "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                           "-i", "mcp/github"))
            .build();

        return new DefaultMcpClient.Builder()
            .key("github")
            .transport(transport)
            .build();
    }

    @Bean
    @ConditionalOnProperty("mcp.database.enabled")
    public McpClient databaseMcpClient() {
        McpTransport transport = new StdioMcpTransport.Builder()
            .command(List.of("/usr/bin/npm", "exec", "@modelcontextprotocol/server-sqlite"))
            .build();

        return new DefaultMcpClient.Builder()
            .key("database")
            .transport(transport)
            .build();
    }

    @Bean
    public McpToolProvider enterpriseToolProvider(List<McpClient> mcpClients) {
        return McpToolProvider.builder()
            .mcpClients(mcpClients)
            .failIfOneServerFails(false)
            .filter(this::filterToolsForSecurity)
            .build();
    }

    private boolean filterToolsForSecurity(McpClient client, ToolSpecification tool) {
        // Implement security filtering logic
        return !tool.name().startsWith("admin_") || hasAdminRole();
    }

    @Bean
    public AIOrchestrator aiOrchestrator(ChatModel chatModel, McpToolProvider toolProvider) {
        return AiServices.builder(AIOrchestrator.class)
            .chatModel(chatModel)
            .toolProvider(toolProvider)
            .build();
    }
}
```

### Dynamic Tool Discovery Pattern

**Runtime tool discovery and filtering based on user context:**
```java
@Service
public class DynamicToolService {

    private final List<McpClient> mcpClients;
    private final ChatModel chatModel;

    public AIAssistant createContextualAssistant(String userId, String[] allowedDomains) {
        McpToolProvider contextualProvider = McpToolProvider.builder()
            .mcpClients(mcpClients)
            .filter((client, tool) -> isToolAllowedForUser(userId, allowedDomains, client, tool))
            .build();

        return AiServices.builder(AIAssistant.class)
            .chatModel(chatModel)
            .toolProvider(contextualProvider)
            .build();
    }

    private boolean isToolAllowedForUser(String userId, String[] allowedDomains,
                                       McpClient client, ToolSpecification tool) {
        // Check user permissions
        if (!userHasPermission(userId, tool.name())) {
            return false;
        }

        // Check domain restrictions
        return Arrays.stream(allowedDomains)
            .anyMatch(domain -> client.key().startsWith(domain));
    }
}
```

### Resilient MCP Client Pattern

**Robust MCP client with retry logic and fallback strategies:**
```java
@Component
public class ResilientMcpService {

    private final List<McpClient> mcpClients;
    private final RetryTemplate retryTemplate;

    public ResilientMcpService(List<McpClient> mcpClients) {
        this.mcpClients = mcpClients;
        this.retryTemplate = RetryTemplate.builder()
            .maxAttempts(3)
            .exponentialBackoff(1000, 2, 10000)
            .build();
    }

    public Optional<String> executeToolWithFallback(String toolName, String arguments) {
        for (McpClient client : mcpClients) {
            try {
                return Optional.of(retryTemplate.execute(context -> {
                    ToolExecutionRequest request = ToolExecutionRequest.builder()
                        .name(toolName)
                        .arguments(arguments)
                        .build();
                    return client.executeTool(request);
                }));
            } catch (Exception e) {
                log.warn("Failed to execute tool {} with client {}: {}",
                        toolName, client.key(), e.getMessage());
            }
        }
        return Optional.empty();
    }

    public List<ToolSpecification> getAvailableTools() {
        return mcpClients.stream()
            .flatMap(client -> {
                try {
                    return client.listTools().stream();
                } catch (Exception e) {
                    log.warn("Failed to list tools from client {}: {}",
                            client.key(), e.getMessage());
                    return Stream.empty();
                }
            })
            .collect(Collectors.toList());
    }
}
```

### Resource-Driven AI Pattern

**AI service that utilizes MCP resources for context enhancement:**
```java
@Service
public class ResourceDrivenAIService {

    private final McpClient mcpClient;
    private final ChatModel chatModel;

    public String chatWithContext(String message, List<String> resourceUris) {
        // Gather context from resources
        String context = resourceUris.stream()
            .map(uri -> {
                try {
                    return mcpClient.getResource(uri);
                } catch (Exception e) {
                    return "Failed to load resource: " + uri;
                }
            })
            .collect(Collectors.joining("\n\n"));

        // Create enhanced prompt with context
        String enhancedMessage = String.format(
            "Context:\n%s\n\nUser Question: %s", context, message);

        // Create AI service with resource tools
        McpToolProvider toolProvider = McpToolProvider.builder()
            .mcpClients(mcpClient)
            .build();

        AIAssistant assistant = AiServices.builder(AIAssistant.class)
            .chatModel(chatModel)
            .toolProvider(toolProvider)
            .build();

        return assistant.chat(enhancedMessage);
    }
}
```

## Best Practices

### 1. Use Proper Resource Management

Always close MCP clients to prevent resource leaks.

```java
// Good - Using try-with-resources
try (McpClient mcpClient = new DefaultMcpClient.Builder()
        .transport(transport)
        .build()) {
    // Use client
} // Automatically closed

// Good - Spring bean with @PreDestroy
@Component
public class McpClientManager {
    private final List<McpClient> clients = new ArrayList<>();

    @PreDestroy
    public void cleanup() {
        clients.forEach(client -> {
            try {
                client.close();
            } catch (Exception e) {
                log.warn("Failed to close MCP client: {}", e.getMessage());
            }
        });
    }
}
```

### 2. Implement Proper Error Handling

Handle MCP server failures gracefully with appropriate fallback strategies.

```java
// Good - Graceful failure handling
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(primaryClient, fallbackClient)
    .failIfOneServerFails(false)  // Continue with available servers
    .build();

// Good - Custom error handling
public class SafeMcpExecutor {
    public Optional<String> executeTool(McpClient client, ToolExecutionRequest request) {
        try {
            return Optional.of(client.executeTool(request));
        } catch (McpException e) {
            log.error("MCP tool execution failed: {}", e.getMessage());
            return Optional.empty();
        }
    }
}
```

### 3. Use Tool Filtering for Security

Implement security-conscious tool filtering to prevent unauthorized access.

```java
// Good - Security-aware filtering
McpToolProvider secureProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .filter((client, tool) -> {
        // Check user permissions
        if (tool.name().startsWith("admin_") && !currentUser.hasRole("ADMIN")) {
            return false;
        }

        // Check sensitive operations
        if (tool.name().contains("delete") && !currentUser.canDelete()) {
            return false;
        }

        return true;
    })
    .build();
```

### 4. Cache Tools Appropriately

Use caching to improve performance while ensuring freshness.

```java
// Good - Balanced caching strategy
McpClient mcpClient = new DefaultMcpClient.Builder()
    .transport(transport)
    .cacheToolList(true)  // Cache for performance
    .build();

// Good - Refresh cache periodically
@Scheduled(fixedRate = 300000) // 5 minutes
public void refreshToolCache() {
    mcpClients.forEach(client -> {
        try {
            client.invalidateCache();
            client.listTools(); // Preload cache
        } catch (Exception e) {
            log.warn("Failed to refresh cache for client {}: {}",
                    client.key(), e.getMessage());
        }
    });
}
```

### 5. Use Structured Configuration

Organize MCP configuration for maintainability and flexibility.

```java
// Good - Structured configuration
@ConfigurationProperties(prefix = "ai.mcp")
public class McpConfiguration {
    private boolean enabled = true;
    private Map<String, ServerConfig> servers = new HashMap<>();
    private ToolFilterConfig toolFilter = new ToolFilterConfig();
    private RetryConfig retry = new RetryConfig();

    // Nested configuration classes for better organization
    public static class ServerConfig {
        private String type;
        private List<String> command;
        private String url;
        private boolean logEvents = false;
        // getters/setters
    }

    public static class ToolFilterConfig {
        private List<String> allowedPrefixes = List.of();
        private List<String> blockedPrefixes = List.of("admin_", "system_");
        // getters/setters
    }
}
```

### 6. Implement Health Checks

Monitor MCP server health and availability.

```java
// Good - Health check implementation
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

### 7. Use Observability

Implement comprehensive logging and monitoring.

```java
// Good - Comprehensive observability
@Component
public class ObservableMcpService {

    private final MeterRegistry meterRegistry;
    private final Counter toolExecutionCounter;
    private final Timer toolExecutionTimer;

    public String executeTool(String toolName, String arguments) {
        return Timer.Sample.start(meterRegistry)
            .stop(toolExecutionTimer.tag("tool", toolName))
            .recordCallable(() -> {
                toolExecutionCounter.increment(Tags.of("tool", toolName));
                return mcpClient.executeTool(
                    ToolExecutionRequest.builder()
                        .name(toolName)
                        .arguments(arguments)
                        .build()
                );
            });
    }
}
```

### 8. Design for Scalability

Structure your MCP integration to scale with multiple servers and high load.

```java
// Good - Scalable design
@Configuration
public class ScalableMcpConfiguration {

    @Bean
    public Executor mcpExecutor() {
        return Executors.newFixedThreadPool(10); // Dedicated thread pool
    }

    @Bean
    public LoadBalancer<McpClient> mcpLoadBalancer(List<McpClient> clients) {
        return new RoundRobinLoadBalancer<>(clients);
    }

    @Bean
    public McpToolProvider scalableToolProvider(LoadBalancer<McpClient> loadBalancer) {
        return new LoadBalancedMcpToolProvider(loadBalancer);
    }
}
```

### 9. Version Management

Handle MCP server versioning and compatibility.

```java
// Good - Version-aware client
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

### 10. Test MCP Integration

Implement comprehensive testing strategies for MCP integrations.

```java
// Good - Comprehensive testing
@TestConfiguration
public class MockMcpConfiguration {

    @Bean
    @Primary
    public McpClient mockMcpClient() {
        McpClient mock = Mockito.mock(McpClient.class);

        // Setup common tool responses
        when(mock.listTools()).thenReturn(List.of(
            ToolSpecification.builder()
                .name("test_tool")
                .description("Test tool for integration tests")
                .build()
        ));

        when(mock.executeTool(any(ToolExecutionRequest.class)))
            .thenReturn("Mock tool execution result");

        return mock;
    }
}

@SpringBootTest
class McpIntegrationTest {

    @Autowired
    private AIAssistant assistant;

    @Test
    void shouldExecuteToolsSuccessfully() {
        String response = assistant.chat("Execute test tool");

        assertThat(response).contains("Mock tool execution result");
    }
}
```

## Summary

This LangChain4j MCP Server integration skill covers:

1. **Model Context Protocol Fundamentals**: Understanding MCP architecture, components, and benefits
2. **Transport Configuration**: Setting up stdio, HTTP, and Docker-based MCP connections
3. **Client Management**: Creating, configuring, and managing MCP clients with proper lifecycle handling
4. **Tool Provider Patterns**: Bridging MCP servers to LangChain4j AI services with filtering and error handling
5. **AI Service Integration**: Seamless integration of MCP tools with LangChain4j AI services and Spring Boot
6. **Resource Handling**: Working with MCP resources for context enhancement and data access
7. **Enterprise Patterns**: Configuration management, security filtering, and scalable architectures
8. **Error Handling**: Resilient patterns for handling MCP server failures and network issues
9. **Observability**: Monitoring, logging, and health checking for production deployments
10. **Best Practices**: Security, performance, testing, and maintenance considerations

The patterns and examples are based on official LangChain4j documentation (Trust Score: 7.8) and MCP specification, representing modern AI integration practices for enterprise Java applications.