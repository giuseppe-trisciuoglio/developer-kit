# Next.js Performance Optimization Checklist

## Core Web Vitals

### Largest Contentful Paint (LCP)
- [ ] Hero images use `<Image>` component with `priority` prop
- [ ] Above-the-fold content loads without JavaScript dependency
- [ ] Fonts preloaded with `next/font` (no FOIT/FOUT)
- [ ] Server Components used for initial content rendering
- [ ] No client-side data fetching for primary content

### First Input Delay (FID) / Interaction to Next Paint (INP)
- [ ] `'use client'` boundaries minimize client JavaScript
- [ ] Heavy computations offloaded to Web Workers or server
- [ ] Event handlers don't block the main thread
- [ ] Third-party scripts loaded with `next/script` strategy

### Cumulative Layout Shift (CLS)
- [ ] Images have explicit `width` and `height` (or `fill` with container)
- [ ] Skeleton loaders match final layout dimensions
- [ ] Fonts don't cause layout shift (use `next/font`)
- [ ] Dynamic content has reserved space

## Data Fetching Performance

### Avoid Request Waterfalls
```tsx
// ❌ Sequential — slow
const user = await getUser();
const orders = await getOrders(user.id); // waits for user
const reviews = await getReviews(user.id); // waits for orders

// ✅ Parallel — fast
const user = await getUser();
const [orders, reviews] = await Promise.all([
  getOrders(user.id),
  getReviews(user.id),
]);
```

### Streaming with Suspense
- [ ] Independent data sections wrapped in `<Suspense>` boundaries
- [ ] Each Suspense boundary has a meaningful loading fallback
- [ ] Critical content renders immediately without Suspense

### Caching Strategy
- [ ] Static pages use `generateStaticParams` for build-time generation
- [ ] Frequently accessed data has appropriate `revalidate` intervals
- [ ] Cache tags used for granular on-demand revalidation
- [ ] Dynamic rendering only for truly dynamic content (user-specific, real-time)

## Image Optimization

### Using next/image
- [ ] All images use `<Image>` component (not `<img>`)
- [ ] Above-the-fold images have `priority={true}`
- [ ] Images specify `width`/`height` or use `fill` with sized container
- [ ] Appropriate `sizes` prop for responsive images
- [ ] Remote image domains configured in `next.config.js`

```tsx
// ✅ Optimized image usage
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero banner"
  width={1200}
  height={600}
  priority // Above the fold
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

## Bundle Optimization

### Code Splitting
- [ ] Dynamic imports for heavy components (`next/dynamic`)
- [ ] Route-based code splitting (automatic with App Router)
- [ ] Large libraries loaded conditionally

```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/chart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Client-only if uses browser APIs
});
```

### Tree Shaking
- [ ] Named imports instead of default imports for large libraries
- [ ] No barrel file re-exports that pull in entire modules
- [ ] Unused dependencies removed from `package.json`

```typescript
// ❌ Imports entire library
import _ from 'lodash';
_.debounce(fn, 300);

// ✅ Named import — tree-shakeable
import debounce from 'lodash/debounce';
debounce(fn, 300);
```

## Font Optimization

### Using next/font
- [ ] All fonts loaded through `next/font/google` or `next/font/local`
- [ ] Font subsets specified to reduce file size
- [ ] `display: 'swap'` for visible text during load

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
});

export default function RootLayout({ children }) {
  return (
    <html className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
```

## Third-Party Script Optimization

### Using next/script
- [ ] Analytics scripts use `strategy="afterInteractive"` or `"lazyOnload"`
- [ ] No render-blocking third-party scripts
- [ ] Critical scripts use `strategy="beforeInteractive"` only when necessary

```tsx
import Script from 'next/script';

<Script
  src="https://analytics.example.com/script.js"
  strategy="lazyOnload" // Loads after page is idle
/>
```

## Server-Side Performance

### Database Queries
- [ ] Queries select only needed fields (no `SELECT *`)
- [ ] Pagination implemented for list endpoints
- [ ] Database connections pooled (PgBouncer, connection limits)
- [ ] No N+1 queries (use eager loading or batching)

### API Route Performance
- [ ] Response headers include appropriate cache control
- [ ] Large responses use streaming
- [ ] API routes validate input early to fail fast
- [ ] Background jobs for long-running operations

## Middleware Performance
- [ ] Middleware runs only on necessary routes (use `matcher`)
- [ ] Middleware logic is fast — no heavy computation
- [ ] No database queries in middleware (use Edge-compatible alternatives)
- [ ] Proper short-circuiting for early returns

## Monitoring and Measurement
- [ ] Core Web Vitals tracked in production (Vercel Analytics, web-vitals library)
- [ ] Bundle size monitored in CI (`@next/bundle-analyzer`)
- [ ] Performance budgets defined for key pages
- [ ] Lighthouse CI running on pull requests
