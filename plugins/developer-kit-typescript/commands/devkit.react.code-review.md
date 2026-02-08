---
allowed-tools: Read, Write, Bash, Edit, Grep, Glob
argument-hint: "[review-type] [file/directory-path] [options]"
description: Provides comprehensive React 19 + Tailwind CSS code review focusing on modern patterns, hooks, Server Components, Actions, performance, accessibility, and Tailwind best practices. Use when reviewing React code changes or before merging pull requests.
model: inherit
---

# React 19 + Tailwind CSS Code Review

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Commits**: !`git log --oneline -5`
- **Modified Files**: !`git diff --name-only HEAD~1`
- **React Version**: !`[ -f package.json ] && grep -o '"react":\s*"[^"]*"' package.json 2>/dev/null || echo "Not detected"`
- **Tailwind Version**: !`[ -f package.json ] && grep -o '"tailwindcss":\s*"[^"]*"' package.json 2>/dev/null || echo "Not detected"`

## Review Configuration

The review will analyze: **$ARGUMENTS**

**Available review types:**
- `full` - Complete 360° review (default)
- `components` - Focus on component architecture and patterns
- `hooks` - React hooks usage and custom hooks
- `performance` - Rendering, memoization, bundle size
- `accessibility` - A11y compliance and ARIA
- `styling` - Tailwind CSS patterns and design system
- `forms` - Form handling with Actions and validation
- `testing` - Test coverage and strategies

## Phase 1: Identify Review Scope

### 1.1 Detect Scope

IF "$1" IS PROVIDED
THEN Analyze specific file or component: $ARGUMENTS
ELSE Analyze modified and affected components in the project
ENDIF

### 1.2 Project Configuration

- **Framework**: Next.js, Vite, Create React App, Remix
- **TypeScript**: tsconfig.json strictness level
- **Tailwind Config**: tailwind.config.js/ts customizations
- **Build Tool**: Vite, Webpack, Turbopack
- **State Management**: React Context, Zustand, Redux, Jotai

## Phase 2: React 19 Best Practices

### 2.1 New React 19 Features

#### Server Components & Actions
- Verify proper use of `"use server"` directive for Server Actions
- Check `"use client"` boundaries are minimal and intentional
- Validate Server Components don't import client-only code
- Ensure Actions return proper response structures

#### useActionState Hook
```jsx
// ✅ Correct: useActionState for form submissions
const [state, formAction, isPending] = useActionState(submitAction, initialState);

// ❌ Avoid: Manual state management for forms
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

#### use() Hook for Async Data
```jsx
// ✅ Correct: use() with Suspense for data fetching
function Comments({ commentsPromise }) {
  const comments = use(commentsPromise);
  return comments.map(c => <p key={c.id}>{c.text}</p>);
}

// ❌ Avoid: useEffect for data fetching when use() is appropriate
useEffect(() => { fetchData().then(setData); }, []);
```

#### useFormStatus Hook
```jsx
// ✅ Correct: useFormStatus for submit button state
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>;
}
```

#### useOptimistic Hook
```jsx
// ✅ Correct: Optimistic updates for better UX
const [optimisticItems, addOptimisticItem] = useOptimistic(
  items,
  (state, newItem) => [...state, { ...newItem, pending: true }]
);
```

### 2.2 Refs as Props (React 19)
```jsx
// ✅ React 19: ref is a regular prop
function Input({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}

// ❌ Deprecated: forwardRef wrapper (still works but unnecessary)
const Input = forwardRef((props, ref) => <input ref={ref} {...props} />);
```

### 2.3 Document Metadata
```jsx
// ✅ React 19: Native metadata support
function BlogPost({ post }) {
  return (
    <article>
      <title>{post.title}</title>
      <meta name="description" content={post.summary} />
      <h1>{post.title}</h1>
    </article>
  );
}
```

## Phase 3: Component Architecture

### 3.1 Component Structure
- Single responsibility principle per component
- Prefer composition over prop drilling
- Use compound components for complex UI patterns
- Keep components under 200 lines, extract sub-components

### 3.2 Props Design
```jsx
// ✅ Correct: Discriminated unions for variant props
type ButtonProps = 
  | { variant: 'primary'; onClick: () => void }
  | { variant: 'link'; href: string };

// ✅ Correct: Spread remaining props
function Button({ variant, children, ...props }: ButtonProps) {
  return <button className={variants[variant]} {...props}>{children}</button>;
}

// ❌ Avoid: Boolean prop explosion
<Button isPrimary isLarge isDisabled isLoading />
```

### 3.3 Children Patterns
```jsx
// ✅ Correct: Render props for flexibility
<DataProvider render={(data) => <List items={data} />} />

// ✅ Correct: Compound components
<Select>
  <Select.Option value="1">One</Select.Option>
  <Select.Option value="2">Two</Select.Option>
</Select>
```

## Phase 4: Hooks Best Practices

### 4.1 Built-in Hooks Review
- **useState**: Avoid redundant state, derive when possible
- **useEffect**: Minimal dependencies, proper cleanup
- **useMemo/useCallback**: Only when profiler shows need
- **useRef**: DOM refs and mutable values that don't trigger re-render
- **useContext**: Check for missing providers, context splitting

### 4.2 Custom Hooks
```jsx
// ✅ Correct: Custom hook extracts reusable logic
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  
  return debouncedValue;
}

