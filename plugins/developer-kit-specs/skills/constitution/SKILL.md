---
name: constitution
description: "Creates, updates, validates, and displays the architectural DNA of a project through two shared documents: docs/specs/architecture.md (technology stack, architectural rules, security constraints, AI guardrails) and docs/specs/ontology.md (domain glossary / Ubiquitous Language). Use BEFORE brainstorm as a project setup step, or at any point in the SDD lifecycle to validate specs/tasks against architecture principles. Triggers on 'create constitution', 'update constitution', 'constitution check', 'validate against constitution', 'project principles', 'architectural guardrails', 'setup project architecture', 'define ontology'."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite
---

## Instructions

1. Identify the operation from `$ARGUMENTS` or user intent: `create`, `update`, `check`, or `show`.
2. For **create**: ask which files to create (architecture.md, ontology.md, or both), gather required information via `AskUserQuestion`, then write the files using the templates below.
3. For **update**: identify the target file and section, apply the change surgically, update the `Last Updated` date.
4. For **check**: read both constitution files, read the target file, validate against architectural rules and ontology terms, output a Constitution Check Report.
5. For **show**: read and display both files formatted for readability.
6. Always confirm with the user before writing or overwriting files.

## Examples

**Create constitution before first brainstorm:**
```
/developer-kit-specs:constitution create
```

**Validate a spec against architecture and ontology:**
```
/developer-kit-specs:constitution check --target=docs/specs/001/2024-01-15--user-auth.md
```

**Update the security constraints section:**
```
/developer-kit-specs:constitution update --file=architecture --section=security
```

**Show current constitution:**
```
/developer-kit-specs:constitution show
```

---

# Constitution Skill

## Overview

The **Constitution** is the architectural DNA of a project, expressed through two shared documents:

| File | Purpose |
|------|---------|
| `docs/specs/architecture.md` | Technology stack, infrastructure choices, architectural rules, security constraints, AI guardrails |
| `docs/specs/ontology.md` | Domain glossary (Ubiquitous Language) — terms, definitions, bounded contexts |

These files live at the `docs/specs/` level and are **shared across all specifications**.

**Key difference from the old constitution.md approach**: instead of a single monolithic file, the constitution is split into two focused documents that are also created and enriched by `brainstorm` (Phase 6.8.6) and `spec-to-tasks` (Phase 1.5). This skill lets you create or manage them **before brainstorm**, as a project setup step.

## Context Rot Prevention

The Constitution is designed to survive **context rot** — the degradation of long conversations where initial context is lost, architectural decisions are forgotten, and specifications drift from original principles.

### The Problem

In extended conversations without file-based constitution:
1. Early decisions get buried deep in conversation context
2. Agents forget architectural constraints over time
3. Specifications drift from original principles
4. Team knowledge becomes implicit, not documented
5. Different agents have inconsistent understanding

### The Solution: File-Based Constitution

The Constitution is stored in files, NOT in conversation context:

```
docs/specs/architecture.md  ← Read at start of EVERY session
docs/specs/ontology.md       ← Read at start of EVERY session
```

**Key principle**: The Constitution is NEVER assumed to be in context. It MUST be explicitly read from file before any implementation work.

### Why File-Based (Not Context-Based)

| Approach | Context Rot | Reliability | Team Visibility |
|----------|-------------|-------------|-----------------|
| **File-based** (ours) | Immune | Always current | Shared across team |
| Context-based | Degrades over time | May be incomplete | Single-user |
| Session memory | Degrades | Depends on model | Not shared |

### Session Start Checklist

At the beginning of EVERY session:

```
[ ] Read `docs/specs/architecture.md`
[ ] Read `docs/specs/ontology.md`
[ ] Check if Constitution has been updated since last session
[ ] Validate current work against Constitution
[ ] Flag any deviations in decision-log
```

### Warning Signs of Context Rot

If you notice these, re-read the Constitution immediately:

- "I assumed we use X but I see Y in the code"
- "I thought we had A but it's not in the codebase"
- "The spec says B but it doesn't match reality"
- Decisions contradicting previous conversations
- "This was decided earlier but I can't find it in context"

### Recovery Protocol

When context rot is detected:

1. **Stop**: Don't continue implementation
2. **Read**: `cat docs/specs/architecture.md` and `docs/specs/ontology.md`
3. **Compare**: Match current state against Constitution
4. **Fix**: Update decision-log if deviations exist
5. **Resume**: Continue with correct context

### Context Rot Scenarios

#### Scenario 1: Long Implementation Session

