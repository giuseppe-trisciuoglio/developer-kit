# Entity Mapping Reference

This document provides detailed information about entity mapping in DynamoDB Enhanced Client.

## @DynamoDbBean Annotation

The `@DynamoDbBean` annotation marks a class as a DynamoDB entity:

```java
@DynamoDbBean
public class Customer {
    // Class implementation
}
```

## Field Annotations

### @DynamoDbPartitionKey
Marks a field as the partition key:

```java
@DynamoDbPartitionKey
public String getCustomerId() {
    return customerId;
}
```

### @DynamoDbSortKey
Marks a field as the sort key (used with composite keys):

```java
@DynamoDbSortKey
@DynamoDbAttribute("order_id")
public String getOrderId() {
    return orderId;
}
```

### @DynamoDbAttribute
Maps a field to a DynamoDB attribute with custom name:

```java
@DynamoDbAttribute("customer_name")
public String getName() {
    return name;
}
```

### @DynamoDbSecondaryPartitionKey
Marks a field as a partition key for a Global Secondary Index:

```java
@DynamoDbSecondaryPartitionKey(indexNames = "category-index")
public String getCategory() {
    return category;
}
```

### @DynamoDbSecondarySortKey
Marks a field as a sort key for a Global Secondary Index:

```java
@DynamoDbSecondarySortKey(indexNames = "category-index")
public BigDecimal getPrice() {
    return price;
}
```

### @DynamoDbConvertedBy
Custom attribute conversion:

```java
@DynamoDbConvertedBy(LocalDateTimeConverter.class)
public LocalDateTime getCreatedAt() {
    return createdAt;
}
```

## Supported Data Types

The enhanced client automatically handles the following data types:

- String → S (String)
- Integer, Long → N (Number)
- BigDecimal → N (Number)
- Boolean → BOOL
- LocalDateTime → S (ISO-8601 format)
- LocalDate → S (ISO-8601 format)
- UUID → S (String)
- Enum → S (String representation)
- Custom types with converters

## Custom Converters

Create custom converters for complex data types:

```java
public class LocalDateTimeConverter extends AttributeConverter<LocalDateTime, String> {

    @Override
    public String transformFrom(LocalDateTime input) {
        return input.toString();
    }

    @Override
    public LocalDateTime transformTo(String input) {
        return LocalDateTime.parse(input);
    }

    @Override
    public AttributeValue transformToAttributeValue(String input) {
        return AttributeValue.builder().s(input).build();
    }

    @Override
    public String transformFromAttributeValue(AttributeValue attributeValue) {
        return attributeValue.s();
    }
}
```