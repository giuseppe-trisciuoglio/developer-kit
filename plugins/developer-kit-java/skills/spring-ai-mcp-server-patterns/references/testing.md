# Spring AI MCP Server - Testing Patterns

## Unit Testing Tools

```java
@SpringBootTest
class DatabaseToolsTest {

    @Autowired
    private DatabaseTools databaseTools;

    @MockBean
    private JdbcTemplate jdbcTemplate;

    @Test
    void testExecuteQuery_Success() {
        String query = "SELECT * FROM users WHERE id = ?";
        Map<String, Object> params = Map.of("id", 1);
        List<Map<String, Object>> expectedResults = List.of(
            Map.of("id", 1, "name", "John")
        );

        when(jdbcTemplate.queryForList(anyString(), anyMap()))
            .thenReturn(expectedResults);

        List<Map<String, Object>> results = databaseTools.executeQuery(query, params);

        assertThat(results).isEqualTo(expectedResults);
        verify(jdbcTemplate).queryForList(query, params);
    }

    @Test
    void testExecuteQuery_InvalidQuery_ThrowsException() {
        String query = "DROP TABLE users";

        assertThatThrownBy(() -> databaseTools.executeQuery(query, null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Only SELECT queries are allowed");

        verifyNoInteractions(jdbcTemplate);
    }

    @Test
    void testGetTableSchema_Success() {
        String tableName = "users";
        List<Map<String, Object>> columns = List.of(
            Map.of("column_name", "id", "data_type", "integer"),
            Map.of("column_name", "name", "data_type", "varchar")
        );

        when(jdbcTemplate.queryForList(anyString(), eq(tableName)))
            .thenReturn(columns);

        TableSchema schema = databaseTools.getTableSchema(tableName);

        assertThat(schema.tableName()).isEqualTo(tableName);
        assertThat(schema.columns()).isEqualTo(columns);
    }
}
```

## Integration Testing

```java
@SpringBootTest
@AutoConfigureMockMvc
class McpServerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private McpServer mcpServer;

    @MockBean
    private DatabaseTools databaseTools;

    @Test
    void testExecuteTool_Success() throws Exception {
        Map<String, Object> args = Map.of(
            "query", "SELECT * FROM users",
            "params", Map.of()
        );

        List<Map<String, Object>> expectedResult = List.of(
            Map.of("id", 1, "name", "Test User")
        );

        when(databaseTools.executeQuery(anyString(), anyMap()))
            .thenReturn(expectedResult);

        mockMvc.perform(post("/mcp/tools/executeQuery")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(args)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.result").isArray())
                .andExpect(jsonPath("$.result[0].id").value(1));
    }

    @Test
    void testListTools_Success() throws Exception {
        mockMvc.perform(get("/mcp/tools"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.tools").isArray());
    }

    @Test
    void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/actuator/health/mcp"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"));
    }
}
```

## Integration Testing with Testcontainers

```java
@SpringBootTest
@Testcontainers
@AutoConfigureMockMvc
class McpServerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void properties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testDatabaseToolWithRealDatabase() throws Exception {
        String query = "SELECT current_database(), current_user";
        Map<String, Object> request = Map.of(
                "tool", "executeQuery",
                "arguments", Map.of("query", query)
        );

        mockMvc.perform(post("/mcp/tools/executeQuery")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));
    }
}
```

## Testing Tool Validation

```java
@ExtendWith(MockitoExtension.class)
class ToolValidationTest {

    private ToolValidator validator;

    @BeforeEach
    void setUp() {
        McpServerProperties properties = new McpServerProperties();
        properties.getTools().getValidation().setMaxArgumentsSize(1000);
        validator = new DefaultToolValidator(properties);
    }

    @Test
    void testValidArguments() {
        Tool tool = Tool.builder()
                .name("testTool")
                .method(getTestMethod())
                .build();
        Map<String, Object> args = Map.of("param1", "value1", "param2", 123);

        assertDoesNotThrow(() -> validator.validateArguments(tool, args));
    }

    @Test
    void testArgumentsTooLarge() {
        Tool tool = Tool.builder().name("testTool").build();
        Map<String, Object> args = Map.of("largeParam", "x".repeat(2000));

        ValidationException exception = assertThrows(
                ValidationException.class,
                () -> validator.validateArguments(tool, args)
        );
        assertThat(exception.getMessage()).contains("Arguments too large");
    }
}
```

## Testing Security Integration

```java
@SpringBootTest
@AutoConfigureMockMvc
@WithMockUser(roles = {"USER"})
class McpSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testUserCanAccessRegularTools() throws Exception {
        mockMvc.perform(get("/mcp/tools/getWeather"))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = {"USER"})
    void testUserCannotAccessAdminTools() throws Exception {
        mockMvc.perform(get("/mcp/tools/admin/deleteData"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = {"ADMIN"})
    void testAdminCanAccessAllTools() throws Exception {
        mockMvc.perform(get("/mcp/tools/admin/deleteData"))
                .andExpect(status().isOk());
    }
}
```

## Configuration Testing

```java
@SpringBootTest
@EnableConfigurationProperties(McpServerProperties.class)
class McpPropertiesTest {

    @Autowired
    private McpServerProperties properties;

    @Test
    void testDefaultValues() {
        assertThat(properties.getServer().getName()).isEqualTo("spring-ai-mcp-server");
        assertThat(properties.getTransport().getType()).isEqualTo(TransportType.STDIO);
        assertThat(properties.getSecurity().isEnabled()).isFalse();
    }
}
```

## Slice Test

```java
@WebMvcTest(controllers = McpController.class)
class McpControllerSliceTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private McpServer mcpServer;

    @MockBean
    private ToolRegistry toolRegistry;

    @Test
    void testListToolsEndpoint() throws Exception {
        Tool tool1 = Tool.builder().name("tool1").description("Tool 1").build();
        Tool tool2 = Tool.builder().name("tool2").description("Tool 2").build();

        when(toolRegistry.listTools()).thenReturn(List.of(tool1, tool2));

        mockMvc.perform(get("/mcp/tools"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.tools").isArray())
                .andExpect(jsonPath("$.tools.length()").value(2))
                .andExpect(jsonPath("$.tools[0].name").value("tool1"));
    }
}
```
