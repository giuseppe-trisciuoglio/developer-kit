# shadcn/ui - Next.js Integration

## App Router Setup

Most shadcn/ui components require `"use client"` directive when used with App Router. Static display components (Card, Table) can work in Server Components without the directive.

```tsx
// src/components/ui/button.tsx — already includes "use client" after npx shadcn@latest add button
"use client"
import * as React from "react"
// ... rest of component
```

## Root Layout with Toaster

```tsx
// app/layout.tsx
import { Inter } from "next/font/google"
import { Toaster } from "@/components/ui/toaster"
import { cn } from "@/lib/utils"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn("min-h-screen bg-background font-sans antialiased", inter.className)}>
        {children}
        <Toaster />
      </body>
    </html>
  )
}
```

## Server Components with Interactive Elements

When using interactive shadcn/ui components in Server Components, wrap them in a Client Component:

```tsx
// app/dashboard/page.tsx — Server Component
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ButtonClient } from "@/components/button-client"

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <ButtonClient>Interactive Button</ButtonClient>
        </CardContent>
      </Card>
    </div>
  )
}
```

```tsx
// src/components/button-client.tsx — Client Component wrapper
"use client"
import { Button } from "@/components/ui/button"

export function ButtonClient(props: React.ComponentProps<typeof Button>) {
  return <Button {...props} />
}
```

## Metadata with shadcn/ui Pages

```tsx
// app/layout.tsx
import { Metadata } from "next"

export const metadata: Metadata = {
  title: { default: "My App", template: "%s | My App" },
  description: "Built with shadcn/ui and Next.js",
}
```

```tsx
// app/about/page.tsx
import { Metadata } from "next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export const metadata: Metadata = {
  title: "About Us",
  description: "Learn more about our company",
}

export default function AboutPage() {
  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader><CardTitle>About Our Company</CardTitle></CardHeader>
        <CardContent>
          <p>We build amazing products with modern web technologies.</p>
        </CardContent>
      </Card>
    </div>
  )
}
```

## Dark Mode Setup

### With next-themes

```bash
npm install next-themes
```

```tsx
// components/theme-provider.tsx
"use client"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children, ...props }) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Theme Toggle Component

```tsx
"use client"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Moon, Sun } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  return (
    <Button variant="ghost" size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```
