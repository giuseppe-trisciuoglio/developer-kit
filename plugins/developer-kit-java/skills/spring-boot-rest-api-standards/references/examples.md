# Spring Boot REST API Examples

## Complete CRUD REST API with Validation

### Entity with Validation
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be 2-100 characters")
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Valid email required")
    @Column(unique = true)
    private String email;

    @Min(value = 18, message = "Must be at least 18")
    @Max(value = 120, message = "Invalid age")
    private Integer age;

    @Size(min = 8, max = 100, message = "Password must be 8-100 characters")
    private String password;

    @Column(name = "is_active")
    private Boolean active = true;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

### Service with Transaction Management
```java
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final EmailService emailService;

    @Transactional(readOnly = true)
    public Page<UserResponse> findAll(Pageable pageable) {
        log.debug("Fetching users page {} size {}", pageable.getPageNumber(), pageable.getPageSize());
        return userRepository.findAll(pageable)
                .map(this::toResponse);
    }

    @Transactional(readOnly = true)
    public UserResponse findById(Long id) {
        log.debug("Looking for user with id {}", id);
        return userRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new EntityNotFoundException("User not found"));
    }

    @Transactional
    public UserResponse create(CreateUserRequest request) {
        log.info("Creating user with email: {}", request.getEmail());

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("Email already exists");
        }

        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setAge(request.getAge());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        User saved = userRepository.save(user);
        emailService.sendWelcomeEmail(saved.getEmail(), saved.getName());

        return toResponse(saved);
    }

    @Transactional
    public UserResponse update(Long id, UpdateUserRequest request) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("User not found"));

        if (request.getName() != null) {
            user.setName(request.getName());
        }
        if (request.getEmail() != null) {
            if (!user.getEmail().equals(request.getEmail()) &&
                userRepository.existsByEmail(request.getEmail())) {
                throw new BusinessException("Email already exists");
            }
            user.setEmail(request.getEmail());
        }
        if (request.getAge() != null) {
            user.setAge(request.getAge());
        }

        User updated = userRepository.save(user);
        return toResponse(updated);
    }

    @Transactional
    public void delete(Long id) {
        if (!userRepository.existsById(id)) {
            throw new EntityNotFoundException("User not found");
        }

        User user = userRepository.findById(id).orElseThrow();
        emailService.sendDeletionEmail(user.getEmail(), user.getName());
        userRepository.deleteById(id);
    }

    private UserResponse toResponse(User user) {
        return new UserResponse(
            user.getId(),
            user.getName(),
            user.getEmail(),
            user.getAge(),
            user.getActive(),
            user.getCreatedAt(),
            user.getUpdatedAt()
        );
    }
}
```

