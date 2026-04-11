# Developer Kit TypeScript Plugin Documentation

Welcome to the Developer Kit TypeScript Plugin documentation. This plugin provides comprehensive tools for TypeScript, JavaScript, NestJS, React, React Native, and monorepo development.

---

## Available Documentation

### Skills Guides

- **[NestJS Skills](./guide-skills-nestjs.md)** - NestJS framework skills
- **[Frontend Skills](./guide-skills-frontend.md)** - React, Next.js, TypeScript, UI framework skills
- **[Architecture Skills](./guide-skills-architecture.md)** - Clean Architecture and DDD skills
- **[Monorepo Skills](./guide-skills-monorepo.md)** - Nx and Turborepo monorepo patterns

### Component Guides

- **[Agent Guide](./guide-agents.md)** - TypeScript, NestJS, React specialized agents
- **[Command Guide](./guide-commands.md)** - TypeScript and React commands
- **[Rules Guide](./guide-rules.md)** - TypeScript coding rules (19 rules covering NestJS, React, Data, Infrastructure)

---

## About TypeScript Plugin

The Developer Kit TypeScript Plugin provides:

- **TypeScript Agents**: 13 specialized agents for NestJS, React, TypeScript, and React Native development
- **TypeScript Commands**: 3 commands for code review and security assessment
- **TypeScript Skills**: 26 skills covering NestJS, React patterns, Next.js, Better Auth, Drizzle ORM, DynamoDB-Toolbox v2, Zod validation, Monorepo (Nx/Turborepo), shadcn-ui, Tailwind CSS, AWS Lambda, AWS CDK, TypeScript documentation, Clean Architecture, and Code Review (NestJS, Next.js, React, TypeScript Security)

---

## Plugin Structure

```
developer-kit-typescript/
├── agents/              # TypeScript, NestJS, React agents
├── commands/            # TypeScript commands (devkit.typescript.*, devkit.react.*, devkit.ts.*)
├── skills/              # TypeScript skills
│   ├── nestjs/          # NestJS framework skill
│   ├── react-patterns/  # React patterns skill
│   ├── shadcn-ui/       # shadcn/ui component library skill
│   ├── tailwind-css-patterns/  # Tailwind CSS skill
│   ├── typescript-docs/ # TypeScript documentation skill
│   ├── zod-validation-utilities/ # Zod v4 validation utilities
│   ├── clean-architecture/     # Clean Architecture patterns
│   ├── better-auth/            # Better Auth integration (NestJS + Next.js)
│   ├── nextjs-app-router/      # Next.js App Router
│   ├── nextjs-authentication/  # Next.js Authentication
│   ├── nextjs-data-fetching/   # Next.js Data Fetching
│   ├── nextjs-performance/     # Next.js Performance
│   ├── nextjs-deployment/      # Next.js Deployment
│   ├── drizzle-orm-patterns/   # Drizzle ORM patterns
│   ├── dynamodb-toolbox-patterns/ # DynamoDB-Toolbox v2 patterns
│   ├── nestjs-drizzle-crud-generator/ # NestJS CRUD generator with Drizzle
│   ├── nx-monorepo/            # Nx monorepo patterns
│   ├── turborepo-monorepo/     # Turborepo monorepo patterns
│   ├── aws-lambda-typescript-integration/ # AWS Lambda TypeScript integration
│   ├── aws-cdk/                     # AWS CDK infrastructure-as-code
│   ├── nestjs-code-review/        # NestJS code review
│   ├── nextjs-code-review/        # Next.js code review
│   ├── react-code-review/         # React code review
│   └── typescript-security-review/ # TypeScript security review
└── docs/               # This documentation
```

---

## Quick Start

1. **Explore available agents**: See [Agent Guide](./guide-agents.md)
2. **Try TypeScript commands**: See [Command Guide](./guide-commands.md)
3. **Learn NestJS patterns**: See [NestJS Skills](./guide-skills-nestjs.md)
4. **Master React development**: See [Frontend Skills](./guide-skills-frontend.md)

---

## Key Features

### NestJS Backend Development
- Module organization and structure
- Controller and service patterns
- Dependency injection
- Middleware, guards, interceptors
- Database integration (TypeORM, Prisma, Mongoose)
- Security implementation
- Comprehensive testing

### React Frontend Development
- Component design and patterns
- React Hooks best practices
- State management (Context, Redux, Zustand)
- Performance optimization
- API integration

### Authentication
- Better Auth integration for NestJS backend and Next.js frontend
- Email/password, OAuth providers, JWT tokens, session management
- MFA/2FA, passkeys, social providers
- Drizzle ORM + PostgreSQL database schema
- Role-based access control (RBAC)

### Next.js Full-Stack Development
- App Router patterns and fundamentals
- Server Components and Client Components
- Authentication with Auth.js/NextAuth
- Data fetching with React Query/TanStack Query
- Performance optimization and Core Web Vitals
- Deployment patterns (Docker, Vercel, AWS)
- SEO and metadata optimization

### Drizzle ORM & Database
- Schema definitions and type-safe queries
- Relations (one-to-one, one-to-many, many-to-many)
- Transactions and migrations with Drizzle Kit
- NestJS CRUD module generation with Drizzle ORM
- Support for PostgreSQL, MySQL, SQLite

