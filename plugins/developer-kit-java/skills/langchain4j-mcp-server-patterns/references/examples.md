# LangChain4j MCP Server Implementation Examples

This document provides comprehensive, production-ready examples for implementing MCP servers with LangChain4j.

## Basic MCP Server Setup

### Simple MCP Server Implementation

Create a basic MCP server with single tool functionality:

```java
import dev.langchain4j.mcp.MCPServer;
import dev.langchain4j.mcp.ToolProvider;
import dev.langchain4j.mcp.server.StdioServer;

public class BasicMcpServer {

    public static void main(String[] args) {
        MCPServer server = MCPServer.builder()
            .server(new StdioServer.Builder())
            .addToolProvider(new SimpleWeatherToolProvider())
            .build();

        // Start the server
        server.start();
    }
}

class SimpleWeatherToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(ToolSpecification.builder()
            .name("get_weather")
            .description("Get weather information for a city")
            .inputSchema(Map.of(
                "type", "object",
                "properties", Map.of(
                    "city", Map.of(
                        "type", "string",
                        "description", "City name to get weather for"
                    )
                ),
                "required", List.of("city")
            ))
            .build());
    }

    @Override
    public String executeTool(String name, String arguments) {
        if ("get_weather".equals(name)) {
            JsonObject args = JsonParser.parseString(arguments).getAsJsonObject();
            String city = args.get("city").getAsString();

            // Simulate weather API call
            return String.format("Weather in %s: Sunny, 22°C", city);
        }
        throw new UnsupportedOperationException("Unknown tool: " + name);
    }
}
```

### Spring Boot MCP Server Integration

Integrate MCP server with Spring Boot application:

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class McpSpringBootApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpSpringBootApplication.class, args);
    }

    @Bean
    public MCPServer mcpServer() {
        return MCPServer.builder()
            .server(new StdioServer.Builder())
            .addToolProvider(new DatabaseToolProvider())
            .addToolProvider(new FileToolProvider())
            .build();
    }
}

@Component
class DatabaseToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(ToolSpecification.builder()
            .name("query_database")
            .description("Execute SQL queries against the database")
            .inputSchema(Map.of(
                "type", "object",
                "properties", Map.of(
                    "sql", Map.of(
                        "type", "string",
                        "description", "SQL query to execute"
                    )
                ),
                "required", List.of("sql")
            ))
            .build());
    }

    @Override
    public String executeTool(String name, String arguments) {
        if ("query_database".equals(name)) {
            JsonObject args = JsonParser.parseString(arguments).getAsJsonObject();
            String sql = args.get("sql").getAsString();

            // Execute database query
            return executeDatabaseQuery(sql);
        }
        throw new UnsupportedOperationException("Unknown tool: " + name);
    }

    private String executeDatabaseQuery(String sql) {
        // Implementation using Spring Data JPA
        try {
            return jdbcTemplate.queryForObject(sql, String.class);
        } catch (Exception e) {
            return "Error executing query: " + e.getMessage();
        }
    }
}
```

## Multi-Tool MCP Server

### Enterprise MCP Server with Multiple Tools

Create a comprehensive MCP server with multiple tool providers:

```java
@Component
public class EnterpriseMcpServer {

    @Bean
    public MCPServer enterpriseMcpServer(
            GitHubToolProvider githubToolProvider,
            DatabaseToolProvider databaseToolProvider,
            FileToolProvider fileToolProvider,
            EmailToolProvider emailToolProvider) {

        return MCPServer.builder()
            .server(new StdioServer.Builder())
            .addToolProvider(githubToolProvider)
            .addToolProvider(databaseToolProvider)
            .addToolProvider(fileToolProvider)
            .addToolProvider(emailToolProvider)
            .enableLogging(true)
            .setLogHandler(new CustomLogHandler())
            .build();
    }
}

