# React Query Advanced Patterns

## Table of Contents

1. [Prefetching and Hydration](#prefetching-and-hydration)
2. [Mutations and Optimistic Updates](#mutations-and-optimistic-updates)
3. [Infinite Queries](#infinite-queries)
4. [Parallel Queries](#parallel-queries)
5. [Dependent Queries](#dependent-queries)
6. [Query Invalidation](#query-invalidation)

## Prefetching and Hydration

### Server-Side Prefetching

Prefetch data on server for immediate hydration:

```tsx
// app/posts/page.tsx
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from '@tanstack/react-query';
import { Posts } from './Posts';

export default async function PostsPage() {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch('https://api.example.com/posts');
      return res.json();
    },
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Posts />
    </HydrationBoundary>
  );
}
```

```tsx
// app/posts/Posts.tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function Posts() {
  const { data: posts } = useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch('https://api.example.com/posts');
      return res.json();
    },
  });

  return (
    <ul>
      {posts?.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## Mutations and Optimistic Updates

### Basic Mutation

```tsx
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';

export function CreatePost() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (newPost: { title: string; content: string }) => {
      const res = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost),
      });
      return res.json();
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  return (
    <button
      onClick={() =>
        mutation.mutate({ title: 'New Post', content: 'Content here' })
      }
      disabled={mutation.isPending}
    >
      {mutation.isPending ? 'Creating...' : 'Create Post'}
    </button>
  );
}
```

### Optimistic Updates

```tsx
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';

interface Post {
  id: string;
  title: string;
  content: string;
}

export function LikePost({ postId }: { postId: string }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`/api/posts/${postId}/like`, {
        method: 'POST',
      });
      return res.json();
    },
    onMutate: async () => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['posts', postId] });

      // Snapshot previous value
      const previousPost = queryClient.getQueryData<Post>(['posts', postId]);

      // Optimistically update
      queryClient.setQueryData(['posts', postId], (old: Post | undefined) =>
        old ? { ...old, likes: old.likes + 1 } : old
      );

      return { previousPost };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousPost) {
        queryClient.setQueryData(['posts', postId], context.previousPost);
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['posts', postId] });
    },
  });

  return (
    <button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
      Like
    </button>
  );
}
```

## Infinite Queries

### Infinite Scroll

```tsx
'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useInView } from 'react-intersection-observer';

interface Post {
  id: string;
  title: string;
}

interface PostsResponse {
  posts: Post[];
  nextCursor?: string;
}

export function InfinitePosts() {
  const { ref, inView } = useInView();

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useInfiniteQuery<PostsResponse>({
    queryKey: ['posts'],
    queryFn: async ({ pageParam }) => {
      const res = await fetch(`/api/posts?cursor=${pageParam || ''}`);
      return res.json();
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: undefined as string | undefined,
  });

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, fetchNextPage]);

  if (status === 'pending') return <div>Loading...</div>;
  if (status === 'error') return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.pages.map((page, i) => (
        <div key={i}>
          {page.posts.map((post) => (
            <div key={post.id}>{post.title}</div>
          ))}
        </div>
      ))}
      <div ref={ref}>
        {isFetchingNextPage && 'Loading more...'}
      </div>
    </div>
  );
}
```

## Parallel Queries

```tsx
'use client';

import { useQueries } from '@tanstack/react-query';

export function Dashboard() {
  const results = useQueries({
    queries: [
      {
        queryKey: ['user'],
        queryFn: () => fetch('/api/user').then(r => r.json()),
      },
      {
        queryKey: ['posts'],
        queryFn: () => fetch('/api/posts').then(r => r.json()),
      },
      {
        queryKey: ['analytics'],
        queryFn: () => fetch('/api/analytics').then(r => r.json()),
      },
    ],
  });

  const [user, posts, analytics] = results;

  if (user.isLoading || posts.isLoading || analytics.isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Welcome {user.data?.name}</h1>
      <p>Posts: {posts.data?.length}</p>
      <p>Views: {analytics.data?.views}</p>
    </div>
  );
}
```

## Dependent Queries

```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function UserPosts({ userId }: { userId?: string }) {
  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const res = await fetch(`/api/users/${userId}`);
      return res.json();
    },
    enabled: !!userId, // Only run when userId exists
  });

  const { data: posts } = useQuery({
    queryKey: ['posts', user?.id],
    queryFn: async () => {
      const res = await fetch(`/api/users/${user.id}/posts`);
      return res.json();
    },
    enabled: !!user?.id, // Wait for user data
  });

  if (!userId) return <div>Select a user</div>;
  if (!user) return <div>Loading user...</div>;
  if (!posts) return <div>Loading posts...</div>;

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## Query Invalidation

### Selective Invalidation

```tsx
'use client';

import { useQueryClient } from '@tanstack/react-query';

export function RefreshControls() {
  const queryClient = useQueryClient();

  const refreshAll = () => {
    queryClient.invalidateQueries();
  };

  const refreshPosts = () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
  };

  const refreshCurrentPost = (postId: string) => {
    queryClient.invalidateQueries({
      queryKey: ['posts', postId],
      exact: true,
    });
  };

  return (
    <div>
      <button onClick={refreshAll}>Refresh All</button>
      <button onClick={refreshPosts}>Refresh Posts</button>
    </div>
  );
}
```

### Background Refetching

```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function LiveData() {
  const { data, isFetching, dataUpdatedAt } = useQuery({
    queryKey: ['live-data'],
    queryFn: async () => {
      const res = await fetch('/api/live-data');
      return res.json();
    },
    refetchInterval: 5000, // Refetch every 5 seconds
    refetchIntervalInBackground: true,
    staleTime: 0, // Always consider data stale
  });

  return (
    <div>
      <p>Data: {JSON.stringify(data)}</p>
      {isFetching && <span>Updating...</span>}
      <small>
        Last updated: {new Date(dataUpdatedAt).toLocaleTimeString()}
      </small>
    </div>
  );
}
```
