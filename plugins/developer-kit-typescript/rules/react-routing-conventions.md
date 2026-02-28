---
globs: "**/*.tsx"
---
# Rule: React Routing Conventions

## Context
Enforce consistent routing patterns using React Router v6, including modal-as-route patterns and platform differentiation.

## Guidelines

### React Router v6 with createRoutesFromElements
Use `createBrowserRouter` with `createRoutesFromElements` for route definitions:

```typescript
export function router() {
  return createRoutesFromElements([
    <Route path="/auth/*" element={<AuthRoutes />} />,
    <Route path="/app/*" element={
      <RequiredAuthRedirection>
        <Routes>
          <Route path="orders/*" element={<OrderRoutes />} />
          <Route path="*" element={<Navigate to="/app/orders" replace />} />
        </Routes>
      </RequiredAuthRedirection>
    } />,
  ]);
}
```

### Modals as Routes
Render modals via React Router `<Outlet>` — navigating to a sub-route opens the modal:

```typescript
<Route path="/" element={<OrderListPage />}>
  <Route path="new" element={<CreateOrderModal />} />
  <Route path="export" element={<ExportModal />} />
</Route>
```

This keeps modal state in the URL, making it shareable and back-button compatible.

### Platform Differentiation
Use an enum to differentiate behavior between internal (backoffice) and external (customer) platforms:

```typescript
export enum PlatformTypeEnum {
  Internal = 'internal',
  External = 'external',
}

// Conditional rendering based on platform
{platform === PlatformTypeEnum.Internal && (
  <Route path="admin/*" element={<AdminRoutes />} />
)}
```

### Route File Organization
Each feature library defines its routes in a single `routes.tsx` file:

```
libs/client/{feature}/src/lib/
├── routes.tsx           # Feature route definitions
├── pages/               # Page-level components
│   ├── order-list.page.tsx
│   └── order-detail.page.tsx
└── components/          # Feature components
```

### Auth-Protected Routes
Wrap authenticated routes with a `RequiredAuthRedirection` guard component:

```typescript
<Route path="/app/*" element={
  <RequiredAuthRedirection>
    <AppLayout>
      <Routes>
        <Route path="orders/*" element={<OrderRoutes />} />
      </Routes>
    </AppLayout>
  </RequiredAuthRedirection>
} />
```

## Examples

### ✅ Good
```typescript
// Feature routes file — routes.tsx
export function OrderRoutes() {
  return (
    <Routes>
      <Route path="/" element={<OrderListPage />}>
        <Route path="new" element={<CreateOrderModal />} />
        <Route path="export" element={<ExportModal />} />
      </Route>
      <Route path=":order_uuid" element={<OrderDetailPage />} />
    </Routes>
  );
}
```

### ❌ Bad
```typescript
// Mixing routing logic inside components
function OrderList() {
  const [showModal, setShowModal] = useState(false);
  return (
    <>
      <button onClick={() => setShowModal(true)}>New</button>
      {showModal && <CreateOrderModal />}
    </>
  );
  // Modal state should be in the URL, not local state
}

// Using React Router v5 patterns
import { Switch, Route } from 'react-router-dom'; // Use v6 Routes
```
