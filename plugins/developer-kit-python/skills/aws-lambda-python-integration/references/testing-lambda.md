# Testing Python Lambda Functions

Testing strategies for Python Lambda functions including unit tests, integration tests, and local emulation.

## Testing Tools

```txt
# requirements-dev.txt
pytest>=8.0.0
pytest-cov>=5.0.0
pytest-asyncio>=0.23.0
moto>=5.0.0  # AWS service mocking - uses mock_aws decorator
responses>=0.25.0  # HTTP mocking
factory-boy>=3.3.0  # Test data generation
freezegun>=1.5.0  # Time mocking
```

## Unit Testing

### Basic Test Structure

```python
# tests/test_lambda_function.py
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from lambda_function import lambda_handler, get_user, create_user

class TestLambdaHandler:
    """Test suite for Lambda handler."""

    @pytest.fixture
    def lambda_context(self):
        """Create a mock Lambda context."""
        context = Mock()
        context.function_name = 'test-function'
        context.memory_limit_in_mb = 256
        context.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789:function:test-function'
        context.aws_request_id = 'test-request-id'
        context.get_remaining_time_in_millis.return_value = 5000
        return context

    @pytest.fixture
    def api_gateway_event(self):
        """Create a sample API Gateway event."""
        return {
            'httpMethod': 'GET',
            'path': '/users/123',
            'pathParameters': {'user_id': '123'},
            'queryStringParameters': None,
            'headers': {'Content-Type': 'application/json'},
            'body': None,
            'requestContext': {
                'requestId': 'test-request-id',
                'identity': {'sourceIp': '127.0.0.1'}
            }
        }

    def test_lambda_handler_get_user(self, api_gateway_event, lambda_context):
        """Test GET /users/{id} endpoint."""
        with patch('lambda_function.get_table') as mock_get_table:
            mock_table = Mock()
            mock_table.get_item.return_value = {'Item': {'id': '123', 'name': 'Test User'}}
            mock_get_table.return_value = mock_table

            response = lambda_handler(api_gateway_event, lambda_context)

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['id'] == '123'
            assert body['name'] == 'Test User'

    def test_lambda_handler_user_not_found(self, api_gateway_event, lambda_context):
        """Test 404 response when user not found."""
        with patch('lambda_function.get_table') as mock_get_table:
            mock_table = Mock()
            mock_table.get_item.return_value = {}
            mock_get_table.return_value = mock_table

            response = lambda_handler(api_gateway_event, lambda_context)

            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert 'error' in body
```

### Testing with Fixtures

```python
# tests/conftest.py
import pytest
import json
from unittest.mock import Mock

@pytest.fixture
def mock_context():
    """Standard mock Lambda context."""
    context = Mock()
    context.function_name = 'test-function'
    context.memory_limit_in_mb = 256
    context.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789:function:test'
    context.aws_request_id = 'test-request-id'
    context.get_remaining_time_in_millis.return_value = 30000
    return context

@pytest.fixture
def mock_api_event():
    """Factory for API Gateway events."""
    def _make_event(
        method='GET',
        path='/',
        path_params=None,
        query_params=None,
        body=None,
        headers=None
    ):
        event = {
            'httpMethod': method,
            'path': path,
            'pathParameters': path_params or {},
            'queryStringParameters': query_params or {},
            'headers': headers or {'Content-Type': 'application/json'},
            'body': json.dumps(body) if body else None,
            'requestContext': {'requestId': 'test-id'}
        }
        return event
    return _make_event

@pytest.fixture
def mock_dynamodb_item():
    """Factory for DynamoDB items."""
    def _make_item(user_id='123', name='Test', email='test@example.com'):
        return {
            'id': user_id,
            'name': name,
            'email': email,
            'created_at': '2024-01-01T00:00:00Z'
        }
    return _make_item
```

## Moto: AWS Service Mocking

### DynamoDB Testing

