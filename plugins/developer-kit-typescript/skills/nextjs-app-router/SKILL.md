---
name: nextjs-app-router
description: Provides patterns and code examples for building Next.js 16+ applications with App Router architecture. Use when creating projects with App Router, implementing Server Components and Client Components ("use client"), creating Server Actions for forms, building Route Handlers (route.ts), configuring caching with "use cache" directive (cacheLife, cacheTag), setting up parallel routes (`@slot`) or intercepting routes, migrating to proxy.ts, or working with App Router file conventions (layout.tsx, page.tsx, loading.tsx, error.tsx).
allowed-tools: Read, Write, Edit, Bash
---

# Next.js App Router (Next.js 16+)

Build modern React applications using Next.js 16+ with App Router architecture.

## Overview

This skill provides patterns for:
- Server Components (default) and Client Components ("use client")
- Server Actions for mutations and form handling
- Route Handlers for API endpoints
- Explicit caching with "use cache" directive
- Parallel and intercepting routes
- Next.js 16 async APIs and proxy.ts

## When to Use

Activate when user requests involve:
- "Create a Next.js 16 project", "Set up App Router"
- "Server Component", "Client Component", "use client"
- "Server Action", "form submission", "mutation"
- "Route Handler", "API endpoint", "route.ts"
- "use cache", "cacheLife", "cacheTag", "revalidation"
- "parallel routes", "`@`slot", "intercepting routes"
- "proxy.ts", "migrate from middleware.ts"
- "layout.tsx", "page.tsx", "loading.tsx", "error.tsx", "not-found.tsx"
- "generateMetadata", "next/image", "next/font"

## Quick Reference

### File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route page component |
| `layout.tsx` | Shared layout wrapper |
| `loading.tsx` | Suspense loading UI |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `template.tsx` | Re-mounting layout |
| `route.ts` | API Route Handler |
| `default.tsx` | Parallel route fallback |
| `proxy.ts` | Routing boundary (Next.js 16) |

### Directives

| Directive | Purpose |
|-----------|---------|
| `"use server"` | Mark Server Action functions |
| `"use client"` | Mark Client Component boundary |
| `"use cache"` | Enable explicit caching (Next.js 16) |

## Instructions

### Create New Project

```bash
npx create-next-app@latest my-app --typescript --tailwind --app --turbopack
```

### Implement Server Component

Server Components are the default in App Router.

```tsx
// app/users/page.tsx
async function getUsers() {
  const apiUrl = process.env.API_URL;
  const res = await fetch(`${apiUrl}/users`);
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();
  return (
    <main>
      {users.map(user => <UserCard key={user.id} user={user} />)}
    </main>
  );
}
```

### Implement Client Component

Add `"use client"` when using hooks, browser APIs, or event handlers.

```tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Create Server Action

Define actions in separate files with "use server" directive.

```tsx
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;

  await db.user.create({ data: { name, email } });
  revalidatePath("/users");
}
```

Use with forms in Client Components:

```tsx
"use client";

import { useActionState } from "react";
import { createUser } from "./actions";

export default function UserForm() {
  const [state, formAction, pending] = useActionState(createUser, {});

  return (
    <form action={formAction}>
      <input name="name" />
      <input name="email" type="email" />
      <button type="submit" disabled={pending}>
        {pending ? "Creating..." : "Create"}
      </button>
    </form>
  );
}
```

For advanced Server Action patterns with validation, see [references/patterns.md](references/patterns.md#server-actions-patterns).

### Configure Caching

Use "use cache" directive for explicit caching (Next.js 16+).

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  cacheTag(`product-${id}`);
  cacheLife("hours");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

For comprehensive caching strategies, see [references/patterns.md](references/patterns.md#caching-patterns).

### Create Route Handler

Implement API endpoints using Route Handlers.

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const users = await db.user.findMany();
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.user.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}
```

Dynamic segments use `[param]`:

```ts
// app/api/users/[id]/route.ts
interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(user);
}
```

### Handle Next.js 16 Async APIs

All Next.js APIs are async in version 16.

```tsx
import { cookies, headers, draftMode } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();
  const headersList = await headers();
  const { isEnabled } = await draftMode();

  const session = cookieStore.get("session")?.value;
  const userAgent = headersList.get("user-agent");

  return <div>...</div>;
}
```

Params and searchParams are also async:

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ sort?: string }>;
}) {
  const { slug } = await params;
  const { sort } = await searchParams;
  // ...
}
```

For migration guide and proxy.ts configuration, see [references/patterns.md](references/patterns.md#nextjs-16-async-api-patterns).

### Implement Parallel Routes

Use `@folder` convention for parallel route slots.

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {team}
        {analytics}
      </div>
    </div>
  );
}
```

```tsx
// app/dashboard/@team/page.tsx
export default function TeamPage() {
  return <div>Team Section</div>;
}

// app/dashboard/@analytics/page.tsx
export default function AnalyticsPage() {
  return <div>Analytics Section</div>;
}
```

