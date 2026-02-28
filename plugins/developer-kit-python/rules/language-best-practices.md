---
globs: "**/*.py"
---
# Rule: Python Best Practices

## Context
Enforce modern Python (3.11+) best practices to produce clean, maintainable, and type-safe code.

## Guidelines

### Type Hints
- **Always** annotate all function parameters and return types
- Use `-> None` for functions that return nothing
- Use built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]` (not `List`, `Dict`, `Tuple` from `typing`)
- Use `X | None` instead of `Optional[X]`
- Use `X | Y` instead of `Union[X, Y]`
- Use `TypeAlias` for complex type definitions

### Data Modeling
- Use **Pydantic `BaseModel`** for API request/response schemas and validation
- Use **`dataclasses`** for internal data structures without validation needs
- Use **`NamedTuple`** for lightweight immutable records
- Use `@dataclass(frozen=True)` for immutable data classes
- Avoid plain dictionaries for structured data — use typed models

### Functions and Methods
- Keep functions short and focused (max ~20 lines of logic)
- Use keyword-only arguments for functions with 3+ parameters: `def func(*, name, age, email)`
- Use `*args` and `**kwargs` sparingly — prefer explicit parameters
- Prefer returning values over mutating arguments
- Use list comprehensions and generator expressions over `map()`/`filter()`

### Context Managers and Resources
- **Always** use `with` statements for resource management (files, connections, locks)
- Implement `__enter__` / `__exit__` or use `@contextmanager` for custom resource managers
- Use `pathlib.Path` instead of `os.path` for file operations

### Async Programming
- Use `async`/`await` for I/O-bound operations
- Never mix blocking I/O with async code — use `asyncio.to_thread()` for blocking calls
- Prefer `asyncio.TaskGroup` over `asyncio.gather()` for structured concurrency

### Imports
- Group imports: stdlib → third-party → local (separated by blank lines)
- Use absolute imports over relative imports
- Avoid wildcard imports (`from module import *`)
- Import specific names, not entire modules when practical

### Documentation
- Use **Google style** or **NumPy style** docstrings consistently across the project
- Document all public functions, classes, and modules
- Include `Args`, `Returns`, `Raises` sections in docstrings

## Examples

### ✅ Good
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AppConfig:
    database_url: str
    max_connections: int = 10
    debug: bool = False

def read_config(path: Path) -> AppConfig:
    """Read application configuration from a TOML file.

    Args:
        path: Path to the configuration file.

    Returns:
        Parsed application configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    with open(path) as f:
        data = tomllib.load(f)
    return AppConfig(**data)
```

### ❌ Bad
```python
import os
from typing import Optional, List, Dict

def read_config(path):  # Missing type hints
    """Read config."""
    f = open(path)      # No context manager
    data = f.read()
    f.close()
    return data         # Returns raw string, not typed model
```
