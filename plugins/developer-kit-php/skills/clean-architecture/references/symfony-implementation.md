# Symfony Implementation Guide

## Project Setup

### Directory Structure

```
project/
├── config/
│   ├── packages/
│   │   ├── doctrine.yaml
│   │   └── messenger.yaml
│   └── services.yaml
├── src/
│   ├── Domain/
│   ├── Application/
│   ├── Adapter/
│   ├── Infrastructure/
│   └── Kernel.php
├── tests/
│   ├── Unit/
│   ├── Integration/
│   └── Infrastructure/
└── composer.json
```

### Composer Dependencies

```json
{
    "require": {
        "php": ">=8.3",
        "symfony/framework-bundle": "^7.0",
        "symfony/dependency-injection": "^7.0",
        "symfony/messenger": "^7.0",
        "symfony/serializer": "^7.0",
        "symfony/property-access": "^7.0",
        "symfony/uid": "^7.0",
        "doctrine/orm": "^3.0",
        "doctrine/dbal": "^4.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^11.0",
        "symfony/test-pack": "^1.0"
    }
}
```

## Dependency Injection Configuration

### Autowiring Repository Interface

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

    # Bind interface to implementation
    App\Domain\Repository\UserRepositoryInterface:
        class: App\Adapter\Persistence\Doctrine\Repository\DoctrineUserRepository

    App\Domain\Repository\OrderRepositoryInterface:
        class: App\Adapter\Persistence\Doctrine\Repository\DoctrineOrderRepository
```

### Multiple Implementations with Named Services

```yaml
# config/services.yaml
services:
    # Primary: Doctrine implementation
    App\Domain\Repository\UserRepositoryInterface:
        alias: App\Adapter\Persistence\Doctrine\Repository\DoctrineUserRepository

    # Alternative: In-memory for testing
    App\Infrastructure\Repository\InMemoryUserRepository:
        class: App\Infrastructure\Repository\InMemoryUserRepository

    # Use named autowiring
    App\Application\Handler\CreateUserHandler:
        arguments:
            $userRepository: '@App\Domain\Repository\UserRepositoryInterface'
```

### #[Autowire] Attribute (PHP 8)

```php
<?php
// src/Infrastructure/Service/SendgridEmailService.php

namespace App\Infrastructure\Service;

use App\Application\Service\EmailServiceInterface;
use Symfony\Component\DependencyInjection\Attribute\Autowire;

readonly class SendgridEmailService implements EmailServiceInterface
{
    public function __construct(
        #[Autowire('%env(SENDGRID_API_KEY)%')]
        private string $apiKey,
        #[Autowire('%env(SENDGRID_FROM_EMAIL)%')]
        private string $fromEmail
    ) {
    }

    public function send(string $to, string $subject, string $body): void
    {
        // Sendgrid implementation
    }
}
```

## Doctrine ORM Mapping

### XML Mapping (Recommended)

```xml
<!-- config/doctrine/User.orm.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<doctrine-mapping xmlns="https://doctrine-project.org/schemas/orm/doctrine-mapping"
                  xmlns:xsi="https://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="https://doctrine-project.org/schemas/orm/doctrine-mapping
                                      https://www.doctrine-project.org/schemas/orm/doctrine-mapping.xsd">

    <entity name="App\Domain\Entity\User" table="users">
        <id name="id" type="string" length="36">
            <generator strategy="NONE"/>
        </id>

        <embedded name="email" class="App\Domain\ValueObject\Email"/>

        <field name="name" type="string" length="100"/>

        <field name="createdAt" type="datetime_immutable"/>

        <field name="isActive" type="boolean"/>
    </entity>
</doctrine-mapping>
```

### Value Object Embeddable

```xml
<!-- config/doctrine/Email.orm.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<doctrine-mapping xmlns="https://doctrine-project.org/schemas/orm/doctrine-mapping">

    <embeddable name="App\Domain\ValueObject\Email">
        <field name="value" type="string" column="email" length="255"/>
    </embeddable>