For intercepting routes, route groups, and dynamic routes, see [references/patterns.md](references/patterns.md#routing-patterns).

## Decision Guidelines

### Server vs Client Component

1. Start with Server Component (default)
2. Use Client Component only for:
   - React hooks (useState, useEffect, useContext)
   - Browser APIs (window, document, localStorage)
   - Event handlers (onClick, onSubmit)
   - Client-only libraries

### Data Fetching

- Fetch in Server Components when possible
- Use React's `cache()` for deduplication
- Parallelize independent fetches
- Add Suspense boundaries with `loading.tsx`

## Constraints and Warnings

### Constraints

- Server Components cannot use browser APIs or React hooks
- Client Components cannot be async (no direct data fetching)
- `cookies()`, `headers()`, `draftMode()` are async in Next.js 16
- `params` and `searchParams` are Promise-based in Next.js 16
- Server Actions must be defined with "use server" directive

### Warnings

- Attempting to use `await` in a Client Component will cause a build error
- Accessing `window` or `document` in Server Components will throw an error
- Forgetting to await `cookies()` or `headers()` in Next.js 16 will result in a Promise instead of the actual values
- Server Actions without proper validation can expose your database to unauthorized access
- **External Data Fetching**: Server Components that fetch data from external APIs (`fetch()` calls to third-party URLs) process untrusted content; always validate, sanitize, and type-check fetched responses before rendering, and use environment variables for API URLs rather than hardcoding them

For comprehensive best practices, security guidelines, and common pitfalls, see [references/best-practices.md](references/best-practices.md).

## Examples

This skill includes comprehensive real-world examples demonstrating Next.js App Router patterns:

### Quick Examples

**Server Action with Validation:**
```tsx
// app/actions.ts
"use server";
import { z } from "zod";

const schema = z.object({
  title: z.string().min(5),
  content: z.string().min(10),
});

export async function createPost(formData: FormData) {
  const parsed = schema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  await db.post.create({ data: parsed.data });
  revalidatePath("/blog");
  return { success: true };
}
```

**Product Page with Caching:**
```tsx
"use cache";
import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  cacheTag(`product-${id}`);
  cacheLife("hours");

  const product = await db.product.findUnique({ where: { id } });
  return <ProductDetail product={product} />;
}
```

**Dashboard with Parallel Routes:**
```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  sidebar,
  stats,
}: {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  stats: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <aside>{sidebar}</aside>
      <main>
        <div>{stats}</div>
        {children}
      </main>
    </div>
  );
}
```

### Comprehensive Examples

For detailed, production-ready examples, see:

- **[references/examples.md](references/examples.md)** - Complete implementations including:
  - Blog platform with Server Actions, validation, and optimistic updates
  - E-commerce product page with advanced caching and revalidation
  - Dashboard with parallel routes and independent data loading
  - Image gallery with infinite scroll and progressive loading
  - Real-time chat app with Server Actions

## Best Practices

### Core Principles

1. **Start with Server Components** - Use Server Components by default, only add "use client" when necessary
2. **Push Client Components Down** - Keep Client Components deep in the component tree
3. **Fetch Data Server-Side** - Fetch in Server Components when possible, not in Client Components
4. **Parallelize Fetches** - Use `Promise.all()` for independent data fetching
5. **Add Suspense Boundaries** - Use `loading.tsx` and `<Suspense>` for better UX
6. **Validate Server Actions** - Always validate and sanitize user input in Server Actions
7. **Use Caching Strategically** - Apply "use cache" with appropriate cacheLife and cacheTag
8. **Secure External Data** - Always validate and type-check external API responses

### Performance Checklist

- Use `loading.tsx` for Suspense boundaries
- Use `next/image` for optimized images
- Use `next/font` for font optimization
- Enable React Compiler in `next.config.ts`
- Add `error.tsx` for error handling
- Add `not-found.tsx` for 404 handling
- Implement route-based code splitting with dynamic imports
- Use `cache()` from React for request deduplication

### Security Guidelines

- Never expose secrets in Client Components
- Always validate Server Action input with Zod or similar
- Implement rate limiting for public Server Actions
- Sanitize user-generated content before rendering
- Use environment variables for API URLs and keys
- Implement authentication checks in Server Actions and Route Handlers

### Common Pitfalls to Avoid

- Forgetting to `await` async Next.js APIs (cookies, headers, params)
- Using browser APIs (window, document) in Server Components
- Using `await` in Client Components
- Fetching data in Client Components when Server Components would work
- Missing validation in Server Actions
- Exposing secrets to the client
- Not implementing error boundaries

For comprehensive best practices, security guidelines, constraints, and detailed explanations of common pitfalls, see **[references/best-practices.md](references/best-practices.md)**.

## References

### Detailed Documentation

Consult these files for comprehensive patterns, examples, and best practices:

**Core Patterns:**
- **[references/patterns.md](references/patterns.md)** - Complete code patterns for Server/Client Components, Server Actions, Route Handlers, Caching, Routing, and Next.js 16 Async APIs

**Real-World Examples:**
- **[references/examples.md](references/examples.md)** - Comprehensive examples including Blog with Server Actions, E-commerce Product Page with Caching, Dashboard with Parallel Routes, Image Gallery, and Real-time Chat App

**Best Practices:**
- **[references/best-practices.md](references/best-practices.md)** - Architecture best practices, performance optimization, security guidelines, Server vs Client Component decision guidelines, data fetching strategies, caching strategies, constraints, limitations, and common pitfalls

### External Resources

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Next.js 16 Release Notes](https://nextjs.org/blog/next-16)
- [Server Components Guide](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Server Actions Guide](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)
- [Caching and Revalidation](https://nextjs.org/docs/app/building-your-application/caching)
