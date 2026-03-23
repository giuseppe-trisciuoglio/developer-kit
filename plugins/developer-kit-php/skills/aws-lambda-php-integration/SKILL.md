---
name: aws-lambda-php-integration
description: Provides AWS Lambda integration patterns for PHP with Symfony using the Bref framework. Use when deploying PHP/Symfony applications to AWS Lambda, optimizing cold starts, configuring API Gateway integration, or implementing serverless PHP applications with Bref. Triggers include "create lambda php", "deploy symfony lambda", "bref lambda aws", "php lambda cold start", "aws lambda php performance", "symfony serverless", "php serverless framework".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# AWS Lambda PHP Integration

Patterns for deploying PHP and Symfony applications on AWS Lambda using the Bref framework.

## Overview

This skill provides complete patterns for AWS Lambda PHP development with two main approaches:

1. **Bref Framework** - The standard solution for PHP on Lambda with Symfony support, built-in routing, and cold start optimization
2. **Raw PHP** - Minimal overhead approach with maximum control

Both approaches support API Gateway integration with production-ready configurations.

## When to Use

Use this skill when:
- Creating new Lambda functions in PHP
- Migrating existing Symfony applications to Lambda
- Optimizing cold start performance for PHP Lambda
- Choosing between Bref-based and minimal PHP approaches
- Configuring API Gateway integration
- Setting up deployment pipelines for PHP Lambda

## Instructions

### 1. Choose Your Approach

| Approach | Cold Start | Best For | Complexity |
|----------|------------|----------|------------|
| Bref | < 2s | Symfony apps, full-featured APIs | Medium |
| Raw PHP | < 500ms | Simple handlers, maximum control | Low |

### 2. Quick Start

**Install Bref:**
```bash
composer require bref/bref
```

**Basic handler (Bref):**
```php
use Bref\Symfony\Bref;
use App\Kernel;

require __DIR__.'/../vendor/autoload.php';

$kernel = new Kernel('prod', false);
$bref = new Bref($kernel);
return $bref->run($event, $context);
```

**Basic handler (Raw PHP):**
```php
use function Bref\Lambda\main;

main(function ($event) {
    return [
        'statusCode' => 200,
        'body' => json_encode(['message' => 'Hello from PHP Lambda!'])
    ];
});
```

### 3. Deploy

```bash
# Deploy with Serverless Framework
serverless deploy

# Or use Bref CLI
vendor/bin/bref deploy
```

## Examples

For complete examples including:

1. **Create a Symfony Lambda API** - Build a REST API using Bref for a todo application
2. **Optimize Cold Start** - Reduce Symfony Lambda cold start from 5s to <2s
3. **Deploy with GitHub Actions** - Configure CI/CD pipeline for automated deployment

See [examples.md](references/examples.md) for detailed Input/Output examples and step-by-step guides.

## References

For detailed guidance on specific topics:

- **[Patterns](references/patterns.md)** - Project structure, core concepts, deployment configurations, and implementation patterns
- **[Best Practices](references/best-practices.md)** - Memory/timeout configuration, error handling, logging, security, and common pitfalls
- **[Examples](references/examples.md)** - Complete examples for creating APIs, optimizing cold starts, and CI/CD setup
- **[Bref Lambda](references/bref-lambda.md)** - Complete Bref setup, Symfony integration, and routing
- **[Raw PHP Lambda](references/raw-php-lambda.md)** - Minimal handler patterns, caching, and packaging
- **[Serverless Deployment](references/serverless-deployment.md)** - Serverless Framework, SAM, and CI/CD pipelines
- **[Testing Lambda](references/testing-lambda.md)** - PHPUnit, SAM Local, and integration testing

## Version

Version: 1.0.0
