# AWS SDK for Java 2.x Developer Guide

## Overview

The AWS SDK for Java 2.x provides a modern, type-safe API for AWS services. Built on Java 8+, it offers improved performance, better error handling, and enhanced security compared to v1.x.

## Key Features

- **Modern Architecture**: Built on Java 8+ with reactive and async support
- **Type Safety**: Comprehensive type annotations and validation
- **Performance Optimized**: Connection pooling, async support, and SSL optimization
- **Enhanced Security**: Better credential management and security practices
- **Extensive Coverage**: Support for all AWS services with regular updates

## Core Concepts

### Service Clients
The primary interface for interacting with AWS services. All clients implement the `SdkClient` interface.

```java
// S3Client example
S3Client s3 = S3Client.builder().region(Region.US_EAST_1).build();
```

### Client Configuration
Configure behavior through builders supporting:
- Timeout settings
- HTTP client selection
- Authentication methods
- Monitoring and metrics

### Credential Providers
Multiple authentication methods:
- Environment variables
- System properties
- Shared credential files
- IAM roles
- SSO integration

### HTTP Clients
Choose from three HTTP implementations:
- Apache HttpClient (synchronous)
- Netty NIO Client (asynchronous)
- URL Connection Client (lightweight)

## Migration from v1.x

The SDK 2.x is not backward compatible with v1.x. Key changes:
- Builder pattern for client creation
- Different package structure
- Enhanced error handling
- New credential system
- Improved resource management

## Getting Started

Include the BOM (Bill of Materials) for version management:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>bom</artifactId>
            <version>2.25.0</version> // Use latest stable version
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

Add service-specific dependencies:

```xml
<dependencies>
    <!-- S3 Service -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>s3</artifactId>
    </dependency>

    <!-- Core SDK -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>sdk-core</artifactId>
    </dependency>
</dependencies>
```

## Architecture Overview

```
AWS Service Client
├── Configuration Layer
│   ├── Client Override Configuration
│   └── HTTP Client Configuration
├── Authentication Layer
│   ├── Credential Providers
│   └── Security Context
├── Transport Layer
│   ├── HTTP Client (Apache/Netty/URLConn)
│   └── Connection Pool
└── Protocol Layer
    ├── Service Protocol Implementation
    └── Error Handling
```

## Service Discovery

The SDK automatically discovers and registers all available AWS services through service interfaces and paginators.

### Available Services

All AWS services are available through dedicated client interfaces:
- S3 (Simple Storage Service)
- DynamoDB (NoSQL Database)
- Lambda (Serverless Functions)
- EC2 (Compute Cloud)
- RDS (Managed Databases)
- And 200+ other services

For a complete list, see the AWS Service documentation.

## Support and Community

- **GitHub Issues**: Report bugs and request features
- **AWS Amplify**: For mobile app developers
- **Migration Guide**: Available for v1.x users
- **Changelog**: Track changes on GitHub