---
name: better-auth
description: Provides Better Auth authentication integration patterns for NestJS backend and Next.js frontend with Drizzle ORM and PostgreSQL. Use when implementing authentication - Setting up Better Auth with NestJS backend, Integrating Next.js App Router frontend, Configuring Drizzle ORM schema with PostgreSQL, Implementing social login (GitHub, Google, etc.), Adding plugins (2FA, Organization, SSO, Magic Link, Passkey), Email/password authentication with session management, Creating protected routes and middleware
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Better Auth Integration Guide

## Overview

Better Auth is a comprehensive authentication framework for TypeScript that provides type-safe authentication with support for multiple providers, 2FA, SSO, organizations, and more. This skill covers complete integration patterns for NestJS backend with Drizzle ORM and PostgreSQL, plus Next.js App Router frontend integration.

## When to Use

- Setting up Better Auth with NestJS backend
- Integrating Next.js App Router frontend with Better Auth
- Configuring Drizzle ORM schema with PostgreSQL for authentication
- Implementing social login (GitHub, Google, Facebook, Microsoft, etc.)
- Adding Multi-Factor Authentication (MFA/2FA) with TOTP
- Implementing passkey (WebAuthn) passwordless authentication
- Managing trusted devices for streamlined authentication
- Using backup codes for 2FA account recovery
- Adding authentication plugins (2FA, Organization, SSO, Magic Link, Passkey)
- Email/password authentication with secure session management
- Creating protected routes and authentication middleware
- Implementing role-based access control (RBAC)
- Building multi-tenant applications with organizations

## Quick Start

### Installation

```bash
# Backend (NestJS)
npm install better-auth @auth/drizzle-adapter
npm install drizzle-orm pg
npm install -D drizzle-kit

# Frontend (Next.js)
npm install better-auth
```

### Basic Setup

1. Configure Better Auth instance (backend)
2. Set up Drizzle schema with Better Auth tables
3. Create auth module in NestJS
4. Configure Next.js auth client
5. Set up middleware for protected routes

## Architecture

### Backend (NestJS)

```
src/
├── auth/
│   ├── auth.module.ts           # Auth module configuration
│   ├── auth.controller.ts       # Auth HTTP endpoints
│   ├── auth.service.ts          # Business logic
│   ├── auth.guard.ts            # Route protection
│   └── schema.ts                # Drizzle auth schema
├── database/
│   ├── database.module.ts       # Database module
│   └── database.service.ts      # Drizzle connection
└── main.ts
```

### Frontend (Next.js)

```
app/
├── (auth)/
│   ├── sign-in/
│   │   └── page.tsx            # Sign in page
│   └── sign-up/
│       └── page.tsx            # Sign up page
├── (dashboard)/
│   ├── dashboard/
│   │   └── page.tsx            # Protected page
│   └── layout.tsx              # With auth check
├── api/
│   └── auth/
│       └── [...auth]/route.ts  # Auth API route
├── layout.tsx                   # Root layout
└── middleware.ts                # Auth middleware
lib/
├── auth.ts                      # Better Auth client
└── utils.ts
```

## Instructions

### Phase 1: Database Setup

1. **Install Dependencies**
   ```bash
   npm install drizzle-orm pg @auth/drizzle-adapter better-auth
   npm install -D drizzle-kit
   ```

2. **Configure Drizzle**
   - Create `drizzle.config.ts`
   - Set up database connection
   - Define schema with Better Auth tables

3. **Generate and Run Migrations**
   ```bash
   npx drizzle-kit generate
   npx drizzle-kit migrate
   ```

### Phase 2: Backend Setup (NestJS)

1. **Create Database Module**
   - Set up Drizzle connection
   - Provide database service

2. **Configure Better Auth**
   - Create auth instance with Drizzle adapter
   - Configure providers (GitHub, Google, etc.)
   - Set up session management

3. **Create Auth Module**
   - Auth controller with endpoints
   - Auth service with business logic
   - Auth guard for protection

### Phase 3: Frontend Setup (Next.js)

1. **Configure Auth Client**
   - Set up Better Auth client
   - Configure server actions

2. **Create Auth Pages**
   - Sign in page
   - Sign up page
   - Error handling

3. **Add Middleware**
   - Protect routes
   - Handle redirects

### Phase 4: Advanced Features

1. **Social Providers**
   - Configure OAuth apps
   - Add provider callbacks

2. **Plugins**
   - Two-Factor Authentication (2FA)
   - Organizations
   - SSO
   - Magic Links
   - Passkeys

## Examples

See [references/examples.md](./references/examples.md) for detailed implementation examples including:

- Complete NestJS Auth Setup
- Next.js Middleware for Route Protection
- Server Component with Session
- Two-Factor Authentication
- Passkey Authentication
- Backup Codes for 2FA Recovery

## Best Practices

See [references/best-practices.md](./references/best-practices.md) for comprehensive best practices including:

- Environment variable security
- Secret generation
- Session security
- Rate limiting
- CSRF protection
- Type safety guidelines

## Constraints and Warnings

See [references/best-practices.md](./references/best-practices.md#constraints-and-warnings) for:

- Security notes (secrets, HTTPS, OAuth)
- Known limitations
- Troubleshooting guide

## References

For detailed implementation guidance, see the reference files:

| Reference | Description |
|-----------|-------------|
| [examples.md](./references/examples.md) | Detailed implementation examples (8 scenarios) |
| [patterns.md](./references/patterns.md) | Common patterns, version requirements, environment variables |
| [best-practices.md](./references/best-practices.md) | Security guidelines, troubleshooting, constraints |
| [nestjs-setup.md](./references/nestjs-setup.md) | Complete NestJS backend setup guide |
| [nextjs-setup.md](./references/nextjs-setup.md) | Complete Next.js frontend setup guide |
| [mfa-2fa.md](./references/mfa-2fa.md) | Multi-factor authentication details |
| [passkey.md](./references/passkey.md) | Passkey authentication setup |
| [plugins.md](./references/plugins.md) | Plugin configuration guide |
| [schema.md](./references/schema.md) | Database schema reference |
| [social-providers.md](./references/social-providers.md) | OAuth provider setup |

## Resources

### Documentation

- [Better Auth Documentation](https://www.better-auth.com)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [NestJS Documentation](https://docs.nestjs.com)
- [Next.js App Router Documentation](https://nextjs.org/docs/app)

### Example Files

See `assets/` directory for example code files and environment templates.
