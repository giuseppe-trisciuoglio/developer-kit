# Caching and Revalidation Strategies

## Time-based Revalidation (ISR)

Use time-based revalidation when stale data is acceptable for a bounded period.

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: {
      revalidate: 60,
    },
  });
  return res.json();
}
```

Choose the revalidation interval based on how often the data changes.

## On-Demand Revalidation

Use Route Handlers or Server Actions with `revalidateTag()` or `revalidatePath()` when data should refresh immediately after a write.

```tsx
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const tag = request.nextUrl.searchParams.get('tag');

  if (tag) {
    revalidateTag(tag);
    return Response.json({ revalidated: true });
  }

  return Response.json({ revalidated: false }, { status: 400 });
}
```

Keep invalidation tags stable and descriptive so read and write paths stay coordinated.

## Tag Cached Data for Selective Invalidation

Attach cache tags when the same data source is read in multiple places.

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: {
      tags: ['posts'],
      revalidate: 3600,
    },
  });
  return res.json();
}
```

Use a small set of predictable tags instead of dynamically generating unnecessary tag variants.

## Opt Out of Caching

Disable caching for highly dynamic or user-specific data.

```tsx
async function getRealTimeData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store',
  });
  return res.json();
}

export const dynamic = 'force-dynamic';
```

Use `no-store` intentionally because it trades performance for freshness.

## Cache Selection Checklist

- Use ISR when the page can tolerate bounded staleness.
- Use tags when a mutation needs to refresh multiple consumers.
- Use `no-store` for real-time, user-specific, or security-sensitive responses.
- Avoid sharing cache entries across different user contexts.

## Example: Blog Page with ISR

**Input:** Create a blog page that fetches posts and updates every hour.

```tsx
// app/blog/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 },
  });
  return res.json();
}

export default async function BlogPage() {
  const posts = await getPosts();
  return (
    <main>
      <h1>Blog Posts</h1>
      {posts.map((post) => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </main>
  );
}
```

**Output:** The page is cached and revalidated every hour.
