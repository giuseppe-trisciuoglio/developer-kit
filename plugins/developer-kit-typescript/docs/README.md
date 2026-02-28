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

---

## About TypeScript Plugin

The Developer Kit TypeScript Plugin provides:

- **TypeScript Agents**: 13 specialized agents for NestJS, React, TypeScript, and React Native development
- **TypeScript Commands**: 3 commands for code review and security assessment
- **TypeScript Skills**: 22 skills covering NestJS, React patterns, Next.js, Better Auth, Drizzle ORM, Monorepo (Nx/Turborepo), shadcn-ui, Tailwind CSS, AWS Lambda, TypeScript documentation, Clean Architecture, and Code Review (NestJS, Next.js, React, TypeScript Security)

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
│   ├── clean-architecture/     # Clean Architecture patterns
│   ├── better-auth/            # Better Auth integration (NestJS + Next.js)
│   ├── nextjs-app-router/      # Next.js App Router
│   ├── nextjs-authentication/  # Next.js Authentication
│   ├── nextjs-data-fetching/   # Next.js Data Fetching
│   ├── nextjs-performance/     # Next.js Performance
│   ├── nextjs-deployment/      # Next.js Deployment
│   ├── drizzle-orm-patterns/   # Drizzle ORM patterns
│   ├── nestjs-drizzle-crud-generator/ # NestJS CRUD generator with Drizzle
│   ├── nx-monorepo/            # Nx monorepo patterns
│   ├── turborepo-monorepo/     # Turborepo monorepo patterns
│   ├── aws-lambda-typescript-integration/ # AWS Lambda TypeScript integration
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

### UI Frameworks
- **shadcn-ui**: Modern React component library
- **Tailwind CSS**: Utility-first CSS framework
- Component composition patterns
- Responsive design

---

## See Also

- [Core Plugin Documentation](../developer-kit-core/docs/) - Core guides and installation
- [Java Plugin Documentation](../developer-kit-java/docs/) - Java and Spring Boot guides
- [Python Plugin Documentation](../developer-kit-python/docs/) - Python development guides
