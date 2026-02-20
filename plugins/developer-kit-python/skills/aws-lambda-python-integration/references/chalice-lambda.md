# AWS Chalice Lambda Framework

Complete guide for building AWS Lambda functions with the AWS Chalice framework.

## What is Chalice?

AWS Chalice is a Python serverless microframework that lets you quickly create and deploy applications that use AWS Lambda. It provides:

- Decorator-based routing (similar to Flask)
- Automatic IAM policy generation
- Local development server
- Built-in CORS support
- Easy deployment to API Gateway

## Installation

```bash
# Install Chalice
pip install chalice

# Verify installation
chalice --version

# Create new project
chalice new-project my-api
cd my-api
```

## Basic Structure

### Project Layout

```
my-chalice-project/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .chalice/
│   ├── config.json       # Stage configuration
│   └── deploy/           # Deployment artifacts (auto-generated)
├── chalicelib/           # Additional Python modules
│   ├── __init__.py
│   └── services.py
└── tests/
    └── test_app.py
```

### Minimal Application

```python
# app.py
from chalice import Chalice

app = Chalice(app_name='hello-world')

@app.route('/')
def index():
    return {'hello': 'world'}
```

## Routing

### HTTP Methods

```python
from chalice import Chalice

app = Chalice(app_name='my-api')

@app.route('/users', methods=['GET'])
def list_users():
    return {'users': []}

@app.route('/users', methods=['POST'])
def create_user():
    user = app.current_request.json_body
    return {'user': user, 'created': True}

@app.route('/users/{user_id}', methods=['GET'])
def get_user(user_id):
    return {'user_id': user_id}

@app.route('/users/{user_id}', methods=['PUT'])
def update_user(user_id):
    updates = app.current_request.json_body
    return {'user_id': user_id, 'updated': updates}

@app.route('/users/{user_id}', methods=['DELETE'])
def delete_user(user_id):
    return {'user_id': user_id, 'deleted': True}
```

### Path Parameters

```python
@app.route('/orders/{order_id}/items/{item_id}')
def get_order_item(order_id, item_id):
    return {
        'order_id': order_id,
        'item_id': item_id
    }
```

### Query Parameters

```python
from urllib.parse import parse_qs

@app.route('/search')
def search():
    # Access query parameters
    query_params = app.current_request.query_params or {}

    search_term = query_params.get('q')
    page = int(query_params.get('page', 1))
    limit = int(query_params.get('limit', 10))

    return {
        'search_term': search_term,
        'page': page,
        'limit': limit
    }
```

## Request Handling

### Accessing Request Data

```python
@app.route('/data', methods=['POST'])
def process_data():
    request = app.current_request

    # Request properties
    return {
        'method': request.method,           # POST
        'path': request.path,               # /data
        'query_params': request.query_params,
        'headers': dict(request.headers),
        'json_body': request.json_body,     # Parsed JSON body
        'raw_body': request.raw_body,       # Raw bytes
        'context': request.context,         # Lambda context
        'stage_vars': request.stage_vars,   # API Gateway stage variables
    }
```

### Custom Responses

```python
from chalice import Response
import json

@app.route('/custom-response')
def custom_response():
    return Response(
        body=json.dumps({'message': 'Custom response'}),
        status_code=201,
        headers={
            'Content-Type': 'application/json',
            'X-Custom-Header': 'value'
        }
    )

@app.route('/binary-data')
def binary_data():
    return Response(
        body=b'binary content',
        status_code=200,
        headers={'Content-Type': 'application/octet-stream'}
    )
```

## CORS Configuration

### Global CORS

```python
from chalice import Chalice, CORSConfig

# Global CORS configuration
cors_config = CORSConfig(
    allow_origin='https://example.com',
    allow_headers=['Content-Type', 'Authorization'],
    allow_credentials=True,
    max_age=600
)

app = Chalice(app_name='my-api')
app.api.cors_config = cors_config
```

### Per-Route CORS

```python
from chalice import CORSConfig

# Simple CORS
@app.route('/public', cors=True)
def public_endpoint():
    return {'data': 'public'}

# Custom CORS per route
custom_cors = CORSConfig(
    allow_origin='https://specific-domain.com',
    allow_headers=['X-Custom-Header']
)

@app.route('/restricted', cors=custom_cors)
def restricted_endpoint():
    return {'data': 'restricted'}
```

## Error Handling

### Built-in Errors

