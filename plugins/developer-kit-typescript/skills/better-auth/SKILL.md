---
name: better-auth
description: This skill should be used when the user asks to "set up Better Auth", "integrate Better Auth with NestJS", "configure Better Auth in Next.js App Router", "add 2FA/passkeys/SSO with Better Auth", or "build Drizzle/PostgreSQL auth schema and protected routes" for a TypeScript stack.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
category: backend
tags: [authentication, better-auth, nestjs, nextjs, drizzle, postgresql, oauth, sso, 2fa]
---

# Better Auth Integration Guide

## Overview

Better Auth is a TypeScript authentication framework with email/password, social providers, session management, and advanced plugins (2FA, passkey, organizations, SSO, magic links). This skill provides integration patterns for:
- NestJS backend
- Next.js App Router frontend
- Drizzle ORM + PostgreSQL schema/migrations

Keep `SKILL.md` concise and use `references/` and `assets/` for full implementations.

## When to Use

- New project setup for Better Auth in NestJS + Next.js
- Migration from custom auth to Better Auth
- Drizzle schema and migrations for auth tables
- Social login onboarding (GitHub, Google, Microsoft, Facebook)
- MFA rollout (TOTP, backup codes, trusted devices) or passkeys
- Protected routes and session-aware middleware in App Router
- Multi-tenant organization/SSO plugin integration

## Instructions

### Phase 1: Database Setup
1. Install core dependencies:
   - `npm install better-auth drizzle-orm pg`
   - `npm install -D drizzle-kit`
2. Define Better Auth tables in Drizzle schema.
3. Generate and run migrations:
   - `npx drizzle-kit generate`
   - `npx drizzle-kit migrate`
4. Confirm required env vars from `assets/env.example`.

### Phase 2: Backend (NestJS)
1. Create Database module/service (see `assets/nestjs/database.module.ts` and `assets/nestjs/database.service.ts`).
2. Configure Better Auth instance with Drizzle adapter and providers.
3. Expose auth endpoints and guard protected controllers.
4. Ensure request handling is compatible with Better Auth:
   - disable Nest body parser where needed
   - forward raw auth requests to Better Auth handler pattern

### Phase 3: Frontend (Next.js)
1. Configure auth client in `lib/auth`.
2. Mount Better Auth route handler (`app/api/auth/[...auth]/route.ts`).
3. Create sign-in/sign-up pages.
4. Protect server components and routes via middleware/session checks.

### Phase 4: Advanced Features
1. Add social providers and callback URLs.
2. Enable plugins incrementally:
   - 2FA (TOTP + backup codes)
   - Passkey (WebAuthn)
   - Organization + SSO
   - Magic link
3. Validate each flow end-to-end before enabling the next plugin.

### Phase 5: Verification
1. Test sign-up/sign-in/sign-out/session refresh.
2. Test at least one social provider callback.
3. Test unauthorized route access and redirect behavior.
4. Test one recovery path (backup codes or password reset).

## Examples

### NestJS Auth Setup

Input: "Expose Better Auth on a NestJS app with PostgreSQL."

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { toNodeHandler } from "better-auth/node";
import { db } from "@/db";
import * as schema from "@/db/schema";

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
  private readonly handler = toNodeHandler(auth);

  @All('*')
  async handleAuth(@Req() req: Request, @Res() res: Response) {
    return this.handler(req, res);
  }
}
```

Output: Backend auth endpoints are served from `/auth/*` using the Better Auth instance.

### Next.js Server Component with Session

Input: "Protect dashboard page in App Router."

```typescript
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();
  if (!session) redirect('/sign-in');
  return <div>Welcome, {session.user.name}</div>;
}
```

Output: Unauthenticated users are redirected to `/sign-in`; authenticated users get dashboard content.

### Session Management

Input: "Read session across API/server/client surfaces."

```typescript
// API route: await auth.api.getSession({ headers: await headers() });
// Server Component: const session = await auth();
// Client Component: const { data: session } = useSession();
```

Output: Consistent session access patterns for API routes, server components, and client components.

## Constraints and Warnings

- **Never commit secrets**: Add `.env` to `.gitignore`
- **HTTPS required**: OAuth callbacks require HTTPS in production
- **Passkeys**: Require HTTPS and compatible browsers
- Verify runtime version requirements for your stack (for example, Next.js 14+ requires Node.js 18.17+)
- Always implement email verification for password-based auth
- Keep OAuth client secrets secure and rotate periodically
- Validate callback URLs to avoid open redirect issues
- Add rate limiting on auth endpoints to mitigate brute-force attempts

## Best Practices

1. Use environment variables for all sensitive data
2. Generate strong secrets: `openssl rand -base64 32`
3. Configure appropriate session expiration times
4. Add indexes on frequently queried fields (email, userId)
5. Implement rate limiting on auth endpoints
6. Leverage TypeScript types from Better Auth for full type safety
7. Keep `SKILL.md` concise; move deep implementation details to `references/`
8. Reuse `assets/` snippets instead of rewriting auth primitives from scratch

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
