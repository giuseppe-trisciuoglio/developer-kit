package com.example.mcp.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

/**
 * Template for creating MCP tools with Spring AI.
 *
 * Follow these best practices when creating tools:
 * 1. Use descriptive names and clear descriptions
 * 2. Document all parameters with @ToolParam
 * 3. Implement proper validation
 * 4. Handle errors gracefully
 * 5. Return structured results
 * 6. Consider security implications
 * 7. Add appropriate logging
 * 8. Implement rate limiting if needed
 * 9. Use caching for expensive operations
 * 10. Test thoroughly
 */
@Component
public class ToolTemplate {

    /**
     * Brief description of what this tool does.
     * Make it clear and concise - this is used by AI models
     * to understand when to invoke the tool.
     *
     * Include: What the tool does, expected inputs, return value
     * Example: "Calculate the square root of a positive number"
     */
    @Tool(
        description = "DESCRIPTION: Clear explanation of what this tool does and when to use it"
    )
    public ToolResult exampleTool(
            // Always document parameters with @ToolParam
            @ToolParam("Clear description of what this parameter represents")
            String requiredParam,

            // Use required = false for optional parameters
            @ToolParam(value = "Description of optional parameter", required = false)
            String optionalParam) {

        try {
            // 1. Input validation
            if (requiredParam == null || requiredParam.isBlank()) {
                return ToolResult.error("Required parameter cannot be null or empty");
            }

            // 2. Security validation
            if (containsDangerousContent(requiredParam)) {
                return ToolResult.error("Invalid input: contains dangerous characters");
            }

            // 3. Business logic
            Object result = performOperation(requiredParam, optionalParam);

            // 4. Return structured result
            return ToolResult.success(result);

        } catch (Exception e) {
            // 5. Error handling
            return ToolResult.error("Operation failed: " + e.getMessage());
        }
    }

    /**
     * Tool with complex input/output.
     * Shows how to handle structured data.
     */
    @Tool(
        description = """
            Process user data with validation and enrichment.
            Takes user information, validates it, enriches with additional data,
            and returns processed result.
            Example input: {"name": "John", "email": "john@example.com"}
            """
    )
    public ProcessResult processUserData(
            @ToolParam("User data as JSON string")
            String userDataJson,

            @ToolParam(value = "Perform validation", required = false)
            Boolean validate) {

        try {
            // Parse JSON input
            UserData userData = new ObjectMapper().readValue(userDataJson, UserData.class);

            // Validate if requested
            if (Boolean.TRUE.equals(validate)) {
                validateUserData(userData);
            }

            // Process data
            ProcessResult result = new ProcessResult();
            result.setOriginalData(userData);
            result.setProcessedAt(Instant.now());
            result.setSuccess(true);

            // Enrich with additional data
            enrichUserData(result);

            return result;

        } catch (JsonProcessingException e) {
            return new ProcessResult(null, false, "Invalid JSON format: " + e.getMessage());
        } catch (ValidationException e) {
            return new ProcessResult(null, false, "Validation failed: " + e.getMessage());
        }
    }

    /**
     * Tool that performs expensive operation.
     * Shows caching pattern.
     */
    @Tool(
        description = "Get data from external API with caching"
    )
    @Cacheable(value = "api-data", key = "#cacheKey")
    public ApiData getCachedApiData(
            @ToolParam("API endpoint URL")
            String endpoint,

            @ToolParam("Cache key for storing result")
            String cacheKey,

            @ToolParam(value = "Force refresh cache", required = false)
            Boolean forceRefresh) {

        // If force refresh, evict cache first
        if (Boolean.TRUE.equals(forceRefresh)) {
            Cache cache = cacheManager.getCache("api-data");
            if (cache != null) {
                cache.evict(cacheKey);
            }
        }

        // Perform API call
        return performApiCall(endpoint);
    }

    /**
     * Tool with rate limiting.
     * Shows how to protect against abuse.
     */
    @Tool(
        description = "Perform rate-limited operation"
    )
    @RateLimited(requests = 10, duration = "1m") // 10 requests per minute
    public RateLimitedResult performRateLimitedOperation(
            @ToolParam("Operation type")
            String operation) {

        // Check rate limit first (handled by annotation)
        // Business logic here
        Object result = executeOperation(operation);

        RateLimitedResult response = new RateLimitedResult();
        response.setResult(result);
        response.setRemainingRequests(getRemainingRequests());
        response.setResetTime(getRateLimitResetTime());

        return response;
    }

