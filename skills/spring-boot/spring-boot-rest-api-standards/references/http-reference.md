# HTTP Methods and Status Codes Reference

## HTTP Methods

| Method | Idempotent | Safe | Purpose | Typical Status |
|--------|-----------|------|---------|----------------|
| GET | Yes | Yes | Retrieve resource | 200, 304, 404 |
| POST | No | No | Create resource | 201, 400, 409 |
| PUT | Yes | No | Replace resource | 200, 204, 404 |
| PATCH | No | No | Partial update | 200, 204, 400 |
| DELETE | Yes | No | Remove resource | 204, 404 |
| HEAD | Yes | Yes | Like GET, no body | 200, 304, 404 |
| OPTIONS | Yes | Yes | Describe communication options | 200 |

### Idempotent Operations
An operation is idempotent if making the same request multiple times produces the same result as making it once.

### Safe Operations
A safe operation doesn't change the state of the server. Safe operations are always idempotent.

## HTTP Status Codes

### 2xx Success
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST (include Location header)
- `202 Accepted`: Async processing accepted
- `204 No Content`: Successful DELETE or POST with no content
- `206 Partial Content`: Range request successful

### 3xx Redirection
- `301 Moved Permanently`: Resource permanently moved
- `304 Not Modified`: Cache valid, use local copy
- `307 Temporary Redirect`: Temporary redirect

### 4xx Client Errors
- `400 Bad Request`: Invalid format or parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Constraint violation or conflict
- `422 Unprocessable Entity`: Validation failed (semantic error)
- `429 Too Many Requests`: Rate limit exceeded

### 5xx Server Errors
- `500 Internal Server Error`: Unexpected server error
- `502 Bad Gateway`: External service unavailable
- `503 Service Unavailable`: Server temporarily down
- `504 Gateway Timeout`: External service timeout

## Common REST API Patterns

### Resource URLs
```
GET    /users              # List all users
GET    /users/123           # Get specific user
POST   /users              # Create user
PUT    /users/123           # Update user
DELETE /users/123           # Delete user
GET    /users/123/orders   # Get user's orders
```

### Query Parameters
```
GET /users?page=0&size=20&sort=createdAt,desc
- page: Page number (0-based)
- size: Number of items per page
- sort: Sorting format (field,direction)
```

### Response Headers
```
Location: /api/users/123           # For 201 Created responses
X-Total-Count: 45                 # Total items count
Cache-Control: no-cache           # Cache control
Content-Type: application/json     # Response format
```

## Error Response Format

```json
{
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed: name: Name cannot be blank, email: Valid email required",
  "path": "/api/users",
  "timestamp": "2024-01-15T10:30:00Z"
}
```