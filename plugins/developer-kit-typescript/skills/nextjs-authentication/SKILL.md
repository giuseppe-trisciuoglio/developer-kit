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

This skill provides production-ready authentication patterns for Next.js 15+ with App Router and Auth.js 5.

Key capabilities include:
- Auth.js 5 setup for App Router
- Middleware-based route protection
- Session access in Server Components
- Auth checks in Server Actions
- OAuth provider integration and credentials patterns
- Role-based access control (RBAC)
- JWT and database session strategies
- Testing guidance and security constraints

## When to Use

- Trigger phrase: "implement auth in nextjs app router"
- Trigger phrase: "protect routes and server actions with auth.js"
- Setting up Auth.js 5 (NextAuth.js) from scratch
- Implementing protected routes with Middleware
- Handling authentication in Server Components and Server Actions
- Configuring OAuth providers (Google, GitHub, Discord, etc.)
- Implementing role-based access control (RBAC)
- Managing sessions with JWT or database strategy
- Creating sign-in/sign-out flows
- Extending session/JWT types for custom fields

## Instructions

1. Install dependencies:
```bash
npm install next-auth@beta
```

2. Configure environment variables (recommended Auth.js naming):
```bash
# .env.local
AUTH_SECRET=your-random-secret-at-least-32-characters
AUTH_TRUST_HOST=true

AUTH_GITHUB_ID=your-github-client-id
AUTH_GITHUB_SECRET=your-github-client-secret
AUTH_GOOGLE_ID=your-google-client-id
AUTH_GOOGLE_SECRET=your-google-client-secret
```
Generate `AUTH_SECRET` with:
```bash
npx auth secret
```

3. Create `auth.ts` in project root:
```typescript
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  providers: [GitHub, Google],
  callbacks: {
    async jwt({ token, user }) {
      if (user) token.id = user.id;
      return token;
    },
    async session({ session, token }) {
      if (token?.id) session.user.id = token.id as string;
      return session;
    },
  },
  pages: { signIn: "/login" },
});
```

4. Create API route handler:
```typescript
// app/api/auth/[...nextauth]/route.ts
export { GET, POST } from "@/auth";
```

5. Add middleware for route protection:
```typescript
// middleware.ts
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isDashboardRoute = req.nextUrl.pathname.startsWith("/dashboard");

  if (!isLoggedIn && isDashboardRoute) {
    return NextResponse.redirect(new URL("/login", req.nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
```

6. Access session in Server Components:
```tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user?.id) redirect("/login");

  return <h1>Welcome, {session.user.name}</h1>;
}
```

7. Protect Server Actions before data mutations:
```tsx
"use server";

import { auth } from "@/auth";

export async function createTodo(formData: FormData) {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Unauthorized");

  const title = formData.get("title") as string;
  await db.todo.create({ data: { title, userId: session.user.id } });
}
```

8. Implement sign-in/sign-out flows:
```tsx
// app/login/page.tsx
import { signIn } from "@/auth";

export default function LoginPage() {
  return (
    <form action={async () => {
      "use server";
      await signIn("github", { redirectTo: "/dashboard" });
    }}>
      <button type="submit">Sign in with GitHub</button>
    </form>
  );
}
```

9. Add RBAC checks in privileged routes:
```tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();
  if (session?.user?.role !== "admin") unauthorized();
  return <h1>Admin dashboard</h1>;
}
```

10. Extend NextAuth types for `id`/`role`:
```typescript
// types/next-auth.d.ts
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role?: "user" | "admin";
    } & DefaultSession["user"];
  }
}
```

## Examples

### Example 1: Protected Dashboard

**Input:** A dashboard page that must be accessible only to authenticated users.

```tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user?.id) redirect("/login");
  return <h1>Welcome, {session.user.name}</h1>;
}
```

**Output:** Unauthenticated users are redirected to `/login`; authenticated users see dashboard content.

### Example 2: Protected Server Action

**Input:** A form action that creates todos and must reject unauthenticated requests.

```tsx
"use server";
import { auth } from "@/auth";

export async function createTodo(formData: FormData) {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Unauthorized");

  await db.todo.create({
    data: {
      title: formData.get("title") as string,
      userId: session.user.id,
    },
  });
}
```

**Output:** Authorized users can create todos; unauthorized requests fail before mutation.

### Example 3: RBAC Admin Route

**Input:** A route that only admins can access.

```tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();
  if (session?.user?.role !== "admin") unauthorized();
  return <h1>Admin panel</h1>;
}
```

**Output:** Users without role `admin` receive an unauthorized response.

## Constraints and Warnings

- Middleware runs on Edge runtime: avoid direct Node.js DB drivers in middleware.
- Server Components cannot set cookies: use Server Actions or Route Handlers.
- Middleware checks are not sufficient alone: always verify in Server Actions and APIs.
- Keep callback logic deterministic: avoid expensive calls in `jwt`/`session` callbacks.
- Never expose provider secrets to client components.

## Best Practices

1. Use Server Components by default for session access.
2. Keep client auth UI minimal and rely on server-side auth checks for authorization.
3. Treat Server Actions like API endpoints and enforce auth before mutations.
4. Prefer provider environment variable inference (`AUTH_<PROVIDER>_ID/SECRET`).
5. Generate and rotate `AUTH_SECRET` securely.
6. Extend NextAuth session/JWT types for custom claims (`id`, `role`).
7. Use `redirect()` for navigation flows and `unauthorized()` for denied access.
8. Add integration tests for login redirects, RBAC, and action protection.

## References

Consult these files for detailed patterns:

- **[references/authjs-setup.md](references/authjs-setup.md)** - Complete Auth.js 5 setup with Prisma/Drizzle adapters
- **[references/oauth-providers.md](references/oauth-providers.md)** - Provider-specific configurations
- **[references/database-adapter.md](references/database-adapter.md)** - Database session management
- **[references/testing-patterns.md](references/testing-patterns.md)** - Testing authentication flows
