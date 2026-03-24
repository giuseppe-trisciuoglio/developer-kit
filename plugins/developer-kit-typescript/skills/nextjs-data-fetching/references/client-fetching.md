# Client-Side Data Fetching

Use client-side libraries when the component needs browser-driven refresh, optimistic interactions, or local cache coordination.

## SWR Integration

Choose SWR for lightweight refresh and revalidation behavior.

Install with `npm install swr`.

```tsx
'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function Posts() {
  const { data, error, isLoading } = useSWR('/api/posts', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Failed to load posts</div>;

  return (
    <ul>
      {data.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

Use SWR when the data model is simple and the main need is background refresh.

## React Query Integration

Choose React Query when you need structured query keys, richer cache invalidation, or advanced mutation flows.

Install with `npm install @tanstack/react-query`.

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

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

  return (
    <ul>
      {data.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

For hydration, optimistic updates, infinite queries, and invalidation strategies, see [react-query.md](react-query.md).

## Library Selection Guide

Prefer SWR when you need:

- Lightweight polling or refresh
- Minimal setup
- Simple cache behavior

Prefer React Query when you need:

- Query hydration from the server
- Rich mutation workflows
- Centralized invalidation rules
- Infinite or dependent queries

## Example: Real-Time Data with SWR

**Input:** Display live cryptocurrency prices that update every 5 seconds.

```tsx
// app/crypto/PriceTicker.tsx
'use client';

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function PriceTicker() {
  const { data, error } = useSWR('/api/crypto/prices', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });

  if (error) return <div>Failed to load prices</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="ticker">
      <span>BTC: ${data.bitcoin}</span>
      <span>ETH: ${data.ethereum}</span>
    </div>
  );
}
```

**Output:** The component refreshes automatically while preserving a simple API.