```
Day 1: Constitution created
Day 5: Brainstorm generates spec
Day 10: Implementation starts
Day 15: Context is fading...

→ At Day 15, re-read Constitution before continuing
→ Validate current work against architecture
→ Fix any drift before it compounds
```

#### Scenario 2: Returning After Break

```
Week 1: Feature development started
Week 3: Other work on different features

→ Return to original feature → Re-read Constitution first
→ Match current state vs Constitution
→ Resume with correct context, not memory
```

#### Scenario 3: Handoff to Different Agent

```
Agent A: Created Constitution, started work
Agent B: Taking over the feature

→ Agent B reads Constitution files first
→ Understands architecture from files, not memory
→ Continues with consistent context
```

---

## When to Use

| Scenario | Operation |
|----------|-----------|
| New project — define stack and domain language before first brainstorm | `create` |
| Stack or security rules changed | `update` |
| Validate a spec, task, or file against architecture and ontology | `check` |
| Review current architecture and ontology | `show` |

**Trigger phrases:**
- "Create constitution", "Setup project architecture", "Define ontology"
- "Update constitution", "Update architecture", "Update ontology"
- "Constitution check", "Validate against constitution"
- "Show constitution", "Project principles", "Architectural guardrails"

## Available Operations

**1. create** — Create one or both files interactively
**2. update** — Update a specific section of one file
**3. check** — Validate a spec/task/file against both documents
**4. show** — Display the current state of both documents

---

## Operation: create

1. Ask the user which files to create (if not specified in `$ARGUMENTS`):
   - Options: "Both architecture.md and ontology.md" (recommended), "architecture.md only", "ontology.md only"

2. For each file to create, check if it already exists. If yes, ask: overwrite or skip.

3. **For `docs/specs/architecture.md`**, gather via `AskUserQuestion`:

   **Q1 — Logical Architecture** (domains and bounded contexts):
   - "What are the main domains/bounded contexts of your project?"
   - Options: "I'll describe them", "Single monolith (one context)", or freeform

   **Q2 — Infrastructure**:
   - Options: "AWS", "Docker / Docker Compose", "Kubernetes", "Serverless", "Not yet decided", or freeform

   **Q3 — Software Stack**:
   - Options: "Java / Spring Boot", "TypeScript / NestJS", "TypeScript / React", "Python / Django or FastAPI", "PHP / Laravel or Symfony", or freeform

   **Q4 — Data Architecture**:
   - Options: "PostgreSQL", "MySQL", "MongoDB", "Multiple databases", or freeform

   **Q5 — Architectural Style** (optional):
   - Options: "Layered", "Hexagonal (Ports & Adapters)", "Clean Architecture", "CQRS", "Microservices", or freeform

   **Q6 — Architectural Rules** (optional, freeform):
   - Forbidden patterns, required patterns, security constraints, AI guardrails

   Then create `docs/specs/architecture.md` using the **Architecture Template** with this lookup order:
   1. `${CLAUDE_PLUGIN_ROOT}/templates/architecture.md`
   3. `templates/architecture.md` inside the installed skill folder for non-Claude agents.
   Read the first available file, fill the gathered answers into the placeholder sections, and write the result to `docs/specs/architecture.md`.

4. **For `docs/specs/ontology.md`**, gather via `AskUserQuestion`:

   Ask the user to list the main domain terms and their definitions. Explain:
   > "The ontology captures the Ubiquitous Language of your project. It is normally enriched during brainstorming when terms emerge from the idea. You can seed it now with known terms, or create an empty scaffold to fill later."

   - Options: "Seed with known terms (I'll provide them)", "Create empty scaffold", "Skip for now"

   Then create `docs/specs/ontology.md` using the **Ontology Template** below.

5. Confirm with the user before writing each file.

---

## Operation: update

1. Identify the target file and section from `$ARGUMENTS`:
   - `--file=architecture` or `--file=ontology`
   - `--section=<section-name>` (e.g., `--section=security`, `--section=glossary`)
2. Read the target file.
3. Apply the update surgically — do not touch other sections.
4. Update the `Last Updated` date.
5. Write the updated file.

---

## Operation: check

1. Read both `docs/specs/architecture.md` and `docs/specs/ontology.md`. If either is missing, warn the user but continue with the available file(s).
2. Read the target file from `$ARGUMENTS` (`--target=<path>`).
3. Check against **architecture.md**:
   - Forbidden libraries/imports present?
   - Unapproved patterns used?
   - Security constraints violated (raw SQL, hardcoded secrets, etc.)?
   - AI guardrails violated?
   - **Library imports present?** → Check if in Library Verification section
   - **API calls made?** → Verify signature matches approved list
   - **Security Pattern Violations?** → Check against Security Constraints table
