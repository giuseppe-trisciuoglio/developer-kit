# Route Handlers Ottimizzati

## Overview

Route handlers in `app/` directory per API endpoints con supporto streaming e edge runtime.

---

## Pattern Base

### GET Handler

```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-static'
export const revalidate = 3600

export async function GET() {
  const users = await db.user.findMany()
  return NextResponse.json(users)
}
```

### POST Handler

```typescript
// app/api/users/route.ts
export async function POST(request: Request) {
  try {
    const body = await request.json()

    const user = await db.user.create({
      data: body,
    })

    return NextResponse.json(user, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    )
  }
}
```

---

## Edge Runtime

```typescript
// app/api/edge/route.ts
export const runtime = 'edge'
export const preferredRegion = 'iad1' // US East

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get('q')

  // Edge runtime: minore cold start, distribuito globalmente
  const result = await fetch(`https://api.example.com/search?q=${query}`)

  return new Response(await result.text(), {
    headers: { 'content-type': 'application/json' },
  })
}
```

---

## Streaming Response

```typescript
// app/api/stream/route.ts
export const runtime = 'edge'

export async function POST(request: Request) {
  const { prompt } = await request.json()

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      stream: true,
    }),
  })

  // Stream la response direttamente
  return new Response(response.body, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

---

## Caching Headers

```typescript
// app/api/data/route.ts
export async function GET() {
  const data = await fetchData()

  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
    },
  })
}

// Con ETag
export async function GET(request: Request) {
  const data = await fetchData()
  const etag = generateETag(data)

  // Check If-None-Match
  if (request.headers.get('If-None-Match') === etag) {
    return new Response(null, { status: 304 })
  }

  return NextResponse.json(data, {
    headers: {
      ETag: etag,
      'Cache-Control': 'public, max-age=3600',
    },
  })
}
```

---

## Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // CORS headers
  const response = NextResponse.next()

  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  // Rate limiting semplice
  const ip = request.ip ?? 'anonymous'
  const limit = await checkRateLimit(ip)

  if (!limit.success) {
    return new NextResponse('Rate limit exceeded', { status: 429 })
  }

  return response
}

export const config = {
  matcher: '/api/:path*',
}
```

---

## Error Handling

```typescript
// app/api/error-handler.ts
import { NextResponse } from 'next/server'

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code: string = 'INTERNAL_ERROR'
  ) {
    super(message)
  }
}

export function handleError(error: unknown) {
  if (error instanceof APIError) {
    return NextResponse.json(
      { error: error.message, code: error.code },
      { status: error.statusCode }
    )
  }

  console.error(error)
  return NextResponse.json(
    { error: 'Internal server error', code: 'INTERNAL_ERROR' },
    { status: 500 }
  )
}

// Uso
import { APIError, handleError } from './error-handler'

export async function GET() {
  try {
    const data = await fetchData()
    if (!data) {
      throw new APIError('Not found', 404, 'NOT_FOUND')
    }
    return NextResponse.json(data)
  } catch (error) {
    return handleError(error)
  }
}
```

---

## Route Groups

```typescript
// app/api/(public)/health/route.ts
export async function GET() {
  return NextResponse.json({ status: 'ok', timestamp: Date.now() })
}

// app/api/(private)/admin/route.ts
export async function GET() {
  // Protetto da middleware auth
  return NextResponse.json({ data: 'sensitive' })
}
```