</doctrine-mapping>
```

### Attribute Mapping (Alternative)

```php
<?php
// src/Domain/Entity/User.php

namespace App\Domain\Entity;

use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use DateTimeImmutable;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity]
#[ORM\Table(name: 'users')]
class User
{
    #[ORM\Id]
    #[ORM\Column(type: 'string', length: 36)]
    private string $id;

    #[ORM\Embedded(class: Email::class)]
    private Email $email;

    #[ORM\Column(type: 'string', length: 100)]
    private string $name;

    #[ORM\Column(type: 'datetime_immutable')]
    private DateTimeImmutable $createdAt;

    #[ORM\Column(type: 'boolean')]
    private bool $isActive = true;

    // ... methods
}
```

## Controllers with Attributes

### REST API Controller

```php
<?php
// src/Adapter/Http/Controller/Api/UserController.php

namespace App\Adapter\Http\Controller\Api;

use App\Adapter\Http\Request\CreateUserRequest;
use App\Adapter\Http\Request\UpdateUserRequest;
use App\Application\Command\CreateUserCommand;
use App\Application\Command\UpdateUserCommand;
use App\Application\Handler\CreateUserHandler;
use App\Application\Handler\UpdateUserHandler;
use App\Application\Query\GetUserQuery;
use App\Domain\ValueObject\UserId;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpKernel\Attribute\AsController;
use Symfony\Component\HttpKernel\Attribute\MapRequestPayload;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Uid\Uuid;

#[AsController]
#[Route('/api/users')]
class UserController
{
    public function __construct(
        private CreateUserHandler $createHandler,
        private UpdateUserHandler $updateHandler,
        private GetUserQuery $getUserQuery
    ) {
    }

    #[Route('', methods: ['POST'])]
    public function create(
        #[MapRequestPayload] CreateUserRequest $request
    ): JsonResponse {
        $id = Uuid::v4()->toRfc4122();

        $command = new CreateUserCommand(
            id: $id,
            email: $request->email,
            name: $request->name
        );

        ($this->createHandler)($command);

        return new JsonResponse(
            ['id' => $id, 'message' => 'User created'],
            Response::HTTP_CREATED
        );
    }

    #[Route('/{id}', methods: ['GET'])]
    public function get(string $id): JsonResponse
    {
        $user = $this->getUserQuery->execute(new UserId($id));

        if ($user === null) {
            return new JsonResponse(
                ['error' => 'User not found'],
                Response::HTTP_NOT_FOUND
            );
        }

        return new JsonResponse($user);
    }

    #[Route('/{id}', methods: ['PUT'])]
    public function update(
        string $id,
        #[MapRequestPayload] UpdateUserRequest $request
    ): JsonResponse {
        $command = new UpdateUserCommand(
            id: $id,
            name: $request->name
        );

        ($this->updateHandler)($command);

        return new JsonResponse(['message' => 'User updated']);
    }
}
```

### Request Validation with Attributes

```php
<?php
// src/Adapter/Http/Request/CreateUserRequest.php

namespace App\Adapter\Http\Request;

use Symfony\Component\Validator\Constraints as Assert;

class CreateUserRequest
{
    #[Assert\NotBlank(message: 'Email is required')]
    #[Assert\Email(message: 'Invalid email format')]
    public string $email;

    #[Assert\NotBlank(message: 'Name is required')]
    #[Assert\Length(
        min: 2,
        max: 100,
        minMessage: 'Name must be at least {{ limit }} characters',
        maxMessage: 'Name cannot exceed {{ limit }} characters'
    )]
    public string $name;
}
```

## Symfony Messenger for Commands

### Command Bus Configuration

```yaml
# config/packages/messenger.yaml
framework:
    messenger:
        default_bus: command.bus

        buses:
            command.bus:
                middleware:
                    - doctrine_transaction_middleware

        transports:
            async: '%env(MESSENGER_TRANSPORT_DSN)%'

        routing:
            App\Application\Command\SendNotificationCommand: async
