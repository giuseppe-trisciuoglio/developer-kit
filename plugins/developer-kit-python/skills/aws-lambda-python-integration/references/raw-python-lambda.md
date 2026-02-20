# Raw Python Lambda

Guide for creating minimal AWS Lambda functions in Python without frameworks.

## When to Use Raw Python

- Simple handlers with minimal dependencies
- Maximum control over the execution environment
- Smallest deployment package size
- Learning Lambda fundamentals
- Custom runtime requirements

## Basic Handler

### Minimal Handler

```python
# lambda_function.py
import json

def lambda_handler(event, context):
    """
    Main entry point for Lambda function.

    Args:
        event: Event data passed to the function
        context: Lambda runtime context

    Returns:
        dict: Response object
    """
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Hello from Lambda!'})
    }
```

### Handler with Different Triggers

```python
# lambda_function.py
import json

def lambda_handler(event, context):
    """Handle different event sources."""

    # Detect event source
    if 'httpMethod' in event:
        return handle_api_gateway(event, context)
    elif 'Records' in event:
        return handle_s3_event(event, context)
    elif 'source' in event and event['source'] == 'aws.events':
        return handle_cloudwatch_event(event, context)
    else:
        return handle_direct_invoke(event, context)

def handle_api_gateway(event, context):
    """Handle API Gateway proxy integration."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': 'API Gateway request',
            'path': event.get('path'),
            'method': event.get('httpMethod')
        })
    }

def handle_s3_event(event, context):
    """Handle S3 trigger events."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"S3 event: {bucket}/{key}")

    return {'statusCode': 200, 'processed': len(event['Records'])}

def handle_cloudwatch_event(event, context):
    """Handle CloudWatch scheduled events."""
    print(f"Scheduled event: {event}")
    return {'statusCode': 200}

def handle_direct_invoke(event, context):
    """Handle direct Lambda invocation."""
    return {
        'statusCode': 200,
        'result': event
    }
```

## Cold Start Optimization

### Module-Level Caching

```python
# lambda_function.py
import boto3
import os

# Initialize at module level - persists across warm invocations
_dynamodb = None
_table = None
_s3 = None

def get_dynamodb_table():
    """Lazy initialization with caching."""
    global _dynamodb, _table
    if _table is None:
        _dynamodb = boto3.resource('dynamodb')
        _table = _dynamodb.Table(os.environ['TABLE_NAME'])
    return _table

def get_s3_client():
    """Lazy initialization with caching."""
    global _s3
    if _s3 is None:
        _s3 = boto3.client('s3')
    return _s3

def lambda_handler(event, context):
    # Uses cached clients
    table = get_dynamodb_table()
    s3 = get_s3_client()

    # Handler logic here
    return {'statusCode': 200}
```

### Lazy Loading Heavy Dependencies

```python
# lambda_function.py
_heavy_service = None

def get_heavy_service():
    """Defer loading heavy modules until needed."""
    global _heavy_service
    if _heavy_service is None:
        # Import here to avoid loading during cold start
        from heavy_library import HeavyService
        _heavy_service = HeavyService()
    return _heavy_service

def lambda_handler(event, context):
    # Only load heavy service when needed
    if event.get('needs_heavy_processing'):
        service = get_heavy_service()
        return service.process(event['data'])

    return {'statusCode': 200, 'light': True}
```

## API Gateway Integration

### REST API Handler

```python
# lambda_function.py
import json
import re

# Route definitions
ROUTES = {
    r'^GET /users$': 'list_users',
    r'^GET /users/(?P<user_id>[^/]+)$': 'get_user',
    r'^POST /users$': 'create_user',
    r'^PUT /users/(?P<user_id>[^/]+)$': 'update_user',
    r'^DELETE /users/(?P<user_id>[^/]+)$': 'delete_user',
}

def lambda_handler(event, context):
    """Main router for API Gateway requests."""
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')

    # Match route
    route_key = f"{http_method} {path}"

    for pattern, handler_name in ROUTES.items():
        match = re.match(pattern, route_key)
        if match:
            handler = globals()[handler_name]
            return handler(event, context, **match.groupdict())

    return response(404, {'error': 'Not found'})

def list_users(event, context):
    """GET /users"""
    # Implementation here
    return response(200, {'users': []})

def get_user(event, context, user_id):
    """GET /users/{user_id}"""
    return response(200, {'user_id': user_id})

def create_user(event, context):
    """POST /users"""
    body = json.loads(event.get('body', '{}'))
    return response(201, {'created': body})

def update_user(event, context, user_id):
    """PUT /users/{user_id}"""
    body = json.loads(event.get('body', '{}'))
    return response(200, {'updated': user_id, 'data': body})

def delete_user(event, context, user_id):
    """DELETE /users/{user_id}"""
    return response(200, {'deleted': user_id})

def response(status_code, body, headers=None):
    """Helper for API Gateway responses."""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    if headers:
        default_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body)
    }
```

