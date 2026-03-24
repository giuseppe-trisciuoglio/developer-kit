# Architectural Decision Records (ADRs)

## ADR Template

```markdown
# ADR-001: [Decision Title]

## Status
Proposed | Accepted | Rejected | Deprecated | Superseded

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

## Compliance
- Links to standards or regulations
- Impact on compliance requirements

## References
- [TypeScript Strict Mode Documentation](https://www.typescriptlang.org/tsconfig#strict)
- [Related ADRs](#)
```

## Sample ADR

```markdown
# ADR-003: NestJS Framework Selection for Backend API

## Status
Accepted

## Context
Our Express.js monolith has grown to 50k+ lines with:
- Inconsistent error handling patterns
- No standardized validation
- Difficult testing due to tight coupling
- Poor TypeScript integration

We need a framework that provides:
- Strong TypeScript support
- Opinionated structure
- Built-in validation and error handling
- Excellent testing support
- Microservices readiness

## Decision
Adopt NestJS for all new backend services with:
- Full TypeScript strict mode
- Class-based DI container
- Modular architecture
- Built-in validation pipes
- Exception filters
- Swagger/OpenAPI integration

## Consequences

### Positive
- 40% reduction in boilerplate code
- Consistent patterns across services
- Improved testability with dependency injection
- Better developer experience with decorators
- Built-in support for microservices

### Negative
- Learning curve for team (2-3 weeks)
- More complex for simple APIs
- Requires understanding of decorators
- Additional build step needed

## Implementation
1. Create NestJS starter template
2. Migrate new services to NestJS
3. Gradually refactor critical Express services
4. Establish NestJS best practices guide

## Compliance
- Aligns with architecture standards v2.1
- Supports SOC2 through better error handling
- Enables GDPR compliance with structured logging
```

## ADR Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "adr:new": "node scripts/create-adr.js",
    "adr:generate-index": "node scripts/generate-adr-index.js"
  }
}
```
