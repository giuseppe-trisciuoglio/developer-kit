# TypeScript Patterns for React

TypeScript integration patterns for React components, hooks, and events.

## Component Props

Basic interface:

```typescript
interface UserProps {
  id: string;
  name: string;
  email: string;
  age?: number; // Optional
}

function User({ id, name, email, age }: UserProps) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{email}</p>
      {age && <p>Age: {age}</p>}
    </div>
  );
}
```

Using `React.FC` (explicit):

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant,
  size = 'md',
  onClick,
  children,
  disabled = false
}) => (
  <button
    className={`btn btn-${variant} btn-${size}`}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);
```

## Generic Components

Type-safe list component:

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}

// Usage
<List
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
  keyExtractor={(user) => user.id}
/>
```

## Event Handlers

Typed event handlers:

```typescript
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    console.log(e.target.value);
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Clicked');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') console.log('Enter pressed');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} onKeyDown={handleKeyDown} />
      <select onChange={handleSelect}>
        <option value="a">A</option>
      </select>
      <button onClick={handleClick}>Submit</button>
    </form>
  );
}
```

## Hook Return Types

Typed custom hook:

```typescript
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    // Trigger re-fetch
  }, [url]);

  return { data, loading, error, refetch };
}

// Usage
const { data, loading } = useApi<User[]>('/api/users');
```

## Discriminated Unions for State

```typescript
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };

function useAsyncData<T>(url: string): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ status: 'idle' });

  useEffect(() => {
    setState({ status: 'loading' });
    fetch(url)
      .then(res => res.json())
      .then(data => setState({ status: 'success', data }))
      .catch(err => setState({ status: 'error', error: err.message }));
  }, [url]);

  return state;
}

// Usage
function UserPage() {
  const state = useAsyncData<User>('/api/user/1');

  if (state.status === 'loading') return <p>Loading...</p>;
  if (state.status === 'error') return <p>Error: {state.error}</p>;
  if (state.status === 'success') return <div>{state.data.name}</div>;
  return null;
}
```

## Context Typing

```typescript
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authApi.login(credentials);
    setUser(user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

## Ref Typing

```typescript
// DOM element refs
const inputRef = useRef<HTMLInputElement>(null);
const divRef = useRef<HTMLDivElement>(null);
const buttonRef = useRef<HTMLButtonElement>(null);

// Mutable value (not null)
const counterRef = useRef<number>(0);
const timerRef = useRef<NodeJS.Timeout | null>(null);

// Previous value pattern
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}
```

## Component Prop Patterns

Extending HTML element props:

```typescript
interface CustomButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  loading?: boolean;
}

function CustomButton({ variant = 'primary', loading, children, ...rest }: CustomButtonProps) {
  return (
    <button className={`btn btn-${variant}`} disabled={loading} {...rest}>
      {loading ? 'Loading...' : children}
    </button>
  );
}
```

Polymorphic component (render as different element):

```typescript
interface BoxProps<T extends React.ElementType> {
  as?: T;
  children: React.ReactNode;
}

function Box<T extends React.ElementType = 'div'>({
  as,
  children,
  ...props
}: BoxProps<T> & Omit<React.ComponentPropsWithoutRef<T>, keyof BoxProps<T>>) {
  const Component = as || 'div';
  return <Component {...props}>{children}</Component>;
}

// Usage
<Box as="section" className="container">Content</Box>
<Box as="article">Article content</Box>
```

## Testing Utilities

Typed render helper with providers:

```typescript
import { render, RenderOptions } from '@testing-library/react';

function renderWithProviders(
  ui: React.ReactElement,
  options: RenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <AuthProvider>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </AuthProvider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}
```
