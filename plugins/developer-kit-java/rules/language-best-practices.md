---
globs: "**/*.java"
---
# Rule: Java Best Practices

## Context
Enforce modern Java (17+) and Spring Boot best practices to produce clean, maintainable, and performant code.

## Guidelines

### Dependency Injection
- **Always** use constructor-based injection, never field injection
- Use `@RequiredArgsConstructor` (Lombok) or explicit constructors
- Declare injected fields as `private final`
- Avoid `@Autowired` annotation — constructor injection is implicit with a single constructor

### Modern Java Features (17+)
- Use **Records** for DTOs, value objects, and immutable data carriers
- Use **sealed classes** and **sealed interfaces** for restricted type hierarchies
- Use **pattern matching** for `instanceof` checks
- Use **text blocks** for multi-line strings (SQL, JSON, templates)
- Use **switch expressions** with arrow syntax and pattern matching
- Prefer `var` for local variables when the type is obvious from context

### Collections and Streams
- Prefer `List.of()`, `Set.of()`, `Map.of()` for immutable collections
- Use `Optional` for return types that may be absent — never for fields or parameters
- Use Streams for data transformation pipelines, not for simple iterations
- Avoid nested streams — extract to named methods for readability

### Spring Boot Specific
- Use `@RestController` with `@RequestMapping` at class level
- Return `ResponseEntity<>` from controllers for explicit HTTP status control
- Use `@Valid` for request body validation with Jakarta Validation annotations
- Use `@Transactional` on service methods, not on repository methods
- Prefer `application.yml` over `application.properties`
- Use `@ConfigurationProperties` for type-safe configuration binding

### Code Quality
- Keep methods short (max ~20 lines of logic)
- Favor composition over inheritance
- Use meaningful names — avoid abbreviations (e.g., `customer` not `cust`)
- Annotate nullable parameters/returns with `@Nullable` from `jakarta.annotation`
- Use `Objects.requireNonNull()` for defensive null checks in constructors
- Write `toString()`, `equals()`, and `hashCode()` only when semantically needed (Records handle this automatically)

## Examples

### ✅ Good
```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody OrderRequest request) {
        var order = orderService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(order);
    }
}
```

### ❌ Bad
```java
@RestController
public class OrderController {

    @Autowired
    private OrderService orderService;  // Field injection

    @PostMapping("/api/orders")
    public OrderDTO createOrder(@RequestBody Map<String, Object> request) {  // No validation, raw Map
        return orderService.create(request);
    }
}
```
