---
globs: "**/*.py"
---
# Rule: Python Naming Conventions

## Context
Standardize identifier naming across Python projects following PEP 8 conventions to ensure readability and consistency.

## Guidelines

### Modules and Packages
- **Modules**: Must use `snake_case` (e.g., `order_service.py`, `user_repository.py`)
- **Packages**: Must use `snake_case`, short and lowercase (e.g., `models`, `services`, `utils`)
- Avoid single-character or overly abbreviated module names

### Classes
- **Classes**: Must use `PascalCase` (e.g., `OrderService`, `UserRepository`)
- **Exception classes**: Must end with `Error` or `Exception` suffix (e.g., `OrderNotFoundError`)
- **Abstract base classes**: Use `PascalCase`, optionally prefixed with `Base` or `Abstract`
- **Dataclasses / Pydantic models**: Must use `PascalCase`

### Functions and Methods
- **Functions**: Must use `snake_case` (e.g., `calculate_total()`, `find_by_email()`)
- **Methods**: Must use `snake_case` (e.g., `process_order()`, `get_user_name()`)
- **Private methods**: Prefix with single underscore (e.g., `_validate_input()`)
- **Name-mangled methods**: Prefix with double underscore only when needed to avoid subclass conflicts

### Variables
- **Variables**: Must use `snake_case` (e.g., `order_total`, `customer_name`)
- **Constants**: Must use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)
- **Private variables**: Prefix with single underscore (e.g., `_internal_state`)
- **Boolean variables**: Use `is_`, `has_`, `can_`, `should_` prefixes (e.g., `is_active`, `has_permission`)

### Type Variables and Generics
- **TypeVar**: Use `PascalCase` single letters or short names (e.g., `T`, `KT`, `VT`)
- **Type aliases**: Use `PascalCase` (e.g., `UserId = int`)

## Examples

### ✅ Good
```python
from dataclasses import dataclass

MAX_RETRY_COUNT = 3

@dataclass
class OrderResponse:
    order_id: int
    customer_name: str
    is_active: bool

class OrderService:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    def find_by_id(self, order_id: int) -> OrderResponse:
        ...

    def _validate_order(self, order: Order) -> bool:
        ...
```

### ❌ Bad
```python
maxRetryCount = 3  # Should be UPPER_SNAKE_CASE

class order_response:  # Should be PascalCase
    OrderId: int       # Should be snake_case
    CustomerName: str

class orderService:  # Should be PascalCase
    def FindById(self, Id):  # Should be snake_case
        ...
```
