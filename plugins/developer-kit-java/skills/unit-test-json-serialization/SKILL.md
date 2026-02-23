---
name: unit-test-json-serialization
description: Provides patterns for unit testing JSON serialization/deserialization with Jackson and @JsonTest. Use when validating JSON mapping, custom serializers, and date format handling.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing JSON Serialization with `@JsonTest`

## Overview

This skill defines focused JSON mapping tests for Spring Boot 3.x using Jackson.
It validates serialization, deserialization, custom formats, and contract stability.

## When to Use

Use this skill when:
- Testing DTO to JSON serialization rules
- Testing JSON to DTO deserialization behavior
- Verifying custom serializer/deserializer logic
- Validating date/time, enum, and null-field handling

Trigger phrases:
- "json test with jacksontester"
- "test jackson serializer"
- "verify json contract"
- "deserialize dto test"

## Instructions

1. Use `@JsonTest` for Jackson-focused test slices.
2. Inject `JacksonTester<T>` for type-safe JSON assertions.
3. Test both serialization and deserialization for each DTO.
4. Assert exact field names, formats, and null behavior.
5. Register custom modules or serializers when needed.
6. Add negative-path tests for malformed payloads.

## Examples

```java
@JsonTest
class InvoiceJsonTest {
  @Autowired JacksonTester<InvoiceDto> json;

  @Test
  void shouldSerialize() throws Exception {
    InvoiceDto dto = new InvoiceDto("INV-1", LocalDate.parse("2026-02-23"));
    assertThat(json.write(dto)).extractingJsonPathStringValue("@.id").isEqualTo("INV-1");
  }
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Prefer field-level assertions over full JSON string comparisons.
- Keep DTOs immutable where possible for stable mapping behavior.
- Include backward-compatible parsing cases for evolving payloads.

## Constraints and Warnings

- Jackson default settings may differ from production custom ObjectMapper configuration.
- `@JsonTest` does not validate controller binding or endpoint content negotiation.
- Date/time assertions must use explicit format expectations to avoid timezone drift.
- Unknown property behavior depends on mapper features and annotations.

## Constraints

- Do not mix business logic validation into serialization tests.
- Do not rely on endpoint tests to validate low-level JSON contracts.
- Keep examples compatible with Spring Boot 3.x and Jackson.

## References

- [Examples](references/examples.md) - Complete runnable test examples
