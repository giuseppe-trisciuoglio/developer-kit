# React Component Patterns

Patterns for component composition, props, state lifting, and common UI patterns.

## Props and Children

Type-safe component props:

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  children: React.ReactNode;
  disabled?: boolean;
}

function Button({ variant = 'primary', size = 'md', onClick, children, disabled = false }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
```

Composition with children:

```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}
```

## Lifting State Up

Share state between sibling components by lifting to a common ancestor:

```typescript
function Parent() {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <>
      <Panel isActive={activeIndex === 0} onShow={() => setActiveIndex(0)}>
        Panel 1 content
      </Panel>
      <Panel isActive={activeIndex === 1} onShow={() => setActiveIndex(1)}>
        Panel 2 content
      </Panel>
    </>
  );
}

function Panel({ isActive, onShow, children }: {
  isActive: boolean;
  onShow: () => void;
  children: React.ReactNode;
}) {
  return (
    <div>
      <button onClick={onShow}>Show</button>
      {isActive && <div>{children}</div>}
    </div>
  );
}
```

## Controlled Components

Input with controlled state:

```typescript
function ControlledForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log({ name, email });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={e => setName(e.target.value)} />
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Conditional Rendering

```typescript
function Greeting({ isLoggedIn }: { isLoggedIn: boolean }) {
  return (
    <div>
      {isLoggedIn ? <UserGreeting /> : <GuestGreeting />}
    </div>
  );
}

// Short-circuit for optional elements
function Notification({ message }: { message?: string }) {
  return <div>{message && <p className="notification">{message}</p>}</div>;
}
```

## Lists and Keys

Always use stable IDs, not array indices:

```typescript
function UserList({ users }: { users: User[] }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

## Compound Components Pattern

Group related components with shared context:

```typescript
const MenuContext = createContext<{ isOpen: boolean; setIsOpen: (v: boolean) => void } | null>(null);

function Menu({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <MenuContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="menu">{children}</div>
    </MenuContext.Provider>
  );
}

function MenuButton({ children }: { children: React.ReactNode }) {
  const ctx = useContext(MenuContext)!;
  return <button onClick={() => ctx.setIsOpen(!ctx.isOpen)}>{children}</button>;
}

function MenuItems({ children }: { children: React.ReactNode }) {
  const { isOpen } = useContext(MenuContext)!;
  return isOpen ? <ul>{children}</ul> : null;
}

// Usage
<Menu>
  <MenuButton>Open Menu</MenuButton>
  <MenuItems>
    <li>Item 1</li>
    <li>Item 2</li>
  </MenuItems>
</Menu>
```

## Render Props Pattern

```typescript
function MouseTracker({ render }: { render: (pos: { x: number; y: number }) => React.ReactNode }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  return (
    <div onMouseMove={e => setPosition({ x: e.clientX, y: e.clientY })}>
      {render(position)}
    </div>
  );
}

// Usage
<MouseTracker render={({ x, y }) => <h1>Mouse: {x}, {y}</h1>} />
```

## Context for State Management

```typescript
// contexts/ThemeContext.tsx
const ThemeContext = createContext<{ theme: string; setTheme: (t: string) => void } | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

// Usage
function Header() {
  const { theme, setTheme } = useTheme();
  return (
    <header className={theme}>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle
      </button>
    </header>
  );
}
```

## Error Boundaries

```typescript
class ErrorBoundary extends Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Error:', error, info);
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<p>Something went wrong.</p>}>
  <MyComponent />
</ErrorBoundary>
```

## forwardRef Pattern

```typescript
const FancyInput = forwardRef<HTMLInputElement, { placeholder?: string }>(
  function FancyInput({ placeholder }, ref) {
    return <input ref={ref} placeholder={placeholder} className="fancy-input" />;
  }
);

// Usage
function Form() {
  const inputRef = useRef<HTMLInputElement>(null);
  return <FancyInput ref={inputRef} placeholder="Enter value" />;
}
```
