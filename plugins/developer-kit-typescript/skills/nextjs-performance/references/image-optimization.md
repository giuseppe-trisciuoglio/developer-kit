# Image Optimization - next/image

## Overview

Next.js fornisce un componente `Image` ottimizzato che:
- Ottimizza automaticamente le immagini
- Serve formati moderni (WebP, AVIF)
- Responsive images automatiche
- Lazy loading nativo
- Previene layout shift

---

## Configurazione Base

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // Domini esterni consentiti
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.example.com',
        port: '',
        pathname: '/images/**',
      },
    ],
    // Formati supportati (ordine di preferenza)
    formats: ['image/avif', 'image/webp'],
    // Qualità di default (1-100)
    quality: 75,
    // Dimensioni per responsive images
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
}

module.exports = nextConfig
```

---

## Pattern Comuni

### 1. Immagine Hero (LCP)

```typescript
// BEFORE
<img src="/hero.jpg" className="w-full h-auto" />

// AFTER
import Image from 'next/image'

export function Hero() {
  return (
    <div className="relative w-full h-[600px]">
      <Image
        src="/hero.jpg"
        alt="Hero image"
        fill
        priority  // ← Disabilita lazy loading per LCP
        quality={85}
        className="object-cover"
        sizes="100vw"
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      />
    </div>
  )
}
```

### 2. Immagini Responsive

```typescript
// BEFORE - Stessa immagine per tutti i device
<img src="/photo-large.jpg" />

// AFTER - Immagini adattive
import Image from 'next/image'

export function ResponsiveImage() {
  return (
    <Image
      src="/photo.jpg"
      alt="Photo"
      width={800}
      height={600}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px"
      // Genera srcset automaticamente:
      // 640w, 750w, 828w, 1080w, 1200w...
    />
  )
}
```

### 3. Grid di Immagini

```typescript
// AFTER - Grid ottimizzata
import Image from 'next/image'

export function ImageGrid({ images }: { images: { src: string; alt: string }[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {images.map((img, i) => (
        <div key={i} className="relative aspect-square">
          <Image
            src={img.src}
            alt={img.alt}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            className="object-cover rounded-lg"
            loading={i < 3 ? 'eager' : 'lazy'}  // Prime 3 eager, resto lazy
          />
        </div>
      ))}
    </div>
  )
}
```

### 4. Immagini da CMS/CDN Esterno

```typescript
// AFTER - Configurazione con loader personalizzato
import Image from 'next/image'

// Se il CMS ha le sue ottimizzazioni
const contentfulLoader = ({ src, width, quality }: {
  src: string
  width: number
  quality?: number
}) => {
  return `${src}?w=${width}&q=${quality || 75}&fm=webp`
}

export function CMSImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      loader={contentfulLoader}
      src={src}
      alt={alt}
      width={800}
      height={600}
    />
  )
}
```

---

## Placeholder e Loading States

### Blur Placeholder

```typescript
// Generare blurDataURL (lato build o API)
import { getPlaiceholder } from 'plaiceholder'

async function getBlurData(src: string) {
  const buffer = await fetch(src).then(async (res) =>
    Buffer.from(await res.arrayBuffer())
  )
  const { base64 } = await getPlaiceholder(buffer)
  return base64
}

// Uso nel componente
export async function ImageWithBlur({ src, alt }: { src: string; alt: string }) {
  const blurDataURL = await getBlurData(src)

  return (
    <Image
      src={src}
      alt={alt}
      width={800}
      height={600}
      placeholder="blur"
      blurDataURL={blurDataURL}
    />
  )
}
```

### Color Placeholder

```typescript
<Image
  src="/photo.jpg"
  alt="Photo"
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3Crect width='1' height='1' fill='%23e2e8f0'/%3E%3C/svg%3E"
/>
```

---

## Art Direction (Picture Element)

```typescript
// BEFORE - Stessa immagine per tutti
<img src="/landscape.jpg" />

// AFTER - Art direction con picture
export function ArtDirectedImage() {
  return (
    <picture>
      {/* Mobile: portrait crop */}
      <source
        media="(max-width: 768px)"
        srcSet="/photo-mobile.jpg"
        width={400}
        height={600}
      />
      {/* Tablet: square crop */}
      <source
        media="(max-width: 1024px)"
        srcSet="/photo-tablet.jpg"
        width={600}
        height={600}
      />
      {/* Desktop: full image */}
      <img
        src="/photo-desktop.jpg"
        alt="Responsive photo"
        width={1200}
        height={800}
      />
    </picture>
  )
}
```

---

## Ottimizzazione Avanzata

### Preload Critical Images

```typescript
// app/page.tsx
import Image from 'next/image'

export default function Page() {
  return (
    <>
      {/* Preload per immagine LCP */}
      <link
        rel="preload"
        href="/hero.jpg"
        as="image"
        type="image/jpeg"
      />

      <Image
        src="/hero.jpg"
        alt="Hero"
        width={1200}
        height={600}
        priority
      />
    </>
  )
}
```

### SVG come Componenti (non come img)

```typescript
// BEFORE - SVG come img (non ottimale)
<Image src="/icon.svg" width={24} height={24} />

// AFTER - SVG inline per animazioni e styling
import Icon from './icon.svg'

export function Button() {
  return (
    <button>
      <Icon className="w-6 h-6 text-blue-500" />
    </button>
  )
}

// next.config.js per supportare SVG come componenti
const nextConfig = {
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })
    return config
  },
}
```

### Client-side Image Loading (con fallback)

```typescript
'use client'

import Image from 'next/image'
import { useState } from 'react'

export function SafeImage({
  src,
  alt,
  fallback = '/placeholder.jpg',
  ...props
}: {
  src: string
  alt: string
  fallback?: string
} & React.ComponentProps<typeof Image>) {
  const [imgSrc, setImgSrc] = useState(src)

  return (
    <Image
      {...props}
      src={imgSrc}
      alt={alt}
      onError={() => setImgSrc(fallback)}
    />
  )
}
```

---

## Errori Comuni da Evitare

```typescript
// ❌ NON: Usare width/height stringhe
<Image src="/photo.jpg" width="100%" height="auto" />

// ✅ SÌ: Usare numeri (px) o fill con parent sized
<Image src="/photo.jpg" width={800} height={600} />
// oppure
<div className="relative w-full h-64">
  <Image src="/photo.jpg" fill />
</div>

// ❌ NON: Dimenticare alt text
<Image src="/photo.jpg" width={800} height={600} />

// ✅ SÌ: Sempre fornire alt significativo
<Image src="/photo.jpg" alt="Gatto che dorme sul divano" width={800} height={600} />

// ❌ NON: Usare priority su tutte le immagini
<Image src="/photo1.jpg" priority />
<Image src="/photo2.jpg" priority />
<Image src="/photo3.jpg" priority />

// ✅ SÌ: Priority solo per LCP image
<Image src="/hero.jpg" priority />
<Image src="/photo1.jpg" loading="lazy" />
<Image src="/photo2.jpg" loading="lazy" />
```
