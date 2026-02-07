---
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[scope] [options]"
description: Comprehensive security review for TypeScript/Node.js applications (Next.js, NestJS, Express, etc.)
---

Execute comprehensive security review for TypeScript/Node.js applications. Analyze vulnerabilities, dependencies, security configurations, and best practices specific to the TypeScript ecosystem.

## Security Analysis for TypeScript/Node.js Applications

### Main Analysis Areas

**Security Review Scope**: $ARGUMENTS

### 1. OWASP Top 10 Vulnerability Analysis for TypeScript

Analyze the following vulnerability categories in TypeScript context:

#### A01: Broken Access Control
- Verify authentication middleware implementations (Express.js, NestJS guards)
- Analyze JWT token validation and refresh mechanisms
- Check role-based access control (RBAC) patterns
- Verify API route protection in Next.js API routes
- Review GraphQL resolvers authorization

#### A02: Cryptographic Failures
- Analyze crypto library usage (Node.js crypto, bcryptjs)
- Verify password hashing implementations
- Check SSL/TLS configurations for Node.js servers
- Review secrets management (dotenv, config libraries)
- Validate encryption/decryption patterns

#### A03: Injection
- SQL Injection in TypeORM/Prisma/Sequelize
- NoSQL Injection in MongoDB/Mongoose
- Command Injection in child_process.exec/execSync
- Template Injection in Handlebars/EJS/JSX
- XSS in React/Vue/Angular components

#### A04: Insecure Design
- Missing security middleware (Helmet, CORS)
- Insecure architectural patterns in microservices
- Lack of input validation strategy
- Insecure API design patterns
- Missing rate limiting configurations

#### A05: Security Misconfiguration
- Insecure Express.js/NestJS configurations
- Exposed development endpoints
- CORS misconfigurations
- Insecure default settings in production
- Missing security headers

#### A06: Vulnerable and Outdated Components
- npm/yarn dependency scanning (npm audit, yarn audit)
- Libraries with known CVEs
- Outdated Node.js/TypeScript versions
- Vulnerable transitive dependencies
- Malicious package detection

#### A07: Identification and Authentication Failures
- Weak password policies in authentication systems
- Insecure session management
- Improper JWT implementation
- Missing MFA implementation
- Insecure OAuth flows

#### A08: Software and Data Integrity Failures
- Missing package integrity verification (npm package-lock.json)
- Insecure CI/CD pipeline configurations
- Lack of code signing for critical operations
- Deserialization vulnerabilities (JSON.parse)
- Missing checksum validation

#### A09: Security Logging and Monitoring Failures
- Inadequate security logging (Winston, Pino)
- Missing audit trail implementation
- Absent security event monitoring
- Insufficient error handling that leaks information
- Missing intrusion detection

#### A10: Server-Side Request Forgery (SSRF)
- Analyze HTTP calls (axios, node-fetch)
- Missing URL validation in API requests
- Insecure proxy configurations
- File inclusion attacks via require/import
- Open redirect vulnerabilities

### 2. Framework-Specific Security Analysis

#### Next.js Security Analysis
- API route security configurations
- Server-side rendering (SSR) security
- Static site generation (SSG) security
- Middleware security implementations
- NextAuth.js configuration review

#### NestJS Security Analysis
- Guard implementations (AuthGuard, RolesGuard)
- Passport strategy configurations
- Interceptor security patterns
- Exception filter security
- Module dependency security

#### Express.js Security Analysis
- Middleware security configurations
- Route protection patterns
- Error handling security
- Session management
- Helmet/CORS implementations

### 3. Dependencies and Libraries Analysis

#### npm/yarn Dependency Analysis
```bash
# Run vulnerability scan
npm audit
npm audit fix
yarn audit
yarn audit --json
```

#### Critical Libraries to Review
- Express.js/NestJS versions
- React/Vue/Angular frameworks
- Database libraries (TypeORM, Prisma, Mongoose)
- Authentication libraries (Passport.js, NextAuth)
- HTTP clients (axios, node-fetch)
- Utility libraries (lodash, moment.js)

#### Package.json Security Review
- Analyze dependency versions
- Check for malicious packages
- Review package scripts security
- Validate package integrity
- Check for dependency confusion

### 4. Database Security

#### TypeORM/Prisma Security
- SQL injection prevention
- Query builder security
- Database connection security
- Migration security
- Entity access control

#### MongoDB/Mongoose Security
- NoSQL injection prevention
- Schema validation security
- Connection security
- Index security considerations

#### Database Connection Security
- Connection pool configuration
- Database credential management
- SSL/TLS database connections
- Environment variable security

### 5. API Security

#### REST API Security
- Input validation (Joi, Zod, class-validator)
- Rate limiting implementation (express-rate-limit)
- API authentication patterns
- Response security headers
- OpenAPI/Swagger security definitions

#### GraphQL Security
- Query depth limiting
- Query complexity analysis
- Resolver authorization
- Introspection security
- Subscription security

#### WebSocket Security
- Socket.IO authentication
- Message validation
- Rate limiting for connections
- CORS for WebSocket connections

### 6. Frontend Security

#### React/Vue/Angular Security
- XSS prevention in components
- CSRF token handling
- Content Security Policy (CSP)
- Secure routing configurations
- State management security

