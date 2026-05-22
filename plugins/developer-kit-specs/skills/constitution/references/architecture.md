# Project Architecture

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

---

## 1. Logical Architecture

> Describes the decomposition of the system into domains, bounded contexts, modules and their relationships. This section is about WHAT the system does from a domain perspective, independent of technology.

### 1.1 Domains and Bounded Contexts

| Bounded Context | Description | Key Responsibilities | Dependencies |
|-----------------|-------------|----------------------|--------------|
| [e.g., Identity] | [e.g., User authentication and authorization] | [e.g., Registration, Login, RBAC] | [e.g., None — core context] |
| [e.g., Catalog] | [e.g., Product catalog management] | [e.g., CRUD products, categories, search] | [e.g., Identity] |
| [e.g., Ordering] | [e.g., Order lifecycle management] | [e.g., Cart, Checkout, Payment, Fulfillment] | [e.g., Catalog, Identity] |

### 1.2 Module Map

```
┌─────────────────────────────────────────────────────┐
│                    [System Name]                     │
├──────────┬──────────┬──────────┬────────────────────┤
│ [Module] │ [Module] │ [Module] │ [Module]           │
│          │          │          │                    │
│  → [dep] │  → [dep] │          │  → [dep]          │
└──────────┴──────────┴──────────┴────────────────────┘
```

<!-- Describe the logical dependency flow between modules.
     Use arrows (→) to indicate "depends on" relationships.
     Keep it at a high level; this is NOT a class diagram. -->

### 1.3 Shared Kernel

| Shared Concept | Used By | Description |
|---------------|---------|-------------|
| [e.g., Money value object] | [e.g., Catalog, Ordering] | [e.g., Currency + amount, no arithmetic logic] |
| [e.g., Event bus interface] | [e.g., All contexts] | [e.g., In-process event dispatch contract] |

### 1.4 Context Map

<!-- Describe the relationships between bounded contexts.
     Patterns: Upstream/Downstream, Conformist, Anti-Corruption Layer,
     Open Host Service, Published Language, Separate Ways, Partnership. -->

| Upstream | Downstream | Relationship Pattern | Notes |
|----------|-----------|---------------------|-------|
| [e.g., Identity] | [e.g., Ordering] | [e.g., Open Host Service] | [e.g., REST API for user lookup] |
| [e.g., Catalog] | [e.g., Ordering] | [e.g., Published Language] | [e.g., Shared product ID schema] |

---

## 2. Infrastructure Architecture

> Describes the deployment model, networking, data flow, and scaling strategy. This section is about WHERE and HOW the system runs in production.

### 2.1 Deployment Topology

```
[Client/Browser] ──HTTPS──▶ [CDN / Load Balancer]
                                  │
                         ┌────────┴────────┐
                         │   [App Tier]     │
                         │  [e.g., ECS / K8s]│
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
              ┌─────┴─────┐ ┌────┴────┐ ┌──────┴─────┐
              │ [Service] │ │[Service]│ │ [Service]  │
              └─────┬─────┘ └────┬────┘ └──────┬─────┘
                    │             │             │
              ┌─────┴─────┐      │      ┌──────┴─────┐
              │  [DB/Store]│      │      │  [DB/Store]│
              └───────────┘      │      └────────────┘
                          ┌──────┴──────┐
                          │ [Message Bus]│
                          └─────────────┘
```

<!-- Replace with actual topology. Use ASCII art or reference a diagram file
     in docs/architecture/diagrams/. -->

### 2.2 Infrastructure Components

| Component | Technology | Version | Purpose | Environment |
|-----------|-----------|---------|---------|-------------|
| Hosting | [e.g., AWS ECS Fargate] | [e.g., N/A] | [e.g., Container orchestration] | [e.g., All] |
| CI/CD | [e.g., GitHub Actions] | [e.g., N/A] | [e.g., Build, test, deploy pipeline] | [e.g., All] |
| Containerization | [e.g., Docker] | [e.g., 24.x] | [e.g., Application packaging] | [e.g., All] |
| Load Balancer | [e.g., AWS ALB] | [e.g., N/A] | [e.g., TLS termination, routing] | [e.g., Staging, Prod] |
| Message Broker | [e.g., RabbitMQ / SQS] | [e.g., 3.12] | [e.g., Async event processing] | [e.g., All] |
| CDN | [e.g., CloudFront] | [e.g., N/A] | [e.g., Static assets, caching] | [e.g., Prod] |
| Secrets Manager | [e.g., AWS Secrets Manager] | [e.g., N/A] | [e.g., Credential storage] | [e.g., All] |