### DynamoDB-Toolbox v2
- Type-safe Table/Entity modeling for DynamoDB with AWS SDK v3 DocumentClient
- `.build()` command workflows for CRUD operations (GetItem, PutItem, UpdateItem, DeleteItem)
- Complex schema patterns with `item`, `string`, `number`, `list`, `set`, `map`, `record` types
- Modifiers: `.key()`, `.required()`, `.default()`, `.transform()`, `.link()`
- Query/Scan and index-focused access pattern guidance
- Batch/transaction operations (BatchWriteCommand, TransactWriteCommand)
- Single-table design with computed keys and entity patterns

### Zod Validation
- Modern Zod v4 validation utilities and schema patterns
- Primitives with custom `error` option (`z.uuid()`, `z.email()`, `z.url()`)
- Coercion at boundaries (`z.coerce.*`) for uncertain input types
- `preprocess` and `transform` for data normalization
- Complex structures: discriminated unions, tuples, records, arrays
- `refine` and `superRefine` for custom validation logic
- React Hook Form integration with `zodResolver`
- `z.input`/`z.output` type inference for transformed schemas

### Monorepo Management
- Nx workspace patterns (generators, affected commands, Module Federation)
- Turborepo patterns (turbo.json, task dependencies, remote caching)
- CI/CD integration for monorepo architectures
- Framework-specific configurations (NestJS, React, Next.js)

### AWS Lambda Integration
- TypeScript Lambda handlers with NestJS adapters
- Express and Fastify Lambda adapters
- Serverless Framework deployment patterns
- Raw TypeScript Lambda handlers

### React Native Mobile
- Expo development workflow
- React Native components
- Device API integration
- Mobile UI/UX patterns
- App deployment

### TypeScript Development
- Type system optimization
- Code refactoring with types
- Security assessment
- Architecture review
- Documentation generation

## Claude Code Hooks

The TypeScript plugin ships with four Claude Code hooks that run automatically during development sessions. All hooks are written in pure Python 3 (no external dependencies) and follow the same exit-code contract as the core plugin.

| Hook script | Event | Blocking? | Purpose |
|---|---|---|---|
| `ts-session-context.py` | `PreToolUse` (first call) | No | Injects git branch, commits, and TODO.md into context |
| `ts-file-validator.py` | `PostToolUse` (Write) | **Yes** (exit 2) | Enforces kebab-case naming for `.ts`/`.tsx` files |
| `ts-pattern-validator.py` | `PostToolUse` (Write) | No (advisory) | Warns on anti-patterns and missing NestJS decorators |
| `ts-quality-gate.py` | `Stop` | **Yes** (exit 2) | Runs `tsc --noEmit` and `eslint` on modified files |

### Exit Code Semantics

| Code | Meaning | Behavior |
|---|---|---|
| `0` | Success | Proceed silently |
| `1` | Warning / context | Show stdout to Claude; continue |
| `2` | Error / violation | Show stderr to Claude; **block** until fixed |

### Session Context (`ts-session-context.py`)

Fires once per session (first `PreToolUse` event) and outputs:

- Active git branch and last 5 commits
- Uncommitted changes summary
- Project name, version, and detected frameworks (NestJS, Next.js, React, Nx, etc.)
- Contents of `TODO.md` if present

### File Naming Validator (`ts-file-validator.py`)

Fires after every `Write` call that produces a `.ts` or `.tsx` file. **Blocks** (exit 2) if the base filename is not `kebab-case`:

```
# ✅ Valid
user-profile.service.ts
auth-token.controller.ts
create-user.dto.ts

# ❌ Blocked — must be renamed
UserProfile.service.ts   → user-profile.service.ts
authToken.controller.ts  → auth-token.controller.ts
```

`index.ts`, declaration files (`.d.ts`), and files inside `node_modules`, `dist`, `build` etc. are exempt.

### Architectural Pattern Validator (`ts-pattern-validator.py`)

Fires after every `Write` call on a TypeScript file. Emits non-blocking advisories (exit 1) for:

- **Missing NestJS decorators** — e.g., a `.controller.ts` without `@Controller`
- **Anti-patterns**: `any`, `@ts-ignore`, `@ts-nocheck`, `require()`, `console.*` in production code
- **Direct instantiation**: `new SomeService()` / `new SomeRepository()`
- **Business logic in controllers**: direct ORM/DB access in `.controller.ts`

### Quality Gate (`ts-quality-gate.py`)

Fires on every `Stop` event. Runs against the TypeScript project in `CLAUDE_CWD`:

1. `npx tsc --noEmit` — type-checks the whole project
2. `npx eslint <modified-files>` — lints only the files modified in the current session
3. `npx nx affected --target=lint` — for Nx monorepos

Exits with code 2 (blocking) if type errors or lint errors are found, code 1 for warnings, code 0 on clean.

---


## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) - Core guides and installation
- [Java Plugin Documentation](../../developer-kit-java/docs/) - Java and Spring Boot guides
- [Python Plugin Documentation](../../developer-kit-python/docs/) - Python development guides
