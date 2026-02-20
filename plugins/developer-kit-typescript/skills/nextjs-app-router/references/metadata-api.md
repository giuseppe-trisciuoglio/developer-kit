# Metadata API

## Static Metadata

```tsx
// app/layout.tsx o app/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My App",
  description: "A great application built with Next.js",

  openGraph: {
    title: "My App",
    description: "A great application",
    type: "website",
    url: "https://myapp.com",
    images: [
      {
        url: "https://myapp.com/og.png",
        width: 1200,
        height: 630,
        alt: "My App",
      },
    ],
  },

  twitter: {
    card: "summary_large_image",
    title: "My App",
    description: "A great application",
    images: ["https://myapp.com/twitter.png"],
  },

  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },

  icons: {
    icon: "/favicon.ico",
    shortcut: "/shortcut-icon.png",
    apple: "/apple-icon.png",
  },

  manifest: "/manifest.json",

  alternates: {
    canonical: "https://myapp.com",
    languages: {
      "en-US": "https://myapp.com/en",
      "de-DE": "https://myapp.com/de",
    },
  },
};
```

## Dynamic Metadata (generateMetadata)

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata, ResolvingMetadata } from "next";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata(
  { params }: PageProps,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const { slug } = await params;
  const post = await fetchPost(slug);

  // Access parent metadata
  const previousImages = (await parent).openGraph?.images || [];

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage, ...previousImages],
      type: "article",
      publishedTime: post.publishedAt,
      authors: [post.author.name],
    },
  };
}
```

## Metadata Template (layout)

```tsx
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    template: "%s | My App",
    default: "My App - Tagline here",
  },
  description: "Default description",
};
```

```tsx
// app/blog/page.tsx
import type { Metadata } from "next";

// Risultato: "Blog | My App"
export const metadata: Metadata = {
  title: "Blog",
};
```

## Metadata per Segmento

```tsx
// app/layout.tsx (root)
export const metadata: Metadata = {
  title: "My App",
  description: "Root description",
};
```

```tsx
// app/blog/layout.tsx
export const metadata: Metadata = {
  title: "Blog",
  description: "Blog posts and articles",
};
```

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  return {
    title: `Post: ${slug}`, // Combina con template del layout
  };
}
```

## viewport Export (Separato)

```tsx
// app/layout.tsx
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "My App",
  // ...
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
};
```

## File-Based Metadata

### favicon.ico e icon.ico

Posizionare nella stessa carta del segmento:

```
app/
├── favicon.ico      → /favicon.ico
├── icon.png         → /icon.png
└── blog/
    └── icon.png     → /blog/icon.png (dynamic)
```

### Dynamic Icon/OG Image

```tsx
// app/icon.tsx
import { ImageResponse } from "next/og";

export const runtime = "edge";

export const size = {
  width: 32,
  height: 32,
};

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 24,
          background: "black",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
        }}
      >
        A
      </div>
    ),
    size
  );
}
```

```tsx
// app/opengraph-image.tsx
import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "About Acme";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 128,
          background: "white",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        About Acme
      </div>
    ),
    size
  );
}
```

## robots.txt

### Static

Crea `app/robots.txt`:

```
User-Agent: *
Allow: /
Disallow: /admin/

Sitemap: https://myapp.com/sitemap.xml
```

### Dynamic

```tsx
// app/robots.ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "Googlebot",
        allow: "/",
        disallow: "/admin/",
      },
      {
        userAgent: "*",
        allow: "/",
        disallow: "/private/",
      },
    ],
    sitemap: "https://myapp.com/sitemap.xml",
  };
}
```

## sitemap.xml

### Static

Crea `app/sitemap.xml`:

```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://myapp.com</loc>
    <lastmod>2024-01-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1</priority>
  </url>
</urlset>
```

### Dynamic

```tsx
// app/sitemap.ts
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await fetchPosts();

  const postUrls = posts.map((post) => ({
    url: `https://myapp.com/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

  return [
    {
      url: "https://myapp.com",
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    ...postUrls,
  ];
}
```

## Structured Data (JSON-LD)

```tsx
// app/page.tsx
export default function Page() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "My Company",
    url: "https://myapp.com",
    logo: "https://myapp.com/logo.png",
    sameAs: [
      "https://twitter.com/mycompany",
      "https://linkedin.com/company/mycompany",
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main>{/* Content */}</main>
    </>
  );
}
```

```tsx
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: PageProps) {
  const { slug } = await params;
  const post = await fetchPost(slug);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    datePublished: post.publishedAt,
    dateModified: post.updatedAt,
    author: {
      "@type": "Person",
      name: post.author.name,
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article>{/* Content */}</article>
    </>
  );
}
```