```python
from chalice import (
    Chalice,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    ChaliceViewError
)

app = Chalice(app_name='my-api')

@app.route('/users/{user_id}')
def get_user(user_id):
    user = find_user(user_id)
    if user is None:
        raise NotFoundError(f'User {user_id} not found')
    return user

@app.route('/users', methods=['POST'])
def create_user():
    data = app.current_request.json_body

    if not data or 'email' not in data:
        raise BadRequestError('Email is required')

    if user_exists(data['email']):
        raise ConflictError('User already exists')

    return create_new_user(data)
```

### Custom Error Handler

```python
from chalice import ChaliceViewError

@app.errorhandler(ChaliceViewError)
def handle_errors(error):
    return Response(
        body=json.dumps({
            'error': error.__class__.__name__,
            'message': str(error)
        }),
        status_code=error.STATUS_CODE if hasattr(error, 'STATUS_CODE') else 500,
        headers={'Content-Type': 'application/json'}
    )
```

## AWS Service Integration

### DynamoDB

```python
import boto3
from botocore.exceptions import ClientError

# Initialize at module level for connection reuse
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

@app.route('/items/{item_id}')
def get_item(item_id):
    try:
        response = table.get_item(Key={'id': item_id})
        item = response.get('Item')

        if not item:
            raise NotFoundError(f'Item {item_id} not found')

        return item
    except ClientError as e:
        app.log.error(f"DynamoDB error: {e}")
        raise ChaliceViewError('Database error')

@app.route('/items', methods=['POST'])
def create_item():
    item = app.current_request.json_body

    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        app.log.error(f"DynamoDB error: {e}")
        raise ChaliceViewError('Failed to create item')
```

### S3

```python
import boto3
import json

s3 = boto3.client('s3')
BUCKET_NAME = 'my-bucket'

@app.route('/files/{key}')
def get_file(key):
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content = response['Body'].read()
        return Response(
            body=content,
            status_code=200,
            headers={'Content-Type': response['ContentType']}
        )
    except s3.exceptions.NoSuchKey:
        raise NotFoundError(f'File {key} not found')

@app.route('/files', methods=['POST'])
def upload_file():
    request = app.current_request
    key = request.query_params.get('key')

    if not key:
        raise BadRequestError('Key parameter required')

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=request.raw_body,
        ContentType=request.headers.get('content-type', 'application/octet-stream')
    )

    return {'key': key, 'uploaded': True}
```

### SQS

```python
import boto3
import json

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/my-queue'

@app.route('/messages', methods=['POST'])
def enqueue_message():
    message = app.current_request.json_body

    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message),
        MessageAttributes={
            'Type': {
                'StringValue': message.get('type', 'default'),
                'DataType': 'String'
            }
        }
    )

    return {
        'message_id': response['MessageId'],
        'status': 'queued'
    }
```

## Configuration

### config.json

```json
{
  "version": "2.0",
  "app_name": "my-api",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "DEBUG": "true",
        "TABLE_NAME": "dev-table"
      },
      "lambda_functions": {
        "api_handler": {
          "lambda_timeout": 10,
          "lambda_memory_size": 256
        }
      },
      "tags": {
        "Environment": "dev",
        "Project": "my-api"
      }
    },
    "prod": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "DEBUG": "false",
        "TABLE_NAME": "prod-table"
      },
      "lambda_functions": {
        "api_handler": {
          "lambda_timeout": 30,
          "lambda_memory_size": 512,
          "reserved_concurrent_executions": 100
        }
      },
      "tags": {
        "Environment": "prod",
        "Project": "my-api"
      }
    }
  }
}
```

### Environment Variables

```python
import os

# Access environment variables
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
TABLE_NAME = os.environ.get('TABLE_NAME', 'default-table')
SECRET_KEY = os.environ.get('SECRET_KEY')

@app.route('/config')
def get_config():
    return {
        'debug': DEBUG,
        'table_name': TABLE_NAME,
        'has_secret': SECRET_KEY is not None
    }
```

## Local Development

### Local Server

```bash
# Start local development server
chalice local

# With specific port
chalice local --port 8080

# With stage configuration
chalice local --stage dev
```

### Testing Endpoints

```bash
# Test local endpoints
curl http://localhost:8000/
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'
```

## Deployment

### Deploy to AWS

```bash
# Deploy to default stage (dev)
chalice deploy

# Deploy to specific stage
chalice deploy --stage prod

# Get deployment info
chalice url --stage dev
chalice logs --stage dev
```

