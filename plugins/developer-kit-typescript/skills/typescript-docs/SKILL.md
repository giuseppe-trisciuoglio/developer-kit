---
name: typescript-docs
description: Generates comprehensive TypeScript documentation using JSDoc, TypeDoc, and multi-layered documentation patterns for different audiences. Use when creating API documentation, architectural decision records (ADRs), code examples, and framework-specific patterns for NestJS, Express, React, Angular, and Vue.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# TypeScript Documentation

Generate production-ready TypeScript documentation with layered architecture for multiple audiences. Supports API docs with TypeDoc, ADRs, and framework-specific patterns.

## When to Use

- "generate TypeScript API docs" - Create TypeDoc configuration and generate documentation
- "document this TypeScript module" - Add comprehensive JSDoc to a module
- "create ADR for TypeScript decision" - Document architectural decisions
- "setup documentation pipeline" - Configure automated documentation generation
- "document React component" - Create component documentation with examples
- "create API reference" - Generate comprehensive API documentation

## Quick Reference

| Tool | Purpose | Command |
|------|---------|---------|
| TypeDoc | API documentation generation | `npx typedoc` |
| Compodoc | Angular documentation | `npx compodoc -p tsconfig.json` |
| ESLint JSDoc | Documentation validation | `eslint --ext .ts src/` |

### JSDoc Tags

| Tag | Use Case |
|-----|----------|
| `@param` | Document parameters |
| `@returns` | Document return values |
| `@throws` | Document error conditions |
| `@example` | Provide code examples |
| `@remarks` | Add implementation notes |
| `@see` | Cross-reference related items |
| `@deprecated` | Mark deprecated APIs |

## Instructions

### 1. Configure TypeDoc

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
```

```json
{
  "entryPoints": ["src/index.ts"],
  "out": "docs/api",
  "theme": "markdown",
  "excludePrivate": true,
  "readme": "README.md"
}
```

### 2. Add JSDoc Comments

```typescript
/**
 * Service for managing user authentication
 *
 * @remarks
 * Handles JWT-based authentication with bcrypt password hashing.
 *
 * @example
 * ```typescript
 * const authService = new AuthService(config);
 * const token = await authService.login(email, password);
 * ```
 *
 * @security
 * - Passwords hashed with bcrypt (cost factor 12)
 * - JWT tokens signed with RS256
 */
@Injectable()
export class AuthService {
  /**
   * Authenticates a user and returns access tokens
   * @param credentials - User login credentials
   * @returns Authentication result with tokens
   * @throws {InvalidCredentialsError} If credentials are invalid
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    // Implementation
  }
}
```

### 3. Create an ADR

```markdown
# ADR-001: TypeScript Strict Mode Configuration

## Status
Accepted

## Context
What is the issue motivating this decision?

## Decision
What change are we proposing?

## Consequences
What becomes easier or more difficult?
```

### 4. Set Up CI/CD Pipeline

```yaml
name: Documentation
on:
  push:
    branches: [main]
    paths: ['src/**', 'docs/**']

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run docs:generate
      - run: npm run docs:validate
```

### 5. Validate Documentation

```json
{
  "rules": {
    "jsdoc/require-description": "error",
    "jsdoc/require-param-description": "error",
    "jsdoc/require-returns-description": "error",
    "jsdoc/require-example": "warn"
  }
}
```

## Best Practices

1. **Document Public APIs**: All public methods, classes, and interfaces
2. **Use `@example`**: Provide runnable examples for complex functions
3. **Include `@throws`**: Document all possible errors
4. **Add `@see`**: Cross-reference related functions/types
5. **Use `@remarks`**: Add implementation details and notes
6. **Document Generics**: Explain generic constraints and usage
7. **Include Performance Notes**: Document time/space complexity
8. **Add Security Warnings**: Highlight security considerations
9. **Keep Updated**: Update docs when code changes
10. **Don't document obvious code**: Focus on why, not what

## Constraints and Warnings

- **Private Members**: Use `@private` or exclude from TypeDoc output
- **Complex Types**: Document generic constraints and type parameters
- **Breaking Changes**: Use `@deprecated` with migration guidance
- **Security Info**: Never include secrets or credentials in documentation
- **Link Validity**: Ensure `@see` references point to valid locations
- **Example Code**: All examples should be runnable and tested
- **Versioning**: Keep documentation in sync with code versions

## References

- **[references/jsdoc-patterns.md](references/jsdoc-patterns.md)** — JSDoc patterns for interfaces, functions, classes, generics, and unions
- **[references/framework-patterns.md](references/framework-patterns.md)** — Framework-specific patterns for NestJS, React, Express, and Angular
- **[references/adr-patterns.md](references/adr-patterns.md)** — ADR templates and examples
- **[references/pipeline-setup.md](references/pipeline-setup.md)** — CI/CD pipeline configuration for documentation
- **[references/validation.md](references/validation.md)** — ESLint rules and validation checklists
- **[references/typedoc-configuration.md](references/typedoc-configuration.md)** — Complete TypeDoc configuration options
- **[references/examples.md](references/examples.md)** — Additional code examples
