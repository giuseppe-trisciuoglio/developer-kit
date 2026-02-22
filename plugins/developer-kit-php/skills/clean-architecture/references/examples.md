# Clean Architecture Examples

## Entity with Domain Logic

```php
<?php
// src/Domain/Entity/User.php

namespace App\Domain\Entity;

use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use App\Domain\Event\UserCreatedEvent;
use DateTimeImmutable;

class User
{
    private array $domainEvents = [];

    public function __construct(
        private UserId $id,
        private Email $email,
        private string $name,
        private DateTimeImmutable $createdAt,
        private bool $isActive = true
    ) {
        $this->recordEvent(new UserCreatedEvent($id->value()));
    }

    public static function create(
        UserId $id,
        Email $email,
        string $name
    ): self {
        return new self(
            $id,
            $email,
            $name,
            new DateTimeImmutable()
        );
    }

    public function deactivate(): void
    {
        $this->isActive = false;
    }

    public function canPlaceOrder(): bool
    {
        return $this->isActive;
    }

    public function id(): UserId
    {
        return $this->id;
    }

    public function email(): Email
    {
        return $this->email;
    }

    public function domainEvents(): array
    {
        return $this->domainEvents;
    }

    public function clearDomainEvents(): void
    {
        $this->domainEvents = [];
    }

    private function recordEvent(object $event): void
    {
        $this->domainEvents[] = $event;
    }
}
```

## Repository Port (Interface)

```php
<?php
// src/Domain/Repository/UserRepositoryInterface.php

namespace App\Domain\Repository;

use App\Domain\Entity\User;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;

interface UserRepositoryInterface
{
    public function findById(UserId $id): ?User;

    public function findByEmail(Email $email): ?User;

    public function save(User $user): void;

    public function delete(UserId $id): void;
}
```

## Command and Handler

```php
<?php
// src/Application/Command/CreateUserCommand.php

namespace App\Application\Command;

final readonly class CreateUserCommand
{
    public function __construct(
        public string $id,
        public string $email,
        public string $name
    ) {
    }
}
```

```php
<?php
// src/Application/Handler/CreateUserHandler.php

namespace App\Application\Handler;

use App\Application\Command\CreateUserCommand;
use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use InvalidArgumentException;

readonly class CreateUserHandler
{
    public function __construct(
        private UserRepositoryInterface $userRepository
    ) {
    }

    public function __invoke(CreateUserCommand $command): void
    {
        $email = new Email($command->email);

        if ($this->userRepository->findByEmail($email) !== null) {
            throw new InvalidArgumentException(
                'User with this email already exists'
            );
        }

        $user = User::create(
            new UserId($command->id),
            $email,
            $command->name
        );

        $this->userRepository->save($user);
    }
}
```

## Symfony Controller

```php
<?php
// src/Adapter/Http/Controller/UserController.php

namespace App\Adapter\Http\Controller;

use App\Adapter\Http\Request\CreateUserRequest;
use App\Application\Command\CreateUserCommand;
use App\Application\Handler\CreateUserHandler;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Uid\Uuid;

#[AsController]
class UserController
{
    public function __construct(
        private CreateUserHandler $createUserHandler
    ) {
    }

    #[Route('/api/users', methods: ['POST'])]
    public function create(CreateUserRequest $request): JsonResponse
    {
        $command = new CreateUserCommand(
            id: Uuid::v4()->toRfc4122(),
            email: $request->email,
            name: $request->name
        );

        ($this->createUserHandler)($command);

        return new JsonResponse(['id' => $command->id], 201);
    }
}
```

## Request DTO with Validation

```php
<?php
// src/Adapter/Http/Request/CreateUserRequest.php

namespace App\Adapter\Http\Request;

use Symfony\Component\Validator\Constraints as Assert;

class CreateUserRequest
{
    #[Assert\NotBlank]
    #[Assert\Email]
    public string $email;

    #[Assert\NotBlank]
    #[Assert\Length(min: 2, max: 100)]
    public string $name;
}
```

## Doctrine Repository Adapter

```php
<?php
// src/Adapter/Persistence/Doctrine/Repository/DoctrineUserRepository.php

namespace App\Adapter\Persistence\Doctrine\Repository;

use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use Doctrine\ORM\EntityManagerInterface;

readonly class DoctrineUserRepository implements UserRepositoryInterface
{
    public function __construct(
        private EntityManagerInterface $entityManager
    ) {
    }

    public function findById(UserId $id): ?User
    {
        return $this->entityManager
            ->getRepository(User::class)
            ->find($id->value());
    }

    public function findByEmail(Email $email): ?User
    {
        return $this->entityManager
            ->getRepository(User::class)
            ->findOneBy(['email.value' => $email->value()]);
    }

    public function save(User $user): void
    {
        $this->entityManager->persist($user);
        $this->entityManager->flush();
    }

    public function delete(UserId $id): void
    {
        $user = $this->findById($id);
        if ($user !== null) {
            $this->entityManager->remove($user);
            $this->entityManager->flush();
        }
    }
}
```

## Symfony DI Configuration

```yaml
# config/services.yaml
services:
    _defaults:
        autowire: true
        autoconfigure: true

    App\:
        resource: '../src/'
        exclude:
            - '../src/Domain/Entity/'
            - '../src/Kernel.php'

    # Repository binding - Port to Adapter
    App\Domain\Repository\UserRepositoryInterface:
        class: App\Adapter\Persistence\Doctrine\Repository\DoctrineUserRepository

    # In-memory repository for tests
    App\Domain\Repository\UserRepositoryInterface $inMemoryUserRepository:
        class: App\Tests\Infrastructure\Repository\InMemoryUserRepository
```

## In-Memory Repository for Testing

```php
<?php
// tests/Infrastructure/Repository/InMemoryUserRepository.php

namespace App\Tests\Infrastructure\Repository;

use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;

class InMemoryUserRepository implements UserRepositoryInterface
{
    private array $users = [];

    public function findById(UserId $id): ?User
    {
        return $this->users[$id->value()] ?? null;
    }

    public function findByEmail(Email $email): ?User
    {
        foreach ($this->users as $user) {
            if ($user->email()->equals($email)) {
                return $user;
            }
        }
        return null;
    }

    public function save(User $user): void
    {
        $this->users[$user->id()->value()] = $user;
    }

    public function delete(UserId $id): void
    {
        unset($this->users[$id->value()]);
    }
}
```
