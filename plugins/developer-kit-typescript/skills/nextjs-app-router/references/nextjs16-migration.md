# Next.js 16 Migration Guide

## Async APIs (Breaking Change)

In Next.js 16, `cookies()`, `headers()`, `draftMode()` sono tutti async.

### Before (Next.js 15)

```tsx
import { cookies, headers } from "next/headers";

export default function Page() {
  const cookieStore = cookies();
  const session = cookieStore.get("session");

  const headersList = headers();
  const userAgent = headersList.get("user-agent");

  // ...
}
```

### After (Next.js 16)

```tsx
import { cookies, headers } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();
  const session = cookieStore.get("session");

  const headersList = await headers();
  const userAgent = headersList.get("user-agent");

  // ...
}
```

### Async Params e SearchParams

```tsx
// Before
export default function Page({
  params,
  searchParams,
}: {
  params: { slug: string };
  searchParams: { sort?: string };
}) {
  const { slug } = params;
  const { sort } = searchParams;
  // ...
}

// After
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ sort?: string }>;
}) {
  const { slug } = await params;
  const { sort } = await searchParams;
  // ...
}
```

## proxy.ts (Replacement for middleware.ts)

Next.js 16 introduce `proxy.ts` come nuovo boundary per la logica di routing avanzato, sostituendo gradualmente `middleware.ts`.

### When to Use proxy.ts vs middleware.ts

| Use Case | Solution |
|----------|----------|
| Header rewriting, auth redirects | `middleware.ts` |
| Complex routing logic, A/B testing, feature flags | `proxy.ts` |
| Request/Response modification | `middleware.ts` |
| Dynamic route selection | `proxy.ts` |

### proxy.ts Structure

```tsx
// app/proxy.ts
import { proxy } from "next/proxy";

export default proxy({
  // Route matching
  routes: [
    {
      pattern: "/old-path/:slug",
      destination: "/new-path/:slug",
      permanent: true,
    },
    {
      pattern: "/blog/:slug",
      destination: "/articles/:slug",
    },
  ],

  // Conditional routing
  async selectRoute(request) {
    const { pathname } = request.nextUrl;

    // A/B testing
    const variant = request.cookies.get("ab-variant")?.value ?? "a";

    if (pathname === "/landing") {
      return variant === "a" ? "/landing/a" : "/landing/b";
    }

    // Feature flags
    const featureEnabled = await checkFeatureFlag("new-dashboard");
    if (pathname === "/dashboard" && featureEnabled) {
      return "/dashboard/v2";
    }

    return null; // Continue with normal routing
  },
});
```

### middleware.ts (Still Valid)

```tsx
// middleware.ts (root of project)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const session = request.cookies.get("session")?.value;

  // Auth protection
  if (request.nextUrl.pathname.startsWith("/dashboard") && !session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set("x-custom-header", "value");

  return response;
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/protected/:path*"],
};
```

## Turbopack (Stable)

Next.js 16 ha Turbopack come dev server predefinito.

```bash
# Già attivo di default, ma puoi verificare con:
next dev --turbopack

# Per disabilitare (non consigliato):
next dev --no-turbopack
```

### Configuration

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      "@components": "./app/components",
    },
    resolveExtensions: [".mdx", ".tsx", ".ts", ".jsx", ".js"],
  },
};

export default nextConfig;
```

## React Compiler (Automatic Memoization)

Next.js 16 include React Compiler per memoizzazione automatica.

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};

export default nextConfig;
```

### Manual Memo Still Works

```tsx
// React Compiler gestisce automaticamente la maggior parte dei casi
// ma puoi ancora usare manualmente quando necessario

import { memo, useMemo, useCallback } from "react";

// Ancora valido per casi complessi
const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  const processed = useMemo(() => heavyComputation(data), [data]);
  // ...
});
```

## "use cache" Directive

La nuova direttiva per caching esplicito (sostituisce in parte `fetch` cache).

```tsx
"use cache";

import { cacheLife, cacheTag } from "next/cache";

export default async function Page() {
  cacheLife("hours");
  cacheTag("homepage");

  const data = await fetchData();
  return <Component data={data} />;
}
```

## next.config.ts (TypeScript Default)

Next.js 16 consiglia `.ts` per la configurazione.

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configurazioni
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.example.com",
      },
    ],
  },

  // Experimental
  experimental: {
    reactCompiler: true,
    cacheLife: {
      blog: {
        stale: 3600,
        revalidate: 900,
        expire: 86400,
      },
    },
  },
};

export default nextConfig;
```

## ESLint Configuration

```bash
# Installazione dipendenze aggiornate
npm install -D eslint-config-next@latest eslint@latest
```

```js
// eslint.config.mjs
import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default eslintConfig;
```