### 2.3 Networking

| Network Zone | CIDR / Description | Accessible From | Purpose |
|-------------|---------------------|-----------------|---------|
| [e.g., Public] | [e.g., ALB only] | [e.g., Internet] | [e.g., HTTPS entry point] |
| [e.g., Private App] | [e.g., 10.0.1.0/24] | [e.g., Public zone only] | [e.g., Application services] |
| [e.g., Data] | [e.g., 10.0.2.0/24] | [e.g., Private App only] | [e.g., Databases, caches] |

### 2.4 Scaling Strategy

| Component | Scaling Type | Trigger | Min / Max |
|-----------|-------------|---------|-----------|
| [e.g., App Service] | [e.g., Horizontal (auto)] | [e.g., CPU > 70%] | [e.g., 2 / 10] |
| [e.g., Database] | [e.g., Vertical (manual)] | [e.g., Storage > 80%] | [e.g., N/A] |
| [e.g., Cache] | [e.g., Vertical (manual)] | [e.g., Memory > 85%] | [e.g., N/A] |

### 2.5 Environments

| Environment | Purpose | URL / Access | Infra Differences |
|-------------|---------|--------------|-------------------|
| [e.g., Local] | [e.g., Development] | [e.g., localhost:3000] | [e.g., Docker Compose, no ALB] |
| [e.g., Staging] | [e.g., Pre-production testing] | [e.g., staging.example.com] | [e.g., Single instance, no auto-scaling] |
| [e.g., Production] | [e.g., Live traffic] | [e.g., app.example.com] | [e.g., Full setup with HA] |

---

## 3. Software Architecture

> Describes the technical structure of the codebase: layers, patterns, conventions, and technology stack. This section is about HOW the system is built.

### 3.1 Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | [e.g., TypeScript] | [e.g., 5.4] | |
| Runtime | [e.g., Node.js] | [e.g., 20 LTS] | |
| Framework | [e.g., NestJS] | [e.g., 10.x] | |
| Key Libraries | [e.g., Drizzle ORM, Passport, class-validator] | | |
| Testing | [e.g., Jest, Supertest] | | [e.g., Unit + Integration] |

### 3.2 Data Architecture

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Primary Database | [e.g., PostgreSQL] | [e.g., 16] | |
| Caching | [e.g., Redis, none] | | |
| ORM / Data Access | [e.g., Drizzle ORM] | [e.g., 0.30] | |
| Migrations | [e.g., Drizzle Kit] | | |
| File Storage | [e.g., S3, none] | | |

### 3.3 Architectural Style

<!-- Pick the primary architectural style and describe how it is applied.
     Common styles: Layered, Hexagonal (Ports & Adapters), Clean Architecture,
     Microservices, Event-Driven, CQRS. -->

**Style**: [e.g., Hexagonal Architecture (Ports & Adapters)]

```
┌────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│          [e.g., REST Controllers, GraphQL Resolvers]    │
├────────────────────────────────────────────────────────┤
│                    Application Layer                    │
│          [e.g., Use Cases, Application Services]        │
├────────────────────────────────────────────────────────┤
│                      Domain Layer                       │
│          [e.g., Entities, Value Objects, Domain Events] │
├────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                 │
│     [e.g., Repositories, External API Clients, DB]      │
└────────────────────────────────────────────────────────┘
```

### 3.4 Project Structure

<!-- Show the canonical directory layout of the project.
     This helps AI agents and new developers understand code organization. -->

```
src/
├── [module-a]/           # [e.g., Bounded Context: Identity]
│   ├── domain/           #   Entities, Value Objects, Domain Events
│   ├── application/      #   Use Cases, Application Services
│   ├── infrastructure/   #   Repositories, External Clients
│   └── presentation/     #   Controllers, DTOs
├── [module-b]/           # [e.g., Bounded Context: Catalog]
│   └── ...
├── shared/               # Shared Kernel
│   ├── domain/           #   Common value objects, interfaces
│   └── infrastructure/   #   Common infrastructure utilities
└── config/               # Application configuration
```

