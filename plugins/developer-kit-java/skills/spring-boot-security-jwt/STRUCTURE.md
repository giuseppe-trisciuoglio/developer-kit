# Spring Security JWT Skill Structure

```
spring-boot-security-jwt/
├── SKILL.md                           # Main skill documentation
├── README.md                          # User-friendly overview and quick start
├── STRUCTURE.md                       # This file - skill structure documentation
│
├── references/                        # Comprehensive reference documentation
│   ├── jwt-configuration.md          # Complete JWT setup and configuration
│   ├── examples.md                   # Real-world implementation examples
│   ├── authorization-patterns.md     # RBAC, ABAC, and permission models
│   ├── token-management.md           # Refresh tokens, rotation, and revocation
│   ├── microservices-security.md     # Inter-service authentication
│   ├── oauth2-integration.md         # OAuth2 provider integration
│   ├── testing-jwt-security.md       # Unit and integration testing
│   ├── performance-optimization.md   # Caching and performance tuning
│   ├── security-hardening.md         # Security best practices
│   └── troubleshooting.md            # Common issues and solutions
│
├── scripts/                          # Utility scripts
│   └── test-jwt-setup.sh            # Automated testing script
│
└── assets/                           # Supporting assets and tools
    └── generate-jwt-keys.sh         # Key generation utility
```

## Skill Coverage

### Core Features (SKILL.md)
- JWT generation and validation with multiple algorithms (RSA, HMAC, ECDSA)
- Bearer token and cookie-based authentication patterns
- Database-backed and OAuth2 provider integration
- Both RBAC and permission-based access control
- Advanced patterns: refresh tokens, token rotation, multi-tenancy

### Configuration (jwt-configuration.md)
- Comprehensive dependency management
- Key configuration for RSA, HMAC, and ECDSA
- Custom claims and validation
- Application properties and YAML configurations
- Key rotation support

### Implementation Examples (examples.md)
- Complete application setup
- Domain models (User, Role, Permission entities)
- Authentication and registration controllers
- Service layer implementations
- Advanced security configuration

### Authorization Patterns (authorization-patterns.md)
- Hierarchical role structures
- Custom permission evaluators
- Attribute-Based Access Control (ABAC)
- Time-based access control
- Location-based restrictions
- Organizational access control

### Token Management (token-management.md)
- Secure refresh token storage
- Token rotation strategies
- Token blacklisting
- Session management
- Distributed security events

### Microservices Security (microservices-security.md)
- Inter-service authentication
- API gateway patterns
- Distributed token validation
- Service mesh integration (Istio)
- Circuit breaker patterns

### OAuth2 Integration (oauth2-integration.md)
- Multi-provider support
- Custom OAuth2 user service
- Token exchange patterns
- Delegated authorization
- Client registration API

### Testing (testing-jwt-security.md)
- Unit testing JWT services
- Integration tests with Testcontainers
- Security testing with OWASP ZAP
- Performance testing
- Custom security test utilities

### Performance Optimization (performance-optimization.md)
- Caching strategies for token validation
- Database optimization
- Async processing
- Monitoring and metrics
- Resource optimization

### Security Hardening (security-hardening.md)
- Secure configuration practices
- Attack prevention (brute force, XSS, SQL injection)
- Key management best practices
- Security monitoring
- GDPR compliance features

### Troubleshooting (troubleshooting.md)
- Common JWT token problems
- Authentication flow debugging
- Configuration validation
- Quick fix scripts
- Debugging checklist

## Integration Points

This skill integrates with:

1. **Spring Boot Actuator** - For security monitoring and health checks
2. **Spring Data JPA** - For user and token persistence
3. **Spring Cache** - For token validation caching
4. **JUnit Testing** - For comprehensive security testing
5. **LangChain4j** - For AI-powered security analysis (if needed)

## Quick Start Flow

1. Review README.md for overview
2. Generate keys using `./assets/generate-jwt-keys.sh`
3. Implement basic JWT using SKILL.md quick start
4. Reference jwt-configuration.md for detailed setup
5. Use examples.md for implementation patterns
6. Apply security-hardening.md for production
7. Run tests with `./scripts/test-jwt-setup.sh`
8. Monitor with troubleshooting.md as needed

## Key Benefits

1. **Comprehensive Coverage**: From basic JWT to advanced microservices patterns
2. **Production Ready**: Includes security hardening and performance optimization
3. **Well Documented**: Each aspect has detailed reference documentation
4. **Practical Examples**: Real-world code implementations
5. **Testing Included**: Automated test suite and testing strategies
6. **Troubleshooting Guide**: Common issues and solutions

## Maintenance

This skill should be updated when:
- New Spring Security features are released
- New security vulnerabilities are discovered
- Performance optimizations are identified
- Community feedback suggests improvements
- Integration patterns evolve