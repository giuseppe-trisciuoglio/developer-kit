# SpringDoc Configuration

## Basic Configuration

### application.properties

```properties
# API Documentation Path
springdoc.api-docs.path=/api-docs
springdoc.api-docs.enabled=true

# Swagger UI Configuration
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.enabled=true
springdoc.swagger-ui.operationsSorter=method
springdoc.swagger-ui.tagsSorter=alpha
springdoc.swagger-ui.tryItOutEnabled=true

# Package and Path Filtering
springdoc.packages-to-scan=com.example.controller
springdoc.paths-to-match=/api/**
```

### application.yml

```yaml
springdoc:
  api-docs:
    path: /api-docs
    enabled: true
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
    operationsSorter: method
    tagsSorter: alpha
    tryItOutEnabled: true
  packages-to-scan: com.example.controller
  paths-to-match: /api/**
```

## Access Endpoints

After configuration:
- **OpenAPI JSON**: `http://localhost:8080/v3/api-docs`
- **OpenAPI YAML**: `http://localhost:8080/v3/api-docs.yaml`
- **Swagger UI**: `http://localhost:8080/swagger-ui/index.html`

## Advanced Configuration Options

### Disable Specific Features

```properties
# Disable Swagger UI
springdoc.swagger-ui.enabled=false

# Disable API docs
springdoc.api-docs.enabled=false

# Disable try-it-out
springdoc.swagger-ui.tryItOutEnabled=false
```

### Sort Options

- **operationsSorter**: `method` (HTTP method), `alpha` (alphabetical)
- **tagsSorter**: `alpha` (alphabetical)
- **defaultModelsExpandDepth**: Controls model expansion in UI

### Filter by Package/Path

```properties
# Scan multiple packages
springdoc.packages-to-scan=com.example.controller,vendor.another.controller

# Match multiple paths
springdoc.paths-to-match=/api/**,/public/**

# Exclude paths
springdoc.paths-to-exclude=/actuator/**,/admin/**
```
