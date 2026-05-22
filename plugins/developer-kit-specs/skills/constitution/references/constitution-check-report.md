# Constitution Check Report Examples

Complete report examples for different scenarios.

---

## Example 1: Clean Check (No Violations)

```markdown
## Constitution Check Report
Target: src/services/UserService.java
Date: 2024-01-15

### Security Check (CWE/OWASP Compliance)
| Rule | Level | Status | Location | CWE/OWASP |
|------|-------|--------|----------|-----------|
| No SQL injection | CRITICAL | ✅ OK | - | CWE-89 |
| No hardcoded secrets | CRITICAL | ✅ OK | - | CWE-798 |
| CSRF protection | CRITICAL | ✅ OK | - | CWE-352 |
| Password hashing | CRITICAL | ✅ OK | - | CWE-916 |
| Secure session cookies | CRITICAL | ✅ OK | - | CWE-1004 |
| Rate limiting | SHOULD | ✅ OK | - | CWE-307 |
| Security logging | SHOULD | ✅ OK | - | CWE-778 |

**CRITICAL Violations (MUST fix)**: 0
**SHOULD Warnings**: 0
**Compliant**: 6

### CWE Compliance Report
| CWE | OWASP | Status | Location | Last Verified |
|-----|-------|--------|----------|---------------|
| CWE-89 | A03 | ✅ OK | UserRepository.java:45 | 2024-01-15 |
| CWE-798 | A02 | ✅ OK | - | 2024-01-15 |
| CWE-352 | A01 | ✅ OK | - | 2024-01-15 |
| CWE-916 | A02 | ✅ OK | AuthService.java:23 | 2024-01-15 |
| CWE-307 | A07 | ✅ OK | - | 2024-01-15 |
| CWE-778 | A09 | ✅ OK | - | 2024-01-15 |

### Architecture Check
| Rule | Status | Detail |
|------|--------|--------|
| Constructor injection required | ✅ OK | All dependencies via constructor |
| Layered architecture followed | ✅ OK | Service → Repository → DB |
| No hardcoded secrets | ✅ OK | All config via @Value or env |

### Library Verification Check
| Library | Status | Detail |
|---------|--------|--------|
| bcrypt | ✅ OK | Using hash(password, 12) |
| Spring JPA | ✅ OK | Parameterized queries via JPQL |
| Lombok | ✅ OK | @Slf4j, @Getter, @Setter only |

### Ontology Check
| Term | Status | Detail |
|------|--------|--------|
| "User" used consistently | ✅ OK | No synonym "Account" found |
| "Order" domain model used | ✅ OK | No technical terms mixed |

### Summary
- CRITICAL violations: 0
- WARNING violations: 0
- Compliant rules: 15
- Library verification: All verified ✅
```

---

## Example 2: Multiple Violations

```markdown
## Constitution Check Report
Target: src/controllers/AuthController.ts
Date: 2024-01-15

### Security Check (CWE/OWASP Compliance)
| Rule | Level | Status | Location | CWE/OWASP |
|------|-------|--------|----------|-----------|
| No SQL injection | CRITICAL | ✅ OK | - | CWE-89 |
| No hardcoded secrets | CRITICAL | ❌ FAIL | auth-service.ts:42 | CWE-798 |
| CSRF protection | CRITICAL | ✅ OK | - | CWE-352 |
| Password hashing | CRITICAL | ✅ OK | - | CWE-916 |
| Secure session cookies | CRITICAL | ⚠️ WARN | cookie-middleware.ts:15 | CWE-1004 |
| Rate limiting | SHOULD | ⚠️ WARN | auth-controller.ts:15 | CWE-307 |
| Security logging | SHOULD | ⚠️ WARN | - | CWE-778 |

**CRITICAL Violations (MUST fix)**: 1 — Blocks merge
**SHOULD Warnings**: 3 — Needs justification
**Compliant**: 3

### CWE Compliance Report
| CWE | OWASP | Status | Location | Last Verified |
|-----|-------|--------|----------|---------------|
| CWE-89 | A03 | ✅ OK | - | 2024-01-15 |
| CWE-798 | A02 | ❌ FAIL | auth-service.ts:42 | 2024-01-15 |
| CWE-352 | A01 | ✅ OK | - | 2024-01-15 |
| CWE-916 | A02 | ✅ OK | auth-service.ts:23 | 2024-01-15 |
| CWE-1004 | A01 | ⚠️ WARN | cookie-middleware.ts:15 | 2024-01-15 |
| CWE-307 | A07 | ⚠️ WARN | auth-controller.ts:15 | 2024-01-15 |

**Gap Analysis**:
- CWE-798 (Secrets): Hardcoded API key found → Use env variable
- CWE-1004 (Cookies): Missing SameSite attribute → Add SameSite=Strict
- CWE-307 (Rate Limiting): Not implemented → Add express-rate-limit

### Architecture Check
| Rule | Status | Detail |
|------|--------|--------|
| Constructor injection required | ✅ OK | - |
| Authentication middleware used | ⚠️ WARN | Middleware not in architecture |
| No hardcoded secrets | ❌ FAIL | Line 42: hardcoded "api_key_xxx" |

### Library Verification Check
| Library | Status | Detail |
|---------|--------|--------|
| bcrypt | ✅ OK | Using hash(password, 12) |
| express | ⚠️ WARN | Missing rate-limit dependency |
| jsonwebtoken | ✅ OK | Using verify() correctly |
| lodash | ❌ CRITICAL | Not in Library Verification section |

### Ontology Check
| Term | Status | Detail |
|------|--------|--------|
| "User" used consistently | ✅ OK | - |
| "Authentication" vs "AuthN" | ⚠️ WARN | Inconsistent terminology |

### Summary
- CRITICAL violations: 2 (must fix before proceeding)
  - Hardcoded secret in auth-service.ts:42
  - Unverified library (lodash)
- WARNING violations: 5 (should fix)
- Compliant rules: 7
- **BLOCKED**: Fix CRITICAL violations to proceed
```

---

## Example 3: Context Rot Warning

```markdown
## Constitution Check Report
Target: docs/specs/003-old-feature/2023-06-01--feature-spec.md
Date: 2024-01-15

### ⚠️ Context Rot Warning
This file has not been updated in 30+ days.
Context rot may have occurred — architectural decisions may have drifted.
Consider running `specs.sync` or updating the spec before continuing.

### Security Check (CWE/OWASP Compliance)
| Rule | Level | Status | Location | CWE/OWASP |
|------|-------|--------|----------|-----------|
| No SQL injection | CRITICAL | ✅ OK | - | CWE-89 |
| No hardcoded secrets | CRITICAL | ✅ OK | - | CWE-798 |

**CRITICAL Violations (MUST fix)**: 0
**Compliant**: 2

### Architecture Check
| Rule | Status | Detail |
|------|--------|--------|
| Implementation matches spec | ⚠️ WARN | Code structure changed since spec |
| Stack consistency | ✅ OK | - |

### Summary
- CRITICAL violations: 0
- WARNING violations: 1
- Context rot risk: HIGH
- **Recommendation**: Run `specs.sync` before continuing work on this spec
```