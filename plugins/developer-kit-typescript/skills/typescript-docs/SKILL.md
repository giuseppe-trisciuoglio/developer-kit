---
name: typescript-docs
description: Generates comprehensive TypeScript documentation using JSDoc, TypeDoc, and multi-layered documentation patterns for different audiences. Use when creating API documentation, architectural decision records (ADRs), code examples, and framework-specific patterns for NestJS, Express, React, Angular, and Vue.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# TypeScript Documentation Skill

## Overview

Deliver production-ready TypeScript documentation that serves multiple audiences through layered documentation architecture. Generate API docs with TypeDoc, create architectural decision records, and maintain comprehensive code examples.

## When to Use

- "generate TypeScript API docs" - Create TypeDoc configuration and generate documentation
- "document this TypeScript module" - Add comprehensive JSDoc to a module
- "create ADR for TypeScript decision" - Document architectural decisions
- "setup documentation pipeline" - Configure automated documentation generation
- "document React component" - Create component documentation with examples
- "create API reference" - Generate comprehensive API documentation

## Instructions

1. **Configure TypeDoc**: Set up typedoc.json with entry points and output settings
2. **Add JSDoc Comments**: Document all public APIs with @param, @returns, @example
3. **Create ADRs**: Document architectural decisions with context and consequences
4. **Set Up Pipeline**: Configure CI/CD for automated documentation generation
5. **Write Examples**: Include runnable code examples for complex functions
6. **Cross-Reference**: Use @see and @link to connect related documentation
7. **Validate Docs**: Run ESLint with JSDoc rules to ensure completeness

## Examples

### Documenting a Service Class

```typescript
/**
 * Service for managing user authentication and authorization
 *
 * @remarks
 * Handles JWT-based authentication, password hashing,
 * and role-based access control.
 *
 * @example
 * ```typescript
 * const authService = new AuthService(config);
 * const token = await authService.login(email, password);
 * const user = await authService.verifyToken(token);
 * ```
 */
@Injectable()
export class AuthService {
  /**
   * Authenticates a user and returns access tokens
   * @param credentials - User login credentials
   * @returns Authentication result with access and refresh tokens
   * @throws {InvalidCredentialsError} If credentials are invalid
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    // Implementation
  }
}
```

### TypeDoc Quick Start

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
npx typedoc
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

## Constraints and Warnings

- **Private Members**: Use @private or exclude from TypeDoc output
- **Complex Types**: Document generic constraints and type parameters
- **Breaking Changes**: Use @deprecated with migration guidance
- **Security Info**: Never include secrets or credentials in documentation
- **Example Code**: All examples should be runnable and tested

## Best Practices

1. Document all public methods, classes, and interfaces
2. Provide runnable @example for complex functions
3. Include @throws for all possible errors
4. Use @see to cross-reference related functions/types
5. Add @remarks for implementation details
6. Document generic constraints and usage
7. Keep documentation updated when code changes

## References

Consult these files for detailed patterns and examples:

- **[references/examples.md](references/examples.md)** - JSDoc patterns (interfaces, functions, classes, generics, unions), framework-specific docs (NestJS, React, Angular, Express), ADR templates
- **[references/typedoc-configuration.md](references/typedoc-configuration.md)** - TypeDoc config, CI/CD pipeline, ESLint rules, validation plugins, documentation scripts
