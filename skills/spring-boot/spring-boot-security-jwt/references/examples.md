# Spring Security JWT Implementation Examples

## Complete Application Setup

### Application Main Class
```java
@SpringBootApplication
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@EnableJpaRepositories(basePackages = "com.example.security.repository")
@EntityScan(basePackages = "com.example.security.model")
public class SecurityApplication {
    public static void main(String[] args) {
        SpringApplication.run(SecurityApplication.class, args);
    }

    @Bean
    public CommandLineRunner initData(UserRepository userRepository,
                                     RoleRepository roleRepository,
                                     PermissionRepository permissionRepository,
                                     PasswordEncoder passwordEncoder) {
        return args -> {
            // Create permissions
            Permission readPermission = permissionRepository.save(
                new Permission("USER_READ", "Read user information"));
            Permission writePermission = permissionRepository.save(
                new Permission("USER_WRITE", "Write user information"));
            Permission deletePermission = permissionRepository.save(
                new Permission("USER_DELETE", "Delete user information"));
            Permission adminPermission = permissionRepository.save(
                new Permission("ADMIN", "Full administrative access"));

            // Create roles
            Role userRole = roleRepository.save(new Role("USER"));
            Role adminRole = roleRepository.save(new Role("ADMIN"));
            Role managerRole = roleRepository.save(new Role("MANAGER"));

            // Assign permissions to roles
            userRole.getPermissions().addAll(Set.of(readPermission));
            managerRole.getPermissions().addAll(Set.of(readPermission, writePermission));
            adminRole.getPermissions().addAll(Set.of(readPermission, writePermission, deletePermission, adminPermission));

            roleRepository.saveAll(List.of(userRole, adminRole, managerRole));

            // Create users
            User user = new User("user@example.com", passwordEncoder.encode("password"));
            user.setRoles(Set.of(userRole));
            user.setEnabled(true);

            User admin = new User("admin@example.com", passwordEncoder.encode("admin"));
            admin.setRoles(Set.of(adminRole));
            admin.setEnabled(true);

            User manager = new User("manager@example.com", passwordEncoder.encode("manager"));
            manager.setRoles(Set.of(managerRole));
            manager.setEnabled(true);

            userRepository.saveAll(List.of(user, admin, manager));
        };
    }
}
```

### Domain Models
```java
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    private String firstName;
    private String lastName;

    @Column(name = "phone_number")
    private String phoneNumber;

    @Column(nullable = false)
    private boolean enabled = true;

    @Column(nullable = false)
    private boolean accountNonExpired = true;

    @Column(nullable = false)
    private boolean accountNonLocked = true;

    @Column(nullable = false)
    private boolean credentialsNonExpired = true;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<RefreshToken> refreshTokens = new ArrayList<>();

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<UserSession> sessions = new ArrayList<>();

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return roles.stream()
            .flatMap(role -> {
                Collection<GrantedAuthority> authorities = new ArrayList<>();
                authorities.add(new SimpleGrantedAuthority("ROLE_" + role.getName()));
                authorities.addAll(role.getPermissions().stream()
                    .map(permission -> new SimpleGrantedAuthority(permission.getName()))
                    .collect(Collectors.toList()));
                return authorities.stream();
            })
            .collect(Collectors.toList());
    }

    @Override
    public String getUsername() {
        return email;
    }

    public String getFullName() {
        return String.format("%s %s", firstName, lastName).trim();
    }

    public boolean hasPermission(String permission) {
        return getAuthorities().stream()
            .anyMatch(auth -> auth.getAuthority().equals(permission));
    }

    public boolean hasRole(String role) {
        return roles.stream()
            .anyMatch(r -> r.getName().equals(role));
    }
}

@Entity
@Table(name = "roles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Role {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

    private String description;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "role_permissions",
        joinColumns = @JoinColumn(name = "role_id"),
        inverseJoinColumns = @JoinColumn(name = "permission_id")
    )
    private Set<Permission> permissions = new HashSet<>();
}

@Entity
@Table(name = "permissions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Permission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

    private String description;

    @Column(name = "resource_type")
    private String resourceType;
}
```

## Authentication Controller

