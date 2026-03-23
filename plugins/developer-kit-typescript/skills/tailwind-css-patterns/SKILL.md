---
name: tailwind-css-patterns
description: Provides comprehensive Tailwind CSS utility-first styling patterns including responsive design, layout utilities, flexbox, grid, spacing, typography, colors, and modern CSS best practices. Use when styling React/Vue/Svelte components, building responsive layouts, implementing design systems, or optimizing CSS workflow.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Tailwind CSS Development Patterns

Expert guide for building modern, responsive user interfaces with Tailwind CSS utility-first framework. Covers v4.1+ features including CSS-first configuration, custom utilities, and enhanced developer experience.

## When to Use

- Styling React/HTML components with utility classes
- Building responsive layouts with breakpoints
- Implementing flexbox and grid layouts
- Managing spacing, colors, and typography
- Creating custom design systems
- Optimizing for mobile-first design
- Building dark mode interfaces

## Quick Reference

### Responsive Breakpoints

| Prefix | Min Width | Description |
|--------|-----------|-------------|
| `sm:` | 640px | Small screens |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Desktops |
| `xl:` | 1280px | Large screens |
| `2xl:` | 1536px | Extra large |

### Common Patterns

```html
<!-- Center content -->
<div class="flex items-center justify-center min-h-screen">
  Content
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- Items -->
</div>

<!-- Card component -->
<div class="bg-white rounded-lg shadow-lg p-6">
  <h3 class="text-xl font-bold">Title</h3>
  <p class="text-gray-600">Description</p>
</div>
```

## Instructions

1. **Start Mobile-First**: Write base styles for mobile, add responsive prefixes for larger screens
2. **Use Design Tokens**: Leverage Tailwind's spacing, color, and typography scales
3. **Compose Utilities**: Combine multiple utilities for complex styles
4. **Extract Components**: Create reusable component classes for repeated patterns
5. **Configure Theme**: Customize design tokens in `tailwind.config.js` or using `@theme`
6. **Optimize for Production**: Configure content paths for CSS purging
7. **Test Responsive**: Verify layouts at all breakpoint sizes

## Examples

### Responsive Card Component

```tsx
function ProductCard({ product }: { product: Product }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden sm:flex">
      <img className="h-48 w-full object-cover sm:h-auto sm:w-48" src={product.image} />
      <div className="p-6">
        <h3 className="text-lg font-semibold">{product.name}</h3>
        <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
```

### Dark Mode Toggle

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <h1 class="dark:text-white">Title</h1>
</div>
```

### Form Input

```html
<input
  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="you@example.com"
/>
```

## Best Practices

1. **Mobile-First**: Start with mobile styles, add responsive prefixes for larger screens
2. **Consistent Spacing**: Use Tailwind's spacing scale (4, 8, 12, 16, etc.)
3. **Color Palette**: Stick to Tailwind's color system for consistency
4. **Component Extraction**: Extract repeated patterns into components
5. **Utility Composition**: Prefer utility classes over `@apply`
6. **Semantic HTML**: Use proper HTML elements with Tailwind classes
7. **Performance**: Configure content paths for optimal CSS purging
8. **Accessibility**: Include focus styles, ARIA labels, and respect user preferences

## Constraints and Warnings

- **Class Proliferation**: Long class strings reduce readability; extract components when needed
- **Purge Configuration**: Configure content paths correctly for production builds
- **Arbitrary Values**: Use sparingly; prefer design tokens for consistency
- **Specificity Issues**: Avoid `@apply` with complex selectors
- **Dark Mode**: Requires proper configuration (class or media strategy)
- **Browser Support**: Check Tailwind docs for browser compatibility

## References

- **[references/layout-patterns.md](references/layout-patterns.md)** — Flexbox, grid, spacing, typography, colors
- **[references/component-patterns.md](references/component-patterns.md)** — Cards, navigation, forms, modals, React patterns
- **[references/responsive-design.md](references/responsive-design.md)** — Responsive patterns, dark mode, container queries
- **[references/animations.md](references/animations.md)** — Transitions, transforms, built-in animations, motion preferences
- **[references/performance.md](references/performance.md)** — Bundle optimization, CSS optimization, production builds
- **[references/accessibility.md](references/accessibility.md)** — Focus management, screen readers, color contrast, ARIA
- **[references/configuration.md](references/configuration.md)** — CSS-first config, JavaScript config, plugins, presets
- **[references/reference.md](references/reference.md)** — Additional reference materials

## External Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind UI](https://tailwindui.com)
- [Tailwind Play](https://play.tailwindcss.com)
