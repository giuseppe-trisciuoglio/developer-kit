# SpringDoc OpenAPI Examples

## Complete E-commerce API Example

This example demonstrates a comprehensive e-commerce API with full OpenAPI documentation.

### Project Structure

```
ecommerce-api/
├── src/main/java/com/ecommerce/
│   ├── config/
│   │   ├── OpenApiConfig.java
│   │   └── SecurityConfig.java
│   ├── controller/
│   │   ├── ProductController.java
│   │   ├── OrderController.java
│   │   └── UserController.java
│   ├── dto/
│   │   ├── request/
│   │   │   ├── ProductCreateRequest.java
│   │   │   ├── OrderCreateRequest.java
│   │   │   └── UserRegistrationRequest.java
│   │   └── response/
│   │       ├── ProductResponse.java
│   │       ├── OrderResponse.java
│   │       └── UserResponse.java
│   ├── exception/
│   │   ├── GlobalExceptionHandler.java
│   │   └── ErrorResponse.java
│   └── model/
│       ├── Product.java
│       ├── Order.java
│       └── User.java
└── src/main/resources/
    └── application.yml
```

### Configuration

**pom.xml**
```xml
<dependencies>
    <!-- Spring Boot Starter Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- SpringDoc OpenAPI -->
    <dependency>
        <groupId>org.springdoc</groupId>
        <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
        <version>2.8.13</version>
    </dependency>
    
    <!-- Validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    
    <!-- Spring Security (optional) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    
    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

**application.yml**
```yaml
server:
  port: 8080

spring:
  application:
    name: ecommerce-api