```

### Message Handler

```php
<?php
// src/Application/Handler/CreateUserHandler.php

namespace App\Application\Handler;

use App\Application\Command\CreateUserCommand;
use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use Symfony\Component\Messenger\Attribute\AsMessageHandler;

#[AsMessageHandler(bus: 'command.bus')]
readonly class CreateUserHandler
{
    public function __construct(
        private UserRepositoryInterface $userRepository
    ) {
    }

    public function __invoke(CreateUserCommand $command): void
    {
        $user = User::create(
            new UserId($command->id),
            new Email($command->email),
            $command->name
        );

        $this->userRepository->save($user);
    }
}
```

### Dispatching Commands

```php
<?php
// src/Adapter/Http/Controller/UserController.php

use Symfony\Component\Messenger\MessageBusInterface;

class UserController
{
    public function __construct(
        private MessageBusInterface $commandBus
    ) {
    }

    #[Route('/api/users', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        $command = new CreateUserCommand(
            id: Uuid::v4()->toRfc4122(),
            email: $data['email'],
            name: $data['name']
        );

        $this->commandBus->dispatch($command);

        return new JsonResponse(['id' => $command->id], 201);
    }
}
```

## Domain Events with Symfony EventDispatcher

### Domain Event Listener

```php
<?php
// src/Infrastructure/Event/DomainEventDispatcher.php

namespace App\Infrastructure\Event;

use App\Domain\Event\UserCreatedEvent;
use Psr\Log\LoggerInterface;
use Symfony\Component\EventDispatcher\Attribute\AsEventListener;

#[AsEventListener(event: UserCreatedEvent::class, method: 'onUserCreated')]
readonly class UserCreatedListener
{
    public function __construct(
        private LoggerInterface $logger,
        private EmailServiceInterface $emailService
    ) {
    }

    public function onUserCreated(UserCreatedEvent $event): void
    {
        $this->logger->info('User created', ['user_id' => $event->userId]);

        // Send welcome email
        $this->emailService->sendWelcomeEmail($event->userId);
    }
}
```

### Publishing Domain Events

```php
<?php
// src/Adapter/Persistence/Doctrine/Repository/DoctrineUserRepository.php

namespace App\Adapter\Persistence\Doctrine\Repository;

use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Contracts\EventDispatcher\EventDispatcherInterface;

readonly class DoctrineUserRepository implements UserRepositoryInterface
{
    public function __construct(
        private EntityManagerInterface $entityManager,
        private EventDispatcherInterface $eventDispatcher
    ) {
    }

    public function save(User $user): void
    {
        $this->entityManager->persist($user);
        $this->entityManager->flush();

        // Dispatch domain events
        foreach ($user->domainEvents() as $event) {
            $this->eventDispatcher->dispatch($event);
        }
        $user->clearDomainEvents();
    }
}
```

## Testing with Symfony

### Integration Test

```php
<?php
// tests/Integration/Controller/UserControllerTest.php

namespace App\Tests\Integration\Controller;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class UserControllerTest extends WebTestCase
{
    public function testCanCreateUser(): void
    {
        $client = static::createClient();

        $client->request(
            'POST',
            '/api/users',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode([
                'email' => 'test@example.com',
                'name' => 'John Doe'
            ])
        );

        $this->assertResponseStatusCodeSame(201);

        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertArrayHasKey('id', $response);
    }

    public function testReturns404ForNonExistentUser(): void
    {
        $client = static::createClient();

        $client->request('GET', '/api/users/non-existent-id');

        $this->assertResponseStatusCodeSame(404);
    }
}
```

### Repository Integration Test

```php
<?php
// tests/Integration/Repository/UserRepositoryTest.php

