---
name: unit-test-mapper-converter
description: Provides patterns for unit testing mappers and converters (MapStruct, custom mappers). Validates object transformation logic in isolation. Use when ensuring correct data transformation between DTOs and domain objects.
category: testing
tags: [junit-5, mapstruct, mapper, dto, entity, converter]
version: 2.2.0
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Mappers and Converters

## Overview

This skill provides patterns for unit testing MapStruct mappers and custom converter classes. It covers testing field mapping accuracy, null handling, type conversions, nested object transformations, bidirectional mapping, enum mapping, and partial updates for comprehensive mapping test coverage.

## When to Use

Use this skill when:
- Testing MapStruct mapper implementations
- Testing custom entity-to-DTO converters
- Testing nested object mapping
- Verifying null handling in mappers
- Testing type conversions and transformations
- Want comprehensive mapping test coverage before integration tests

## Instructions

1. **Use Mappers.getMapper()**: Get mapper instances for non-Spring standalone tests
2. **Test bidirectional mapping**: Verify entity→DTO and DTO→entity transformations are symmetric
3. **Test null handling**: Verify null inputs produce null outputs or appropriate defaults
4. **Test nested objects**: Verify nested objects are mapped correctly and independently
5. **Use recursive comparison**: For complex nested structures, use assertThat().usingRecursiveComparison()
6. **Test custom mappings**: Verify @Mapping annotations with custom expressions work correctly
7. **Test enum mappings**: Verify @ValueMapping correctly translates enum values
8. **Test partial updates**: Verify @MappingTarget updates only specified fields

## Examples

## Setup: Testing Mappers

### Maven
```xml
<dependency>
  <groupId>org.mapstruct</groupId>
  <artifactId>mapstruct</artifactId>
  <version>1.5.5.Final</version>
</dependency>
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle
```kotlin
dependencies {
  implementation("org.mapstruct:mapstruct:1.5.5.Final")
  testImplementation("org.junit.jupiter:junit-jupiter")
  testImplementation("org.assertj:assertj-core")
}
```

## Basic Pattern: Testing MapStruct Mapper

### Simple Entity to DTO Mapping

```java
// Mapper interface
@Mapper(componentModel = "spring")
public interface UserMapper {
  UserDto toDto(User user);
  User toEntity(UserDto dto);
  List<UserDto> toDtos(List<User> users);
}

// Unit test
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class UserMapperTest {

  private final UserMapper userMapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapUserToDto() {
    User user = new User(1L, "Alice", "alice@example.com", 25);
    
    UserDto dto = userMapper.toDto(user);
    
    assertThat(dto)
      .isNotNull()
      .extracting("id", "name", "email", "age")
      .containsExactly(1L, "Alice", "alice@example.com", 25);
  }

  @Test
  void shouldMapDtoToEntity() {
    UserDto dto = new UserDto(1L, "Alice", "alice@example.com", 25);
    
    User user = userMapper.toEntity(dto);
    
    assertThat(user)
      .isNotNull()
      .hasFieldOrPropertyWithValue("id", 1L)
      .hasFieldOrPropertyWithValue("name", "Alice");
  }

  @Test
  void shouldMapListOfUsers() {
    List<User> users = List.of(
      new User(1L, "Alice", "alice@example.com", 25),
      new User(2L, "Bob", "bob@example.com", 30)
    );
    
    List<UserDto> dtos = userMapper.toDtos(users);
    
    assertThat(dtos)
      .hasSize(2)
      .extracting(UserDto::getName)
      .containsExactly("Alice", "Bob");
  }

  @Test
  void shouldHandleNullEntity() {
    UserDto dto = userMapper.toDto(null);
    
    assertThat(dto).isNull();
  }
}
```

## Testing Nested Object Mapping

### Map Complex Hierarchies

```java
// Entities with nesting
class User {
  private Long id;
  private String name;
  private Address address;
  private List<Phone> phones;
}

// Mapper with nested mapping
@Mapper(componentModel = "spring")
public interface UserMapper {
  UserDto toDto(User user);
  User toEntity(UserDto dto);
}

// Unit test for nested objects
class NestedObjectMapperTest {

  private final UserMapper userMapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapNestedAddress() {
    Address address = new Address("123 Main St", "New York", "NY", "10001");
    User user = new User(1L, "Alice", address);
    
    UserDto dto = userMapper.toDto(user);
    
    assertThat(dto.getAddress())
      .isNotNull()
      .hasFieldOrPropertyWithValue("street", "123 Main St")
      .hasFieldOrPropertyWithValue("city", "New York");
  }

  @Test
  void shouldMapListOfNestedPhones() {
    List<Phone> phones = List.of(
      new Phone("123-456-7890", "MOBILE"),
      new Phone("987-654-3210", "HOME")
    );
    User user = new User(1L, "Alice", null, phones);
    
    UserDto dto = userMapper.toDto(user);
    
    assertThat(dto.getPhones())
      .hasSize(2)
      .extracting(PhoneDto::getNumber)
      .containsExactly("123-456-7890", "987-654-3210");
  }

  @Test
  void shouldHandleNullNestedObjects() {
    User user = new User(1L, "Alice", null);
    
    UserDto dto = userMapper.toDto(user);
    
    assertThat(dto.getAddress()).isNull();
  }
}
```

For detailed examples covering custom @Mapping annotations, enum mapping, custom type converters, bidirectional mapping round-trips, and partial @MappingTarget updates, see [Examples](references/examples.md).

## Best Practices

- **Test all mapper methods** comprehensively
- **Verify null handling** for every nullable field
- **Test nested objects** independently and together
- **Use recursive comparison** for complex nested structures
- **Test bidirectional mapping** to catch asymmetries
- **Keep mapper tests simple and focused** on transformation correctness
- **Use Mappers.getMapper()** for non-Spring standalone tests

## Common Pitfalls

- Not testing null input cases
- Not verifying nested object mappings
- Assuming bidirectional mapping is symmetric
- Not testing edge cases (empty collections, etc.)
- Tight coupling of mapper tests to MapStruct internals

## Constraints and Warnings

- **MapStruct generates code at compile time**: Tests will fail if mapper doesn't generate correctly
- **Mapper componentModel**: Spring component model requires @Component for dependency injection
- **Null value strategies**: Configure nullValueMappingStrategy and nullValuePropertyMappingStrategy appropriately
- **Collection immutability**: Be aware that mapping immutable collections may require special handling
- **Circular dependencies**: MapStruct cannot handle circular dependencies between mappers
- **Date/Time mapping**: Verify date/time objects map correctly across timezones
- **Expression-based mappings**: Expressions in @Mapping are not validated at compile time

## Troubleshooting

**Null pointer exceptions during mapping**: Check `nullValuePropertyMappingStrategy` and `nullValueCheckStrategy` in `@Mapper`.

**Enum mapping not working**: Verify `@ValueMapping` annotations correctly map source to target values.

**Nested mapping produces null**: Ensure nested mapper interfaces are also mapped in parent mapper.

## References

- [MapStruct Official Documentation](https://mapstruct.org/)
- [MapStruct Mapping Strategies](https://mapstruct.org/documentation/stable/reference/html/)
- [JUnit 5 Best Practices](https://junit.org/junit5/docs/current/user-guide/)
