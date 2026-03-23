# AWS Lambda PHP Patterns

Detailed patterns for implementing AWS Lambda with PHP and Symfony.

## Project Structure

### Symfony with Bref Structure

```
my-symfony-lambda/
├── composer.json
├── serverless.yml
├── public/
│   └── index.php         # Lambda entry point
├── src/
│   └── Kernel.php        # Symfony Kernel
├── config/
│   ├── bundles.php
│   ├── routes.yaml
│   └── services.yaml
└── templates/
```

### Raw PHP Structure

```
my-lambda-function/
├── public/
│   └── index.php         # Handler entry point
├── composer.json
├── serverless.yml
└── src/
    └── Services/
```

## Core Concepts

### Cold Start Optimization

PHP cold start depends on framework initialization. Key strategies:

1. **Lazy loading** - Defer heavy services until needed
2. **Disable unused Symfony features** - Turn off validation, annotations, etc.
3. **Optimize composer autoload** - Use classmap for production
4. **Use Bref optimized runtime** - Leverage PHP 8.x optimizations

### Connection Management

```php
// Cache AWS clients at function level
use Aws\DynamoDb\DynamoDbClient;

class DatabaseService
{
    private static ?DynamoDbClient $client = null;

    public static function getClient(): DynamoDbClient
    {
        if (self::$client === null) {
            self::$client = new DynamoDbClient([
                'region' => getenv('AWS_REGION'),
                'version' => 'latest'
            ]);
        }
        return self::$client;
    }
}
```

### Environment Configuration

```php
// config/services.yaml
parameters:
    env(DATABASE_URL): null
    env(APP_ENV): 'dev'

services:
    App\Service\Configuration:
        arguments:
            $tableName: '%env(DATABASE_URL)%'
```

## Deployment Options

### Quick Start with Serverless Framework

```yaml
# serverless.yml
service: symfony-lambda-api

provider:
  name: aws
  runtime: php-82
  memorySize: 512
  timeout: 20

package:
  individually: true
  exclude:
    - '**/node_modules/**'
    - '**/.git/**'

functions:
  api:
    handler: public/index.php
    events:
      - http:
          path: /{proxy+}
          method: ANY
      - http:
          path: /
          method: ANY
```

**Deploy with Bref:**
```bash
composer require bref/bref --dev
vendor/bin/bref deploy
```

### Symfony Full Configuration

```yaml
# serverless.yml for Symfony
service: symfony-lambda-api

provider:
  name: aws
  runtime: php-82
  stage: ${self:custom.stage}
  region: ${self:custom.region}
  environment:
    APP_ENV: ${self:custom.stage}
    APP_DEBUG: ${self:custom.isLocal}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource: '*'

functions:
  web:
    handler: public/index.php
    timeout: 30
    memorySize: 1024
    events:
      - http:
          path: /{proxy+}
          method: ANY

  console:
    handler: bin/console
    timeout: 300
    events:
      - schedule: rate(1 day)

plugins:
  - ./vendor/bref/bref

custom:
  stage: dev
  region: us-east-1
  isLocal: false
```

## Implementation Examples

**Symfony with Bref:**
```php
// public/index.php
use Bref\Symfony\Bref;
use App\Kernel;
use Symfony\Component\HttpFoundation\Request;

require __DIR__.'/../vendor/autoload.php';

$kernel = new Kernel($_SERVER['APP_ENV'] ?? 'dev', $_SERVER['APP_DEBUG'] ?? true);
$kernel->boot();

$bref = new Bref($kernel);
return $bref->run($event, $context);
```

**Raw PHP Handler:**
```php
// public/index.php
use function Bref\Lambda\main;

main(function ($event) {
    $path = $event['path'] ?? '/';
    $method = $event['httpMethod'] ?? 'GET';

    return [
        'statusCode' => 200,
        'body' => json_encode(['message' => 'Hello from PHP Lambda!'])
    ];
});
```