4. Check against **ontology.md**:
   - Are domain terms used consistently (no synonyms for defined terms)?
   - Are new domain concepts introduced without being added to the glossary?
5. **Generate Security Section**:
   - For each security rule in Security Constraints, check if violated
   - Classify violation level (CRITICAL/SHOULD/MAY)
   - Map to CWE/OWASP for compliance reporting
   - Include detection method results in report
6. Output a **Constitution Check Report** with Security section first (see format below).

### Library Verification Check

When checking library usage, output:

```markdown
### Library Verification Check

| Library | Status | Detail |
|---------|--------|--------|
| bcrypt | ✅ OK | Using approved API `hash` with correct signature |
| express | ✅ OK | Route handlers follow pattern |
| pg | ⚠️ WARNING | `pool.query` correct, but missing `pool.end()` cleanup |
| lodash | ❌ CRITICAL | Library not in Library Verification section |
```

**Response to Violations**:
- `❌ CRITICAL`: Library not verified → Stop, flag for user
- `⚠️ WARNING`: API used correctly but pattern incomplete → Warn
- `✅ OK`: Verified against section

---

## Operation: show

1. Read `docs/specs/architecture.md` and `docs/specs/ontology.md`.
2. Print both files formatted for readability, with a header indicating which file is which.

---

## Architecture Template

The architecture template is maintained canonically in the centralized file below, with fallback copies for other installation modes:

```
Primary: `${CLAUDE_PLUGIN_ROOT}/templates/architecture.md`
Fallback: `skills/constitution/templates/architecture.md`
Standalone skill install fallback: `templates/architecture.md`
```

**Do NOT duplicate the template inline in this skill.** Always read the first available file from the lookup order above to get the latest version for the current installation mode.

The template defines these sections:

| # | Section | Purpose |
|---|---------|----------|
| 1 | Logical Architecture | Bounded contexts, modules, context map, shared kernel |
| 2 | Infrastructure Architecture | Deployment topology, networking, scaling, environments |
| 3 | Software Architecture | Tech stack, data architecture, architectural style, project structure, rules, patterns, API conventions, library verification |
| 4 | Security Constraints | Forbidden/required/recommended patterns with CWE/OWASP mapping |
| 5 | AI Guardrails | Rules for AI agents generating code |

<details>
<summary>Legacy template reference (deprecated — primary template path: ${CLAUDE_PLUGIN_ROOT}/templates/architecture.md; fallback: skills/constitution/templates/architecture.md)</summary>

```markdown
# Project Architecture

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Software Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Language | [e.g., TypeScript] | [version if known] |
| Framework | [e.g., NestJS] | [version if known] |
| Key Libraries | [e.g., Drizzle ORM, Passport] | |

## Data Architecture

| Component | Technology | Notes |
|-----------|-----------|-------|
| Primary Database | [e.g., PostgreSQL] | |
| Caching | [e.g., Redis, none] | |
| ORM / Data Access | [e.g., Drizzle, Hibernate] | |
| Migrations | [e.g., Flyway, Drizzle Kit] | |

## Infrastructure

| Component | Technology | Notes |
|-----------|-----------|-------|
| Hosting | [e.g., AWS ECS] | |
| CI/CD | [e.g., GitHub Actions] | |
| Containerization | [e.g., Docker] | |
| Orchestration | [e.g., Kubernetes, none] | |

## Architectural Rules

- [Rule 1, e.g., "Use constructor injection. Never use @Autowired on fields."]
- [Rule 2, e.g., "Domain entities must not depend on framework annotations."]

## Security Constraints

**Note**: Every rule maps to industry standards (OWASP, CWE) for compliance traceability.

### Enforcement Levels

| Level | Meaning | What Happens |
|-------|---------|---------------|
| **CRITICAL** | Must pass before merge | Blocks merge, requires immediate fix |
| **SHOULD** | Should pass, minor deviation acceptable | Warning logged, needs justification |
| **MAY** | Informational, best practice | Suggestion only |

### Forbidden Patterns (CRITICAL — Blocks Merge)

| Pattern | CWE-ID | OWASP | Reason | Detection |
|---------|--------|-------|--------|-----------|
| Raw SQL string concatenation | CWE-89 | A03:2021 | SQL Injection | Grep for `'+` in SQL, use parameterized queries |
| Hardcoded secrets/credentials | CWE-798 | A02:2021 | Credential Exposure | Grep for `password=`, `secret=`, `api_key=` |
| Deserialization of untrusted data | CWE-502 | A08:2021 | Software/Data Integrity Failure | Look for `ObjectInputStream`, `JSON.parse` without validation |
| Unvalidated redirects | CWE-601 | A01:2021 | Broken Access Control | Check for `redirect(` without validation |
| Missing authentication on sensitive endpoints | CWE-306 | A01:2021 | Broken Access Control | Scan for `@RequestMapping` without security annotation |
| Insufficient password hashing (no bcrypt/scrypt/Argon2) | CWE-916 | A02:2021 | Cryptographic Failures | Check for plain text or MD5/SHA1 password storage |
| Use of deprecated crypto (MD5, SHA1 for hashing) | CWE-327 | A02:2021 | Cryptographic Failures | Grep for MD5, SHA1 in crypto contexts |
| Insecure random number generation (Math.random, java.util.Random) | CWE-338 | A02:2021 | Cryptographic Failures | Look for `Math.random()`, `Random()` for security purposes |
| XML External Entity (XXE) | CWE-611 | A05:2021 | Security Misconfiguration | Check for `new XMLParser()` without disable external entities |
| Path traversal (unsafe file access) | CWE-22 | A01:2021 | Broken Access Control | Check for `FileInputStream` without path sanitization |

