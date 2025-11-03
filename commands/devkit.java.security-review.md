---
allowed-tools: Read, Grep, Glob, Bash, Task
argument-hint: [scope] [options]
description: Comprehensive security review for Java enterprise applications (Spring, Jakarta EE, etc.)
---

Execute comprehensive security review for Java enterprise applications. Analyze vulnerabilities, dependencies, security configurations, and best practices specific to the Java ecosystem.

## Security Analysis for Java Enterprise Applications

### Main Analysis Areas

**Security Review Scope**: $ARGUMENTS

### 1. OWASP Top 10 Vulnerability Analysis for Java

Analyze the following vulnerability categories in Java context:

#### A01: Broken Access Control
- Verify Spring Security configurations (@PreAuthorize, @Secured)
- Analyze method-level and URL access controls
- Check JWT and OAuth2 implementations
- Verify Role-Based Access Control (RBAC)

#### A02: Cryptographic Failures
- Analyze cryptographic algorithms usage (JCA, Bouncy Castle)
- Verify password management (BCrypt, PBKDF2)
- Check SSL/TLS configurations
- Review key and secrets management

#### A03: Injection
- SQL Injection in JPA/Hibernate (JPQL, Criteria API)
- NoSQL Injection (MongoDB, Cassandra)
- Command Injection (ProcessBuilder, Runtime.exec)
- LDAP Injection in JNDI

#### A04: Insecure Design
- Missing layered security architecture
- Insecure design patterns (Singleton, Prototype)
- Lack of Domain-Driven Design for security
- Unclear separation of responsibilities

#### A05: Security Misconfiguration
- Insecure Spring Boot configurations
- Exposed Actuator endpoints
- Unprotected database connection pools
- Missing CORS and security headers

#### A06: Vulnerable and Outdated Components
- Maven/Gradle dependency scanning (OWASP Dependency-Check)
- Libraries with known CVEs
- Outdated Spring/Jakarta EE versions
- Vulnerable transitive dependencies

#### A07: Identification and Authentication Failures
- Inadequate Spring Security configurations
- Insecure session management
- Weak password policies
- Incorrectly implemented MFA

#### A08: Software and Data Integrity Failures
- Verify JAR/WAR signatures integrity
- Missing data integrity controls
- Unimplemented anti-tampering
- Secure deserialization (Java serialization)

#### A09: Security Logging and Monitoring Failures
- Inadequate security logging (Logback, Log4j)
- Missing audit trail
- Absent security event monitoring
- Unimplemented intrusion detection

#### A10: Server-Side Request Forgery (SSRF)
- Analyze HTTP/HTTPS calls (RestTemplate, WebClient)
- Missing URL validation
- Insecure proxy configurations
- File inclusion attacks

### 2. Spring Security Analysis

#### Configuration Analysis
- @EnableWebSecurity configurations
- PasswordEncoder implementations
- Authentication providers setup
- HTTP security rules (authorizeRequests())

#### Authentication & Authorization
- JWT implementation security
- OAuth2/OpenID Connect setup
- Method-level security (@PreAuthorize, @Secured)
- Role-based access control patterns

#### Session Management
- Session fixation protection
- Concurrent session control
- Session timeout configuration
- State vs Stateless authentication

### 3. Dependencies and Libraries Analysis

#### Maven/Gradle Dependency Analysis
```bash
# Run vulnerability scan
mvn dependency:tree
mvn org.owasp:dependency-check-maven:check
```

#### Critical Libraries to Review
- Spring Framework versions
- Jakarta EE implementations
- Database drivers (JDBC)
- JSON libraries (Jackson, Gson)
- Crypto libraries (Bouncy Castle)
- HTTP clients (Apache HttpClient, OkHttp)

### 4. Database Security

#### JPA/Hibernate Security
- SQL injection in JPQL queries
- N+1 query problems
- Lazy loading security issues
- Entity access control

#### Connection Security
- Connection pool configuration
- Database credential management
- SSL/TLS database connections
- Stored procedure security

### 5. API Security

#### REST API Security
- Input validation (Jakarta Bean Validation)
- Rate limiting implementation
- API authentication patterns
- Response security headers

#### Microservices Security
- Service-to-service authentication
- API gateway security patterns
- Circuit breaker security
- Distributed tracing security

### 6. Containerization and Cloud Security

#### Docker/Kubernetes Security
- Container base image security
- Secrets management (K8s secrets)
- Network policies
- Pod security policies

#### Cloud Platform Security
- AWS/Azure/GCP security configurations
- IAM roles and policies
- VPC/network security
- Cloud security groups

### 7. Security Testing

#### Unit Testing for Security
```java
// Access control test
@Test
@WithMockUser(roles = "ADMIN")
void adminEndpoint_shouldReturn200_forAdminUser() {
    // test implementation
}
```

#### Integration Security Testing
- Spring Security test annotations
- Penetration testing setup
- Security smoke tests
- OWASP ZAP integration

### 8. Code Quality Security Patterns

#### Secure Coding Practices
- Input validation and sanitization
- Error handling without information disclosure
- Secure defaults implementation
- Defense in depth patterns

#### Static Analysis Integration
- SonarQube security rules
- SpotBugs security plugins
- PMD security rulesets
- Checkstyle security checks

### 9. Configuration Security

#### Application Properties Security
```yaml
spring:
  security:
    user:
      name: ${SECURITY_USER_NAME}
      password: ${SECURITY_USER_PASSWORD}
  datasource:
    url: jdbc:mysql://${DB_HOST}/${DB_NAME}?useSSL=true
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
```

#### Environment-Specific Security
- Profile-specific security configurations
- Secrets management strategies
- Configuration encryption
- Environment variable validation

### 10. Reporting and Recommendations

#### Critical Security Issues (P0)
- Remote code execution vulnerabilities
- Authentication bypass vulnerabilities
- Data exposure incidents
- Injection vulnerabilities

#### High Priority Security Issues (P1)
- Outdated dependencies with CVEs
- Insecure configurations
- Missing security headers
- Weak authentication mechanisms

#### Medium Priority Security Issues (P2)
- Logging/monitoring gaps
- Insufficient input validation
- Access control improvements
- Code quality security improvements

#### Low Priority Security Issues (P3)
- Security documentation updates
- Code style security improvements
- Additional security testing
- Security training recommendations

### 11. Tools and Automation

#### Static Analysis Tools
- SonarQube/SonarCloud
- SpotBugs with security plugins
- OWASP Dependency Check
- Checkstyle with security rules

#### Dynamic Testing Tools
- OWASP ZAP
- Burp Suite
- Postman security testing
- JMeter security tests

#### CI/CD Security Integration
```yaml
# GitHub Actions security scan example
- name: OWASP Dependency Check
  uses: dependency-check/Dependency-Check_Action@main
- name: SonarCloud Scan
  uses: SonarSource/sonarcloud-github-action@master
```

## Execution Steps

1. **Setup Analysis Environment**
   - Prepare codebase for review
   - Configure security scanning tools
   - Set up reporting framework

2. **Automated Security Scanning**
   - Run dependency vulnerability scans
   - Execute static analysis security rules
   - Perform configuration security checks

3. **Manual Security Review**
   - Review authentication/authorization logic
   - Analyze input validation patterns
   - Check error handling security

4. **Generate Security Report**
   - Consolidate findings from all tools
   - Prioritize vulnerabilities by risk
   - Provide actionable remediation steps

5. **Security Recommendations**
   - Framework-specific security improvements
   - Code pattern recommendations
   - Configuration security enhancements
   - Monitoring and alerting setup

Target: $ARGUMENTS