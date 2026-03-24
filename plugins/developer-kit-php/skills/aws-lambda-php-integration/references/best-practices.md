# AWS Lambda PHP Best Practices

Best practices, constraints, and security considerations for PHP Lambda development.

## Memory and Timeout Configuration

- **Memory**: Start with 512MB for Symfony, 256MB for raw PHP
- **Timeout**: Set based on expected processing time
  - Symfony: 10-30 seconds for cold start buffer
  - Raw PHP: 3-10 seconds typically sufficient

## Dependencies

Keep `composer.json` minimal:

```json
{
    "require": {
        "php": "^8.2",
        "bref/bref": "^2.0",
        "symfony/framework-bundle": "^6.0"
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist"
    }
}
```

## Error Handling

Return proper Lambda responses:

```php
try {
    $result = processRequest($event);
    return [
        'statusCode' => 200,
        'body' => json_encode($result)
    ];
} catch (ValidationException $e) {
    return [
        'statusCode' => 400,
        'body' => json_encode(['error' => $e->getMessage()])
    ];
} catch (Exception $e) {
    error_log($e->getMessage());
    return [
        'statusCode' => 500,
        'body' => json_encode(['error' => 'Internal error'])
    ];
}
```

## Logging

Use structured logging:

```php
error_log(json_encode([
    'level' => 'info',
    'message' => 'Request processed',
    'request_id' => $context->getAwsRequestId(),
    'path' => $event['path'] ?? '/'
]));
```

## Lambda Limits

- **Deployment package**: 250MB unzipped maximum (50MB zipped)
- **Memory**: 128MB to 10GB
- **Timeout**: 29 seconds (API Gateway), 15 minutes for async
- **Concurrent executions**: 1000 default

## PHP-Specific Considerations

- **Cold start**: PHP has moderate cold start; use Bref for optimized runtimes
- **Dependencies**: Keep composer.json minimal; use Lambda Layers for shared deps
- **PHP version**: Use PHP 8.2+ for best Lambda performance
- **No local storage**: Lambda containers are ephemeral; use S3/DynamoDB for persistence

## Common Pitfalls

1. **Large vendor folder** - Exclude dev dependencies; use --no-dev
2. **Session storage** - Don't use local file storage; use DynamoDB
3. **Long-running processes** - Not suitable for Lambda; use ECS instead
4. **Websockets** - Use API Gateway WebSockets or AppSync instead

## Security Considerations

- Never hardcode credentials; use IAM roles and SSM Parameter Store
- Validate all input data
- Use least privilege IAM policies
- Enable CloudTrail for audit logging
- Set proper CORS headers