@Component
class GitHubToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(
            ToolSpecification.builder()
                .name("get_issue")
                .description("Get GitHub issue details")
                .inputSchema(Map.of(
                    "type", "object",
                    "properties", Map.of(
                        "owner", Map.of(
                            "type", "string",
                            "description", "Repository owner"
                        ),
                        "repo", Map.of(
                            "type", "string",
                            "description", "Repository name"
                        ),
                        "issue_number", Map.of(
                            "type", "integer",
                            "description", "Issue number"
                        )
                    ),
                    "required", List.of("owner", "repo", "issue_number")
                ))
                .build(),
            ToolSpecification.builder()
                .name("list_issues")
                .description("List GitHub issues for a repository")
                .inputSchema(Map.of(
                    "type", "object",
                    "properties", Map.of(
                        "owner", Map.of(
                            "type", "string",
                            "description", "Repository owner"
                        ),
                        "repo", Map.of(
                            "type", "string",
                            "description", "Repository name"
                        ),
                        "state", Map.of(
                            "type", "string",
                            "description", "Issue state: open, closed, all",
                            "enum", List.of("open", "closed", "all")
                        )
                    ),
                    "required", List.of("owner", "repo")
                ))
                .build()
        );
    }

    @Override
    public String executeTool(String name, String arguments) {
        switch (name) {
            case "get_issue":
                return getIssueDetails(arguments);
            case "list_issues":
                return listRepositoryIssues(arguments);
            default:
                throw new UnsupportedOperationException("Unknown tool: " + name);
        }
    }

    private String getIssueDetails(String arguments) {
        JsonObject args = JsonParser.parseString(arguments).getAsJsonObject();
        String owner = args.get("owner").getAsString();
        String repo = args.get("repo").getAsString();
        int issueNumber = args.get("issue_number").getAsInt();

        // Call GitHub API
        GitHubIssue issue = githubService.getIssue(owner, repo, issueNumber);
        return "Issue #" + issueNumber + ": " + issue.getTitle() +
               "\nState: " + issue.getState() +
               "\nCreated: " + issue.getCreatedAt();
    }

    private String listRepositoryIssues(String arguments) {
        JsonObject args = JsonParser.parseString(arguments).getAsJsonObject();
        String owner = args.get("owner").getAsString();
        String repo = args.get("repo").getAsString();
        String state = args.has("state") ? args.get("state").getAsString() : "open";

        List<GitHubIssue> issues = githubService.listIssues(owner, repo, state);

        return issues.stream()
            .map(issue -> "#%d: %s (%s)".formatted(issue.getNumber(), issue.getTitle(), issue.getState()))
            .collect(Collectors.joining("\n"));
    }
}
```

## Resource Provider Implementation

### Static Resource Provider

Provide static resources for context enhancement:

```java
@Component
class StaticResourceProvider implements ResourceListProvider, ResourceReadHandler {

    private final Map<String, String> resources = new HashMap<>();

    public StaticResourceProvider() {
        // Initialize with static resources
        resources.put("company-policies", loadCompanyPolicies());
        resources.put("api-documentation", loadApiDocumentation());
        resources.put("best-practices", loadBestPractices());
    }

    @Override
    public List<McpResource> listResources() {
        return resources.keySet().stream()
            .map(uri -> McpResource.builder()
                .uri(uri)
                .name(uri.replace("-", " "))
                .description("Documentation resource")
                .mimeType("text/plain")
                .build())
            .collect(Collectors.toList());
    }

    @Override
    public String readResource(String uri) {
        if (!resources.containsKey(uri)) {
            throw new ResourceNotFoundException("Resource not found: " + uri);
        }
        return resources.get(uri);
    }

    private String loadCompanyPolicies() {
        // Load company policies from file or database
        return "Company Policies:\n1. Work hours: 9-5\n2. Security compliance\n3. Data privacy";
    }

    private String loadApiDocumentation() {
        // Load API documentation
        return "API Documentation:\nGET /api/users - List users\nPOST /api/users - Create user";
    }
}
```

### Dynamic Resource Provider

Create dynamic resources that update in real-time:

```java
@Component
class DynamicResourceProvider implements ResourceListProvider, ResourceReadHandler {

    @Autowired
    private MetricsService metricsService;

    @Override
    public List<McpResource> listResources() {
        return List.of(
            McpResource.builder()
                .uri("system-metrics")
                .name("System Metrics")
                .description("Real-time system performance metrics")
                .mimeType("application/json")
                .build(),
            McpResource.builder()
                .uri("user-analytics")
                .name("User Analytics")
                .description("User behavior and usage statistics")
                .mimeType("application/json")
                .build()
        );
    }

    @Override
    public String readResource(String uri) {
        switch (uri) {
            case "system-metrics":
                return metricsService.getCurrentSystemMetrics();
            case "user-analytics":
                return metricsService.getUserAnalytics();
            default:
                throw new ResourceNotFoundException("Resource not found: " + uri);
        }
    }
}
```

## Prompt Template Provider

### Prompt Template Server

Create prompt templates for common AI tasks:

```java
@Component
class PromptTemplateProvider implements PromptListProvider, PromptGetHandler {

    private final Map<String, PromptTemplate> templates = new HashMap<>();

    public PromptTemplateProvider() {
        templates.put("code-review", PromptTemplate.builder()
            .name("Code Review")
            .description("Review code for quality, security, and best practices")
            .template("Review the following code for:\n" +
                     "1. Code quality and readability\n" +
                     "2. Security vulnerabilities\n" +
                     "3. Performance optimizations\n" +
                     "4. Best practices compliance\n\n" +
                     "Code:\n" +
                     "```{code}```\n\n" +
                     "Provide a detailed analysis with specific recommendations.")
            .build());

        templates.put("documentation-generation", PromptTemplate.builder()
            .name("Documentation Generator")
            .description("Generate technical documentation from code")
            .template("Generate comprehensive documentation for the following code:\n" +
                     "{code}\n\n" +
                     "Include:\n" +
                     "1. Function/method signatures\n" +
                     "2. Parameters and return values\n" +
                     "3. Purpose and usage examples\n" +
                     "4. Dependencies and requirements")
            .build());
    }

    @Override
    public List<Prompt> listPrompts() {
        return templates.values().stream()
            .map(template -> Prompt.builder()
                .name(template.getName())
                .description(template.getDescription())
                .build())
            .collect(Collectors.toList());
    }

