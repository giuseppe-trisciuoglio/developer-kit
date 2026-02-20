# Caching Strategies in Next.js

## Overview

Next.js offre multiple strategie di caching:
- **Request Memoization**: Deduplica fetch nello stesso render
- **Data Cache**: Cache persistente tra request
- **Full Route Cache**: Cache delle pagine statiche
- **Router Cache**: Cache client-side delle route

---

## Fetch Caching

### Default Behavior (Next.js 15+)

```typescript
// BEFORE (Next.js 14) - Cache di default
fetch('https://api.example.com/data') // cached

// AFTER (Next.js 15) - No cache di default
fetch('https://api.example.com/data') // no-store
fetch('https://api.example.com/data', { cache: 'force-cache' }) // cached
```

### Cache Time-based (ISR)

```typescript
// Revalidazione automatica ogni 60 secondi
async function getData() {
  const res = await fetch('https://api.example.com/data', {
    next: {
      revalidate: 60, // secondi
      tags: ['products'],
    },
  })
  return res.json()
}
```

### On-demand Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidateTag, revalidatePath } from 'next/cache'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const { tag, path } = await request.json()

  try {
    if (tag) {
      revalidateTag(tag)
      return Response.json({ revalidated: true, tag })
    }

    if (path) {
      revalidatePath(path)
      return Response.json({ revalidated: true, path })
    }

    return Response.json({ error: 'Missing tag or path' }, { status: 400 })
  } catch (error) {
    return Response.json({ error: 'Revalidation failed' }, { status: 500 })
  }
}

// Uso da webhook o admin
await fetch('/api/revalidate', {
  method: 'POST',
  body: JSON.stringify({ tag: 'products' }),
})
```

---

## unstable_cache

### Cache di Funzioni

```typescript
import { unstable_cache } from 'next/cache'

// BEFORE - Query ad ogni richiesta
async function getProducts() {
  return db.product.findMany({ include: { category: true } })
}

// AFTER - Cache con revalidation
const getCachedProducts = unstable_cache(
  async () => {
    return db.product.findMany({ include: { category: true } })
  },
  ['products'], // Cache key
  {
    revalidate: 3600, // 1 ora
    tags: ['products', 'inventory'],
  }
)

// Uso nel componente
export default async function ProductPage() {
  const products = await getCachedProducts()
  return <ProductList products={products} />
}
```

### Cache con Parametri

```typescript
const getCachedProduct = unstable_cache(
  async (id: string) => {
    return db.product.findUnique({ where: { id } })
  },
  ['product'], // Key base
  { tags: ['products'] }
)

// Cache key finale: ['product', '123']
const product = await getCachedProduct('123')
```

---

## Route Segment Config

### Static vs Dynamic

```typescript
// app/page.tsx

// Static (default se no dynamic data)
export const dynamic = 'auto'

// Forza statico
export const dynamic = 'force-static'

// Forza dinamico (no cache)
export const dynamic = 'force-dynamic'

// Error se usa dynamic data
export const dynamic = 'error'

// Revalidation
export const revalidate = 3600 // 1 ora
export const revalidate = false // Mai (default static)
export const revalidate = 0 // Ogni richiesta (dynamic)
```

### Runtime

```typescript
// Edge runtime (più veloce, meno features)
export const runtime = 'edge'

// Node.js runtime (default, più compatibile)
export const runtime = 'nodejs'
```

---

## Server Actions Cache

```typescript
// app/actions.ts
'use server'

import { revalidatePath, revalidateTag } from 'next/cache'

export async function createProduct(formData: FormData) {
  const data = Object.fromEntries(formData)

  await db.product.create({ data })

  // Revalidate specifiche route
  revalidatePath('/products')
  revalidatePath('/admin/products')
  revalidateTag('products')

  return { success: true }
}

export async function updateProduct(id: string, data: FormData) {
  await db.product.update({ where: { id }, data: Object.fromEntries(data) })

  // Revalidate specifico
  revalidatePath(`/products/${id}`)
  revalidateTag(`product-${id}`)
  revalidateTag('products')
}
```

---

## Route Handlers Cache

```typescript
// app/api/products/route.ts

// Static route con revalidation
export const dynamic = 'force-static'
export const revalidate = 60

export async function GET() {
  const products = await db.product.findMany()
  return Response.json(products)
}
```

### Handler Dinamici con Cache

```typescript
// app/api/products/[id]/route.ts

export const dynamic = 'force-static'
export const revalidate = 3600

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params

  const product = await db.product.findUnique({
    where: { id },
  })

  if (!product) {
    return Response.json({ error: 'Not found' }, { status: 404 })
  }

  return Response.json(product)
}

// Genera static params per build
export async function generateStaticParams() {
  const products = await db.product.findMany({ select: { id: true } })
  return products.map((p) => ({ id: p.id }))
}
```

---

## Pattern Avanzati

### Stale-While-Revalidate Pattern

```typescript
import { unstable_cache } from 'next/cache'

const getData = unstable_cache(
  async () => fetchExpensiveData(),
  ['expensive-data'],
  {
    revalidate: 3600, // 1 ora
  }
)

// Con fetch diretto
async function getFreshData() {
  const res = await fetch('https://api.example.com/data', {
    next: {
      revalidate: 3600,
    },
  })
  return res.json()
}
```

### Cache Tagging Granulare

```typescript
// Cache per differenti entità
const getUser = unstable_cache(
  async (id: string) => db.user.findById(id),
  ['user'],
  { tags: (id) => [`user-${id}`, 'users'] }
)

const getUserOrders = unstable_cache(
  async (userId: string) => db.order.findByUser(userId),
  ['user-orders'],
  { tags: (userId) => [`user-${userId}-orders`, 'orders'] }
)

// Invalidazione selettiva
revalidateTag('user-123')      // Solo user
revalidateTag('user-123-orders') // Solo orders di user-123
revalidateTag('orders')         // Tutti gli orders
revalidateTag('users')          // Tutti gli users
```

### Cache con Headers Condizionali

```typescript
// Route handler con ETag
export async function GET() {
  const data = await getData()
  const etag = generateETag(data)

  const headers = new Headers()
  headers.set('ETag', etag)
  headers.set('Cache-Control', 'public, max-age=3600, stale-while-revalidate=86400')

  return new Response(JSON.stringify(data), { headers })
}
```

---

## Best Practices

```typescript
// ✅ SÌ: Cache con tags significativi
const getData = unstable_cache(fetchData, ['key'], {
  revalidate: 3600,
  tags: ['entity-type', 'entity-id'],
})

// ✅ SÌ: Revalidate selettivo
revalidateTag('user-123') // Non tutto 'users'

// ✅ SÌ: Differenti TTL per differenti dati
// Dati raramente modificati: lungo TTL
const getCategories = unstable_cache(fetchCategories, ['categories'], {
  revalidate: 86400, // 24 ore
})

// Dati frequentemente modificati: breve TTL
const getComments = unstableCache(fetchComments, ['comments'], {
  revalidate: 60, // 1 minuto
})

// ❌ NON: Cache di tutto con stesso TTL
// ❌ NON: Dimenticare di revalidate dopo mutation
// ❌ NON: Usare cache per dati utente-specifici senza key appropriata
```
