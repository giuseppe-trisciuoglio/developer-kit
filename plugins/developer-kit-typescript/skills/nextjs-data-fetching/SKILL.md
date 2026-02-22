---
name: nextjs-data-fetching
description: Provides Next.js App Router data fetching patterns including SWR and React Query integration, parallel data fetching, Incremental Static Regeneration (ISR), revalidation strategies, and error boundaries. Use when implementing data fetching in Next.js applications, choosing between server and client fetching, setting up caching strategies, or handling loading and error states.
allowed-tools: Read, Write, Edit, Bash
category: frontend
tags: [nextjs, data-fetching, server-components, ssg, ssr, isr]
---

# Next.js Data Fetching

## Overview

Comprehensive patterns for data fetching in Next.js App Router applications. Covers server-side fetching, client-side libraries (SWR, React Query), caching strategies, error handling, and loading states.

## When to Use

- Implementing data fetching in Next.js App Router
- Choosing between Server Components and Client Components for data
- Setting up SWR or React Query integration
- Implementing parallel data fetching patterns
- Configuring ISR and revalidation strategies
- Creating error boundaries and loading states

## Instructions

1. **Default to Server Components** for data fetching (better performance)
2. **Use parallel fetching** with `Promise.all()` for independent requests
3. **Choose caching strategy**: ISR for static, `cache: 'no-store'` for dynamic
4. **Use SWR/React Query** for real-time data and client interactivity
5. **Add Suspense boundaries** with `loading.tsx` for loading states
6. **Handle errors** with error boundaries and `error.tsx`
7. **Use Server Actions** for mutations that need to revalidate cache

## Examples

### Server Component Fetching

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600, tags: ['posts'] }
  });
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>;
}
```

### Parallel Data Fetching

```tsx
export default async function DashboardPage() {
  const [user, posts, analytics] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
    fetch('/api/analytics').then(r => r.json()),
  ]);
  return <Dashboard user={user} posts={posts} analytics={analytics} />;
}
```

### Decision Matrix

| Scenario | Solution |
|----------|----------|
| Static content, infrequent updates | Server Component + ISR |
| Dynamic content, user-specific | Server Component + `cache: 'no-store'` |
| Real-time updates | Client Component + SWR/React Query |
| User interactions | Client Component + mutation library |

## Constraints and Warnings

- Server Components cannot use hooks (useState, useEffect) or data fetching libraries
- Client Components must include `'use client'` directive
- Server Actions require `'use server'` directive
- Avoid fetching data inside loops in Server Components
- Be careful with `cache: 'force-cache'` for user-specific data

## Best Practices

1. Default to Server Components for data fetching
2. Use parallel fetching for independent requests
3. Implement `loading.tsx` or Suspense boundaries for loading states
4. Handle errors with error boundaries
5. Use Server Actions for form submissions and mutations
6. Use SWR/React Query for real-time and interactive data

## References

Consult these files for detailed patterns:

- **[references/examples.md](references/examples.md)** - Complete examples: ISR, parallel fetching, SWR integration, React Query setup, error boundaries, Server Actions, loading patterns, Suspense
- **[references/REACT-QUERY.md](references/REACT-QUERY.md)** - Advanced React Query patterns
