---
globs: "**/*.{ts,tsx}"
---
# Rule: React Data Fetching Conventions

## Context
Enforce consistent data fetching patterns using SWR for server state management, custom hooks for data access, and proper mutation handling.

## Guidelines

### SWR for All Data Fetching
Use SWR as the single data fetching library. Do not mix with React Query, axios interceptors, or raw fetch in components:

```typescript
import useSwr from 'swr';
import useSWRInfinite from 'swr/infinite';
```

### Custom Data Access Hooks
Encapsulate every API call in a dedicated custom hook following the pattern `use{Action}{Resource}`:

```typescript
// data-access/get-users.hooks.ts
export function useGetUsers(params: UseGetUsersParams) {
  const fetcher = useFetcherWithAcceptLanguage();
  const query = buildQueryString(params);

  const result = useSwr<PaginatedResponseDto<UserDto>>(
    `/api/users?${query}`,
    fetcher
  );

  return {
    ...result,
    data: result.data,
    error: result.error,
  };
}

// data-access/get-user-me.hooks.ts
export function useGetUserMe() {
  const fetcher = useFetcherWithAcceptLanguage();
  return useSwr<SafeUserDto>('/api/users/me', fetcher);
}
```

### Hook Naming Convention

| Pattern | Usage | Example |
|---|---|---|
| `useGet{Resource}` | Fetch single/list resource | `useGetUsers`, `useGetOrderById` |
| `useCreate{Resource}` | POST mutation hook | `useCreateOrder`, `useCreateUser` |
| `useUpdate{Resource}` | PUT/PATCH mutation hook | `useUpdateOrder` |
| `useDelete{Resource}` | DELETE mutation hook | `useDeleteOrder` |

### Hook File Naming
Data access hooks go in a `data-access/` directory with `.hooks.ts` suffix:

```
feature/
└── data-access/
    ├── get-orders.hooks.ts
    ├── create-order.hooks.ts
    └── get-order-detail.hooks.ts
```

### Paginated/Infinite Data
Use `useSWRInfinite` for paginated or infinite scroll data:

```typescript
export function useGetOrders(params: UseGetOrdersParams) {
  const fetcher = useFetcherWithAcceptLanguage();

  const result = useSWRInfinite<PaginatedResponseDto<OrderDto>>(
    (index) => `/api/orders?page=${index}&${buildQuery(params)}`,
    fetcher
  );

  const data = result.data?.flatMap((page) => page.data) ?? [];
  const count = result.data?.[0]?.count ?? 0;

  return { ...result, data, count };
}
```

### Mutations (POST, PUT, DELETE)
Mutations are imperative functions within hooks, not managed by SWR caching:

```typescript
export function useCreateOrder() {
  const fetcher = useFetcherWithAcceptLanguage();

  async function createOrder(data: CreateOrderDto): Promise<OrderDto> {
    const result = await fetcher('/api/orders', {
      method: 'POST',
      body: data,
    });
    return handle<OrderDto>(result);
  }

  return { createOrder };
}
```

### Custom Fetchers
Provide reusable fetcher functions via a shared data-access library:

- `useFetcherWithAcceptLanguage()` — JSON fetcher with language header
- `usePlainFetcherWithAcceptLanguage()` — Raw `Response` fetcher for file downloads

Fetchers handle token injection, language headers, and base URL configuration.

### Error Handling
Use a shared error handler utility for consistent error handling across hooks:

```typescript
const { handleError } = useHandleRespError();

try {
  const result = await createOrder(data);
  // success handling
} catch (error) {
  handleError(error);
}
```

### State Management: No Global Store
- **Server state**: SWR cache is the store — no Redux/Zustand for API data
- **Form state**: React Hook Form
- **App config**: React Context providers
- **UI state**: Local component state or URL parameters

## Examples

### ✅ Good
```typescript
// data-access/get-orders.hooks.ts
export function useGetOrders(filters: OrderFilters) {
  const fetcher = useFetcherWithAcceptLanguage();
  const query = new URLSearchParams(filters).toString();

  return useSwr<PaginatedResponseDto<OrderDto>>(
    `/api/orders?${query}`,
    fetcher
  );
}

// Component usage
function OrderList() {
  const { data, error, isLoading } = useGetOrders({ status: 'active' });

  if (isLoading) return <Spinner />;
  if (error) return <Alert type="error" message={error.message} />;
  return <Table data={data.data} />;
}
```

### ❌ Bad
```typescript
// Raw fetch in component — no abstraction
function OrderList() {
  const [orders, setOrders] = useState([]);
  useEffect(() => {
    fetch('/api/orders').then(r => r.json()).then(setOrders);
  }, []);
}

// Mixing data fetching libraries
import { useQuery } from '@tanstack/react-query'; // Don't mix with SWR
import axios from 'axios'; // Don't use axios directly in components
```
