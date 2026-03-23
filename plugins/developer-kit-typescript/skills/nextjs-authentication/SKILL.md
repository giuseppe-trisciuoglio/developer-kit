---
name: nextjs-authentication
description: Provides authentication implementation patterns for Next.js 15+ App Router using Auth.js 5 (NextAuth.js). Use when setting up authentication flows, implementing protected routes, managing sessions in Server Components and Server Actions, configuring OAuth providers, implementing role-based access control, or handling sign-in/sign-out flows in Next.js applications.
allowed-tools: Read, Write, Edit, Bash
---

# Next.js Authentication

## Overview

This skill provides comprehensive authentication patterns for Next.js 15+ applications using the App Router architecture and Auth.js 5. It covers the complete authentication lifecycle from initial setup to production-ready implementations with role-based access control.

Key capabilities include:
- Auth.js 5 setup with Next.js App Router
- Protected routes using Middleware
- Session management in Server Components
- Authentication checks in Server Actions
- OAuth provider integration (GitHub, Google, etc.)
- Role-based access control (RBAC)
- JWT and database session strategies

## When to Use

Use this skill when implementing authentication for Next.js 15+ with App Router:

- Setting up Auth.js 5 (NextAuth.js) from scratch
- Implementing protected routes with Middleware
- Handling authentication in Server Components
- Securing Server Actions with auth checks
- Configuring OAuth providers (Google, GitHub, Discord, etc.)
- Implementing role-based access control (RBAC)
- Managing sessions with JWT or database strategy
- Creating credential-based authentication
- Handling sign-in/sign-out flows

## Instructions

### 1. Install Dependencies

Install Auth.js v5 (beta) for Next.js App Router:

```bash
npm install next-auth@beta
```

### 2. Configure Environment Variables

Create `.env.local` with required variables:

```bash
# Required for Auth.js
AUTH_SECRET="your-secret-key-here"
AUTH_URL="http://localhost:3000"

# OAuth Providers (add as needed)
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

Generate `AUTH_SECRET` with:
```bash
openssl rand -base64 32
```

### 3. Create Auth Configuration

Create `auth.ts` in the project root with providers and callbacks:

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
  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/error",
  },
});
```

### 4. Create API Route Handler

Create `app/api/auth/[...nextauth]/route.ts`:

```typescript
export { GET, POST } from "@/auth";
```

### 5. Add Middleware for Route Protection

Create `middleware.ts` in the project root:

```typescript
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { nextUrl } = req;
  const isLoggedIn = !!req.auth;
  const isApiAuthRoute = nextUrl.pathname.startsWith("/api/auth");
  const isPublicRoute = ["/", "/login", "/register"].includes(nextUrl.pathname);
  const isProtectedRoute = nextUrl.pathname.startsWith("/dashboard");

  if (isApiAuthRoute) return NextResponse.next();

  if (!isLoggedIn && isProtectedRoute) {
    return NextResponse.redirect(new URL("/login", nextUrl));
  }

  if (isLoggedIn && nextUrl.pathname === "/login") {
    return NextResponse.redirect(new URL("/dashboard", nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
```

### 6. Access Session in Server Components

Use the `auth()` function to access session in Server Components:

```tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect("/login");
  }

  return (
    <div>
      <h1>Welcome, {session.user.name}</h1>
    </div>
  );
}
```

### 7. Secure Server Actions

Always verify authentication in Server Actions before mutations:

```tsx
"use server";

import { auth } from "@/auth";

export async function createTodo(formData: FormData) {
  const session = await auth();

  if (!session?.user) {
    throw new Error("Unauthorized");
  }

  // Proceed with protected action
  const title = formData.get("title") as string;
  await db.todo.create({
    data: { title, userId: session.user.id },
  });
}
```

### 8. Handle Sign-In/Sign-Out

Create a login page with server action:

```tsx
// app/login/page.tsx
import { signIn } from "@/auth";
import { redirect } from "next/navigation";

export default function LoginPage() {
  async function handleLogin(formData: FormData) {
    "use server";

    const result = await signIn("credentials", {
      email: formData.get("email"),
      password: formData.get("password"),
      redirect: false,
    });

    if (result?.error) {
      return { error: "Invalid credentials" };
    }

    redirect("/dashboard");
  }

  return (
    <form action={handleLogin}>
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

For client-side sign-out:

```tsx
"use client";

import { signOut } from "next-auth/react";

export function SignOutButton() {
  return <button onClick={() => signOut()}>Sign Out</button>;
}
```

### 9. Implement Role-Based Access

Check roles in Server Components:

```tsx
import { auth } from "@/auth";
import { unauthorized } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();

  if (session?.user?.role !== "admin") {
    unauthorized();
  }

  return <AdminDashboard />;
}
```

### 10. Extend TypeScript Types

Create `types/next-auth.d.ts` for type-safe sessions:

```typescript
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role: "user" | "admin";
    } & DefaultSession["user"];
  }

  interface User {
    role?: "user" | "admin";
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    role?: "user" | "admin";
  }
}
```

## Constraints and Warnings

- Middleware runs on Edge runtime - cannot use Node.js database drivers
- Server Components cannot set cookies - use Server Actions instead
- Always verify authentication in Server Actions, not just middleware
- See [references/best-practices.md](references/best-practices.md) for complete security guidelines

## Examples

See [references/examples.md](references/examples.md) for comprehensive code examples:
- Complete protected dashboard
- Role-based admin panel
- Secure Server Action with form
- OAuth sign-in button
- Credentials provider login

## Best Practices

See [references/best-practices.md](references/best-practices.md) for detailed guidance on:
- Server Components vs Client Components
- Security considerations
- Common mistakes to avoid
- Performance optimization tips

## References

- [references/authjs-setup.md](references/authjs-setup.md) - Complete Auth.js 5 setup guide with Prisma/Drizzle adapters
- [references/oauth-providers.md](references/oauth-providers.md) - Provider-specific configurations (GitHub, Google, Discord, Auth0, etc.)
- [references/database-adapter.md](references/database-adapter.md) - Database session management with Prisma, Drizzle, and custom adapters
- [references/testing-patterns.md](references/testing-patterns.md) - Testing authentication flows with Vitest and Playwright
- [references/examples.md](references/examples.md) - Comprehensive code examples
- [references/best-practices.md](references/best-practices.md) - Best practices and security guidelines