### Request/Response Helpers

```python
# lambda_function.py
import json
from typing import Dict, Any, Optional

class APIGatewayRequest:
    """Wrapper for API Gateway events."""

    def __init__(self, event: Dict[str, Any]):
        self.event = event
        self.method = event.get('httpMethod', 'GET')
        self.path = event.get('path', '/')
        self.query_params = event.get('queryStringParameters') or {}
        self.path_params = event.get('pathParameters') or {}
        self.headers = {k.lower(): v for k, v in (event.get('headers') or {}).items()}

        body = event.get('body')
        self.body = json.loads(body) if body and event.get('isBase64Encoded') else body

    def get_header(self, name: str, default: str = None) -> Optional[str]:
        return self.headers.get(name.lower(), default)

    def get_query(self, name: str, default: str = None) -> Optional[str]:
        return self.query_params.get(name, default)

class APIGatewayResponse:
    """Builder for API Gateway responses."""

    def __init__(self):
        self.status_code = 200
        self.headers = {'Content-Type': 'application/json'}
        self.body = {}

    def status(self, code: int) -> 'APIGatewayResponse':
        self.status_code = code
        return self

    def header(self, name: str, value: str) -> 'APIGatewayResponse':
        self.headers[name] = value
        return self

    def json(self, data: Dict) -> Dict[str, Any]:
        return {
            'statusCode': self.status_code,
            'headers': self.headers,
            'body': json.dumps(data)
        }

    def text(self, text: str) -> Dict[str, Any]:
        self.headers['Content-Type'] = 'text/plain'
        return {
            'statusCode': self.status_code,
            'headers': self.headers,
            'body': text
        }

# Usage
def lambda_handler(event, context):
    request = APIGatewayRequest(event)

    if request.method == 'GET':
        return APIGatewayResponse().json({'path': request.path})

    return APIGatewayResponse().status(405).json({'error': 'Method not allowed'})
```

## Error Handling

### Structured Error Responses

```python
# lambda_function.py
import json
import traceback
from typing import Dict, Any

class LambdaError(Exception):
    """Custom error with HTTP status code."""

    def __init__(self, message: str, status_code: int = 500, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(LambdaError):
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message, 400, details)

class NotFoundError(LambdaError):
    def __init__(self, message: str):
        super().__init__(message, 404)

def error_response(error: LambdaError, request_id: str = None) -> Dict[str, Any]:
    """Format error for API Gateway response."""
    return {
        'statusCode': error.status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'error': error.__class__.__name__,
            'message': error.message,
            'details': error.details,
            'requestId': request_id
        })
    }

def lambda_handler(event, context):
    """Handler with centralized error handling."""
    try:
        return process_request(event, context)
    except LambdaError as e:
        return error_response(e, context.aws_request_id)
    except Exception as e:
        # Log full traceback for debugging
        print(f"Unhandled error: {traceback.format_exc()}")
        return error_response(
            LambdaError("Internal server error"),
            context.aws_request_id
        )

def process_request(event, context):
    """Main request processing logic."""
    user_id = event.get('pathParameters', {}).get('user_id')

    if not user_id:
        raise ValidationError("user_id is required")

    user = find_user(user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'user': user})
    }

def find_user(user_id: str) -> Dict:
    # Implementation
    return None
```

## Context Usage

### Lambda Context Object

```python
# lambda_function.py

def lambda_handler(event, context):
    """Demonstrate context object usage."""
    context_info = {
        # Identity
        'function_name': context.function_name,
        'function_version': context.function_version,
        'memory_limit_mb': context.memory_limit_in_mb,
        'aws_request_id': context.aws_request_id,
        'invoked_function_arn': context.invoked_function_arn,
        'log_group_name': context.log_group_name,
        'log_stream_name': context.log_stream_name,

        # Timing
        'remaining_time_ms': context.get_remaining_time_in_millis(),
    }

    # Check if we have enough time
    if context.get_remaining_time_in_millis() < 1000:
        print("Warning: Running low on time!")

    # Identity (for Cognito authorizer)
    if hasattr(context, 'identity'):
        context_info['identity'] = {
            'cognito_identity_id': context.identity.cognito_identity_id,
            'cognito_identity_pool_id': context.identity.cognito_identity_pool_id,
        }

    # Client context (for mobile SDK)
    if hasattr(context, 'client_context'):
        context_info['client_context'] = context.client_context

    return {
        'statusCode': 200,
        'body': json.dumps(context_info)
    }
```

