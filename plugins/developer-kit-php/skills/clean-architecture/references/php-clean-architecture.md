# PHP Clean Architecture Patterns

## Value Objects Deep Dive

### Money Value Object

```php
<?php
// src/Domain/ValueObject/Money.php

namespace App\Domain\ValueObject;

use InvalidArgumentException;

final readonly class Money
{
    public function __construct(
        private int $cents,
        private string $currency
    ) {
        if ($cents < 0) {
            throw new InvalidArgumentException('Amount cannot be negative');
        }

        if (!in_array($currency, ['EUR', 'USD', 'GBP'], true)) {
            throw new InvalidArgumentException('Unsupported currency');
        }
    }

    public static function fromEuros(float $amount): self
    {
        return new self((int) round($amount * 100), 'EUR');
    }

    public function cents(): int
    {
        return $this->cents;
    }

    public function asFloat(): float
    {
        return $this->cents / 100;
    }

    public function currency(): string
    {
        return $this->currency;
    }

    public function add(self $other): self
    {
        $this->assertSameCurrency($other);

        return new self($this->cents + $other->cents, $this->currency);
    }

    public function subtract(self $other): self
    {
        $this->assertSameCurrency($other);

        return new self($this->cents - $other->cents, $this->currency);
    }

    public function multiply(float $factor): self
    {
        return new self((int) round($this->cents * $factor), $this->currency);
    }

    public function equals(self $other): bool
    {
        return $this->cents === $other->cents
            && $this->currency === $other->currency;
    }

    public function isGreaterThan(self $other): bool
    {
        $this->assertSameCurrency($other);

        return $this->cents > $other->cents;
    }

    private function assertSameCurrency(self $other): void
    {
        if ($this->currency !== $other->currency) {
            throw new InvalidArgumentException('Currency mismatch');
        }
    }
}
```

### UUID Value Object

```php
<?php
// src/Domain/ValueObject/UserId.php

namespace App\Domain\ValueObject;

use InvalidArgumentException;
use Symfony\Component\Uid\Uuid;

final readonly class UserId
{
    private string $value;

    public function __construct(string $value)
    {
        if (!Uuid::isValid($value)) {
            throw new InvalidArgumentException('Invalid UUID format');
        }

        $this->value = $value;
    }

    public static function generate(): self
    {
        return new self(Uuid::v4()->toRfc4122());
    }

    public function value(): string
    {
        return $this->value;
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }

    public function __toString(): string
    {
        return $this->value;
    }
}
```

## Aggregate Pattern

```php
<?php
// src/Domain/Entity/Order.php

namespace App\Domain\Entity;

use App\Domain\ValueObject\Money;
use App\Domain\ValueObject\OrderId;
use App\Domain\Event\OrderSubmittedEvent;
use InvalidArgumentException;

class Order
{
    private array $items = [];
    private string $status = 'pending';
    private array $domainEvents = [];

    public function __construct(
        private OrderId $id,
        private UserId $userId
    ) {
    }

    public function addItem(string $productId, int $quantity, Money $price): void
    {
        if ($this->status !== 'pending') {
            throw new InvalidArgumentException('Cannot modify submitted order');
        }

        if ($quantity <= 0) {
            throw new InvalidArgumentException('Quantity must be positive');
        }

        $this->items[] = new OrderItem($productId, $quantity, $price);
    }

    public function submit(): void
    {
        if (empty($this->items)) {
            throw new InvalidArgumentException('Cannot submit empty order');
        }

        if ($this->status !== 'pending') {
            throw new InvalidArgumentException('Order already submitted');
        }

        $this->status = 'submitted';
        $this->recordEvent(new OrderSubmittedEvent($this->id->value()));
    }

    public function total(): Money
    {
        $total = Money::fromEuros(0);

        foreach ($this->items as $item) {
            $total = $total->add($item->total());
        }

        return $total;
    }

    public function id(): OrderId
    {
        return $this->id;
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

### OrderItem (Part of Aggregate)

```php
<?php
// src/Domain/Entity/OrderItem.php

namespace App\Domain\Entity;

use App\Domain\ValueObject\Money;

final readonly class OrderItem
{
    public function __construct(
        private string $productId,
        private int $quantity,
        private Money $unitPrice
    ) {
    }

    public function total(): Money
    {
        return $this->unitPrice->multiply($this->quantity);
    }
}
```

## Domain Services

When logic does not belong to a single entity:

```php
<?php
// src/Domain/Service/PricingService.php

