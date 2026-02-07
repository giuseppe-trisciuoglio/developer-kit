# Spring AI MCP Server Examples

Comprehensive examples for implementing MCP servers with Spring AI.

## Table of Contents

1. [Basic MCP Server Setup](#basic-mcp-server-setup)
2. [Database Query Tools](#database-query-tools)
3. [API Integration Tools](#api-integration-tools)
4. [File System Tools](#file-system-tools)
5. [Business Logic Tools](#business-logic-tools)
6. [Multi-Modal Tools](#multi-modal-tools)
7. [Secure Enterprise Tools](#secure-enterprise-tools)
8. [Real-Time Streaming](#real-time-streaming)
9. [Dynamic Tool Registration](#dynamic-tool-registration)
10. [Complete Application](#complete-application)

## Basic MCP Server Setup

### Minimal Spring Boot MCP Server

```java
@SpringBootApplication
@EnableMcpServer
public class SimpleMcpApplication {

    public static void main(String[] args) {
        SpringApplication.run(SimpleMcpApplication.class, args);
    }
}

@Component
class CalculatorTools {

    @Tool(description = "Add two numbers")
    public double add(
            @ToolParam("First number") double a,
            @ToolParam("Second number") double b) {
        return a + b;
    }

    @Tool(description = "Multiply two numbers")
    public double multiply(
            @ToolParam("First number") double a,
            @ToolParam("Second number") double b) {
        return a * b;
    }

    @Tool(description = "Calculate the square root")
    public double sqrt(@ToolParam("Number") double x) {
        if (x < 0) {
            throw new IllegalArgumentException("Cannot calculate square root of negative number");
        }
        return Math.sqrt(x);
    }
}

// application.properties
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.mcp.enabled=true
spring.ai.mcp.transport.type=stdio
```

### HTTP Transport Setup

```java
@SpringBootApplication
public class HttpMcpApplication {

    public static void main(String[] args) {
        SpringApplication.run(HttpMcpApplication.class, args);
    }

    @Bean
    public McpServer mcpServer(List<FunctionCallback> callbacks) {
        return McpServer.builder()
                .transport(HttpTransport.builder()
                        .port(8080)
                        .path("/mcp")
                        .cors(CorsConfig.builder()
                                .allowedOrigins("*")
                                .build())
                        .build())
                .tools(callbacks.stream()
                        .map(Tool::fromFunctionCallback)
                        .toList())
                .build();
    }
}
```

### Multi-Transport Server

```java
@Component
public class MultiTransportMcpServer {

    private final McpServer stdioServer;
    private final McpServer httpServer;

    public MultiTransportMcpServer(List<Tool> tools) {
        this.stdioServer = McpServer.builder()
                .transport(new StdioTransport())
                .tools(tools)
                .build();

        this.httpServer = McpServer.builder()
                .transport(HttpTransport.builder()
                        .port(8081)
                        .path("/mcp")
                        .build())
                .tools(tools)
                .build();
    }

    @PostConstruct
    public void start() {
        // Start both servers
        new Thread(stdioServer::start).start();
        new Thread(httpServer::start).start();
    }
}
```

## Database Query Tools

### PostgreSQL Query Tool

```java
@Component
public class PostgreSqlTools {

    private final JdbcTemplate jdbcTemplate;

    public PostgreSqlTools(DataSource dataSource) {
        this.jdbcTemplate = new JdbcTemplate(dataSource);
    }

    @Tool(description = "Execute a read-only SQL query on PostgreSQL database")
    public QueryResult executeReadOnlyQuery(
            @ToolParam("SQL SELECT query") String query,
            @ToolParam(value = "Query parameters as JSON object", required = false)
            String paramsJson) {

        // Security: Only allow SELECT queries
        String normalizedQuery = query.trim().toUpperCase();
        if (!normalizedQuery.startsWith("SELECT")) {
            throw new SecurityException("Only SELECT queries are allowed");
        }

        // Security: Check for dangerous patterns
        if (normalizedQuery.contains(";") && !normalizedQuery.endsWith(";")) {
            throw new SecurityException("Multiple statements are not allowed");
        }

        try {
            Map<String, Object> params = paramsJson != null && !paramsJson.isBlank()
                    ? new ObjectMapper().readValue(paramsJson, Map.class)
                    : Map.of();

            List<Map<String, Object>> results = jdbcTemplate.queryForList(query, params);
            int rowCount = results.size();

            return new QueryResult(true, results, null, "Query returned " + rowCount + " rows");

        } catch (DataAccessException e) {
            return new QueryResult(false, null, e.getMessage(), "Query execution failed");
        } catch (JsonProcessingException e) {
            return new QueryResult(false, null, e.getMessage(), "Invalid parameters JSON");
        }
    }

    @Tool(description = "Get database schema information")
    public SchemaInfo getDatabaseSchema(
            @ToolParam(value = "Table name filter", required = false)
            String tableFilter) {

        String sql = """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            """;

        if (tableFilter != null && !tableFilter.isBlank()) {
            sql += " AND table_name LIKE ?";
            return new SchemaInfo(jdbcTemplate.queryForList(sql, "%" + tableFilter + "%"));
        }

        return new SchemaInfo(jdbcTemplate.queryForList(sql));
    }

    @Tool(description = "Get query execution plan")
    public ExecutionPlan explainQuery(
            @ToolParam("SQL query to analyze") String query) {

        String explainSql = "EXPLAIN (FORMAT JSON, ANALYZE) " + query;
        List<Map<String, Object>> plan = jdbcTemplate.queryForList(explainSql);

        return new ExecutionPlan(query, plan);
    }

    @Tool(description = "Get database statistics")
    public DatabaseStats getDatabaseStats() {
        String sql = """
            SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
            FROM pg_stat_user_tables
            ORDER BY n_tup_ins DESC
            LIMIT 10
            """;

        return new DatabaseStats(jdbcTemplate.queryForList(sql));
    }
}

record QueryResult(boolean success, List<Map<String, Object>> data, String error, String message) {}
record SchemaInfo(List<Map<String, Object>> columns) {}
record ExecutionPlan(String query, List<Map<String, Object>> plan) {}
record DatabaseStats(List<Map<String, Object>> stats) {}
```

### MongoDB Query Tool

```java
@Component
public class MongoDbTools {

    private final MongoTemplate mongoTemplate;

    public MongoDbTools(MongoTemplate mongoTemplate) {
        this.mongoTemplate = mongoTemplate;
    }

    @Tool(description = "Execute a MongoDB find query")
    public MongoResult findDocuments(
            @ToolParam("Collection name") String collection,
            @ToolParam(value = "Query filter as JSON", required = false)
            String filterJson,
            @ToolParam(value = "Maximum documents to return", required = false)
            Integer limit) {

        try {
            Query query = new Query();

            if (filterJson != null && !filterJson.isBlank()) {
                Document filter = Document.parse(filterJson);
                query.addCriteria(Criteria.byExample(filter));
            }

            if (limit != null) {
                query.limit(limit);
            }

            List<Document> results = mongoTemplate.find(query, Document.class, collection);

            return new MongoResult(true, results, null);

        } catch (Exception e) {
            return new MongoResult(false, null, e.getMessage());
        }
    }

    @Tool(description = "Get collection statistics")
    public CollectionStats getCollectionStats(
            @ToolParam("Collection name") String collection) {

        MongoCollection<Document> coll = mongoTemplate.getCollection(collection);
        long count = coll.countDocuments();

        return new CollectionStats(collection, count);
    }

    @Tool(description = "List all collections")
    public List<String> listCollections() {
        return mongoTemplate.getCollectionNames().stream()
                .sorted()
                .toList();
    }

    @Tool(description = "Get collection indexes")
    public List<Document> getIndexes(
            @ToolParam("Collection name") String collection) {

        return mongoTemplate.getCollection(collection)
                .listIndexes()
                .into(new ArrayList<>());
    }
}

record MongoResult(boolean success, List<Document> data, String error) {}
record CollectionStats(String collection, long count) {}
```

### Redis Query Tool

```java
@Component
public class RedisTools {

    private final RedisTemplate<String, Object> redisTemplate;

    public RedisTools(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Tool(description = "Get value from Redis by key")
    public RedisValue getValue(
            @ToolParam("Redis key") String key) {

        Object value = redisTemplate.opsForValue().get(key);

        if (value == null) {
            return new RedisValue(key, null, false);
        }

        String type = determineType(value);
        return new RedisValue(key, value.toString(), type, true);
    }

    @Tool(description = "Get Redis key information")
    public KeyInfo getKeyInfo(
            @ToolParam("Redis key") String key) {

        Long ttl = redisTemplate.getExpire(key);
        String type = redisTemplate.type(key).code();
        Long size = switch (type) {
            case "string" -> redisTemplate.opsForValue().size(key);
            case "list" -> redisTemplate.opsForList().size(key);
            case "set" -> redisTemplate.opsForSet().size(key);
            case "hash" -> (long) redisTemplate.opsForHash().size(key);
            default -> 0L;
        };

        return new KeyInfo(key, type, ttl, size);
    }

    @Tool(description = "Search for keys by pattern")
    public List<String> findKeys(
            @ToolParam("Key pattern (e.g., user:*)") String pattern) {

        Set<String> keys = redisTemplate.keys(pattern);
        return keys != null ? new ArrayList<>(keys) : List.of();
    }

    private String determineType(Object value) {
        if (value instanceof String) return "string";
        if (value instanceof List) return "list";
        if (value instanceof Set) return "set";
        if (value instanceof Map) return "hash";
        return "unknown";
    }
}

record RedisValue(String key, String value, String type, boolean exists) {}
record KeyInfo(String key, String type, Long ttl, Long size) {}
```

## API Integration Tools

### REST API Client Tool

```java
@Component
public class RestApiTools {

    private final WebClient webClient;
    private final CircuitBreakerRegistry circuitBreakerRegistry;

    public RestApiTools(WebClient.Builder builder, CircuitBreakerRegistry registry) {
        this.webClient = builder
                .defaultHeader(HttpHeaders.USER_AGENT, "Spring-AI-MCP-Client/1.0")
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
                .codecs(config -> config.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
        this.circuitBreakerRegistry = registry;
    }

    @Tool(description = "Make HTTP GET request to a REST API")
    public ApiResponse httpGet(
            @ToolParam("URL to request") String url,
            @ToolParam(value = "Headers as JSON object", required = false)
            String headersJson,
            @ToolParam(value = "Timeout in seconds", required = false)
            Integer timeout) {

        // Validate URL
        if (!isValidUrl(url)) {
            return new ApiResponse(0, null, Map.of(), "Invalid URL: " + url);
        }

        CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("http-get");

        return circuitBreaker.executeSupplier(() -> {
            try {
                WebClient.RequestHeadersSpec<?> request = webClient.get()
                        .uri(url)
                        .httpRequest(httpRequest -> {
                            if (timeout != null) {
                                httpRequest.headers(headers ->
                                    headers.setReadTimeout(Duration.ofSeconds(timeout))
                                );
                            }
                        });

                // Add custom headers if provided
                if (headersJson != null && !headersJson.isBlank()) {
                    Map<String, String> headers = new ObjectMapper().readValue(headersJson, Map.class);
                    request.headers(httpHeaders -> headers.forEach(httpHeaders::add));
                }

                ResponseEntity<String> response = request
                        .retrieve()
                        .onStatus(HttpStatus::isError, clientResponse ->
                            Mono.error(new ApiException("HTTP error: " + clientResponse.statusCode()))
                        )
                        .toEntity(String.class)
                        .block();

                if (response == null) {
                    return new ApiResponse(500, null, Map.of(), "No response received");
                }

                String body = response.getBody();
                Object parsedBody = parseResponseBody(body, response.getHeaders().getContentType());

                return new ApiResponse(
                        response.getStatusCode().value(),
                        parsedBody,
                        response.getHeaders().toSingleValueMap(),
                        "Success"
                );

            } catch (Exception e) {
                return new ApiResponse(500, null, Map.of(), "Error: " + e.getMessage());
            }
        });
    }

    @Tool(description = "Make HTTP POST request to a REST API")
    public ApiResponse httpPost(
            @ToolParam("URL to request") String url,
            @ToolParam("Request body as JSON string") String bodyJson,
            @ToolParam(value = "Headers as JSON object", required = false)
            String headersJson) {

        CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("http-post");

        return circuitBreaker.executeSupplier(() -> {
            try {
                WebClient.RequestBodySpec request = webClient.post()
                        .uri(url);

                // Add headers
                if (headersJson != null && !headersJson.isBlank()) {
                    Map<String, String> headers = new ObjectMapper().readValue(headersJson, Map.class);
                    request.headers(httpHeaders -> headers.forEach(httpHeaders::add));
                }

                // Parse and set body
                Object body = parseRequestBody(bodyJson);
                Mono<Object> bodyMono = Mono.justOrEmpty(body);

                ResponseEntity<String> response = request
                        .body(bodyMono, Object.class)
                        .retrieve()
                        .toEntity(String.class)
                        .block();

                if (response == null) {
                    return new ApiResponse(500, null, Map.of(), "No response received");
                }

                Object parsedBody = parseResponseBody(response.getBody(), response.getHeaders().getContentType());

                return new ApiResponse(
                        response.getStatusCode().value(),
                        parsedBody,
                        response.getHeaders().toSingleValueMap(),
                        "Success"
                );

            } catch (Exception e) {
                return new ApiResponse(500, null, Map.of(), "Error: " + e.getMessage());
            }
        });
    }

    @Tool(description = "Get API status and health")
    public HealthCheckResult checkApiHealth(
            @ToolParam("Base URL of the API") String baseUrl) {

        String healthUrl = baseUrl.endsWith("/") ? baseUrl + "health" : baseUrl + "/health";

        try {
            ResponseEntity<String> response = webClient.get()
                    .uri(healthUrl)
                    .retrieve()
                    .toEntity(String.class)
                    .block();

            return new HealthCheckResult(
                    baseUrl,
                    response != null && response.getStatusCode().is2xxSuccessful(),
                    response != null ? response.getStatusCode().value() : 0,
                    response != null ? response.getBody() : "No response"
            );

        } catch (Exception e) {
            return new HealthCheckResult(baseUrl, false, 0, e.getMessage());
        }
    }

    private boolean isValidUrl(String url) {
        try {
            URL parsed = new URL(url);
            String protocol = parsed.getProtocol();
            return "http".equals(protocol) || "https".equals(protocol);
        } catch (MalformedURLException e) {
            return false;
        }
    }

    private Object parseResponseBody(String body, MediaType contentType) {
        if (body == null || body.isBlank()) {
            return null;
        }

        try {
            if (contentType != null && contentType.includes(MediaType.APPLICATION_JSON)) {
                return new ObjectMapper().readValue(body, Object.class);
            }
            return body;
        } catch (Exception e) {
            return body; // Return raw body if parsing fails
        }
    }

    private Object parseRequestBody(String bodyJson) throws JsonProcessingException {
        if (bodyJson == null || bodyJson.isBlank()) {
            return null;
        }
        return new ObjectMapper().readValue(bodyJson, Object.class);
    }
}

record ApiResponse(int status, Object body, Map<String, String> headers, String message) {}
record HealthCheckResult(String url, boolean healthy, int statusCode, String response) {}
class ApiException extends RuntimeException {
    public ApiException(String message) {
        super(message);
    }
}
```

### GraphQL API Tool

```java
@Component
public class GraphQlTools {

    private final WebClient webClient;

    public GraphQlTools(WebClient.Builder builder) {
        this.webClient = builder
                .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
                .build();
    }

    @Tool(description = "Execute GraphQL query")
    public GraphQlResponse executeQuery(
            @ToolParam("GraphQL endpoint URL") String endpoint,
            @ToolParam("GraphQL query") String query,
            @ToolParam(value = "Query variables as JSON", required = false)
            String variablesJson) {

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("query", query);

            if (variablesJson != null && !variablesJson.isBlank()) {
                Map<String, Object> variables = new ObjectMapper().readValue(variablesJson, Map.class);
                requestBody.put("variables", variables);
            }

            ResponseEntity<String> response = webClient.post()
                    .uri(endpoint)
                    .bodyValue(requestBody)
                    .retrieve()
                    .toEntity(String.class)
                    .block();

            if (response == null) {
                return new GraphQlResponse(null, List.of("No response received"));
            }

            Map<String, Object> responseBody = new ObjectMapper().readValue(response.getBody(), Map.class);

            return new GraphQlResponse(
                    (Map<String, Object>) responseBody.get("data"),
                    (List<Map<String, Object>>) responseBody.get("errors")
            );

        } catch (Exception e) {
            return new GraphQlResponse(null, List.of(Map.of("message", e.getMessage())));
        }
    }

    @Tool(description = "Get GraphQL schema")
    public String getSchema(
            @ToolParam("GraphQL endpoint URL") String endpoint) {

        String introspectionQuery = """
            query IntrospectionQuery {
              __schema {
                queryType { name }
                mutationType { name }
                types {
                  name
                  kind
                  description
                }
              }
            }
            """;

        GraphQlResponse response = executeQuery(endpoint, introspectionQuery, null);
        return new ObjectMapper().valueToTree(response).toPrettyString();
    }
}

record GraphQlResponse(Map<String, Object> data, List<Map<String, Object>> errors) {}
```

## File System Tools

### File Operations Tool

```java
@Component
public class FileSystemTools {

    private final Path baseDirectory;

    public FileSystemTools(@Value("{mcp.filesystem.base-dir:/tmp/mcp") String baseDir) {
        this.baseDirectory = Paths.get(baseDir).toAbsolutePath().normalize();
        // Security: Create base directory if it doesn't exist
        try {
            Files.createDirectories(this.baseDirectory);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create base directory", e);
        }
    }

    @Tool(description = "Read file contents")
    public FileReadResult readFile(
            @ToolParam("Path to file, relative to base directory") String filePath) {

        try {
            Path file = resolveSafePath(filePath);

            if (!Files.exists(file)) {
                return new FileReadResult(false, null, "File does not exist: " + filePath);
            }

            if (!Files.isRegularFile(file)) {
                return new FileReadResult(false, null, "Path is not a file: " + filePath);
            }

            // Security: Check file size
            long size = Files.size(file);
            if (size > 10 * 1024 * 1024) { // 10MB limit
                return new FileReadResult(false, null, "File too large: " + size + " bytes");
            }

            String content = Files.readString(file);
            String mimeType = Files.probeContentType(file);

            return new FileReadResult(true, content, mimeType, filePath, size);

        } catch (IOException e) {
            return new FileReadResult(false, null, "Error reading file: " + e.getMessage());
        }
    }

    @Tool(description = "Write content to file")
    public FileWriteResult writeFile(
            @ToolParam("Path to file, relative to base directory") String filePath,
            @ToolParam("Content to write") String content) {

        try {
            Path file = resolveSafePath(filePath);

            // Security: Don't allow writing outside base directory
            if (!file.startsWith(baseDirectory)) {
                return new FileWriteResult(false, filePath, "Invalid path");
            }

            // Create parent directories if needed
            Files.createDirectories(file.getParent());

            Files.writeString(file, content, StandardOpenOption.CREATE,
                            StandardOpenOption.TRUNCATE_EXISTING);

            return new FileWriteResult(true, filePath, "File written successfully");

        } catch (IOException e) {
            return new FileWriteResult(false, filePath, "Error writing file: " + e.getMessage());
        }
    }

    @Tool(description = "List files in directory")
    public ListFilesResult listFiles(
            @ToolParam(value = "Directory path, relative to base directory", required = false)
            String dirPath,
            @ToolParam(value = "File pattern (e.g., *.txt)", required = false)
            String pattern) {

        try {
            Path dir = dirPath != null && !dirPath.isBlank()
                    ? resolveSafePath(dirPath)
                    : baseDirectory;

            if (!Files.isDirectory(dir)) {
                return new ListFilesResult(false, null, "Not a directory: " + dirPath);
            }

            try (var stream = Files.list(dir)) {
                List<FileInfo> files = stream
                        .filter(path -> pattern == null ||
                                path.getFileName().toString().matches(pattern.replace("*", ".*")))
                        .map(path -> {
                            try {
                                return new FileInfo(
                                        path.getFileName().toString(),
                                        Files.isDirectory(path),
                                        Files.size(path),
                                        Files.getLastModifiedTime(path).toInstant()
                                );
                            } catch (IOException e) {
                                return null;
                            }
                        })
                        .filter(Objects::nonNull)
                        .sorted(Comparator.comparing(FileInfo::name))
                        .toList();

                return new ListFilesResult(true, files, null);
            }

        } catch (IOException e) {
            return new ListFilesResult(false, null, "Error listing files: " + e.getMessage());
        }
    }

    @Tool(description = "Get file information")
    public FileInfo getFileInfo(
            @ToolParam("Path to file or directory") String path) {

        try {
            Path file = resolveSafePath(path);

            if (!Files.exists(file)) {
                return new FileInfo(path, false, -1, null, "File does not exist");
            }

            boolean isDirectory = Files.isDirectory(file);
            long size = isDirectory ? -1 : Files.size(file);
            Instant lastModified = Files.getLastModifiedTime(file).toInstant();

            return new FileInfo(file.getFileName().toString(), isDirectory, size, lastModified, null);

        } catch (IOException e) {
            return new FileInfo(path, false, -1, null, "Error: " + e.getMessage());
        }
    }

    private Path resolveSafePath(String path) throws IOException {
        // Security: Prevent path traversal
        Path file = baseDirectory.resolve(path).normalize();

        if (!file.startsWith(baseDirectory)) {
            throw new SecurityException("Invalid path");
        }

        return file;
    }
}

record FileReadResult(boolean success, String content, String mimeType, String path, long size, String error) {
    public FileReadResult(boolean success, String content, String error) {
        this(success, content, null, null, 0, error);
    }
}
record FileWriteResult(boolean success, String path, String message) {}
record ListFilesResult(boolean success, List<FileInfo> files, String error) {}
record FileInfo(String name, boolean isDirectory, long size, Instant lastModified, String error) {}
```

### CSV Processing Tool

```java
@Component
public class CsvTools {

    @Tool(description = "Read and analyze CSV file")
    public CsvAnalysis analyzeCsv(
            @ToolParam("Path to CSV file") String filePath,
            @ToolParam(value = "Has header row", required = false)
            Boolean hasHeader) {

        boolean header = hasHeader != null ? hasHeader : true;

        try (Reader reader = new FileReader(filePath);
             CSVParser parser = new CSVParser(reader,
                     CSVFormat.DEFAULT.builder()
                             .setHeader()
                             .setSkipHeaderRecord(header)
                             .build())) {

            List<CSVRecord> records = parser.getRecords();
            Map<String, Integer> columnCount = new HashMap<>();

            if (header) {
                for (String column : parser.getHeaderNames()) {
                    columnCount.put(column, 0);
                }
            }

            // Analyze data types
            Map<String, Set<String>> columnTypes = new HashMap<>();
            for (CSVRecord record : records) {
                for (int i = 0; i < record.size(); i++) {
                    String column = header ? parser.getHeaderNames().get(i) : "col_" + i;
                    String value = record.get(i);

                    columnTypes.computeIfAbsent(column, k -> new HashSet<>())
                            .add(inferType(value));
                }
            }

            return new CsvAnalysis(
                    filePath,
                    records.size(),
                    header ? parser.getHeaderNames() : null,
                    columnTypes,
                    header
            );

        } catch (IOException e) {
            throw new RuntimeException("Failed to analyze CSV", e);
        }
    }

    private String inferType(String value) {
        if (value == null || value.isBlank()) return "empty";
        if (value.matches("-?\\d+")) return "integer";
        if (value.matches("-?\\d*\\.\\d+")) return "decimal";
        if (value.matches("true|false", "true", "false")) return "boolean";
        if (value.matches("\\d{4}-\\d{2}-\\d{2}")) return "date";
        if (value.matches("\\d{4}(-\\d{2}){2}T\\d{2}(:\\d{2}){2}")) return "datetime";
        return "string";
    }

    @Tool(description = "Convert CSV to JSON")
    public List<Map<String, String>> csvToJson(
            @ToolParam("Path to CSV file") String filePath) {

        try (Reader reader = new FileReader(filePath);
             CSVParser parser = new CSVParser(reader,
                     CSVFormat.DEFAULT.builder().setHeader().build())) {

            return parser.getRecords().stream()
                    .map(record -> {
                        Map<String, String> json = new LinkedHashMap<>();
                        for (String header : parser.getHeaderNames()) {
                            json.put(header, record.get(header));
                        }
                        return json;
                    })
                    .toList();

        } catch (IOException e) {
            throw new RuntimeException("Failed to convert CSV to JSON", e);
        }
    }
}

record CsvAnalysis(
    String filePath,
    int rowCount,
    List<String> headers,
    Map<String, Set<String>> columnTypes,
    boolean hasHeader
) {}
```

## Business Logic Tools

### User Management Tools

```java
@Component
public class UserManagementTools {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserManagementTools(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Tool(description = "Search users by criteria")
    public List<UserInfo> searchUsers(
            @ToolParam(value = "Email contains", required = false)
            String email,
            @ToolParam(value = "Name contains", required = false)
            String name,
            @ToolParam(value = "Role", required = false)
            String role,
            @ToolParam(value = "Active status", required = false)
            Boolean active) {

        List<User> users = userRepository.findAll((root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            if (email != null && !email.isBlank()) {
                predicates.add(cb.like(root.get("email"), "%" + email + "%"));
            }
            if (name != null && !name.isBlank()) {
                predicates.add(cb.like(root.get("name"), "%" + name + "%"));
            }
            if (role != null && !role.isBlank()) {
                predicates.add(cb.equal(root.get("role"), role));
            }
            if (active != null) {
                predicates.add(cb.equal(root.get("active"), active));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        });

        return users.stream()
                .map(user -> new UserInfo(
                        user.getId(),
                        user.getEmail(),
                        user.getName(),
                        user.getRole(),
                        user.isActive(),
                        user.getCreatedAt()
                ))
                .toList();
    }

    @Tool(description = "Create a new user account")
    public UserCreationResult createUser(
            @ToolParam("User email") String email,
            @ToolParam("User name") String name,
            @ToolParam("User password") String password,
            @ToolParam(value = "User role", required = false)
            String role) {

        // Validate input
        if (!isValidEmail(email)) {
            return new UserCreationResult(false, null, "Invalid email format");
        }

        if (password.length() < 8) {
            return new UserCreationResult(false, null, "Password must be at least 8 characters");
        }

        // Check if user exists
        if (userRepository.findByEmail(email).isPresent()) {
            return new UserCreationResult(false, null, "User already exists: " + email);
        }

        try {
            User user = new User();
            user.setEmail(email);
            user.setName(name);
            user.setPassword(passwordEncoder.encode(password));
            user.setRole(role != null ? role : "USER");
            user.setActive(true);
            user.setCreatedAt(LocalDateTime.now());

            User saved = userRepository.save(user);

            return new UserCreationResult(
                    true,
                    new UserInfo(
                            saved.getId(),
                            saved.getEmail(),
                            saved.getName(),
                            saved.getRole(),
                            saved.isActive(),
                            saved.getCreatedAt()
                    ),
                    "User created successfully"
            );

        } catch (Exception e) {
            return new UserCreationResult(false, null, "Error creating user: " + e.getMessage());
        }
    }

    @Tool(description = "Get user statistics")
    public UserStatistics getUserStatistics() {
        long totalUsers = userRepository.count();
        long activeUsers = userRepository.countByActive(true);
        long inactiveUsers = userRepository.countByActive(false);

        Map<String, Long> usersByRole = userRepository.findAll().stream()
                .collect(Collectors.groupingBy(User::getRole, Collectors.counting()));

        return new UserStatistics(
                totalUsers,
                activeUsers,
                inactiveUsers,
                usersByRole
        );
    }

    private boolean isValidEmail(String email) {
        return email != null && email.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$");
    }
}

record UserInfo(Long id, String email, String name, String role, boolean active, LocalDateTime createdAt) {}
record UserCreationResult(boolean success, UserInfo user, String message) {}
record UserStatistics(long totalUsers, long activeUsers, long inactiveUsers, Map<String, Long> usersByRole) {}
```

### Order Management Tools

```java
@Component
public class OrderManagementTools {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;

    public OrderManagementTools(OrderRepository orderRepository, ProductRepository productRepository) {
        this.orderRepository = orderRepository;
        this.productRepository = productRepository;
    }

    @Tool(description = "Create a new order")
    public OrderCreationResult createOrder(
            @ToolParam("Customer email") String customerEmail,
            @ToolParam("Product IDs and quantities as JSON array")
            String itemsJson) {

        try {
            List<OrderItemInput> items = new ObjectMapper().readValue(itemsJson,
                    new TypeReference<List<OrderItemInput>>() {});

            // Validate items
            List<OrderItem> orderItems = new ArrayList<>();
            BigDecimal totalAmount = BigDecimal.ZERO;

            for (OrderItemInput itemInput : items) {
                Product product = productRepository.findById(itemInput.productId())
                        .orElseThrow(() -> new IllegalArgumentException(
                                "Product not found: " + itemInput.productId()));

                if (product.getStock() < itemInput.quantity()) {
                    throw new IllegalArgumentException(
                            "Insufficient stock for product: " + product.getName());
                }

                OrderItem orderItem = new OrderItem();
                orderItem.setProductId(product.getId());
                orderItem.setProductName(product.getName());
                orderItem.setQuantity(itemInput.quantity());
                orderItem.setUnitPrice(product.getPrice());
                orderItem.setSubtotal(product.getPrice().multiply(BigDecimal.valueOf(itemInput.quantity())));

                orderItems.add(orderItem);
                totalAmount = totalAmount.add(orderItem.getSubtotal());
            }

            // Create order
            Order order = new Order();
            order.setCustomerEmail(customerEmail);
            order.setOrderItems(orderItems);
            order.setTotalAmount(totalAmount);
            order.setStatus("PENDING");
            order.setCreatedAt(LocalDateTime.now());

            Order saved = orderRepository.save(order);

            return new OrderCreationResult(true, saved.getId(), saved.getTotalAmount(),
                    "Order created successfully");

        } catch (Exception e) {
            return new OrderCreationResult(false, null, null,
                    "Error: " + e.getMessage());
        }
    }

    @Tool(description = "Search orders")
    public List<OrderInfo> searchOrders(
            @ToolParam(value = "Customer email", required = false)
            String customerEmail,
            @ToolParam(value = "Order status", required = false)
            String status,
            @ToolParam(value = "Start date (YYYY-MM-DD)", required = false)
            String startDate,
            @ToolParam(value = "End date (YYYY-MM-DD)", required = false)
            String endDate) {

        return orderRepository.findAll((root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            if (customerEmail != null && !customerEmail.isBlank()) {
                predicates.add(cb.equal(root.get("customerEmail"), customerEmail));
            }
            if (status != null && !status.isBlank()) {
                predicates.add(cb.equal(root.get("status"), status));
            }
            if (startDate != null && !startDate.isBlank()) {
                predicates.add(cb.greaterThanOrEqualTo(
                        root.get("createdAt"), LocalDate.parse(startDate).atStartOfDay()));
            }
            if (endDate != null && !endDate.isBlank()) {
                predicates.add(cb.lessThanOrEqualTo(
                        root.get("createdAt"), LocalDate.parse(endDate).atTime(LocalTime.MAX)));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        }).stream().map(order -> new OrderInfo(
                order.getId(),
                order.getCustomerEmail(),
                order.getStatus(),
                order.getTotalAmount(),
                order.getCreatedAt(),
                order.getOrderItems().size()
        )).toList();
    }

    @Tool(description = "Get order statistics")
    public OrderStatistics getOrderStatistics(
            @ToolParam(value = "Start date (YYYY-MM-DD)", required = false)
            String startDate,
            @ToolParam(value = "End date (YYYY-MM-DD)", required = false)
            String endDate) {

        LocalDateTime start = startDate != null ?
                LocalDate.parse(startDate).atStartOfDay() :
                LocalDateTime.now().minusDays(30);

        LocalDateTime end = endDate != null ?
                LocalDate.parse(endDate).atTime(LocalTime.MAX) :
                LocalDateTime.now();

        List<Order> orders = orderRepository.findByCreatedAtBetween(start, end);

        BigDecimal totalRevenue = orders.stream()
                .map(Order::getTotalAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Map<String, Long> ordersByStatus = orders.stream()
                .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));

        Order lastOrder = orders.stream()
                .max(Comparator.comparing(Order::getCreatedAt))
                .orElse(null);

        return new OrderStatistics(
                orders.size(),
                totalRevenue,
                ordersByStatus,
                lastOrder != null ? lastOrder.getCreatedAt() : null
        );
    }
}

record OrderItemInput(Long productId, int quantity) {}
record OrderCreationResult(boolean success, Long orderId, BigDecimal total, String message) {}
record OrderInfo(Long id, String customerEmail, String status, BigDecimal totalAmount,
                 LocalDateTime createdAt, int itemCount) {}
record OrderStatistics(int totalOrders, BigDecimal totalRevenue,
                       Map<String, Long> ordersByStatus, LocalDateTime lastOrderDate) {}
```

## Multi-Modal Tools

### Image Processing Tools

```java
@Component
public class ImageTools {

    private final RestTemplate restTemplate;

    public ImageTools(RestTemplateBuilder builder) {
        this.restTemplate = builder.build();
    }

    @Tool(description = "Download and analyze image")
    public ImageAnalysis analyzeImage(@ToolParam("Image URL") String imageUrl) {
        try {
            // Download image
            ResponseEntity<byte[]> response = restTemplate.getForEntity(imageUrl, byte[].class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                return new ImageAnalysis(false, null, "Failed to download image");
            }

            byte[] imageData = response.getBody();
            if (imageData == null) {
                return new ImageAnalysis(false, null, "No image data");
            }

            // Analyze image
            String contentType = response.getHeaders().getContentType() != null ?
                    response.getHeaders().getContentType().toString() : "unknown";

            // Load image to get dimensions
            InputStream is = new ByteArrayInputStream(imageData);
            BufferedImage image = ImageIO.read(is);

            Map<String, Object> metadata = Map.of(
                    "url", imageUrl,
                    "size", imageData.length,
                    "contentType", contentType,
                    "width", image != null ? image.getWidth() : -1,
                    "height", image != null ? image.getHeight() : -1
            );

            return new ImageAnalysis(true, metadata, null);

        } catch (Exception e) {
            return new ImageAnalysis(false, null, "Error: " + e.getMessage());
        }
    }

    @Tool(description = "Convert image format")
    public ImageConversionResult convertImage(
            @ToolParam("Source image URL") String sourceUrl,
            @ToolParam("Target format (jpg, png, gif)") String targetFormat) {

        try {
            // Download source image
            ResponseEntity<byte[]> response = restTemplate.getForEntity(sourceUrl, byte[].class);
            byte[] sourceImage = response.getBody();

            if (sourceImage == null) {
                return new ImageConversionResult(false, null, "No source image data");
            }

            // Convert image
            InputStream is = new ByteArrayInputStream(sourceImage);
            BufferedImage image = ImageIO.read(is);

            String outputFileName = "converted_" + System.currentTimeMillis() + "." + targetFormat;

            ByteArrayOutputStream os = new ByteArrayOutputStream();
            ImageIO.write(image, targetFormat, os);

            byte[] convertedImage = os.toByteArray();

            // Save to temp file
            Path outputPath = Paths.get(System.getProperty("java.io.tmpdir"), outputFileName);
            Files.write(outputPath, convertedImage);

            return new ImageConversionResult(true, outputPath.toString(), null);

        } catch (Exception e) {
            return new ImageConversionResult(false, null, e.getMessage());
        }
    }

    @Tool(description = "Generate QR code")
    public QrCodeResult generateQrCode(
            @ToolParam("Text or URL to encode") String content,
            @ToolParam(value = "QR code size", required = false)
            Integer size) {

        int qrSize = size != null ? size : 200;

        try {
            QRCodeWriter qrCodeWriter = new QRCodeWriter();
            BitMatrix bitMatrix = qrCodeWriter.encode(
                    content,
                    BarcodeFormat.QR_CODE,
                    qrSize,
                    qrSize
            );

            BufferedImage image = MatrixToImageWriter.toBufferedImage(bitMatrix);

            String outputFileName = "qr_" + System.currentTimeMillis() + ".png";
            Path outputPath = Paths.get(System.getProperty("java.io.tmpdir"), outputFileName);

            ImageIO.write(image, "PNG", outputPath.toFile());

            return new QrCodeResult(true, outputPath.toString(), content, qrSize, null);

        } catch (Exception e) {
            return new QrCodeResult(false, null, content, qrSize, e.getMessage());
        }
    }
}

record ImageAnalysis(boolean success, Map<String, Object> metadata, String error) {}
record ImageConversionResult(boolean success, String outputPath, String error) {}
record QrCodeResult(boolean success, String filePath, String content, int size, String error) {}
```

### Audio Processing Tools

```java
@Component
public class AudioTools {

    private final Logger log = LoggerFactory.getLogger(AudioTools.class);

    @Tool(description = "Convert text to speech")
    public TextToSpeechResult textToSpeech(
            @ToolParam("Text to convert to speech") String text,
            @ToolParam(value = "Voice (alloy, echo, fable, onyx, nova, shimmer)", required = false)
            String voice,
            @ToolParam(value = "Response format (mp3, opus, aac, flac)", required = false)
            String responseFormat) {

        String selectedVoice = voice != null ? voice : "alloy";
        String format = responseFormat != null ? responseFormat : "mp3";

        try {
            // This would integrate with actual TTS service like OpenAI
            // For demonstration, we'll create a dummy audio file
            log.info("Converting text to speech: {} chars, voice: {}", text.length(), selectedVoice);

            // Simulate processing time
            Thread.sleep(1000);

            // Create dummy audio file
            String outputFileName = "speech_" + System.currentTimeMillis() + "." + format;
            Path outputPath = Paths.get(System.getProperty("java.io.tmpdir"), outputFileName);

            // Write dummy audio data
            Files.write(outputPath, new byte[]{0, 1, 2, 3, 4, 5});

            return new TextToSpeechResult(true, outputPath.toString(), text.length(), 1, selectedVoice, format);

        } catch (Exception e) {
            return new TextToSpeechResult(false, null, text.length(), 0, selectedVoice, format, e.getMessage());
        }
    }

    @Tool(description = "Transcribe audio to text")
    public SpeechToTextResult speechToText(
            @ToolParam("Path to audio file") String audioFilePath,
            @ToolParam(value = "Language (e.g., en, es, fr)", required = false)
            String language) {

        try {
            Path audioPath = Paths.get(audioFilePath);

            if (!Files.exists(audioPath)) {
                return new SpeechToTextResult(false, null, null, "File not found");
            }

            long fileSize = Files.size(audioPath);
            if (fileSize > 25 * 1024 * 1024) { // 25MB limit
                return new SpeechToTextResult(false, null, null, "File too large (max 25MB)");
            }

            // This would integrate with actual STT service
            log.info("Transcribing audio: {} bytes, language: {}", fileSize, language);

            // Simulate transcription
            Thread.sleep(2000);

            String transcription = "This is a simulated transcription of the audio file. " +
                                 "In a real implementation, this would be the actual transcribed text.";

            return new SpeechToTextResult(true, transcription, language, null);

        } catch (Exception e) {
            return new SpeechToTextResult(false, null, language, e.getMessage());
        }
    }

    @Tool(description = "Analyze audio file")
    public AudioAnalysis analyzeAudio(@ToolParam("Path to audio file") String audioFilePath) {
        try {
            Path audioPath = Paths.get(audioFilePath);

            if (!Files.exists(audioPath)) {
                return new AudioAnalysis(false, null, "File not found");
            }

            long fileSize = Files.size(audioPath);
            String fileName = audioPath.getFileName().toString();
            String extension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();

            // Get audio format details
            AudioFormat format = null;
            long duration = 0;

            if ("wav".equals(extension)) {
                try (AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(audioPath.toFile())) {
                    format = audioInputStream.getFormat();
                    long frames = audioInputStream.getFrameLength();
                    duration = (long) (frames / format.getSampleRate());
                }
            }

            Map<String, Object> metadata = new LinkedHashMap<>();
            metadata.put("fileName", fileName);
            metadata.put("fileSize", fileSize);
            metadata.put("fileSizeMB", String.format("%.2f", fileSize / (1024.0 * 1024.0)));
            metadata.put("extension", extension);

            if (format != null) {
                metadata.put("sampleRate", format.getSampleRate());
                metadata.put("channels", format.getChannels());
                metadata.put("bitsPerSample", format.getSampleSizeInBits());
                metadata.put("durationSeconds", duration);
                metadata.put("durationFormatted", String.format("%d:%02d", duration / 60, duration % 60));
            }

            return new AudioAnalysis(true, metadata, null);

        } catch (Exception e) {
            return new AudioAnalysis(false, null, e.getMessage());
        }
    }
}

record TextToSpeechResult(
        boolean success,
        String outputFilePath,
        int textLength,
        int durationSeconds,
        String voice,
        String format,
        String error
) {}
record SpeechToTextResult(boolean success, String transcription, String language, String error) {}
record AudioAnalysis(boolean success, Map<String, Object> metadata, String error) {}
```

## Secure Enterprise Tools

### Secure Database Operations

```java
@Component
public class SecureDatabaseTools {

    private final JdbcTemplate jdbcTemplate;
    private final SecurityService securityService;

    public SecureDatabaseTools(JdbcTemplate jdbcTemplate, SecurityService securityService) {
        this.jdbcTemplate = jdbcTemplate;
        this.securityService = securityService;
    }

    @PreAuthorize("hasRole('ADMIN') or hasRole('DB_USER')")
    @Tool(description = "Execute secure database query (requires authentication)")
    public SecureQueryResult executeSecureQuery(
            @ToolParam("SQL query") String query,
            @ToolParam(value = "Query parameters", required = false)
            String paramsJson) {

        // Multi-factor authentication for sensitive operations
        if (isSensitiveQuery(query)) {
            if (!securityService.verifyMfaToken()) {
                return new SecureQueryResult(false, null, null, "MFA verification required");
            }
            securityService.logSensitiveOperation("database_query", query);
        }

        // Query sanitization
        String sanitizedQuery = sanitizeQuery(query);
        if (sanitizedQuery == null) {
            return new SecureQueryResult(false, null, null, "Query not allowed");
        }

        try {
            Map<String, Object> params = paramsJson != null
                    ? new ObjectMapper().readValue(paramsJson, Map.class)
                    : Map.of();

            long startTime = System.currentTimeMillis();
            List<Map<String, Object>> results = jdbcTemplate.queryForList(sanitizedQuery, params);
            long duration = System.currentTimeMillis() - startTime;

            User user = securityService.getCurrentUser();
            securityService.auditQueryExecution(user, query, duration, results.size());

            if (duration > 5000) {
                log.warn("Slow query detected: {}ms by user {}", duration, user.getUsername());
            }

            return new SecureQueryResult(true, results, duration, null);

        } catch (Exception e) {
            securityService.logSecurityEvent("query_error", e.getMessage());
            return new SecureQueryResult(false, null, null, "Query execution failed");
        }
    }

    private boolean isSensitiveQuery(String query) {
        String upper = query.toUpperCase();
        return upper.contains("DELETE") || upper.contains("UPDATE") || upper.contains("DROP") ||
                upper.contains("CREATE") || upper.contains("ALTER") || upper.contains("GRANT");
    }

    private String sanitizeQuery(String query) {
        // Remove comments
        String sanitized = query.replaceAll("\\/\\*.*?\\*\\/", "")
                               .replaceAll("--.*$", "")
                               .trim();

        // Check for dangerous patterns
        String upper = sanitized.toUpperCase();
        if (upper.contains("UNION") || upper.contains(";/*") || upper.contains("xp_")) {
            return null; // Potentially dangerous
        }

        return sanitized;
    }
}

record SecureQueryResult(boolean success, List<Map<String, Object>> data, Long durationMs, String error) {}
```

## Real-Time Streaming

### Streaming MCP Server

```java
@Component
public class StreamingMcpServer {

    private final SseEmitter emitter;
    private final McpServer mcpServer;

    public StreamingMcpServer(McpServer mcpServer) {
        this.mcpServer = mcpServer;
        this.emitter = new SseEmitter(600000L); // 10 minutes
    }

    @Tool(description = "Stream real-time data")
    public void streamData(
            @ToolParam("Data source") String source,
            @ToolParam(value = "Stream interval (seconds)", required = false)
            Integer interval) {

        int seconds = interval != null ? interval : 5;

        try {
            emitter.send(SseEmitter.event()
                    .name("stream-start")
                    .data(Map.of("source", source, "interval", seconds)));

            ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();
            AtomicInteger counter = new AtomicInteger(0);

            executor.scheduleAtFixedRate(() -> {
                try {
                    Map<String, Object> data = fetchRealTimeData(source);
                    data.put("timestamp", Instant.now().toString());
                    data.put("sequence", counter.incrementAndGet());

                    emitter.send(SseEmitter.event()
                            .name("data-update")
                            .data(data));

                } catch (IOException e) {
                    log.error("Failed to send stream data", e);
                    emitter.completeWithError(e);
                    executor.shutdown();
                }
            }, 0, seconds, TimeUnit.SECONDS);

            // Stop after 100 updates or on client disconnect
            emitter.onCompletion(() -> {
                executor.shutdown();
                log.info("Stream completed, shutting down executor");
            });
            emitter.onTimeout(() -> {
                executor.shutdown();
                emitter.complete();
                log.warn("Stream timed out");
            });
            emitter.onError((ex) -> {
                executor.shutdown();
                log.error("Stream error occurred", ex);
            });

        } catch (IOException e) {
            log.error("Failed to start stream", e);
            emitter.completeWithError(e);
        } finally {
            // Ensure executor is shutdown in all cases
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                if (!executor.isShutdown()) {
                    executor.shutdown();
                }
            }));
        }
    }

    private Map<String, Object> fetchRealTimeData(String source) {
        // Simulate real-time data fetching
        return Map.of(
                "source", source,
                "value", Math.random() * 100,
                "unit", "metric",
                "status", "active"
        );
    }
}
```

## Complete Application Example

### Full Spring Boot MCP Application

```java
@SpringBootApplication
@EnableMcpServer
public class EnterpriseMcpApplication {

    public static void main(String[] args) {
        SpringApplication.run(EnterpriseMcpApplication.class, args);
    }

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/mcp/*")
                        .allowedOrigins("*")
                        .allowedMethods("GET", "POST", "PUT", "DELETE");
            }
        };
    }
}
```

### Security Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/mcp/tools/secure*").hasRole("ADMIN")
                .requestMatchers("/mcp/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt());

        return http.build();
    }
}
```

### Production Configuration

```yaml
spring:
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
        name: enterprise-mcp-server
        version: 1.0.0
      transport: stdio
      security:
        enabled: true
        authorization:
          mode: role-based
        audit:
          enabled: true
      logging:
        enabled: true
        level: DEBUG
      metrics:
        enabled: true
        export:
          prometheus:
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
```

This comprehensive example demonstrates how to build a complete MCP server with Spring AI for various use cases and enterprise requirements.
