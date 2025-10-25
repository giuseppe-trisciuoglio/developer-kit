# Spring Boot REST API Standards - Examples

Comprehensive examples demonstrating REST API design patterns and best practices.

## Example 1: Complete CRUD REST API with Validation

A fully functional REST API with proper request/response handling and validation.

```java
// Controller
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
@Slf4j
public class ProductController {
    private final ProductService productService;

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody CreateProductRequest request) {
        log.info("Creating product: {}", request.name());
        ProductResponse response = productService.create(request);
        return ResponseEntity
            .created(URI.create("/api/v1/products/" + response.id()))
            .body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
        return ResponseEntity.ok(productService.findById(id));
    }

    @GetMapping
    public ResponseEntity<Page<ProductResponse>> getAllProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDirection) {
        
        Pageable pageable = PageRequest.of(page, size, 
            Sort.Direction.valueOf(sortDirection), sortBy);
        return ResponseEntity.ok(productService.findAll(pageable));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable Long id,
            @Valid @RequestBody UpdateProductRequest request) {
        return ResponseEntity.ok(productService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
}

// DTOs with validation
public record CreateProductRequest(
    @NotBlank(message = "Name is required") String name,
    @NotNull(message = "Price is required") 
    @DecimalMin(value = "0.01", message = "Price must be greater than 0") 
    BigDecimal price,
    String description,
    @NotNull(message = "Stock is required") 
    @Min(value = 0, message = "Stock cannot be negative") 
    Integer stock
) {}

public record ProductResponse(
    Long id,
    String name,
    BigDecimal price,
    Integer stock,
    LocalDateTime createdAt
) {}
```

## Example 2: Advanced Error Handling

Comprehensive global exception handler with proper HTTP status codes.

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {
        log.warn("Resource not found: {}", ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(buildErrorResponse(HttpStatus.NOT_FOUND, ex.getMessage(), request));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        String errors = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));

        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(buildErrorResponse(HttpStatus.BAD_REQUEST, errors, request));
    }

    @ExceptionHandler(ConflictException.class)
    public ResponseEntity<ErrorResponse> handleConflict(
            ConflictException ex, HttpServletRequest request) {
        log.warn("Conflict: {}", ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(buildErrorResponse(HttpStatus.CONFLICT, ex.getMessage(), request));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
            Exception ex, HttpServletRequest request) {
        log.error("Unexpected error", ex);
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, 
                "An unexpected error occurred", request));
    }

    private ErrorResponse buildErrorResponse(HttpStatus status, String message, 
                                             HttpServletRequest request) {
        return new ErrorResponse(
            status.value(),
            status.getReasonPhrase(),
            message,
            request.getRequestURI(),
            LocalDateTime.now()
        );
    }
}

record ErrorResponse(
    int status,
    String error,
    String message,
    String path,
    LocalDateTime timestamp
) {}
```

## Example 3: Pagination and Filtering

Advanced search with multiple filter criteria.

```java
@GetMapping("/search")
public ResponseEntity<Page<ProductResponse>> searchProducts(
        @RequestParam(required = false) String name,
        @RequestParam(required = false) BigDecimal minPrice,
        @RequestParam(required = false) BigDecimal maxPrice,
        @RequestParam(required = false) String status,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "DESC") String sortDirection) {
    
    ProductSearchFilter filter = ProductSearchFilter.builder()
        .name(name)
        .minPrice(minPrice)
        .maxPrice(maxPrice)
        .status(status)
        .build();
    
    Pageable pageable = PageRequest.of(page, size, 
        Sort.Direction.valueOf(sortDirection), sortBy);
    
    Page<ProductResponse> results = productService.search(filter, pageable);
    
    return ResponseEntity
        .ok()
        .header("X-Total-Count", String.valueOf(results.getTotalElements()))
        .header("X-Total-Pages", String.valueOf(results.getTotalPages()))
        .body(results);
}

@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductRepository repository;
    
    @Transactional(readOnly = true)
    public Page<ProductResponse> search(ProductSearchFilter filter, Pageable pageable) {
        Specification<Product> spec = Specification.where(null);
        
        if (filter.getName() != null && !filter.getName().isEmpty()) {
            spec = spec.and((root, query, cb) -> 
                cb.like(cb.lower(root.get("name")), 
                    "%" + filter.getName().toLowerCase() + "%"));
        }
        
        if (filter.getMinPrice() != null) {
            spec = spec.and((root, query, cb) -> 
                cb.greaterThanOrEqualTo(root.get("price"), filter.getMinPrice()));
        }
        
        if (filter.getMaxPrice() != null) {
            spec = spec.and((root, query, cb) -> 
                cb.lessThanOrEqualTo(root.get("price"), filter.getMaxPrice()));
        }
        
        return repository.findAll(spec, pageable)
            .map(this::toResponse);
    }
}
```

## Example 4: API Versioning

Managing multiple API versions with proper routing.

```java
// V1 Controller
@RestController
@RequestMapping("/api/v1/products")
public class ProductControllerV1 {
    @GetMapping("/{id}")
    public ResponseEntity<ProductResponseV1> getProduct(@PathVariable Long id) {
        // V1 implementation
        return ResponseEntity.ok(new ProductResponseV1(id, "name", BigDecimal.TEN));
    }
}

// V2 Controller with enhanced response
@RestController
@RequestMapping("/api/v2/products")
public class ProductControllerV2 {
    @GetMapping("/{id}")
    public ResponseEntity<ProductResponseV2> getProduct(@PathVariable Long id) {
        // V2 implementation with additional fields
        return ResponseEntity.ok(new ProductResponseV2(id, "name", BigDecimal.TEN, "category", "description"));
    }
}

// Version detection via Accept header (alternative)
@RestController
@RequestMapping("/api/products")
public class ProductControllerVersioned {
    @GetMapping("/{id}")
    public ResponseEntity<?> getProduct(
            @PathVariable Long id,
            @RequestHeader(value = "Accept", defaultValue = "application/json") String accept) {
        
        if (accept.contains("v2")) {
            return ResponseEntity.ok(new ProductResponseV2(id, "name", BigDecimal.TEN, "cat", "desc"));
        }
        return ResponseEntity.ok(new ProductResponseV1(id, "name", BigDecimal.TEN));
    }
}
```

These examples cover the core patterns for building production-ready REST APIs with Spring Boot.
