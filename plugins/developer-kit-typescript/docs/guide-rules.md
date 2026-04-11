# TypeScript Plugin Rules Guide

Standardized coding rules that auto-activate based on file path patterns for consistent code quality across TypeScript, NestJS, React, and related projects.

---

## Rules Overview

Rules are defined in `rules/*.md` files and activate automatically via `globs:` path-scoped matching. When Claude Code works with files matching a rule's glob pattern, that rule's guidelines are automatically applied.

### Available Rules (19 total)

| Category | Rules |
|----------|-------|
| **TypeScript Core** | naming-conventions, project-structure, language-best-practices, error-handling |
| **NestJS** | nestjs-architecture, nestjs-api-design, nestjs-security, nestjs-testing |
| **React & Frontend** | react-component-conventions, react-data-fetching, react-routing-conventions, tailwind-styling-conventions |
| **Data & ORM** | drizzle-orm-conventions, shared-dto-conventions, zod-validation-patterns |
| **Infrastructure** | nx-monorepo-conventions, i18n-conventions, lambda-conventions, server-feature-conventions |

---

## TypeScript Core Rules

### `naming-conventions` — `**/*.ts`

TypeScript identifier naming standards enforcing strict typing and no use of `any`.

**Key Guidelines:**
- Use `PascalCase` for classes, interfaces, type aliases, enums
- Use `camelCase` for variables, functions, methods, parameters
- Use `UPPER_SNAKE_CASE` for constants and environment variables
- Prefix interfaces with `I` only when needed for disambiguation (`IUserService`)
- Avoid using `any` type — use `unknown` with type guards when type is uncertain
- File names: `kebab-case` (`user-profile.service.ts`)

### `project-structure` — `**/*.ts`

Domain-driven module organization for scalable project architecture.

**Key Guidelines:**
- Organize code by feature/domain, not by technical layer
- Use clear, consistent directory naming (`src/features/`, `src/shared/`)
- Keep related files together (entity, DTO, service, controller)
- Apply hexagonal/Clean Architecture patterns for complex domains
- Avoid deep nesting — prefer flat structures with clear naming

### `language-best-practices` — `**/*.ts`

Modern TypeScript features and clean code patterns.

**Key Guidelines:**
- Use strict TypeScript configuration (`strict: true`)
- Leverage utility types (`Partial<T>`, `Required<T>`, `Pick<T>`, `Omit<T>`)
- Prefer `type` over `interface` for simple object shapes
- Use `readonly` for immutable properties
- Leverage template literal types, conditional types, and mapped types
- Use `satisfies` operator for type-safe object literals
- Avoid non-null assertions (`!`) — use optional chaining and nullish coalescing

### `error-handling` — `**/*.ts`

Result pattern, exception hierarchies, and error response strategies.

**Key Guidelines:**
- Use Result pattern (either `Result<T, E>` or discriminated unions) for operations that can fail
- Create custom error classes extending base `Error` for domain-specific errors
- Never swallow errors silently — always log or propagate
- Use `try/catch` with specific exception types
- Return consistent error response shapes across the API
- Use global exception filters in NestJS for centralized error handling

---

## NestJS Rules

### `nestjs-architecture` — `src/**/*.ts`

Modular design, Core/Shared module separation, and circular dependency prevention.

**Key Guidelines:**
- Use feature-based module organization
- Implement `CoreModule` for singleton services (guards, interceptors, pipes)
- Use `SharedModule` for common utilities and reusable components
- Avoid circular dependencies — use `forwardRef()` sparingly
- Keep modules focused with single responsibility
- Export only what's needed from each module (`exports` array)

### `nestjs-api-design` — `src/**/*.ts`

RESTful API design, DTO validation, and response transformation.

**Key Guidelines:**
- Use DTOs for request/response contracts — never expose entities directly
- Validate incoming data with `class-validator` and `class-transformer`
- Use appropriate HTTP status codes (201 for create, 204 for delete, etc.)
- Implement pagination for list endpoints
- Use Swagger decorators for API documentation
- Transform responses consistently with interceptors

### `nestjs-security` — `src/**/*.ts`

Authentication guards, authorization, and input sanitization.

**Key Guidelines:**
- Implement JWT or session-based authentication
- Use guards for endpoint protection (`@UseGuards(AuthGuard)`)
- Implement role-based access control with custom decorators
- Sanitize all user input to prevent injection attacks
- Use helmet and rate limiting middleware
- Never log sensitive data (passwords, tokens, PII)

### `nestjs-testing` — `**/*.spec.ts`

Unit/integration testing patterns with Jest.

**Key Guidelines:**
- Use `@nestjs/testing` for NestJS-specific testing utilities
- Mock external dependencies (database, APIs, services)
- Follow Arrange-Act-Assert (AAA) pattern
- Write focused unit tests — one concept per test
- Use `beforeEach` for test setup, `afterEach` for cleanup
- Aim for high coverage on business logic in services

---

## React & Frontend Rules

### `react-component-conventions` — `**/*.tsx`

Component composition, hooks patterns, and prop design.

**Key Guidelines:**
- Use functional components with hooks
- Define prop interfaces with `interface` (not `type` for props)
- Destructure props with defaults for optional values
- Keep components focused — extract complex logic into custom hooks
- Use `React.memo` for pure components that re-render often
- Prefer composition over prop drilling — use Context or composition

