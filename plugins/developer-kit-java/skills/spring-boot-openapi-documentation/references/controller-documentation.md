# Controller Documentation Patterns

## Basic Controller Documentation

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/books")
@Tag(name = "Book", description = "Book management APIs")
public class BookController {

    @Operation(
        summary = "Retrieve a book by ID",
        description = "Get a Book object by specifying its ID. The response includes id, title, author and description."
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved book",
            content = @Content(schema = @Schema(implementation = Book.class))
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found"
        )
    })
    @GetMapping("/{id}")
    public Book findById(
        @Parameter(description = "ID of book to retrieve", required = true)
        @PathVariable Long id
    ) {
        return repository.findById(id)
            .orElseThrow(() -> new BookNotFoundException());
    }
}
```

## Document Request Bodies

```java
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import io.swagger.v3.oas.annotations.media.ExampleObject;

@Operation(summary = "Create a new book")
@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public Book createBook(
    @RequestBody(
        description = "Book to create",
        required = true,
        content = @Content(
            schema = @Schema(implementation = Book.class),
            examples = @ExampleObject(
                value = """
                {
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "isbn": "978-0132350884",
                    "description": "A handbook of agile software craftsmanship"
                }
                """
            )
        )
    )
    Book book
) {
    return repository.save(book);
}
```

## Multiple Response Types

```java
@Operation(summary = "Search books")
@ApiResponses(value = {
    @ApiResponse(
        responseCode = "200",
        description = "Search completed",
        content = @Content(
            array = @ArraySchema(schema = @Schema(implementation = Book.class))
        )
    ),
    @ApiResponse(
        responseCode = "400",
        description = "Invalid search parameters",
        content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
})
@GetMapping("/search")
public List<Book> searchBooks(
    @Parameter(description = "Search query")
    @RequestParam String query
) {
    return service.search(query);
}
```

## Document Parameters

```java
@GetMapping("/filtered")
public List<Book> filterBooks(
    @Parameter(description = "Title filter", example = "Clean Code")
    @RequestParam(required = false) String title,

    @Parameter(description = "Author filter", example = "Robert C. Martin")
    @RequestParam(required = false) String author,

    @Parameter(description = "Minimum publication year", example = "2000")
    @RequestParam(required = false) Integer fromYear
) {
    return service.filter(title, author, fromYear);
}
```

## Document Matrix Parameters

```java
@Operation(summary = "Get book attributes")
@GetMapping("/{id}/attributes/{attributeType}")
public BookAttribute getAttribute(
    @Parameter(description = "Book ID", required = true)
    @PathVariable Long id,

    @Parameter(description = "Attribute type (metadata, reviews, ratings)", required = true)
    @PathVariable String attributeType
) {
    return service.getAttribute(id, attributeType);
}
```

## Document Headers

```java
@Operation(summary = "Get authenticated user profile")
@GetMapping("/profile")
public UserProfile getProfile(
    @Parameter(description = "Authorization token", required = true, example = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    @RequestHeader("Authorization") String authorization
) {
    return service.getProfile(authorization);
}
```