### Controller with Proper HTTP Methods
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<UserResponse>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "DESC") String sortDirection) {

        Sort sort = Sort.by(Sort.Direction.fromString(sortDirection), sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<UserResponse> users = userService.findAll(pageable);

        HttpHeaders headers = new HttpHeaders();
        headers.add("X-Total-Count", String.valueOf(users.getTotalElements()));
        headers.add("X-Total-Pages", String.valueOf(users.getTotalPages()));

        return ResponseEntity.ok()
                .headers(headers)
                .body(users);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserResponse created = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .header("Location", "/api/users/" + created.getId())
                .body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        UserResponse updated = userService.update(id, request);
        return ResponseEntity.ok(updated);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<UserResponse> patchUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        UserResponse updated = userService.update(id, request);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## API Versioning Examples

### URL Versioning
```java
@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 {
    // Version 1 endpoints
}

@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {
    // Version 2 endpoints with different response format
}
```

### Header Versioning
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping
    public ResponseEntity<UserResponse> getUsers(
            @RequestHeader(value = "Accept-Version", defaultValue = "1.0") String version) {

        if (version.equals("2.0")) {
            return ResponseEntity.ok(v2UserResponse);
        }
        return ResponseEntity.ok(v1UserResponse);
    }
}
```

### Media Type Versioning
```java
@GetMapping(produces = {
    "application/vnd.company.v1+json",
    "application/vnd.company.v2+json"
})
public ResponseEntity<UserResponse> getUsers(
        @RequestHeader("Accept") String accept) {

    if (accept.contains("v2")) {
        return ResponseEntity.ok(v2UserResponse);
    }
    return ResponseEntity.ok(v1UserResponse);
}
```

## HATEOAS Implementation

### Response with Links
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseWithLinks {
    private Long id;
    private String name;
    private String email;
    private Map<String, String> _links;

    // Lombok generates constructors/getters/setters
}

@GetMapping("/{id}")
public ResponseEntity<UserResponseWithLinks> getUserWithLinks(@PathVariable Long id) {
    UserResponse user = userService.findById(id);

    Map<String, String> links = Map.of(
        "self", "/api/users/" + id,
        "all", "/api/users",
        "update", "/api/users/" + id,
        "delete", "/api/users/" + id
    );

    UserResponseWithLinks response = new UserResponseWithLinks(
        user.getId(), user.getName(), user.getEmail(), links);

    return ResponseEntity.ok(response);
}
```

### Advanced HATEOAS with Spring HATEOAS
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final EntityLinks entityLinks;

    @GetMapping
    public ResponseEntity<CollectionModel<UserResponse>> getAllUsers() {
        List<UserResponse> users = userService.findAll().stream()
                .map(this::toResponse)
                .collect(Collectors.toList());

        CollectionModel<UserResponse> resource = CollectionModel.of(users);
        resource.add(entityLinks.linkToCollectionResource(UserController.class).withSelfRel());
        resource.add(entityLinks.linkToCollectionResource(UserController.class).withRel("users"));

        return ResponseEntity.ok(resource);
    }

    @GetMapping("/{id}")
    public ResponseEntity<EntityModel<UserResponse>> getUserById(@PathVariable Long id) {
        UserResponse user = userService.findById(id);

        EntityModel<UserResponse> resource = EntityModel.of(user);
        resource.add(entityLinks.linkToItemResource(UserController.class, id).withSelfRel());
        resource.add(entityLinks.linkToCollectionResource(UserController.class).withRel("users"));
        resource.add(linkTo(methodOn(UserController.class).getUserOrders(id)).withRel("orders"));

        return ResponseEntity.ok(resource);
    }

    private UserResponse toResponse(User user) {
        return new UserResponse(
            user.getId(),
            user.getName(),
            user.getEmail(),
            user.getActive(),
            user.getCreatedAt()
        );
    }
}
```

## Async Processing

### Asynchronous Controller
```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class AsyncUserController {

    private final AsyncUserService asyncUserService;

    @GetMapping("/{id}")
    public CompletableFuture<ResponseEntity<UserResponse>> getUserById(@PathVariable Long id) {
        return asyncUserService.getUserById(id)
                .thenApply(ResponseEntity::ok)
                .exceptionally(ex -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public CompletableFuture<ResponseEntity<UserResponse>> createUser(
            @Valid @RequestBody CreateUserRequest request) {
        return asyncUserService.createUser(request)
                .thenApply(created ->
                    ResponseEntity.status(HttpStatus.CREATED)
                        .header("Location", "/api/users/" + created.getId())
                        .body(created))
                .exceptionally(ex -> {
                    if (ex.getCause() instanceof BusinessException) {
                        return ResponseEntity.badRequest().build();
                    }
                    return ResponseEntity.internalServerError().build();
                });
    }
}
```

### Async Service Implementation
```java
@Service
@RequiredArgsConstructor
public class AsyncUserService {

    private final UserService userService;
    private final ExecutorService executor;

    @Async
    public CompletableFuture<UserResponse> getUserById(Long id) {
        return CompletableFuture.supplyAsync(() -> userService.findById(id), executor);
    }

    @Async
    public CompletableFuture<UserResponse> createUser(CreateUserRequest request) {
        return CompletableFuture.supplyAsync(() -> userService.create(request), executor);
    }
}
```

## File Upload and Download

### File Upload Controller
```java
@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final FileStorageService fileStorageService;

    @PostMapping("/upload")
    public ResponseEntity<FileUploadResponse> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            throw new BusinessException("File is empty");
        }

        String fileName = fileStorageService.storeFile(file);
        String fileDownloadUri = ServletUriComponentsBuilder.fromCurrentContextPath()
                .path("/api/files/download/")
                .path(fileName)
                .toUriString();

        FileUploadResponse response = new FileUploadResponse(
            fileName, fileDownloadUri, file.getContentType(), file.getSize());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/download/{fileName:.+}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String fileName) {
        Resource resource = fileStorageService.loadFileAsResource(fileName);

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\"" + resource.getFilename() + "\"")
                .body(resource);
    }
}
```

### File Storage Service
```java
@Service
public class FileStorageService {

