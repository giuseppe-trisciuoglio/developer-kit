# Migration Guide: Spring Security 5.x to 6.x for JWT

This guide helps you migrate JWT authentication from Spring Security 5.x to 6.x, covering the major API changes and best practices.

## Table of Contents

1. [Overview of Changes](#overview-of-changes)
2. [Configuration Changes](#configuration-changes)
3. [JWT Filter Changes](#jwt-filter-changes)
4. [Authentication Provider Changes](#authentication-provider-changes)
5. [CORS Configuration Changes](#cors-configuration-changes)
6. [Method Security Changes](#method-security-changes)
7. [Common Migration Issues](#common-migration-issues)
8. [Step-by-Step Migration](#step-by-step-migration)

## Overview of Changes

Spring Security 6.x introduced significant changes to the security configuration API, moving from the deprecated `WebSecurityConfigurerAdapter` to a more functional approach using `SecurityFilterChain`.

### Key Changes:
- `WebSecurityConfigurerAdapter` is deprecated
- `antMatchers()` replaced with `requestMatchers()`
- `and()` method chaining removed
- Lambda DSL is now the default
- `csrf()` and `cors()` require explicit configuration
- New `authorizeHttpRequests()` method

## Configuration Changes

### Before (Spring Security 5.x)
```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeRequests()
                .antMatchers("/api/auth/**").permitAll()
                .antMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
    }
}
```

### After (Spring Security 6.x)
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Changed from EnableGlobalMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Lambda DSL required
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(authz -> authz // New method
                .requestMatchers("/api/auth/**").permitAll() // Changed from antMatchers
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

## JWT Filter Changes

### Before (Spring Security 5.x)
```java
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            // ... token validation logic
        }

        filterChain.doFilter(request, response);
    }
}
```

### After (Spring Security 6.x)
```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request,
                                   @NonNull HttpServletResponse response,
                                   @NonNull FilterChain filterChain) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);
        String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);

            if (jwtService.isTokenValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                    userDetails, null, userDetails.getAuthorities()
                );
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

## Authentication Provider Changes

### Before (Spring Security 5.x)
```java
@Bean
public AuthenticationProvider authenticationProvider() {
    DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
    authProvider.setUserDetailsService(userDetailsService);
    authProvider.setPasswordEncoder(passwordEncoder());
    return authProvider;
}
```

### After (Spring Security 6.x)
```java
@Bean
public AuthenticationProvider authenticationProvider() {
    DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
    authProvider.setUserDetailsService(userDetailsService);
    authProvider.setPasswordEncoder(passwordEncoder());
    return authProvider;
}

// No changes needed - same implementation
```

## CORS Configuration Changes

### Before (Spring Security 5.x)
```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
```

### After (Spring Security 6.x)
```java
@Configuration
public class CorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of("*")); // Changed from setAllowedOrigins
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

## Method Security Changes

### Before (Spring Security 5.x)
```java
@EnableGlobalMethodSecurity(
    prePostEnabled = true,
    securedEnabled = true,
    jsr250Enabled = true
)
```

### After (Spring Security 6.x)
```java
@EnableMethodSecurity( // Simplified annotation
    prePostEnabled = true,
    securedEnabled = true,
    jsr250Enabled = true
)
```

### Method Security Usage
```java
@Service
public class UserService {

    @PreAuthorize("hasRole('ADMIN')") // No changes
    public List<User> getAllUsers() {
        // ...
    }

    @PreAuthorize("hasRole('USER') or #username == authentication.name")
    public User getUser(String username) {
        // ...
    }
}
```

## Common Migration Issues

### Issue 1: `antMatchers()` Not Found
**Error**: `The method antMatchers(String) is undefined for the type ExpressionInterceptUrlRegistry`

**Solution**: Use `requestMatchers()` instead
```java
// Before
.antMatchers("/api/auth/**").permitAll()

// After
.requestMatchers("/api/auth/**").permitAll()
```

### Issue 2: `and()` Method Not Found
**Error**: `The method and() is undefined`

**Solution**: Use lambda DSL
```java
// Before
http
    .csrf().disable()
    .and()
    .sessionManagement()...

// After
http
    .csrf(csrf -> csrf.disable())
    .sessionManagement(session -> ...)...
```

### Issue 3: `WebSecurityConfigurerAdapter` Deprecated
**Warning**: `The type WebSecurityConfigurerAdapter is deprecated`

**Solution**: Use `SecurityFilterChain` bean
```java
// Before
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // ...
    }
}

// After
public class SecurityConfig {
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        // ...
        return http.build();
    }
}
```

### Issue 4: `configure(AuthenticationManagerBuilder)` Not Working
**Error**: Authentication configuration not applied

**Solution**: Use `AuthenticationManager` bean
```java
// Before
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
    auth.userDetailsService(userDetailsService).passwordEncoder(passwordEncoder());
}

// After
@Bean
public AuthenticationManager authenticationManager(
        UserDetailsService userDetailsService,
        PasswordEncoder passwordEncoder) throws Exception {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(userDetailsService);
    provider.setPasswordEncoder(passwordEncoder);
    return new ProviderManager(provider);
}
```

## Step-by-Step Migration

### Step 1: Update Dependencies
```xml
<!-- pom.xml -->
<properties>
    <spring-boot.version>3.5.0</spring-boot.version>
    <spring-security.version>6.3.0</spring-security.version>
</properties>
```

### Step 2: Update Configuration Class
```java
// Remove extends WebSecurityConfigurerAdapter
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Update annotation
public class SecurityConfig {

    // Add SecurityFilterChain bean
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        // Configuration using lambda DSL
        return http.build();
    }
}
```

### Step 3: Update Request Matchers
```java
// Replace all antMatchers() with requestMatchers()
http
    .authorizeHttpRequests(authz -> authz
        .requestMatchers("/api/auth/**").permitAll()
        .requestMatchers(HttpMethod.GET, "/api/public/**").permitAll()
        .anyRequest().authenticated()
    )
```

### Step 4: Update CORS Configuration
```java
// If using WebMvcConfigurer, switch to CorsConfigurationSource
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOriginPatterns(List.of("*"));
    // ... rest of configuration
}
```

### Step 5: Update JWT Filter
```java
// Add @NonNull annotations to parameters
@Override
protected void doFilterInternal(@NonNull HttpServletRequest request,
                               @NonNull HttpServletResponse response,
                               @NonNull FilterChain filterChain) throws ServletException, IOException {
    // ... implementation
}
```

### Step 6: Update Authentication Manager
```java
// Create AuthenticationManager bean instead of overriding
@Bean
public AuthenticationManager authenticationManager(
        UserDetailsService userDetailsService,
        PasswordEncoder passwordEncoder) throws Exception {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(userDetailsService);
    provider.setPasswordEncoder(passwordEncoder);
    return new ProviderManager(provider);
}
```

### Step 7: Update Tests
```java
// Update test configurations
@SpringBootTest
@AutoConfigureMockMvc
class SecurityTest {

    @Test
    void testSecurityConfiguration() throws Exception {
        mockMvc.perform(get("/api/protected"))
                .andExpect(status().isForbidden());
    }
}
```

## New Features in Spring Security 6.x

### 1. Request Authorization Improvements
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(authz -> authz
            .requestMatchers("/api/users/{userId}/**")
                .access(new WebExpressionAuthorizationManager(
                    "@authz.checkUserId(authentication, #userId)"))
            .anyRequest().authenticated()
        );
    return http.build();
}
```

### 2. Custom Authorization Manager
```java
@Component
public class CustomAuthorizationManager implements AuthorizationManager<RequestAuthorizationContext> {

    @Override
    public AuthorizationDecision check(Supplier<Authentication> authentication,
                                      RequestAuthorizationContext context) {
        // Custom authorization logic
        return new AuthorizationDecision(true);
    }
}
```

### 3. Simplified Security Expressions
```java
@PreAuthorize("@securityService.hasPermission(#id, authentication)")
public void deleteResource(Long id) {
    // Method implementation
}
```

## Verification Checklist

After migration, verify:

- [ ] All endpoints are properly secured
- [ ] JWT authentication works correctly
- [ ] CORS configuration is applied
- [ ] Method security annotations work
- [ ] All tests pass
- [ ] No deprecated API warnings
- [ ] Application starts without errors
- [ ] Token generation and validation work
- [ ] Logout functionality works
- [ ] Refresh token mechanism works

## Rollback Plan

If issues arise:

1. Keep the old configuration in a separate branch
2. Gradually migrate components
3. Test thoroughly in staging environment
4. Monitor application logs after deployment
5. Have a quick rollback mechanism ready

## References

- [Spring Security 6.x Migration Guide](https://docs.spring.io/spring-security/reference/5.8/migration/index.html)
- [Spring Boot 3.x Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Release-Notes)
- [Spring Security Configuration Changes](https://spring.io/blog/2022/02/21/spring-security-without-the-websecurityconfigureradapter)
- [OAuth2 Resource Server Configuration](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html)