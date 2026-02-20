# Bundle Optimization

## Overview

Ottimizzazioni per ridurre il JavaScript bundle e migliorare i tempi di caricamento.

---

## Code Splitting

### Dynamic Imports

```typescript
// BEFORE - Import statico, sempre nel bundle
import HeavyChart from './HeavyChart'

export default function Dashboard() {
  return <HeavyChart />
}

// AFTER - Lazy loaded
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Disabilita SSR se necessario
})

export default function Dashboard() {
  return <HeavyChart />
}
```

### Condizionale Loading

```typescript
'use client'

import dynamic from 'next/dynamic'

const MapComponent = dynamic(() => import('./Map'), {
  ssr: false,
  loading: () => <MapPlaceholder />,
})

export function LocationSection({ showMap }: { showMap: boolean }) {
  // Componente caricato solo quando showMap è true
  return showMap ? <MapComponent /> : null
}
```

### Import con Named Exports

```typescript
const DynamicComponent = dynamic(
  () => import('./components').then((mod) => mod.HeavyChart),
  {
    loading: () => <Loading />,
  }
)
```

---

## Tree Shaking

### Export Named vs Default

```typescript
// ✅ SÌ: Named exports per tree shaking
export { Button, Input, Select }

// ❌ NON: Tutto in un oggetto
export default { Button, Input, Select }

// ❌ NON: Re-export wildcards
export * from 'lodash' // Importa tutto lodash

// ✅ SÌ: Import specifici
import { debounce } from 'lodash-es'
```

### Package.json Side Effects

```json
{
  "name": "my-lib",
  "sideEffects": false,
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  }
}
```

---

## Bundle Analysis

### @next/bundle-analyzer

```bash
npm install --save-dev @next/bundle-analyzer
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  // config
})
```

```bash
ANALYZE=true npm run build
```

---

## Ottimizzazioni Librerie

### Modular Imports (MUI)

```javascript
// next.config.js
module.exports = {
  modularizeImports: {
    '@mui/material': {
      transform: '@mui/material/{{member}}',
    },
    '@mui/icons-material': {
      transform: '@mui/icons-material/{{member}}',
    },
    lodash: {
      transform: 'lodash/{{member}}',
    },
  },
}
```

### ESM over CommonJS

```typescript
// ❌ NON: CommonJS
const lodash = require('lodash')

// ✅ SÌ: ESM
import { debounce } from 'lodash-es'

// next.config.js per preferire ESM
module.exports = {
  experimental: {
    esmExternals: true,
  },
}
```

---

## Ottimizzazione Dependencies

```bash
# Analizza bundle
npx webpack-bundle-analyzer .next/stats.json

# Trova duplicate dependencies
npx depcheck

# Bundle size check
npm run build 2>&1 | grep -E "(First Load JS|/api)"
```

### next.config.js Ottimizzazioni

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ottimizzazione webpack
  webpack: (config, { isServer }) => {
    // Split chunks più aggressivo
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        commons: {
          name: 'commons',
          chunks: 'initial',
          minChunks: 2,
        },
      },
    }

    return config
  },

  // Ottimizzazioni build
  swcMinify: true,

  // Compressione
  compress: true,
}

module.exports = nextConfig
```

---

## Best Practices

```typescript
// ✅ SÌ: Lazy load componenti pesanti
const HeavyEditor = dynamic(() => import('./Editor'), { ssr: false })

// ✅ SÌ: Intersection Observer per below-fold
'use client'
import { useEffect, useRef, useState } from 'react'

export function LazyComponent({ component: Component }) {
  const [shouldLoad, setShouldLoad] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setShouldLoad(true)
        observer.disconnect()
      }
    })

    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  return <div ref={ref}>{shouldLoad ? <Component /> : <Placeholder />}</div>
}

// ✅ SÌ: Prefetch route importante
import Link from 'next/link'

<Link href="/dashboard" prefetch={true}>Dashboard</Link>

// ❌ NON: Prefetch tutto
<Link href="/rarely-used" prefetch={true}>Rare</Link>
```
