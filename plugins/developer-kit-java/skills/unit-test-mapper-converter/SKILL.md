---
name: unit-test-mapper-converter
description: Provides patterns for unit testing mappers, converters, and bean mappings. Validates entity-to-DTO and model transformation logic in isolation. Generates executable mapping tests with MapStruct and custom converter test coverage. Use when writing mapping tests, converter tests, entity mapping tests, or ensuring correct data transformation between DTOs and domain objects.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Mappers and Converters

## Overview

Provides patterns for unit testing MapStruct mappers and custom converter classes. Covers field mapping accuracy, null handling, type conversions, nested object transformations, bidirectional mapping, enum mapping, and partial updates.

## When to Use

- Writing mapping tests for MapStruct mapper implementations
- Testing custom entity-to-DTO converters and bean mappings
- Validating nested object mapping and collection transformations

## Instructions

### 1. Validate Generated Mapper Classes
Before testing, verify generated mapper classes exist:
```bash
# Maven
ls target/generated-sources/

# Gradle
ls build/generated/sources/
```

**If generated classes are missing:**
1. Run `mvn compile` (Maven) or `./gradlew compileJava` (Gradle)
2. Check that the MapStruct annotation processor is configured
3. Verify `@Mapper` interfaces are in a compiled source set

### 2. Test Null Handling
```java
assertThat(mapper.toDto(null)).isNull();
```
Configure `nullValueMappingStrategy` in mapper if null should return empty/default.

**If null tests fail:**
1. Add `nullValueMappingStrategy = NullValueMappingStrategy.RETURN_NULL` to `@Mapper`
2. Or use `nullValuePropertyMappingStrategy` for nested property handling

### 3. Test Bidirectional Mapping
```java
User restored = mapper.toEntity(mapper.toDto(original));
assertThat(restored).usingRecursiveComparison().isEqualTo(original);
```

**If bidirectional tests fail:**
1. Check `@Mapping` annotations for field name mismatches
2. Verify both directions are explicitly mapped if auto-mapping fails
3. Use `unmappedTargetPolicy = ReportingPolicy.ERROR` to catch missing mappings

### 4. Test Nested Object Mapping
```java
assertThat(dto.getNested()).usingRecursiveComparison().isEqualTo(expected);
```

**If nested tests fail:**
1. Ensure nested mapper exists or is referenced via `uses = NestedMapper.class`
2. Check collection element mappings with `elementMappingStrategy`

### 5. Test Custom Expressions
Custom expressions in `@Mapping(target = "field", expression = "java(...)")` are not compile-time validated.

**If expression tests fail:**
1. Verify the expression syntax and method signatures
2. Check that imported classes are accessible from the expression context

### 6. Test Enum Mappings
Use `@ValueMapping` for enum-to-enum translations. Test all enum values exhaustively.

## Best Practices

- Use `Mappers.getMapper()` for standalone tests, Spring injection for integration tests
- Use `usingRecursiveComparison()` for complex nested structures
- Test all mapper methods including collection transformations
- Verify null handling for all nullable source fields
- Test bidirectional mapping catches asymmetries between entity→DTO and DTO→entity
- Keep mapper tests focused on transformation correctness, not implementation details

## Constraints and Warnings

- **Compile-time generation**: MapStruct generates code at compile time—verify generated classes exist before running tests
- **Null handling**: Configure `nullValueMappingStrategy` and `nullValuePropertyMappingStrategy` appropriately
- **Expression validation**: Expressions in `@Mapping` are not validated at compile time—test them explicitly
- **Circular dependencies**: MapStruct cannot handle circular dependencies between mappers
- **Collection immutability**: Mapping immutable collections may require special configuration
- **Date/Time**: Verify date/time objects map correctly across timezones

## Examples

Complete executable test with imports:
```java
package com.example.mapper;

import org.junit.jupiter.api.Test;
import org.mapstruct.factory.Mappers;
import static org.assertj.core.api.Assertions.*;

class UserMapperCompleteTest {
  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapUserToDto() {
    User user = new User(1L, "Alice", "alice@example.com", 25);
    UserDto dto = mapper.toDto(user);
    assertThat(dto)
      .isNotNull()
      .extracting(UserDto::getName, UserDto::getEmail)
      .containsExactly("Alice", "alice@example.com");
  }

  @Test
  void shouldMaintainRoundTrip() {
    User original = new User(1L, "Alice", "alice@example.com", 25);
    assertThat(mapper.toEntity(mapper.toDto(original)))
      .usingRecursiveComparison()
      .isEqualTo(original);
  }

  @Test
  void shouldHandleNullInput() {
    assertThat(mapper.toDto(null)).isNull();
  }
}
```

Additional examples in: `references/examples.md`
