# Architecture Patterns for REST APIs

## Layered Architecture

### Feature-Based Structure
```
feature-name/
├── domain/
│   ├── model/           # Domain entities (Spring-free)
│   │   └── User.java
│   ├── repository/      # Domain ports (interfaces)
│   │   └── UserRepository.java
│   └── service/         # Domain services
│       └── UserService.java
├── application/
│   ├── service/         # Use cases (@Service beans)
│   │   └── UserApplicationService.java
│   └── dto/             # Immutable DTOs/records
│       ├── UserRequest.java
│       └── UserResponse.java
├── presentation/
│   └── rest/            # Controllers and mappers
│       ├── UserController.java
│       ├── UserMapper.java
│       └── UserExceptionHandler.java
└── infrastructure/
    └── persistence/     # JPA adapters
        └── JpaUserRepository.java
```

### Domain Layer (Clean Architecture)

#### Domain Entity
```java
package com.example.domain.model;

import java.time.LocalDateTime;
import java.util.Objects;

public class User {
    private final UserId id;
    private final String name;
    private final Email email;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    private User(UserId id, String name, Email email) {
        this.id = Objects.requireNonNull(id);
        this.name = Objects.requireNonNull(name);
        this.email = Objects.requireNonNull(email);
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    public static User create(UserId id, String name, Email email) {
        return new User(id, name, email);
    }

    public User updateName(String newName) {
        return new User(this.id, newName, this.email);
    }

    public User updateEmail(Email newEmail) {
        return new User(this.id, this.name, newEmail);
    }

    // Getters
    public UserId getId() { return id; }
    public String getName() { return name; }
    public Email getEmail() { return email; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}

// Value objects
public class UserId {
    private final Long value;

    public UserId(Long value) {
        this.value = Objects.requireNonNull(value);
        if (value <= 0) {
            throw new IllegalArgumentException("User ID must be positive");
        }
    }

    public Long getValue() { return value; }
}

public class Email {
    private final String value;

    public Email(String value) {
        this.value = Objects.requireNonNull(value);
        if (!isValid(value)) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }

    private boolean isValid(String email) {
        return email.contains("@") && email.length() > 5;
    }

    public String getValue() { return value; }
}
```

#### Domain Repository Port
```java
package com.example.domain.repository;

import com.example.domain.model.User;
import com.example.domain.model.UserId;
import java.util.Optional;

public interface UserRepository {
    Optional<User> findById(UserId id);
    void save(User user);
    void delete(UserId id);
    boolean existsByEmail(Email email);
}
```

#### Domain Service
```java
package com.example.domain.service;

import com.example.domain.model.User;
import com.example.domain.model.Email;
import com.example.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public class UserDomainService {
    private final UserRepository userRepository;

    public User registerUser(String name, String email) {
        Email emailObj = new Email(email);

        if (userRepository.existsByEmail(emailObj)) {
            throw new BusinessException("Email already exists");
        }

        User user = User.create(UserId.generate(), name, emailObj);
        userRepository.save(user);
        return user;
    }
}
```

### Application Layer (Use Cases)

#### Application Service
```java
package com.example.application.service;

import com.example.application.dto.UserRequest;
import com.example.application.dto.UserResponse;
import com.example.domain.model.User;
import com.example.domain.repository.UserRepository;
import com.example.application.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserApplicationService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    @Transactional
    public UserResponse createUser(UserRequest request) {
        log.info("Creating user: {}", request.getName());
        User user = userMapper.toDomain(request);
        User saved = userRepository.save(user);
        return userMapper.toResponse(saved);
    }

    @Transactional(readOnly = true)
    public Page<UserResponse> findAllUsers(Pageable pageable) {
        return userRepository.findAll(pageable)
                .map(userMapper::toResponse);
    }

    @Transactional(readOnly = true)
    public UserResponse findUserById(Long id) {
        return userRepository.findById(new UserId(id))
                .map(userMapper::toResponse)
                .orElseThrow(() -> new EntityNotFoundException("User not found"));
    }

    @Transactional
    public UserResponse updateUser(Long id, UserRequest request) {
        User user = userRepository.findById(new UserId(id))
                .orElseThrow(() -> new EntityNotFoundException("User not found"));

        User updated = user.updateName(request.getName());
        User saved = userRepository.save(updated);
        return userMapper.toResponse(saved);
    }

    @Transactional
    public void deleteUser(Long id) {
        userRepository.delete(new UserId(id));
    }
}
```

