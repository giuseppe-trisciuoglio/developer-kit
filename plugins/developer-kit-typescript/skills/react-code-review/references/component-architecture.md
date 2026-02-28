# React Component Architecture Patterns

## Component Composition

### Container / Presentational Pattern
Separate data logic from visual rendering.

```tsx
// Container: Handles data and state
function UserListContainer() {
  const { data: users, isLoading } = useUsers();
  const [filter, setFilter] = useState('');

  if (isLoading) return <UserListSkeleton />;
  return <UserList users={users} filter={filter} onFilterChange={setFilter} />;
}

// Presentational: Pure rendering, easy to test
function UserList({
  users,
  filter,
  onFilterChange,
}: {
  users: User[];
  filter: string;
  onFilterChange: (value: string) => void;
}) {
  const filtered = users.filter(u => u.name.includes(filter));
  return (
    <div>
      <input value={filter} onChange={e => onFilterChange(e.target.value)} />
      {filtered.map(user => <UserCard key={user.id} user={user} />)}
    </div>
  );
}
```

### Compound Components
Components that work together sharing implicit state.

```tsx
// Compound component API
<Tabs defaultValue="overview">
  <Tabs.List>
    <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
    <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="overview">Overview content</Tabs.Content>
  <Tabs.Content value="settings">Settings content</Tabs.Content>
</Tabs>

// Implementation using Context
const TabsContext = createContext<TabsState | null>(null);

function Tabs({ defaultValue, children }: TabsProps) {
  const [value, setValue] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ value, setValue }}>
      <div role="tablist">{children}</div>
    </TabsContext.Provider>
  );
}

Tabs.List = function TabsList({ children }: { children: ReactNode }) {
  return <div role="tablist">{children}</div>;
};

Tabs.Trigger = function TabsTrigger({ value, children }: TabsTriggerProps) {
  const ctx = useContext(TabsContext)!;
  return (
    <button
      role="tab"
      aria-selected={ctx.value === value}
      onClick={() => ctx.setValue(value)}
    >
      {children}
    </button>
  );
};

Tabs.Content = function TabsContent({ value, children }: TabsContentProps) {
  const ctx = useContext(TabsContext)!;
  if (ctx.value !== value) return null;
  return <div role="tabpanel">{children}</div>;
};
```

### Polymorphic Components
Components that render as different HTML elements.

```tsx
type PolymorphicProps<E extends React.ElementType> = {
  as?: E;
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<E>, 'as' | 'children'>;

function Box<E extends React.ElementType = 'div'>({
  as,
  children,
  ...props
}: PolymorphicProps<E>) {
  const Component = as || 'div';
  return <Component {...props}>{children}</Component>;
}

// Usage
<Box as="section" className="p-4">Content</Box>
<Box as="article" id="post-1">Article</Box>
```

## Component Size Guidelines

### When to Split Components
Split a component when:
- It exceeds ~200 lines of code
- It has more than 7 props
- It renders conditionally complex UI sections
- Parts of it could be reused elsewhere
- It mixes multiple concerns (data + UI + layout)

### Prop Drilling Solutions

```tsx
// ❌ Prop drilling through multiple levels
<App theme={theme} user={user}>
  <Layout theme={theme} user={user}>
    <Sidebar theme={theme}>
      <UserInfo user={user} />
    </Sidebar>
  </Layout>
</App>

// ✅ Context for cross-cutting values
const ThemeContext = createContext<Theme>(defaultTheme);
const UserContext = createContext<User | null>(null);

function App() {
  return (
    <ThemeContext.Provider value={theme}>
      <UserContext.Provider value={user}>
        <Layout>
          <Sidebar>
            <UserInfo />
          </Sidebar>
        </Layout>
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
}

// ✅ Component composition (children pattern)
function Layout({ children }: { children: ReactNode }) {
  return <div className="layout">{children}</div>;
}

function App() {
  return (
    <Layout>
      <Sidebar>
        <UserInfo user={user} /> {/* user passed directly */}
      </Sidebar>
    </Layout>
  );
}
```

## State Management Decision Matrix

| State Type | Solution | When to Use |
|-----------|----------|-------------|
| Local UI state | `useState` / `useReducer` | Toggle, form inputs, modals |
| Server state | TanStack Query / SWR | API data, caching, refetching |
| Form state | React Hook Form | Complex forms, validation |
| URL state | Router search params | Filters, pagination, sorting |
| Cross-component | Context (narrow scope) | Theme, auth, locale |
| Global app state | Zustand / Jotai | Shopping cart, notifications |
| Complex domain | Redux Toolkit | Rarely — only for complex interactions |

## Error Handling Patterns

### Error Boundaries
Every major section of the app should have an error boundary.

```tsx
// Reusable error boundary component
'use client';

import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error boundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorFallback />}>
  <Dashboard />
</ErrorBoundary>
```

## Review Checklist

- [ ] Components follow single responsibility principle
- [ ] Component size is manageable (under ~200 lines)
- [ ] Props count is reasonable (under 7)
- [ ] State is colocated with the components that use it
- [ ] Context is scoped narrowly — not used as global state
- [ ] Server state uses TanStack Query / SWR, not useEffect + useState
- [ ] Error boundaries wrap major UI sections
- [ ] Components are properly typed with TypeScript
- [ ] Memoization (memo, useMemo, useCallback) is used only when measured benefit exists
