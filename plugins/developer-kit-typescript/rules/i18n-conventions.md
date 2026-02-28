---
globs: "**/*.{ts,tsx}"
---
# Rule: Internationalization (i18n) Conventions

## Context
Enforce consistent internationalization patterns for both frontend (React Intl) and backend (NestJS i18n) to ensure all user-facing strings are translatable.

## Guidelines

### Frontend — React Intl
Use `react-intl` for all user-facing strings in React components.

**JSX strings** use `<FormattedMessage>`:
```tsx
<FormattedMessage
  id="header.menu.orders"
  defaultMessage="Orders"
  description="Header menu item for orders"
/>
```

**Imperative strings** (toasts, alerts, dynamic content) use `useIntl()`:
```typescript
const intl = useIntl();
const message = intl.formatMessage({
  id: 'export.in-preparation',
  defaultMessage: 'Export in preparation',
  description: 'Export in preparation toast',
});
```

### Message ID Convention
Use dotted kebab-case notation: `{component-name}.{purpose}`

```
header.menu.orders
order-card.view-details
order-list.empty-state
create-order.validation.required-field
export-modal.success
```

### Always Include All Three Properties
Every message descriptor MUST include `id`, `defaultMessage`, and `description`:

```typescript
// ✅ Complete descriptor
intl.formatMessage({
  id: 'order-list.no-results',
  defaultMessage: 'No orders found',
  description: 'Empty state message when no orders match filters',
});

// ❌ Missing description
intl.formatMessage({ id: 'order-list.no-results', defaultMessage: 'No orders found' });
```

### Backend — NestJS i18n
Use a shared i18n module (e.g., `@f-technology-srl/f-i18n-nest`). Controllers receive the intl instance via a custom decorator:

```typescript
@Get('/orders/:order_uuid')
async getOrder(
  @Param('order_uuid') order_uuid: string,
  @GetIntl() intl: IntlInstance,
): Promise<OrderDto> {
  const order = await this.orderService.findById(order_uuid);
  if (!order) {
    throw new BadRequestException(
      intl.formatMessage({
        id: 'order-controller.error-not-found',
        defaultMessage: 'Order not found',
        description: 'Order not found error',
      })
    );
  }
  return order;
}
```

### Translation Files
- Frontend: `apps/{app}/translations/{lang}.json`
- Backend: `apps/api/src/assets/langs/{lang}.json`
- Default language: Italian (or project default)
- Supported: Italian, English, German, French (project-dependent)

### Language Context
Provide a language context provider at the app root:

```typescript
<AppLanguagePlatformProvider>
  <IntlProvider locale={currentLocale} messages={messages}>
    <App />
  </IntlProvider>
</AppLanguagePlatformProvider>
```

Data fetching hooks include the language via `Accept-Language` header automatically through custom fetchers.

### Rules for String Handling
- **Never** hardcode user-facing strings directly in JSX or error messages
- **Never** use template literals for translatable content
- **Always** use `FormattedMessage` in JSX and `intl.formatMessage()` in logic
- **Keep** `defaultMessage` values in the project's primary language
- **Use** descriptive `description` fields to help translators understand context

## Examples

### ✅ Good
```tsx
// Component with i18n
export const OrderStatus = (props: { status: OrderStatusEnum }) => {
  return (
    <StatusChip type={getChipType(props.status)}>
      <FormattedMessage
        id={`order-status.${props.status}`}
        defaultMessage={props.status}
        description={`Order status label for ${props.status}`}
      />
    </StatusChip>
  );
};

// Backend error with i18n
throw new BadRequestException(
  intl.formatMessage({
    id: 'order-service.insufficient-stock',
    defaultMessage: 'Insufficient stock for this product',
    description: 'Error when order quantity exceeds available stock',
  })
);
```

### ❌ Bad
```tsx
// Hardcoded string in JSX
<button>Submit Order</button>

// Template literal for user-facing text
const msg = `Order ${orderId} not found`;
throw new BadRequestException(msg);

// Missing description
<FormattedMessage id="submit" defaultMessage="Submit" />
```
