# Mapper & Converter Test Examples

## Setup

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

## Basic Pattern: MapStruct Mapper

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
  UserDto toDto(User user);
  User toEntity(UserDto dto);
  List<UserDto> toDtos(List<User> users);
}

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
    assertThat(userMapper.toDto(null)).isNull();
  }
}
```

## Nested Object Mapping

```java
class User {
  private Long id;
  private String name;
  private Address address;
  private List<Phone> phones;
}

class NestedObjectMapperTest {
  private final UserMapper userMapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapNestedAddress() {
    Address address = new Address("123 Main St", "New York", "NY", "10001");
    User user = new User(1L, "Alice", address);
    UserDto dto = userMapper.toDto(user);
    assertThat(dto.getAddress())
      .isNotNull()
      .hasFieldOrPropertyWithValue("street", "123 Main St");
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
    assertThat(userMapper.toDto(user).getAddress()).isNull();
  }
}
```

## Custom Mapping Methods

```java
@Mapper(componentModel = "spring")
public interface ProductMapper {
  @Mapping(source = "name", target = "productName")
  @Mapping(source = "price", target = "salePrice")
  @Mapping(target = "discount", expression = "java(product.getPrice() * 0.1)")
  ProductDto toDto(Product product);
}

class CustomMappingTest {
  private final ProductMapper mapper = Mappers.getMapper(ProductMapper.class);

  @Test
  void shouldMapFieldsWithCustomNames() {
    Product product = new Product(1L, "Laptop", 999.99);
    ProductDto dto = mapper.toDto(product);
    assertThat(dto)
      .hasFieldOrPropertyWithValue("productName", "Laptop")
      .hasFieldOrPropertyWithValue("salePrice", 999.99);
  }

  @Test
  void shouldCalculateDiscountFromExpression() {
    Product product = new Product(1L, "Laptop", 100.0);
    ProductDto dto = mapper.toDto(product);
    assertThat(dto.getDiscount()).isEqualTo(10.0);
  }
}
```

## Enum Mapping

```java
enum UserStatus { ACTIVE, INACTIVE, SUSPENDED }
enum UserStatusDto { ENABLED, DISABLED, LOCKED }

@Mapper(componentModel = "spring")
public interface StatusMapper {
  @ValueMapping(source = "ACTIVE", target = "ENABLED")
  @ValueMapping(source = "INACTIVE", target = "DISABLED")
  @ValueMapping(source = "SUSPENDED", target = "LOCKED")
  UserStatusDto toStatusDto(UserStatus status);
}

class EnumMapperTest {
  private final StatusMapper mapper = Mappers.getMapper(StatusMapper.class);

  @Test
  void shouldMapActiveToEnabled() {
    assertThat(mapper.toStatusDto(UserStatus.ACTIVE)).isEqualTo(UserStatusDto.ENABLED);
  }

  @Test
  void shouldMapAllEnumValues() {
    for (UserStatus status : UserStatus.values()) {
      assertThat(mapper.toStatusDto(status)).isNotNull();
    }
  }
}
```

## Custom Type Converter

```java
public class DateFormatter {
  private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");

  public static String format(LocalDate date) {
    return date != null ? date.format(formatter) : null;
  }

  public static LocalDate parse(String dateString) {
    return dateString != null ? LocalDate.parse(dateString, formatter) : null;
  }
}

class DateFormatterTest {
  @Test
  void shouldFormatLocalDateToString() {
    assertThat(DateFormatter.format(LocalDate.of(2024, 1, 15))).isEqualTo("2024-01-15");
  }

  @Test
  void shouldParseStringToLocalDate() {
    assertThat(DateFormatter.parse("2024-01-15")).isEqualTo(LocalDate.of(2024, 1, 15));
  }

  @Test
  void shouldHandleNullInFormat() {
    assertThat(DateFormatter.format(null)).isNull();
  }

  @Test
  void shouldThrowOnInvalidDateFormat() {
    assertThatThrownBy(() -> DateFormatter.parse("invalid-date"))
      .isInstanceOf(DateTimeParseException.class);
  }
}
```

## Bidirectional Mapping (Round Trip)

```java
class BidirectionalMapperTest {
  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMaintainDataInRoundTrip() {
    User original = new User(1L, "Alice", "alice@example.com", 25);
    UserDto dto = mapper.toDto(original);
    User restored = mapper.toEntity(dto);
    assertThat(restored)
      .hasFieldOrPropertyWithValue("id", original.getId())
      .hasFieldOrPropertyWithValue("name", original.getName());
  }

  @Test
  void shouldPreserveAllFieldsInBothDirections() {
    Address address = new Address("123 Main", "NYC", "NY", "10001");
    User user = new User(1L, "Alice", "alice@example.com", 25, address);
    UserDto dto = mapper.toDto(user);
    User restored = mapper.toEntity(dto);
    assertThat(restored).usingRecursiveComparison().isEqualTo(user);
  }
}
```

## Partial Mapping (Update)

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
  void updateEntity(@MappingTarget User entity, UserDto dto);
}

class PartialMapperTest {
  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldUpdateExistingEntity() {
    User existing = new User(1L, "Alice", "alice@old.com", 25);
    UserDto dto = new UserDto(1L, "Alice", "alice@new.com", 26);
    mapper.updateEntity(existing, dto);
    assertThat(existing)
      .hasFieldOrPropertyWithValue("email", "alice@new.com")
      .hasFieldOrPropertyWithValue("age", 26);
  }

  @Test
  void shouldNotUpdateFieldsNotInDto() {
    User existing = new User(1L, "Alice", "alice@example.com", 25);
    UserDto dto = new UserDto(1L, "Bob", null, 0);
    mapper.updateEntity(existing, dto);
    assertThat(existing.getEmail()).isEqualTo("alice@example.com");
  }
}
```