namespace App\Domain\Service;

use App\Domain\Entity\Order;
use App\Domain\ValueObject\Money;

interface PricingServiceInterface
{
    public function calculateDiscount(Order $order): Money;
}
```

## Domain Events

```php
<?php
// src/Domain/Event/OrderSubmittedEvent.php

namespace App\Domain\Event;

use DateTimeImmutable;

final readonly class OrderSubmittedEvent
{
    public function __construct(
        public string $orderId,
        public DateTimeImmutable $occurredAt = new DateTimeImmutable()
    ) {
    }
}
```

## Specification Pattern

```php
<?php
// src/Domain/Specification/SpecificationInterface.php

namespace App\Domain\Specification;

interface SpecificationInterface
{
    public function isSatisfiedBy(object $candidate): bool;
}
```

```php
<?php
// src/Domain/Specification/ActiveUserSpecification.php

namespace App\Domain\Specification;

use App\Domain\Entity\User;

class ActiveUserSpecification implements SpecificationInterface
{
    public function isSatisfiedBy(object $candidate): bool
    {
        if (!$candidate instanceof User) {
            return false;
        }

        return $candidate->isActive();
    }
}
```

## Enum for Status (PHP 8.1+)

```php
<?php
// src/Domain/Enum/OrderStatus.php

namespace App\Domain\Enum;

enum OrderStatus: string
{
    case PENDING = 'pending';
    case SUBMITTED = 'submitted';
    case PAID = 'paid';
    case SHIPPED = 'shipped';
    case CANCELLED = 'cancelled';

    public function canTransitionTo(self $newStatus): bool
    {
        return match ($this) {
            self::PENDING => in_array($newStatus, [self::SUBMITTED, self::CANCELLED], true),
            self::SUBMITTED => in_array($newStatus, [self::PAID, self::CANCELLED], true),
            self::PAID => in_array($newStatus, [self::SHIPPED, self::CANCELLED], true),
            self::SHIPPED => false,
            self::CANCELLED => false,
        };
    }
}
```

## Testing Value Objects

```php
<?php
// tests/Domain/ValueObject/EmailTest.php

namespace App\Tests\Domain\ValueObject;

use App\Domain\ValueObject\Email;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

class EmailTest extends TestCase
{
    public function testCanCreateValidEmail(): void
    {
        $email = new Email('test@example.com');

        $this->assertEquals('test@example.com', $email->value());
    }

    public function testThrowsExceptionForInvalidEmail(): void
    {
        $this->expectException(InvalidArgumentException::class);

        new Email('invalid-email');
    }

    public function testEmailsAreComparable(): void
    {
        $email1 = new Email('test@example.com');
        $email2 = new Email('test@example.com');
        $email3 = new Email('other@example.com');

        $this->assertTrue($email1->equals($email2));
        $this->assertFalse($email1->equals($email3));
    }
}
```

## Testing Use Cases (No Framework)

```php
<?php
// tests/Application/Handler/CreateUserHandlerTest.php

namespace App\Tests\Application\Handler;

use App\Application\Command\CreateUserCommand;
use App\Application\Handler\CreateUserHandler;
use App\Tests\Infrastructure\Repository\InMemoryUserRepository;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

class CreateUserHandlerTest extends TestCase
{
    private InMemoryUserRepository $repository;
    private CreateUserHandler $handler;

    protected function setUp(): void
    {
        $this->repository = new InMemoryUserRepository();
        $this->handler = new CreateUserHandler($this->repository);
    }

    public function testCanCreateUser(): void
    {
        $command = new CreateUserCommand(
            id: '550e8400-e29b-41d4-a716-446655440000',
            email: 'test@example.com',
            name: 'John Doe'
        );

        ($this->handler)($command);

        $user = $this->repository->findById(new UserId($command->id));
        $this->assertNotNull($user);
        $this->assertEquals('John Doe', $user->name());
    }

    public function testCannotCreateDuplicateUser(): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('User with this email already exists');

        $command = new CreateUserCommand(
            id: '550e8400-e29b-41d4-a716-446655440000',
            email: 'test@example.com',
            name: 'John Doe'
        );

        ($this->handler)($command);
        ($this->handler)($command);
    }
}
```
