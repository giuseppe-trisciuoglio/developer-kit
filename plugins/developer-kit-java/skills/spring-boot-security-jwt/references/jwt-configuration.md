# JWT Configuration and Setup

## Core Dependencies

### Maven Dependencies
```xml
<properties>
    <spring-security.version>6.3.1</spring-security.version>
    <nimbus-jose-jwt.version>9.37.3</nimbus-jose-jwt.version>
</properties>

<dependencies>
    <!-- Core Spring Security -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>

    <!-- OAuth2 Resource Server for JWT support -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
    </dependency>

    <!-- JOSE (JWT) support -->
    <dependency>
        <groupId>org.springframework.security</groupId>
        <artifactId>spring-security-oauth2-jose</artifactId>
    </dependency>

    <!-- Nimbus JOSE+JWT library -->
    <dependency>
        <groupId>com.nimbusds</groupId>
        <artifactId>nimbus-jose-jwt</artifactId>
        <version>${nimbus-jose-jwt.version}</version>
    </dependency>

    <!-- Optional: For password encoding -->
    <dependency>
        <groupId>org.springframework.security</groupId>
        <artifactId>spring-security-crypto</artifactId>
    </dependency>

    <!-- Optional: For JWT claims validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

### Gradle Dependencies
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-oauth2-resource-server'
    implementation 'org.springframework.security:spring-security-oauth2-jose'
    implementation 'com.nimbusds:nimbus-jose-jwt:9.37.3'
    implementation 'org.springframework.security:spring-security-crypto'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
}
```

## JWT Encoder Configuration

### Asymmetric Key Configuration (RSA)
```java
@Configuration
public class JwtConfig {

    @Value("${jwt.key-store:classpath:jwt.jks}")
    private Resource keyStore;

    @Value("${jwt.key-store-password:password}")
    private char[] keyStorePassword;

    @Value("${jwt.key-alias:jwt}")
    private String keyAlias;

    @Value("${jwt.private-key-password:password}")
    private char[] privateKeyPassword;

    @Bean
    public KeyStore keyStore() throws Exception {
        KeyStore ks = KeyStore.getInstance("PKCS12");
        ks.load(keyStore.getInputStream(), keyStorePassword);
        return ks;
    }

    @Bean
    public RSAPrivateKey jwtSigningKey(KeyStore keyStore) throws Exception {
        return (RSAPrivateKey) keyStore.getKey(keyAlias, privateKeyPassword);
    }

    @Bean
    public RSAPublicKey jwtValidationKey(KeyStore keyStore) throws Exception {
        return (RSAPublicKey) keyStore.getCertificate(keyAlias).getPublicKey();
    }

    @Bean
    public JwtEncoder jwtEncoder(RSAPrivateKey privateKey) {
        JWKSet jwkSet = new JWKSet(new RSAKey.Builder(privateKey).build());
        return new NimbusJwtEncoder(new ImmutableJWKSet<>(jwkSet));
    }

    @Bean
    public JwtDecoder jwtDecoder(RSAPublicKey publicKey) {
        RSAKey key = new RSAKey.Builder(publicKey).build();
        JWKSet jwkSet = new JWKSet(key);
        return NimbusJwtDecoder.withPublicKey(publicKey).build();
    }
}
```

### Symmetric Key Configuration (HMAC)
```java
@Configuration
public class SymmetricJwtConfig {

    @Value("${jwt.secret:my-very-long-and-secure-secret-key-for-hmac-sha256}")
    private String jwtSecret;

    @Bean
    public JwtEncoder jwtEncoder() {
        SecretKey key = Keys.hmacShaKeyFor(
            Decoders.BASE64URL.decode(EncodedSecretKey.get(jwtSecret)));
        return new NimbusJwtEncoder(new ImmutableSecret<>(key));
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        SecretKey key = Keys.hmacShaKeyFor(
            Decoders.BASE64URL.decode(EncodedSecretKey.get(jwtSecret)));
        return NimbusJwtDecoder.withSecretKey(key).build();
    }

    @Component
    static class EncodedSecretKey {
        static String get(String secret) {
            // Ensure minimum 256 bits for HS256
            if (secret.length() < 32) {
                throw new IllegalArgumentException(
                    "JWT secret must be at least 32 characters");
            }
            return Base64.getUrlEncoder()
                .withoutPadding()
                .encodeToString(secret.getBytes(StandardCharsets.UTF_8));
        }
    }
}
```

