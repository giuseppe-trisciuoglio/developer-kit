# Server Components - Best Practices

## Overview

Server Components eseguono sul server:
- Zero JavaScript bundle size
- Accesso diretto a database/API
- Riduzione del tempo di hydration
- Accesso a risorse server-side

---

## Pattern Base

### Server Component Puro

```typescript
// BEFORE (Client Component)
'use client'
import { useEffect, useState } from 'react'

export default function ProductList() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    fetch('/api/products')
      .then(r => r.json())
      .then(setProducts)
  }, [])

  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}

// AFTER (Server Component)
import { db } from '@/lib/db'

export default async function ProductList() {
  const products = await db.product.findMany()

  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  )
}
```

### Client Component Ibrido

```typescript
// ProductCard.tsx - Server Component
import { AddToCartButton } from './AddToCartButton'
import { db } from '@/lib/db'

export async function ProductCard({ id }: { id: string }) {
  const product = await db.product.findById(id)

  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      {/* Solo il bottone è client component */}
      <AddToCartButton productId={id} />
    </div>
  )
}

// AddToCartButton.tsx - Client Component
'use client'

import { useState } from 'react'

export function AddToCartButton({ productId }: { productId: string }) {
  const [adding, setAdding] = useState(false)

  const addToCart = async () => {
    setAdding(true)
    await fetch('/api/cart', {
      method: 'POST',
      body: JSON.stringify({ productId }),
    })
    setAdding(false)
  }

  return (
    <button onClick={addToCart} disabled={adding}>
      {adding ? 'Adding...' : 'Add to Cart'}
    </button>
  )
}
```

---

## React 19 + Next.js 16 Patterns

### Async Params (Next.js 15+)

```typescript
// BEFORE (Next.js 14)
export default async function Page({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug)
  // ...
}

// AFTER (Next.js 15+) - params è una Promise
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetchPost(slug)
  // ...
}
```

### use() Hook (React 19)

```typescript
'use client'

import { use } from 'react'

// Promise creata fuori dal componente
const messagePromise = fetchMessage()

export function Message() {
  // Suspende finché la promise non resolve
  const message = use(messagePromise)

  return <p>{message}</p>
}

// Con props
function Comments({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise)

  return (
    <ul>
      {comments.map(c => <li key={c.id}>{c.text}</li>)}
    </ul>
  )
}
```

### Server Actions Migliorati

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

// Action con validazione
export async function updateProfile(prevState: any, formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string

  // Validazione
  if (!name || name.length < 2) {
    return { error: 'Name must be at least 2 characters' }
  }

  try {
    await db.user.update({
      where: { id: session.userId },
      data: { name, email },
    })

    revalidatePath('/profile')
    return { success: true }
  } catch (error) {
    return { error: 'Update failed' }
  }
}

// Componente con useActionState (React 19)
'use client'

import { useActionState } from 'react'
import { updateProfile } from './actions'

export function ProfileForm() {
  const [state, action, pending] = useActionState(updateProfile, null)

  return (
    <form action={action}>
      <input name="name" placeholder="Name" />
      <input name="email" type="email" placeholder="Email" />
      <button type="submit" disabled={pending}>
        {pending ? 'Saving...' : 'Save'}
      </button>
      {state?.error && <p className="error">{state.error}</p>}
      {state?.success && <p className="success">Saved!</p>}
    </form>
  )
}
```

---

## Conversione Client → Server Component

### Checklist di Conversione

1. **Rimuovere 'use client'**
2. **Spostare data fetching nel componente**
3. **Rimuovere useState/useEffect per data loading**
4. **Spostare interattività in componenti figli**

```typescript
// BEFORE - Client Component
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function ProductPage({ params }: { params: { id: string } }) {
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetch(`/api/products/${params.id}`)
      .then(r => r.json())
      .then(data => {
        setProduct(data)
        setLoading(false)
      })
  }, [params.id])

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h1>{product.name}</h1>
      <button onClick={() => router.push('/products')}>Back</button>
    </div>
  )
}

// AFTER - Server Component + Client Component

// ProductPage.tsx (Server Component)
import { db } from '@/lib/db'
import { BackButton } from './BackButton'

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const product = await db.product.findById(id)

  if (!product) {
    notFound()
  }

  return (
    <div>
      <h1>{product.name}</h1>
      <BackButton /> {/* Client component per interattività */}
    </div>
  )
}

// BackButton.tsx (Client Component)
'use client'

import { useRouter } from 'next/navigation'

export function BackButton() {
  const router = useRouter()
  return <button onClick={() => router.back()}>Back</button>
}
```

---

## Accesso a Risorse Server-side

### Database Access

```typescript
// lib/db.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma: PrismaClient }

export const db = globalForPrisma.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db

// Uso nel componente
import { db } from '@/lib/db'

export default async function Page() {
  // Query diretta - nessuna API route necessaria
  const users = await db.user.findMany()
  // ...
}
```

### File System

```typescript
import { readFile } from 'fs/promises'
import path from 'path'

export default async function Page() {
  const filePath = path.join(process.cwd(), 'content', 'about.md')
  const content = await readFile(filePath, 'utf-8')

  return <Markdown content={content} />
}
```

### Environment Variables

```typescript
// Server Components possono accedere a tutte le env vars
export default async function Page() {
  // ✅ Accesso diretto alle variabili server
  const apiKey = process.env.API_SECRET_KEY
  const dbUrl = process.env.DATABASE_URL

  const data = await fetch('https://api.example.com/data', {
    headers: { Authorization: `Bearer ${apiKey}` },
  })

  // ...
}
```

---

## Errori Comuni

```typescript
// ❌ NON: Usare browser APIs in Server Component
export default function Page() {
  const width = window.innerWidth // ❌ window non esiste sul server
  localStorage.getItem('key')     // ❌ localStorage non esiste sul server
}

// ✅ SÌ: Spostare in Client Component
'use client'
export function WindowSize() {
  const [width, setWidth] = useState(window.innerWidth)
  // ...
}

// ❌ NON: Usare hooks in Server Component
export default function Page() {
  const [count, setCount] = useState(0) // ❌ Hook non funzionano
  useEffect(() => {...}, [])            // ❌
}

// ❌ NON: Dimenticare di gestire errori
export default async function Page() {
  const data = await fetchData() // Può lanciare
  // ...
}

// ✅ SÌ: Gestire errori
export default async function Page() {
  try {
    const data = await fetchData()
    return <DataView data={data} />
  } catch (error) {
    return <ErrorMessage />
  }
}

// ❌ NON: Troppi Client Components annidati
// ServerComponent
//   → ClientComponent1
//     → ClientComponent2
//       → ClientComponent3

// ✅ SÌ: Mantenere Client Components il più in basso possibile
// ServerComponent
//   → ServerComponent
//     → ServerComponent
//       → ClientComponent (solo dove necessario)
```
