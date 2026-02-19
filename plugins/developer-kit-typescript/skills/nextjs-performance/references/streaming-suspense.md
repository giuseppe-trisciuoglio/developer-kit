# Streaming e Suspense in Next.js

## Overview

Streaming permette di inviare parti della UI man mano che sono pronte, migliorando il Time to First Byte (TTFB) e permettendo all'utente di vedere contenuto più velocemente.

---

## Pattern Base

### Loading.tsx

```typescript
// app/blog/loading.tsx
export default function Loading() {
  return (
    <div className="loading-skeleton">
      <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
      <div className="mt-4 space-y-2">
        {<>Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-4 bg-gray-200 rounded animate-pulse" />
        ))}</>
      </div>
    </div>
  )
}
```

### Suspense Boundaries

```typescript
// app/page.tsx
import { Suspense } from 'react'
import { ProductListSkeleton } from './components/ProductListSkeleton'
import { ProductList } from './components/ProductList'
import { ReviewsSkeleton } from './components/ReviewsSkeleton'
import { Reviews } from './components/Reviews'

export default function Page() {
  return (
    <div>
      {/* Questo è streamato immediatamente */}
      <header>
        <h1>Our Products</h1>
      </header>

      {/* Suspense boundary per ProductList */}
      <Suspense fallback={<ProductListSkeleton />}>
        <ProductList />
      </Suspense>

      {/* Reviews può caricare indipendentemente */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews />
      </Suspense>
    </div>
  )
}
```

---

## Streaming Pattern

### Waterfall Ottimizzato

```typescript
// BEFORE - Waterfall sequenziale
export default async function Page() {
  const user = await fetchUser()      // 100ms
  const orders = await fetchOrders()   // 150ms (dipende da user)
  const recommendations = await fetchRecommendations() // 200ms

  return (
    <div>
      <UserProfile user={user} />
      <OrderList orders={orders} />
      <Recommendations items={recommendations} />
    </div>
  )
}

// AFTER - Parallel fetching con Suspense
export default function Page() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile />
      </Suspense>

      <Suspense fallback={<OrdersSkeleton />}>
        <OrderList />
      </Suspense>

      <Suspense fallback={<RecsSkeleton />}>
        <Recommendations />
      </Suspense>
    </div>
  )
}

// Ogni componente fetcha i propri dati
async function UserProfile() {
  const user = await fetchUser()
  return <div>{user.name}</div>
}

async function OrderList() {
  const orders = await fetchOrders()
  return <ul>{orders.map(o => <li key={o.id}>{o.total}</li>)}</ul>
}
```

### Nested Suspense

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <Dashboard />
    </Suspense>
  )
}

// app/dashboard/Dashboard.tsx
async function Dashboard() {
  return (
    <div>
      <Sidebar />

      <main>
        <Suspense fallback={<ChartSkeleton />}>
          <RevenueChart />
        </Suspense>

        <Suspense fallback={<TableSkeleton />}>
          <RecentOrders />
        </Suspense>
      </main>
    </div>
  )
}
```

---

## use() Hook (React 19)

```typescript
'use client'

import { use, Suspense } from 'react'

// Promise creata fuori dal componente
const messagePromise = fetchMessage()

function Message() {
  // Suspende finché la promise non resolve
  const message = use(messagePromise)
  return <p>{message}</p>
}

export default function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <Message />
    </Suspense>
  )
}
```

### Con Props

```typescript
'use client'

import { use } from 'react'

function Comments({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise)

  return (
    <ul>
      {comments.map(c => <li key={c.id}>{c.text}</li>)}
    </ul>
  )
}

// Server Component che passa la promise
export default function Page() {
  const commentsPromise = fetchComments() // Non await!

  return (
    <Suspense fallback={<Loading />}>
      <Comments commentsPromise={commentsPromise} />
    </Suspense>
  )
}
```

---

## Error Boundaries

```typescript
// app/error.tsx
'use client'

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

---

## Best Practices

```typescript
// ✅ SÌ: Place Suspense boundaries strategically
<Suspense fallback={<SpecificSkeleton />}>
  <ExpensiveComponent />
</Suspense>

// ❌ NON: Unico Suspense in alto livello
<Suspense fallback={<GenericLoading />}>
  <EntirePage />
</Suspense>

// ✅ SÌ: Skeletons specifici per ogni sezione
<Suspense fallback={<ProductGridSkeleton />}>
  <ProductGrid />
</Suspense>

<Suspense fallback={<ReviewListSkeleton />}>
  <ReviewList />
</Suspense>

// ✅ SÌ: Fetch nel componente che usa i dati
async function ProductList() {
  const products = await fetchProducts() // Fetch locale
  return <div>{...}</div>
}

// ❌ NON: Passare dati attraverso props
async function Page() {
  const products = await fetchProducts() // ❌ Blocca tutta la pagina
  return <ProductList products={products} />
}
```