### Required Patterns (CRITICAL — Must Implement)

| Pattern | CWE-ID | OWASP | Why Required |
|---------|--------|-------|--------------|
| All SQL queries use parameterized statements | CWE-20 | A03:2021 | Prevents SQL injection |
| All secrets via environment variables or Secrets Manager | CWE-522 | A02:2021 | Prevents credential exposure |
| Password hashing with bcrypt cost factor >= 12 | CWE-916 | A02:2021 | Brute force protection |
| JWT tokens include expiration and signature verification | CWE-345 | A01:2021 | Session integrity |
| CSRF tokens on state-changing operations | CWE-352 | A01:2021 | Cross-site request forgery prevention |
| Secure session cookies (HttpOnly, Secure, SameSite) | CWE-1004 | A01:2021 | Session hijacking prevention |
| Input validation on all public endpoints | CWE-20 | A03:2021 | Prevents injection attacks |
| Output encoding for XSS prevention | CWE-79 | A03:2021 | Cross-site scripting prevention |

### Recommended Patterns (SHOULD — Strongly Advised)

| Pattern | CWE-ID | Why Recommended |
|---------|--------|-----------------|
| Input sanitization beyond validation | CWE-138 | Defense in depth |
| Rate limiting on authentication endpoints | CWE-307 | Brute force protection |
| Security event logging | CWE-778 | Audit trail and incident response |
| Timeout for external API calls | CWE-835 | Resource exhaustion prevention |
| Content Security Policy headers | CWE-1021 | XSS prevention |
| File upload validation (type, size, content) | CWE-434 | Malicious file upload prevention |
| SQL query timeout to prevent DoS | CWE-400 | Database resource exhaustion |

### Informational Patterns (MAY — Best Practice)

| Pattern | Why Informational |
|---------|-------------------|
| Encryption at rest for sensitive data | Implementation-specific |
| Regular dependency vulnerability scanning | Maintenance |
| Security code review checklist | Process improvement |
| Penetration testing schedule | Validation |

### Security Validation Workflow

Before implementation, the agent MUST:

1. **Check if code involves security-relevant operations**:
   - User input handling
   - Authentication/authorization
   - Data storage (especially credentials)
   - External API calls
   - File operations
   - Cryptographic operations

2. **Map to CWE/OWASP standards**:
   - Identify relevant CWE categories
   - Check OWASP Top 10 mappings
   - Ensure compliance with project standards

3. **Apply correct enforcement level**:
   - CRITICAL: Must fix before merge
   - SHOULD: Warning, needs justification
   - MAY: Suggestion, no blocking

4. **Document violations with standard references**:
   ```markdown
   ❌ CRITICAL: Raw SQL concatenation at line 42
   - CWE-89 (SQL Injection)
   - OWASP A03:2021
   - Fix: Use parameterized query
   ```

### Remediation Guide

**For CRITICAL violations**:
```
1. STOP implementation immediately
2. Fix the security violation
3. Document the fix with CWE/OWASP reference
4. Re-run constitution check
5. Only proceed when CRITICAL issues are resolved
```

**For SHOULD warnings**:
```
1. Document justification for deviation
2. Add note to decision-log.md
3. Proceed with warning logged
4. Schedule follow-up improvement
5. May proceed if business justification is strong
```

