# Pagination Documentation

## Spring Data Pageable Support

### Basic Pageable Parameter

```java
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

@Operation(summary = "Get paginated list of books")
@GetMapping("/paginated")
public Page<Book> findAllPaginated(
    @ParameterObject Pageable pageable
) {
    return repository.findAll(pageable);
}
```

This generates parameters:
- `page`: Page number (0-based)
- `size`: Page size
- `sort`: Sort criteria (field,direction)

### Custom Pageable Documentation

```java
@Operation(summary = "Get paginated books with custom defaults")
@GetMapping("/paginated")
public Page<Book> getBooksPaginated(
    @ParameterObject
    @Parameter(
        description = "Pagination parameters (default: page=0, size=20, sort=id,asc)",
        example = "page=0&size=20&sort=title,asc"
    )
    Pageable pageable
) {
    return repository.findAll(pageable);
}
```

### Pageable with `@ParameterObject`

```java
@GetMapping("/search")
public Page<Book> searchBooks(
    @Parameter(description = "Search query")
    @RequestParam String query,

    @ParameterObject
    Pageable pageable
) {
    return repository.searchByTitle(query, pageable);
}
```

## Custom Page Response

### Page Metadata

```java
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

@Schema(description = "Paginated response wrapper")
public record PagedResponse<T>(
    @Schema(description = "List of items")
    List<T> content,

    @Schema(description = "Current page number (0-based)", example = "0")
    int currentPage,

    @Schema(description = "Total number of pages", example = "5")
    int totalPages,

    @Schema(description = "Total number of items", example = "100")
    long totalItems,

    @Schema(description = "Number of items per page", example = "20")
    int pageSize,

    @Schema(description = "Whether this is the first page", example = "true")
    boolean isFirst,

    @Schema(description = "Whether this is the last page", example = "false")
    boolean isLast
) {
    public static <T> PagedResponse<T> from(Page<T> page) {
        return new PagedResponse<>(
            page.getContent(),
            page.getNumber(),
            page.getTotalPages(),
            page.getTotalElements(),
            page.getSize(),
            page.isFirst(),
            page.isLast()
        );
    }
}

@Operation(summary = "Get books with custom pagination")
@GetMapping("/paged")
public PagedResponse<Book> getPagedBooks(
    @ParameterObject Pageable pageable
) {
    Page<Book> page = repository.findAll(pageable);
    return PagedResponse.from(page);
}
```

## Slice Documentation

### Using Slice for Large Datasets

```java
import org.springframework.data.domain.Slice;

@Operation(summary = "Get books as slice (no count query)")
@GetMapping("/sliced")
public Slice<Book> getBookSlice(
    @Parameter(description = "Page number (0-based)", example = "0")
    @RequestParam(defaultValue = "0") int page,

    @Parameter(description = "Page size", example = "20")
    @RequestParam(defaultValue = "20") int size
) {
    return repository.findAll(PageRequest.of(page, size));
}
```

## Custom Pagination Objects

### Custom Pagination DTO

```java
@Schema(description = "Pagination request")
public record PaginationRequest(
    @Schema(description = "Page number (0-based)", example = "0", minValue = "0")
    @Min(0)
    int page,

    @Schema(description = "Page size", example = "20", minValue = "1", maxValue = "100")
    @Min(1)
    @Max(100)
    int size,

    @Schema(description = "Sort field", example = "title")
    String sortField,

    @Schema(description = "Sort direction", example = "asc", allowableValues = {"asc", "desc"})
    String sortDirection
) {
    public Pageable toPageable() {
        Sort.Direction direction = Sort.Direction.fromString(sortDirection);
        return PageRequest.of(page, size, Sort.by(direction, sortField));
    }
}

@Operation(summary = "Get books with custom pagination")
@PostMapping("/paginated-custom")
public Page<Book> getBooksCustomPagination(
    @RequestBody PaginationRequest request
) {
    return repository.findAll(request.toPageable());
}
```

## Pagination with Filters

### Filtered Pageable Endpoints

```java
@Operation(summary = "Search books with pagination and filters")
@GetMapping("/search")
public Page<Book> searchBooks(
    @Parameter(description = "Title filter")
    @RequestParam(required = false) String title,

    @Parameter(description = "Author filter")
    @RequestParam(required = false) String author,

    @Parameter(description = "Minimum price")
    @RequestParam(required = false) BigDecimal minPrice,

    @Parameter(description = "Maximum price")
    @RequestParam(required = false) BigDecimal maxPrice,

    @ParameterObject
    Pageable pageable
) {
    return repository.searchBooks(title, author, minPrice, maxPrice, pageable);
}
```

## Pagination Best Practices

1. **Set reasonable defaults**: page=0, size=20
2. **Limit max page size**: Prevent performance issues (max 100)
3. **Document sort options**: List sortable fields in description
4. **Use Slice for large datasets**: Avoid expensive count queries
5. **Include pagination metadata**: Help clients navigate results
6. **Consider cursor-based pagination**: For infinite scroll scenarios

```java
@Operation(
    summary = "Get paginated books",
    description = """
    Returns paginated list of books.

    **Parameters:**
    - `page`: Page number (0-based, default: 0)
    - `size`: Items per page (1-100, default: 20)
    - `sort`: Sort field and direction (e.g., `title,asc` or `price,desc`)

    **Sortable fields:** id, title, author, price, publicationDate
    """
)
@GetMapping("/paginated")
public Page<Book> getPaginatedBooks(
    @ParameterObject
    @Parameter(description = "Pagination and sorting parameters")
    Pageable pageable
) {
    return repository.findAll(pageable);
}
```