### ECDSA Key Configuration (Elliptic Curve)
```java
@Configuration
public class EcdsaJwtConfig {

    @Value("${jwt.ecdsa-private-key}")
    private String ecdsaPrivateKey;

    @Value("${jwt.ecdsa-public-key}")
    private String ecdsaPublicKey;

    @Bean
    public JwtEncoder jwtEncoder() throws Exception {
        ECPrivateKey privateKey = (ECPrivateKey) KeyFactory
            .getInstance("EC")
            .generatePrivate(new PKCS8EncodedKeySpec(
                Base64.getDecoder().decode(ecdsaPrivateKey)));

        ECKey key = new ECKey.Builder(ECKey.Curve.P_256, privateKey).build();
        return new NimbusJwtEncoder(new ImmutableJWKSet<>(new JWKSet(key)));
    }

    @Bean
    public JwtDecoder jwtDecoder() throws Exception {
        ECPublicKey publicKey = (ECPublicKey) KeyFactory
            .getInstance("EC")
            .generatePublic(new X509EncodedKeySpec(
                Base64.getDecoder().decode(ecdsaPublicKey)));

        return NimbusJwtDecoder.withPublicKey(publicKey).build();
    }
}
```

## JWT Claims Configuration

### Custom Claims Set Builder
```java
@Service
public class JwtClaimsService {

    @Value("${jwt.issuer:http://localhost:8080}")
    private String issuer;

    @Value("${jwt.audience:my-app}")
    private String audience;

    @Value("${jwt.access-token-expiration:PT15M}")
    private Duration accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration:P7D}")
    private Duration refreshTokenExpiration;

    public JwtClaimsSet createAccessTokenClaims(User user) {
        Instant now = Instant.now();
        List<String> authorities = user.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toList());

        return JwtClaimsSet.builder()
            .issuer(issuer)
            .subject(user.getId().toString())
            .audience(List.of(audience))
            .issuedAt(now)
            .expiresAt(now.plus(accessTokenExpiration))
            .claim("email", user.getEmail())
            .claim("roles", authorities)
            .claim("name", user.getFullName())
            .claim("type", "access")
            .claim("jti", UUID.randomUUID().toString())
            .build();
    }

    public JwtClaimsSet createRefreshTokenClaims(User user) {
        Instant now = Instant.now();

        return JwtClaimsSet.builder()
            .issuer(issuer)
            .subject(user.getId().toString())
            .audience(List.of(audience))
            .issuedAt(now)
            .expiresAt(now.plus(refreshTokenExpiration))
            .claim("email", user.getEmail())
            .claim("type", "refresh")
            .claim("jti", UUID.randomUUID().toString())
            .claim("sessionId", UUID.randomUUID().toString())
            .build();
    }
}
```

### JWT Token Service
```java
@Service
@Transactional
public class JwtTokenService {

    private final JwtEncoder jwtEncoder;
    private final JwtClaimsService claimsService;
    private final RefreshTokenRepository refreshTokenRepository;

    public JwtTokenService(JwtEncoder jwtEncoder,
                          JwtClaimsService claimsService,
                          RefreshTokenRepository refreshTokenRepository) {
        this.jwtEncoder = jwtEncoder;
        this.claimsService = claimsService;
        this.refreshTokenRepository = refreshTokenRepository;
    }

    public AccessTokenResponse generateAccessToken(User user) {
        JwtClaimsSet claims = claimsService.createAccessTokenClaims(user);
        String tokenValue = jwtEncoder.encode(
            JwtEncoderParameters.from(claims)).getTokenValue();

        return new AccessTokenResponse(
            tokenValue,
            claims.getExpiresAt().toEpochMilli(),
            claims.getIssuedAt().toEpochMilli(),
            claims.getClaimAsString("type"));
    }

    public RefreshTokenResponse generateRefreshToken(User user) {
        JwtClaimsSet claims = claimsService.createRefreshTokenClaims(user);
        String tokenValue = jwtEncoder.encode(
            JwtEncoderParameters.from(claims)).getTokenValue();

        // Store refresh token in database
        RefreshToken refreshToken = new RefreshToken(
            tokenValue,
            user,
            claims.getExpiresAt(),
            claims.getClaimAsString("sessionId"));

        refreshTokenRepository.save(refreshToken);

        return new RefreshTokenResponse(
            tokenValue,
            claims.getExpiresAt().toEpochMilli());
    }

    public Jwt parseToken(String token) {
        try {
            return jwtDecoder.decode(token);
        } catch (JwtException e) {
            throw new InvalidTokenException("Failed to parse JWT token", e);
        }
    }
}
```