**For MAY suggestions**:
```
1. Consider the recommendation
2. Implement if straightforward
3. No blocking if not implemented
```

### Security Check Integration in Constitution Check

When running `constitution check`, the Security Check section is generated by:

1. Scanning the target file for security-relevant patterns
2. Checking against Forbidden Patterns table
3. Verifying Required Patterns are implemented
4. Classifying violations by enforcement level
5. Mapping to CWE/OWASP for compliance reporting

### Security CWE Quick Reference

| CWE-ID | Name | Category |
|--------|------|----------|
| CWE-79 | Cross-site Scripting (XSS) | A03:2021 |
| CWE-89 | SQL Injection | A03:2021 |
| CWE-306 | Missing Authentication | A01:2021 |
| CWE-400 | Uncontrolled Resource Consumption | A04:2021 |
| CWE-502 | Deserialization of Untrusted Data | A08:2021 |
| CWE-601 | URL Redirect to Untrusted Site | A01:2021 |
| CWE-798 | Hardcoded Credentials | A02:2021 |
| CWE-916 | Use of Password Hash With Insufficient Computational Effort | A02:2021 |

### OWASP Top 10 2021 Mapping

| Category | Description |
|----------|-------------|
| A01:2021 | Broken Access Control |
| A02:2021 | Cryptographic Failures |
| A03:2021 | Injection |
| A04:2021 | Insecure Design |
| A05:2021 | Security Misconfiguration |
| A06:2021 | Vulnerable Components |
| A07:2021 | Auth Failures |
| A08:2021 | Software Integrity Failures |
| A09:2021 | Security Logging Failures |
| A10:2021 | SSRF |

### CWE/OWASP Reference Guide

This section documents the complete mappings for security rules, enabling compliance traceability and gap analysis.

#### Top 10 OWASP (2021) Mapping

| OWASP Category | CWE Categories | Our Rules |
|----------------|---------------|-----------|
| A01:2021 Broken Access Control | CWE-269, CWE-639, CWE-862 | Auth required, RBAC enforced |
| A02:2021 Cryptographic Failures | CWE-327, CWE-916, CWE-798 | bcrypt, no hardcoded secrets |
| A03:2021 Injection | CWE-79, CWE-89, CWE-94 | Parameterized queries, sanitization |
| A04:2021 Insecure Design | CWE-755, CWE-841 | Security design review |
| A05:2021 Security Misconfiguration | CWE-16, CWE-611 | Secure defaults, no debug mode |
| A06:2021 Vulnerable Components | CWE-1104, CWE-1035 | Dependency scanning |
| A07:2021 Auth Failures | CWE-306, CWE-307 | Session timeout, rate limiting |
| A08:2021 Software Integrity | CWE-502, CWE-94 | No untrusted deserialization |
| A09:2021 Security Logging | CWE-778, CWE-117 | Security event logging |
| A10:2021 SSRF | CWE-918 | URL validation, allowlist |

#### Common CWE Reference Table

| CWE-ID | Name | Detection | Our Rule |
|--------|------|-----------|----------|
| CWE-79 | Cross-site Scripting (XSS) | Reflected user input in HTML | Output encoding required |
| CWE-89 | SQL Injection | String concatenation in SQL | Parameterized queries only |
| CWE-94 | Code Injection | eval() or dynamic code execution | No eval, sandboxed execution |
| CWE-269 | Privilege Escalation | Missing authorization checks | RBAC, least privilege principle |
| CWE-306 | Missing Authentication | Unprotected endpoints | `@PreAuthorize` on all endpoints |
| CWE-307 | Brute Force | No rate limiting on auth | Rate limiter required |
| CWE-327 | Weak Cryptography | MD5/SHA1 usage | Use AES-256, bcrypt, Argon2 |
| CWE-338 | Predictable Random Number Generation | Math.random() for security | Use `SecureRandom` |
| CWE-352 | Cross-Site Request Forgery (CSRF) | Missing CSRF tokens | CSRF token on all state changes |
| CWE-400 | Uncontrolled Resource Consumption | No query timeout | SQL query timeout required |
| CWE-434 | Unrestricted Upload | No file type validation | File type/size validation required |
| CWE-502 | Unsafe Deserialization | ObjectInputStream usage | JSON only, no binary deserialization |
| CWE-522 | Insufficient Password Storage | Plain text passwords | bcrypt with cost >= 12 |
| CWE-601 | Open Redirect | Unvalidated redirect | Allowlist validation only |
| CWE-639 | Authorization Bypass via User ID (IDOR) | Missing ownership check | Authorization check required |
| CWE-798 | Hardcoded Credentials | Password/secret in code | Environment variables or Secrets Manager |
| CWE-835 | Loop Unbounded | No timeout on loops | Timeout required for external calls |
| CWE-862 | Missing Authorization | Unprotected resource | Auth required on all resources |
| CWE-916 | Password Hashing with Insufficient Effort | MD5/plain text | bcrypt cost >= 12 |
| CWE-918 | Server-Side Request Forgery (SSRF) | URL from user without validation | URL validation, allowlist only |