    @Override
    public String getPrompt(String name, Map<String, String> arguments) {
        PromptTemplate template = templates.get(name);
        if (template == null) {
            throw new PromptNotFoundException("Prompt not found: " + name);
        }

        // Replace template variables
        String content = template.getTemplate();
        for (Map.Entry<String, String> entry : arguments.entrySet()) {
            content = content.replace("{" + entry.getKey() + "}", entry.getValue());
        }

        return content;
    }
}
```

## Error Handling and Validation

### Robust Error Handling

Implement comprehensive error handling and validation:

```java
@Component
class RobustToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(ToolSpecification.builder()
            .name("secure_data_access")
            .description("Access sensitive data with proper validation")
            .inputSchema(Map.of(
                "type", "object",
                "properties", Map.of(
                    "data_type", Map.of(
                        "type", "string",
                        "description", "Type of data to access",
                        "enum", List.of("user_data", "system_data", "admin_data")
                    ),
                    "user_id", Map.of(
                        "type", "string",
                        "description", "User ID requesting access"
                    )
                ),
                "required", List.of("data_type", "user_id")
            ))
            .build());
    }

    @Override
    public String executeTool(String name, String arguments) {
        if ("secure_data_access".equals(name)) {
            try {
                JsonObject args = JsonParser.parseString(arguments).getAsJsonObject();
                String dataType = args.get("data_type").getAsString();
                String userId = args.get("user_id").getAsString();

                // Validate user permissions
                if (!hasPermission(userId, dataType)) {
                    return "Access denied: Insufficient permissions";
                }

                // Get data securely
                return getSecureData(dataType, userId);

            } catch (JsonParseException e) {
                return "Invalid JSON format: " + e.getMessage();
            } catch (Exception e) {
                return "Error accessing data: " + e.getMessage();
            }
        }
        throw new UnsupportedOperationException("Unknown tool: " + name);
    }

    private boolean hasPermission(String userId, String dataType) {
        // Implement permission checking
        if ("admin_data".equals(dataType)) {
            return userRepository.isAdmin(userId);
        }
        return true;
    }

    private String getSecureData(String dataType, String userId) {
        // Implement secure data retrieval
        if ("user_data".equals(dataType)) {
            return userDataService.getUserData(userId);
        }
        return "Data not available";
    }
}
```

## Advanced Server Configuration

### Multi-Transport Server Configuration

Configure MCP server with multiple transport options:

```java
@Configuration
public class AdvancedMcpConfiguration {

    @Bean
    public MCPServer advancedMcpServer(
            List<ToolProvider> toolProviders,
            List<ResourceListProvider> resourceProviders,
            List<PromptListProvider> promptProviders) {

        return MCPServer.builder()
            .server(new StdioServer.Builder())
            .addToolProvider(toolProviders)
            .addResourceProvider(resourceProviders)
            .addPromptProvider(promptProviders)
            .enableLogging(true)
            .setLogHandler(new StructuredLogHandler())
            .enableHealthChecks(true)
            .setHealthCheckInterval(30) // seconds
            .setMaxConcurrentRequests(100)
            .setRequestTimeout(30) // seconds
            .build();
    }

    @Bean
    public HttpMcpTransport httpTransport() {
        return new HttpMcpTransport.Builder()
            .sseUrl("http://localhost:8080/mcp/sse")
            .logRequests(true)
            .logResponses(true)
            .setCorsEnabled(true)
            .setAllowedOrigins(List.of("http://localhost:3000"))
            .build();
    }
}
```

## Client Integration Patterns

### Multi-Client MCP Integration

Integrate with multiple MCP servers for comprehensive functionality:

```java
@Service
public class MultiMcpIntegrationService {

    private final List<McpClient> mcpClients;
    private final ChatModel chatModel;
    private final McpToolProvider toolProvider;

    public MultiMcpIntegrationService(List<McpClient> mcpClients, ChatModel chatModel) {
        this.mcpClients = mcpClients;
        this.chatModel = chatModel;

        // Create tool provider with multiple MCP clients
        this.toolProvider = McpToolProvider.builder()
            .mcpClients(mcpClients)
            .failIfOneServerFails(false) // Continue with available servers
            .filter((client, tool) -> {
                // Implement cross-server tool filtering
                return !tool.name().startsWith("deprecated_");
            })
            .build();
    }

    public String processUserQuery(String userId, String query) {
        // Create AI service with multiple MCP integrations
        AIAssistant assistant = AiServices.builder(AIAssistant.class)
            .chatModel(chatModel)
            .toolProvider(toolProvider)
            .chatMemoryProvider(memoryProvider)
            .build();

        return assistant.chat(userId, query);
    }

    public List<ToolSpecification> getAvailableTools() {
        return mcpClients.stream()
            .flatMap(client -> {
                try {
                    return client.listTools().stream();
                } catch (Exception e) {
                    log.warn("Failed to list tools from client {}: {}", client.key(), e.getMessage());
                    return Stream.empty();
                }
            })
            .distinct()
            .collect(Collectors.toList());
    }
}
```

These comprehensive examples provide a solid foundation for implementing MCP servers with LangChain4j, covering everything from basic setup to advanced enterprise patterns.