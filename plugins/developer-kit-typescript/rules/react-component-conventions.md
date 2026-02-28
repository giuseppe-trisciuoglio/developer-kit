---
globs: "**/*.tsx"
---
# Rule: React Component Conventions

## Context
Enforce consistent React component patterns including functional components, props typing, and design system usage.

## Guidelines

### Functional Components Only
All React components MUST be functional components. Never use class components:

```typescript
// Named export (preferred for most components)
export const Button = (props: React.PropsWithChildren<ButtonProps>) => {
  return <button>{props.children}</button>;
};

// Function declaration (for page components and route definitions)
export function OrderListPage(props: OrderListPageProps) {
  return <div>...</div>;
}
```

### Props Typing
Define props as a dedicated `interface` above the component. Use `React.PropsWithChildren<T>` when children are needed:

```typescript
export interface ButtonProps {
  type: ButtonType;
  disabled?: boolean;
  iconType?: keyof typeof AllIcons | null;
  onClick?: () => void;
}

export const Button = (props: React.PropsWithChildren<ButtonProps>) => { /* ... */ };
```

For components with `forwardRef`:
```typescript
export const InputText = React.forwardRef(
  (props: InputTextProps, ref: ForwardedRef<HTMLInputElement>) => {
    return <input ref={ref} {...props} />;
  }
);
```

### File Naming with Purpose Suffix

| Suffix | Usage | Example |
|---|---|---|
| `.page.tsx` | Page-level components | `order-list.page.tsx` |
| `.hooks.ts` | Custom hooks | `get-orders.hooks.ts` |
| `.stories.tsx` | Storybook stories | `button.stories.tsx` |
| `.spec.tsx` | Component tests | `button.spec.tsx` |
| (no suffix) `.tsx` | Regular components | `button.tsx`, `modal.tsx` |
| `routes.tsx` | Route definitions | `routes.tsx` |

### Design System Components
Use the shared core-ui library for all primitive UI components. Never recreate primitives:

```typescript
import { Button, InputText, Modal, Table, Spinner } from '@myproject/core-ui';
```

Every core-ui component MUST have an accompanying Storybook story.

### Form Handling — React Hook Form + class-validator
Forms use React Hook Form with `class-validator` resolver for validation:

```typescript
import { classValidatorResolver } from '@hookform/resolvers/class-validator';
import { FormProvider, useForm } from 'react-hook-form';

function CreateOrderForm(props: CreateOrderFormProps) {
  const form = useForm<CreateOrderDto>({
    resolver: classValidatorResolver(CreateOrderDto),
    defaultValues: props.defaultValues,
  });

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(props.onSubmit)}>
        <InputTextFormInput name="customerName" label="Name" />
        <SelectFormInput name="status" options={statusOptions} />
        <Button type="submit">Submit</Button>
      </form>
    </FormProvider>
  );
}
```

Form-aware wrapper components (e.g., `InputTextFormInput`, `SelectFormInput`) connect to form context via `useController`.

## Examples

### ✅ Good
```typescript
// order-card.tsx
export interface OrderCardProps {
  order: OrderDto;
  onSelect?: (id: string) => void;
}

export const OrderCard = (props: OrderCardProps) => {
  return (
    <div className={cn('rounded-8 border p-16', props.order.isUrgent && 'border-red-2')}>
      <h3>{props.order.title}</h3>
      <Button type="secondary" onClick={() => props.onSelect?.(props.order.id)}>
        <FormattedMessage id="order-card.view" defaultMessage="View" />
      </Button>
    </div>
  );
};
```

### ❌ Bad
```typescript
// Class component — never use
class OrderCard extends React.Component<OrderCardProps> {
  render() { return <div>...</div>; }
}

// Direct fetch in component — use data access hooks
useEffect(() => { fetch('/api/orders').then(...) }, []);
```
