# Server Components and Client Components Guide

## Component Boundary Rules

### When to Use Server Components (Default)
Server Components are the default in Next.js App Router. Use them when:
- Fetching data from databases or APIs
- Accessing server-side resources (file system, environment variables)
- Rendering static content that doesn't need interactivity
- Keeping sensitive logic (API keys, database queries) on the server
- Reducing client-side JavaScript bundle size

### When to Use Client Components ('use client')
Add `'use client'` directive only when the component needs:
- Event handlers (`onClick`, `onChange`, `onSubmit`)
- React hooks (`useState`, `useEffect`, `useRef`, `useContext`)
- Browser-only APIs (`window`, `document`, `localStorage`)
- Third-party libraries that use React hooks or browser APIs

## Boundary Placement Strategy

### Push 'use client' Down the Tree
The `'use client'` directive creates a boundary — everything imported by a Client Component becomes client-side code. Place boundaries as deep as possible.

```tsx
// ❌ Bad: Entire page is a Client Component
'use client';

export default function ProductPage({ params }) {
  const [quantity, setQuantity] = useState(1);
  const product = useProductQuery(params.id); // Client-side fetch
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <QuantitySelector value={quantity} onChange={setQuantity} />
    </div>
  );
}

// ✅ Good: Only interactive part is a Client Component
// page.tsx (Server Component)
export default async function ProductPage({ params }) {
  const { id } = await params;
  const product = await getProduct(id); // Server-side fetch
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <QuantitySelector productId={product.id} />
    </div>
  );
}

// quantity-selector.tsx (Client Component)
'use client';
export function QuantitySelector({ productId }: { productId: string }) {
  const [quantity, setQuantity] = useState(1);
  return <input type="number" value={quantity} onChange={e => setQuantity(+e.target.value)} />;
}
```

## Data Passing Patterns

### Server to Client: Props
Pass serializable data from Server Components to Client Components via props.

```tsx
// Server Component
export default async function Page() {
  const user = await getUser(); // Fetched on server
  return <UserCard user={user} />; // Passed as prop
}

// Client Component
'use client';
function UserCard({ user }: { user: User }) {
  const [editing, setEditing] = useState(false);
  return <div>{user.name}</div>;
}
```

### Server to Client: Children Pattern
Pass Server Components as children to Client Components.

```tsx
// Client Component wrapper
'use client';
function Accordion({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(!open)}>Toggle</button>
      {open && children}
    </div>
  );
}

// Server Component using client wrapper
export default async function FAQ() {
  const faqs = await getFAQs();
  return (
    <Accordion>
      {/* These remain Server Components */}
      {faqs.map(faq => <FAQItem key={faq.id} faq={faq} />)}
    </Accordion>
  );
}
```

## Common Mistakes

### Importing Server-Only Code in Client Components

```tsx
// ❌ Error: Server-only code imported in client
'use client';
import { db } from '@/lib/db'; // Database client in client component!

// ✅ Fix: Use server-only package to prevent accidental imports
// lib/db.ts
import 'server-only';
import { PrismaClient } from '@prisma/client';
export const db = new PrismaClient();
```

### Serialization Errors
Client Components can only receive serializable props (no functions, Date objects, Maps, etc.).

```tsx
// ❌ Error: Non-serializable prop
<ClientComponent
  onClick={() => console.log('click')} // Functions can't be serialized
  date={new Date()} // Date objects can't be serialized
/>

// ✅ Fix: Serialize data, handle events client-side
<ClientComponent
  dateString={date.toISOString()} // Serializable string
/>
```

### Unnecessary 'use client' on Components Without Interactivity

```tsx
// ❌ Unnecessary: No hooks or event handlers
'use client';
function Footer() {
  return <footer>© 2024 My App</footer>;
}

// ✅ Fix: Remove 'use client' — this is pure rendering
function Footer() {
  return <footer>© 2024 My App</footer>;
}
```

## Third-Party Library Integration

### Context Providers
Wrap context providers in a Client Component at the layout level.

```tsx
// app/providers.tsx
'use client';

import { ThemeProvider } from 'next-themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}

// app/layout.tsx (Server Component)
import { Providers } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

## Review Checklist for Component Boundaries

- [ ] `'use client'` is only on components that need interactivity
- [ ] `'use client'` is as deep in the component tree as possible
- [ ] Server Components don't import client-only modules
- [ ] Client Components don't import `server-only` modules
- [ ] Props passed from Server to Client Components are serializable
- [ ] Context providers are wrapped in a dedicated Client Component
- [ ] Data fetching happens in Server Components, not Client Components
- [ ] Sensitive data (API keys, secrets) stays in Server Components only
- [ ] Third-party libraries that use hooks are wrapped in Client Components
