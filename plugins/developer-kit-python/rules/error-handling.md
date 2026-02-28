---
globs: "**/*.py"
---
# Rule: Python Error Handling

## Context
Establish a consistent error handling strategy for Python applications, ensuring meaningful error reporting, proper exception hierarchies, and clean recovery patterns.

## Guidelines

### Exception Hierarchy
- Create a base `ApplicationError` inheriting from `Exception` for all domain-specific errors
- Create specific exception classes for each error domain (e.g., `OrderNotFoundError`, `PaymentDeclinedError`)
- Name exceptions with `Error` suffix (PEP 8 convention)
- Include meaningful error messages and relevant context attributes
- Keep the hierarchy shallow (max 2-3 levels deep)

```python
class ApplicationError(Exception):
    """Base exception for all application errors."""

class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, identifier: str | int) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with ID '{identifier}' was not found")

class OrderNotFoundError(NotFoundError):
    def __init__(self, order_id: int) -> None:
        super().__init__("Order", order_id)
```

### Exception Handling Best Practices
- **Never** use bare `except:` — always catch specific exception types
- **Never** silently swallow exceptions (`except: pass`)
- Use `except Exception` only at the top-level error boundary
- Re-raise with context: `raise NewError("message") from original_error`
- Log exceptions with `logger.exception()` to capture the traceback
- Use `else` clause for code that should run only if no exception was raised
- Use `finally` for cleanup code that must always execute

### Logging Errors
- Use the `logging` module, never `print()` for error reporting
- Use `logger.exception("message")` inside `except` blocks to capture traceback
- Use `logger.warning()` for business rule violations
- Use `logger.error()` for unexpected failures
- Include structured context in log messages (IDs, parameters)

### API Error Responses
For web frameworks (FastAPI, Flask, Django), return standardized error responses:

```python
# FastAPI example
from fastapi import HTTPException, status

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "type": "not_found",
            "title": "Resource Not Found",
            "detail": str(exc),
        },
    )
```

### Validation
- Use **Pydantic** for input validation — it raises `ValidationError` automatically
- Do not manually raise exceptions for data validation that Pydantic can handle
- Validate at the boundary (API layer), not deep inside business logic

## Examples

### ✅ Good
```python
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def find_by_id(self, order_id: int) -> Order:
        order = self._repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def process_order(self, order_id: int) -> OrderResult:
        try:
            order = self.find_by_id(order_id)
            result = self._payment_gateway.charge(order)
        except PaymentGatewayError as e:
            logger.exception("Payment failed for order %d", order_id)
            raise PaymentProcessingError(order_id) from e
        else:
            logger.info("Order %d processed successfully", order_id)
            return result
```

### ❌ Bad
```python
def process_order(order_id):
    try:
        order = get_order(order_id)
        charge(order)
    except:              # Bare except
        pass             # Silent swallow

def find_order(order_id):
    order = db.get(order_id)
    if not order:
        return None      # Returning None instead of raising
```