// ❌ Avoid: Hooks that do too much
function useEverything() { /* manages auth, theme, data, routing... */ }
```

### 4.3 Hook Rules Compliance
- Hooks only at top level (no conditions/loops)
- Hooks only in React functions
- Exhaustive deps rule compliance
- No stale closure issues

## Phase 5: Tailwind CSS Best Practices

### 5.1 Utility Class Organization
```jsx
// ✅ Correct: Logical grouping of utilities
<div className="
  flex items-center gap-4           /* Layout */
  px-4 py-2                         /* Spacing */
  bg-white dark:bg-gray-800         /* Colors */
  rounded-lg shadow-md              /* Effects */
  hover:shadow-lg transition-shadow /* States */
">

// ❌ Avoid: Random ordering
<div className="shadow-md py-2 flex hover:shadow-lg bg-white px-4 rounded-lg">
```

### 5.2 Dark Mode Implementation
```jsx
// ✅ Correct: Consistent dark mode variants
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  <h1 className="text-gray-800 dark:text-white">Title</h1>
  <p className="text-gray-600 dark:text-gray-400">Description</p>
</div>

// ❌ Avoid: Inconsistent or missing dark mode
<div className="bg-white text-black"> /* No dark mode support */
```

### 5.3 Responsive Design
```jsx
// ✅ Correct: Mobile-first responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div className="p-4 md:p-6 lg:p-8">
    <h2 className="text-lg md:text-xl lg:text-2xl">Heading</h2>
  </div>
</div>

// ❌ Avoid: Desktop-first or inconsistent breakpoints
<div className="lg:grid-cols-3 grid-cols-1"> /* Confusing order */
```

### 5.4 Component Variants with CVA/clsx
```jsx
// ✅ Correct: Use cva for variant management
import { cva } from 'class-variance-authority';

const button = cva('rounded font-medium transition-colors', {
  variants: {
    intent: {
      primary: 'bg-blue-600 text-white hover:bg-blue-700',
      secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    },
    size: {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    },
  },
  defaultVariants: { intent: 'primary', size: 'md' },
});

// ❌ Avoid: String concatenation for variants
className={`btn ${isPrimary ? 'bg-blue-600' : 'bg-gray-200'} ${isLarge ? 'px-6' : 'px-4'}`}
```

### 5.5 Avoiding Tailwind Anti-patterns
```jsx
// ❌ Avoid: Arbitrary values when design tokens exist
<div className="mt-[13px] text-[#1a2b3c]">

// ✅ Correct: Use design system values
<div className="mt-3 text-gray-800">

// ❌ Avoid: @apply in CSS (loses utility benefits)
.btn { @apply px-4 py-2 rounded; }

// ✅ Correct: Component abstraction in JSX
const Button = ({ children }) => (
  <button className="px-4 py-2 rounded">{children}</button>
);
```

## Phase 6: Performance Optimization

### 6.1 Rendering Optimization
- Check for unnecessary re-renders with React DevTools
- Verify memo() usage is justified by profiler data
- Ensure keys are stable and unique (not index for dynamic lists)
- Use React.lazy() for code splitting

### 6.2 Bundle Size
- Tree-shaking friendly imports
- Dynamic imports for heavy dependencies
- Verify Tailwind purge/content configuration
- Check for duplicate dependencies

### 6.3 React Compiler (React 19)
```jsx
// React Compiler auto-optimizes, manual memoization often unnecessary
// ✅ Let compiler optimize
function ExpensiveList({ items }) {
  return items.map(item => <Item key={item.id} data={item} />);
}

// ❌ Avoid: Premature optimization
const MemoizedList = memo(({ items }) => {
  const processedItems = useMemo(() => items.map(process), [items]);
  const handleClick = useCallback(() => {}, []);
  // ...
});
```

## Phase 7: Accessibility (A11y)

### 7.1 Semantic HTML
- Use semantic elements (button, nav, main, article, section)
- Proper heading hierarchy (h1 > h2 > h3)
- Labels associated with form inputs
- Alt text for images

### 7.2 ARIA Attributes
```jsx
// ✅ Correct: Proper ARIA usage
<button 
  aria-label="Close dialog"
  aria-expanded={isOpen}
  aria-controls="menu-content"
