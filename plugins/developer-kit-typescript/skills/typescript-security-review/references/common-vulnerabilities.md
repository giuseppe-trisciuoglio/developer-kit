# Common TypeScript/Node.js Vulnerability Patterns

## Injection Vulnerabilities

### SQL Injection via Template Literals

```typescript
// ❌ Vulnerable
async function searchUsers(name: string) {
  return db.query(`SELECT * FROM users WHERE name LIKE '%${name}%'`);
}

// ✅ Fix: Parameterized query
async function searchUsers(name: string) {
  return db.query('SELECT * FROM users WHERE name LIKE $1', [`%${name}%`]);
}
```

### NoSQL Injection (MongoDB)

```typescript
// ❌ Vulnerable: User input as query operator
app.post('/login', async (req, res) => {
  const user = await User.findOne({
    email: req.body.email,
    password: req.body.password, // Could be { $ne: '' }
  });
});

// ✅ Fix: Validate and cast input types
app.post('/login', async (req, res) => {
  const { email, password } = loginSchema.parse(req.body); // Zod ensures strings
  const user = await User.findOne({ email });
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

### Command Injection

```typescript
// ❌ Vulnerable: Shell command with user input
import { exec } from 'child_process';
exec(`convert ${filename} output.png`);

// ✅ Fix: Use execFile (no shell interpretation)
import { execFile } from 'child_process';
execFile('convert', [filename, 'output.png']);
```

### Regex Denial of Service (ReDoS)

```typescript
// ❌ Vulnerable: Catastrophic backtracking
const emailRegex = /^([a-zA-Z0-9]+)*@([a-zA-Z0-9]+)*\.([a-zA-Z]+)$/;

// ✅ Fix: Use non-backtracking patterns or Zod
import { z } from 'zod';
const emailSchema = z.string().email();
```

## Cross-Site Scripting (XSS)

### React dangerouslySetInnerHTML

```tsx
// ❌ Vulnerable
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ Fix: Sanitize with DOMPurify
import DOMPurify from 'isomorphic-dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

### Server-Side Template Injection

```typescript
// ❌ Vulnerable: String interpolation in HTML response
app.get('/greeting', (req, res) => {
  res.send(`<h1>Hello ${req.query.name}</h1>`);
});

// ✅ Fix: Escape HTML entities
import { escape } from 'html-escaper';
app.get('/greeting', (req, res) => {
  res.send(`<h1>Hello ${escape(req.query.name as string)}</h1>`);
});
```

## Authentication Vulnerabilities

### Timing Attack on Comparison

```typescript
// ❌ Vulnerable: Early return leaks timing information
function verifyApiKey(provided: string, stored: string): boolean {
  return provided === stored; // Timing attack possible
}

// ✅ Fix: Constant-time comparison
import { timingSafeEqual } from 'crypto';
function verifyApiKey(provided: string, stored: string): boolean {
  const a = Buffer.from(provided);
  const b = Buffer.from(stored);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
```

### JWT Algorithm Confusion

```typescript
// ❌ Vulnerable: Accepts any algorithm
jwt.verify(token, publicKey); // Attacker can use 'none' or switch HS/RS

// ✅ Fix: Restrict algorithms
jwt.verify(token, publicKey, {
  algorithms: ['RS256'], // Only accept expected algorithm
});
```

### Insecure Password Reset

```typescript
// ❌ Vulnerable: Predictable token
const resetToken = Math.random().toString(36);

// ✅ Fix: Cryptographically secure token with expiration
import { randomBytes } from 'crypto';
const resetToken = randomBytes(32).toString('hex');
const tokenHash = createHash('sha256').update(resetToken).digest('hex');
const expires = new Date(Date.now() + 3600_000); // 1 hour
```

## Path Traversal

```typescript
// ❌ Vulnerable: User controls file path
app.get('/files', (req, res) => {
  const filePath = path.join('/uploads', req.query.name as string);
  res.sendFile(filePath);
});
// Attack: ?name=../../etc/passwd

// ✅ Fix: Validate path stays within allowed directory
import path from 'path';

app.get('/files', (req, res) => {
  const basePath = path.resolve('/uploads');
  const filePath = path.resolve(basePath, req.query.name as string);

  if (!filePath.startsWith(basePath)) {
    return res.status(400).json({ error: 'Invalid file path' });
  }
  res.sendFile(filePath);
});
```

## Prototype Pollution

```typescript
// ❌ Vulnerable: Deep merge with user input
function deepMerge(target: any, source: any) {
  for (const key in source) {
    if (typeof source[key] === 'object') {
      target[key] = deepMerge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
// Attack: { "__proto__": { "isAdmin": true } }

// ✅ Fix: Block prototype keys
function safeMerge(target: Record<string, unknown>, source: Record<string, unknown>) {
  for (const key of Object.keys(source)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    if (typeof source[key] === 'object' && source[key] !== null) {
      target[key] = safeMerge(
        (target[key] as Record<string, unknown>) || {},
        source[key] as Record<string, unknown>,
      );
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

## Information Disclosure

### Error Messages

```typescript
// ❌ Vulnerable: Exposes internals
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack, // Full stack trace
    query: req.query, // Request details
  });
});

// ✅ Fix: Generic error response
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id,
  });
});
```

### Enumeration via Timing or Response

```typescript
// ❌ Vulnerable: Different responses for existing vs non-existing users
app.post('/login', async (req, res) => {
  const user = await findUser(req.body.email);
  if (!user) return res.status(404).json({ error: 'User not found' });
  if (!await bcrypt.compare(req.body.password, user.hash)) {
    return res.status(401).json({ error: 'Wrong password' });
  }
});

// ✅ Fix: Same response for all failures
app.post('/login', async (req, res) => {
  const user = await findUser(req.body.email);
  const isValid = user && await bcrypt.compare(req.body.password, user.hash);
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

## Denial of Service

### Event Loop Blocking

```typescript
// ❌ Vulnerable: Blocking the event loop
app.get('/hash', (req, res) => {
  const hash = crypto.pbkdf2Sync(req.query.data, 'salt', 100000, 64, 'sha512');
  res.json({ hash: hash.toString('hex') });
});

// ✅ Fix: Async operation
app.get('/hash', async (req, res) => {
  const hash = await new Promise((resolve, reject) => {
    crypto.pbkdf2(req.query.data, 'salt', 100000, 64, 'sha512', (err, key) => {
      if (err) reject(err);
      else resolve(key.toString('hex'));
    });
  });
  res.json({ hash });
});
```

### Unbounded Input

```typescript
// ❌ Vulnerable: No limit on request body size
app.use(express.json());

// ✅ Fix: Limit body size
app.use(express.json({ limit: '10kb' }));
```