## Application Properties

### JWT Configuration Properties
```yaml
jwt:
  issuer: "https://api.myapp.com"
  audience: "myapp-client"
  access-token-expiration: "PT15M"  # 15 minutes
  refresh-token-expiration: "P7D"   # 7 days

  # RSA Configuration
  key-store: "classpath:jwt.jks"
  key-store-password: "${JWT_KEYSTORE_PASSWORD:password}"
  key-alias: "jwt"
  private-key-password: "${JWT_PRIVATE_KEY_PASSWORD:password}"

  # HMAC Configuration (alternative to RSA)
  secret: "${JWT_SECRET:very-long-secret-key-at-least-256-bits}"

  # ECDSA Configuration (alternative)
  ecdsa-private-key: "${JWT_ECDSA_PRIVATE_KEY}"
  ecdsa-public-key: "${JWT_ECDSA_PUBLIC_KEY}"

  # Token validation
  allowed-clock-skew: "PT30S"  # 30 seconds
  require-issuer: true
  require-audience: true
  require-subject: true
  require-expiration: true
```

### Security Configuration
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: "https://auth.myapp.com"
          jwk-set-uri: "https://auth.myapp.com/.well-known/jwks.json"

          # Custom JWT decoder configuration
          audiences: "myapp-client"
          public-key-location: "classpath:jwt.pub"

          # JWT claim mappings
          principal-attribute: "sub"
          authorities-attribute: "roles"

          # Decoder configuration
          jwt-decoder-algorithm: "RS256"  # RS256, ES256, HS256

          # Cache configuration for JWK Set
          jwk-set-cache:
            cache-timeout: "PT5M"   # 5 minutes
            cache-ttl: "PT30M"      # 30 minutes

    # Session management for stateful cookie-based auth
    sessions:
      maximum-sessions: 5
      max-sessions-prevents-login: false

    # Remember-me configuration
    remember-me:
      key: "${REMEMBER_ME_KEY}"
      token-validity: 604800  # 7 days

# CORS configuration
cors:
  allowed-origins:
    - "https://app.myapp.com"
    - "https://admin.myapp.com"
  allowed-methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  allowed-headers:
    - "Authorization"
    - "Content-Type"
    - "X-Requested-With"
  allow-credentials: true
  max-age: 3600
```

## Key Management Utilities

### Key Generator for RSA
```java
@Component
public class RsaKeyGenerator {

    @EventListener(ApplicationReadyEvent.class)
    public void generateKeys() throws Exception {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
        keyPairGenerator.initialize(2048);
        KeyPair keyPair = keyPairGenerator.generateKeyPair();

        // Store keys in JKS format
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        keyStore.load(null, null);

        char[] password = "changeit".toCharArray();
        Certificate[] chain = new Certificate[] { generateSelfSignedCertificate(keyPair) };

        keyStore.setKeyEntry("jwt", keyPair.getPrivate(), password, chain);

        // Save to file
        try (FileOutputStream fos = new FileOutputStream("jwt.jks")) {
            keyStore.store(fos, password);
        }
    }

