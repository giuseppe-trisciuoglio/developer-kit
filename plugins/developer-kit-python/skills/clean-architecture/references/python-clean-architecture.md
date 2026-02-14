# Python Clean Architecture Patterns

This reference covers Python-specific patterns for implementing Clean Architecture, Hexagonal Architecture, and Domain-Driven Design.

## Python 3.11+ Features for Clean Architecture

### Dataclasses with Slots (Python 3.10+)

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """Value object with slots for memory efficiency."""
    amount: int  # cents
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

### Pattern Matching for Domain Logic (Python 3.10+)

```python
from dataclasses import dataclass
from typing import Union


@dataclass
class CreditCardPayment:
    card_number: str
    expiry: str
    cvv: str


@dataclass
class PayPalPayment:
    email: str


@dataclass
class BankTransferPayment:
    iban: str
    bic: str


PaymentMethod = Union[CreditCardPayment, PayPalPayment, BankTransferPayment]


class PaymentProcessor:
    async def process(self, amount: Money, method: PaymentMethod) -> PaymentResult:
        match method:
            case CreditCardPayment(card_number, expiry, cvv):
                return await self._process_card(amount, card_number, expiry, cvv)
            case PayPalPayment(email):
                return await self._process_paypal(amount, email)
            case BankTransferPayment(iban, bic):
                return await self._process_transfer(amount, iban, bic)
            case _:
                raise ValueError("Unknown payment method")
```

### Self Type for Fluent Interfaces (Python 3.11+)

```python
from typing import Self


class Order:
    def __init__(self):
        self._items: list[OrderItem] = []
        self._status = OrderStatus.DRAFT

    def add_item(self, item: OrderItem) -> Self:
        self._items.append(item)
        return self

    def apply_discount(self, percentage: float) -> Self:
        for item in self._items:
            item.apply_discount(percentage)
        return self

    def finalize(self) -> Self:
        self._status = OrderStatus.FINALIZED
        return self


# Usage: fluent interface
order = (
    Order()
    .add_item(OrderItem("Product A", 100))
    .add_item(OrderItem("Product B", 200))
    .apply_discount(0.1)
    .finalize()
)
```

## Repository Pattern Implementations

### Generic Repository Base

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from uuid import UUID

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """Generic repository interface."""

    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        pass


class IUnitOfWork(ABC):
    """Unit of Work pattern for transaction management."""

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
```

### SQLAlchemy 2.0 Repository

```python
from typing import Type, TypeVar, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)
E = TypeVar('E')  # Entity type