### `react-data-fetching` — `**/*.{ts,tsx}`

Data fetching strategies with TanStack Query.

**Key Guidelines:**
- Use TanStack Query for server state management
- Define query keys as constants for consistency (`['users', userId]`)
- Handle loading, error, and success states explicitly
- Implement optimistic updates for mutations
- Use appropriate stale time to reduce unnecessary refetches
- Prefetch data when navigation is likely

### `react-routing-conventions` — `**/*.tsx`

Route organization and navigation patterns.

**Key Guidelines:**
- Use file-based routing patterns consistent with framework conventions
- Co-locate route-related components and logic
- Implement lazy loading for route-level code splitting
- Use protected routes for authenticated areas
- Handle 404 and error boundaries at route level
- Pass route params as props, not global state

### `tailwind-styling-conventions` — `**/*.tsx`

Tailwind CSS class ordering and responsive design.

**Key Guidelines:**
- Use consistent class ordering: layout → spacing → typography → colors → effects
- Use Tailwind's mobile-first responsive prefixes (`sm:`, `md:`, `lg:`)
- Extract repeated class patterns into components
- Use Tailwind config for design tokens, not hardcoded values
- Use `@apply` sparingly — prefer direct classes in JSX
- Use `clsx` or `cn` utility for conditional classes

---

## Data & ORM Rules

### `drizzle-orm-conventions` — `**/*.schema.ts`

Schema design, migrations, and query patterns for Drizzle ORM.

**Key Guidelines:**
- Define schemas in `*.schema.ts` files following Drizzle conventions
- Use descriptive column names with snake_case in database
- Define relations explicitly with `relations()` function
- Use migrations for all schema changes
- Use transactions for multi-table operations
- Leverage Drizzle's type inference for query results

### `shared-dto-conventions` — `**/*.dto.ts`

DTO design, validation, and serialization.

**Key Guidelines:**
- Create separate DTOs for create, update, and response operations
- Use `class-validator` decorators for validation rules
- Use `class-transformer` for serialization/deserialization
- Omit sensitive fields (passwords, tokens) from response DTOs
- Use `PartialType`, `PickType`, `OmitType` for DTO inheritance
- Document DTOs with JSDoc comments

### `zod-validation-patterns` — `**/*.ts`

Zod schema patterns for runtime validation.

**Key Guidelines:**
- Define schemas at module level for reuse and tree-shaking
- Use Zod's built-in validators (`z.string()`, `z.number()`, etc.)
- Create refined schemas with `z.coerce.*` for input normalization
- Use `z.infer<>` type inference for type-safe validation
- Compose schemas with `merge`, `pick`, `omit`, `partial`
- Use `z.union()` or `z.discriminatedUnion()` for variant types

---

## Infrastructure Rules

### `nx-monorepo-conventions` — `**/*.ts`

Nx workspace organization, library boundaries, and affected commands.

**Key Guidelines:**
- Follow Nx workspace conventions for project structure
- Tag projects consistently (`type:app`, `scope:shared`, etc.)
- Use `affected` commands in CI to test/build only changed projects
- Keep library boundaries enforced with `eslint-plugin-nx` rules
- Use path aliases in `tsconfig.base.json` for clean imports
- Generate code with Nx generators for consistency

### `i18n-conventions` — `**/*.{ts,tsx}`

Internationalization patterns and translation management.

**Key Guidelines:**
- Use i18n keys following namespace patterns (`feature.subsection.key`)
- Provide default values in source language
- Handle pluralization with ICU message format
- Lazy-load translation files for large apps
- Support RTL languages in layout and styling
- Test with multiple languages during development

### `lambda-conventions` — `**/*.ts`

AWS Lambda handler patterns and best practices.

**Key Guidelines:**
- Export handler function as default or named export
- Use TypeScript types for event and context objects
- Implement proper error handling with appropriate error responses
- Use middleware/decorator patterns for common logic
- Keep cold start times minimal
- Implement proper logging with structured formats
- Handle timeouts gracefully

### `server-feature-conventions` — `**/*.ts`

Serverless feature module organization.

**Key Guidelines:**
- Organize serverless functions by feature, not by function type
- Share code through layers or common packages
- Use consistent handler patterns across features
- Implement environment-based configuration
- Use infrastructure-as-code for resource provisioning
- Follow the single responsibility principle for each function

---

## Installation

Rules are automatically activated when working with matching file patterns. To use rules manually or copy them to a project:

```bash
# Copy rules to your project's .claude/rules directory
mkdir -p .claude/rules
cp -r plugins/developer-kit-typescript/rules/* .claude/rules/
```

Rules will activate automatically based on their `globs:` patterns in the YAML frontmatter.

---

## See Also

- [NestJS Skills Guide](./guide-skills-nestjs.md) - NestJS framework patterns
- [Frontend Skills Guide](./guide-skills-frontend.md) - React and Next.js patterns
- [Architecture Skills Guide](./guide-skills-architecture.md) - Clean Architecture patterns
- [Monorepo Skills Guide](./guide-skills-monorepo.md) - Nx and Turborepo patterns
