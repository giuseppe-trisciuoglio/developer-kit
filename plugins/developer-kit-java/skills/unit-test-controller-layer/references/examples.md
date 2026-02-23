# Controller Layer Test Examples

## Example 1: `@WebMvcTest` with success, validation, and not-found paths

```java
package com.example.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.http.MediaType.APPLICATION_JSON;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = UserControllerWebMvcTest.UserController.class)
@Import(UserControllerWebMvcTest.GlobalExceptionHandler.class)
class UserControllerWebMvcTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private UserService userService;

    @Test
    void shouldReturnUserById() throws Exception {
        when(userService.findById(1L)).thenReturn(new UserResponse(1L, "Alice", "alice@example.com"));

        mockMvc.perform(get("/users/{id}", 1L))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.name").value("Alice"))
                .andExpect(jsonPath("$.email").value("alice@example.com"));

        verify(userService).findById(1L);
    }

    @Test
    void shouldReturnBadRequestWhenPayloadInvalid() throws Exception {
        CreateUserRequest request = new CreateUserRequest("", "not-an-email");

        mockMvc.perform(post("/users")
                        .contentType(APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("validation_failed"));
    }

    @Test
    void shouldReturnNotFoundWhenUserMissing() throws Exception {
        when(userService.findById(99L)).thenThrow(new UserNotFoundException("User 99 not found"));

        mockMvc.perform(get("/users/{id}", 99L))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error").value("not_found"))
                .andExpect(jsonPath("$.message").value("User 99 not found"));
    }

    @RestController
    @RequestMapping("/users")
    static class UserController {

        private final UserService userService;

        UserController(UserService userService) {
            this.userService = userService;
        }

        @GetMapping("/{id}")
        UserResponse getById(@PathVariable Long id) {
            return userService.findById(id);
        }

        @PostMapping
        ResponseEntity<UserResponse> create(@Valid @RequestBody CreateUserRequest request) {
            UserResponse created = userService.create(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        }
    }

    @ControllerAdvice
    static class GlobalExceptionHandler {

        @ExceptionHandler(UserNotFoundException.class)
        ResponseEntity<Map<String, String>> handleNotFound(UserNotFoundException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "not_found", "message", ex.getMessage()));
        }

        @ExceptionHandler(MethodArgumentNotValidException.class)
        ResponseEntity<Map<String, String>> handleValidation(MethodArgumentNotValidException ex) {
            return ResponseEntity.badRequest().body(Map.of("error", "validation_failed"));
        }
    }

    interface UserService {
        UserResponse findById(Long id);
        UserResponse create(CreateUserRequest request);
    }

    static class CreateUserRequest {
        @NotBlank
        private String name;

        @Email
        @NotBlank
        private String email;

        CreateUserRequest() {
        }

        CreateUserRequest(String name, String email) {
            this.name = name;
            this.email = email;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }
    }

    record UserResponse(Long id, String name, String email) {
    }

    static class UserNotFoundException extends RuntimeException {
        UserNotFoundException(String message) {
            super(message);
        }
    }
}
```

## Example 2: Standalone MockMvc for focused controller testing

```java
package com.example.web;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
class ProductControllerStandaloneTest {

    @Mock
    private ProductService productService;

    @InjectMocks
    private ProductController productController;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(productController).build();
    }

    @Test
    void shouldReturnPlainTextProductName() throws Exception {
        when(productService.getNameById(10L)).thenReturn("Keyboard");

        mockMvc.perform(get("/products/{id}/name", 10L).accept(MediaType.TEXT_PLAIN))
                .andExpect(status().isOk())
                .andExpect(content().string("Keyboard"));
    }

    @RestController
    @RequestMapping("/products")
    static class ProductController {
        private final ProductService productService;

        ProductController(ProductService productService) {
            this.productService = productService;
        }

        @GetMapping("/{id}/name")
        String productName(@PathVariable Long id) {
            return productService.getNameById(id);
        }
    }

    interface ProductService {
        String getNameById(Long id);
    }
}
```