## Environment Configuration

### Configuration Class

```python
# config.py
import os
from typing import List

class Config:
    """Configuration management with validation."""

    # Required environment variables
    REQUIRED = ['TABLE_NAME']

    # Optional with defaults
    DEBUG: bool = os.environ.get('DEBUG', 'false').lower() == 'true'
    REGION: str = os.environ.get('AWS_REGION', 'us-east-1')
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    TABLE_NAME: str = os.environ.get('TABLE_NAME', '')
    BUCKET_NAME: str = os.environ.get('BUCKET_NAME', '')

    # Numeric values
    TIMEOUT_SECONDS: int = int(os.environ.get('TIMEOUT_SECONDS', '30'))
    MAX_RETRIES: int = int(os.environ.get('MAX_RETRIES', '3'))

    # Lists
    ALLOWED_ORIGINS: List[str] = os.environ.get('ALLOWED_ORIGINS', '*').split(',')

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        missing = []
        for var in cls.REQUIRED:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary."""
        return {
            'DEBUG': cls.DEBUG,
            'REGION': cls.REGION,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'TABLE_NAME': cls.TABLE_NAME,
            'BUCKET_NAME': cls.BUCKET_NAME,
            'TIMEOUT_SECONDS': cls.TIMEOUT_SECONDS,
            'MAX_RETRIES': cls.MAX_RETRIES,
        }

# lambda_function.py
from config import Config

# Validate on module load
Config.validate()

def lambda_handler(event, context):
    if Config.DEBUG:
        print(f"Config: {Config.to_dict()}")

    return {'statusCode': 200, 'config': Config.to_dict()}
```

## Logging

### Structured Logging

```python
# lambda_function.py
import json
import logging
from datetime import datetime, timezone

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class StructuredLog:
    """Structured logging for CloudWatch."""

    @staticmethod
    def info(message: str, **kwargs):
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': 'INFO',
            'message': message,
            **kwargs
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def error(message: str, error: Exception = None, **kwargs):
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': 'ERROR',
            'message': message,
            **kwargs
        }
        if error:
            log_entry['error_type'] = error.__class__.__name__
            log_entry['error_message'] = str(error)

        logger.error(json.dumps(log_entry))

    @staticmethod
    def metric(name: str, value: float, unit: str = 'Count'):
        """Emit CloudWatch metric via log."""
        log_entry = {
            '_aws': {
                'Timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                'CloudWatchMetrics': [{
                    'Namespace': 'Lambda/Custom',
                    'Dimensions': [['FunctionName']],
                    'Metrics': [{'Name': name, 'Unit': unit}]
                }]
            },
            'FunctionName': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'unknown'),
            name: value
        }
        logger.info(json.dumps(log_entry))

# Usage
def lambda_handler(event, context):
    StructuredLog.info(
        'Processing request',
        request_id=context.aws_request_id,
        path=event.get('path')
    )

    try:
        result = process_event(event)
        StructuredLog.metric('SuccessCount', 1)
        return {'statusCode': 200, 'body': result}
    except Exception as e:
        StructuredLog.error('Processing failed', error=e)
        StructuredLog.metric('ErrorCount', 1)
        raise
```

## Deployment Packaging

### requirements.txt

```txt
# Minimal requirements for raw Python Lambda
boto3>=1.35.0

# Add only what you need
requests>=2.32.0  # For HTTP calls
pydantic>=2.5.0   # For data validation
```

### Build Script

```bash
#!/bin/bash
# build.sh - Build deployment package

set -e

PACKAGE_DIR="package"
OUTPUT="deployment.zip"

# Clean previous builds
rm -rf $PACKAGE_DIR $OUTPUT

# Install dependencies
pip install -r requirements.txt -t $PACKAGE_DIR

# Copy source code
cp lambda_function.py config.py $PACKAGE_DIR/

# Create zip
cd $PACKAGE_DIR
zip -r ../$OUTPUT .
cd ..

echo "Created $OUTPUT"
```

## Best Practices

1. **Keep handlers small** - Delegate to separate functions/classes
2. **Initialize outside handler** - Module-level for warm start reuse
3. **Use lazy loading** - Defer heavy imports until needed
4. **Handle timeouts** - Check `context.get_remaining_time_in_millis()`
5. **Validate input** - Always check event structure
6. **Use structured logging** - JSON for CloudWatch Insights
7. **Environment configuration** - No hardcoded values
8. **Error handling** - Graceful degradation with proper HTTP codes
