# Raw PHP Lambda Reference

Minimal PHP Lambda handler patterns without framework overhead for maximum performance.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Handler Patterns](#handler-patterns)
3. [Cold Start Optimization](#cold-start-optimization)
4. [AWS SDK Integration](#aws-sdk-integration)
5. [Packaging](#packaging)

---

## Project Setup

### Basic composer.json

```json
{
    "name": "my/lambda-function",
    "description": "Raw PHP Lambda",
    "require": {
        "php": "^8.2",
        "bref/bref": "^2.0",
        "aws/aws-sdk-php": "^3.300"
    },
    "autoload": {
        "psr-4": {
            "App\\": "src/"
        }
    },
    "config": {
        "optimize-autoloader": true
    }
}
```

### Project Structure

```
my-lambda-function/
├── composer.json
├── serverless.yml
├── public/
│   └── index.php
├── src/
│   ├── Handler.php
│   └── Services/
│       └── DynamoDbService.php
└── conf.d/
    └── lambda.ini
```

---

## Handler Patterns

### Basic Request Handler

```php
// public/index.php
use function Bref\Lambda\handler;

handler(function (array $event, $context) {
    $path = $event['path'] ?? '/';
    $method = $event['httpMethod'] ?? 'GET';

    switch ($path) {
        case '/health':
            return healthCheck();
        case '/users':
            return handleUsers($method, $event);
        default:
            return notFound();
    }
});

function healthCheck(): array
{
    return [
        'statusCode' => 200,
        'body' => json_encode(['status' => 'ok'])
    ];
}

function handleUsers(string $method, array $event): array
{
    return match($method) {
        'GET' => listUsers($event),
        'POST' => createUser($event),
        default => methodNotAllowed()
    };
}

function listUsers(array $event): array
{
    return [
        'statusCode' => 200,
        'body' => json_encode(['users' => []])
    ];
}

function createUser(array $event): array
{
    $body = json_decode($event['body'] ?? '{}', true);
    return [
        'statusCode' => 201,
        'body' => json_encode(['id' => 'new-user-id'])
    ];
}

function notFound(): array
{
    return [
        'statusCode' => 404,
        'body' => json_encode(['error' => 'Not found'])
    ];
}

function methodNotAllowed(): array
{
    return [
        'statusCode' => 405,
        'body' => json_encode(['error' => 'Method not allowed'])
    ];
}
```

### PSR-15 Handler

```php
// public/index.php
use Psr\Http\Server\RequestHandlerInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Message\ResponseInterface;
use Nyholm\Psr7\ServerRequest;
use Nyholm\Psr7\Response;
use function Bref\Lambda\handler;

class PsrHandler implements RequestHandlerInterface
{
    public function handle(ServerRequestInterface $request): ResponseInterface
    {
        $path = $request->getUri()->getPath();

        if ($path === '/api/users') {
            return new Response(
                200,
                ['Content-Type' => 'application/json'],
                json_encode(['users' => []])
            );
        }

        return new Response(404, [], json_encode(['error' => 'Not found']));
    }
}

handler(function (array $event, $context) {
    $request = ServerRequest::fromArrays(
        $event['headers'] ?? [],
        [], // query params
        $event['body'] ?? null,
        $event['httpMethod'] ?? 'GET',
        $event['path'] ?? '/'
    );

    $handler = new PsrHandler();
    $response = $handler->handle($request);

    return [
        'statusCode' => $response->getStatusCode(),
        'headers' => $response->getHeaders(),
        'body' => (string) $response->getBody()
    ];
});
```

---

## Cold Start Optimization

### Lazy Loading Pattern

```php
// src/Services/LazyServiceLoader.php
class LazyServiceLoader
{
    private static array $cache = [];

    public static function getDynamoDbClient(): \Aws\DynamoDb\DynamoDbClient
    {
        $key = 'dynamodb';

        if (!isset(self::$cache[$key])) {
            self::$cache[$key] = new \Aws\DynamoDb\DynamoDbClient([
                'region' => getenv('AWS_REGION') ?: 'us-east-1',
                'version' => 'latest',
            ]);
        }

        return self::$cache[$key];
    }
}
```

### Singleton Pattern

```php
// src/Services/UserService.php
class UserService
{
    private static ?self $instance = null;
    private \Aws\DynamoDb\DynamoDbClient $db;

    private function __construct()
    {
        $this->db = LazyServiceLoader::getDynamoDbClient();
    }

    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function getUser(string $id): array
    {
        $result = $this->db->getItem([
            'TableName' => getenv('USERS_TABLE'),
            'Key' => ['id' => ['S' => $id]]
        ]);

        return $result['Item'] ?? [];
    }
}
```

### Module-Level Caching

```php
// public/index.php
// Declare at the top - persists across warm invocations
$dbClient = null;
$tableName = null;

function getDbClient(): \Aws\DynamoDb\DynamoDbClient
{
    global $dbClient;

    if ($dbClient === null) {
        $dbClient = new \Aws\DynamoDb\DynamoDbClient([
            'region' => getenv('AWS_REGION') ?: 'us-east-1',
            'version' => 'latest',
        ]);
    }

    return $dbClient;
}

function getTableName(): string
{
    global $tableName;

    if ($tableName === null) {
        $tableName = getenv('USERS_TABLE') ?: 'users';
    }

    return $tableName;
}

handler(function (array $event, $context) {
    $client = getDbClient();
    $table = getTableName();

    $result = $client->scan([
        'TableName' => $table
    ]);

    return [
        'statusCode' => 200,
        'body' => json_encode($result['Items'])
    ];
});
```

---

## AWS SDK Integration

### DynamoDB Operations

```php
// src/Services/DynamoDbService.php
class DynamoDbService
{
    private \Aws\DynamoDb\DynamoDbClient $client;
    private string $tableName;

    public function __construct(string $tableName)
    {
        $this->client = new \Aws\DynamoDb\DynamoDbClient([
            'region' => getenv('AWS_REGION') ?: 'us-east-1',
            'version' => 'latest',
        ]);
        $this->tableName = $tableName;
    }

    public function get(string $id): ?array
    {
        $result = $this->client->getItem([
            'TableName' => $this->tableName,
            'Key' => ['id' => ['S' => $id]]
        ]);

        return $result['Item'] ?? null;
    }

    public function put(string $id, array $data): void
    {
        $item = ['id' => ['S' => $id]];

        foreach ($data as $key => $value) {
            $item[$key] = is_string($value) ? ['S' => $value] : ['N' => (string) $value];
        }

        $this->client->putItem([
            'TableName' => $this->tableName,
            'Item' => $item
        ]);
    }

    public function delete(string $id): void
    {
        $this->client->deleteItem([
            'TableName' => $this->tableName,
            'Key' => ['id' => ['S' => $id]]
        ]);
    }

    public function query(string $pk, string $sk = null): array
    {
        $params = [
            'TableName' => $this->tableName,
            'KeyConditionExpression' => 'id = :id',
            'ExpressionAttributeValues' => [':id' => ['S' => $pk]]
        ];

        if ($sk) {
            $params['KeyConditionExpression'] .= ' AND sort = :sort';
            $params['ExpressionAttributeValues'][':sort'] = ['S' => $sk];
        }

        $result = $this->client->query($params);
        return $result['Items'] ?? [];
    }
}
```

### S3 Operations

```php
class S3Service
{
    private \Aws\S3\S3Client $client;
    private string $bucket;

    public function __construct(string $bucket)
    {
        $this->client = new \Aws\S3\S3Client([
            'region' => getenv('AWS_REGION') ?: 'us-east-1',
            'version' => 'latest',
        ]);
        $this->bucket = $bucket;
    }

    public function getObject(string $key): string
    {
        $result = $this->client->getObject([
            'Bucket' => $this->bucket,
            'Key' => $key
        ]);

        return (string) $result['Body'];
    }

    public function putObject(string $key, string $content, string $contentType = 'text/plain'): void
    {
        $this->client->putObject([
            'Bucket' => $this->bucket,
            'Key' => $key,
            'Body' => $content,
            'ContentType' => $contentType
        ]);
    }
}
```

---

## Packaging

### Serverless Configuration

```yaml
# serverless.yml
service: raw-php-lambda

provider:
  name: aws
  runtime: php-82
  memorySize: 256
  timeout: 10
  environment:
    AWS_REGION: us-east-1
    USERS_TABLE: !Ref UsersTable

functions:
  api:
    handler: public/index.php
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
      - httpApi:
          path: /
          method: ANY

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: users
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH

plugins:
  - ./vendor/bref/bref
```

### Deployment

```bash
# Install dependencies
composer install --no-dev

# Deploy
vendor/bin/bref deploy
```

---

## Error Handling

### Structured Error Responses

```php
function handleError(\Throwable $e): array
{
    error_log(json_encode([
        'error' => $e->getMessage(),
        'type' => get_class($e),
        'trace' => $e->getTraceAsString()
    ]));

    $statusCode = match (true) {
        $e instanceof \InvalidArgumentException => 400,
        $e instanceof \RuntimeException => 500,
        default => 500
    };

    return [
        'statusCode' => $statusCode,
        'body' => json_encode([
            'error' => $e->getMessage()
        ])
    ];
}

handler(function (array $event, $context) {
    try {
        // Process request
    } catch (\Throwable $e) {
        return handleError($e);
    }
});
```

---

## Logging

### Structured Logging

```php
function logRequest(string $level, array $data): void
{
    $logData = [
        'timestamp' => date('c'),
        'level' => $level,
        'aws_request_id' => $context->getAwsRequestId(),
        ...$data
    ];

    error_log(json_encode($logData));
}

// Usage
logRequest('info', [
    'event' => 'request_received',
    'path' => $event['path'],
    'method' => $event['httpMethod']
]);
```
