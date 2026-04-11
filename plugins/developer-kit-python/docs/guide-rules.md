# Python Coding Rules Guide

Reference guide for Python coding rules that activate automatically for all `**/*.py` files.

## Rules Overview

Rules activate automatically based on file globs (`**/*.py`) and provide consistent Python coding standards across the project.

| Rule | File | Purpose |
|------|------|---------|
| `error-handling` | `rules/error-handling.md` | Exception hierarchies, logging, and recovery patterns |
| `language-best-practices` | `rules/language-best-practices.md` | Modern Python (3.11+) patterns and type hints |
| `naming-conventions` | `rules/naming-conventions.md` | PEP 8 naming standards |
| `project-structure` | `rules/project-structure.md` | Modular project organization |

---

## error-handling

**File**: `rules/error-handling.md`

Establishes a consistent error handling strategy with meaningful error reporting, proper exception hierarchies, and clean recovery patterns.

### Exception Hierarchy

```python
class ApplicationError(Exception):
    """Base exception for all application errors."""

class NotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, identifier: str | int) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with ID '{identifier}' was not found")
```

### Best Practices

- **Never** use bare `except:` - always catch specific exception types
- **Never** silently swallow exceptions (`except: pass`)
- Re-raise with context: `raise NewError("message") from original_error`
- Use `logger.exception()` to capture traceback
- Validate at the boundary (API layer), not deep inside business logic

### Example

```python
def process_order(order_id: int) -> OrderResult:
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

---

## language-best-practices

**File**: `rules/language-best-practices.md`

Enforces modern Python (3.11+) best practices for clean, maintainable, and type-safe code.

### Type Hints

- **Always** annotate all function parameters and return types
- Use built-in generics: `list[str]`, `dict[str, int]` (not `List`, `Dict`)
- Use `X | None` instead of `Optional[X]`
- Use `X | Y` instead of `Union[X, Y]`

### Data Modeling

- Use **Pydantic `BaseModel`** for API request/response schemas
- Use **`dataclasses`** for internal data structures
- Use **`NamedTuple`** for lightweight immutable records
- Use `@dataclass(frozen=True)` for immutable data classes

### Async Programming

- Use `async`/`await` for I/O-bound operations
- Never mix blocking I/O with async code
- Prefer `asyncio.TaskGroup` over `asyncio.gather()`

### Example

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    database_url: str
    max_connections: int = 10
    debug: bool = False

def read_config(path: Path) -> AppConfig:
    """Read application configuration from a TOML file."""
    with open(path) as f:
        data = tomllib.load(f)
    return AppConfig(**data)
```

---

## naming-conventions

**File**: `rules/naming-conventions.md`

Standardizes identifier naming following PEP 8 conventions.

### Naming Rules

| Element | Convention | Example |
|---------|------------|---------|
| **Modules** | `snake_case` | `order_service.py` |
| **Packages** | `snake_case` | `models/` |
| **Classes** | `PascalCase` | `OrderService` |
| **Functions** | `snake_case` | `calculate_total()` |
| **Variables** | `snake_case` | `order_total` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| **Exceptions** | `PascalCase` + `Error` | `OrderNotFoundError` |

### Private Members

- Single underscore prefix for private: `_internal_state`
- Double underscore for name mangling: `__mangled_name`

### Boolean Variables

Use `is_`, `has_`, `can_`, `should_` prefixes:
- `is_active`
- `has_permission`
- `can_login`

### Example

```python
MAX_RETRY_COUNT = 3

@dataclass
class OrderResponse:
    order_id: int
    customer_name: str
    is_active: bool

class OrderService:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    def find_by_id(self, order_id: int) -> OrderResponse | None:
        ...
```

---

## project-structure

**File**: `rules/project-structure.md`

Enforces a consistent, modular project structure with clear layer separation.

### Package Organization

```
project_name/
├── pyproject.toml               # Project metadata
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config/              # Configuration
│       ├── common/              # Shared utilities
│       ├── order/               # Domain module
│       │   ├── router.py        # API endpoints
│       │   ├── schemas.py       # Pydantic models
│       │   ├── service.py       # Business logic
│       │   ├── repository.py    # Data access
│       │   └── models.py        # ORM models
│       └── user/                # Domain module
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_order/
│   └── test_user/
└── scripts/
```

### Layer Responsibilities

| File | Responsibility |
|------|----------------|
| `router.py` | API route definitions, request parsing |
| `schemas.py` | Pydantic models for validation |
| `service.py` | Business logic, orchestration |
| `repository.py` | Data access, database queries |
| `models.py` | ORM models (SQLAlchemy, Django) |
| `config/` | Settings, environment variables |

### Test Structure

Mirror source structure under `tests/`:
```
tests/
├── conftest.py
├── test_order/
│   ├── test_router.py
│   └── test_service.py
└── test_user/
```

---

## Quick Reference

| Rule | Key Points |
|------|------------|
| **error-handling** | Exception hierarchy, logging, never bare except |
| **language-best-practices** | Type hints, dataclasses, async patterns |
| **naming-conventions** | snake_case modules, PascalCase classes |
| **project-structure** | Modular organization, layer separation |

---

**Note**: Rules activate automatically for all `**/*.py` files. See the rule files at `rules/*.md` for complete guidelines.