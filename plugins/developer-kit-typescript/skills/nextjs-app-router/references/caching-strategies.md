# Caching Strategies (Next.js 16+)

## Explicit Caching with "use cache"

Next.js 16 introduce la cache esplicita con la direttiva `"use cache"`.

### Basic Usage

```tsx
"use cache";

export default async function ProductPage() {
  const products = await fetchProducts();
  return <ProductList products={products} />;
}
```

### Cache Life Configuration

```tsx
import { cacheLife } from "next/cache";

"use cache";

export default async function ProductPage() {
  cacheLife("hours"); // Predefined profile

  const products = await fetchProducts();
  return <ProductList products={products} />;
}
```

### Predefined Cache Profiles

| Profile | Durata | stale | revalidate |
|---------|--------|-------|------------|
| `"seconds"` | 1s | 0 | auto |
| `"minutes"` | 1m | 0 | auto |
| `"hours"` | 1h | 0 | auto |
| `"days"` | 1d | 0 | auto |
| `"weeks"` | 1w | 0 | auto |
| `"max"` | 1y | 0 | auto |

### Custom Cache Profile (next.config.ts)

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    cacheLife: {
      blog: {
        stale: 3600,      // 1 hour
        revalidate: 900,  // 15 minutes
        expire: 86400,    // 24 hours
      },
      product: {
        stale: 60,
        revalidate: 30,
        expire: 3600,
      },
    },
  },
};

export default nextConfig;
```

```tsx
"use cache";

import { cacheLife } from "next/cache";

export default async function BlogPost() {
  cacheLife("blog");
  // ...
}
```

### Cache Tags for Revalidation

```tsx
"use cache";

import { cacheTag } from "next/cache";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  cacheTag(`product-${id}`);
  cacheTag("products");

  const product = await fetchProduct(id);
  return <ProductDetail product={product} />;
}
```

### On-Demand Revalidation

```tsx
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { tag } = await request.json();

  revalidateTag(tag);

  return NextResponse.json({ revalidated: true });
}
```

### Cache per Function

```tsx
import { cache } from "react";

// React cache deduplicates requests
const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } });
});

export default async function Profile({ userId }: { userId: string }) {
  const user = await getUser(userId);
  // ...
}
```

## Disabling Cache

```tsx
export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function RealtimeData() {
  const data = await fetchData({ cache: "no-store" });
  // ...
}
```

## Route Segment Config

```tsx
// app/dashboard/page.tsx
export const dynamic = "auto"; // 'auto' | 'force-dynamic' | 'force-static' | 'error'
export const revalidate = 3600; // seconds
export const fetchCache = "auto"; // 'auto' | 'default-cache' | 'only-no-store' | 'force-cache' | 'force-no-store'
export const runtime = "nodejs"; // 'nodejs' | 'edge'
export const preferredRegion = "iad1"; // 'auto' | 'global' | 'home' | string

export default async function DashboardPage() {
  // ...
}
```
