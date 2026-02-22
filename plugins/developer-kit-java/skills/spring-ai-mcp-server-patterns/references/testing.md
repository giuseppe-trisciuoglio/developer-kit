# Spring AI MCP Server - Testing Patterns

## Unit Test for MCP Tools

```java
@ExtendWith(MockitoExtension.class)
class CalculatorToolsTest {

    private final CalculatorTools tools = new CalculatorTools();

    @Test
    void add_returnsExpectedValue() {
        assertThat(tools.add(2, 3)).isEqualTo(5);
    }

    @Test
    void divide_rejectsZeroDivisor() {
        assertThatThrownBy(() -> tools.divide(10, 0))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("non-zero");
    }
}
```

## Validation Test for Tool Parameters

```java
class ValidatedToolTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    void blankOrderId_isRejected() {
        var request = new DeleteOrderRequest(" ");
        var violations = validator.validate(request);
        assertThat(violations).isNotEmpty();
    }
}

record DeleteOrderRequest(@NotBlank String orderId) {}
```

## Spring Context Smoke Test

```java
@SpringBootTest
class McpServerContextTest {

    @Test
    void contextLoads() {
        // verifies MCP starter wiring and annotation scanning
    }
}
```

## Integration Test Guidance

1. Use `@SpringBootTest` to validate tool bean discovery and wiring.
2. Keep one smoke test per transport profile (`stdio`, `webmvc`, `webflux`) when supported by your app.
3. For data tools, use Testcontainers and assert behavior for both success and dependency failures.
4. Add contract tests for tool schemas and prompt argument requirements.

## Security Test Guidance

1. Verify `@PreAuthorize` behavior for allowed and denied roles.
2. Assert that sensitive tools are inaccessible without required authorities.
3. Test sanitization/validation paths for malicious input payloads.
