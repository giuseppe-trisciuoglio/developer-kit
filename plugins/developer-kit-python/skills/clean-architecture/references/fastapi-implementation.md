# FastAPI Clean Architecture Implementation

Complete reference for implementing Clean Architecture with FastAPI, including dependency injection, middleware, and testing.

## Project Structure

```
fastapi_clean_app/
├── app/
│   ├── __init__.py
│   ├── domain/                    # Pure business logic
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── events/
│   │   └── repositories/
│   ├── use_cases/                 # Application business rules
│   │   ├── __init__.py
│   │   └── user/
│   ├── adapters/                  # Interface implementations
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   └── controllers/
│   ├── infrastructure/            # Framework concerns
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── container.py
│   │   ├── config.py
│   │   └── middleware.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
└── alembic.ini
```

## Dependencies

```toml
# pyproject.toml
[project]
name = "fastapi-clean-app"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "sqlalchemy[asyncio]>=2.0.23",
    "asyncpg>=0.29.0",
    "dependency-injector>=4.41.0",
    "alembic>=1.12.0",
    "structlog>=23.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

## Domain Layer

```python
# app/domain/value_objects/email.py
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """Value object representing a validated email address."""
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

    def domain(self) -> str:
        return self.value.split('@')[1]
```

```python
# app/domain/entities/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from domain.value_objects.email import Email


@dataclass
class User:
    """User aggregate root."""
    email: Email
    name: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    _events: List = field(default_factory=list, repr=False)

    def deactivate(self) -> None:
        self.is_active = False

    def can_login(self) -> bool:
        return self.is_active

    def record_event(self, event) -> None:
        self._events.append(event)

    def clear_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events

    @classmethod
    def create(cls, email: Email, name: str) -> "User":
        user = cls(email=email, name=name)
        from domain.events.user_created import UserCreatedEvent
        user.record_event(UserCreatedEvent(user_id=user.id, email=str(email)))
        return user
```

```python
# app/domain/events/user_created.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UserCreatedEvent:
    user_id: UUID
    email: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

```python
# app/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.entities.user import User
from domain.value_objects.email import Email


class IUserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass
```

## Use Cases

```python
# app/use_cases/user/create_user.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.repositories.user_repository import IUserRepository


@dataclass
class CreateUserRequest:
    email: str
    name: str


@dataclass
class CreateUserResponse:
    user_id: Optional[UUID]
    success: bool
    error_message: Optional[str] = None


class CreateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        try:
            email = Email(request.email)
        except ValueError as e:
            return CreateUserResponse(
                user_id=None,
                success=False,
                error_message=str(e)
            )

        existing = await self._user_repository.find_by_email(email)
        if existing:
            return CreateUserResponse(
                user_id=None,
                success=False,
                error_message="Email already registered"
            )

        user = User.create(email=email, name=request.name)
        saved_user = await self._user_repository.save(user)

        return CreateUserResponse(
            user_id=saved_user.id,
            success=True
        )
```

```python
# app/use_cases/user/get_user.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository


@dataclass
class GetUserRequest:
    user_id: UUID


@dataclass
class GetUserResponse:
    user: Optional[User]
    found: bool


class GetUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository

    async def execute(self, request: GetUserRequest) -> GetUserResponse:
        user = await self._user_repository.find_by_id(request.user_id)
        return GetUserResponse(user=user, found=user is not None)
```

## Infrastructure Layer

```python
# app/infrastructure/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
```

```python
# app/infrastructure/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

```python
# app/infrastructure/container.py
from dependency_injector import containers, providers

from adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from use_cases.user.create_user import CreateUserUseCase
from use_cases.user.get_user import GetUserUseCase
from infrastructure.database import get_session


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Database session
    db_session = providers.Resource(get_session)

    # Repositories
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=db_session
    )

    # Use cases
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository
    )

    get_user_use_case = providers.Factory(
        GetUserUseCase,
        user_repository=user_repository
    )
```

```python
# app/infrastructure/middleware.py
import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            "request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("unhandled_exception", exc=str(exc))
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
```

## Adapters

```python
# app/adapters/repositories/sqlalchemy_user_repository.py
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.repositories.user_repository import IUserRepository
from infrastructure.database import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def find_by_email(self, email: Email) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == str(email))
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def save(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=str(user.email),
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        self._session.add(model)
        await self._session.commit()
        return user

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
            return True
        return False

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at
        )
```

```python
# app/adapters/controllers/user_controller.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from dependency_injector.wiring import inject, Provide

from use_cases.user.create_user import CreateUserUseCase, CreateUserRequest
from use_cases.user.get_user import GetUserUseCase, GetUserRequest
from infrastructure.container import Container


router = APIRouter(prefix="/users", tags=["users"])


class CreateUserInput(BaseModel):
    email: EmailStr
    name: str


class UserOutput(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool


@router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: CreateUserInput,
    use_case: CreateUserUseCase = Depends(Provide[Container.create_user_use_case])
):
    request = CreateUserRequest(email=data.email, name=data.name)
    response = await use_case.execute(request)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error_message
        )

    return {"id": str(response.user_id)}


@router.get("/{user_id}", response_model=UserOutput)
@inject
async def get_user(
    user_id: UUID,
    use_case: GetUserUseCase = Depends(Provide[Container.get_user_use_case])
):
    request = GetUserRequest(user_id=user_id)
    response = await use_case.execute(request)

    if not response.found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserOutput(
        id=str(response.user.id),
        email=str(response.user.email),
        name=response.user.name,
        is_active=response.user.is_active
    )
```

## Main Application

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.controllers import user_controller
from infrastructure.container import Container
from infrastructure.database import init_db
from infrastructure.middleware import LoggingMiddleware, ErrorHandlingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    # Initialize container
    container = Container()
    container.wire(modules=[user_controller])

    app = FastAPI(
        title="Clean Architecture API",
        version="1.0.0",
        lifespan=lifespan
    )
    app.container = container

    # Middleware
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(user_controller.router)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import create_app
from infrastructure.database import Base, get_session
from adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

# Test database
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_db"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(session):
    app = create_app()

    # Override dependency
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

```python
# tests/unit/test_create_user_use_case.py
import pytest
from unittest.mock import AsyncMock

from use_cases.user.create_user import CreateUserUseCase, CreateUserRequest
from domain.entities.user import User
from domain.value_objects.email import Email


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    return CreateUserUseCase(user_repository=mock_repository)


@pytest.mark.asyncio
async def test_create_user_success(use_case, mock_repository):
    mock_repository.find_by_email.return_value = None
    mock_repository.save.return_value = User(
        email=Email("test@example.com"),
        name="Test User"
    )

    request = CreateUserRequest(email="test@example.com", name="Test User")
    response = await use_case.execute(request)

    assert response.success is True
    assert response.user_id is not None


@pytest.mark.asyncio
async def test_create_user_invalid_email(use_case):
    request = CreateUserRequest(email="invalid-email", name="Test")
    response = await use_case.execute(request)

    assert response.success is False
    assert "Invalid email" in response.error_message
```

```python
# tests/integration/test_user_api.py
import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client):
    # Create first user
    await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User"
    })

    # Try to create duplicate
    response = await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Another User"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get("/users/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 404
```

## Running the Application

```bash
# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```