# SpringDoc OpenAPI Configuration
springdoc:
  api-docs:
    enabled: true
    path: /v3/api-docs
  swagger-ui:
    enabled: true
    path: /swagger-ui.html
    operations-sorter: method
    tags-sorter: alpha
    try-it-out-enabled: true
    filter: true
    display-request-duration: true
    default-models-expand-depth: 2
    default-model-expand-depth: 2
  packages-to-scan: com.ecommerce.controller
  paths-to-match: /api/**
  show-actuator: false
  writer-with-default-pretty-printer: true

# Logging
logging:
  level:
    com.ecommerce: DEBUG
    org.springdoc: INFO
```

### OpenAPI Configuration

**OpenApiConfig.java**
```java
package com.ecommerce.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeIn;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.License;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.annotations.servers.Server;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.media.StringSchema;
import io.swagger.v3.oas.models.parameters.HeaderParameter;
import org.springdoc.core.customizers.OpenApiCustomizer;
import org.springdoc.core.customizers.OperationCustomizer;
import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "E-commerce API",
        version = "1.0.0",
        description = """
            RESTful API for e-commerce platform providing product catalog,
            order management, and user authentication services.
            
            ## Features
            - Product catalog management
            - Order processing and tracking
            - User registration and authentication
            - JWT-based security
            
            ## Authentication
            All endpoints except registration and login require JWT authentication.
            Include the JWT token in the Authorization header: `Bearer <token>`
            """,
        termsOfService = "https://example.com/terms",
        contact = @Contact(
            name = "API Support Team",
            email = "api-support@example.com",
            url = "https://example.com/support"
        ),
        license = @License(
            name = "Apache 2.0",
            url = "https://www.apache.org/licenses/LICENSE-2.0.html"
        )
    ),
    servers = {
        @Server(
            url = "https://api.example.com",
            description = "Production server"
        ),
        @Server(
            url = "https://staging-api.example.com",
            description = "Staging server"
        ),
        @Server(
            url = "http://localhost:8080",
            description = "Local development server"
        )
    },
    security = {
        @SecurityRequirement(name = "bearerAuth")
    }
)
@SecurityScheme(
    name = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT",
    description = "JWT authentication token. Obtain from /api/auth/login endpoint."
)
@SecurityScheme(
    name = "apiKey",
    type = SecuritySchemeType.APIKEY,
    in = SecuritySchemeIn.HEADER,
    paramName = "X-API-Key",
    description = "API Key for service-to-service authentication"
)
public class OpenApiConfig {
    
    @Bean
    public GroupedOpenApi publicApi() {
        return GroupedOpenApi.builder()
            .group("public")
            .displayName("Public API")
            .pathsToMatch("/api/public/**")
            .addOpenApiCustomizer(publicApiCustomizer())
            .build();
    }
    
    @Bean
    public GroupedOpenApi productsApi() {
        return GroupedOpenApi.builder()
            .group("products")
            .displayName("Product Management")
            .pathsToMatch("/api/products/**")
            .addOpenApiCustomizer(openApi -> {
                openApi.getInfo()
                    .title("Product Management API")
                    .description("APIs for managing product catalog");
            })
            .build();
    }
    
    @Bean
    public GroupedOpenApi ordersApi() {
        return GroupedOpenApi.builder()
            .group("orders")
            .displayName("Order Management")
            .pathsToMatch("/api/orders/**")
            .addOpenApiCustomizer(openApi -> {
                openApi.getInfo()
                    .title("Order Management API")
                    .description("APIs for order processing and tracking");
            })
            .build();
    }
    
    @Bean
    public GroupedOpenApi adminApi() {
        return GroupedOpenApi.builder()
            .group("admin")
            .displayName("Admin API")
            .pathsToMatch("/api/admin/**")
            .addOpenApiCustomizer(openApi -> {
                openApi.getInfo()
                    .title("Admin API")
                    .description("Administrative endpoints - requires elevated permissions");
                openApi.addSecurityItem(new io.swagger.v3.oas.models.security.SecurityRequirement()
                    .addList("bearerAuth"));
            })
            .build();
    }
    
    @Bean
    public OpenApiCustomizer publicApiCustomizer() {
        return openApi -> {
            openApi.getInfo()
                .title("Public E-commerce API")
                .description("Publicly accessible endpoints - no authentication required");
            
            // Remove security requirements for public API
            openApi.setSecurity(null);
        };
    }
    
    @Bean
    public OpenApiCustomizer globalOpenApiCustomizer() {
        return openApi -> {
            // Add custom extension
            openApi.addExtension("x-api-id", "ecommerce-api-v1");
            openApi.addExtension("x-audience", "external");
            
            // Add global headers
            openApi.getPaths().values().forEach(pathItem -> {
                pathItem.readOperations().forEach(operation -> {
                    operation.addParametersItem(new HeaderParameter()
                        .name("X-Request-ID")
                        .description("Unique request identifier for tracing")
                        .required(false)
                        .schema(new StringSchema()
                            .pattern("^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
                            .example("550e8400-e29b-41d4-a716-446655440000")));
                });
            });
        };
    }
    
    @Bean
    public OperationCustomizer customOperationCustomizer() {
        return (operation, handlerMethod) -> {
            // Add response time extension
            operation.addExtension("x-expected-response-time", "< 500ms");
            
            // Add custom tags based on package
            String packageName = handlerMethod.getBeanType().getPackageName();
            if (packageName.contains("admin")) {
                operation.addTagsItem("Admin Operations");
            }
            
            return operation;
        };
    }
}
```

### DTOs with Validation

**ProductCreateRequest.java**
```java
package com.ecommerce.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;
import lombok.Builder;
import lombok.Value;
import java.math.BigDecimal;
import java.util.Set;

@Value
@Builder
@Schema(
    description = "Request payload for creating a new product",
    example = """
        {
          "name": "Wireless Bluetooth Headphones",
          "sku": "PROD-12345",
          "description": "Premium noise-cancelling headphones",
          "price": 299.99,
          "quantity": 100,
          "category": "Electronics",
          "tags": ["bluetooth", "wireless", "audio"],
          "images": ["https://example.com/image1.jpg"]
        }
        """
)
public class ProductCreateRequest {
    
    @NotNull(message = "Product name is required")
    @Size(min = 3, max = 200, message = "Product name must be between 3 and 200 characters")
    @Schema(
        description = "Product name",
        example = "Wireless Bluetooth Headphones",
        required = true,
        minLength = 3,
        maxLength = 200
    )
    String name;
    
    @NotBlank(message = "SKU is required")
    @Pattern(
        regexp = "^[A-Z0-9-]+$",
        message = "SKU must contain only uppercase letters, numbers, and hyphens"
    )
    @Schema(
        description = "Stock Keeping Unit - unique product identifier",
        example = "PROD-12345",
        required = true,
        pattern = "^[A-Z0-9-]+$"
    )
    String sku;
    
    @Size(max = 2000, message = "Description cannot exceed 2000 characters")
    @Schema(
        description = "Detailed product description",
        example = "Premium noise-cancelling wireless headphones with 30-hour battery life",
        maxLength = 2000
    )
    String description;
    
    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.01", message = "Price must be greater than 0")
    @DecimalMax(value = "999999.99", message = "Price cannot exceed 999,999.99")
    @Schema(
        description = "Product price in USD",
        example = "299.99",
        required = true,
        minimum = "0.01",
        maximum = "999999.99",
        type = "number",
        format = "decimal"
    )
    BigDecimal price;
    
    @NotNull(message = "Quantity is required")
    @Min(value = 0, message = "Quantity cannot be negative")
    @Max(value = 100000, message = "Quantity cannot exceed 100,000")
    @Schema(
        description = "Available stock quantity",
        example = "100",
        required = true,
        minimum = "0",
        maximum = "100000"
    )
    Integer quantity;
    
    @NotBlank(message = "Category is required")
    @Schema(
        description = "Product category",
        example = "Electronics",
        required = true,
        allowableValues = {
            "Electronics", "Clothing", "Books", "Home & Garden",
            "Sports", "Toys", "Food & Beverage"
        }
    )
    String category;
    
    @Size(max = 10, message = "Maximum 10 tags allowed")
    @Schema(
        description = "Product tags for search and filtering",
        example = "[\"bluetooth\", \"wireless\", \"audio\"]",
        maxItems = 10
    )
    Set<@NotBlank @Size(max = 50) String> tags;
    
    @Size(max = 5, message = "Maximum 5 images allowed")
    @Schema(
        description = "Product image URLs",
        example = "[\"https://example.com/image1.jpg\", \"https://example.com/image2.jpg\"]",
        maxItems = 5
    )
    Set<@NotBlank @Pattern(regexp = "^https?://.*\\.(jpg|jpeg|png|gif)$") String> images;
    
    @Schema(
        description = "Product attributes (size, color, material, etc.)",
        example = "{\"color\": \"Black\", \"size\": \"Medium\"}",
        additionalProperties = Schema.AdditionalPropertiesValue.TRUE
    )
    java.util.Map<String, String> attributes;
}
```

**ProductResponse.java**
```java
package com.ecommerce.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Value;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Set;

@Value
@Builder
@Schema(description = "Product information response")
public class ProductResponse {
    
    @Schema(description = "Product unique identifier", example = "1", accessMode = Schema.AccessMode.READ_ONLY)
    Long id;
    
    @Schema(description = "Product name", example = "Wireless Bluetooth Headphones")
    String name;
    
    @Schema(description = "Stock Keeping Unit", example = "PROD-12345")
    String sku;
    
    @Schema(description = "Product description", example = "Premium noise-cancelling headphones")
    String description;
    
    @Schema(description = "Product price in USD", example = "299.99")
    BigDecimal price;
    
    @Schema(description = "Available quantity", example = "100")
    Integer quantity;
    
    @Schema(description = "Product category", example = "Electronics")
    String category;
    
    @Schema(description = "Product tags", example = "[\"bluetooth\", \"wireless\"]")
    Set<String> tags;
    
    @Schema(description = "Product image URLs")
    Set<String> images;
    
    @Schema(description = "Product attributes")
    Map<String, String> attributes;
    
    @Schema(description = "Product status", example = "ACTIVE", allowableValues = {"ACTIVE", "INACTIVE", "OUT_OF_STOCK"})
    String status;
    
    @Schema(description = "Creation timestamp", example = "2024-01-15T10:30:00", accessMode = Schema.AccessMode.READ_ONLY)
    LocalDateTime createdAt;
    
    @Schema(description = "Last update timestamp", example = "2024-01-20T14:45:00", accessMode = Schema.AccessMode.READ_ONLY)
    LocalDateTime updatedAt;
}
```

### Controllers with Full Documentation

**ProductController.java**
```java
package com.ecommerce.controller;

import com.ecommerce.dto.request.ProductCreateRequest;
import com.ecommerce.dto.request.ProductUpdateRequest;
import com.ecommerce.dto.response.ProductResponse;
import com.ecommerce.exception.ErrorResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.Parameters;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import io.swagger.v3.oas.annotations.headers.Header;
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Validated
@Tag(
    name = "Product Management",
    description = "APIs for managing product catalog including CRUD operations, search, and filtering"
)
public class ProductController {
    
    private final ProductService productService;
    
    @GetMapping
    @Operation(
        summary = "Get all products",
        description = """
            Retrieves a paginated list of products with optional filtering and sorting.
            
            Supports:
            - Pagination (page, size)
            - Sorting (sort parameter)
            - Filtering by category, price range, status
            - Search by name or SKU
            """,
        tags = {"Product Management"}
    )
    @Parameters({
        @Parameter(
            name = "page",
            description = "Page number (0-based)",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "integer", defaultValue = "0", minimum = "0")
        ),
        @Parameter(
            name = "size",
            description = "Number of items per page",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "integer", defaultValue = "20", minimum = "1", maximum = "100")
        ),
        @Parameter(
            name = "sort",
            description = "Sort criteria in format: property(,asc|desc). Multiple sort criteria supported.",
            in = ParameterIn.QUERY,
            example = "name,asc",
            schema = @Schema(type = "string")
        ),
        @Parameter(
            name = "category",
            description = "Filter by product category",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "string")
        ),
        @Parameter(
            name = "minPrice",
            description = "Minimum price filter",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "number", format = "decimal")
        ),
        @Parameter(
            name = "maxPrice",
            description = "Maximum price filter",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "number", format = "decimal")
        ),
        @Parameter(
            name = "search",
            description = "Search query for product name or SKU",
            in = ParameterIn.QUERY,
            schema = @Schema(type = "string")
        )
    })
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Products retrieved successfully",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = PagedProductResponse.class),
                examples = @ExampleObject(
                    name = "Products Page",
                    value = """
                        {
                          "content": [
                            {
                              "id": 1,
                              "name": "Wireless Bluetooth Headphones",
                              "sku": "PROD-12345",
                              "price": 299.99,
                              "quantity": 100,
                              "category": "Electronics",
                              "status": "ACTIVE"
                            }
                          ],
                          "pageable": {
                            "pageNumber": 0,
                            "pageSize": 20
                          },
                          "totalElements": 150,
                          "totalPages": 8
                        }
                        """
                )
            ),
            headers = {
                @Header(
                    name = "X-Total-Count",
                    description = "Total number of products",
                    schema = @Schema(type = "integer")
                )
            }
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Invalid request parameters",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = ErrorResponse.class)
            )
        )
    })
    public ResponseEntity<Page<ProductResponse>> getAllProducts(
            @PageableDefault(size = 20) Pageable pageable,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) @Min(0) BigDecimal minPrice,
            @RequestParam(required = false) @Max(999999) BigDecimal maxPrice,
            @RequestParam(required = false) String search) {
        
        Page<ProductResponse> products = productService.findAll(
            pageable, category, minPrice, maxPrice, search
        );
        
        return ResponseEntity.ok()
            .header("X-Total-Count", String.valueOf(products.getTotalElements()))
            .body(products);
    }
    
    @GetMapping("/{id}")
    @Operation(
        summary = "Get product by ID",
        description = "Retrieves detailed information about a specific product by its unique identifier",
        tags = {"Product Management"}
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Product found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = ProductResponse.class),
                examples = @ExampleObject(
                    name = "Product Detail",
                    value = """
                        {
                          "id": 1,
                          "name": "Wireless Bluetooth Headphones",
                          "sku": "PROD-12345",
                          "description": "Premium noise-cancelling headphones",
                          "price": 299.99,
                          "quantity": 100,
                          "category": "Electronics",
                          "tags": ["bluetooth", "wireless", "audio"],
                          "images": ["https://example.com/image1.jpg"],
                          "status": "ACTIVE",
                          "createdAt": "2024-01-15T10:30:00",
                          "updatedAt": "2024-01-20T14:45:00"
                        }
                        """
                )
            )
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Product not found",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = ErrorResponse.class),
                examples = @ExampleObject(
                    value = """
                        {
                          "timestamp": "2024-01-20T15:30:00",
                          "status": 404,
                          "error": "Not Found",
                          "message": "Product with ID 999 not found",
                          "path": "/api/products/999"
                        }
                        """
                )
            )
        )
    })
    public ResponseEntity<ProductResponse> getProductById(
            @Parameter(
                description = "Product ID",
                required = true,
                example = "1",
                schema = @Schema(type = "integer", format = "int64", minimum = "1")
            )
            @PathVariable Long id) {
        
        return ResponseEntity.ok(productService.findById(id));
    }
    
    @PostMapping
    @Operation(
        summary = "Create new product",
        description = """
            Creates a new product in the catalog.
            
            Required permissions:
            - ROLE_ADMIN or ROLE_PRODUCT_MANAGER
            
            Validation rules:
            - Name: 3-200 characters
            - SKU: Must be unique, uppercase letters/numbers/hyphens only
            - Price: 0.01 - 999,999.99
            - Quantity: 0 - 100,000
            - Category: Must be from predefined list
            """,
        tags = {"Product Management"},
        security = @SecurityRequirement(name = "bearerAuth")
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "201",
            description = "Product created successfully",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = ProductResponse.class)
            ),
            headers = @Header(
                name = "Location",
                description = "URL of the created product",
                schema = @Schema(type = "string")
            )
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Invalid request payload",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON_VALUE,
                schema = @Schema(implementation = ErrorResponse.class),
                examples = {
                    @ExampleObject(
                        name = "Validation Error",
                        value = """
                            {
                              "timestamp": "2024-01-20T15:30:00",
                              "status": 400,
                              "error": "Bad Request",
                              "message": "Validation failed",
                              "errors": [
                                {
                                  "field": "name",
                                  "message": "Product name must be between 3 and 200 characters"
                                },
                                {
                                  "field": "price",
                                  "message": "Price must be greater than 0"
                                }
                              ]
                            }
                            """
                    ),
                    @ExampleObject(
                        name = "Duplicate SKU",
                        value = """
                            {
                              "timestamp": "2024-01-20T15:30:00",
                              "status": 400,
                              "error": "Bad Request",
                              "message": "Product with SKU 'PROD-12345' already exists"
                            }
                            """
                    )
                }
            )
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Not authenticated",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Insufficient permissions",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class))
        )
    })
    @PreAuthorize("hasAnyRole('ADMIN', 'PRODUCT_MANAGER')")
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody ProductCreateRequest request) {
        
        ProductResponse created = productService.create(request);
        
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .header("Location", "/api/products/" + created.getId())
            .body(created);
    }
    
    @PutMapping("/{id}")
    @Operation(
        summary = "Update product",
        description = "Updates an existing product. All fields are optional.",
        security = @SecurityRequirement(name = "bearerAuth")
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Product updated successfully",
            content = @Content(schema = @Schema(implementation = ProductResponse.class))
        ),
        @ApiResponse(responseCode = "404", description = "Product not found"),
        @ApiResponse(responseCode = "400", description = "Invalid request payload")
    })
    @PreAuthorize("hasAnyRole('ADMIN', 'PRODUCT_MANAGER')")
    public ResponseEntity<ProductResponse> updateProduct(
            @PathVariable Long id,
            @Valid @RequestBody ProductUpdateRequest request) {
        
        return ResponseEntity.ok(productService.update(id, request));
    }
    
    @DeleteMapping("/{id}")
    @Operation(
        summary = "Delete product",
        description = "Deletes a product from the catalog. This is a soft delete - product is marked as inactive.",
        security = @SecurityRequirement(name = "bearerAuth")
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "204",
            description = "Product deleted successfully"
        ),
        @ApiResponse(responseCode = "404", description = "Product not found"),
        @ApiResponse(responseCode = "409", description = "Product cannot be deleted (has active orders)")
    })
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
    
    @GetMapping("/search")
    @Operation(
        summary = "Search products",
        description = "Advanced product search with multiple criteria",
        tags = {"Product Management", "Search"}
    )
    public ResponseEntity<List<ProductResponse>> searchProducts(
            @Parameter(description = "Search query")
            @RequestParam String query,
            
            @Parameter(description = "Search in fields")
            @RequestParam(defaultValue = "name,description") String[] fields) {
        
        return ResponseEntity.ok(productService.search(query, fields));
    }
}

// Helper class for pagination response documentation
@Schema(description = "Paginated product response")
class PagedProductResponse {
    @Schema(description = "Page content")
    @ArraySchema(schema = @Schema(implementation = ProductResponse.class))
    List<ProductResponse> content;
    
    @Schema(description = "Pagination information")
    PageableInfo pageable;
    
    @Schema(description = "Total number of elements", example = "150")
    long totalElements;
    
    @Schema(description = "Total number of pages", example = "8")
    int totalPages;
}

@Schema(description = "Pagination information")
class PageableInfo {
    @Schema(description = "Current page number", example = "0")
    int pageNumber;
    
    @Schema(description = "Page size", example = "20")
    int pageSize;
}
```

### Exception Handling

**GlobalExceptionHandler.java**
```java
package com.ecommerce.exception;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
@Hidden  // Hide from OpenAPI documentation
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @ApiResponse(
        responseCode = "400",
        description = "Validation error",
        content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    public ErrorResponse handleValidationException(
            MethodArgumentNotValidException ex,
            WebRequest request) {
        
        List<ValidationError> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> new ValidationError(
                error.getField(),
                error.getDefaultMessage()
            ))
            .collect(Collectors.toList());
        
        return ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.BAD_REQUEST.value())
            .error("Validation Failed")
            .message("Invalid request payload")
            .path(request.getDescription(false))
            .validationErrors(errors)
            .build();
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleResourceNotFoundException(
            ResourceNotFoundException ex,
            WebRequest request) {
        
        return ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.NOT_FOUND.value())
            .error("Not Found")
            .message(ex.getMessage())
            .path(request.getDescription(false))
            .build();
    }
    
    @ExceptionHandler(AccessDeniedException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public ErrorResponse handleAccessDeniedException(
            AccessDeniedException ex,
            WebRequest request) {
        
        return ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.FORBIDDEN.value())
            .error("Forbidden")
            .message("You don't have permission to access this resource")
            .path(request.getDescription(false))
            .build();
    }
}
```

**ErrorResponse.java**
```java
package com.ecommerce.exception;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Value;
import java.time.LocalDateTime;
import java.util.List;

@Value
@Builder
@Schema(description = "Error response")
public class ErrorResponse {
    
    @Schema(description = "Error timestamp", example = "2024-01-20T15:30:00")
    LocalDateTime timestamp;
    
    @Schema(description = "HTTP status code", example = "400")
    int status;
    
    @Schema(description = "Error type", example = "Bad Request")
    String error;
    
    @Schema(description = "Error message", example = "Validation failed")
    String message;
    
    @Schema(description = "Request path", example = "/api/products")
    String path;
    
    @Schema(description = "Validation errors (if applicable)")
    List<ValidationError> validationErrors;
}

@Value
@Schema(description = "Field validation error")
class ValidationError {
    @Schema(description = "Field name", example = "name")
    String field;
    
    @Schema(description = "Error message", example = "Name is required")
    String message;
}
```

### Functional Router Documentation

**PersonRouterConfig.java**
```java
package com.ecommerce.config;

import com.ecommerce.handler.PersonHandler;
import com.ecommerce.service.PersonService;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import org.springdoc.core.annotations.RouterOperation;
import org.springdoc.core.annotations.RouterOperations;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.servlet.function.RouterFunction;
import org.springframework.web.servlet.function.ServerResponse;

import static org.springframework.web.servlet.function.RouterFunctions.route;

@Configuration
public class PersonRouterConfig {
    
    @Bean
    @RouterOperations({
        @RouterOperation(
            path = "/api/people",
            method = RequestMethod.GET,
            beanClass = PersonService.class,
            beanMethod = "findAll",
            operation = @io.swagger.v3.oas.annotations.Operation(
                summary = "Get all people",
                description = "Retrieves a list of all people",
                tags = {"People"}
            )
        ),
        @RouterOperation(
            path = "/api/people/{id}",
            method = RequestMethod.GET,
            beanClass = PersonService.class,
            beanMethod = "findById",
            operation = @io.swagger.v3.oas.annotations.Operation(
                summary = "Get person by ID",
                description = "Retrieves a person by their unique identifier",
                tags = {"People"},
                parameters = {
                    @Parameter(
                        name = "id",
                        description = "Person ID",
                        in = ParameterIn.PATH,
                        required = true
                    )
                }
            )
        ),
        @RouterOperation(
            path = "/api/people",
            method = RequestMethod.POST,
            beanClass = PersonService.class,
            beanMethod = "save",
            operation = @io.swagger.v3.oas.annotations.Operation(
                summary = "Create person",
                description = "Creates a new person",
                tags = {"People"}
            )
        )
    })
    public RouterFunction<ServerResponse> personRoutes(PersonHandler handler) {
        return route()
            .GET("/api/people", handler::getAllPeople)
            .GET("/api/people/{id}", handler::getPersonById)
            .POST("/api/people", handler::createPerson)
            .build();
    }
}
```

This comprehensive example demonstrates production-ready OpenAPI documentation with SpringDoc, including validation, security, pagination, error handling, and advanced features.
