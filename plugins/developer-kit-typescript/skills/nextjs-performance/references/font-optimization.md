# Font Optimization - next/font

## Overview

`next/font` ottimizza automaticamente i font:
- Elimina layout shift (CLS)
- Automatic subsetting
- Preload dei font critici
- Zero runtime JavaScript
- Supporto Google Fonts e font locali

---

## Configurazione Base

### Google Font

```typescript
// BEFORE - Layout shift, FOUT
<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet" />

// AFTER - Zero layout shift
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  )
}
```

### Local Font

```typescript
import localFont from 'next/font/local'

const myFont = localFont({
  src: [
    {
      path: './fonts/Custom-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/Custom-Bold.woff2',
      weight: '700',
      style: 'normal',
    },
    {
      path: './fonts/Custom-Italic.woff2',
      weight: '400',
      style: 'italic',
    },
  ],
  variable: '--font-custom',
  display: 'swap',
})
```

---

## Pattern Comuni

### Multiple Fonts

```typescript
// fonts.ts
import { Inter, Playfair_Display } from 'next/font/google'

export const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
})

// app/layout.tsx
import { inter, playfair } from './fonts'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  )
}

// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        serif: ['var(--font-playfair)', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}

export default config
```

### Font con Tailwind CSS v4

```css
/* app/globals.css con Tailwind v4 */
@import "tailwindcss";

@theme {
  --font-sans: var(--font-inter), ui-sans-serif, system-ui;
  --font-serif: var(--font-playfair), ui-serif, Georgia;
}
```

### Variable Fonts (Consigliato)

```typescript
// BEFORE - Multipli file per ogni weight
// AFTER - Un solo file per tutti i weight
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  // Inter è una variable font - un solo file
})

// Uso con qualsiasi weight
<p className="font-sans font-light">Light text</p>
<p className="font-sans font-normal">Normal text</p>
<p className="font-sans font-bold">Bold text</p>
```

### Font Ottimizzati per Performance

```typescript
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  // Aggiungi preconnect per velocizzare il download
  adjustFontFallback: true, // Font fallback ottimizzato
})

// Preconnect in layout
export const metadata = {
  other: {
    preconnect: ['https://fonts.googleapis.com', 'https://fonts.gstatic.com'],
  },
}
```

---

## Ottimizzazioni Avanzate

### Preload Font Critici

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        {/* Preload del font critico */}
        <link
          rel="preload"
          href="/fonts/custom-font.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### Font con CSS Fallback Ottimizzato

```typescript
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  // Next.js genera automaticamente un fallback ottimizzato
  // basato sulle metriche del font scelto
  adjustFontFallback: true,
})

// CSS personalizzato per ridurre FOUT
// globals.css
@font-face {
  font-family: 'Inter Fallback';
  src: local('Arial');
  ascent-override: 90.49%;
  descent-override: 22.52%;
  line-gap-override: 0%;
  size-adjust: 107.06%;
}
```

### Font Condizionali per Lingue

```typescript
// app/[lang]/layout.tsx
import { Inter, Noto_Sans_JP } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const notoJP = Noto_Sans_JP({ subsets: ['latin'], variable: '--font-noto-jp' })

export default function RootLayout({
  children,
  params: { lang },
}: {
  children: React.ReactNode
  params: { lang: string }
}) {
  const fontClass = lang === 'ja' ? notoJP.variable : inter.variable
  const bodyClass = lang === 'ja' ? notoJP.className : inter.className

  return (
    <html lang={lang} className={fontClass}>
      <body className={bodyClass}>{children}</body>
    </html>
  )
}
```

---

## Errori Comuni

```typescript
// ❌ NON: Importare il CSS dei font manualmente
import 'google-fonts/inter.css'

// ✅ SÌ: Usare sempre next/font
import { Inter } from 'next/font/google'

// ❌ NON: Dimenticare subsets (aumenta dimensione)
const inter = Inter({}) // Carica tutti i caratteri

// ✅ SÌ: Specificare subsets
const inter = Inter({ subsets: ['latin'] })

// ❌ NON: Usare display: block (no text visibile durante il load)
const inter = Inter({ display: 'block' })

// ✅ SÌ: Usare swap per immediate text render
const inter = Inter({ display: 'swap' })

// ❌ NON: Importare font in ogni componente
// components/Button.tsx
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'] }) // ❌ Doppio caricamento

// ✅ SÌ: Importare una sola volta in layout
// app/layout.tsx
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'] })
```

---

## Performance Checklist

- [ ] Usare `subsets` per ridurre dimensione font
- [ ] Preferire variable fonts quando disponibili
- [ ] Usare `display: 'swap'` per evitare invisible text
- [ ] Aggiungere `variable` per CSS custom properties
- [ ] Configurare Tailwind per usare le variabili CSS
- [ ] Preconnect a fonts.googleapis.com e fonts.gstatic.com
- [ ] Usare `adjustFontFallback: true` per ridurre CLS
