# Security Patterns Reference

CWE/OWASP compliance patterns for Constitution Check operations.

---

## Forbidden Patterns (CRITICAL — Blocks Merge)

| Pattern | CWE-ID | OWASP | Reason | Detection |
|---------|--------|-------|--------|-----------|
| Raw SQL string concatenation | CWE-89 | A03:2021 | SQL Injection | Grep for `'+` in SQL contexts |
| Hardcoded secrets/credentials | CWE-798 | A02:2021 | Credential Exposure | Grep for `password=`, `secret=`, `api_key=` |
| Deserialization of untrusted data | CWE-502 | A08:2021 | Software/Data Integrity | Look for `ObjectInputStream`, unvalidated `JSON.parse` |
| Unvalidated redirects | CWE-601 | A01:2021 | Broken Access Control | Check for `redirect(` without validation |
| Missing authentication on sensitive endpoints | CWE-306 | A01:2021 | Broken Access Control | Scan for public endpoints without auth |
| Insufficient password hashing | CWE-916 | A02:2021 | Cryptographic Failures | Check for plain text or MD5/SHA1 storage |
| Use of deprecated crypto (MD5, SHA1) | CWE-327 | A02:2021 | Cryptographic Failures | Grep for MD5/SHA1 in crypto contexts |
| XML External Entity (XXE) | CWE-611 | A05:2021 | Security Misconfiguration | Check for XML parsers without entity restrictions |
| Path traversal (unsafe file access) | CWE-22 | A01:2021 | Broken Access Control | Check for unsanitized file path inputs |

## Required Patterns (CRITICAL — Must Implement)

| Pattern | CWE-ID | OWASP | Why Required |
|---------|--------|-------|--------------|
| All SQL queries use parameterized statements | CWE-20 | A03:2021 | Prevents SQL injection |
| All secrets via environment variables or Secrets Manager | CWE-522 | A02:2021 | Prevents credential exposure |
| Password hashing with bcrypt cost factor >= 12 | CWE-916 | A02:2021 | Brute force protection |
| JWT tokens include expiration and signature verification | CWE-345 | A01:2021 | Session integrity |
| CSRF tokens on state-changing operations | CWE-352 | A01:2021 | CSRF prevention |
| Secure session cookies (HttpOnly, Secure, SameSite) | CWE-1004 | A01:2021 | Session hijacking prevention |
| Input validation on all public endpoints | CWE-20 | A03:2021 | Prevents injection attacks |
| Output encoding for XSS prevention | CWE-79 | A03:2021 | XSS prevention |

## Recommended Patterns (SHOULD — Strongly Advised)

| Pattern | CWE-ID | Why Recommended |
|---------|--------|-----------------|
| Input sanitization beyond validation | CWE-138 | Defense in depth |
| Rate limiting on authentication endpoints | CWE-307 | Brute force protection |
| Security event logging | CWE-778 | Audit trail and incident response |
| Timeout for external API calls | CWE-835 | Resource exhaustion prevention |
| Content Security Policy headers | CWE-1021 | XSS prevention |
| File upload validation (type, size, content) | CWE-434 | Malicious file upload prevention |
| SQL query timeout to prevent DoS | CWE-400 | Database resource exhaustion |

## Library Verification Format

```markdown
#### [Library Name]

**Package**: [npm/maven/pypi package name]
**Version**: [Exact version, e.g., 2.14.1]

**Approved APIs**:
| API | Signature | Purpose |
|-----|-----------|---------|
| `methodName` | `(param1: Type, param2: Type): ReturnType` | Brief description |

**Usage Constraints**:
- [Constraint 1]
- [Constraint 2]

**Forbidden APIs**:
| API | Reason |
|-----|--------|
| `deprecatedMethod` | Use `newMethod` instead |

**Verification Examples**:

```typescript
// ✅ CORRECT: Will pass verification
import { correctMethod } from 'library';
const result = await correctMethod(options);

// ❌ INCORRECT: Will be flagged
import { wrongMethod } from 'library'; // This method doesn't exist
```

## Enforcement Levels

| Level | Meaning | What Happens |
|-------|---------|---------------|
| **CRITICAL** | Must pass before merge | Blocks merge, requires immediate fix |
| **SHOULD** | Should pass, minor deviation acceptable | Warning logged, needs justification |
| **MAY** | Informational, best practice | Suggestion only |

## Detection Patterns by Language

### Java/TypeScript
```bash
# SQL Injection detection
grep -rn "SELECT.*\+.*FROM\|INSERT.*\+.*VALUES" src/

# Hardcoded secrets
grep -rn "password\s*=\|secret\s*=\|api_key\s*=" src/

# Missing auth on endpoints
grep -rn "@GetMapping\|@PostMapping\|router\.get\|router\.post" src/
```

### Python
```bash
# SQL Injection detection
grep -rn "cursor\.execute.*%" .

# Hardcoded secrets
grep -rn "password\s*=\|secret\s*=\|os\.environ" .
```

## OWASP Top 10 (2021) Mapping

| OWASP Category | Relevant CWEs | Key Controls |
|---------------|---------------|--------------|
| A01 Broken Access Control | CWE-306, CWE-601, CWE-22 | AuthZ checks, input validation |
| A02 Cryptographic Failures | CWE-327, CWE-916, CWE-798 | Proper crypto, secrets management |
| A03 Injection | CWE-89, CWE-79, CWE-20 | Parameterized queries, output encoding |
| A04 Insecure Design | CWE-502 | Threat modeling, secure defaults |
| A05 Security Misconfiguration | CWE-611, CWE-16 | Hardened configs, minimal setup |
| A06 Vulnerable Components | CWE-1104 | Dependency scanning, versioning |
| A07 Auth Failures | CWE-307, CWE-345 | Rate limiting, secure sessions |
| A08 Software Integrity | CWE-494, CWE-829 | Signed updates, integrity checks |
| A09 Security Logging | CWE-778 | Comprehensive audit logging |
| A10 SSRF | CWE-918 | URL validation, allowlist for fetch |