---
paths:
  - "**/*.py"
---
# Rule: Python Project Structure

## Context
Enforce a consistent, modular project structure for Python applications to maintain separation of concerns and scalability.

## Guidelines

### Package Organization
Organize projects by domain module with clear layer separation:

```
project_name/
├── pyproject.toml               # Project metadata and dependencies
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py              # Application entry point
│       ├── config/              # Configuration management
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── common/              # Shared utilities
│       │   ├── __init__.py
│       │   ├── exceptions.py
│       │   └── utils.py
│       ├── order/               # Domain module: Order
│       │   ├── __init__.py
│       │   ├── router.py        # API endpoints (FastAPI/Flask)
│       │   ├── schemas.py       # Request/Response models (Pydantic)
│       │   ├── service.py       # Business logic
│       │   ├── repository.py    # Data access
│       │   └── models.py        # Database models (SQLAlchemy/Django)
│       └── user/                # Domain module: User
│           ├── __init__.py
│           ├── router.py
│           ├── schemas.py
│           ├── service.py
│           ├── repository.py
│           └── models.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_order/
│   │   ├── __init__.py
│   │   ├── test_router.py
│   │   └── test_service.py
│   └── test_user/
└── scripts/                     # Utility scripts
```

### Layer Responsibilities
- **router.py**: API route definitions, request parsing, response formatting
- **schemas.py**: Pydantic models for request/response validation
- **service.py**: Business logic, orchestration, transaction management
- **repository.py**: Data access, database queries
- **models.py**: ORM models (SQLAlchemy, Django ORM)
- **config/**: Application settings, environment variables, configuration classes

### File Organization Rules
- Use `__init__.py` to control public API exports
- Keep modules focused — one responsibility per file
- Place shared utilities in `common/` package
- Use `conftest.py` for shared test fixtures
- Prefer `pyproject.toml` over `setup.py` for project metadata
- Keep `__init__.py` files minimal — avoid heavy imports

### Test Structure
Mirror the source package structure under `tests/`:
```
tests/
├── conftest.py
├── test_order/
│   ├── test_router.py
│   └── test_service.py
└── test_user/
    ├── test_router.py
    └── test_service.py
```

## Examples

### ✅ Good
```python
# src/project_name/order/schemas.py
from pydantic import BaseModel

class OrderRequest(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    status: str
    total: float
```

### ❌ Bad
```python
# Mixing concerns: models, schemas, and logic in one file
# src/project_name/order.py  (single monolithic file)
class Order:            # ORM model
    ...
class OrderDTO:         # Schema
    ...
def process_order():    # Service logic
    ...
```