    private final Path fileStorageLocation;

    @Autowired
    public FileStorageService(FileStorageProperties fileStorageProperties) {
        this.fileStorageLocation = Paths.get(fileStorageProperties.getUploadDir())
                .toAbsolutePath().normalize();

        try {
            Files.createDirectories(this.fileStorageLocation);
        } catch (Exception ex) {
            throw new FileStorageException("Could not create the directory where the uploaded files will be stored.", ex);
        }
    }

    public String storeFile(MultipartFile file) {
        String fileName = StringUtils.cleanPath(Objects.requireNonNull(file.getOriginalFilename()));

        try {
            if (fileName.contains("..")) {
                throw new FileStorageException("Sorry! Filename contains invalid path sequence " + fileName);
            }

            Path targetLocation = this.fileStorageLocation.resolve(fileName);
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            return fileName;
        } catch (IOException ex) {
            throw new FileStorageException("Could not store file " + fileName + ". Please try again!", ex);
        }
    }

    public Resource loadFileAsResource(String fileName) {
        try {
            Path filePath = this.fileStorageLocation.resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath);

            if (resource.exists() && resource.isReadable()) {
                return resource;
            } else {
                throw new FileNotFoundException("File not found " + fileName);
            }
        } catch (Exception ex) {
            throw new FileNotFoundException("File not found " + fileName, ex);
        }
    }
}
```

## WebSocket Integration

### WebSocket Configuration
```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }
}
```

### WebSocket Controller
```java
@Controller
@RequiredArgsConstructor
public class WebSocketController {

    private final SimpMessagingTemplate messagingTemplate;

    @MessageMapping("/chat.sendMessage")
    @SendTo("/topic/public")
    public ChatMessage sendMessage(@Payload ChatMessage chatMessage) {
        return chatMessage;
    }

    @MessageMapping("/chat.addUser")
    @SendTo("/topic/public")
    public ChatMessage addUser(@Payload ChatMessage chatMessage,
                              SimpMessageHeaderAccessor headerAccessor) {
        headerAccessor.getSessionAttributes().put("username", chatMessage.getSender());
        return chatMessage;
    }

    @Scheduled(fixedRate = 5000)
    public void sendPeriodicUpdates() {
        messagingTemplate.convertAndSend("/topic/updates",
            new UpdateMessage("System update", LocalDateTime.now()));
    }
}
```

### Frontend Integration Example
```javascript
// JavaScript WebSocket client
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.stompClient = null;
        this.connected = false;
    }

    connect() {
        const socket = new SockJS(this.url);
        this.stompClient = Stomp.over(socket);

        this.stompClient.connect({}, (frame) => {
            this.connected = true;
            console.log('Connected: ' + frame);

            // Subscribe to topics
            this.stompClient.subscribe('/topic/public', (message) => {
                this.onMessage(message);
            });

            this.stompClient.subscribe('/topic/updates', (update) => {
                this.onUpdate(update);
            });
        }, (error) => {
            this.connected = false;
            console.error('Error: ' + error);
        });
    }

    sendMessage(message) {
        if (this.connected) {
            this.stompClient.send("/app/chat.sendMessage", {}, JSON.stringify(message));
        }
    }

    onMessage(message) {
        const chatMessage = JSON.parse(message.body);
        console.log('Received message:', chatMessage);
        // Display message in UI
    }

    onUpdate(update) {
        const updateMessage = JSON.parse(update.body);
        console.log('Received update:', updateMessage);
        // Update UI with system messages
    }
}
```