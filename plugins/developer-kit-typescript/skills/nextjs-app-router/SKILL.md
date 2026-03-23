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

### Server vs Client Components

**Server Components** (default):
- Run only on the server
- Cannot use hooks or browser APIs
- Direct database access
- Better performance

```tsx
// app/users/page.tsx (Server Component)
export default async function UsersPage() {
  const users = await db.user.findMany();
  return <UserList users={users} />;
}
```

**Client Components** (add `"use client"`):
- Use hooks (useState, useEffect)
- Browser APIs (window, localStorage)
- Event handlers (onClick, onSubmit)

```tsx
// components/Counter.tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

### Server Actions

Define actions in separate files with "use server" directive:

```tsx
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string;
  await db.user.create({ data: { name } });
  revalidatePath("/users");
}
```

Use with forms:

```tsx
"use client";

import { useActionState } from "react";
import { createUser } from "./actions";

export default function UserForm() {
  const [state, formAction, pending] = useActionState(createUser, {});
  return <form action={formAction}><input name="name" /><button disabled={pending}>Create</button></form>;
}
```

See [references/server-actions.md](references/server-actions.md) for validation with Zod, optimistic updates, and advanced patterns.

### Route Handlers

Implement API endpoints:

```tsx
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

Dynamic segments:

```tsx
// app/api/users/[id]/route.ts
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });
  return NextResponse.json(user);
}
```

### Caching with "use cache"

Use "use cache" directive for explicit caching (Next.js 16+):

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  cacheTag(`product-${id}`);
  cacheLife("hours");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

See [references/caching-strategies.md](references/caching-strategies.md) for cache profiles, on-demand revalidation, and advanced caching patterns.

### Next.js 16 Async APIs

All Next.js APIs are async in version 16:

```tsx
import { cookies, headers, draftMode } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();
  const headersList = await headers();
  const { isEnabled } = await draftMode();

  const session = cookieStore.get("session")?.value;
  return <div>...</div>;
}
```

Params and searchParams are also async:

```tsx
export default async function Page({ params, searchParams }: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ sort?: string }>;
}) {
  const { slug } = await params;
  const { sort } = await searchParams;
}
```

See [references/nextjs16-migration.md](references/nextjs16-migration.md) for migration guide and proxy.ts configuration.

### Parallel Routes

Use `@folder` convention for parallel route slots:

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children, team, analytics }: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return <div>{children}<div className="grid grid-cols-2">{team}{analytics}</div></div>;
}
```

```tsx
// app/dashboard/@team/page.tsx
export default function TeamPage() {
  return <div>Team Section</div>;
}
```

See [references/routing-patterns.md](references/routing-patterns.md) for intercepting routes, route groups, and dynamic routes.

## Examples

For complete, real-world examples, see **[references/examples.md](references/examples.md)**:

- **Blog System**: Complete blog with Server Actions, Zod validation, form handling, and revalidation
- **E-commerce**: Product catalog with caching, shopping cart, and revalidation endpoints
- **Dashboard**: Parallel routes implementation with sidebar, stats, and main content areas
- **Authentication**: Login/logout flow with Server Actions and secure session management
- **Search & Filtering**: Search page with server-side filtering and URL-based query params

Each example includes production-ready code with error handling, validation, and best practices.

## Best Practices

For comprehensive best practices, see **[references/best-practices.md](references/best-practices.md)**:

- **Architecture**: Server vs Client decision tree, component composition, prop passing patterns
- **Data Fetching**: Server-side fetching, cache() for deduplication, parallel fetching, Suspense boundaries
- **Server Actions**: Input validation with Zod, consistent response shapes, revalidation strategies
- **Caching**: Appropriate cache durations, on-demand revalidation patterns
- **Route Handlers**: External API proxying, input validation, error handling
- **File Organization**: Route groups, parallel routes, Server Actions organization
- **Error Handling**: Error boundaries, not-found handling, global error handlers
- **Performance**: Loading states, image optimization, font optimization, React Compiler
- **Security**: Input validation, environment variables, secure Server Actions, protected routes
- **Testing**: Server Action testing, Route Handler testing
- **Deployment**: Environment variables, production optimizations, performance monitoring

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

## References

Consult these files for detailed patterns:

- **[references/patterns.md](references/patterns.md)** - Comprehensive code patterns for Server/Client Components, Route Handlers, async APIs, caching, parallel routes, integration patterns, file organization, error handling, and performance
- **[references/examples.md](references/examples.md)** - Complete real-world examples including blog with Server Actions, e-commerce with caching, dashboard with parallel routes, authentication flow, and search/filtering
- **[references/best-practices.md](references/best-practices.md)** - Architecture patterns, data fetching, Server Actions, caching strategies, route handlers, file organization, error handling, performance optimization, security, testing, deployment, and common pitfalls

### Additional Resources

- **[references/app-router-fundamentals.md](references/app-router-fundamentals.md)** - Server/Client Components, file conventions, navigation, next/image, next/font
- **[references/routing-patterns.md](references/routing-patterns.md)** - Parallel routes, intercepting routes, route groups, dynamic routes
- **[references/caching-strategies.md](references/caching-strategies.md)** - "use cache", cacheLife, cacheTag, revalidation
- **[references/server-actions.md](references/server-actions.md)** - Server Actions, useActionState, validation, optimistic updates
- **[references/nextjs16-migration.md](references/nextjs16-migration.md)** - Async APIs, proxy.ts, Turbopack, config
- **[references/data-fetching.md](references/data-fetching.md)** - Data patterns, Suspense, streaming
- **[references/metadata-api.md](references/metadata-api.md)** - generateMetadata, OpenGraph, sitemap