### 3.5 Architectural Rules

- [e.g., "Domain entities must not depend on framework annotations."]
- [e.g., "Use constructor injection. Never use `@Autowired` on fields."]
- [e.g., "Repositories return domain entities, not framework types."]
- [e.g., "Cross-module communication via domain events only, never direct method calls."]

### 3.6 Design Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| [e.g., Repository] | [e.g., Data access abstraction] | [e.g., `UserRepository` interface in domain, impl in infrastructure] |
| [e.g., CQRS] | [e.g., Separate read/write models] | [e.g., Commands mutate state, Queries return DTOs] |
| [e.g., Domain Event] | [e.g., Loose coupling between modules] | [e.g., `OrderPlacedEvent` published to message bus] |
| [e.g., Factory] | [e.g., Complex entity creation] | [e.g., `OrderFactory.create()` enforces invariants] |

### 3.7 API Conventions

| Aspect | Convention | Example |
|--------|-----------|---------|
| URL Style | [e.g., kebab-case, plural nouns] | [e.g., `/api/v1/user-profiles`] |
| Authentication | [e.g., Bearer JWT] | [e.g., `Authorization: Bearer <token>`] |
| Versioning | [e.g., URL path] | [e.g., `/api/v1/...`] |
| Error Format | [e.g., RFC 7807 Problem Details] | [e.g., `{ "type": "...", "title": "...", "status": 422 }`] |
| Pagination | [e.g., Cursor-based] | [e.g., `?cursor=abc&limit=20`] |

### 3.8 Library Verification

<!-- Documents the exact API signatures and versions of all dependencies.
     AI agents MUST verify against this section before using any library. -->

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

---

## 4. Security Constraints

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
| Raw SQL string concatenation | CWE-89 | A03:2021 | SQL Injection | Grep for `'+` in SQL contexts |
| Hardcoded secrets/credentials | CWE-798 | A02:2021 | Credential Exposure | Grep for `password=`, `secret=`, `api_key=` |
| Deserialization of untrusted data | CWE-502 | A08:2021 | Software/Data Integrity | Look for `ObjectInputStream`, unvalidated `JSON.parse` |
| Unvalidated redirects | CWE-601 | A01:2021 | Broken Access Control | Check for `redirect(` without validation |
| Missing authentication on sensitive endpoints | CWE-306 | A01:2021 | Broken Access Control | Scan for public endpoints without auth |
| Insufficient password hashing | CWE-916 | A02:2021 | Cryptographic Failures | Check for plain text or MD5/SHA1 storage |
| Use of deprecated crypto (MD5, SHA1) | CWE-327 | A02:2021 | Cryptographic Failures | Grep for MD5/SHA1 in crypto contexts |
| XML External Entity (XXE) | CWE-611 | A05:2021 | Security Misconfiguration | Check for XML parsers without entity restrictions |
| Path traversal (unsafe file access) | CWE-22 | A01:2021 | Broken Access Control | Check for unsanitized file path inputs |

### Required Patterns (CRITICAL — Must Implement)

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

---

## 5. AI Guardrails

Rules that AI agents MUST follow when generating code for this project:

- **Library Verification**: Before using ANY external library:
  1. Check if library is in "Library Verification" section (3.8)
  2. Verify exact version matches
  3. Use ONLY listed APIs with correct signatures
  4. Follow usage constraints
  5. NEVER use forbidden APIs

- **Architectural Compliance**:
  1. Respect the Architectural Style (3.3) — do not bypass layers
  2. Follow the Project Structure (3.4) — place files in the correct location
  3. Obey Architectural Rules (3.5) — no exceptions without ADR
  4. Use Design Patterns (3.6) where specified
  5. Follow API Conventions (3.7) for all endpoints

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

- [Guardrail 1, e.g., "Never generate `@Transactional` on repository methods."]
- [Guardrail 2, e.g., "Always generate tests alongside implementation code."]
- [Guardrail 3, e.g., "Do not introduce new dependencies without explicit approval."]