namespace App\Tests\Integration\Repository;

use App\Domain\Entity\User;
use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\Email;
use App\Domain\ValueObject\UserId;
use Symfony\Bundle\FrameworkBundle\Test\KernelTestCase;

class UserRepositoryTest extends KernelTestCase
{
    private UserRepositoryInterface $repository;

    protected function setUp(): void
    {
        self::bootKernel();
        $this->repository = self::getContainer()->get(UserRepositoryInterface::class);
    }

    public function testCanSaveAndRetrieveUser(): void
    {
        $user = User::create(
            UserId::generate(),
            new Email('test@example.com'),
            'John Doe'
        );

        $this->repository->save($user);

        $retrieved = $this->repository->findById($user->id());

        $this->assertNotNull($retrieved);
        $this->assertTrue($user->email()->equals($retrieved->email()));
    }
}
```

## Error Handling

### Domain Exception Handler

```php
<?php
// src/Infrastructure/Http/Exception/DomainExceptionHandler.php

namespace App\Infrastructure\Http\Exception;

use InvalidArgumentException;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpKernel\Event\ExceptionEvent;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;

class DomainExceptionHandler
{
    public function onKernelException(ExceptionEvent $event): void
    {
        $exception = $event->getThrowable();

        if ($exception instanceof InvalidArgumentException) {
            $response = new JsonResponse([
                'error' => 'Validation failed',
                'message' => $exception->getMessage()
            ], Response::HTTP_BAD_REQUEST);

            $event->setResponse($response);
            return;
        }

        // Handle other domain exceptions
        if ($exception instanceof DomainException) {
            $response = new JsonResponse([
                'error' => 'Domain error',
                'message' => $exception->getMessage()
            ], Response::HTTP_UNPROCESSABLE_ENTITY);

            $event->setResponse($response);
        }
    }
}
```

### Registering Exception Handler

```yaml
# config/services.yaml
services:
    App\Infrastructure\Http\Exception\DomainExceptionHandler:
        tags:
            - { name: kernel.event_listener, event: kernel.exception }
```

## Query Bus (CQRS)

### Query Interface

```php
<?php
// src/Application/Query/QueryInterface.php

namespace App\Application\Query;

interface QueryInterface
{
}
```

### Query Handler

```php
<?php
// src/Application/Query/GetUserQuery.php

namespace App\Application\Query;

use App\Domain\Repository\UserRepositoryInterface;
use App\Domain\ValueObject\UserId;

readonly class GetUserQuery
{
    public function __construct(
        private UserRepositoryInterface $userRepository
    ) {
    }

    public function execute(UserId $id): ?array
    {
        $user = $this->userRepository->findById($id);

        if ($user === null) {
            return null;
        }

        return [
            'id' => $user->id()->value(),
            'email' => $user->email()->value(),
            'name' => $user->name(),
            'createdAt' => $user->createdAt()->format('c'),
            'isActive' => $user->isActive()
        ];
    }
}
```

## Best Practices for Symfony

1. **Use Attributes**: Leverage PHP 8 attributes for routing, validation, DI, and event listening.

2. **Keep Controllers Thin**: Controllers should only handle HTTP concerns and delegate to application layer.

3. **Use DTOs**: Separate request/response DTOs from domain entities.

4. **Validation at Boundaries**: Validate input at the adapter layer (controllers), not in domain.

5. **Messenger for Async**: Use Symfony Messenger for commands that need async processing.

6. **XML/Attribute Mapping**: Prefer XML or PHP 8 attributes for Doctrine mapping over annotations.

7. **Service Autoconfiguration**: Let Symfony autoconfigure your services, only override when necessary.

8. **Test with Real Container**: Use `KernelTestCase` for integration tests with real DI container.

9. **Environment Variables**: Use `%env()%` for configuration that changes per environment.

10. **Monolog for Logging**: Use PSR-3 logger interface in domain, Monolog implementation in infrastructure.
