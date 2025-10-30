package com.example.mcp;

import dev.langchain4j.mcp.*;
import dev.langchain4j.mcp.transport.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.List;

// Helper imports
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;

/**
 * Template for creating MCP servers with LangChain4j.
 *
 * This template provides a starting point for building MCP servers with:
 * - Tool providers
 * - Resource providers
 * - Prompt providers
 * - Spring Boot integration
 * - Configuration management
 */
@SpringBootApplication
public class MCPServerTemplate {

    public static void main(String[] args) {
        SpringApplication.run(MCPServerTemplate.class, args);
    }

    /**
     * Configure and build the main MCP server instance.
     */
    @Bean
    public MCPServer mcpServer(
            List<ToolProvider> toolProviders,
            List<ResourceListProvider> resourceProviders,
            List<PromptListProvider> promptProviders) {

        return MCPServer.builder()
            .server(new StdioServer.Builder())
            .addToolProvider(toolProviders)
            .addResourceProvider(resourceProviders)
            .addPromptProvider(promptProviders)
            .enableLogging(true)
            .build();
    }

    /**
     * Configure MCP clients for connecting to external MCP servers.
     */
    @Bean
    public McpClient mcpClient() {
        StdioMcpTransport transport = new StdioMcpTransport.Builder()
            .command(List.of("npm", "exec", "@modelcontextprotocol/server-everything@0.6.2"))
            .logEvents(true)
            .build();

        return new DefaultMcpClient.Builder()
            .key("template-client")
            .transport(transport)
            .cacheToolList(true)
            .build();
    }

    /**
     * Configure MCP tool provider for AI services integration.
     */
    @Bean
    public McpToolProvider mcpToolProvider(McpClient mcpClient) {
        return McpToolProvider.builder()
            .mcpClients(mcpClient)
            .failIfOneServerFails(false)
            .build();
    }
}

/**
 * Example tool provider implementing a simple calculator.
 */
class CalculatorToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(
            ToolSpecification.builder()
                .name("add")
                .description("Add two numbers")
                .inputSchema(Map.of(
                    "type", "object",
                    "properties", Map.of(
                        "a", Map.of("type", "number", "description", "First number"),
                        "b", Map.of("type", "number", "description", "Second number")
                    ),
                    "required", List.of("a", "b")
                ))
                .build(),
            ToolSpecification.builder()
                .name("multiply")
                .description("Multiply two numbers")
                .inputSchema(Map.of(
                    "type", "object",
                    "properties", Map.of(
                        "a", Map.of("type", "number", "description", "First number"),
                        "b", Map.of("type", "number", "description", "Second number")
                    ),
                    "required", List.of("a", "b")
                ))
                .build()
        );
    }

    @Override
    public String executeTool(String name, String arguments) {
        try {
            // Parse JSON arguments
            ObjectMapper mapper = new ObjectMapper();
            JsonNode argsNode = mapper.readTree(arguments);
            double a = argsNode.get("a").asDouble();
            double b = argsNode.get("b").asDouble();

            switch (name) {
                case "add":
                    return String.valueOf(a + b);
                case "multiply":
                    return String.valueOf(a * b);
                default:
                    throw new UnsupportedOperationException("Unknown tool: " + name);
            }
        } catch (Exception e) {
            return "Error executing tool: " + e.getMessage();
        }
    }
}

/**
 * Example resource provider for static company information.
 */
class CompanyResourceProvider implements ResourceListProvider, ResourceReadHandler {

    @Override
    public List<McpResource> listResources() {
        return List.of(
            McpResource.builder()
                .uri("company-info")
                .name("Company Information")
                .description("Basic company details and contact information")
                .mimeType("text/plain")
                .build(),
            McpResource.builder()
                .uri("policies")
                .name("Company Policies")
                .description("Company policies and procedures")
                .mimeType("text/markdown")
                .build()
        );
    }

    @Override
    public String readResource(String uri) {
        switch (uri) {
            case "company-info":
                return loadCompanyInfo();
            case "policies":
                return loadPolicies();
            default:
                throw new ResourceNotFoundException("Resource not found: " + uri);
        }
    }

    private String loadCompanyInfo() {
        return """
        Company Information:
        ===================

        Name: Example Corporation
        Founded: 2020
        Industry: Technology
        Employees: 100+

        Contact:
        - Email: info@example.com
        - Phone: +1-555-0123
        - Website: https://example.com

        Mission: To deliver innovative AI solutions
        """;
    }

    private String loadPolicies() {
        return """
        Company Policies:
        =================

        1. Code of Conduct
        - Treat all team members with respect
        - Maintain professional communication
        - Report any concerns to management

        2. Security Policy
        - Use strong passwords
        - Enable 2FA when available
        - Report security incidents immediately

        3. Work Environment
        - Flexible working hours
        - Remote work options
        - Support for continuous learning
        """;
    }
}

/**
 * Example prompt template provider for common AI tasks.
 */
class PromptTemplateProvider implements PromptListProvider, PromptGetHandler {

    @Override
    public List<Prompt> listPrompts() {
        return List.of(
            Prompt.builder()
                .name("code-review")
                .description("Review code for quality, security, and best practices")
                .build(),
            Prompt.builder()
                .name("documentation-generation")
                .description("Generate technical documentation from code")
                .build(),
            Prompt.builder()
                .name("bug-analysis")
                .description("Analyze and explain potential bugs in code")
                .build()
        );
    }

    @Override
    public String getPrompt(String name, Map<String, String> arguments) {
        switch (name) {
            case "code-review":
                return createCodeReviewPrompt(arguments);
            case "documentation-generation":
                return createDocumentationPrompt(arguments);
            case "bug-analysis":
                return createBugAnalysisPrompt(arguments);
            default:
                throw new PromptNotFoundException("Prompt not found: " + name);
        }
    }

    private String createCodeReviewPrompt(Map<String, String> args) {
        String code = args.getOrDefault("code", "");
        String language = args.getOrDefault("language", "unknown");

        return String.format("""
        Review the following %s code for quality, security, and best practices:

        ```%s
        %s
        ```

        Please analyze:
        1. Code quality and readability
        2. Security vulnerabilities
        3. Performance optimizations
        4. Best practices compliance
        5. Error handling

        Provide specific recommendations for improvements.
        """, language, language, code);
    }

    private String createDocumentationPrompt(Map<String, String> args) {
        String code = args.getOrDefault("code", "");
        String component = args.getOrDefault("component", "function");

        return String.format("""
        Generate comprehensive documentation for the following %s:

        ```%s
        %s
        ```

        Include:
        1. Function/method signatures
        2. Parameters and return values
        3. Purpose and usage examples
        4. Dependencies and requirements
        5. Error conditions and handling
        """, component, "java", code);
    }

    private String createBugAnalysisPrompt(Map<String, String> args) {
        String code = args.getOrDefault("code", "");

        return String.format("""
        Analyze the following code for potential bugs and issues:

        ```java
        %s
        ```

        Look for:
        1. Null pointer exceptions
        2. Logic errors
        3. Resource leaks
        4. Race conditions
        5. Edge cases
        6. Type mismatches

        Explain each issue found and suggest fixes.
        """, code);
    }
}