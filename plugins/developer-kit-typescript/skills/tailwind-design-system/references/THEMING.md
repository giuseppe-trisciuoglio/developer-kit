# Design System Theming References

## Official Documentation

### Tailwind CSS
- [Tailwind CSS v4 Theme Configuration](https://tailwindcss.com/docs/theme)
- [Tailwind CSS Functions and Directives](https://tailwindcss.com/docs/functions-and-directives)
- [Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [Customizing Colors](https://tailwindcss.com/docs/customizing-colors)
- [Customizing Spacing](https://tailwindcss.com/docs/customizing-spacing)

### shadcn/ui
- [Theming Guide](https://ui.shadcn.com/docs/theming)
- [Installation (Manual)](https://ui.shadcn.com/docs/installation/manual)
- [Component Documentation](https://ui.shadcn.com/docs/components)
- [CLI Documentation](https://ui.shadcn.com/docs/cli)

### Color Theory
- [oklch Color Space](https://oklch.com) - Perceptually uniform color picker
- [WCAG Contrast Checker](https://webaim.org/resources/contrastchecker/)

## Design Token Architecture

### Semantic Token Naming

```
--{category}-{variant}-{state}

Examples:
--color-primary-default
--color-primary-hover
--color-primary-disabled
--color-surface-elevated
--color-text-primary
--color-text-secondary
--color-border-subtle
```

### Token Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| `color` | All colors | `--color-primary`, `--color-background` |
| `font` | Typography | `--font-sans`, `--font-mono` |
| `spacing` | Space/distance | `--spacing-4`, `--gap-md` |
| `radius` | Border radius | `--radius-sm`, `--radius-lg` |
| `shadow` | Elevation | `--shadow-sm`, `--shadow-lg` |
| `duration` | Animation time | `--duration-fast`, `--duration-slow` |
| `ease` | Easing functions | `--ease-default`, `--ease-bounce` |

## oklch Color Format

### Why oklch?

- **Perceptually uniform**: Same lightness value appears equally light regardless of hue
- **Wide gamut**: Access to modern display colors (P3)
- **Predictable**: Changing hue doesn't affect perceived lightness

### Format: `oklch(L C H)`

- **L (Lightness)**: 0 to 1 (0 = black, 1 = white)
- **C (Chroma)**: 0 to ~0.4 (saturation/intensity)
- **H (Hue)**: 0 to 360 degrees

### Common Color Values

```css
/* Grays */
--gray-50:  oklch(0.985 0 0);
--gray-100: oklch(0.967 0 0);
--gray-200: oklch(0.92 0 0);
--gray-300: oklch(0.87 0 0);
--gray-400: oklch(0.70 0 0);
--gray-500: oklch(0.56 0 0);
--gray-600: oklch(0.44 0 0);
--gray-700: oklch(0.37 0 0);
--gray-800: oklch(0.27 0 0);
--gray-900: oklch(0.20 0 0);
--gray-950: oklch(0.14 0 0);

/* Blue */
--blue-500: oklch(0.58 0.19 250);

/* Red */
--red-500:  oklch(0.58 0.25 25);

/* Green */
--green-500: oklch(0.62 0.17 145);

/* Yellow */
--yellow-500: oklch(0.84 0.16 84);
```

## CSS Variable Strategy

### Layered Tokens

```css
/* 1. Primitive/Raw values */
:root {
  --color-blue-50: oklch(0.97 0.01 250);
  --color-blue-500: oklch(0.58 0.19 250);
  --color-blue-900: oklch(0.27 0.08 250);
}

/* 2. Semantic mapping */
:root {
  --color-primary: var(--color-blue-500);
  --color-primary-light: var(--color-blue-50);
  --color-primary-dark: var(--color-blue-900);
}

/* 3. Component-specific (rarely needed with shadcn) */
.button {
  --button-bg: var(--color-primary);
}
```

## Tailwind v4.1+ @theme Directive

### Basic Theme Extension

```css
@theme {
  /* Custom colors */
  --color-brand: #3b82f6;
  --color-brand-light: #93c5fd;
  --color-brand-dark: #1e40af;

  /* Custom fonts */
  --font-display: "Satoshi", sans-serif;

  /* Custom spacing */
  --spacing-18: 4.5rem;

  /* Custom breakpoints */
  --breakpoint-3xl: 120rem;
}
```

### Theme with CSS Variables

```css
@theme inline {
  /* Bridge CSS vars to Tailwind */
  --color-primary: var(--primary);
  --color-secondary: var(--secondary);
}
```

### Custom Utilities

```css
@utility content-auto {
  content-visibility: auto;
}

@utility contain-layout {
  contain: layout;
}
```

## Dark Mode Patterns

### Class-based Strategy (Recommended)

```css
@custom-variant dark (&:is(.dark *));

:root {
  --background: white;
  --foreground: black;
}

.dark {
  --background: black;
  --foreground: white;
}
```

### Media Query Strategy

```css
@media (prefers-color-scheme: dark) {
  :root {
    --background: black;
    --foreground: white;
  }
}
```

### Combined Strategy

```css
:root {
  --background: white;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: black;
  }
}

/* Override with class */
.dark {
  --background: black;
}

.light {
  --background: white;
}
```

## Multi-Theme Support

### Data Attribute Themes

```css
[data-theme="ocean"] {
  --primary: oklch(0.55 0.18 230);
  --accent: oklch(0.65 0.12 190);
}

[data-theme="forest"] {
  --primary: oklch(0.50 0.15 145);
  --accent: oklch(0.70 0.10 100);
}
```

### Theme Switcher Component

```tsx
function ThemeSwitcher() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <select value={theme} onChange={(e) => setTheme(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="ocean">Ocean</option>
      <option value="forest">Forest</option>
    </select>
  );
}
```

## Best Practices

1. **Use semantic naming**: `--primary` not `--blue-500`
2. **Always pair foreground**: Every background needs a matching foreground
3. **Consistent scale**: Define complete color scales (50-950)
4. **oklch for colors**: Use oklch for perceptual uniformity
5. **Single source**: All tokens in one `globals.css` file
6. **Test contrast**: Verify WCAG AA compliance (4.5:1 for normal text)
7. **Document tokens**: Maintain visual reference
