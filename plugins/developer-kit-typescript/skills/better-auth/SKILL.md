---
name: better-auth
description: Provides Better Auth authentication integration patterns for NestJS backend and Next.js frontend with Drizzle ORM and PostgreSQL. Use when implementing authentication - Setting up Better Auth with NestJS backend, Integrating Next.js App Router frontend, Configuring Drizzle ORM schema with PostgreSQL, Implementing social login (GitHub, Google, etc.), Adding plugins (2FA, Organization, SSO, Magic Link, Passkey), Email/password authentication with session management, Creating protected routes and middleware
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
category: backend
tags: [authentication, better-auth, nestjs, nextjs, drizzle, postgresql, oauth, sso, 2fa]
---

# Better Auth Integration Guide

## Overview

Better Auth is a comprehensive authentication framework for TypeScript with type-safe authentication, multiple providers, 2FA, SSO, organizations, and more. This skill covers NestJS backend with Drizzle ORM/PostgreSQL and Next.js App Router frontend integration.

## When to Use

- Setting up Better Auth with NestJS backend
- Integrating Next.js App Router frontend with Better Auth
- Configuring Drizzle ORM schema with PostgreSQL for authentication
- Implementing social login (GitHub, Google, Facebook, Microsoft, etc.)
- Adding MFA/2FA with TOTP, passkeys (WebAuthn), or backup codes
- Adding plugins (2FA, Organization, SSO, Magic Link, Passkey)
- Email/password authentication with secure session management
- Creating protected routes and authentication middleware

## Instructions

### Phase 1: Database Setup
1. Install: `npm install better-auth @auth/drizzle-adapter drizzle-orm pg`
2. Configure Drizzle with Better Auth tables schema
3. Generate and run migrations: `npx drizzle-kit generate && npx drizzle-kit migrate`

### Phase 2: Backend (NestJS)
1. Create Database Module with Drizzle connection
2. Configure Better Auth instance with Drizzle adapter and providers
3. Create Auth Module (controller, service, guard)

### Phase 3: Frontend (Next.js)
1. Configure Better Auth client
2. Create auth pages (sign-in, sign-up)
3. Add middleware for protected routes

### Phase 4: Advanced Features
1. Social providers (OAuth apps)
2. Plugins: 2FA, Organizations, SSO, Magic Links, Passkeys

## Examples

### NestJS Auth Setup

```typescript
export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg", schema: { ...schema } }),
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }
  }
});

@Controller('auth')
export class AuthController {
  @All('*')
  async handleAuth(@Req() req: Request, @Res() res: Response) {
    return auth.handler(req);
  }
}
```

### Next.js Server Component with Session

```typescript
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();
  if (!session) redirect('/sign-in');
  return <div>Welcome, {session.user.name}</div>;
}
```

### Session Management

```typescript
// API route: await auth.api.getSession({ headers: await headers() });
// Server Component: const session = await auth();
// Client Component: const { data: session } = useSession();
```

## Constraints and Warnings

- **Never commit secrets**: Add `.env` to `.gitignore`
- **HTTPS required**: OAuth callbacks require HTTPS in production
- **Passkeys**: Require HTTPS and compatible browsers
- Better Auth requires Node.js 18+
- Always implement email verification for password-based auth
- Keep OAuth client secrets secure and rotate periodically

## Best Practices

1. Use environment variables for all sensitive data
2. Generate strong secrets: `openssl rand -base64 32`
3. Configure appropriate session expiration times
4. Add indexes on frequently queried fields (email, userId)
5. Implement rate limiting on auth endpoints
6. Leverage TypeScript types from Better Auth for full type safety

## References

Consult these files for detailed patterns:

- **[references/nestjs-setup.md](references/nestjs-setup.md)** - Complete NestJS backend setup
- **[references/nextjs-setup.md](references/nextjs-setup.md)** - Complete Next.js frontend setup
- **[references/PLUGINS.md](references/PLUGINS.md)** - Plugin configurations (2FA, Org, SSO, Magic Link)
- **[references/SCHEMA.md](references/SCHEMA.md)** - Database schema with Better Auth tables
- **[references/mfa-2fa.md](references/mfa-2fa.md)** - Multi-factor authentication patterns
- **[references/passkey.md](references/passkey.md)** - Passkey/WebAuthn authentication
- **[references/social-providers.md](references/social-providers.md)** - Social provider configurations

### External References
- [Better Auth Documentation](https://www.better-auth.com)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