#### CWE Mapping in Code Examples

When implementing security-sensitive code, document the CWE being addressed:

**Java Example — SQL Injection Prevention (CWE-89):**
```java
// CWE-89: SQL Injection Prevention
// OWASP A03:2021: Injection
// Rule: Use parameterized queries only
// Enforcement: CRITICAL

public User findById(Long id) {
    // ✅ CORRECT: Parameterized query prevents CWE-89
    return jdbcTemplate.queryForObject(
        "SELECT * FROM users WHERE id = ?",
        userRowMapper,
        id
    );

    // ❌ INCORRECT: String concatenation violates CWE-89
    // return jdbcTemplate.queryForObject(
    //     "SELECT * FROM users WHERE id = " + id,
    //     userRowMapper
    // );
}
```

**Java Example — Password Hashing (CWE-916):**
```java
// CWE-916: Password Hashing with Insufficient Computational Effort
// OWASP A02:2021: Cryptographic Failures
// Rule: bcrypt with cost factor >= 12
// Enforcement: CRITICAL

public void setPassword(String plainPassword) {
    // ✅ CORRECT: bcrypt with cost factor 12+ prevents CWE-916
    this.passwordHash = BCrypt.hashpw(plainPassword, BCrypt.withCosts(12));

    // ❌ INCORRECT: MD5 violates CWE-916 and CWE-327
    // this.passwordHash = MD5(plainPassword);
}
```

**TypeScript Example — XSS Prevention (CWE-79):**
```typescript
// CWE-79: Cross-site Scripting (XSS)
// OWASP A03:2021: Injection
// Rule: Output encoding for user input
// Enforcement: CRITICAL

function renderUserInput(input: string): string {
    // ✅ CORRECT: HTML encoding prevents CWE-79
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');

    // ❌ INCORRECT: Direct insertion violates CWE-79
    // return `<div>${input}</div>`;
}
```

**Java Example — Authentication (CWE-306):**
```java
// CWE-306: Missing Authentication
// OWASP A01:2021: Broken Access Control
// Rule: All sensitive endpoints require authentication
// Enforcement: CRITICAL

`@RestController`
public class UserController {

    // ✅ CORRECT: `@PreAuthorize` ensures CWE-306 compliance
    `@PreAuthorize`("isAuthenticated()")
    `@GetMapping`("/api/users/me")
    public UserProfile getCurrentUser() { ... }

    // ❌ INCORRECT: Missing annotation violates CWE-306
    // `@GetMapping`("/api/users/me")
    // public UserProfile getCurrentUser() { ... }
}
```

**TypeScript Example — SSRF Prevention (CWE-918):**
```typescript
// CWE-918: Server-Side Request Forgery
// OWASP A10:2021
// Rule: Validate URLs against allowlist
// Enforcement: CRITICAL

const ALLOWED_HOSTS = ['api.trusted.com', 'cdn.trusted.com'];

async function fetchExternalResource(url: string): Promise<Response> {
    // ✅ CORRECT: URL validation prevents CWE-918
    const parsed = new URL(url);
    if (!ALLOWED_HOSTS.includes(parsed.hostname)) {
        throw new Error('SSRF attempt blocked: ' + url);
    }
    return fetch(url);

    // ❌ INCORRECT: Unvalidated URL violates CWE-918
    // return fetch(url);
}
```

---

## Library Verification

This section documents the exact API signatures and versions of all dependencies. AI agents MUST verify against this section before using any library.

### Purpose

- Prevent API hallucinations (invented methods)
- Ensure version compatibility
- Document approved usage patterns
- Reduce integration errors

### Format

Each library entry should follow this structure:

```markdown
### [Library Name]

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

**Usage Patterns**:
```typescript
// ✅ CORRECT: How to use this library
import { methodName } from 'library';
const result = await methodName(options);

// ❌ INCORRECT: Will be flagged
import { wrongMethod } from 'library'; // This method doesn't exist
```

---

### [Next Library]

[Repeat structure]
```

