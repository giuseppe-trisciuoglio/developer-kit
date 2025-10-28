# Pagination and Filtering Reference

## Pagination with Spring Data

### Basic Pagination
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<UserResponse>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<UserResponse> users = userService.findAll(pageable);
        return ResponseEntity.ok(users);
    }
}
```

### Pagination with Sorting
```java
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getAllUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "DESC") String sortDirection) {

    Sort sort = Sort.by(Sort.Direction.fromString(sortDirection), sortBy);
    Pageable pageable = PageRequest.of(page, size, sort);
    Page<UserResponse> users = userService.findAll(pageable);
    return ResponseEntity.ok(users);
}
```

### Multi-field Sorting
```java
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getAllUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "name") String sortBy,
        @RequestParam(defaultValue = "name,createdAt") String sortFields) {

    List<Sort.Order> orders = Arrays.stream(sortFields.split(","))
        .map(field -> {
            String direction = field.startsWith("-") ? "DESC" : "ASC";
            String property = field.startsWith("-") ? field.substring(1) : field;
            return new Sort.Order(Sort.Direction.fromString(direction), property);
        })
        .collect(Collectors.toList());

    Pageable pageable = PageRequest.of(page, size, Sort.by(orders));
    Page<UserResponse> users = userService.findAll(pageable);
    return ResponseEntity.ok(users);
}
```

## Response Format

### Standard Page Response
```json
{
  "content": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "pageable": {
    "sort": {
      "empty": false,
      "sorted": true,
      "unsorted": false
    },
    "offset": 0,
    "pageNumber": 0,
    "pageSize": 10,
    "paged": true,
    "unpaged": false
  },
  "last": false,
  "totalPages": 5,
  "totalElements": 45,
  "size": 10,
  "number": 0,
  "sort": {
    "empty": false,
    "sorted": true,
    "unsorted": false
  },
  "first": true,
  "numberOfElements": 10,
  "empty": false
}
```

### Custom Page Response Wrapper
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PageResponse<T> {
    private List<T> content;
    private PageMetadata metadata;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PageMetadata {
    private int pageNumber;
    private int pageSize;
    private long totalElements;
    private int totalPages;
    private boolean first;
    private boolean last;
}

// Controller
@GetMapping("/users")
public ResponseEntity<PageResponse<UserResponse>> getAllUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size) {
    Page<User> pageResult = userService.findAll(pageable);

    PageMetadata metadata = new PageMetadata(
        page,
        size,
        pageResult.getTotalElements(),
        pageResult.getTotalPages(),
        pageResult.isFirst(),
        pageResult.isLast()
    );

    PageResponse<UserResponse> response = new PageResponse<>(
        pageResult.stream()
            .map(this::toResponse)
            .collect(Collectors.toList()),
        metadata
    );

    return ResponseEntity.ok(response);
}
```

## Filtering

### Query Parameter Filtering
```java
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getUsers(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) String email,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size) {

    Specification<User> spec = Specification.where(null);

    if (name != null && !name.isEmpty()) {
        spec = spec.and((root, query, cb) ->
            cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%"));
    }

    if (email != null && !email.isEmpty()) {
        spec = spec.and((root, query, cb) ->
            cb.like(cb.lower(root.get("email")), "%" + email.toLowerCase() + "%"));
    }

    Pageable pageable = PageRequest.of(page, size);
    Page<User> pageResult = userService.findAll(spec, pageable);

    return ResponseEntity.ok(pageResult.map(this::toResponse));
}
```

### Dynamic Specification Builder
```java
public class UserSpecifications {

    public static Specification<User> hasName(String name) {
        return (root, query, cb) ->
            name == null ? null :
            cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%");
    }

    public static Specification<User> hasEmail(String email) {
        return (root, query, cb) ->
            email == null ? null :
            cb.like(cb.lower(root.get("email")), "%" + email.toLowerCase() + "%");
    }

    public static Specification<User> isActive(Boolean active) {
        return (root, query, cb) ->
            active == null ? null :
            cb.equal(root.get("active"), active);
    }

    public static Specification<User> createdAfter(LocalDate date) {
        return (root, query, cb) ->
            date == null ? null :
            cb.greaterThanOrEqualTo(root.get("createdAt"), date.atStartOfDay());
    }
}

// Usage
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getUsers(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) String email,
        @RequestParam(required = false) Boolean active,
        @RequestParam(required = false) LocalDate createdAfter,
        Pageable pageable) {

    Specification<User> spec = Specification.where(UserSpecifications.hasName(name))
        .and(UserSpecifications.hasEmail(email))
        .and(UserSpecifications.isActive(active))
        .and(UserSpecifications.createdAfter(createdAfter));

    Page<User> pageResult = userService.findAll(spec, pageable);
    return ResponseEntity.ok(pageResult.map(this::toResponse));
}
```