```python
# tests/test_with_moto.py
import pytest
import boto3
from moto import mock_aws
import json

from lambda_function import lambda_handler

@pytest.fixture
def dynamodb_table():
    """Create mock DynamoDB table."""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName='test-users',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()

        # Seed with test data
        table.put_item(Item={'id': '123', 'name': 'Test User', 'email': 'test@example.com'})

        yield table

def test_get_user_with_moto(dynamodb_table, mock_context):
    """Test using mocked DynamoDB."""
    from lambda_function import get_table

    # Override the table in lambda_function
    import lambda_function
    lambda_function._table = dynamodb_table

    event = {
        'httpMethod': 'GET',
        'path': '/users/123',
        'pathParameters': {'user_id': '123'}
    }

    response = lambda_handler(event, mock_context)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['name'] == 'Test User'

@mock_aws
def test_create_user():
    """Test using decorator style."""
    # Setup
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-users',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Test
    from lambda_function import create_user
    import lambda_function
    lambda_function._table = table

    result = create_user({'id': '456', 'name': 'New User'})

    # Verify
    response = table.get_item(Key={'id': '456'})
    assert response['Item']['name'] == 'New User'
```

### S3 Testing

```python
# tests/test_s3_operations.py
import pytest
import boto3
from moto import mock_aws
import json

@mock_aws
def test_s3_upload_and_retrieve():
    """Test S3 operations."""
    # Setup
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'test-bucket'
    s3.create_bucket(Bucket=bucket_name)

    # Test upload
    s3.put_object(
        Bucket=bucket_name,
        Key='test-file.json',
        Body=json.dumps({'key': 'value'})
    )

    # Test retrieve
    response = s3.get_object(Bucket=bucket_name, Key='test-file.json')
    content = json.loads(response['Body'].read())

    assert content['key'] == 'value'

@mock_aws
def test_lambda_s3_trigger():
    """Test Lambda triggered by S3 event."""
    from lambda_function import lambda_handler

    s3_event = {
        'Records': [{
            'eventVersion': '2.1',
            'eventSource': 'aws:s3',
            'awsRegion': 'us-east-1',
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'uploads/file.txt'}
            }
        }]
    }

    context = Mock()
    response = lambda_handler(s3_event, context)

    assert response['statusCode'] == 200
```

### SQS Testing

```python
# tests/test_sqs.py
import pytest
import boto3
from moto import mock_aws
import json

@mock_aws
def test_sqs_send_and_receive():
    """Test SQS operations."""
    sqs = boto3.client('sqs', region_name='us-east-1')

    # Create queue
    queue = sqs.create_queue(QueueName='test-queue')
    queue_url = queue['QueueUrl']

    # Send message
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({'task': 'process_data'})
    )

    # Receive message
    messages = sqs.receive_message(QueueUrl=queue_url)
    body = json.loads(messages['Messages'][0]['Body'])

    assert body['task'] == 'process_data'
```

## Testing AWS Chalice

### Chalice Test Client

```python
# tests/test_chalice_app.py
import pytest
import json
from chalice.test import Client
from moto import mock_aws
import boto3

from app import app

@pytest.fixture
def client():
    """Create Chalice test client."""
    with Client(app) as client:
        yield client

@mock_aws
def test_index_endpoint(client):
    """Test GET / endpoint."""
    response = client.http.get('/')

    assert response.status_code == 200
    assert response.json_body == {'message': 'Hello from Chalice!'}

@mock_aws
def test_create_user(client):
    """Test POST /users endpoint."""
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='users',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()

    response = client.http.post(
        '/users',
        body=json.dumps({'id': '123', 'name': 'Test User'}),
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 201
    assert 'id' in response.json_body

def test_404_response(client):
    """Test 404 handling."""
    response = client.http.get('/nonexistent')

    assert response.status_code == 404
```

### Testing Chalice Events

```python
# tests/test_chalice_events.py
import pytest
from chalice.test import Client
from app import app

@pytest.fixture
def client():
    with Client(app) as client:
        yield client

def test_s3_event_handler(client):
    """Test S3 event handler."""
    event = client.events.generate_s3_event(
        bucket='my-bucket',
        key='uploads/file.txt'
    )

    response = client.lambda_.invoke(
        'handle_s3_upload',
        event
    )

    assert response.payload == {'status': 'processed'}

def test_scheduled_event(client):
    """Test CloudWatch scheduled event."""
    event = client.events.generate_cw_event(
        source='aws.events',
        detail_type='Scheduled Event'
    )

    response = client.lambda_.invoke('daily_report', event)

    assert response.payload['status'] == 'completed'

def test_sns_event(client):
    """Test SNS event handler."""
    event = client.events.generate_sns_event(
        message=json.dumps({'notification': 'test'}),
        subject='Test Subject'
    )

    response = client.lambda_.invoke('handle_sns_message', event)

    assert response.payload['status'] == 'processed'
```

