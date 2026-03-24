# Model Documentation Patterns

## Entity with Validation

```java
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;

@Entity
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

    @Email(message = "Publisher email must be valid")
    @Schema(description = "Publisher contact email", example = "contact@publisher.com")
    private String publisherEmail;

    // Constructors, getters, setters...
}
```

## Nested Objects

```java
@Schema(description = "Book with publisher details")
public class BookDetail {

    @Schema(description = "Book information")
    private Book book;

    @Schema(description = "Publisher information")
    private Publisher publisher;

    @Schema(description = "Publication details")
    private PublicationInfo publicationInfo;
}

@Schema(description = "Publisher entity")
public class Publisher {
    @Schema(example = "Prentice Hall")
    private String name;

    @Schema(example = "contact@pearson.com")
    private String email;
}
```

## Enum Documentation

```java
public enum BookStatus {
    @Schema(description = "Book is available for purchase")
    AVAILABLE,

    @Schema(description = "Book is out of stock")
    OUT_OF_STOCK,

    @Schema(description = "Book is discontinued")
    DISCONTINUED
}

@Schema(description = "Book entity")
public class Book {
    @Schema(description = "Current book status", example = "AVAILABLE")
    private BookStatus status;
}
```

## Hidden Fields

```java
@Schema(hidden = true)
private String internalField;

@JsonIgnore
@Schema(accessMode = Schema.AccessMode.READ_ONLY)
private LocalDateTime createdAt;

@Schema(description = "Password hash (write-only)", accessMode = Schema.AccessMode.WRITE_ONLY)
private String password;
```

## Read-Only Properties

```java
@Schema(description = "Creation timestamp", accessMode = Schema.AccessMode.READ_ONLY, example = "2024-01-15T10:30:00Z")
private LocalDateTime createdAt;

@Schema(description = "Last update timestamp", accessMode = Schema.AccessMode.READ_ONLY, example = "2024-01-15T10:30:00Z")
private LocalDateTime updatedAt;
```

## Array and Collection Fields

```java
@Schema(description = "List of book tags")
private List<String> tags;

@Schema(description = "Map of book metadata")
private Map<String, String> metadata;

@Schema(description = "Set of book categories")
private Set<Category> categories;
```

## Polymorphic Types

```java
@Schema(description = "Payment method (one of: creditCard, paypal, bankTransfer)")
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.PROPERTY,
    property = "type"
)
@JsonSubTypes({
    @JsonSubTypes.Type(value = CreditCardPayment.class, name = "creditCard"),
    @JsonSubTypes.Type(value = PayPalPayment.class, name = "paypal"),
    @JsonSubTypes.Type(value = BankTransferPayment.class, name = "bankTransfer")
})
public abstract class PaymentMethod {
    @Schema(example = "100.00")
    protected BigDecimal amount;
}
```

## Required vs Optional Fields

```java
@Schema(description = "User profile")
public class UserProfile {

    @NotNull
    @Schema(description = "User first name", example = "John", required = true)
    private String firstName;

    @NotNull
    @Schema(description = "User last name", example = "Doe", required = true)
    private String lastName;

    @Schema(description = "User middle name (optional)", example = "William")
    private String middleName;

    @Schema(description = "User nickname (optional)", example = "Johnny")
    private String nickname;
}
```
