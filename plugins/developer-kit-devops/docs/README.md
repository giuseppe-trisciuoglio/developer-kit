# DevOps Plugin Documentation

Complete documentation for the Developer Kit DevOps Plugin.

## Contents

- **[Agent Guide](./guide-agents.md)** - Detailed guide for all DevOps agents

## Overview

The DevOps Plugin provides two specialized agents:

| Agent | Focus Area |
|-------|------------|
| `general-docker-expert` | Containerization and Docker configurations |
| `github-actions-pipeline-expert` | CI/CD pipelines and GitHub Actions |

## Use Cases

### Containerization Tasks

- Creating production-ready Dockerfiles
- Optimizing image size and build times
- Setting up multi-container environments with Docker Compose
- Implementing container security best practices

### CI/CD Tasks

- Building CI workflows for Java, Node.js, Python, Go applications
- Setting up multi-environment deployments (staging, production)
- Configuring OIDC authentication for cloud providers
- Creating reusable workflow templates
- Implementing Docker build pipelines with multi-platform support

## Integration

This plugin integrates with:

- **developer-kit-core**: Required dependency
- **developer-kit-aws**: For AWS deployment patterns (ECS, Lambda, S3)
- **developer-kit-java**: For Spring Boot containerization
- **developer-kit-typescript**: For Node.js/NestJS workflows

## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) - Installation and core features
- [AWS Plugin Documentation](../../developer-kit-aws/docs/) - AWS infrastructure automation
