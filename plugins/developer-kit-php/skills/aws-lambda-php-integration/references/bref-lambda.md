# Bref Lambda Reference

Complete guide for deploying PHP applications on AWS Lambda using the Bref framework.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Handler Implementation](#handler-implementation)
3. [Symfony Integration](#symfony-integration)
4. [Cold Start Optimization](#cold-start-optimization)
5. [Configuration](#configuration)
6. [Deployment](#deployment)

---

## Project Setup

### Composer Configuration

```json
{
    "name": "my/symfony-lambda",
    "description": "Symfony on AWS Lambda",
    "require": {
        "php": "^8.2",
        "bref/bref": "^2.0",
        "bref/symfony-bridge": "^1.0",
        "symfony/framework-bundle": "^6.0",
        "symfony/yaml": "^6.0",
        "symfony/dotenv": "^6.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0"
    },
    "autoload": {
        "psr-4": {
            "App\\": "src/"
        }
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "allow-plugins": {
            "php-http/discovery": true
        }
    }
}
```

### Serverless Configuration

```yaml
# serverless.yml
service: symfony-lambda

provider:
  name: aws
  runtime: php-82
  memorySize: 512
  timeout: 20
  region: us-east-1

plugins:
  - ./vendor/bref/bref

functions:
  api:
    handler: public/index.php
    description: Symfony Lambda
    events:
      - httpApi: '*'

package:
  exclude:
    - node_modules/**
    - .git/**
    - tests/**
```

---

## Handler Implementation

### Basic Lambda Handler

```php
// public/index.php
use Bref\Bref;
use Bref\Context\Context;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

require __DIR__.'/../vendor/autoload.php';

Bref::initialize();

$app = require __DIR__.'/../config/bootstrap.php';

$handler = function ($event, Context $context) use ($app) {
    $request = Request::createFromGlobals();

    $response = $app->handle($request);

    return [
        'statusCode' => $response->getStatusCode(),
        'headers' => $response->headers->all(),
        'body' => $response->getContent()
    ];
};

return $handler;
```

### Symfony 6.x Integration

```php
// public/index.php
use Bref\Symfony\Bref;
use App\Kernel;
use Symfony\Component\HttpFoundation\Request;

require_once __DIR__.'/../vendor/autoload.php';

$kernel = new Kernel($_SERVER['APP_ENV'] ?? 'dev', $_SERVER['APP_DEBUG'] ?? true);
$ Bref = new Bref($kernel);

// Run the application
return $bref->getAwsHandler();
```

### Console Commands

```php
// bin/console
#!/usr/bin/env php
<?php

use App\Kernel;
use Symfony\Bundle\FrameworkBundle\Console\Application;

require_once __DIR__.'/../vendor/autoload.php';

$kernel = new Kernel($_SERVER['APP_ENV'] ?? 'dev', true);
$application = new Application($kernel);
$application->run();
```

```yaml
# serverless.yml - console function
functions:
  console:
    handler: bin/console
    timeout: 120
    events:
      - schedule: rate(1 hour)
```

---

## Symfony Integration

### Kernel Configuration

```php
// src/Kernel.php
<?php

namespace App;

use Symfony\Bundle\FrameworkBundle\Kernel\MicroKernelTrait;
use Symfony\Component\Config\Loader\LoaderInterface;
use Symfony\Component\Config\Resource\FileResource;
use Symfony\Component\DependencyInjection\ContainerBuilder;
use Symfony\Component\HttpKernel\Kernel as BaseKernel;
use Symfony\Component\Yaml\Yaml;

class Kernel extends BaseKernel
{
    use MicroKernelTrait;

    private const CONFIG_EXTS = '.{php,yaml,yml}';

    public function registerBundles(): iterable
    {
        $contents = require $this->getProjectDir().'/config/bundles.php';
        foreach ($contents as $class => $envs) {
            if ($envs[$this->environment] ?? $envs['all'] ?? false) {
                yield new $class();
            }
        }
    }

    public function getProjectDir(): string
    {
        return dirname(__DIR__);
    }

    protected function configureContainer(ContainerBuilder $container, LoaderInterface $loader): void
    {
        $container->addResource(new FileResource($this->getProjectDir().'/config/bundles.php'));
        $container->setParameter('container.dumper.inline_class_loader', true);

        $loader->load($this->getProjectDir().'/config/services.yaml');
    }

    protected function configureRoutes(RoutingConfigurator $routes): void
    {
        $routes->import('../config/routes.yaml');
    }
}
```

### Services Configuration

```yaml
# config/services.yaml
parameters:
    env(DATABASE_URL): ''
    env(AWS_REGION): 'us-east-1'

services:
    _defaults:
        autowire: true
        autoconfigure: true
        bind:
            $region: '%env(AWS_REGION)%'

    App\:
        resource: '../src/'
        exclude: '../src/{Entity,Repository}'

    App\Service\AwsService:
        arguments:
            $region: '%env(AWS_REGION)%'
```

### Routes Configuration

```yaml
# config/routes.yaml
app_home:
    path: /
    controller: App\Controller\HomeController::index

app_api_users:
    resource: '../src/Controller/UserController.php'
    type: annotation
```

---

## Cold Start Optimization

### Disable Unused Features

```yaml
# config/packages/prod/framework.yaml
framework:
    validation: false
    annotations: false
    serializer: false
    profiler: false

services:
    App\Service\HeavyService: '@App\Service\LazyHeavyService'
```

### Lazy Services

```yaml
# config/services.yaml
services:
    App\Service\LazyReportService:
        class: App\Service\ReportService
        lazy: true
```

### Optimize Composer Autoload

```json
{
    "autoload": {
        "classmap": ["src/"],
        "psr-4": {
            "App\\": "src/"
        }
    },
    "config": {
        "optimize-autoloader": true
    }
}
```

### Minimal Bundles

```php
// config/bundles.php
return [
    // Keep only essential bundles
    Symfony\Bundle\FrameworkBundle\FrameworkBundle::class => ['all' => true],
    Symfony\Bundle\MonologBundle\MonologBundle::class => ['all' => true],
];
```

---

## Configuration

### Environment Variables

```yaml
# serverless.yml
provider:
  environment:
    APP_ENV: ${self:custom.stage}
    DATABASE_URL: ${ssm:/my-app/database-url}
    AWS_REGION: ${self:provider.region}
```

### IAM Permissions

```yaml
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:Query
            - dynamodb:Scan
          Resource: 'arn:aws:dynamodb:${self:provider.region}:*:table/users'

        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
          Resource: 'arn:aws:s3:::my-bucket/*'
```

### VPC Configuration

```yaml
functions:
  api:
    vpc:
      securityGroupIds:
        - !GetAtt LambdaSecurityGroup.GroupId
      subnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

---

## Deployment

### Deploy Commands

```bash
# Install dependencies
composer install --no-dev --optimize-autoloader

# Deploy to dev
vendor/bin/bref deploy --stage dev

# Deploy to production
vendor/bin/bref deploy --stage prod
```

### Stages Configuration

```yaml
# serverless.yml
custom:
  stage: ${opt:stage, 'dev'}

  dev:
    domain: dev-api.example.com
    provisioned: 0

  prod:
    domain: api.example.com
    provisioned: 5

functions:
  api:
    handler: public/index.php
    environment:
      STAGE: ${self:custom.stage}
```

### Provisioned Concurrency

```yaml
functions:
  api:
    handler: public/index.php
    provisionedConcurrency: ${self:custom.${self:custom.stage}.provisioned}
    reservedConcurrency: 10
```

---

## Performance Tuning

### Memory Allocation

```yaml
provider:
  memorySize: 1024  # More memory = more CPU

functions:
  api:
    memorySize: 1024
    timeout: 30
```

### PHP Configuration

```yaml
provider:
  environment:
    PHP_INI_SCAN_DIR: /var/task/conf.d
```

```ini
; conf.d/lambda.ini
memory_limit = 512M
max_execution_time = 30
```

---

## Testing

See [testing-lambda.md](testing-lambda.md) for comprehensive testing patterns.

### Local Development

```bash
# Start local server
composer require bref/local-server --dev

php -S localhost:8000 -t public/
```

---

## Troubleshooting

### Common Issues

1. **Cold start too slow**: Disable unused Symfony features
2. **Memory limit exceeded**: Increase memory or optimize dependencies
3. **Timeout errors**: Increase timeout or optimize database queries
4. **Class not found**: Run `composer dump-autoload --optimize`
