# Developer Kit DevOps Plugin

DevOps expertise for containerization and CI/CD pipeline automation.

## Overview

The `developer-kit-devops` plugin provides specialized agents for Docker containerization and GitHub Actions CI/CD pipeline development. It enables production-ready container configurations and secure, efficient deployment workflows.

## Agents

| Agent | Purpose |
|-------|---------|
| `general-docker-expert` | Docker containerization, multi-stage builds, Docker Compose |
| `github-actions-pipeline-expert` | GitHub Actions workflows, multi-platform deployments, reusable workflows |

## Quick Start

### Docker Containerization

Invoke the Docker expert when you need:
- Production-ready Dockerfiles
- Multi-stage build optimization
- Docker Compose configurations
- Container security hardening

```bash
# Example: Ask Claude to create a Dockerfile for your application
# Claude will automatically invoke the docker expert when relevant
```

### CI/CD Pipeline

Invoke the GitHub Actions expert when you need:
- Workflow creation and optimization
- Multi-environment deployments (AWS, GCP, Azure)
- OIDC authentication setup
- Reusable workflows and composite actions

## Key Capabilities

### Docker Expertise

- **Multi-stage builds** for compiled languages (Java, Go, Rust, Node.js)
- **Image optimization** with Alpine/slim base images
- **Layer caching** strategies for faster builds
- **Health checks** and monitoring configurations
- **Non-root security** hardening
- **Docker Compose** orchestration patterns

### GitHub Actions Expertise

- **OIDC authentication** for AWS, GCP, Azure
- **Multi-platform deployment** patterns (ECS, Lambda, Cloud Run, Azure Container Apps)
- **Matrix strategies** for parallel testing
- **Reusable workflows** and composite actions
- **Dependency caching** for Maven, npm, pip, Gradle
- **Docker buildx** with multi-platform support
- **Environment protection** and approval gates

## Plugin Structure

```
developer-kit-devops/
├── agents/
│   ├── general-docker-expert.md
│   └── github-actions-pipeline-expert.md
└── docs/
    ├── README.md
    └── guide-agents.md
```

## Requirements

- `developer-kit-core` (required dependency)

## Documentation

- [Agent Guide](./docs/guide-agents.md) - Detailed agent capabilities and usage
- [Developer Kit Core](../developer-kit-core/docs/) - Core plugin and installation guides
- [AWS Plugin](../developer-kit-aws/docs/) - AWS CloudFormation and infrastructure

## Version

Current version: **2.8.0**
