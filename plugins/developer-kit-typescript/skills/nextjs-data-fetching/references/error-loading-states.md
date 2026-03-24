# Error and Loading States

Treat loading and failure handling as part of the fetch architecture. Use boundaries and route-level files to keep degraded states predictable.

## Creating Error Boundaries

Use an Error Boundary for client-side failures that should render a fallback instead of crashing the page.

```tsx
// app/components/ErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}
```

## Using Error Boundaries with Data Fetching

Wrap interactive or client-driven fetch flows in a fallback UI.

```tsx
// app/posts/page.tsx
import { ErrorBoundary } from '../components/ErrorBoundary';
import { Posts } from './Posts';
import { PostsError } from './PostsError';

export default function PostsPage() {
  return (
    <ErrorBoundary fallback={<PostsError />}>
      <Posts />
    </ErrorBoundary>
  );
}
```

## Error Boundary with Reset

Add a reset path when the user should be able to retry without leaving the page.

```tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback: (props: { reset: () => void }) => ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  reset = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback({ reset: this.reset });
    }

    return this.props.children;
  }
}
```

## Loading.tsx Pattern

Use `loading.tsx` for route-level loading UI that integrates with Suspense.

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

## Suspense Boundaries

Use smaller Suspense boundaries when different areas of the page can load independently.

```tsx
// app/posts/page.tsx
import { Suspense } from 'react';
import { PostsList } from './PostsList';
import { PostsSkeleton } from './PostsSkeleton';
import { PopularPosts } from './PopularPosts';

export default function PostsPage() {
  return (
    <div>
      <h1>Posts</h1>

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

## Selection Guide

- Use `loading.tsx` for route-level pending states.
- Use Suspense boundaries to stream independent sections.
- Use Error Boundaries for recoverable UI failures.
- Add retry affordances when the user can recover without navigation.
