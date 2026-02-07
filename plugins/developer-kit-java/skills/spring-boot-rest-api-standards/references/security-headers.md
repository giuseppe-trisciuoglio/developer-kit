# Security Headers and CORS Configuration

## Security Headers Configuration

### Basic Security Headers
```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .headers(headers -> headers
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'; " +
                                     "script-src 'self' 'unsafe-inline'; " +
                                     "style-src 'self' 'unsafe-inline'; " +
                                     "img-src 'self' data:; " +
                                     "font-src 'self';")
                    .reportOnly(false))
                .frameOptions(frame -> frame
                    .sameOrigin()
                    .deny()) // Use sameOrigin() for same-origin iframes, deny() to completely block
                .httpStrictTransportSecurity(hsts -> hsts
                    .maxAgeInSeconds(31536000) // 1 year
                    .includeSubDomains(true)
                    .preload(true))
                .xssProtection(xss -> xss
                    .headerValue(XssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
                .contentTypeOptions(contentTypeOptions -> contentTypeOptions
                    .and())
            )
            .cors(cors -> cors
                .configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/**").authenticated()
                .anyRequest().permitAll()
            );

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type", "X-Requested-With"));
        configuration.setExposedHeaders(Arrays.asList("X-Total-Count", "X-Content-Type-Options"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### Enhanced Security Configuration
```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class EnhancedSecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/**")
            .headers(headers -> headers
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'; " +
                                     "script-src 'self 'unsafe-inline' 'unsafe-eval'; " +
                                     "style-src 'self 'unsafe-inline'; " +
                                     "img-src 'self' data: https:; " +
                                     "font-src 'self'; " +
                                     "connect-src 'self' https:; " +
                                     "frame-src 'none'; " +
                                     "object-src 'none';"))
                .frameOptions(frameOptions -> frameOptions.sameOrigin())
                .httpStrictTransportSecurity(hsts -> hsts
                    .maxAgeInSeconds(31536000)
                    .includeSubDomains(true)
                    .preload(true)
                    .includeSubDomains(true))
                .permissionsPolicy(permissionsPolicy -> permissionsPolicy
                    .add("camera", "()")
                    .add("geolocation", "()")
                    .add("microphone", "()")
                    .add("payment", "()"))
                .referrerPolicy(referrerPolicy -> referrerPolicy.noReferrer())
                .and())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf
                .ignoringRequestMatchers("/api/auth/**")
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.GET, "/api/users/**").hasAnyRole("USER", "ADMIN")
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            );

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // Allowed origins (consider restricting to specific domains in production)
        configuration.setAllowedOriginPatterns(List.of("https://yourdomain.com", "https://app.yourdomain.com"));

        // Allowed methods
        configuration.setAllowedMethods(Arrays.asList(
            "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
        ));

        // Allowed headers
        configuration.setAllowedHeaders(Arrays.asList(
            "Authorization",
            "Content-Type",
            "Accept",
            "X-Requested-With",
            "X-Content-Type-Options",
            "X-Total-Count",
            "Cache-Control"
        ));

        // Exposed headers to client
        configuration.setExposedHeaders(Arrays.asList(
            "X-Total-Count",
            "X-Content-Type-Options",
            "Cache-Control"
        ));

        // Allow credentials
        configuration.setAllowCredentials(true);

        // Cache preflight requests for 1 hour
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        return source;
    }
}
```

## Content Security Policy (CSP)

### Basic CSP Configuration
```java
@Configuration
public class ContentSecurityPolicyConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("https://yourdomain.com")
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                    .allowedHeaders("*")
                    .exposedHeaders("X-Total-Count")
                    .allowCredentials(true)
                    .maxAge(3600);
            }

            @Override
            public void addInterceptors(InterceptorRegistry registry) {
                registry.addInterceptor(new ContentSecurityPolicyInterceptor());
            }
        };
    }
}

@Component
public class ContentSecurityPolicyInterceptor implements HandlerInterceptor {

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response,
                          Object handler, ModelAndView modelAndView) throws Exception {
        response.setHeader("Content-Security-Policy",
            "default-src 'self'; " +
            "script-src 'self' 'unsafe-inline'; " +
            "style-src 'self' 'unsafe-inline'; " +
            "img-src 'self' data:; " +
            "font-src 'self'; " +
            "connect-src 'self'; " +
            "frame-src 'none'; " +
            "object-src 'none';");

        response.setHeader("X-Content-Type-Options", "nosniff");
        response.setHeader("X-Frame-Options", "DENY");
        response.setHeader("X-XSS-Protection", "1; mode=block");
    }
}
```

### Advanced CSP with Nonce
```java
@Component
@RequiredArgsConstructor
public class SecurityHeadersFilter extends OncePerRequestFilter {

    private final AtomicLong nonceCounter = new AtomicLong(0);

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                 HttpServletResponse response,
                                 FilterChain filterChain) throws ServletException, IOException {

        // Generate nonce for each request
        String nonce = String.valueOf(nonceCounter.incrementAndGet());

        // Set CSP header with nonce for inline scripts
        response.setHeader("Content-Security-Policy",
            "default-src 'self'; " +
            "script-src 'self' 'nonce-" + nonce + "'; " +
            "style-src 'self' 'unsafe-inline'; " +
            "img-src 'self' data:; " +
            "font-src 'self'; " +
            "connect-src 'self'; " +
            "frame-src 'none'; " +
            "object-src 'none';");

        // Add nonce to request attributes for templates
        request.setAttribute("cspNonce", nonce);

        // Set other security headers
        response.setHeader("X-Content-Type-Options", "nosniff");
        response.setHeader("X-Frame-Options", "SAMEORIGIN");
        response.setHeader("Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload");
        response.setHeader("X-Permitted-Cross-Domain-Policies", "none");
        response.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");

        filterChain.doFilter(request, response);
    }
}
```

## CORS Configuration

### Method-level CORS
```java
@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "https://yourdomain.com", methods = {RequestMethod.GET, RequestMethod.POST})
public class UserController {

    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        // CORS allowed for GET requests
        return ResponseEntity.ok(userService.findAll());
    }

    @PostMapping
    @CrossOrigin(origins = "https://app.yourdomain.com")
    public ResponseEntity<User> createUser(@RequestBody User user) {
        // CORS allowed with different origin for POST requests
        return ResponseEntity.status(HttpStatus.CREATED).body(userService.create(user));
    }
}
```

### Dynamic CORS Configuration
```java
@Configuration
public class DynamicCorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();

        // Development configuration
        CorsConfiguration devConfig = new CorsConfiguration();
        devConfig.setAllowedOriginPatterns(List.of("*"));
        devConfig.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        devConfig.setAllowedHeaders(Arrays.asList("*"));
        devConfig.setAllowCredentials(true);
        source.registerCorsConfiguration("/api/**", devConfig);

        // Production configuration - restrict to specific domains
        CorsConfiguration prodConfig = new CorsConfiguration();
        prodConfig.setAllowedOriginPatterns(List.of(
            "https://yourdomain.com",
            "https://app.yourdomain.com",
            "https://api.yourdomain.com"
        ));
        prodConfig.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        prodConfig.setAllowedHeaders(Arrays.asList(
            "Authorization",
            "Content-Type",
            "Accept",
            "X-Requested-With"
        ));
        prodConfig.setExposedHeaders(Arrays.asList("X-Total-Count"));
        prodConfig.setAllowCredentials(true);
        source.registerCorsConfiguration("/api/**", prodConfig);

        return source;
    }
}
```

## Security Headers Best Practices

### Essential Headers for Production
1. **Content-Security-Policy**: Mitigates XSS attacks
2. **X-Content-Type-Options**: Prevents MIME type sniffing
3. **X-Frame-Options**: Prevents clickjacking
4. **Strict-Transport-Security**: Enforces HTTPS
5. **X-XSS-Protection**: Legacy browser XSS protection
6. **Referrer-Policy**: Controls referrer information

### CSP Examples by Application Type

#### Blog/Content Site
```java
response.setHeader("Content-Security-Policy",
    "default-src 'self'; " +
    "script-src 'self' https://cdn.jsdelivr.net; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' https: data:; " +
    "font-src 'self'; " +
    "connect-src 'self'; " +
    "frame-src https://www.youtube.com; " +
    "media-src https://www.youtube.com;");
```

#### Single Page Application (SPA)
```java
response.setHeader("Content-Security-Policy",
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data:; " +
    "font-src 'self'; " +
    "connect-src 'self' wss:; " +
    "frame-src 'none'; " +
    "object-src 'none';");
```

#### API Only
```java
response.setHeader("Content-Security-Policy",
    "default-src 'self'; " +
    "connect-src 'self'; " +
    "frame-src 'none'; " +
    "object-src 'none';");
```

### Security Header Testing

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class SecurityHeadersTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void securityHeaders_shouldBeSet() throws Exception {
        mockMvc.perform(get("/api/users"))
            .andExpect(header().string("Content-Security-Policy", notNullValue()))
            .andExpect(header().string("X-Content-Type-Options", "nosniff"))
            .andExpect(header().string("X-Frame-Options", notNullValue()))
            .andExpect(header().string("Strict-Transport-Security", notNullValue()));
    }
}
```

## Rate Limiting

### Basic Rate Limiting
```java
@Component
public class RateLimitingFilter extends OncePerRequestFilter {

    private final ConcurrentHashMap<String, RateLimit> rateLimits = new ConcurrentHashMap<>();
    private static final long REQUEST_LIMIT = 100;
    private static final long TIME_WINDOW = 60_000; // 1 minute

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                 HttpServletResponse response,
                                 FilterChain filterChain) throws ServletException, IOException {

        String clientIp = request.getRemoteAddr();
        String path = request.getRequestURI();
        String key = clientIp + ":" + path;

        RateLimit rateLimit = rateLimits.computeIfAbsent(key, k -> new RateLimit());

        synchronized (rateLimit) {
            if (System.currentTimeMillis() - rateLimit.resetTime > TIME_WINDOW) {
                rateLimit.count = 0;
                rateLimit.resetTime = System.currentTimeMillis();
            }

            if (rateLimit.count >= REQUEST_LIMIT) {
                response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
                response.getWriter().write("Rate limit exceeded");
                return;
            }

            rateLimit.count++;
        }

        filterChain.doFilter(request, response);
    }

    private static class RateLimit {
        long count = 0;
        long resetTime = System.currentTimeMillis();
    }
}
```

## Token-based Authentication Headers

```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                 HttpServletResponse response,
                                 FilterChain filterChain) throws ServletException, IOException {

        try {
            String jwt = getJwtFromRequest(request);

            if (StringUtils.hasText(jwt) && jwtTokenProvider.validateToken(jwt)) {
                UsernamePasswordAuthenticationToken authentication =
                    jwtTokenProvider.getAuthentication(jwt);
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }

            filterChain.doFilter(request, response);
        } catch (Exception ex) {
            logger.error("Could not set user authentication in security context", ex);
            response.sendError(HttpStatus.UNAUTHORIZED.value(), "Unauthorized");
        }
    }

    private String getJwtFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

## WebSocket Security

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketSecurityConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
               .setAllowedOriginPatterns("https://yourdomain.com")
               .withSockJS();
    }

    @Override
    public void configureClientInboundChannel(ChannelRegistration registration) {
        registration.interceptors(new ChannelInterceptor() {
            @Override
            public Message<?> preSend(Message<?> message, MessageChannel channel) {
                StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);

                if (StompCommand.CONNECT.equals(accessor.getCommand())) {
                    // Validate token and authenticate
                    String token = accessor.getFirstNativeHeader("Authorization");
                    if (!isValidToken(token)) {
                        throw new UnauthorizedWebSocketException("Invalid token");
                    }
                }

                return message;
            }
        });
    }
}
```