#### SPA Security Considerations
- Token storage strategies
- Authentication flow security
- API communication security
- Browser storage security
- Third-party library security

### 7. Containerization and Cloud Security

#### Docker Security
- Container base image security
- Multi-stage build security
- Secrets management in containers
- Dockerfile security best practices

#### Cloud Platform Security
- Vercel/Netlify security configurations
- AWS Lambda/Cloud security
- Azure Functions security
- Google Cloud Functions security

### 8. Security Testing

#### Unit Testing for Security
```typescript
// Authentication middleware test
describe('AuthMiddleware', () => {
  it('should reject requests without valid token', () => {
    const mockRequest = { headers: {} };
    const mockResponse = { status: jest.fn(), json: jest.fn() };
    const mockNext = jest.fn();

    authMiddleware(mockRequest, mockResponse, mockNext);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
  });
});
```

#### Integration Security Testing
- Jest security testing patterns
- Supertest for API security testing
- Cypress end-to-end security tests
- OWASP ZAP integration

#### Static Analysis for TypeScript
- ESLint security rules
- TypeScript compiler security checks
- SonarJS security analysis
- CodeQL for TypeScript

### 9. Configuration Security

#### Environment Variables Security
```typescript
// Secure configuration loading
import { config } from 'dotenv';
import Joi from 'joi';

const configSchema = Joi.object({
  PORT: Joi.number().default(3000),
  DB_HOST: Joi.string().required(),
  JWT_SECRET: Joi.string().min(32).required(),
}).unknown();

const { error, value } = configSchema.validate(process.env);
if (error) throw new Error('Config validation error');
```

#### TypeScript Configuration Security
- Strict TypeScript compiler options
- ESLint security configuration
- Prettier security considerations
- Webpack/Vite security settings

### 10. Code Quality Security Patterns

#### Secure Coding Practices
- Input validation and sanitization
- Type safety for security
- Error handling without information disclosure
- Secure async/await patterns
- Memory leak prevention

#### Dependency Injection Security
- Secure service instantiation
- Configuration injection patterns
- Scoped dependencies security
- Module dependency validation

### 11. Performance-Related Security

#### DoS Prevention
- Request timeout configurations
- Memory usage monitoring
- CPU usage limits
- Connection pool limiting
- Rate limiting per user/IP

#### Resource Security
- File upload security
- Memory allocation limits
- Process management security
- Event loop security considerations

### 12. Monitoring and Logging Security

#### Security Monitoring
```typescript
// Security event logging
import { Logger } from 'pino';

const logger = new Logger({
  level: 'info',
  redact: ['req.headers.authorization', 'req.body.password']
});

// Log security events
logger.info({
  event: 'login_attempt',
  userId: user.id,
  ip: req.ip,
  timestamp: new Date().toISOString()
});
```

#### Audit Trail Implementation
- User action logging
- Data access logging
- API call auditing
- Failed authentication attempts

### 13. Reporting and Recommendations

#### Critical Security Issues (P0)
- Remote code execution vulnerabilities
- Authentication bypass vulnerabilities
- Data exposure incidents
- Injection vulnerabilities
- SSRF vulnerabilities

#### High Priority Security Issues (P1)
- Outdated dependencies with CVEs
- Insecure configurations
- Missing security headers
- Weak authentication mechanisms
- XSS vulnerabilities

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

### 14. Tools and Automation

#### Static Analysis Tools
- ESLint with security plugins
- SonarJS security analysis
- CodeQL for TypeScript
- Semgrep for TypeScript

#### Dynamic Testing Tools
- OWASP ZAP
- Burp Suite
- Postman security testing
- OWASP Nettacker

#### Dependency Scanning Tools
- npm audit
- Snyk
- GitHub Dependabot
- OWASP Dependency Check

#### CI/CD Security Integration
```yaml
# GitHub Actions security scan example
- name: Run npm audit
  run: npm audit --audit-level high
- name: Run Snyk security scan
  uses: snyk/actions/node@master
- name: Run ESLint security rules
  run: npx eslint . --ext .ts,.tsx --config .eslintrc.security.js
```

## Execution Steps

1. **Setup Analysis Environment**
   - Prepare codebase for review
   - Configure security scanning tools
   - Set up reporting framework

2. **Automated Security Scanning**
   - Run npm audit for vulnerabilities
   - Execute ESLint security rules
   - Perform static analysis with Semgrep
   - Scan dependencies with Snyk

3. **Manual Security Review**
   - Review authentication/authorization logic
   - Analyze input validation patterns
   - Check API endpoint security
   - Review database security configurations

4. **Framework-Specific Analysis**
   - Review Next.js security configurations
   - Analyze NestJS guard implementations
   - Check Express.js middleware security
   - Review frontend security patterns

5. **Generate Security Report**
   - Consolidate findings from all tools
   - Prioritize vulnerabilities by risk
   - Provide actionable remediation steps
   - Create implementation timeline

6. **Security Recommendations**
   - Framework-specific security improvements
   - TypeScript security best practices
   - Configuration security enhancements
   - Monitoring and alerting setup

Target: $ARGUMENTS

## Execution Instructions

**Agent Selection**: To execute this TypeScript security review, use the following agent with fallback:
- Primary: `ts-security-expert`
- If not available: Use `developer-kit:ts-security-expert` or fallback to `general-purpose` agent with security expertise
