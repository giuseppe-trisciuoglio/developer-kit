# OWASP Top 10 for TypeScript/Node.js

## A01: Broken Access Control

### Risk
Users acting outside their intended permissions. The most common web application vulnerability.

### TypeScript/Node.js Patterns

```typescript
// ❌ Vulnerable: No authorization check
app.get('/api/users/:id/profile', async (req, res) => {
  const profile = await db.user.findUnique({ where: { id: req.params.id } });
  res.json(profile); // Any user can access any profile
});

// ✅ Secure: Proper authorization
app.get('/api/users/:id/profile', authenticate, async (req, res) => {
  if (req.user.id !== req.params.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const profile = await db.user.findUnique({ where: { id: req.params.id } });
  res.json(profile);
});
```

### Review Checklist
- [ ] All endpoints enforce authentication
- [ ] Authorization checks verify resource ownership
- [ ] Admin endpoints restricted by role
- [ ] Direct object references validated against user permissions
- [ ] CORS restrictive (not `origin: '*'`)
- [ ] JWT tokens validated on every request

## A02: Cryptographic Failures

### Risk
Exposure of sensitive data due to weak or missing encryption.

### TypeScript/Node.js Patterns

```typescript
// ❌ Vulnerable: MD5 for passwords, no salt
import { createHash } from 'crypto';
const hash = createHash('md5').update(password).digest('hex');

// ✅ Secure: bcrypt with proper cost factor
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);
const isValid = await bcrypt.compare(input, hash);
```

### Review Checklist
- [ ] Passwords hashed with bcrypt or argon2 (cost factor ≥ 10)
- [ ] Sensitive data encrypted at rest (AES-256)
- [ ] TLS/HTTPS enforced for all communications
- [ ] No sensitive data in JWT payloads
- [ ] Strong random values from `crypto.randomBytes`
- [ ] API keys not in source code or client bundles

## A03: Injection

### Risk
Untrusted data sent to an interpreter as part of a command or query.

### TypeScript/Node.js Patterns

```typescript
// ❌ SQL Injection
const result = await db.query(`SELECT * FROM users WHERE name = '${name}'`);

// ✅ Parameterized query
const result = await db.query('SELECT * FROM users WHERE name = $1', [name]);

// ❌ Command Injection
const { exec } = require('child_process');
exec(`ls ${userInput}`); // Shell injection

// ✅ Safe subprocess
const { execFile } = require('child_process');
execFile('ls', [userInput]); // No shell interpretation
```

### Review Checklist
- [ ] All SQL queries use parameterized statements or ORM
- [ ] No `eval()`, `new Function()`, or `vm.runInNewContext()` with user input
- [ ] `child_process.exec` not used with user input (use `execFile` or `spawn`)
- [ ] Template literals not used for SQL, shell commands, or LDAP queries
- [ ] NoSQL queries don't accept operator objects from user input

## A04: Insecure Design

### Review Checklist
- [ ] Business logic has rate limiting for abuse-prone operations
- [ ] Multi-step operations validate state at each step
- [ ] Error messages don't reveal system internals
- [ ] Sensitive operations require re-authentication

## A05: Security Misconfiguration

### TypeScript/Node.js Patterns

```typescript
// ❌ Misconfigured: Debug enabled, permissive CORS
app.use(cors());
app.use(errorHandler({ showStack: true }));

// ✅ Secure configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  credentials: true,
}));
app.use(helmet());
if (process.env.NODE_ENV === 'production') {
  app.set('trust proxy', 1);
}
```

### Review Checklist
- [ ] Debug mode disabled in production
- [ ] Security headers configured (helmet.js)
- [ ] Error responses don't include stack traces in production
- [ ] Default accounts/passwords removed
- [ ] Unnecessary features disabled
- [ ] `NODE_ENV=production` set in production

## A06: Vulnerable and Outdated Components

### Review Checklist
- [ ] `npm audit` reports no critical/high vulnerabilities
- [ ] Dependencies regularly updated
- [ ] Lock file (`package-lock.json`) committed
- [ ] No unnecessary dependencies
- [ ] Dependabot or Renovate configured

## A07: Identification and Authentication Failures

### TypeScript/Node.js Patterns

```typescript
// ❌ Weak session management
app.use(session({
  secret: 'secret',
  cookie: {},
}));

// ✅ Secure session configuration
app.use(session({
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000, // 15 minutes
  },
}));
```

### Review Checklist
- [ ] Passwords require minimum 12 characters with complexity
- [ ] Account lockout after failed attempts
- [ ] Session tokens rotated after login
- [ ] JWT expiration set (short-lived: 15 min)
- [ ] Refresh tokens stored securely (HttpOnly cookie)
- [ ] Multi-factor authentication for sensitive operations

## A08: Software and Data Integrity Failures

### Review Checklist
- [ ] CI/CD pipeline integrity verified
- [ ] Dependencies verified against known good hashes
- [ ] Subresource integrity (SRI) for external scripts
- [ ] Serialization/deserialization validated (no `JSON.parse` of untrusted data without schema validation)

## A09: Security Logging and Monitoring Failures

### TypeScript/Node.js Patterns

```typescript
// ✅ Security event logging
logger.warn('Authentication failed', {
  ip: req.ip,
  email: req.body.email, // Log identifier, NOT password
  userAgent: req.headers['user-agent'],
  timestamp: new Date().toISOString(),
});
```

### Review Checklist
- [ ] Failed login attempts logged with IP and user agent
- [ ] Authorization failures logged
- [ ] Sensitive data NOT included in logs (passwords, tokens, PII)
- [ ] Log injection prevented (sanitize user input in logs)
- [ ] Monitoring alerts for anomalous patterns

## A10: Server-Side Request Forgery (SSRF)

### TypeScript/Node.js Patterns

```typescript
// ❌ SSRF vulnerable
app.get('/fetch', async (req, res) => {
  const response = await fetch(req.query.url as string); // User controls URL
  res.json(await response.json());
});

// ✅ SSRF prevention
const ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com'];

app.get('/fetch', async (req, res) => {
  const url = new URL(req.query.url as string);
  if (!ALLOWED_DOMAINS.includes(url.hostname)) {
    return res.status(400).json({ error: 'Domain not allowed' });
  }
  if (url.protocol !== 'https:') {
    return res.status(400).json({ error: 'HTTPS required' });
  }
  const response = await fetch(url.toString());
  res.json(await response.json());
});
```

### Review Checklist
- [ ] Server-side HTTP requests don't use user-controlled URLs
- [ ] URL allowlists for external requests
- [ ] Internal network addresses blocked (127.0.0.1, 10.x, 172.16.x, 192.168.x)
- [ ] DNS rebinding prevention
