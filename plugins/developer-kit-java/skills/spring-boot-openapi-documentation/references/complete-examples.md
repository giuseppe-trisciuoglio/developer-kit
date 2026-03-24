# Complete REST Controller Example

## Full-Featured Book Controller

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/books")
@Tag(name = "Book", description = "Book management APIs")
@SecurityRequirement(name = "bearer-jwt")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @Operation(summary = "Get all books")
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Found all books",
            content = @Content(
                mediaType = "application/json",
                array = @ArraySchema(schema = @Schema(implementation = Book.class))
            )
        )
    })
    @GetMapping
    public List<Book> getAllBooks() {
        return bookService.getAllBooks();
    }

    @Operation(summary = "Get paginated books")
    @GetMapping("/paginated")
    public Page<Book> getBooksPaginated(@ParameterObject Pageable pageable) {
        return bookService.getBooksPaginated(pageable);
    }

    @Operation(summary = "Get book by ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Book found"),
        @ApiResponse(responseCode = "404", description = "Book not found")
    })
    @GetMapping("/{id}")
    public Book getBookById(
        @Parameter(description = "Book ID", required = true, example = "1")
        @PathVariable Long id
    ) {
        return bookService.getBookById(id);
    }

    @Operation(summary = "Create new book")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Book created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid input")
    })
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Book createBook(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "Book to create",
            required = true,
            content = @Content(
                schema = @Schema(implementation = Book.class),
                examples = @io.swagger.v3.oas.annotations.media.ExampleObject(
                    value = """
                        {
                            "title": "Clean Code",
                            "author": "Robert C. Martin",
                            "isbn": "978-0132350884",
                            "price": 29.99,
                            "publicationDate": "2008-08-01"
                        }
                        """
                )
            )
        )
        @Valid @RequestBody Book book
    ) {
        return bookService.createBook(book);
    }

    @Operation(summary = "Update book")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Book updated"),
        @ApiResponse(responseCode = "404", description = "Book not found"),
        @ApiResponse(responseCode = "400", description = "Invalid input")
    })
    @PutMapping("/{id}")
    public Book updateBook(
        @Parameter(description = "Book ID", required = true)
        @PathVariable Long id,
        @Valid @RequestBody Book book
    ) {
        return bookService.updateBook(id, book);
    }

    @Operation(summary = "Delete book")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "Book deleted"),
        @ApiResponse(responseCode = "404", description = "Book not found")
    })
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteBook(@PathVariable Long id) {
        bookService.deleteBook(id);
    }

    @Operation(summary = "Search books by title")
    @GetMapping("/search")
    public Page<Book> searchBooks(
        @Parameter(description = "Search query", example = "Clean")
        @RequestParam String query,
        @ParameterObject Pageable pageable
    ) {
        return bookService.searchBooks(query, pageable);
    }
}
```

## Complete Book Entity

```java
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "books")
@Schema(description = "Book entity representing a published book")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Schema(description = "Unique identifier", example = "1", accessMode = Schema.AccessMode.READ_ONLY)
    private Long id;

    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 200)
    @Schema(description = "Book title", example = "Clean Code", required = true, maxLength = 200)
    private String title;

    @NotBlank(message = "Author is required")
    @Schema(description = "Book author", example = "Robert C. Martin", required = true)
    private String author;

    @Pattern(regexp = "^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")
    @Schema(description = "ISBN number", example = "978-0132350884")
    private String isbn;

    @Min(value = 0, message = "Price must be positive")
    @Schema(description = "Book price in USD", example = "29.99", minimum = "0")
    private BigDecimal price;

    @Past(message = "Publication date must be in the past")
    @Schema(description = "Publication date", example = "2008-08-01")
    private LocalDate publicationDate;

    @Schema(description = "Book description", example = "A handbook of agile software craftsmanship")
    private String description;

    @Email(message = "Publisher email must be valid")
    @Schema(description = "Publisher contact email", example = "contact@publisher.com")
    private String publisherEmail;

    // Constructors, getters, setters...
}
```

## Complete Configuration Class

```java
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenAPIConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .components(new Components()
                .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                    .type(SecurityScheme.Type.HTTP)
                    .scheme("bearer")
                    .bearerFormat("JWT")
                    .description("JWT authentication - Enter token without 'Bearer' prefix")
                )
            )
            .info(new Info()
                .title("Book Management API")
                .description("Comprehensive API for managing books, authors, and publishers")
                .version("v1.0.0")
                .contact(new Contact()
                    .name("API Support")
                    .email("support@example.com")
                    .url("https://example.com/support")
                )
                .license(new License()
                    .name("MIT License")
                    .url("https://opensource.org/licenses/MIT")
                )
            );
    }
}
```

## Complete Application Properties

```yaml
# application.yml
spring:
  application:
    name: book-management-api

springdoc:
  api-docs:
    path: /api-docs
    enabled: true
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
    operationsSorter: method
    tagsSorter: alpha
    tryItOutEnabled: true
    displayRequestDuration: true
    displayOperationId: false
    defaultModelsExpandDepth: 1
    defaultModelExpandDepth: 1
  packages-to-scan: com.example.controller
  paths-to-match: /api/**
  show-actuator: false

server:
  port: 8080

logging:
  level:
    org.springdoc: DEBUG
```

## Complete Security Configuration

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-ui.html").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

## Maven pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>book-management-api</artifactId>
    <version>1.0.0</version>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <properties>
        <java.version>17</java.version>
        <springdoc.version>2.8.13</springdoc.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>${springdoc.version}</version>
        </dependency>

        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```
