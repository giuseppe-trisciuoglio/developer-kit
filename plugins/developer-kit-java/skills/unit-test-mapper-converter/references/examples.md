# Mapper and Converter Testing - Detailed Examples

## Testing Custom Mapping Methods

### Mapper with @Mapping Annotations

```java
@Mapper(componentModel = "spring")
public interface ProductMapper {
  @Mapping(source = "name", target = "productName")
  @Mapping(source = "price", target = "salePrice")
  @Mapping(target = "discount", expression = "java(product.getPrice() * 0.1)")
  ProductDto toDto(Product product);

  @Mapping(source = "productName", target = "name")
  @Mapping(source = "salePrice", target = "price")
  Product toEntity(ProductDto dto);
}

import org.mapstruct.factory.Mappers;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

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

  @Test
  void shouldReverseMapCustomFields() {
    ProductDto dto = new ProductDto(1L, "Laptop", 999.99);
    Product product = mapper.toEntity(dto);
    assertThat(product)
      .hasFieldOrPropertyWithValue("name", "Laptop")
      .hasFieldOrPropertyWithValue("price", 999.99);
  }
}
```

## Testing Enum Mapping

### Map Enums Between Entity and DTO

```java
enum UserStatus { ACTIVE, INACTIVE, SUSPENDED }
enum UserStatusDto { ENABLED, DISABLED, LOCKED }

@Mapper(componentModel = "spring")
public interface UserMapper {
  @ValueMapping(source = "ACTIVE", target = "ENABLED")
  @ValueMapping(source = "INACTIVE", target = "DISABLED")
  @ValueMapping(source = "SUSPENDED", target = "LOCKED")
  UserStatusDto toStatusDto(UserStatus status);
}

import org.mapstruct.factory.Mappers;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class EnumMapperTest {

  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapActiveToEnabled() {
    UserStatusDto dto = mapper.toStatusDto(UserStatus.ACTIVE);
    assertThat(dto).isEqualTo(UserStatusDto.ENABLED);
  }

  @Test
  void shouldMapSuspendedToLocked() {
    UserStatusDto dto = mapper.toStatusDto(UserStatus.SUSPENDED);
    assertThat(dto).isEqualTo(UserStatusDto.LOCKED);
  }
}
```

## Testing Custom Type Conversions

### Non-MapStruct Custom Converter

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

import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
import java.time.format.DateTimeParseException;

class DateFormatterTest {

  @Test
  void shouldFormatLocalDateToString() {
    LocalDate date = LocalDate.of(2024, 1, 15);
    String result = DateFormatter.format(date);
    assertThat(result).isEqualTo("2024-01-15");
  }

  @Test
  void shouldParseStringToLocalDate() {
    String dateString = "2024-01-15";
    LocalDate result = DateFormatter.parse(dateString);
    assertThat(result).isEqualTo(LocalDate.of(2024, 1, 15));
  }

  @Test
  void shouldHandleNullInFormat() {
    String result = DateFormatter.format(null);
    assertThat(result).isNull();
  }

  @Test
  void shouldHandleInvalidDateFormat() {
    assertThatThrownBy(() -> DateFormatter.parse("invalid-date"))
      .isInstanceOf(DateTimeParseException.class);
  }
}
```

## Testing Bidirectional Mapping

### Entity to DTO Round Trip

```java
import org.mapstruct.factory.Mappers;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class BidirectionalMapperTest {

  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMaintainDataInRoundTrip() {
    User original = new User(1L, "Alice", "alice@example.com", 25);
    UserDto dto = mapper.toDto(original);
    User restored = mapper.toEntity(dto);
    assertThat(restored)
      .hasFieldOrPropertyWithValue("id", original.getId())
      .hasFieldOrPropertyWithValue("name", original.getName())
      .hasFieldOrPropertyWithValue("email", original.getEmail())
      .hasFieldOrPropertyWithValue("age", original.getAge());
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

## Testing Partial Mapping

### Update Existing Entity from DTO

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
  void updateEntity(@MappingTarget User entity, UserDto dto);
}

import org.mapstruct.factory.Mappers;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

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