>
  <XIcon aria-hidden="true" />
</button>

// ❌ Avoid: Redundant ARIA
<button role="button" aria-label="Click me button">Click me</button>
```

### 7.3 Keyboard Navigation
- All interactive elements are focusable
- Logical tab order
- Focus trap for modals/dialogs
- Visible focus indicators

### 7.4 Tailwind A11y Utilities
```jsx
// ✅ Correct: Screen reader utilities
<span className="sr-only">Loading</span>
<div aria-busy="true" className="animate-spin" />

// ✅ Correct: Focus visible styling
<button className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
```

## Phase 8: Forms & Validation

### 8.1 Form Actions (React 19)
```jsx
// ✅ Correct: Form with Server Action
async function createPost(formData: FormData) {
  'use server';
  const title = formData.get('title');
  await db.posts.create({ title });
  revalidatePath('/posts');
}

function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <SubmitButton />
    </form>
  );
}
```

### 8.2 Client-side Validation
```jsx
// ✅ Correct: Progressive enhancement
<input
  type="email"
  required
  pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
  className="invalid:border-red-500 invalid:text-red-600"
/>
```

### 8.3 Form Libraries Integration
- React Hook Form with Tailwind styling
- Zod/Yup schema validation
- Error message display patterns

## Phase 9: Testing Strategy

### 9.1 Component Testing
- Unit tests with Vitest/Jest + Testing Library
- Integration tests for component interactions
- Snapshot tests for UI regression (use sparingly)

### 9.2 Testing Patterns
```jsx
// ✅ Correct: Query by role/label
const button = screen.getByRole('button', { name: /submit/i });
await userEvent.click(button);
expect(screen.getByText(/success/i)).toBeInTheDocument();

// ❌ Avoid: Query by test ID when better options exist
const button = screen.getByTestId('submit-btn');
```

### 9.3 Coverage Targets
- Components: > 80% coverage
- Custom hooks: > 90% coverage
- Utility functions: 100% coverage

## Phase 10: Final Review Report

### Critical Issues (P0 - Fix Immediately)
- Security vulnerabilities (XSS, injection)
- Accessibility blockers (no keyboard nav, missing labels)
- Memory leaks (missing cleanup in effects)
- Production crashes or broken builds

### High Priority (P1 - Next Release)
- Performance regressions (slow renders, large bundles)
- Missing error boundaries
- Inconsistent dark mode support
- Poor mobile experience

### Medium Priority (P2 - Next Sprint)
- Component refactoring for reusability
- Missing tests for critical paths
- Tailwind class organization
- TypeScript strict mode violations

### Low Priority (P3 - Backlog)
- Minor naming improvements
- Additional documentation
- Nice-to-have optimizations
- Code style preferences

## Quality Metrics

- **Component Coverage**: > 80% for shared components
- **Performance Budget**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Bundle Size**: Main bundle < 200KB gzipped
- **Accessibility**: WCAG 2.1 AA compliance
- **TypeScript**: Strict mode enabled, no `any` types

## Recommended Actions

1. **Immediate**: Fix a11y issues, security vulnerabilities, broken builds
2. **Short term**: Migrate to React 19 patterns, optimize bundle
3. **Next sprint**: Improve test coverage, refactor large components
4. **Backlog**: Design system documentation, performance monitoring

## Integrated Support Tools

- React DevTools for component inspection and profiling
- Lighthouse for performance and a11y audits
- axe DevTools for accessibility testing
- Bundle analyzer (webpack-bundle-analyzer, vite-bundle-visualizer)
- Tailwind CSS IntelliSense for IDE support

---

## Execution Instructions

**Agent Selection**: To execute this code review, use the following agent with fallback:
- Primary: `developer-kit:typescript-software-architect-review`
- Fallback: `developer-kit:general-code-reviewer`

**Run context**:
- Provide `$1` as `full`, `components`, `hooks`, `performance`, `accessibility`, `styling`, `forms`, or `testing`
- Optional: specify file or directory path as `$2`

## Overview

Provides comprehensive React 19 + Tailwind CSS code review focusing on modern patterns, hooks, Server Components, Actions, performance, accessibility, and Tailwind best practices. Use when reviewing React code changes or before merging pull requests.

## Usage

```
/devkit.react.code-review $ARGUMENTS
```

## Arguments

| Argument | Description |
|----------|-------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Examples

```bash
/devkit.react.code-review example-input
```
