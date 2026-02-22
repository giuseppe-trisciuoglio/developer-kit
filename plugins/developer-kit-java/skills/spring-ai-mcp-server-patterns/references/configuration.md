# Spring AI MCP Server - Configuration Reference

## Auto-Configuration

```java
@Configuration
@AutoConfigureAfter({WebMvcAutoConfiguration.class})
@ConditionalOnClass({McpServer.class, ChatModel.class})
@ConditionalOnProperty(name = "spring.ai.mcp.enabled", havingValue = "true", matchIfMissing = true)
public class McpAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public McpServerProperties mcpServerProperties() {
        return new McpServerProperties();
    }

    @Bean
    @ConditionalOnMissingBean
    public McpServer mcpServer(
            List<FunctionCallback> functionCallbacks,
            List<PromptTemplate> promptTemplates,
            McpServerProperties properties
    ) {
        McpServer.Builder builder = McpServer.builder()
                .serverInfo("spring-ai-mcp", "1.0.0")
                .transport(properties.getTransport().create());

        functionCallbacks.forEach(callback ->
                builder.tool(Tool.fromFunctionCallback(callback)));

        promptTemplates.forEach(template ->
                builder.prompt(Prompt.fromTemplate(template)));

        return builder.build();
    }

    @Bean
    @ConditionalOnProperty(name = "spring.ai.mcp.actuator.enabled", havingValue = "true")
    public McpHealthIndicator mcpHealthIndicator(McpServer mcpServer) {
        return new McpHealthIndicator(mcpServer);
    }
}

@ConfigurationProperties(prefix = "spring.ai.mcp")
public class McpServerProperties {
    private boolean enabled = true;
    private TransportConfig transport = new TransportConfig();
    private ActuatorConfig actuator = new ActuatorConfig();

    public static class TransportConfig {
        private TransportType type = TransportType.STDIO;
        private HttpConfig http = new HttpConfig();

        public Transport create() {
            return switch (type) {
                case STDIO -> new StdioTransport();
                case HTTP -> new HttpTransport(http.getPort());
                case SSE -> new SseTransport(http.getPort(), http.getPath());
            };
        }
    }

    public static class HttpConfig {
        private int port = 8080;
        private String path = "/mcp";
    }

    public static class ActuatorConfig {
        private boolean enabled = true;
    }

    public enum TransportType {
        STDIO, HTTP, SSE
    }
}
```

## Application Properties

Configure MCP server in `application.yml`:

```yaml
spring:
  ai:
    mcp:
      enabled: true
      transport:
        type: stdio  # Options: stdio, http, sse
        http:
          port: 8080
          path: /mcp
      actuator:
        enabled: true
      tools:
        package-scan: com.example.tools
      prompts:
        package-scan: com.example.prompts
      security:
        enabled: true
        allowed-tools:
          - getWeather
          - executeQuery
        admin-tools:
          - admin_*
```

## Custom Server Configuration

```java
@Configuration
public class CustomMcpConfig {

    @Bean
    public McpServerCustomizer mcpServerCustomizer() {
        return server -> {
            server.addToolInterceptor((tool, args, chain) -> {
                log.info("Executing tool: {}", tool.name());
                long start = System.currentTimeMillis();
                Object result = chain.execute(tool, args);
                long duration = System.currentTimeMillis() - start;
                log.info("Tool {} executed in {}ms", tool.name(), duration);
                metrics.recordToolExecution(tool.name(), duration);
                return result;
            });
        };
    }

    @Bean
    public ToolFilter toolFilter(SecurityService securityService) {
        return (tool, context) -> {
            User user = securityService.getCurrentUser();
            if (tool.name().startsWith("admin_")) {
                return user.hasRole("ADMIN");
            }
            return securityService.isToolAllowed(user, tool.name());
        };
    }
}
```

## Complete Application Properties

```properties
# Spring AI Configuration
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.options.model=gpt-4o-mini
spring.ai.openai.chat.options.temperature=0.7

# MCP Server Configuration
spring.ai.mcp.enabled=true
spring.ai.mcp.server.name=spring-ai-mcp-server
spring.ai.mcp.server.version=1.0.0
spring.ai.mcp.transport.type=stdio

# HTTP Transport (if enabled)
spring.ai.mcp.transport.http.port=8080
spring.ai.mcp.transport.http.path=/mcp
spring.ai.mcp.transport.http.cors.enabled=true
spring.ai.mcp.transport.http.cors.allowed-origins=*

# Security Configuration
spring.ai.mcp.security.enabled=true
spring.ai.mcp.security.authorization.mode=role-based
spring.ai.mcp.security.authorization.default-deny=true
spring.ai.mcp.security.audit.enabled=true

# Tool Configuration
spring.ai.mcp.tools.package-scan=com.example.mcp.tools
spring.ai.mcp.tools.validation.enabled=true
spring.ai.mcp.tools.validation.max-execution-time=30s
spring.ai.mcp.tools.caching.enabled=true
spring.ai.mcp.tools.caching.ttl=5m

# Prompt Configuration
spring.ai.mcp.prompts.package-scan=com.example.mcp.prompts
spring.ai.mcp.prompts.caching.enabled=true
spring.ai.mcp.prompts.caching.ttl=1h

# Actuator and Monitoring
spring.ai.mcp.actuator.enabled=true
spring.ai.mcp.metrics.enabled=true
spring.ai.mcp.metrics.export.prometheus.enabled=true

# Performance Tuning
spring.ai.mcp.thread-pool.core-size=10
spring.ai.mcp.thread-pool.max-size=50
spring.ai.mcp.thread-pool.queue-capacity=100
spring.ai.mcp.rate-limiter.enabled=true
spring.ai.mcp.rate-limiter.requests-per-minute=100
```

## Application YAML (Complete Example)

```yaml
spring:
  application:
    name: weather-mcp-server
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
        name: weather-mcp-server
        version: 1.0.0
      transport:
        type: stdio
        http:
          port: 8080
          path: /mcp
          cors:
            enabled: true
            allowed-origins: "*"
      security:
        enabled: true
        authorization:
          mode: role-based
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
      actuator:
        enabled: true

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
