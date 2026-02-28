# Next.js App Router Fundamentals

## Server Components vs Client Components

### Server Components (Default)

I Server Components sono il default in App Router. Eseguono sul server e possono:
- Accedere direttamente a database, file system, API esterne
- Renderizzare dati sensibili senza esporli al client
- Ridurre il bundle JavaScript inviato al client

```tsx
// app/page.tsx - Server Component di default
async function getData() {
  const res = await fetch(`${process.env.API_URL}/data`);
  return res.json();
}

export default async function Page() {
  const data = await getData();
  return <main>{/* render data */}</main>;
}
```

### Client Components

Usare `"use client"` per componenti che necessitano di:
- React hooks (useState, useEffect, useContext)
- Browser APIs (window, document, localStorage)
- Event handlers (onClick, onSubmit)
- Third-party librerie client-only

```tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### Pattern Ibrido (Server + Client)

```tsx
// app/page.tsx - Server Component
import { ProductCard } from "./product-card";

async function getProducts() {
  return db.product.findMany();
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <div>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

```tsx
// app/product-card.tsx - Client Component
"use client";

import { useState } from "react";

export function ProductCard({ product }: { product: Product }) {
  const [isAdded, setIsAdded] = useState(false);

  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={() => setIsAdded(true)}>
        {isAdded ? "Added!" : "Add to Cart"}
      </button>
    </div>
  );
}
```

## React Compiler (Next.js 16+)

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

Con React Compiler attivo, non serve più manualmente:
- `React.memo()` (in molti casi)
- `useMemo()` per computazioni semplici
- `useCallback()` per event handlers semplici

## File Conventions Speciali

### loading.tsx

Mostra UI durante il caricamento di dati.

```tsx
// app/blog/loading.tsx
export default function Loading() {
  return <p>Loading posts...</p>;
}
```

### error.tsx

Gestisce errori nel segmento con Error Boundary.

```tsx
// app/blog/error.tsx
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

### not-found.tsx

Pagina 404 per segmento.

```tsx
// app/blog/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
    </div>
  );
}
```

```tsx
// Per triggerare programmaticamente
import { notFound } from "next/navigation";

export default async function BlogPost({ params }: PageProps) {
  const post = await fetchPost((await params).slug);

  if (!post) {
    notFound();
  }

  return <article>{/* ... */}</article>;
}
```

### template.tsx

Simile a layout.tsx ma:
- Si re-mounta su ogni navigazione
- Mantiene stato/UI separati tra le route

```tsx
// app/dashboard/template.tsx
export default function Template({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="animate-fade-in">{children}</div>;
}
```

### default.tsx

Fallback per parallel routes quando non c'è match.

```tsx
// app/dashboard/@team/default.tsx
export default function Default() {
  return <div>Select a team member</div>;
}
```

## Navigation

### Link Component

```tsx
import Link from "next/link";

export default function Navigation() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/blog/[slug]" as="/blog/hello-world">
        Post
      </Link>
    </nav>
  );
}
```

### useRouter Hook (Client Components)

```tsx
"use client";

import { useRouter } from "next/navigation";

export default function NavigationButton() {
  const router = useRouter();

  return (
    <button onClick={() => router.push("/dashboard")}>
      Go to Dashboard
    </button>
  );
}
```

| Method | Description |
|--------|-------------|
| `push(href)` | Naviga a nuova route |
| `replace(href)` | Naviga sostituendo la route corrente |
| `back()` | Torna indietro nella history |
| `forward()` | Vai avanti nella history |
| `refresh()` | Refresh della route corrente |
| `prefetch(href)` | Prefetch di una route |

### Programmatic Navigation (Server Components)

```tsx
import { redirect } from "next/navigation";

export default async function ProtectedPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return <div>Protected content</div>;
}
```

## API Route Handlers

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";

// GET /api/users
export async function GET(request: NextRequest) {
  const users = await db.user.findMany();
  return NextResponse.json(users);
}

// POST /api/users
export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.user.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}
```

```ts
// app/api/users/[id]/route.ts
interface RouteParams {
  params: Promise<{ id: string }>;
}

// GET /api/users/[id]
export async function GET(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const user = await db.user.findUnique({ where: { id } });

  if (!user) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(user);
}

// PATCH /api/users/[id]
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const body = await request.json();

  const user = await db.user.update({
    where: { id },
    data: body,
  });

  return NextResponse.json(user);
}

// DELETE /api/users/[id]
export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  await db.user.delete({ where: { id } });
  return NextResponse.json(null, { status: 204 });
}
```

## next/image

```tsx
import Image from "next/image";

export default function Avatar({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={64}
      height={64}
      priority // Per LCP images
      quality={80} // 1-100, default 75
      placeholder="blur" // o "empty"
      blurDataURL="data:image/jpeg;base64,..." // Placeholder base64
      className="rounded-full"
    />
  );
}
```

### Fill Mode

```tsx
<Image
  src="/photo.jpg"
  alt="Photo"
  fill
  sizes="(max-width: 768px) 100vw, 50vw"
  className="object-cover"
/>
```

## next/font

```tsx
// app/layout.tsx
import { Inter, Roboto_Mono } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const robotoMono = Roboto_Mono({
  subsets: ["latin"],
  variable: "--font-roboto-mono",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

```css
/* globals.css */
body {
  font-family: var(--font-inter), system-ui, sans-serif;
}

code {
  font-family: var(--font-roboto-mono), monospace;
}
```

## Environment Variables

```
# .env.local
# Accessibile solo nel server
DATABASE_URL="postgresql://..."
API_SECRET_KEY="secret"

# Accessibile anche nel client (prefisso NEXT_PUBLIC_)
NEXT_PUBLIC_API_URL="https://api.example.com"
NEXT_PUBLIC_APP_NAME="My App"
```

```tsx
// Server Component - accesso diretto
export default async function Page() {
  const data = await fetch(process.env.DATABASE_URL!);
  // ...
}
```

```tsx
// Client Component - solo NEXT_PUBLIC_
"use client";

export default function Config() {
  return <div>API: {process.env.NEXT_PUBLIC_API_URL}</div>;
}
```