#### DTOs
```java
package com.example.application.dto;

import lombok.Value;
import jakarta.validation.constraints.*;

@Value
public class UserRequest {
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be 2-100 characters")
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Valid email required")
    private String email;
}

@Value
public class UserResponse {
    Long id;
    String name;
    String email;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Presentation Layer (REST API)

#### Controller
```java
package com.example.presentation.rest;

import com.example.application.dto.UserRequest;
import com.example.application.dto.UserResponse;
import com.example.application.service.UserApplicationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserApplicationService userApplicationService;

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody UserRequest request) {
        UserResponse created = userApplicationService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping
    public ResponseEntity<Page<UserResponse>> getAllUsers(Pageable pageable) {
        Page<UserResponse> users = userApplicationService.findAllUsers(pageable);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        UserResponse user = userApplicationService.findUserById(id);
        return ResponseEntity.ok(user);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserRequest request) {
        UserResponse updated = userApplicationService.updateUser(id, request);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userApplicationService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

#### Mapper
```java
package com.example.application.mapper;

import com.example.application.dto.UserRequest;
import com.example.application.dto.UserResponse;
import com.example.domain.model.User;
import com.example.domain.model.Email;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;
import org.mapstruct.NullValuePropertyMappingStrategy;

@Mapper(componentModel = "spring")
public interface UserMapper {

    @Mapping(target = "id", source = "id.value")
    UserResponse toResponse(User user);

    User toDomain(UserRequest request);

    default Email toEmail(String email) {
        return new Email(email);
    }

    default String toString(Email email) {
        return email.getValue();
    }
}
```

### Infrastructure Layer (Adapters)

#### JPA Repository Adapter
```java
package com.example.infrastructure.persistence;

import com.example.domain.model.User;
import com.example.domain.model.UserId;
import com.example.domain.repository.UserRepository;
import com.example.infrastructure.entity.UserEntity;
import com.example.infrastructure.mapper.UserEntityMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class JpaUserRepository implements UserRepository {

    private final SpringDataUserRepository springDataRepository;
    private final UserEntityMapper entityMapper;

    @Override
    public Optional<User> findById(UserId id) {
        return springDataRepository.findById(id.getValue())
                .map(entityMapper::toDomain);
    }

    @Override
    public void save(User user) {
        UserEntity entity = entityMapper.toEntity(user);
        springDataRepository.save(entity);
    }

    @Override
    public void delete(UserId id) {
        springDataRepository.deleteById(id.getValue());
    }

    @Override
    public boolean existsByEmail(Email email) {
        return springDataRepository.existsByEmail(email.getValue());
    }
}
```

#### Spring Data Repository
```java
package com.example.infrastructure.persistence;

import com.example.infrastructure.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface SpringDataUserRepository extends JpaRepository<UserEntity, Long> {
    boolean existsByEmail(String email);

    @Query("SELECT u FROM UserEntity u WHERE u.email = :email")
    Optional<UserEntity> findByEmail(@Param("email") String email);
}
```

## CQRS Pattern (Command Query Responsibility Segregation)

### Commands
```java
package com.example.application.command;

import lombok.Value;
import jakarta.validation.constraints.*;

@Value
public class CreateUserCommand {
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;

    @NotBlank(message = "Email is required")
    @Email
    private String email;
}

@Value
public class UpdateUserCommand {
    @NotNull(message = "User ID is required")
    private Long userId;

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;
}
```

### Command Handlers
```java
package com.example.application.command.handler;

import com.example.application.command.CreateUserCommand;
import com.example.application.command.UpdateUserCommand;
import com.example.domain.model.User;
import com.example.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserCommandHandler {

    private final UserRepository userRepository;

    @Transactional
    public User handle(CreateUserCommand command) {
        User user = User.create(UserId.generate(), command.getName(), new Email(command.getEmail()));
        return userRepository.save(user);
    }

    @Transactional
    public User handle(UpdateUserCommand command) {
        User user = userRepository.findById(new UserId(command.getUserId()))
                .orElseThrow(() -> new EntityNotFoundException("User not found"));

        User updated = user.updateName(command.getName());
        return userRepository.save(updated);
    }
}
```

### Queries
```java
package com.example.application.query;

import lombok.Value;
import java.util.List;

@Value
public class FindAllUsersQuery {
    int page;
    int size;
    String sortBy;
    String sortDirection;
}

@Value
public class FindUserByIdQuery {
    Long userId;
}
```

### Query Handlers
```java
package com.example.application.query.handler;

import com.example.application.query.FindAllUsersQuery;
import com.example.application.query.FindUserByIdQuery;
import com.example.application.dto.UserResponse;
import com.example.domain.model.User;
import com.example.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserQueryHandler {

    private final UserRepository userRepository;

    public Page<UserResponse> handle(FindAllUsersQuery query) {
        Pageable pageable = PageRequest.of(
            query.getPage(),
            query.getSize(),
            Sort.by(Sort.Direction.fromString(query.getSortDirection()), query.getSortBy())
        );

        return userRepository.findAll(pageable)
                .map(this::toResponse);
    }

    public UserResponse handle(FindUserByIdQuery query) {
        return userRepository.findById(new UserId(query.getUserId()))
                .map(this::toResponse)
                .orElseThrow(() -> new EntityNotFoundException("User not found"));
    }

    private UserResponse toResponse(User user) {
        return new UserResponse(
            user.getId().getValue(),
            user.getName(),
            user.getEmail().getValue(),
            user.getCreatedAt(),
            user.getUpdatedAt()
        );
    }
}
```

## Event-Driven Architecture

### Domain Events
```java
package com.example.domain.event;

import lombok.Value;
import java.time.LocalDateTime;

@Value
public class UserCreatedEvent {
    String userId;
    String email;
    LocalDateTime timestamp;
}

@Value
public class UserUpdatedEvent {
    String userId;
    String oldName;
    String newName;
    LocalDateTime timestamp;
}
```

### Event Publisher
```java
package com.example.domain.service;

import com.example.domain.event.UserCreatedEvent;
import com.example.domain.event.UserUpdatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserEventPublisher {

    private final ApplicationEventPublisher eventPublisher;

    public void publishUserCreated(String userId, String email) {
        UserCreatedEvent event = new UserCreatedEvent(userId, email, LocalDateTime.now());
        eventPublisher.publishEvent(event);
        log.info("Published UserCreatedEvent for user: {}", userId);
    }

    public void publishUserUpdated(String userId, String oldName, String newName) {
        UserUpdatedEvent event = new UserUpdatedEvent(userId, oldName, newName, LocalDateTime.now());
        eventPublisher.publishEvent(event);
        log.info("Published UserUpdatedEvent for user: {}", userId);
    }
}
```

### Event Listeners
```java
package com.example.application.event.listener;

import com.example.domain.event.UserCreatedEvent;
import com.example.domain.event.UserUpdatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class UserEventListener {

    @EventListener
    public void handleUserCreated(UserCreatedEvent event) {
        log.info("User created: {} with email: {}", event.getUserId(), event.getEmail());
        // Send welcome email, update analytics, etc.
    }

    @EventListener
    public void handleUserUpdated(UserUpdatedEvent event) {
        log.info("User {} updated: {} -> {}", event.getUserId(), event.getOldName(), event.getNewName());
        // Update search index, send notification, etc.
    }
}
```

## Microservices Architecture

### API Gateway Pattern
```java
package com.example.gateway;

import org.springframework.cloud.gateway.route.Route;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r.path("/api/users/**")
                .filters(f -> f.stripPrefix(1))
                .uri("lb://user-service"))
            .route("order-service", r -> r.path("/api/orders/**")
                .filters(f -> f.stripPrefix(1))
                .uri("lb://order-service"))
            .build();
    }
}
```

### Service Communication
```java
package com.example.application.client;

import com.example.application.dto.UserResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(name = "user-service", url = "${user.service.url}")
public interface UserServiceClient {

    @GetMapping("/api/users/{id}")
    UserResponse getUserById(@PathVariable Long id);

    @GetMapping("/api/users")
    List<UserResponse> getAllUsers();
}
```

## Testing Strategy

### Unit Tests
```java
package com.example.application.service;

import com.example.application.dto.UserRequest;
import com.example.domain.model.User;
import com.example.domain.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class UserApplicationServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserApplicationService userApplicationService;

    @Test
    void createUserShouldCreateUser() {
        // Arrange
        UserRequest request = new UserRequest("John Doe", "john@example.com");
        User user = User.create(UserId.generate(), "John Doe", new Email("john@example.com"));

        when(userRepository.save(any(User.class))).thenReturn(user);

        // Act
        UserResponse result = userApplicationService.createUser(request);

        // Assert
        assertNotNull(result);
        assertEquals("John Doe", result.getName());
        verify(userRepository).save(any(User.class));
    }
}
```

### Integration Tests
```java
package com.example.presentation.rest;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createUserShouldReturnCreatedStatus() throws Exception {
        // Arrange
        String requestBody = """
            {
                "name": "John Doe",
                "email": "john@example.com"
            }
            """;

        // Act & Assert
        mockMvc.perform(post("/api/users")
                .contentType("application/json")
                .content(requestBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("John Doe"))
                .andExpect(jsonPath("$.email").value("john@example.com"));
    }
}
```