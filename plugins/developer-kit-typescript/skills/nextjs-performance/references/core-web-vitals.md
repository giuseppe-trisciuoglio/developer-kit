# Core Web Vitals - Next.js Optimization

## Overview

Core Web Vitals (CWV) sono le metriche di performance critiche per l'esperienza utente e il SEO.

| Metrica | Target | Ottimizzazione Principale |
|---------|--------|---------------------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | Ottimizzare l'elemento più grande visibile |
| **INP** (Interaction to Next Paint) | < 200ms | Minimizzare JS sul thread principale |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Riservare spazio per elementi dinamici |

---

## LCP Optimization

### Elementi che contribuiscono a LCP
1. `<img>` elementi
2. `<image>` dentro SVG
3. Video poster
4. Elementi con background-image
5. Block-level text elements

### Strategie Next.js

```typescript
// BEFORE - LCP lento
<img src="/hero.jpg" width={1200} height={600} />

// AFTER - LCP ottimizzato
import Image from 'next/image'

// Priority carica l'immagine con fetchpriority="high"
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority  // ← Essenziale per LCP
  quality={80}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### Preload Critical Resources

```typescript
// app/layout.tsx
export const metadata = {
  other: {
    preconnect: ['https://fonts.googleapis.com'],
    dnsPrefetch: ['https://api.example.com'],
  },
}

// O con next/head in page router
import Head from 'next/head'

<Head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="dns-prefetch" href="https://api.example.com" />
</Head>
```

---

## INP Optimization

### Strategie

1. **Spostare logica pesante su Web Workers**
2. **Utilizzare Server Components per ridurre JS client**
3. **Debouncing/Throttling degli event handlers**

```typescript
// BEFORE - INP alto
<button onClick={() => heavyComputation()}>Click</button>

// AFTER - INP ottimizzato
'use client'

import { useTransition } from 'react'

export function OptimizedButton() {
  const [isPending, startTransition] = useTransition()

  const handleClick = () => {
    startTransition(() => {
      heavyComputation()
    })
  }

  return (
    <button onClick={handleClick} disabled={isPending}>
      {isPending ? 'Processing...' : 'Click'}
    </button>
  )
}
```

---

## CLS Optimization

### Pattern comuni che causano CLS

```typescript
// BEFORE - CLS alto
// Immagine senza dimensioni
<img src="/photo.jpg" />

// Font che cambia durante il load
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter');
</style>

// AFTER - CLS zero
import Image from 'next/image'
import { Inter } from 'next/font/google'

// Font ottimizzato con display: swap gestito automaticamente
const inter = Inter({ subsets: ['latin'] })

// Immagine con dimensioni esplicite
<Image
  src="/photo.jpg"
  alt="Photo"
  width={800}
  height={600}
  // O con fill per layout responsive
  fill
  sizes="(max-width: 768px) 100vw, 800px"
/>
```

### Riservare spazio per contenuti dinamici

```typescript
// BEFORE - Layout shift quando i dati arrivano
export default function Page() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchData().then(setData)
  }, [])

  return <div>{data ? <Content data={data} /> : null}</div>
}

// AFTER - Spazio riservato
export default function Page() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchData().then(setData)
  }, [])

  return (
    <div className="min-h-[400px]">
      {data ? <Content data={data} /> : <Skeleton />}
    </div>
  )
}
```

---

## Monitoring CWV in Next.js

### Vercel Analytics

```bash
npm i @vercel/analytics
```

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
      <Analytics />
    </html>
  )
}
```

### Speed Insights

```bash
npm i @vercel/speed-insights
```

```typescript
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
      <SpeedInsights />
    </html>
  )
}
```

### Web Vitals API (Custom)

```typescript
// app/_components/web-vitals.tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Invia a analytics
    console.log(metric)

    // Esempio: invio a Google Analytics
    if (window.gtag) {
      window.gtag('event', metric.name, {
        value: Math.round(metric.value),
        event_category: 'Web Vitals',
        event_label: metric.id,
        non_interaction: true,
      })
    }
  })

  return null
}
```

---

## Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.13.x
          lhci autorun
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm start",
      "url": ["http://localhost:3000"]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }]
      }
    }
  }
}
```
