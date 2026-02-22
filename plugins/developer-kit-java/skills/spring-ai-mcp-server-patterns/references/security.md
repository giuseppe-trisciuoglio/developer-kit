# Spring AI MCP Server - Security Patterns

## Method-Level Authorization for Tools

Apply authorization directly on MCP tools.

```java
@Component
@Validated
public class AdminTools {

    @McpTool(description = "Delete an order by id")
    @PreAuthorize("hasRole('ADMIN')")
    public DeleteResult deleteOrder(
            @McpToolParam(description = "Order id", required = true)
            @NotBlank String orderId) {

        // call service layer with audited delete
        return new DeleteResult(orderId, true);
    }
}

record DeleteResult(String orderId, boolean deleted) {}
```

## Input Validation and Sanitization

```java
@Component
@Validated
public class QueryTools {

    @McpTool(description = "Run a read-only query")
    public QueryResult executeReadOnlyQuery(
            @McpToolParam(description = "SQL query", required = true)
            @NotBlank String sql) {

        String normalized = sql.trim().toUpperCase(Locale.ROOT);
        if (!normalized.startsWith("SELECT")) {
            throw new IllegalArgumentException("Only SELECT queries are allowed");
        }

        if (normalized.contains("--") || normalized.contains("/*") || normalized.contains(";")) {
            throw new IllegalArgumentException("Potentially unsafe SQL pattern");
        }

        return new QueryResult(true);
    }
}

record QueryResult(boolean success) {}
```

## Transport Hardening

1. Prefer `STDIO` for local/trusted integration.
2. If using HTTP/SSE/Streamable, enforce authentication and authorization at the Spring Security layer.
3. Put MCP endpoints behind API gateway/reverse proxy policies in production.
4. Keep only required capabilities enabled (`tool`, `resource`, `prompt`, `completion`).

## Error Handling Guidance

1. Return user-safe error messages.
2. Log internal details server-side only.
3. Avoid leaking secrets, stack traces, and internal topology in tool errors.
4. Use consistent error categories (`validation`, `authorization`, `execution-timeout`, `dependency-failure`).