### Complete Auth Controller
```java
@RestController
@RequestMapping("/api/auth")
@Validated
@Slf4j
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenService tokenService;
    private final RefreshTokenService refreshTokenService;
    private final UserService userService;
    private final AuthenticationEventListener eventListener;

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletRequest httpRequest) {

        log.info("Login attempt for user: {}", request.email());

        try {
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    request.email(),
                    request.password()
                )
            );

            SecurityContextHolder.getContext()
                .setAuthentication(authentication);

            User user = (User) authentication.getPrincipal();

            // Generate tokens
            AccessTokenResponse accessToken = tokenService.generateAccessToken(user);
            RefreshTokenResponse refreshToken = refreshTokenService.createRefreshToken(user);

            // Track device and location
            String deviceInfo = extractDeviceInfo(httpRequest);
            String ipAddress = extractIpAddress(httpRequest);

            userService.recordLogin(user, deviceInfo, ipAddress);

            // Publish authentication success event
            eventListener.publishAuthenticationSuccess(user, httpRequest);

            LoginResponse response = new LoginResponse(
                accessToken.token(),
                accessToken.expiresAt(),
                refreshToken.token(),
                refreshToken.expiresAt(),
                user.getId(),
                user.getEmail(),
                user.getFullName(),
                user.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toList())
            );

            return ResponseEntity.ok()
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + accessToken.token())
                .body(response);

        } catch (BadCredentialsException e) {
            log.warn("Failed login attempt for user: {}", request.email());
            throw new AuthenticationFailedException("Invalid credentials");
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<RefreshTokenResponse> refreshToken(
            @Valid @RequestBody RefreshTokenRequest request) {

        RefreshTokenResponse response = refreshTokenService.refreshToken(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/logout")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<MessageResponse> logout(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            HttpServletRequest request) {

        String token = extractTokenFromHeader(authorization);
        String jti = tokenService.extractTokenClaim(token, "jti");

        // Invalidate refresh token
        refreshTokenService.revokeRefreshTokenByJti(jti);

        // Record logout
        User user = (User) SecurityContextHolder.getContext()
            .getAuthentication().getPrincipal();
        userService.recordLogout(user, extractIpAddress(request));

        // Clear security context
        SecurityContextHolder.clearContext();

        return ResponseEntity.ok(new MessageResponse("Logged out successfully"));
    }

    @PostMapping("/logout-all")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<MessageResponse> logoutAllSessions(
            Authentication authentication) {

        User user = (User) authentication.getPrincipal();
        refreshTokenService.revokeAllRefreshTokens(user);

        SecurityContextHolder.clearContext();

        return ResponseEntity.ok(new MessageResponse("Logged out from all devices"));
    }

    @GetMapping("/me")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<UserProfileResponse> getCurrentUser(
            Authentication authentication) {

        User user = (User) authentication.getPrincipal();

        UserProfileResponse response = new UserProfileResponse(
            user.getId(),
            user.getEmail(),
            user.getFullName(),
            user.getPhoneNumber(),
            user.getRoles().stream()
                .map(Role::getName)
                .collect(Collectors.toSet()),
            user.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toSet())
        );

        return ResponseEntity.ok(response);
    }

    @PostMapping("/change-password")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<MessageResponse> changePassword(
            @Valid @RequestBody ChangePasswordRequest request,
            Authentication authentication) {

        User user = (User) authentication.getPrincipal();
        userService.changePassword(user, request);

        // Invalidate all sessions except current
        refreshTokenService.revokeAllRefreshTokensExceptCurrent(user, request.currentPassword());

        return ResponseEntity.ok(new MessageResponse("Password changed successfully"));
    }

    private String extractTokenFromHeader(String authorization) {
        if (authorization != null && authorization.startsWith("Bearer ")) {
            return authorization.substring(7);
        }
        throw new IllegalArgumentException("Invalid authorization header");
    }

    private String extractDeviceInfo(HttpServletRequest request) {
        String userAgent = request.getHeader("User-Agent");
        // Parse user agent to extract browser and OS information
        // Implementation depends on your requirements
        return userAgent;
    }

    private String extractIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
```

