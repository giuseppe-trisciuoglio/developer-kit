# Core Patterns

## Basic Tool Definition

Use `@Tool` annotation to define methods as executable tools:

```java
public class BasicTools {

    @Tool("Add two numbers")
    public int add(@P("first number") int a, @P("second number") int b) {
        return a + b;
    }

    @Tool("Get greeting")
    public String greet(@P("name to greet") String name) {
        return "Hello, " + name + "!";
    }
}
```

## Parameter Descriptions and Validation

Provide clear parameter descriptions using `@P` annotation:

```java
public class WeatherService {

    @Tool("Get current weather conditions")
    public String getCurrentWeather(
        @P("City name or coordinates") String location,
        @P("Temperature unit (celsius, fahrenheit)", required = false) String unit) {

        // Implementation with validation
        if (location == null || location.trim().isEmpty()) {
            return "Location is required";
        }

        return weatherClient.getCurrentWeather(location, unit);
    }
}
```

## Complex Parameter Types

Use Java records and descriptions for complex objects:

```java
public class OrderService {

    @Description("Customer order information")
    public record OrderRequest(
        @Description("Customer ID") String customerId,
        @Description("List of items") List<OrderItem> items,
        @JsonProperty(required = false) @Description("Delivery instructions") String instructions
    ) {}

    @Tool("Create customer order")
    public String createOrder(OrderRequest order) {
        return orderService.processOrder(order);
    }
}
```

## Return Types

Tool methods can return various types:

```java
// Simple types
@Tool("Get current time")
public long getCurrentTime() {
    return System.currentTimeMillis();
}

// JSON/POJO
@Tool("Get user profile")
public UserProfile getUserProfile(@P("User ID") String userId) {
    return userProfileService.findById(userId);
}

// Collections
@Tool("Search products")
public List<Product> searchProducts(@P("Search query") String query) {
    return productService.search(query);
}

// Maps
@Tool("Get system status")
public Map<String, Object> getSystemStatus() {
    return monitoringService.getStatus();
}
```
