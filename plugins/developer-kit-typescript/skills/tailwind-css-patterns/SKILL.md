---
name: tailwind-css-patterns
version: 2.2.0
description: Provides comprehensive Tailwind CSS utility-first styling patterns including responsive design, layout utilities, flexbox, grid, spacing, typography, colors, and modern CSS best practices. Use when styling React/Vue/Svelte components, building responsive layouts, implementing design systems, or optimizing CSS workflow.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
category: frontend
tags: [tailwind, css, responsive, design-system, react, nextjs]
---

# Tailwind CSS Development Patterns

## Overview

Expert guide for building modern, responsive user interfaces with Tailwind CSS utility-first framework. Covers v4.1+ features including CSS-first configuration, custom utilities, and enhanced developer experience.

## When to Use

- Styling React/HTML components with utility classes
- Building responsive layouts with breakpoints
- Implementing flexbox and grid layouts
- Managing spacing, colors, and typography
- Creating custom design systems
- Optimizing for mobile-first design
- Building dark mode interfaces

## Instructions

1. **Start Mobile-First**: Write base styles for mobile, add responsive prefixes for larger screens
2. **Use Design Tokens**: Leverage Tailwind's spacing, color, and typography scales
3. **Compose Utilities**: Combine multiple utilities for complex styles
4. **Extract Components**: Create reusable component classes for repeated patterns
5. **Configure Theme**: Customize design tokens in tailwind.config.js or @theme directive
6. **Optimize for Production**: Ensure content paths are configured for CSS purging

## Examples

### Responsive Card Component

```tsx
function ProductCard({ product }: { product: Product }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden sm:flex sm:max-w-2xl">
      <img className="h-48 w-full object-cover sm:h-auto sm:w-48" src={product.image} alt={product.name} />
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
        <p className="mt-2 text-gray-600">{product.description}</p>
        <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
```

### Breakpoint Prefixes

- `sm:` - 640px+
- `md:` - 768px+
- `lg:` - 1024px+
- `xl:` - 1280px+
- `2xl:` - 1536px+

### Core Layout Patterns

```html
<!-- Flexbox center -->
<div class="flex items-center justify-center min-h-screen">Centered</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">...</div>

<!-- Container -->
<div class="container mx-auto px-4 max-w-7xl">...</div>

<!-- Dark mode -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">...</div>
```

## Constraints and Warnings

- **Class Proliferation**: Long class strings can reduce readability; extract components when needed
- **Purge Configuration**: Must configure content paths correctly for production builds
- **Arbitrary Values**: Use sparingly; prefer design tokens for consistency
- **Dark Mode**: Requires proper configuration (class or media strategy)
- **JIT Mode**: Some dynamic patterns may not be detected; use safelist if needed

## Best Practices

1. **Mobile-First**: Start with mobile styles, add responsive prefixes
2. **Consistent Spacing**: Use Tailwind's spacing scale (4, 8, 12, 16, etc.)
3. **Color Palette**: Stick to Tailwind's color system for consistency
4. **Component Extraction**: Extract repeated patterns into components
5. **Semantic HTML**: Use proper HTML elements with Tailwind classes
6. **Accessibility**: Include focus styles, ARIA labels, and respect user preferences
7. **CSS-First Config**: Use @theme directive for v4.1+ instead of JavaScript config

## References

Consult these files for detailed patterns and examples:

- **[references/examples.md](references/examples.md)** - Component patterns (cards, navbars, forms, modals), responsive layouts, animations, dark mode
- **[references/reference.md](references/reference.md)** - Configuration (v4.1 @theme, legacy JS config, Vite integration), spacing, typography, colors, accessibility, performance optimization

### External References
- Tailwind CSS Docs: https://tailwindcss.com/docs
- Tailwind UI: https://tailwindui.com
- Tailwind Play: https://play.tailwindcss.com
- Headless UI: https://headlessui.com
