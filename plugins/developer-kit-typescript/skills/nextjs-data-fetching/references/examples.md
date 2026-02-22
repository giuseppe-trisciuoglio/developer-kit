# Next.js Data Fetching Examples

## Caching and Revalidation

### Time-based Revalidation (ISR)

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 }
  });
  return res.json();
}
```

### On-Demand Revalidation

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

### Tag cached data

```tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { tags: ['posts'], revalidate: 3600 }
  });
  return res.json();
}
```

### Opt-out of Caching

```tsx
const res = await fetch('https://api.example.com/data', { cache: 'no-store' });
// Or use: export const dynamic = 'force-dynamic';
```

## Client-Side Data Fetching

### SWR Integration

```tsx
'use client';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export function Posts() {
  const { data, error, isLoading } = useSWR('/api/posts', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Failed to load posts</div>;

  return (
    <ul>{data.map((post: any) => <li key={post.id}>{post.title}</li>)}</ul>
  );
}
```

### React Query Integration

Setup provider:

```tsx
// app/providers.tsx
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000, refetchOnWindowFocus: false } },
  }));
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

Use in components:

```tsx
'use client';
import { useQuery } from '@tanstack/react-query';

export function Posts() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch('/api/posts');
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <ul>{data.map((post: any) => <li key={post.id}>{post.title}</li>)}</ul>;
}
```

## Error Boundaries

```tsx
'use client';
import { Component, ReactNode } from 'react';

interface Props { children: ReactNode; fallback: (props: { reset: () => void }) => ReactNode; }
interface State { hasError: boolean; }

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };
  static getDerivedStateFromError(): State { return { hasError: true }; }
  reset = () => { this.setState({ hasError: false }); };

  render() {
    if (this.state.hasError) return this.props.fallback({ reset: this.reset });
    return this.props.children;
  }
}
```

## Server Actions for Mutations

```tsx
// app/actions/posts.ts
'use server';
import { revalidateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  const response = await fetch('https://api.example.com/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });

  if (!response.ok) throw new Error('Failed to create post');
  revalidateTag('posts');
  return response.json();
}
```

```tsx
// app/posts/CreatePostForm.tsx
'use client';
import { createPost } from '../actions/posts';

export function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

## Loading States

### Loading.tsx Pattern

```tsx
// app/posts/loading.tsx
export default function PostsLoading() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-16 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

### Suspense Boundaries

```tsx
import { Suspense } from 'react';

export default function PostsPage() {
  return (
    <div>
      <Suspense fallback={<PostsSkeleton />}>
        <PostsList />
      </Suspense>
      <Suspense fallback={<div>Loading popular...</div>}>
        <PopularPosts />
      </Suspense>
    </div>
  );
}
```

## Complete Examples

### Blog with ISR

```tsx
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 }
  }).then(r => r.json());

  return (
    <main>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </main>
  );
}
```

### Real-time Prices with SWR

```tsx
'use client';
import useSWR from 'swr';

export function PriceTicker() {
  const { data, error } = useSWR('/api/crypto/prices', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });

  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;
  return <div>BTC: ${data.bitcoin} | ETH: ${data.ethereum}</div>;
}
```
