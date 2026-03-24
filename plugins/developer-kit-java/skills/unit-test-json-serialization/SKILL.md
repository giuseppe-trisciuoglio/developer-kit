---
name: unit-test-json-serialization
description: Provides patterns for unit testing JSON serialization/deserialization with Jackson and `@JsonTest`. Validates JSON mapping, custom serializers, date formats, and polymorphic types. Use when testing JSON serialization, validating custom serializers, or writing JSON unit tests in Spring Boot applications.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing JSON Serialization with `@JsonTest`

## Overview

Provides patterns for unit testing JSON serialization and deserialization using Spring's `@JsonTest` and Jackson. Covers POJO mapping, custom serializers, field name mappings, nested objects, date/time formatting, and polymorphic types.

## When to Use

- Testing JSON serialization/deserialization of DTOs
- Verifying custom Jackson serializers/deserializers
- Validating `@JsonProperty`, `@JsonIgnore`, and field name mappings
- Testing date/time format handling (LocalDateTime, Date)
- Testing null handling and missing fields
- Testing polymorphic type deserialization

## Instructions

1. **Annotate test class with `@JsonTest`** → Enables JacksonTester auto-configuration
2. **Autowire JacksonTester for target type** → Provides type-safe JSON assertions
3. **Test serialization** → Call `json.write(object)` and assert JSON paths with `extractingJsonPath*`
4. **Test deserialization** → Call `json.parse(json)` or `json.parseObject(json)` and assert object state
5. **Validate round-trip** → Serialize, then deserialize, verify same data (if object is properly comparable)
6. **Test edge cases** → Null values, missing fields, empty collections, invalid JSON
7. **Add validation checkpoints**: After each assertion, verify the test fails meaningfully with wrong data

## Examples

### Maven Setup
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-json</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle Setup
```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter-json")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### Basic Serialization and Deserialization

```java
@JsonTest
class UserDtoJsonTest {

  @Autowired
  private JacksonTester<UserDto> json;

  @Test
  void shouldSerializeUserToJson() throws Exception {
    UserDto user = new UserDto(1L, "Alice", "alice@example.com", 25);
    JsonContent<UserDto> result = json.write(user);

    result
      .extractingJsonPathNumberValue("$.id").isEqualTo(1)
      .extractingJsonPathStringValue("$.name").isEqualTo("Alice")
      .extractingJsonPathStringValue("$.email").isEqualTo("alice@example.com")
      .extractingJsonPathNumberValue("$.age").isEqualTo(25);
  }

  @Test
  void shouldDeserializeJsonToUser() throws Exception {
    String json_content = "{\"id\":1,\"name\":\"Alice\",\"email\":\"alice@example.com\",\"age\":25}";
    UserDto user = json.parse(json_content).getObject();

    assertThat(user.getId()).isEqualTo(1L);
    assertThat(user.getName()).isEqualTo("Alice");
    assertThat(user.getEmail()).isEqualTo("alice@example.com");
    assertThat(user.getAge()).isEqualTo(25);
  }

  @Test
  void shouldHandleNullFields() throws Exception {
    String json_content = "{\"id\":1,\"name\":null,\"email\":\"alice@example.com\"}";
    UserDto user = json.parse(json_content).getObject();
    assertThat(user.getName()).isNull();
  }
}
```

### Custom JSON Properties

```java
public class Order {
  @JsonProperty("order_id")
  private Long id;

  @JsonProperty("total_amount")
  private BigDecimal amount;

  @JsonIgnore
  private String internalNote;
}

@JsonTest
class OrderJsonTest {

  @Autowired
  private JacksonTester<Order> json;

  @Test
  void shouldMapJsonPropertyNames() throws Exception {
    String json_content = "{\"order_id\":123,\"total_amount\":99.99}";
    Order order = json.parse(json_content).getObject();
    assertThat(order.getId()).isEqualTo(123L);
    assertThat(order.getAmount()).isEqualByComparingTo(new BigDecimal("99.99"));
  }

  @Test
  void shouldIgnoreJsonIgnoreFields() throws Exception {
    Order order = new Order(123L, new BigDecimal("99.99"));
    order.setInternalNote("Secret");
    assertThat(json.write(order).json).doesNotContain("internalNote");
  }
}
```

### Nested Objects

```java
public class Product {
  private Long id;
  private String name;
  private Category category;
  private List<Review> reviews;
}

@JsonTest
class ProductJsonTest {

  @Autowired
  private JacksonTester<Product> json;

  @Test
  void shouldSerializeNestedObjects() throws Exception {
    Product product = new Product(1L, "Laptop", new Category(1L, "Electronics"));
    JsonContent<Product> result = json.write(product);

    result
      .extractingJsonPathNumberValue("$.category.id").isEqualTo(1)
      .extractingJsonPathStringValue("$.category.name").isEqualTo("Electronics");
  }

  @Test
  void shouldDeserializeNestedObjects() throws Exception {
    String json_content = "{\"id\":1,\"name\":\"Laptop\",\"category\":{\"id\":1,\"name\":\"Electronics\"}}";
    Product product = json.parse(json_content).getObject();
    assertThat(product.getCategory().getName()).isEqualTo("Electronics");
  }