### Verification Workflow

Before using any external library, the AI agent MUST:

1. **Check this section**: Is the library listed?
2. **Verify version**: Is the version listed?
3. **Check API**: Is the method/function in Approved APIs?
4. **Check constraints**: Are there usage constraints?
5. **Check forbidden**: Is the API in Forbidden APIs?

If library/API not listed:
- ❌ DO NOT use the library/API
- ✅ Ask user for clarification
- ✅ Document in decision-log if approved

### Enforcement Levels

- **CRITICAL**: Using unlisted library/API without approval
- **SHOULD**: Using listed library but wrong signature
- **SHOULD**: Ignoring usage constraints
- **MAY**: Suggesting library improvement

### Adding New Libraries

When a new library is needed:

1. Research the library on official docs
2. Identify the exact package name and version
3. Document all used APIs with signatures
4. Add to this section
5. Update version if upgraded

## AI Guardrails

Rules that AI agents MUST follow when generating code for this project:

- **Library Verification**: Before using ANY external library:
  1. Check if library is in "Library Verification" section
  2. Verify exact version matches
  3. Use ONLY listed APIs with correct signatures
  4. Follow usage constraints
  5. NEVER use forbidden APIs

- **Spec Death Principle**: Every spec has a limited lifespan:
  1. During implementation, spec is the source of truth
  2. After completion, run `specs.sync` to update spec
  3. Archive completed specs to `archived/` folder — never let specs become stale
  4. A spec that lives forever without archiving becomes misleading technical debt

- **Context Rot Prevention**:
  1. Read `docs/specs/architecture.md` at session start
  2. Read `docs/specs/ontology.md` at session start
  3. Do NOT assume Constitution is in context — it MUST be read from file
  4. Validate all work against Constitution files, not memory
  5. If you notice assumptions contradicting Constitution, re-read immediately

- [Guardrail 1, e.g., "Never generate @Transactional on repository methods."]
- [Guardrail 2, e.g., "Always generate tests alongside implementation code."]
- [Guardrail 3, e.g., "Do not introduce new dependencies without explicit approval."]
```

</details>

---

## Ontology Template

```markdown
# Project Ontology — Ubiquitous Language

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Domain Glossary

| Term | Definition | Bounded Context |
|------|-----------|-----------------|
| [Term 1] | [Definition] | [Context where this term applies] |
| [Term 2] | [Definition] | [Context where this term applies] |

## Bounded Contexts

| Context | Description | Key Terms |
|---------|-------------|-----------|
| [Context 1] | [Description] | [Key terms] |

## Conceptual Mapping

[Relationships between key domain entities — to be refined during brainstorming and task generation]
```

---

## Constitution Check Report Format

```
## Constitution Check Report
Target: <file or spec path>
Date: YYYY-MM-DD

### Security Check (CWE/OWASP Compliance)

| Rule | Level | Status | Location | CWE/OWASP |
|------|-------|--------|----------|-----------|
| No SQL injection | CRITICAL | ✅ OK | - | CWE-89 |
| No hardcoded secrets | CRITICAL | ❌ FAIL | user-service.ts:42 | CWE-798 |
| CSRF protection | CRITICAL | ✅ OK | - | CWE-352 |
| Password hashing | CRITICAL | ✅ OK | - | CWE-916 |
| Secure session cookies | CRITICAL | ✅ OK | - | CWE-1004 |
| Rate limiting | SHOULD | ⚠️ WARN | auth-controller.ts:15 | CWE-307 |
| Security logging | SHOULD | ⚠️ WARN | - | CWE-778 |

**CRITICAL Violations (MUST fix)**: 1 — Blocks merge
**SHOULD Warnings**: 2 — Needs justification
**Compliant**: 4

### CWE Compliance Report

| CWE | OWASP | Status | Location | Last Verified |
|-----|-------|--------|----------|---------------|
| CWE-89 | A03 | ✅ OK | UserRepository.java:45 | YYYY-MM-DD |
| CWE-798 | A02 | ❌ FAIL | user-service.ts:42 | YYYY-MM-DD |
| CWE-352 | A01 | ✅ OK | - | YYYY-MM-DD |
| CWE-916 | A02 | ✅ OK | AuthService.java:23 | YYYY-MM-DD |
| CWE-307 | A07 | ⚠️ WARN | auth-controller.ts:15 | YYYY-MM-DD |

**Gap Analysis**:
- CWE-352 (CSRF): Implemented ✅
- CWE-307 (Brute Force): Partial implementation — add rate limiting
- CWE-918 (SSRF): Not applicable to this module