### Registration Controller
```java
@RestController
@RequestMapping("/api/register")
@Validated
public class RegistrationController {

    private final UserService userService;
    private final EmailService emailService;

    @PostMapping
    public ResponseEntity<MessageResponse> register(
            @Valid @RequestBody RegistrationRequest request,
            UriComponentsBuilder uriBuilder) {

        // Check if user already exists
        if (userService.existsByEmail(request.email())) {
            throw new UserAlreadyExistsException("Email already registered");
        }

        // Create new user
        User user = userService.createUser(request);

        // Send verification email
        String verificationToken = userService.generateEmailVerificationToken(user);
        emailService.sendVerificationEmail(user, verificationToken);

        URI location = uriBuilder.path("/api/users/{id}")
            .buildAndExpand(user.getId())
            .toUri();

        return ResponseEntity.created(location)
            .body(new MessageResponse("User registered successfully. Please check your email for verification."));
    }

    @PostMapping("/verify-email")
    public ResponseEntity<MessageResponse> verifyEmail(
            @Valid @RequestBody EmailVerificationRequest request) {

        User user = userService.verifyEmail(request.token());

        return ResponseEntity.ok(new MessageResponse("Email verified successfully"));
    }

    @PostMapping("/resend-verification")
    public ResponseEntity<MessageResponse> resendVerification(
            @Valid @RequestBody ResendVerificationRequest request) {

        User user = userService.findByEmail(request.email());

        if (user.isEmailVerified()) {
            throw new EmailAlreadyVerifiedException("Email already verified");
        }

        String verificationToken = userService.generateEmailVerificationToken(user);
        emailService.sendVerificationEmail(user, verificationToken);

        return ResponseEntity.ok(new MessageResponse("Verification email sent"));
    }
}
```

## Service Layer Implementation

### JWT Token Service
```java
@Service
@Transactional
@Slf4j
public class JwtTokenService {

    private final JwtEncoder jwtEncoder;
    private final JwtDecoder jwtDecoder;
    private final JwtClaimsService claimsService;
    private final BlacklistedTokenRepository blacklistedTokenRepository;

    public JwtTokenService(JwtEncoder jwtEncoder,
                          JwtDecoder jwtDecoder,
                          JwtClaimsService claimsService,
                          BlacklistedTokenRepository blacklistedTokenRepository) {
        this.jwtEncoder = jwtEncoder;
        this.jwtDecoder = jwtDecoder;
        this.claimsService = claimsService;
        this.blacklistedTokenRepository = blacklistedTokenRepository;
    }

    public AccessTokenResponse generateAccessToken(User user) {
        JwtClaimsSet claims = claimsService.createAccessTokenClaims(user);
        String tokenValue = jwtEncoder.encode(
            JwtEncoderParameters.from(claims)).getTokenValue();

        return new AccessTokenResponse(
            tokenValue,
            claims.getExpiresAt().toEpochMilli(),
            claims.getIssuedAt().toEpochMilli(),
            claims.getClaimAsString("type")
        );
    }

    public String extractTokenClaim(String token, String claimName) {
        try {
            Jwt jwt = jwtDecoder.decode(token);
            return jwt.getClaimAsString(claimName);
        } catch (JwtException e) {
            throw new InvalidTokenException("Invalid token", e);
        }
    }

    public boolean isTokenValid(String token) {
        try {
            // Check if token is blacklisted
            String jti = extractTokenClaim(token, "jti");
            if (blacklistedTokenRepository.existsByTokenId(jti)) {
                return false;
            }

            // Decode and validate token
            Jwt jwt = jwtDecoder.decode(token);
            return jwt.getExpiresAt() != null &&
                   Instant.now().isBefore(jwt.getExpiresAt());
        } catch (JwtException e) {
            return false;
        }
    }

    public void blacklistToken(String token) {
        String jti = extractTokenClaim(token, "jti");
        Instant expiresAt = Instant.ofEpochMilli(
            Long.parseLong(extractTokenClaim(token, "exp")));

        BlacklistedToken blacklistedToken = new BlacklistedToken(
            jti, token, expiresAt);
        blacklistedTokenRepository.save(blacklistedToken);
    }

    @Scheduled(fixedRate = 3600000) // Every hour
    public void cleanupExpiredBlacklistedTokens() {
        List<BlacklistedToken> expiredTokens = blacklistedTokenRepository
            .findByExpiresAtBefore(Instant.now());

        blacklistedTokenRepository.deleteAll(expiredTokens);
        log.info("Cleaned up {} expired blacklisted tokens", expiredTokens.size());
    }
}
```

