---
name: nextjs-app-router
description: Provides patterns and code examples for building Next.js 16+ applications with App Router architecture. Use when creating projects with App Router, implementing Server Components and Client Components ("use client"), creating Server Actions for forms, building Route Handlers (route.ts), configuring caching with "use cache" directive (cacheLife, cacheTag), setting up parallel routes (@slot) or intercepting routes, migrating to proxy.ts, or working with App Router file conventions (layout.tsx, page.tsx, loading.tsx, error.tsx).
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
- "parallel routes", "@slot", "intercepting routes"
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

### 1) Create a New Project

```bash
npx create-next-app@latest my-app --typescript --tailwind --app --turbopack
```

### 2) Build with Server Components First

Server Components are default in App Router:

```tsx
// app/users/page.tsx
export default async function UsersPage() {
  const users = await fetchUsers();
  return <main>{users.map(user => <UserCard key={user.id} user={user} />)}</main>;
}
```

Add `"use client"` only for hooks, browser APIs, or event handlers:

```tsx
"use client";
import { useState } from "react";
```

See [references/app-router-fundamentals.md](references/app-router-fundamentals.md) for boundary and composition patterns.

### 3) Add Server Actions for Mutations

```tsx
// app/users/actions.ts
"use server";
import { revalidatePath } from "next/cache";

export async function createUser(formData: FormData) {
  await db.user.create({ data: { name: String(formData.get("name")) } });
  revalidatePath("/users");
}
```

Use actions with `<form action={formAction}>` and `useActionState` in Client Components.
See [references/server-actions.md](references/server-actions.md) for validation, pending states, and optimistic updates.

### 4) Implement Route Handlers

```ts
// app/api/users/[id]/route.ts
export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json(await db.user.findUnique({ where: { id } }));
}
```

Use `route.ts` for API endpoints and await async `params`.
See [references/routing-patterns.md](references/routing-patterns.md) for dynamic and advanced routing.

### 5) Configure Caching and Revalidation

```tsx
"use cache";
import { cacheLife, cacheTag } from "next/cache";

cacheTag("products");
cacheLife("hours");
```

Use `revalidatePath`/`revalidateTag` after mutations.
See [references/caching-strategies.md](references/caching-strategies.md) for full strategy.

### 6) Handle Next.js 16 Async APIs

`cookies()`, `headers()`, `draftMode()`, `params`, and `searchParams` are async in Next.js 16:

```tsx
const cookieStore = await cookies();
const { slug } = await params;
```

See [references/nextjs16-migration.md](references/nextjs16-migration.md) for migration and `proxy.ts`.

### 7) Use Advanced App Router Features as Needed

- Parallel routes: `app/dashboard/@team/page.tsx`
- Intercepting routes: `(..)segment`
- Route groups: `(group-name)`

See [references/routing-patterns.md](references/routing-patterns.md) and [references/data-fetching.md](references/data-fetching.md) for complete patterns.

## Best Practices

### Server vs Client Decision

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

### Caching Strategy

```tsx
"use cache";
import { cacheLife, cacheTag } from "next/cache";

// Set cache duration
cacheLife("hours");

// Tag for revalidation
cacheTag("resource-name");
```

### Performance Checklist

- Use `loading.tsx` for Suspense boundaries
- Use `next/image` for optimized images
- Use `next/font` for font optimization
- Enable React Compiler in `next.config.ts`
- Add `error.tsx` for error handling
- Add `not-found.tsx` for 404 handling

## Examples

### Example 1: Server Action with Validation

**Input:** "Create a form submission flow with validation in App Router."

**Output:**

```tsx
// app/users/actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";

const schema = z.object({ name: z.string().min(2) });

export async function createUser(formData: FormData) {
  const parsed = schema.safeParse({ name: formData.get("name") });
  if (!parsed.success) return { errors: parsed.error.flatten().fieldErrors };

  await db.user.create({ data: parsed.data });
  revalidatePath("/users");
  return { success: true };
}
```

### Example 2: Cached Dynamic Page

**Input:** "Cache a dynamic product page and tag it for revalidation."

**Output:**

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

For a full set of examples (blog post with validation, cached product page, dashboard with parallel routes), see [references/examples.md](references/examples.md).

## Constraints and Warnings

- Server Components cannot use browser APIs or React hooks; Client Components cannot be async
- `cookies()`, `headers()`, `params`, `searchParams` are Promise-based in Next.js 16 - always `await` them
- Server Actions must use `"use server"` directive and include proper validation
- Accessing `window`/`document` in Server Components throws an error at runtime

## References

- [App Router Fundamentals](references/app-router-fundamentals.md) - Components, file conventions, navigation
- [Routing Patterns](references/routing-patterns.md) - Parallel routes, intercepting routes, dynamic routes
- [Caching Strategies](references/caching-strategies.md) - "use cache", cacheLife, revalidation
- [Server Actions](references/server-actions.md) - Actions, useActionState, validation
- [Next.js 16 Migration](references/nextjs16-migration.md) - Async APIs, Turbopack, config
- [Data Fetching](references/data-fetching.md) - Data patterns, Suspense, streaming
- [Metadata API](references/metadata-api.md) - generateMetadata, OpenGraph, sitemap
- [Examples](references/examples.md) - End-to-end sample implementations
