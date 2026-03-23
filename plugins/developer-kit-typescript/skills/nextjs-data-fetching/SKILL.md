---
name: nextjs-data-fetching
description: Provides Next.js App Router data fetching patterns including SWR and React Query integration, parallel data fetching, Incremental Static Regeneration (ISR), revalidation strategies, and error boundaries. Use when implementing data fetching in Next.js applications, choosing between server and client fetching, setting up caching strategies, or handling loading and error states.
allowed-tools: Read, Write, Edit, Bash
---

# Next.js Data Fetching

Provides practical guidance for data fetching in Next.js App Router applications. Use this skill to choose between server and client fetching, configure caching and revalidation, and pair data access with reliable loading and error handling.

## Overview

Default to data fetching in async Server Components. Move to client-side libraries only when the UX needs browser-driven refresh, optimistic updates, or long-lived interactive state.

Keep `SKILL.md` focused on the decision flow below, then load the relevant reference files for implementation details.

## When to Use

Use this skill when you need to:

- Implement data fetching in a Next.js App Router application
- Choose between Server Components and Client Components for data access
- Set up parallel or sequential fetching strategies
- Configure ISR, cache tags, or `cache: 'no-store'`
- Add SWR or React Query for client-driven data flows
- Handle loading states, Suspense boundaries, and error boundaries
- Use Server Actions for mutations that refresh cached data

## How to Use This Skill

1. Start with the decision guide to pick the right fetching model.
2. Load the reference file that matches the work area:
   - Server, parallel, or sequential fetching -> `references/data-fetching.md`
   - ISR, cache tags, or revalidation -> `references/caching-strategies.md`
   - SWR or client-driven fetching -> `references/client-fetching.md`
   - Advanced React Query patterns -> `references/react-query.md`
   - Loading states or error boundaries -> `references/error-loading-states.md`
   - Mutations with Server Actions -> `references/server-actions.md`
3. Apply the smallest viable pattern for the feature.
4. Verify that caching, loading, and error behavior match the use case.

## Quick Decision Guide

| Scenario | Default choice |
|----------|----------------|
| Static or cacheable content | Server Component + `fetch()` + `revalidate` |
| Multiple independent requests | Parallel fetching with `Promise.all()` |
| Requests with data dependency | Sequential fetching |
| User-specific or real-time data | Client Component + SWR or React Query |
| Mutation followed by refresh | Server Action + `revalidateTag()` or `revalidatePath()` |
| Data that must never be cached | `fetch(..., { cache: 'no-store' })` |

## Instructions

### 1. Default to Server Component fetching

Fetch directly in async Server Components for the initial render whenever browser state is not required.

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();
  return <PostsList posts={posts} />;
}
```

Use parallel fetching for independent requests, and switch to sequential fetching only when one request depends on the result of another. See [references/data-fetching.md](references/data-fetching.md) for full patterns and examples.

### 2. Choose caching intentionally

Use time-based revalidation for cacheable content, tags for selective invalidation, and `no-store` for truly dynamic data.

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60, tags: ['posts'] },
  });
  return res.json();
}
```

Prefer explicit cache behavior over defaults so the rendering model stays obvious. See [references/caching-strategies.md](references/caching-strategies.md) for ISR, tag revalidation, and dynamic rendering patterns.

### 3. Use client fetching only when the UX needs it

Reach for SWR or React Query when the component needs polling, background refresh, optimistic updates, or user-driven cache coordination.

```tsx
'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function Posts() {
  const { data, error, isLoading } = useSWR('/api/posts', fetcher);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Failed to load posts</div>;

  return <PostsList posts={data} />;
}
```

Start simple with SWR for lightweight refresh needs. Use React Query when you need richer cache orchestration, hydration, or mutation workflows. See [references/client-fetching.md](references/client-fetching.md) and [references/react-query.md](references/react-query.md).

### 4. Pair data fetching with loading and error UI

Add `loading.tsx`, Suspense boundaries, or error boundaries so failures and slow requests degrade gracefully.

```tsx
import { Suspense } from 'react';
import { PostsList } from './PostsList';
import { PostsSkeleton } from './PostsSkeleton';

export default function PostsPage() {
  return (
    <Suspense fallback={<PostsSkeleton />}>
      <PostsList />
    </Suspense>
  );
}
```

Treat loading and error handling as part of the fetching design, not as an afterthought. See [references/error-loading-states.md](references/error-loading-states.md) for reusable patterns.

### 5. Use Server Actions for mutations

Handle writes in Server Actions, then invalidate the relevant cache entries.

```tsx
'use server';

import { revalidateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  await fetch('https://api.example.com/posts', {
    method: 'POST',
    body: JSON.stringify({
      title: formData.get('title'),
      content: formData.get('content'),
    }),
  });

  revalidateTag('posts');
}
```

Keep the mutation close to the cache invalidation strategy so reads and writes stay aligned. See [references/server-actions.md](references/server-actions.md) for full form patterns.

## Best Practices

- Prefer Server Components for the first render whenever possible.
- Parallelize independent requests with `Promise.all()`.
- Pick cache settings based on data volatility, not convenience.
- Use client-side libraries only for interactive or continuously refreshed data.
- Add explicit loading and error states for every non-trivial fetch flow.
- Revalidate cache entries immediately after successful mutations.

## Constraints and Warnings

- Server Components cannot use hooks such as `useState`, `useEffect`, SWR, or React Query.
- Client Components must include the `'use client'` directive.
- Avoid shared caching for user-specific data.
- Treat Server Actions as server-side write paths and validate inputs accordingly.
- Keep server and client rendering aligned to avoid hydration mismatches.

## Examples

### Example 1: Cacheable content page

Use a Server Component with `revalidate` when the page can tolerate bounded staleness.

### Example 2: Interactive dashboard

Use parallel server fetching for the initial render, then add SWR or React Query only to the widgets that need live refresh or mutation handling.

## References

- [references/data-fetching.md](references/data-fetching.md) - Server Component, parallel, and sequential fetching patterns
- [references/caching-strategies.md](references/caching-strategies.md) - ISR, tag invalidation, on-demand revalidation, and `no-store`
- [references/client-fetching.md](references/client-fetching.md) - SWR setup, React Query basics, and client-fetching decisions
- [references/react-query.md](references/react-query.md) - Advanced React Query hydration, mutations, infinite queries, and invalidation
- [references/error-loading-states.md](references/error-loading-states.md) - Error boundaries, `loading.tsx`, and Suspense patterns
- [references/server-actions.md](references/server-actions.md) - Server Actions for mutations and cache refresh workflows
