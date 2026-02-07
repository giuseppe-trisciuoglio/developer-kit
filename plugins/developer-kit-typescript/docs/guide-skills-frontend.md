# Frontend Development Skills Guide

This guide provides comprehensive documentation for frontend development skills available in the Developer Kit, covering React, TypeScript, UI libraries, and modern frontend patterns.

---

## Table of Contents

1. [Overview](#overview)
2. [React Development Skills](#react-development-skills)
3. [UI Component Libraries](#ui-component-libraries)
4. [Styling and CSS Frameworks](#styling-and-css-frameworks)
5. [TypeScript Documentation](#typescript-documentation)
6. [Best Practices](#best-practices)
7. [Common Workflows](#common-workflows)
8. [Integration with Backend](#integration-with-backend)

---

## Overview

Frontend skills in the Developer Kit provide comprehensive patterns for modern web development, with focus on:

- **React ecosystem** - Component patterns, hooks, state management
- **Modern UI libraries** - Component-driven development with Shadcn-UI
- **Utility-first CSS** - Tailwind CSS for rapid styling
- **TypeScript integration** - Type-safe frontend development
- **Performance optimization** - Bundle optimization and rendering patterns
- **Testing strategies** - Unit and integration testing for frontend components

---

## React Development Skills

### `react`

**Location**: `skills/react/SKILL.md`

**Purpose**: React development patterns and best practices for building modern, scalable user interfaces.

**Key Topics**:
- Component architecture and design patterns
- React Hooks (useState, useEffect, useContext, custom hooks)
- State management (Context API, Redux, Zustand)
- Performance optimization (memo, useMemo, useCallback)
- Server Components and Next.js patterns
- Testing with React Testing Library
- Accessibility best practices

**When to Use**:
- Building new React applications or features
- Refactoring legacy React code
- Implementing complex state management
- Optimizing React performance
- Setting up testing frameworks for React components

---

## UI Component Libraries

### `shadcn-ui`

**Location**: `skills/shadcn-ui/SKILL.md`

**Purpose**: Modern UI component library patterns using Radix UI primitives and Tailwind CSS.

**Key Topics**:
- Component-driven development with shadcn/ui
- Customizing component themes and variants
- Building accessible UI components
- Integrating with design systems
- TypeScript support for components
- Composition patterns for complex UIs
- Animation and transition patterns

**When to Use**:
- Building modern, accessible UI components
- Implementing design system patterns
- Creating reusable component libraries
- Integrating Tailwind CSS with React components

---

## Styling and CSS Frameworks

### `tailwind-css`

**Location**: `skills/tailwind-css/SKILL.md`

**Purpose**: Utility-first CSS framework patterns for rapid UI development.

**Key Topics**:
- Tailwind CSS utility classes and patterns
- Responsive design with mobile-first approach
- Custom configuration and theming
- Component extraction patterns
- Dark mode implementation
- Animation utilities
- Integration with React/Vue/Angular
- Performance optimization with PurgeCSS

**When to Use**:
- Building responsive, modern UIs quickly
- Implementing custom designs without writing CSS
- Creating consistent design systems
- Optimizing for production builds

---

## TypeScript Documentation

### `typescript-docs`

**Location**: `skills/typescript-docs/SKILL.md`

**Purpose**: TypeScript documentation patterns and type definition best practices.

**Key Topics**:
- Writing comprehensive JSDoc/TSDoc comments
- Creating type definitions for APIs and libraries
- Documenting React components with TypeScript
- Auto-generating documentation from types
- API documentation with TypeDoc
- Type-safe prop validation
- Generic type patterns
- Module declaration files

**When to Use**:
- Documenting TypeScript codebases
- Creating type definitions for JavaScript libraries
- Generating API documentation
- Building component libraries with TypeScript

---

## Best Practices

### Component Architecture

1. **Single Responsibility**: Each component should have one clear purpose
2. **Composition over Inheritance**: Prefer composition patterns
3. **Props Interface**: Use TypeScript interfaces for component props
4. **Default Props**: Provide sensible defaults for optional props
5. **State Management**: Keep state close to where it's used

### Performance Optimization

1. **Code Splitting**: Use dynamic imports for large components
2. **Memoization**: React.memo, useMemo, and useCallback for expensive operations
3. **Virtual Scrolling**: For long lists of data
4. **Image Optimization**: Lazy loading and WebP format
5. **Bundle Analysis**: Regular bundle size monitoring

### Accessibility

1. **Semantic HTML**: Use proper HTML elements
2. **ARIA Labels**: Provide accessible labels for custom components
3. **Keyboard Navigation**: Ensure all functionality works with keyboard
4. **Screen Reader Support**: Test with screen readers
5. **Color Contrast**: Meet WCAG AA standards

### Testing

1. **Unit Tests**: Test component logic in isolation
2. **Integration Tests**: Test component interactions
3. **Visual Regression**: Catch UI changes
4. **Accessibility Testing**: Automated a11y checks
5. **Performance Testing**: Monitor render performance

---

## Common Workflows

### Creating a New React Component

```typescript
// With TypeScript and best practices
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant,
  size,
  children,
  onClick,
  disabled = false
}) => {
  const baseClasses = 'font-semibold rounded-lg transition-colors';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300'
  };
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

### Setting up Tailwind CSS with React

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Documenting Components with TypeScript

```typescript
/**
 * A versatile button component that supports different variants and sizes.
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 *
 * @since 1.0.0
 */
export interface ButtonProps {
  /**
   * The visual style of the button
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'outline';

  /**
   * The size of the button
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * The content to display inside the button
   */
  children: React.ReactNode;

  /**
   * Optional click handler
   */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
```

---

## Integration with Backend

### API Client Patterns

```typescript
// Type-safe API client with TypeScript
interface User {
  id: string;
  name: string;
  email: string;
}

interface ApiClient {
  getUsers(): Promise<User[]>;
  getUser(id: string): Promise<User>;
  createUser(user: Omit<User, 'id'>): Promise<User>;
}

// React hook for API integration
export const useUsers = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getUsers();
      setUsers(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  return { users, loading, error, refetch: fetchUsers };
};
```

### State Management with Context API

```typescript
// App context with TypeScript
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  language: string;
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};
```

---

## Related Skills

- **[Backend Skills](guide-skills-spring-boot.md)** - For API development and integration
- **[Testing Skills](guide-skills-junit-test.md)** - For backend testing patterns
- **[AI Skills](guide-skills-langchain4j.md)** - For AI integration in frontend apps
- **[TypeScript Security](typescript-security-expert.md)** - For security best practices

---

## Contributing

To add new frontend skills:

1. Create `skills/frontend/<skill-name>/SKILL.md`
2. Include YAML frontmatter with proper metadata
3. Add practical examples and TypeScript code
4. Document dependencies and setup instructions
5. Update this guide with the new skill

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.