### Date Range Filtering
```java
@GetMapping("/orders")
public ResponseEntity<Page<OrderResponse>> getOrders(
        @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
        @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
        Pageable pageable) {

    Specification<Order> spec = Specification.where(null);

    if (startDate != null) {
        spec = spec.and((root, query, cb) ->
            cb.greaterThanOrEqualTo(root.get("createdAt"), startDate.atStartOfDay()));
    }

    if (endDate != null) {
        spec = spec.and((root, query, cb) ->
            cb.lessThanOrEqualTo(root.get("createdAt"), endDate.atEndOfDay()));
    }

    Page<Order> pageResult = orderService.findAll(spec, pageable);
    return ResponseEntity.ok(pageResult.map(this::toResponse));
}
```

## Advanced Filtering

### Filter DTO Pattern
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserFilter {
    private String name;
    private String email;
    private Boolean active;
    private LocalDate createdAfter;
    private LocalDate createdBefore;
    private List<Long> roleIds;

    public Specification<User> toSpecification() {
        Specification<User> spec = Specification.where(null);

        if (name != null && !name.isEmpty()) {
            spec = spec.and(hasName(name));
        }

        if (email != null && !email.isEmpty()) {
            spec = spec.and(hasEmail(email));
        }

        if (active != null) {
            spec = spec.and(isActive(active));
        }

        if (createdAfter != null) {
            spec = spec.and(createdAfter(createdAfter));
        }

        if (createdBefore != null) {
            spec = spec.and(createdBefore(createdBefore));
        }

        if (roleIds != null && !roleIds.isEmpty()) {
            spec = spec.and(hasRoles(roleIds));
        }

        return spec;
    }
}

// Controller
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getUsers(
        UserFilter filter,
        Pageable pageable) {

    Specification<User> spec = filter.toSpecification();
    Page<User> pageResult = userService.findAll(spec, pageable);
    return ResponseEntity.ok(pageResult.map(this::toResponse));
}
```

## Link Headers for Pagination

```java
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getAllUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        Pageable pageable) {

    Page<UserResponse> pageResult = userService.findAll(pageable);

    HttpHeaders headers = new HttpHeaders();
    headers.add("X-Total-Count", String.valueOf(pageResult.getTotalElements()));
    headers.add("X-Total-Pages", String.valueOf(pageResult.getTotalPages()));
    headers.add("X-Page-Number", String.valueOf(pageResult.getNumber()));
    headers.add("X-Page-Size", String.valueOf(pageResult.getSize()));

    // Link headers for pagination
    if (pageResult.hasNext()) {
        headers.add("Link", buildLinkHeader(pageResult.getNumber() + 1, size));
    }
    if (pageResult.hasPrevious()) {
        headers.add("Link", buildLinkHeader(pageResult.getNumber() - 1, size));
    }

    return ResponseEntity.ok()
        .headers(headers)
        .body(pageResult);
}

private String buildLinkHeader(int page, int size) {
    return String.format("<%s/api/users?page=%d&size=%d>; rel=\"next\"",
        baseUrl, page, size);
}
```

## Performance Considerations

### Database Optimization
```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public Page<UserResponse> findAll(Specification<User> spec, Pageable pageable) {
        // Use projection to only fetch needed fields
        Page<User> page = userRepository.findAll(spec, pageable);
        return page.stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
    }
}
```

### Cache Pagination Results
```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final CacheManager cacheManager;

    public Page<UserResponse> findAll(Specification<User> spec, Pageable pageable) {
        String cacheKey = "users:" + spec.hashCode() + ":" + pageable.hashCode();

        return cacheManager.getCache("users").get(cacheKey, () -> {
            Page<User> page = userRepository.findAll(spec, pageable);
            return page.map(this::toResponse);
        });
    }
}
```