### Generate CloudFormation Template

```bash
# Generate SAM/CloudFormation template
chalice package --stage prod ./out

# Output:
# ./out/sam.json          # CloudFormation template
# ./out/deployment.zip    # Lambda deployment package
```

## Advanced Features

### Request Middleware

```python
from chalice import Chalice

app = Chalice(app_name='my-api')

@app.middleware('http')
def auth_middleware(event, get_response):
    # Run before handler
    auth_header = event.headers.get('Authorization')

    if not auth_header and event.path != '/':
        return Response(
            body=json.dumps({'error': 'Unauthorized'}),
            status_code=401
        )

    # Call the actual handler
    response = get_response(event)

    # Run after handler
    response.headers['X-Request-ID'] = event.request_context['requestId']

    return response
```

### Scheduled Events

```python
from chalice import Chalice, Cron

app = Chalice(app_name='scheduled-tasks')

@app.schedule(Cron(0, 12, '*', '*', '?', '*'))
def daily_report(event):
    """Run every day at 12:00 PM UTC"""
    app.log.info("Running daily report")
    generate_daily_report()
    return {'status': 'completed'}

@app.schedule('rate(1 hour)')
def hourly_cleanup(event):
    """Run every hour"""
    app.log.info("Running hourly cleanup")
    cleanup_old_data()
    return {'status': 'completed'}
```

### S3 Event Handlers

```python
@app.on_s3_event(bucket='my-bucket', events=['s3:ObjectCreated:*'])
def handle_s3_upload(event):
    app.log.info(f"File uploaded: {event.key}")
    process_file(event.bucket, event.key)
    return {'status': 'processed'}
```

### SNS Event Handlers

```python
@app.on_sns_message(topic='my-topic')
def handle_sns_message(event):
    app.log.info(f"Received SNS message: {event.subject}")
    app.log.info(f"Message body: {event.message}")
    process_notification(event.message)
    return {'status': 'processed'}
```

### SQS Event Handlers

```python
@app.on_sqs_message(queue='my-queue', batch_size=10)
def handle_sqs_message(event):
    for record in event:
        app.log.info(f"Processing message: {record.body}")
        process_message(record.body)
    return {'status': 'processed'}
```

## Best Practices

1. **Initialize AWS clients at module level** for connection reuse across warm invocations
2. **Use `chalicelib/` for additional modules** to keep `app.py` clean
3. **Configure CORS properly** for browser-based clients
4. **Use environment variables** for configuration, not hardcoded values
5. **Handle exceptions** with Chalice error classes for proper HTTP responses
6. **Log with `app.log`** for CloudWatch integration
7. **Use `chalice package`** for CI/CD pipelines
8. **Set appropriate timeouts and memory** for your workload

## Common Patterns

### CRUD Service Pattern

```python
# chalicelib/users_service.py
import boto3
from botocore.exceptions import ClientError
from chalice import NotFoundError, BadRequestError

class UsersService:
    def __init__(self, table_name):
        self.table = boto3.resource('dynamodb').Table(table_name)

    def get_user(self, user_id):
        response = self.table.get_item(Key={'id': user_id})
        user = response.get('Item')
        if not user:
            raise NotFoundError(f'User {user_id} not found')
        return user

    def create_user(self, user_data):
        if 'id' not in user_data:
            raise BadRequestError('id is required')
        self.table.put_item(Item=user_data)
        return user_data

# app.py
from chalicelib.users_service import UsersService

users_service = UsersService(os.environ.get('TABLE_NAME'))

@app.route('/users/{user_id}')
def get_user(user_id):
    return users_service.get_user(user_id)

@app.route('/users', methods=['POST'])
def create_user():
    return users_service.create_user(app.current_request.json_body)
```

### Pagination Pattern

```python
@app.route('/users')
def list_users():
    query_params = app.current_request.query_params or {}

    limit = int(query_params.get('limit', 20))
    cursor = query_params.get('cursor')

    kwargs = {'Limit': limit}
    if cursor:
        kwargs['ExclusiveStartKey'] = {'id': cursor}

    response = table.scan(**kwargs)

    result = {
        'users': response.get('Items', []),
        'count': response.get('Count', 0)
    }

    if 'LastEvaluatedKey' in response:
        result['next_cursor'] = response['LastEvaluatedKey']['id']

    return result
```