  @Test
  void shouldHandleListOfNestedObjects() throws Exception {
    String json_content = "{\"id\":1,\"reviews\":[{\"rating\":5},{\"rating\":4}]}";
    Product product = json.parse(json_content).getObject();
    assertThat(product.getReviews()).hasSize(2);
  }
}
```

### Date/Time Formatting

```java
@JsonTest
class DateTimeJsonTest {

  @Autowired
  private JacksonTester<Event> json;

  @Test
  void shouldFormatDateTimeCorrectly() throws Exception {
    LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 10, 30, 0);
    json.write(new Event("Conference", dt))
      .extractingJsonPathStringValue("$.scheduledAt").isEqualTo("2024-01-15T10:30:00");
  }
}
```

### Custom Serializers

```java
public class CustomMoneySerializer extends JsonSerializer<BigDecimal> {
  @Override
  public void serialize(BigDecimal value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
    gen.writeString(value == null ? null : String.format("$%.2f", value));
  }
}

@JsonTest
class CustomSerializerTest {

  @Autowired
  private JacksonTester<Price> json;

  @Test
  void shouldUseCustomSerializer() throws Exception {
    json.write(new Price(new BigDecimal("99.99")))
      .extractingJsonPathStringValue("$.amount").isEqualTo("$99.99");
  }
}
```

### Polymorphic Deserialization

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
  @JsonSubTypes.Type(value = CreditCard.class, name = "credit_card"),
  @JsonSubTypes.Type(value = PayPal.class, name = "paypal")
})
public abstract class PaymentMethod { }

@JsonTest
class PolymorphicJsonTest {

  @Autowired
  private JacksonTester<PaymentMethod> json;

  @Test
  void shouldDeserializeCreditCard() throws Exception {
    String json_content = "{\"type\":\"credit_card\",\"id\":\"card123\"}";
    assertThat(json.parse(json_content).getObject()).isInstanceOf(CreditCard.class);
  }

  @Test
  void shouldDeserializePayPal() throws Exception {
    String json_content = "{\"type\":\"paypal\",\"id\":\"pp123\"}";
    assertThat(json.parse(json_content).getObject()).isInstanceOf(PayPal.class);
  }
}
```

## Best Practices

- Test serialization AND deserialization for complete coverage
- Verify JSON paths individually rather than comparing full JSON strings
- Test null handling explicitly — null fields may be included or excluded depending on `@JsonInclude`
- Use `extractingJsonPath*` methods for precise field assertions
- Test round-trip: serialize an object, deserialize the JSON, verify the result matches
- Validate edge cases: empty strings, empty collections, deeply nested structures
- Group related assertions in a single test for clarity

## Constraints and Warnings

- **`@JsonTest` loads limited context**: Only JSON-related beans; use `@SpringBootTest` for full Spring context
- **Jackson version**: Ensure annotation versions match the Jackson version in use
- **Date formats**: ISO-8601 is default; use `@JsonFormat` for custom patterns
- **Null handling**: Use `@JsonInclude(Include.NON_NULL)` to exclude nulls from serialization
- **Circular references**: Use `@JsonManagedReference`/`@JsonBackReference` to prevent infinite loops
- **Immutable objects**: Use `@JsonCreator` + `@JsonProperty` for constructor-based deserialization
- **Polymorphic types**: `@JsonTypeInfo` must correctly identify the subtype for deserialization to work

## Debugging Workflow

When a JSON test fails, follow this workflow:

| Failure Symptom | Common Cause | How to Verify |
|----------------|--------------|---------------|
| `JsonPath` assertion fails | Field name mismatch | Check `@JsonProperty` spelling matches JSON key |
| Null expected but got value | `@JsonInclude(NON_NULL)` configured | Verify annotation on field/class |
| Deserialization returns wrong type | Missing `@JsonTypeInfo` | Add type info property to JSON or configure subtype mapping |
| Date format mismatch | Format string incorrect | Confirm `@JsonFormat(pattern=...)` matches expected string |
| Missing field in output | `@JsonIgnore` or transient modifier | Check field for `@JsonIgnore` or `transient` keyword |
| Nested object is null | Inner JSON missing or malformed | Log parsed JSON; verify inner structure matches POJO |
| `JsonParseException` | Malformed JSON string | Validate JSON syntax; check for unescaped characters |

**Validation checkpoint after fixing**: Re-run the test — if it passes, write a complementary test for the opposite case (e.g., if you fixed null handling, add a test for non-null values to prevent regression).

## References

- [Spring `@JsonTest` Documentation](https://docs.spring.io/spring-boot/docs/current/api/org/springframework/boot/test/autoconfigure/json/JsonTest.html)
- [Jackson ObjectMapper](https://fasterxml.github.io/jackson-databind/javadoc/2.15/com/fasterxml/jackson/databind/ObjectMapper.html)
- [Jackson Annotations](https://fasterxml.github.io/jackson-annotations/javadoc/2.15/)
