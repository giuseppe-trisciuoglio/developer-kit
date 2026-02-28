---
globs: "**/*.tsx"
---
# Rule: Tailwind Styling Conventions

## Context
Enforce consistent styling patterns using TailwindCSS with a shared design system, cn() utility for conditional classes, and design token standardization.

## Guidelines

### TailwindCSS for All Component Styling
Use TailwindCSS exclusively for component styling. Never use CSS Modules or styled-components:

```typescript
import { cn } from '../../utils';

<div className={cn(
  'rounded-4 border-[1.5px] py-[18px] px-16',
  props.status === 'error' && 'border-red-2 bg-red-4',
  props.disabled && 'border-grey-7 bg-grey-9 cursor-not-allowed',
  props.className
)} />
```

### cn() Utility for Conditional Classes
Use the `cn()` utility (class-variance-authority + tailwind-merge) for all conditional class composition:

```typescript
// utils.ts
import { cx } from 'class-variance-authority';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(cx(inputs));
}
```

### Shared Tailwind Configuration
All apps import a global Tailwind config from the core-ui library:

```javascript
// apps/client/tailwind.config.js
const globalTailwindConf = require('../../libs/client/core-ui/src/lib/styles/tailwind-config.global');
module.exports = { ...globalTailwindConf(__dirname) };
```

### Design Token Conventions
Use project-defined design tokens instead of default Tailwind values:

- **Colors**: Numbered scale (e.g., `yellow-1` through `yellow-10`, `grey-1` through `grey-9`)
- **Spacing**: Numeric px-based scale (e.g., `p-4`, `p-8`, `p-16`, `p-24`, `p-32`)
- **Border radius**: Named sizes (e.g., `rounded-4`, `rounded-8`, `rounded-10`)
- **Font**: Project-defined font family (e.g., Roboto Condensed)

### SCSS for Global Styles Only
SCSS is allowed **only** for global styles (`styles.scss`), not for component-level styling.

### Styling Rules
- **Never** use inline `style={{ }}` attributes
- **Never** use CSS Modules (`*.module.css`)
- **Never** use styled-components or Emotion
- **Always** pass `className` through `cn()` when composing conditional classes
- **Always** allow a `className` prop on reusable components for override support

## Examples

### ✅ Good
```typescript
export const Card = (props: React.PropsWithChildren<CardProps>) => {
  return (
    <div className={cn(
      'rounded-8 border border-grey-7 p-16 bg-white',
      props.variant === 'highlighted' && 'border-yellow-3 bg-yellow-10',
      props.className
    )}>
      {props.children}
    </div>
  );
};
```

### ❌ Bad
```typescript
// Inline styles — use Tailwind classes
<div style={{ borderRadius: 8, padding: 16 }}>

// CSS Modules — use Tailwind + cn()
import styles from './Card.module.css';
<div className={styles.card}>

// Raw string concatenation — use cn()
<div className={`rounded-8 ${isActive ? 'bg-yellow-3' : ''}`}>
```