### Architecture Check

| Rule | Status | Detail |
|------|--------|--------|
| Constructor injection required | ✅ OK | No field injection found |
| No hardcoded secrets | ❌ FAIL | Line 42: hardcoded password string |
| JWT authentication | ⚠️ WARNING | Missing @PreAuthorize on endpoint |

### Library Verification Check

| Library | Status | Detail |
|---------|--------|--------|
| bcrypt | ✅ OK | Using hash(password, 12) |
| express | ✅ OK | All routes use typed handlers |
| pg | ✅ OK | Parameterized queries only |
| lodash | ❌ CRITICAL | Not in Library Verification section |

### Ontology Check

| Term | Status | Detail |
|------|--------|--------|
| "Reservation" used consistently | ✅ OK | No synonym "Booking" found |
| New term "Voucher" introduced | ⚠️ WARNING | Not defined in ontology.md |

### Summary
- CRITICAL violations: 2 (must fix before proceeding)
- WARNING violations: 3 (should fix)
- Compliant rules: 5
- Library verification: 1 critical violation (lodash not verified)
```

---

## Relationship with brainstorm and spec-to-tasks

This skill is the **pre-brainstorm setup** entry point. The same files are also created/enriched by:

| Command | When | What it does |
|---------|------|-------------|
| `constitution create` | Before brainstorm (this skill) | Creates architecture.md and/or ontology.md from scratch |
| `brainstorm` Phase 6.8.6 | During brainstorming | Creates/enriches ontology.md with terms extracted from the idea |
| `spec-to-tasks` Phase 1.5 | After brainstorm | Creates architecture.md if missing; enriches ontology.md with new terms from the spec |

**If you run `constitution create` before brainstorm**, the brainstorm and spec-to-tasks commands will detect the existing files and load them instead of creating new ones — no duplication.

**Note on ontology.md**: The ontology is normally most naturally created during brainstorming, because domain terms emerge from the idea description. Using `constitution create` to seed it beforehand is useful when the team already has a well-defined domain language.

---

## Integration with SDD Workflow

```
[Session Start] → Read Constitution files
        ↓
[Optional] constitution create        ← this skill (pre-brainstorm setup)
        ↓
brainstorm                            ← Constitution loaded before brainstorming
        ↓
spec-to-tasks                         ← Constitution validates spec
        ↓
task-implementation                   ← Constitution guardrails active
        ↓
task-review                           ← Constitution check validates
        ↓
[Session End] → Constitution files updated if needed
```

**Constitution Loading**: Before ANY of these commands run, the agent MUST:
1. Read `docs/specs/architecture.md`
2. Read `docs/specs/ontology.md`

Required for:
- `specs.brainstorm` — Validate requirements align with architecture
- `specs.spec-to-tasks` — Check stack compatibility
- `specs.task-implementation` — Apply AI guardrails
- `specs.task-review` — Constitution check
- `specs.constitution check` — Full validation

Optional for:
- `specs.sync` — Only if spec-to-code drift suspected

**Note**: Library Verification is enforced:
1. At `task-implementation` time: Check imports before using
2. At `task-review` time: Verify against constitution
3. At `constitution check` time: Full audit of library usage

---

## Constitution Check — Context Rot Detection

When running `constitution check`, also evaluate file freshness:

| Age of Target File | Risk | Action |
|--------------------|------|--------|
| < 7 days | LOW | Proceed normally |
| 7-30 days | MEDIUM | Warn user, check for updates |
| > 30 days | HIGH | Suggest review/update, context rot likely |

**Context Rot Warning**: If the target file is older than 30 days, include this warning:

```markdown
> ⚠️ **Context Rot Warning**: This file has not been updated in 30+ days.
> Context rot may have occurred — architectural decisions may have drifted.
> Consider running `specs.sync` or updating the spec before continuing.
```

**Recovery Actions** for high context rot risk:
1. Read current Constitution files (`docs/specs/architecture.md`, `docs/specs/ontology.md`)
2. Compare spec vs Constitution
3. Identify drifts
4. Update spec or Constitution
5. Document deviations in decision-log

---

## Constraints

- **Does NOT modify source code** — only creates/updates `docs/specs/architecture.md` and `docs/specs/ontology.md`
- **Constitution Check is advisory for WARNINGs** — CRITICAL violations must be resolved
- **One architecture.md and one ontology.md per project** — shared across all specs
- **Version the architecture** — update `Last Updated` date on every change; use ADRs for significant decisions
