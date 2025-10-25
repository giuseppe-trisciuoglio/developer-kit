# Spring Boot Test Patterns - Examples

Practical examples demonstrating integration and unit testing patterns for Spring Boot applications.

## Example 1: Repository Integration Test with Testcontainers

Testing JPA repositories with a real PostgreSQL database.

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class ProductRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Autowired
    private ProductRepository productRepository;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldSaveAndRetrieveProduct() {
        // Arrange
        Product product = Product.builder()
            .name("Laptop")
            .price(BigDecimal.valueOf(999.99))
            .stock(10)
            .build();

        // Act
        Product saved = productRepository.save(product);
        entityManager.flush();

        // Assert
        Optional<Product> retrieved = productRepository.findById(saved.getId());
        assertThat(retrieved)
            .isPresent()
            .hasValueSatisfying(p -> assertThat(p.getName()).isEqualTo("Laptop"));
    }

    @Test
    void shouldFindProductByName() {
        // Arrange
        Product product = Product.builder()
            .name("Desktop")
            .price(BigDecimal.valueOf(1499.99))
            .stock(5)
            .build();
        productRepository.save(product);
        entityManager.flush();

        // Act
        List<Product> results = productRepository.findByNameContaining("Desktop");

        // Assert
        assertThat(results).hasSize(1);
    }

    @Test
    void shouldThrowExceptionForInvalidProduct() {
        // Arrange
        Product invalidProduct = Product.builder()
            .price(BigDecimal.valueOf(-10))  // Invalid: negative price
            .stock(5)
            .build();

        // Act & Assert
        assertThatThrownBy(() -> {
            productRepository.save(invalidProduct);
            entityManager.flush();
        }).isInstanceOf(ConstraintViolationException.class);
    }
}
```

---

## Example 2: REST Controller Slice Test

Testing controllers with MockMvc without loading full Spring context.

```java
@WebMvcTest(ProductController.class)
class ProductControllerSliceTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Test
    void shouldReturnProductWithStatus200() throws Exception {
        // Arrange
        ProductResponse response = new ProductResponse(1L, "Laptop", BigDecimal.TEN, 5, LocalDateTime.now(), LocalDateTime.now());
        when(productService.findById(1L)).thenReturn(response);

        // Act & Assert
        mockMvc.perform(get("/api/v1/products/1")
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Laptop"))
            .andExpect(jsonPath("$.price").value(10.0));

        verify(productService, times(1)).findById(1L);
    }

    @Test
    void shouldCreateProductWithStatus201() throws Exception {
        // Arrange
        CreateProductRequest request = new CreateProductRequest("New Product", BigDecimal.TEN, "Desc", 100);
        ProductResponse response = new ProductResponse(2L, "New Product", BigDecimal.TEN, 100, LocalDateTime.now(), LocalDateTime.now());
        
        when(productService.create(any())).thenReturn(response);

        // Act & Assert
        mockMvc.perform(post("/api/v1/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                        "name": "New Product",
                        "price": 10.00,
                        "description": "Desc",
                        "stockQuantity": 100
                    }
                    """))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"))
            .andExpect(jsonPath("$.id").value(2L));
    }

    @Test
    void shouldReturnNotFoundForMissingProduct() throws Exception {
        // Arrange
        when(productService.findById(999L))
            .thenThrow(new ResourceNotFoundException("Product not found"));

        // Act & Assert
        mockMvc.perform(get("/api/v1/products/999"))
            .andExpect(status().isNotFound());
    }

    @Test
    void shouldValidateRequestBody() throws Exception {
        // Act & Assert - Missing required name field
        mockMvc.perform(post("/api/v1/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                        "price": 10.00,
                        "stockQuantity": 100
                    }
                    """))
            .andExpect(status().isBadRequest());
    }
}
```

---

## Example 3: Service Unit Test (No Spring)

Fast unit tests using Mockito without Spring context.

```java
@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private ProductMapper productMapper;

    @InjectMocks
    private ProductApplicationService productService;

    private Product testProduct;
    private ProductResponse testResponse;

    @BeforeEach
    void setUp() {
        testProduct = Product.builder()
            .id(ProductId.of("123"))
            .name("Test Product")
            .price(Money.of(BigDecimal.TEN))
            .stock(Stock.of(100))
            .build();

        testResponse = new ProductResponse("123", "Test Product", BigDecimal.TEN, "EUR", 100, "ACTIVE", LocalDateTime.now(), LocalDateTime.now());
    }

    @Test
    void shouldCreateProductSuccessfully() {
        // Arrange
        CreateProductRequest request = new CreateProductRequest("Test", BigDecimal.TEN, "Desc", 100);
        when(productRepository.save(any(Product.class))).thenReturn(testProduct);
        when(productMapper.toResponse(testProduct)).thenReturn(testResponse);

        // Act
        ProductResponse result = productService.createProduct(request);

        // Assert
        assertThat(result).isNotNull();
        assertThat(result.name()).isEqualTo("Test Product");
        verify(productRepository, times(1)).save(any(Product.class));
    }

    @Test
    void shouldFindProductByIdSuccessfully() {
        // Arrange
        when(productRepository.findById(ProductId.of("123")))
            .thenReturn(Optional.of(testProduct));
        when(productMapper.toResponse(testProduct)).thenReturn(testResponse);

        // Act
        ProductResponse result = productService.getProductById("123");

        // Assert
        assertThat(result.name()).isEqualTo("Test Product");
    }

    @Test
    void shouldThrowExceptionWhenProductNotFound() {
        // Arrange
        when(productRepository.findById(any())).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> productService.getProductById("999"))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("Product not found: 999");
    }

    @Test
    void shouldUpdateProductSuccessfully() {
        // Arrange
        UpdateProductRequest request = new UpdateProductRequest("Updated", BigDecimal.valueOf(20), "Updated Desc");
        when(productRepository.findById(ProductId.of("123")))
            .thenReturn(Optional.of(testProduct));
        when(productRepository.save(any(Product.class))).thenReturn(testProduct);
        when(productMapper.toResponse(any())).thenReturn(testResponse);

        // Act
        ProductResponse result = productService.updateProduct("123", request);

        // Assert
        assertThat(result).isNotNull();
        verify(productRepository, times(1)).save(any(Product.class));
    }

    @Test
    void shouldDeleteProductSuccessfully() {
        // Act
        productService.deleteProduct("123");

        // Assert
        verify(productRepository, times(1)).delete(ProductId.of("123"));
    }
}
```

---

## Example 4: Full Integration Test

Testing complete request-response cycle with real database.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class ProductControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ProductRepository productRepository;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @BeforeEach
    void setUp() {
        productRepository.deleteAll();
    }

    @Test
    void shouldCreateProductAndReturn201() {
        // Arrange
        CreateProductRequest request = new CreateProductRequest(
            "Integration Test Product",
            BigDecimal.valueOf(149.99),
            "Test Description",
            50
        );

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.postForEntity(
            "/api/v1/products",
            request,
            ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().name()).isEqualTo("Integration Test Product");
        assertThat(response.getHeaders().getLocation()).isNotNull();
    }

    @Test
    void shouldRetrieveProductByIdAndReturn200() {
        // Arrange
        Product product = Product.create("Integration Product", "Test", BigDecimal.valueOf(99.99), 30);
        Product saved = productRepository.save(product);

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.getForEntity(
            "/api/v1/products/" + saved.getId().getValue(),
            ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().name()).isEqualTo("Integration Product");
    }

    @Test
    void shouldReturnNotFoundForNonExistentProduct() {
        // Act
        ResponseEntity<String> response = restTemplate.getForEntity(
            "/api/v1/products/non-existent",
            String.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldUpdateProductAndReturn200() {
        // Arrange
        Product product = Product.create("Original", "Original Desc", BigDecimal.TEN, 100);
        Product saved = productRepository.save(product);
        
        UpdateProductRequest updateRequest = new UpdateProductRequest(
            "Updated", BigDecimal.TWENTY, "Updated Desc"
        );

        // Act
        ResponseEntity<ProductResponse> response = restTemplate.exchange(
            "/api/v1/products/" + saved.getId().getValue(),
            HttpMethod.PUT,
            new HttpEntity<>(updateRequest),
            ProductResponse.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().name()).isEqualTo("Updated");
    }

    @Test
    void shouldDeleteProductAndReturn204() {
        // Arrange
        Product product = Product.create("To Delete", "Desc", BigDecimal.TEN, 100);
        Product saved = productRepository.save(product);

        // Act
        ResponseEntity<Void> response = restTemplate.exchange(
            "/api/v1/products/" + saved.getId().getValue(),
            HttpMethod.DELETE,
            null,
            Void.class
        );

        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);
        assertThat(productRepository.findById(saved.getId())).isEmpty();
    }
}
```

These examples demonstrate unit testing, slice testing, and full integration testing patterns for Spring Boot applications.