    private Certificate generateSelfSignedCertificate(KeyPair keyPair) {
        // Implementation for self-signed certificate generation
        // Use Bouncy Castle or similar library
        return null;
    }
}
```

### Key Rotation Support
```java
@Configuration
public class KeyRotationConfig {

    @Bean
    @Primary
    public JwtDecoder jwtDecoder(List<JWKSet> jwkSets) {
        // Merge multiple key sets for rotation support
        JWKSet mergedSet = jwkSets.stream()
            .reduce(JWKSet::new)
            .orElse(new JWKSet());

        return NimbusJwtDecoder.withJwkSetUri(jwkSetUri())
            .jwsAlgorithm(JWSAlgorithm.RS256)
            .build();
    }

    @Bean
    public JWKSet currentJwkSet(@Value("${jwt.current-key-id}") String currentKeyId) {
        // Load current key set from database or file
        return loadJwkSetFromStorage(currentKeyId);
    }

    @Bean
    public JWKSet previousJwkSet(@Value("${jwt.previous-key-id}") String previousKeyId) {
        // Load previous key set for validation of existing tokens
        return loadJwkSetFromStorage(previousKeyId);
    }
}
```

## Custom JWT Decoder

### Enhanced JWT Decoder with Validation
```java
@Component
public class CustomJwtDecoder implements JwtDecoder {

    private final JwtDecoder delegate;
    private final JwtClaimsValidator claimsValidator;

    public CustomJwtDecoder(JwtDecoder delegate,
                           JwtClaimsValidator claimsValidator) {
        this.delegate = delegate;
        this.claimsValidator = claimsValidator;
    }

    @Override
    public Jwt decode(String token) throws JwtException {
        Jwt jwt = delegate.decode(token);

        // Validate claims
        claimsValidator.validate(jwt);

        // Add custom processing
        if (hasRequiredClaims(jwt)) {
            return jwt;
        }

        throw new JwtException("JWT validation failed");
    }

    private boolean hasRequiredClaims(Jwt jwt) {
        return jwt.containsClaim("type") &&
               jwt.containsClaim("jti") &&
               jwt.containsClaim("sessionId");
    }
}
```

### Claims Validator
```java
@Component
public class JwtClaimsValidator {

    @Value("${jwt.issuer}")
    private String expectedIssuer;

    @Value("${jwt.audience}")
    private String expectedAudience;

    @Value("${jwt.allowed-clock-skew:PT30S}")
    private Duration allowedClockSkew;

    public void validate(Jwt jwt) {
        validateIssuer(jwt);
        validateAudience(jwt);
        validateExpiration(jwt);
        validateNotBefore(jwt);
        validateIssuedAt(jwt);
        validateType(jwt);
    }

    private void validateIssuer(Jwt jwt) {
        if (!expectedIssuer.equals(jwt.getIssuer())) {
            throw new JwtException("Invalid issuer: " + jwt.getIssuer());
        }
    }

    private void validateAudience(Jwt jwt) {
        if (jwt.getAudience() == null ||
            !jwt.getAudience().contains(expectedAudience)) {
            throw new JwtException("Invalid audience");
        }
    }

    private void validateExpiration(Jwt jwt) {
        Instant now = Instant.now();
        Instant exp = jwt.getExpiresAt();

        if (exp == null || now.isAfter(exp.plus(allowedClockSkew))) {
            throw new JwtException("Token expired");
        }
    }

    private void validateNotBefore(Jwt jwt) {
        Instant now = Instant.now();
        Instant nbf = jwt.getNotBefore();

        if (nbf != null && now.isBefore(nbf.minus(allowedClockSkew))) {
            throw new JwtException("Token not yet valid");
        }
    }

    private void validateIssuedAt(Jwt jwt) {
        Instant now = Instant.now();
        Instant iat = jwt.getIssuedAt();

        if (iat != null && now.isBefore(iat.minus(allowedClockSkew))) {
            throw new JwtException("Token issued in the future");
        }
    }

    private void validateType(Jwt jwt) {
        String type = jwt.getClaimAsString("type");
        if (!"access".equals(type)) {
            throw new JwtException("Invalid token type: " + type);
        }
    }
}
```