class SQLAlchemyRepository(IRepository[E], Generic[T, E]):
    """Generic SQLAlchemy repository implementation."""

    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self._session = session
        self._model_class = model_class

    async def find_by_id(self, entity_id: UUID) -> Optional[E]:
        result = await self._session.execute(
            select(self._model_class).where(self._model_class.id == entity_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all(self) -> List[E]:
        result = await self._session.execute(select(self._model_class))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, entity: E) -> E:
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self._session.execute(
            delete(self._model_class).where(self._model_class.id == entity_id)
        )
        return result.rowcount > 0

    @abstractmethod
    def _to_entity(self, model: T) -> E:
        """Convert model to domain entity."""
        pass

    @abstractmethod
    def _to_model(self, entity: E) -> T:
        """Convert domain entity to model."""
        pass
```

### In-Memory Repository for Testing

```python
from typing import Dict, List, Optional
from uuid import UUID


class InMemoryRepository(IRepository[E], Generic[E]):
    """In-memory repository for testing."""

    def __init__(self):
        self._storage: Dict[UUID, E] = {}

    async def find_by_id(self, entity_id: UUID) -> Optional[E]:
        return self._storage.get(entity_id)

    async def find_all(self) -> List[E]:
        return list(self._storage.values())

    async def save(self, entity: E) -> E:
        # Assuming entity has an 'id' attribute
        self._storage[entity.id] = entity
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def clear(self) -> None:
        self._storage.clear()
```

## Domain Events

### Event Bus Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Callable, Type, Dict, Any
from collections import defaultdict
import asyncio


@dataclass
class DomainEvent:
    """Base class for domain events."""
    occurred_at: datetime = field(default_factory=datetime.utcnow)


class IEventBus(ABC):
    """Event bus interface for publishing and subscribing to events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        pass


class InMemoryEventBus(IEventBus):
    """In-memory event bus implementation."""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True
        )


class OutboxPattern(IEventBus):
    """Outbox pattern for reliable event publishing."""

    def __init__(self, event_bus: IEventBus, outbox_repository):
        self._event_bus = event_bus
        self._outbox = outbox_repository

    async def publish(self, event: DomainEvent) -> None:
        # Store in outbox first
        await self._outbox.store(event)

    async def process_outbox(self) -> None:
        """Process pending events - call this after transaction commit."""
        events = await self._outbox.get_pending()
        for event in events:
            try:
                await self._event_bus.publish(event)
                await self._outbox.mark_as_processed(event)
            except Exception:
                await self._outbox.mark_as_failed(event)
                raise
```

## Specification Pattern

```python
from abc import ABC, abstractmethod
from typing import List, TypeVar

T = TypeVar('T')


class Specification(ABC, Generic[T]):
    """Specification pattern for business rules."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)


# Example usage
class PremiumCustomerSpecification(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.total_orders > 100 and customer.average_order_value > 500


class ActiveCustomerSpecification(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.last_order_date > datetime.now() - timedelta(days=90)


# Combine specifications
eligible_for_vip = PremiumCustomerSpecification() & ActiveCustomerSpecification()
customers = [c for c in all_customers if eligible_for_vip.is_satisfied_by(c)]
```

## Result Pattern for Error Handling

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E


Result = Union[Ok[T], Err[E]]


class DomainError:
    """Base class for domain errors."""
    pass


@dataclass(frozen=True)
class ValidationError(DomainError):
    field: str
    message: str


@dataclass(frozen=True)
class NotFoundError(DomainError):
    resource: str
    identifier: str


# Usage in use cases
class CreateOrderUseCase:
    async def execute(self, request: CreateOrderRequest) -> Result[Order, DomainError]:
        customer = await self._customer_repo.find_by_id(request.customer_id)
        if not customer:
            return Err(NotFoundError("Customer", str(request.customer_id)))

        if not customer.can_place_orders():
            return Err(ValidationError("customer", "Customer cannot place orders"))

        order = Order.create(customer, request.items)
        await self._order_repo.save(order)
        return Ok(order)
```

## Manual Dependency Injection

```python
from typing import TypeVar, Callable, Dict, Type, Any

T = TypeVar('T')


class Container:
    """Simple manual dependency injection container."""

    def __init__(self):
        self._registrations: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory for an interface."""
        self._registrations[interface] = factory

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a singleton instance."""
        self._singletons[interface] = instance

    def resolve(self, interface: Type[T]) -> T:
        """Resolve an interface to its implementation."""
        if interface in self._singletons:
            return self._singletons[interface]

        if interface not in self._registrations:
            raise KeyError(f"No registration for {interface}")

        return self._registrations[interface]()


# Usage
container = Container()

# Register repositories
container.register(
    IUserRepository,
    lambda: SQLAlchemyUserRepository(get_db_session())
)

# Register use cases
container.register(
    CreateUserUseCase,
    lambda: CreateUserUseCase(container.resolve(IUserRepository))
)

# Resolve
use_case = container.resolve(CreateUserUseCase)
```

## Async Context Managers for Resources

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator


@asynccontextmanager
async def unit_of_work(session: AsyncSession) -> AsyncGenerator[UnitOfWork, None]:
    """Context manager for transaction handling."""
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise


# Usage
async def create_user_handler(request: CreateUserRequest):
    async with unit_of_work(session) as uow:
        use_case = CreateUserUseCase(uow.user_repository)
        result = await use_case.execute(request)
        # Automatically commits or rolls back
```

## Type Hints Best Practices

```python
from typing import NewType, Protocol
from uuid import UUID

# NewType for type safety
UserId = NewType('UserId', UUID)
OrderId = NewType('OrderId', UUID)


def get_user(user_id: UserId) -> User: ...
def get_order(order_id: OrderId) -> Order: ...

# This will be caught by type checker:
# get_user(order_id)  # Error: Expected UserId, got OrderId


# Protocol for structural typing
class Logger(Protocol):
    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...


class UseCase:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger


# Any object with debug/info/error methods works
class ConsoleLogger:
    def debug(self, msg: str) -> None: print(f"DEBUG: {msg}")
    def info(self, msg: str) -> None: print(f"INFO: {msg}")
    def error(self, msg: str) -> None: print(f"ERROR: {msg}")


use_case = UseCase(ConsoleLogger())  # Works!
```