## Local Testing

### SAM Local

```bash
# Install SAM CLI
pip install aws-sam-cli

# Build the application
sam build

# Start local API
sam local start-api

# Invoke function locally
sam local invoke ApiFunction -e events/api-get.json

# Invoke with environment variables
sam local invoke ApiFunction \
  -e events/api-get.json \
  --env-vars env.json
```

### Serverless Offline

```bash
# Install plugin
npm install serverless-offline

# Start offline server
serverless offline

# With specific port
serverless offline --httpPort 3000

# Invoke function
serverless invoke local -f api -p event.json
```

### LocalStack

```yaml
# docker-compose.yml
version: '3.8'
services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=lambda,s3,dynamodb,apigateway,sqs
      - DEBUG=1
      - LAMBDA_EXECUTOR=docker
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
```

```python
# tests/test_with_localstack.py
import pytest
import boto3
import requests
import json

LOCALSTACK_ENDPOINT = 'http://localhost:4566'

@pytest.fixture(scope='module')
def aws_clients():
    """Create AWS clients pointing to LocalStack."""
    return {
        'lambda': boto3.client(
            'lambda',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        ),
        'dynamodb': boto3.resource(
            'dynamodb',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        ),
        'apigateway': boto3.client(
            'apigateway',
            endpoint_url=LOCALSTACK_ENDPOINT,
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    }

def test_deploy_and_invoke(aws_clients):
    """Deploy Lambda and invoke via API Gateway."""
    # This would deploy the Lambda and test end-to-end
    pass
```

## Integration Testing

### Full Stack Test

```python
# tests/integration/test_api_integration.py
import pytest
import requests
import os

# Skip if no deployment
pytestmark = pytest.mark.skipif(
    not os.getenv('API_ENDPOINT'),
    reason='API_ENDPOINT not set'
)

@pytest.fixture
def api_endpoint():
    return os.getenv('API_ENDPOINT')

@pytest.fixture
def api_key():
    return os.getenv('API_KEY')

def test_health_check(api_endpoint):
    """Test health endpoint."""
    response = requests.get(f"{api_endpoint}/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_create_and_get_user(api_endpoint, api_key):
    """Test full CRUD flow."""
    headers = {'X-Api-Key': api_key}

    # Create user
    create_response = requests.post(
        f"{api_endpoint}/users",
        json={'name': 'Integration Test', 'email': 'test@example.com'},
        headers=headers
    )
    assert create_response.status_code == 201
    user_id = create_response.json()['id']

    # Get user
    get_response = requests.get(
        f"{api_endpoint}/users/{user_id}",
        headers=headers
    )
    assert get_response.status_code == 200
    assert get_response.json()['name'] == 'Integration Test'

    # Cleanup
    requests.delete(f"{api_endpoint}/users/{user_id}", headers=headers)
```

## Code Coverage

```bash
# Run tests with coverage
pytest --cov=lambda_function --cov-report=term-missing

# Generate HTML report
pytest --cov=lambda_function --cov-report=html

# Generate XML report for CI
pytest --cov=lambda_function --cov-report=xml

# Fail if coverage below threshold
pytest --cov=lambda_function --cov-fail-under=80
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = .
omit =
    */tests/*
    */venv/*
    */.venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

## Testing Best Practices

1. **Use fixtures** - For common setup and teardown
2. **Mock external services** - Use moto for AWS services
3. **Test error paths** - Not just happy paths
4. **Use parameterized tests** - For multiple test cases
5. **Keep tests fast** - Unit tests should run in milliseconds
6. **Test in isolation** - Each test should be independent
7. **Use factories** - For test data generation
8. **Clean up resources** - Even in tests
