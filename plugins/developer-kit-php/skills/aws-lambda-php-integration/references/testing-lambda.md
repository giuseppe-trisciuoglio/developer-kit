# Testing Lambda Reference

Patterns for testing PHP Lambda functions including unit tests, integration tests, and local development.

## Table of Contents

1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [Local Development](#local-development)
4. [Mocking AWS Services](#mocking-aws-services)

---

## Unit Testing

### PHPUnit Configuration

```xml
<!-- phpunit.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="https://schema.phpunit.de/10.0/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true"
         cacheDirectory=".phpunit.cache">
    <testsuites>
        <testsuite name="Unit">
            <directory>tests/Unit</directory>
        </testsuite>
        <testsuite name="Integration">
            <directory>tests/Integration</directory>
        </testsuite>
    </testsuites>
    <source>
        <include>
            <directory>src</directory>
        </include>
    </source>
</phpunit>
```

### Basic Unit Test

```php
// tests/Unit/UserServiceTest.php
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Services\UserService;
use App\Services\DynamoDbService;

class UserServiceTest extends TestCase
{
    private UserService $service;
    private $mockDb;

    protected function setUp(): void
    {
        parent::setUp();

        // Create mock for DynamoDB service
        $this->mockDb = $this->createMock(DynamoDbService::class);
        $this->service = new UserService($this->mockDb);
    }

    public function testGetUserReturnsUserData(): void
    {
        $userId = 'user-123';
        $expectedData = ['id' => $userId, 'name' => 'Test User'];

        $this->mockDb->expects($this->once())
            ->method('get')
            ->with($userId)
            ->willReturn($expectedData);

        $result = $this->service->getUser($userId);

        $this->assertEquals($expectedData, $result);
    }

    public function testCreateUserReturnsNewId(): void
    {
        $userData = ['name' => 'New User'];

        $this->mockDb->expects($this->once())
            ->method('put')
            ->willReturnCallback(function ($id, $data) {
                $this->assertNotEmpty($id);
                $this->assertEquals('New User', $data['name']);
            });

        $result = $this->service->createUser($userData);

        $this->assertNotEmpty($result['id']);
    }

    public function testGetUserThrowsExceptionForInvalidId(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('User ID is required');

        $this->service->getUser('');
    }
}
```

### Testing Handler Logic

```php
// tests/Unit/HandlerTest.php
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

class HandlerTest extends TestCase
{
    public function testHealthCheckReturnsOk(): void
    {
        $event = [
            'path' => '/health',
            'httpMethod' => 'GET'
        ];

        $result = handleHealthCheck($event);

        $this->assertEquals(200, $result['statusCode']);
        $this->assertJson($result['body']);
    }

    public function testGetUsersReturnsUserList(): void
    {
        $event = [
            'path' => '/users',
            'httpMethod' => 'GET'
        ];

        $result = handleUsers('GET', $event, []);

        $this->assertEquals(200, $result['statusCode']);
        $body = json_decode($result['body'], true);
        $this->assertArrayHasKey('users', $body);
    }

    public function testCreateUserReturnsCreatedStatus(): void
    {
        $event = [
            'path' => '/users',
            'httpMethod' => 'POST',
            'body' => json_encode(['name' => 'Test User'])
        ];

        $result = handleUsers('POST', $event, []);

        $this->assertEquals(201, $result['statusCode']);
        $body = json_decode($result['body'], true);
        $this->assertArrayHasKey('id', $body);
    }

    public function testInvalidPathReturns404(): void
    {
        $event = [
            'path' => '/invalid',
            'httpMethod' => 'GET'
        ];

        $result = handleRequest($event, []);

        $this->assertEquals(404, $result['statusCode']);
    }
}
```

---

## Integration Testing

### Testing with LocalStack

```yaml
# docker-compose.yml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      SERVICES: dynamodb,s3
      DEFAULT_REGION: us-east-1
    volumes:
      - localstack-data:/var/lib/localstack

  php:
    build: .
    depends_on:
      - localstack
    environment:
      AWS_ACCESS_KEY_ID: test
      AWS_SECRET_ACCESS_KEY: test
      AWS_REGION: us-east-1
      DYNAMODB_ENDPOINT: http://localstack:4566
```

### Integration Test Example

```php
// tests/Integration/UserServiceIntegrationTest.php
<?php

namespace Tests\Integration;

use PHPUnit\Framework\TestCase;
use App\Services\DynamoDbService;
use App\Services\UserService;

class UserServiceIntegrationTest extends TestCase
{
    private UserService $service;
    private string $tableName = 'test-users';

    protected function setUp(): void
    {
        parent::setUp();

        // Use local DynamoDB for testing
        $endpoint = getenv('DYNAMODB_ENDPOINT') ?: 'http://localhost:4566';

        $dbService = new DynamoDbService($this->tableName, $endpoint);
        $this->service = new UserService($dbService);

        // Create table if not exists
        $this->createTable();
    }

    private function createTable(): void
    {
        $client = new \Aws\DynamoDb\DynamoDbClient([
            'region' => 'us-east-1',
            'endpoint' => getenv('DYNAMODB_ENDPOINT'),
            'credentials' => [
                'key' => 'test',
                'secret' => 'test'
            ]
        ]);

        try {
            $client->createTable([
                'TableName' => $this->tableName,
                'KeySchema' => [
                    ['AttributeName' => 'id', 'KeyType' => 'HASH']
                ],
                'AttributeDefinitions' => [
                    ['AttributeName' => 'id', 'AttributeType' => 'S']
                ],
                'BillingMode' => 'PAY_PER_REQUEST'
            ]);
        } catch (\Aws\DynamoDb\Exception\ResourceInUseException $e) {
            // Table already exists
        }
    }

    public function testFullUserLifecycle(): void
    {
        // Create
        $user = $this->service->createUser([
            'name' => 'Test User',
            'email' => 'test@example.com'
        ]);

        $this->assertNotEmpty($user['id']);

        // Read
        $found = $this->service->getUser($user['id']);
        $this->assertEquals('Test User', $found['name']);

        // Update
        $updated = $this->service->updateUser($user['id'], ['name' => 'Updated']);
        $this->assertEquals('Updated', $updated['name']);

        // Delete
        $this->service->deleteUser($user['id']);
        $this->assertNull($this->service->getUser($user['id']));
    }

    protected function tearDown(): void
    {
        // Clean up test table
        parent::tearDown();
    }
}
```

---

## Local Development

### Serverless Offline

```bash
# Install serverless-offline
composer require bref/serverless-offline --dev
```

```yaml
# serverless.yml
plugins:
  - ./vendor/bref/bref
  - ./vendor/bref/serverless-offline/plugin.yml

functions:
  api:
    handler: public/index.php
```

```bash
# Run locally
vendor/bin/serverless offline start
```

### PHP Built-in Server

```php
// public/index.php
use Symfony\Component\HttpFoundation\Request;

// Check if running locally
if (php_sapi_name() === 'cli-server') {
    $request = Request::createFromGlobals();
    // Handle request directly
    echo handleRequest($request);
    exit;
}
```

```bash
# Start local server
php -S localhost:8000 -t public/
```

---

## Mocking AWS Services

### Using Mockery

```php
// tests/Mocks/AwsMocks.php
<?php

namespace Tests\Mocks;

use Aws\Result;
use Mockery;

class AwsMocks
{
    public static function dynamoDbGetItem(array $item): Result
    {
        return new Result([
            'Item' => $item
        ]);
    }

    public static function dynamoDbPutItem(): Result
    {
        return new Result([
            'Attributes' => [
                'id' => ['S' => 'test-id']
            ]
        ]);
    }

    public static function dynamoDbDeleteItem(): Result
    {
        return new Result([]);
    }

    public static function s3GetObject(string $content): Result
    {
        return new Result([
            'Body' => Mockery::mock('GuzzleHttp\Psr7\Stream')
                ->shouldReceive('getContents')
                ->andReturn($content)
                ->getMock()
        ]);
    }
}
```

### Mocking in Tests

```php
// tests/Unit/UserServiceWithMocksTest.php
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use Aws\Result;
use App\Services\UserService;
use App\Services\DynamoDbService;
use Tests\Mocks\AwsMocks;

class UserServiceWithMocksTest extends TestCase
{
    public function testGetUserWithMockedDynamoDb(): void
    {
        $mockDb = $this->createMock(DynamoDbService::class);
        $mockDb->method('get')
            ->willReturn(AwsMocks::dynamoDbGetItem([
                'id' => ['S' => 'user-123'],
                'name' => ['S' => 'Test User']
            ]));

        $service = new UserService($mockDb);
        $result = $service->getUser('user-123');

        $this->assertEquals('user-123', $result['id']);
        $this->assertEquals('Test User', $result['name']);
    }
}
```

---

## Test Coverage

### Running Tests

```bash
# Run all tests
vendor/bin/phpunit

# Run specific test suite
vendor/bin/phpunit --testsuite=Unit

# Run with coverage
vendor/bin/phpunit --coverage-html coverage
```

### CI Integration

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: vendor/bin/phpunit --coverage-text

- name: Upload coverage
  if: github.event_name == 'pull_request'
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

---

## Performance Testing

### Cold Start Testing

```php
<?php

// Benchmark cold start
$times = [];
for ($i = 0; $i < 10; $i++) {
    // Simulate cold start by clearing opcache
    if (function_exists('opcache_reset')) {
        opcache_reset();
    }

    $start = microtime(true);

    // Initialize application
    require 'vendor/autoload.php';
    $app = require 'config/bootstrap.php';

    $end = microtime(true);
    $times[] = ($end - $start) * 1000;

    // Wait between tests
    sleep(2);
}

echo "Average cold start: " . (array_sum($times) / count($times)) . "ms\n";
echo "Min: " . min($times) . "ms\n";
echo "Max: " . max($times) . "ms\n";
```
