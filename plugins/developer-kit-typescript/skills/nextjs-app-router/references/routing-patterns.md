# Routing Patterns

## File Conventions

| File | Descrizione |
|------|-------------|
| `page.tsx` | Pagina pubblica accessibile tramite URL |
| `layout.tsx` | Layout condiviso che wrappa i page |
| `loading.tsx` | UI di caricamento durante fetch dati |
| `error.tsx` | UI per gestione errori |
| `not-found.tsx` | UI per 404 |
| `template.tsx` | Layout re-mounted su navigazione |
| `default.tsx` | Fallback per parallel routes |
| `route.ts` | API Route Handler |

## Parallel Routes (@slot)

Permettono di renderizzare più pagine nello stesso layout simultaneamente.

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode;
  team: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {team}
        {analytics}
      </div>
    </div>
  );
}
```

```tsx
// app/dashboard/@team/page.tsx
export default function TeamPage() {
  return <div>Team Section</div>;
}
```

```tsx
// app/dashboard/@analytics/page.tsx
export default function AnalyticsPage() {
  return <div>Analytics Section</div>;
}
```

## Intercepting Routes

Permettono di intercettare route e mostrarle in modalità diversa (es: modal).

| Pattern | Intercetta |
|---------|-----------|
| `(.)` | Stesso livello |
| `(..)` | Un livello sopra |
| `(..)(..)` | Due livelli sopra |
| `(...)` | Root |

```
app/
├── feed/
│   └── page.tsx
└── feed/
    └── @modal/
        └── (.)photo/
            └── [id]/
                └── page.tsx  <- Intercetta /feed/photo/[id]
```

## Route Groups

Organizzano route senza influenzare l'URL (usando parentesi).

```
app/
├── (marketing)/
│   ├── about/
│   │   └── page.tsx      -> /about
│   └── contact/
│       └── page.tsx      -> /contact
├── (shop)/
│   ├── products/
│   │   └── page.tsx      -> /products
│   └── cart/
│       └── page.tsx      -> /cart
└── layout.tsx
```

## Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function BlogPost({ params }: PageProps) {
  const { slug } = await params;
  // Use slug...
}

// Catch-all
// app/docs/[...slug]/page.tsx

// Optional catch-all
// app/docs/[[...slug]]/page.tsx
```

## Generate Static Params

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await fetchPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}

// Con multiple dynamic segments
export async function generateStaticParams() {
  const products = await fetchProducts();

  return products.map((product) => ({
    category: product.category,
    id: product.id,
  }));
}
```