    /**
     * Async tool execution.
     */
    @Tool(
        description = "Execute long-running task asynchronously"
    )
    public AsyncResult executeAsyncTask(
            @ToolParam("Task name")
            String taskName,

            @ToolParam(value = "Task parameters", required = false)
            String paramsJson) {

        // Generate task ID
        String taskId = UUID.randomUUID().toString();

        // Submit task for async execution
        CompletableFuture.supplyAsync(() -> {
            try {
                return performLongRunningTask(taskName, paramsJson);
            } catch (Exception e) {
                log.error("Async task failed: " + taskId, e);
                return null;
            }
        }, asyncExecutor).thenAccept(result -> {
            // Store result when complete
            taskResults.put(taskId, result);
        });

        // Return immediately with task ID
        return new AsyncResult(taskId, "pending", null);
    }

    /**
     * Tool with security check.
     */
    @Tool(
        description = "Perform sensitive operation requiring admin access"
    )
    @PreAuthorize("hasRole('ADMIN')")
    public AdminResult performAdminOperation(
            @ToolParam("Admin command")
            String command,

            @ToolParam("MFA token")
            String mfaToken) {

        // Verify MFA token
        if (!securityService.verifyMfaToken(mfaToken)) {
            return new AdminResult(false, "Invalid MFA token");
        }

        // Log sensitive operation
        auditService.logAdminOperation(command, getCurrentUser());

        // Execute command
        Object result = executeAdminCommand(command);

        return new AdminResult(true, "Command executed successfully", result);
    }

    // Helper methods

    private boolean containsDangerousContent(String input) {
        String upper = input.toUpperCase();
        return upper.contains("UNION") || upper.contains(";") ||
               upper.contains("DROP") || upper.contains("DELETE") ||
               upper.contains("XP_") || upper.contains("SP_");
    }

    private Object performOperation(String param1, String param2) {
        // Implement actual operation logic
        return Map.of(
            "input1", param1,
            "input2", param2,
            "result", "success"
        );
    }

    private void validateUserData(UserData data) throws ValidationException {
        if (data.getName() == null || data.getName().isBlank()) {
            throw new ValidationException("Name is required");
        }
        if (data.getEmail() != null && !data.getEmail().matches("^[^\s@]+@[^\s@]+\.[^\s@]+$")) {
            throw new ValidationException("Invalid email format");
        }
    }

    private void enrichUserData(ProcessResult result) {
        // Add calculated fields, references, etc.
        result.setMetadata(Map.of(
            "enrichedAt", Instant.now(),
            "version", "1.0",
            "sourceSystem", "mcp-server"
        ));
    }

    private Object performLongRunningTask(String taskName, String paramsJson) {
        // Simulate long-running task
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return Map.of("taskName", taskName, "status", "completed");
    }

    // Helper classes

    @Data
    public static class ToolResult {
        private boolean success;
        private Object data;
        private String error;

        public static ToolResult success(Object data) {
            ToolResult result = new ToolResult();
            result.setSuccess(true);
            result.setData(data);
            return result;
        }

        public static ToolResult error(String error) {
            ToolResult result = new ToolResult();
            result.setSuccess(false);
            result.setError(error);
            return result;
        }
    }

    @Data
    public static class UserData {
        private String name;
        private String email;
        private Map<String, Object> additionalData;
    }

    @Data
    public static class ProcessResult {
        private UserData originalData;
        private Object enrichedData;
        private Instant processedAt;
        private boolean success;
        private String error;
        private Map<String, Object> metadata;

        @JsonCreator
        public ProcessResult() {}

        public ProcessResult(UserData originalData, boolean success, String error) {
            this.originalData = originalData;
            this.success = success;
            this.error = error;
        }
    }

    @Data
    public static class ApiData {
        private Map<String, Object> data;
        private Instant fetchedAt;
        private String source;
    }

    @Data
    public static class RateLimitedResult {
        private Object result;
        private int remainingRequests;
        private Instant resetTime;
    }

    @Data
    public static class AsyncResult {
        private String taskId;
        private String status;
        private Object result;
    }

    @Data
    public static class AdminResult {
        private boolean success;
        private String message;
        private Object data;

        public AdminResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }

        public AdminResult(boolean success, String message, Object data) {
            this.success = success;
            this.message = message;
            this.data = data;
        }
    }

    // Dependencies (inject these via constructor)
    private final ObjectMapper objectMapper;
    private final CacheManager cacheManager;
    private final Executor asyncExecutor;
    private final Map<String, Object> taskResults;
    private final SecurityService securityService;
    private final AuditService auditService;

    // Validation exception
    public static class ValidationException extends Exception {
        public ValidationException(String message) {
            super(message);
        }
    }

    // Rate limiting annotation
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface RateLimited {
        int requests()
    default 10;
        String duration() default "1m";
        String limitBy() default "user";
    }
}