### Refresh Token Service
```java
@Service
@Transactional
@Slf4j
public class RefreshTokenService {

    private final JwtTokenService jwtTokenService;
    private final JwtClaimsService claimsService;
    private final RefreshTokenRepository refreshTokenRepository;
    private final UserRepository userRepository;

    @Value("${jwt.refresh-token-expiration:P7D}")
    private Duration refreshTokenExpiration;

    public RefreshTokenResponse createRefreshToken(User user) {
        // Revoke existing refresh tokens if too many
        long activeTokens = refreshTokenRepository.countByUserAndExpiresAtAfter(user, Instant.now());
        if (activeTokens >= 5) {
            refreshTokenRepository.deleteOldestByUser(user);
        }

        JwtClaimsSet claims = claimsService.createRefreshTokenClaims(user);
        String tokenValue = jwtTokenService.encodeToken(claims);

        RefreshToken refreshToken = new RefreshToken(
            tokenValue,
            user,
            claims.getExpiresAt(),
            claims.getClaimAsString("sessionId"),
            claims.getClaimAsString("jti")
        );

        refreshToken = refreshTokenRepository.save(refreshToken);

        return new RefreshTokenResponse(
            refreshToken.getToken(),
            refreshToken.getExpiresAt().toEpochMilli()
        );
    }

    public RefreshTokenResponse refreshToken(RefreshTokenRequest request) {
        String refreshTokenValue = request.refreshToken();

        // Validate refresh token
        RefreshToken refreshToken = refreshTokenRepository
            .findByToken(refreshTokenValue)
            .orElseThrow(() -> new InvalidTokenException("Refresh token not found"));

        if (refreshToken.isExpired()) {
            refreshTokenRepository.delete(refreshToken);
            throw new ExpiredTokenException("Refresh token expired");
        }

        if (!refreshToken.isActive()) {
            throw new InvalidTokenException("Refresh token has been revoked");
        }

        User user = refreshToken.getUser();
        if (!user.isEnabled() || !user.isAccountNonLocked()) {
            throw new AccountDisabledException("Account is disabled or locked");
        }

        // Generate new access token
        AccessTokenResponse accessToken = jwtTokenService.generateAccessToken(user);

        // Optional: Rotate refresh token
        if (shouldRotateRefreshToken(refreshToken)) {
            refreshTokenRepository.delete(refreshToken);
            return createRefreshToken(user);
        }

        return new RefreshTokenResponse(
            accessToken.token(),
            accessToken.expiresAt(),
            refreshToken.getToken(),
            refreshToken.getExpiresAt().toEpochMilli()
        );
    }

    public void revokeRefreshToken(String token) {
        refreshTokenRepository.findByToken(token)
            .ifPresent(refreshToken -> {
                refreshToken.setRevoked(true);
                refreshToken.setRevokedAt(Instant.now());
                refreshTokenRepository.save(refreshToken);
            });
    }

    public void revokeRefreshTokenByJti(String jti) {
        refreshTokenRepository.findByTokenId(jti)
            .ifPresent(refreshToken -> {
                refreshToken.setRevoked(true);
                refreshToken.setRevokedAt(Instant.now());
                refreshTokenRepository.save(refreshToken);
            });
    }

    public void revokeAllRefreshTokens(User user) {
        List<RefreshToken> tokens = refreshTokenRepository
            .findByUserAndRevokedFalse(user);

        tokens.forEach(token -> {
            token.setRevoked(true);
            token.setRevokedAt(Instant.now());
        });

        refreshTokenRepository.saveAll(tokens);
    }

    private boolean shouldRotateRefreshToken(RefreshToken refreshToken) {
        // Rotate refresh token if older than 3 days
        return refreshToken.getCreatedAt()
            .isBefore(Instant.now().minus(3, ChronoUnit.DAYS));
    }

    @Scheduled(fixedRate = 86400000) // Daily
    public void cleanupExpiredTokens() {
        Instant cutoff = Instant.now().minus(7, ChronoUnit.DAYS);
        List<RefreshToken> expiredTokens = refreshTokenRepository
            .findByExpiresAtBefore(cutoff);

        refreshTokenRepository.deleteAll(expiredTokens);
        log.info("Cleaned up {} expired refresh tokens", expiredTokens.size());
    }
}
```

