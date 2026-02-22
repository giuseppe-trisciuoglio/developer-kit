---
name: nextjs-authentication
version: 2.2.0
description: Provides authentication implementation patterns for Next.js 15+ App Router using Auth.js 5 (NextAuth.js). Use when setting up authentication flows, implementing protected routes, managing sessions in Server Components and Server Actions, configuring OAuth providers, implementing role-based access control, or handling sign-in/sign-out flows in Next.js applications.
allowed-tools: Read, Write, Edit, Bash
category: frontend
tags: [nextjs, auth.js, nextauth, authentication, oauth, rbac]
---

# Next.js Authentication

## Overview

Authentication patterns for Next.js 15+ applications using App Router and Auth.js 5. Covers the complete authentication lifecycle from setup to production-ready RBAC.

## When to Use

- Setting up Auth.js 5 (NextAuth.js) from scratch
- Implementing protected routes with Middleware
- Handling authentication in Server Components and Server Actions
- Configuring OAuth providers (Google, GitHub, Discord, etc.)
- Implementing role-based access control (RBAC)
- Managing sessions with JWT or database strategy

## Instructions

1. **Install**: `npm install next-auth@beta`
2. **Configure env**: Set `AUTH_SECRET`, `AUTH_URL`, and provider credentials
3. **Create auth.ts**: Configure providers, callbacks, and custom pages
4. **Create API route**: `app/api/auth/[...nextauth]/route.ts`
5. **Add Middleware**: Protect routes with `middleware.ts`
6. **Access Session**: Use `auth()` in Server Components
7. **Secure Actions**: Always verify auth in Server Actions before mutations

## Examples

### Auth Configuration

```typescript
// auth.ts
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";

export const { handlers: { GET, POST }, auth, signIn, signOut } = NextAuth({
  providers: [GitHub({ clientId: process.env.GITHUB_ID!, clientSecret: process.env.GITHUB_SECRET! })],
  callbacks: {
    async jwt({ token, user }) { if (user) token.id = user.id; return token; },
    async session({ session, token }) { if (token) session.user.id = token.id as string; return session; },
  },
  pages: { signIn: "/login" },
});
```

### Middleware for Route Protection

```typescript
// middleware.ts
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  if (!isLoggedIn && req.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", req.nextUrl));
  }
  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
```

### Session in Server Components

```tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();
  if (!session) redirect("/login");
  return <h1>Welcome, {session.user.name}</h1>;
}
```

### Secure Server Actions

```tsx
"use server";
import { auth } from "@/auth";

export async function createTodo(formData: FormData) {
  const session = await auth();
  if (!session?.user) throw new Error("Unauthorized");
  // Proceed with protected action
}
```

## Constraints and Warnings

- **Middleware runs on Edge runtime** - Cannot use Node.js APIs like database drivers
- **Server Components cannot set cookies** - Use Server Actions for cookie operations
- Always verify authentication in Server Actions - middleware alone is not enough
- Use `unauthorized()` for unauthenticated access, `redirect()` for other cases

## Best Practices

1. Use Server Components by default for session access
2. Minimize Client Components - only use `useSession()` for reactive updates
3. Treat Server Actions like API endpoints - always authenticate before mutations
4. Never hardcode secrets - use environment variables
5. Extend NextAuth types for custom fields (role, id)

## References

Consult these files for detailed patterns:

- **[references/authjs-setup.md](references/authjs-setup.md)** - Complete Auth.js 5 setup with Prisma/Drizzle adapters
- **[references/oauth-providers.md](references/oauth-providers.md)** - Provider-specific configurations
- **[references/database-adapter.md](references/database-adapter.md)** - Database session management
- **[references/testing-patterns.md](references/testing-patterns.md)** - Testing authentication flows
