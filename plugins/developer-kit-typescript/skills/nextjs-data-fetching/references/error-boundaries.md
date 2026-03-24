# Error Boundaries Reference

Full ErrorBoundary implementations for Next.js data fetching error handling.

## Basic ErrorBoundary

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

## ErrorBoundary with Reset

Allows the user to retry after an error:

```tsx
// app/components/ErrorBoundary.tsx
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

## Usage with Data Fetching

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

## Using ErrorBoundary with SWR/React Query

```tsx
// app/components/SWRBoundary.tsx
'use client';

import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

export function SWRBoundary({ children, fallback = <div>Error loading data</div> }: Props) {
  return <>{children}</>; // Wrap in parent ErrorBoundary in page component
}
```