### User Service
```java
@Service
@Transactional
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final RoleRepository roleRepository;

    public User createUser(RegistrationRequest request) {
        User user = User.builder()
            .email(request.email())
            .password(passwordEncoder.encode(request.password()))
            .firstName(request.firstName())
            .lastName(request.lastName())
            .phoneNumber(request.phoneNumber())
            .enabled(true)
            .emailVerified(false)
            .build();

        // Assign default role
        Role userRole = roleRepository.findByName("USER")
            .orElseThrow(() -> new IllegalStateException("Default USER role not found"));
        user.setRoles(Set.of(userRole));

        return userRepository.save(user);
    }

    public void changePassword(User user, ChangePasswordRequest request) {
        // Validate current password
        if (!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new InvalidPasswordException("Current password is incorrect");
        }

        // Validate new password
        if (!request.newPassword().equals(request.confirmPassword())) {
            throw new PasswordMismatchException("New passwords do not match");
        }

        // Update password
        user.setPassword(passwordEncoder.encode(request.newPassword()));
        userRepository.save(user);

        // Force login from other devices
        // This would trigger refresh token invalidation
    }

    public void recordLogin(User user, String deviceInfo, String ipAddress) {
        UserLogin login = UserLogin.builder()
            .user(user)
            .loginAt(Instant.now())
            .ipAddress(ipAddress)
            .userAgent(deviceInfo)
            .build();

        user.addLogin(login);
        userRepository.save(user);
    }

    public void recordLogout(User user, String ipAddress) {
        Optional<UserLogin> lastLogin = user.getLogins().stream()
            .filter(login -> login.getLogoutAt() == null)
            .findFirst();

        lastLogin.ifPresent(login -> {
            login.setLogoutAt(Instant.now());
            login.setLogoutIpAddress(ipAddress);
            userRepository.save(user);
        });
    }

    public String generateEmailVerificationToken(User user) {
        String token = UUID.randomUUID().toString();
        user.setEmailVerificationToken(token);
        user.setEmailVerificationTokenExpiry(Instant.now().plus(24, ChronoUnit.HOURS));
        userRepository.save(user);
        return token;
    }

    @Transactional
    public User verifyEmail(String token) {
        User user = userRepository.findByEmailVerificationToken(token)
            .orElseThrow(() -> new InvalidTokenException("Invalid verification token"));

        if (user.getEmailVerificationTokenExpiry().isBefore(Instant.now())) {
            throw new ExpiredTokenException("Verification token expired");
        }

        user.setEmailVerified(true);
        user.setEmailVerificationToken(null);
        user.setEmailVerificationTokenExpiry(null);

        return userRepository.save(user);
    }
}
```

## Advanced Security Configuration

### Complete Security Configuration
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationEntryPoint authenticationEntryPoint;
    private final JwtAccessDeniedHandler accessDeniedHandler;
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final CustomAuthenticationProvider authenticationProvider;
    private final LogoutHandler logoutHandler;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .ignoringRequestMatchers("/api/auth/**", "/api/public/**"))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .exceptionHandling(exception -> exception
                .authenticationEntryPoint(authenticationEntryPoint)
                .accessDeniedHandler(accessDeniedHandler))
            .headers(headers -> headers
                .frameOptions().deny()
                .contentTypeOptions().and()
                .httpStrictTransportSecurity(hstsConfig -> hstsConfig
                    .maxAgeInSeconds(31536000)
                    .includeSubdomains(true))
                .cacheControl())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/api/public/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/manager/**").hasAnyRole("MANAGER", "ADMIN")
                .requestMatchers("/api/users/me").authenticated()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .decoder(jwtDecoder())
                    .jwtAuthenticationConverter(jwtAuthenticationConverter())))
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")
                .addLogoutHandler(logoutHandler)
                .logoutSuccessHandler((request, response, authentication) ->
                    response.setStatus(HttpStatus.NO_CONTENT.value())))
            .build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        // Custom decoder with validation
        return new CustomJwtDecoder(nimbusJwtDecoder(), jwtClaimsValidator());
    }

    @Bean
    public NimbusJwtDecoder nimbusJwtDecoder() {
        return NimbusJwtDecoder.withPublicKey(rsaPublicKey()).build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter authoritiesConverter = new JwtGrantedAuthoritiesConverter();
        authoritiesConverter.setAuthorityPrefix("ROLE_");
        authoritiesConverter.setAuthoritiesClaimName("roles");

        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(authoritiesConverter);
        converter.setPrincipalClaimName("sub");

        return converter;
    }
}
```