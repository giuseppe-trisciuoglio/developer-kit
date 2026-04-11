# DevOps Plugin Agents Guide

Detailed documentation for all DevOps specialized agents.

---

## Overview

The DevOps Plugin provides two agents with deep expertise in containerization and CI/CD automation.

| Agent | Model | Tools |
|-------|-------|-------|
| `general-docker-expert` | Sonnet | Read, Write, Edit, Glob, Grep, Bash |
| `github-actions-pipeline-expert` | Sonnet | Read, Write, Edit, Glob, Grep, Bash |

---

## `general-docker-expert`

Docker containerization specialist for building, optimizing, and managing containerized applications.

### When to Use

Invoke this agent when you need to:

- Create a new Dockerfile for an application
- Optimize an existing Docker configuration
- Set up multi-container environments with Docker Compose
- Implement container security best practices
- Troubleshoot Docker build or runtime issues
- Design multi-stage build pipelines

### Key Capabilities

| Capability | Description |
|------------|-------------|
| Multi-stage builds | Optimized builds for compiled languages (Java, Go, Rust) |
| Image optimization | Size reduction using Alpine/slim images and layer caching |
| Docker Compose | Service orchestration, health checks, networking |
| Security hardening | Non-root users, minimal attack surface, vulnerability scanning |
| Stack-specific patterns | Spring Boot, Node.js, Python, Go, React/Frontend |

### Example Interactions

```
"Create a Dockerfile for my Spring Boot application"
"Optimize this Node.js image to be under 200MB"
"Set up Docker Compose with PostgreSQL and Redis for local development"
"Add health checks and non-root user to my Python Dockerfile"
```

### Output Structure

The agent provides structured responses with:

1. **Analysis**: Application requirements and constraints
2. **Recommendations**: Dockerfile patterns and best practices
3. **Implementation**: Complete, production-ready configuration
4. **Considerations**: Trade-offs, security notes, optimization tips

---

## `github-actions-pipeline-expert`

GitHub Actions CI/CD pipeline specialist for automating build, test, and deployment workflows.

### When to Use

Invoke this agent when you need to:

- Create a new GitHub Actions workflow
- Set up CI/CD for a new project
- Configure multi-environment deployments
- Implement OIDC authentication for cloud providers
- Create reusable workflows or composite actions
- Optimize pipeline performance and caching

### Key Capabilities

| Capability | Description |
|------------|-------------|
| Multi-platform deployment | AWS (ECS, Lambda, S3), GCP (Cloud Run), Azure (Container Apps) |
| OIDC authentication | Secure cloud access without long-lived credentials |
| Reusable workflows | Modular workflow_call patterns for DRY pipelines |
| Composite actions | Custom action development with caching |
| Matrix strategies | Parallel testing across versions and platforms |
| Dependency caching | Maven, npm, pip, Gradle with buildKit |

### Deployment Targets

| Platform | Services |
|----------|----------|
| **AWS** | ECS Fargate, Lambda, S3 + CloudFront, ECR |
| **GCP** | Cloud Run, GKE, Artifact Registry |
| **Azure** | Container Apps, App Service, Container Registry |
| **Kubernetes** | Generic K8s deployments, Helm charts |

### Security Patterns

- **OIDC authentication**: Preferred over static credentials
- **Minimal permissions**: Start with `contents: read`, add as needed
- **Environment protection**: Production deployments require approval
- **Secret management**: Environment-level secrets with OIDC

### Example Interactions

```
"Create a CI pipeline for my Spring Boot application"
"Set up multi-environment deployment to AWS ECS"
"Create a reusable workflow for Docker builds"
"Configure OIDC authentication for GitHub Actions to AWS"
"Build a matrix pipeline testing across Node.js 18, 20, and 22"
```

### Output Structure

The agent provides structured responses with:

1. **Analysis**: Project requirements and deployment targets
2. **Recommendations**: Workflow patterns and security considerations
3. **Implementation**: Complete, validated YAML configuration
4. **Considerations**: Trigger requirements, secret setup, troubleshooting tips

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Create or optimize Dockerfile | `general-docker-expert` |
| Docker Compose setup | `general-docker-expert` |
| Container security hardening | `general-docker-expert` |
| Create GitHub Actions workflow | `github-actions-pipeline-expert` |
| Multi-environment deployment | `github-actions-pipeline-expert` |
| Cloud deployment (AWS/GCP/Azure) | `github-actions-pipeline-expert` |
| OIDC authentication setup | `github-actions-pipeline-expert` |
| Reusable workflow templates | `github-actions-pipeline-expert` |
| Docker build in CI/CD | Both agents (Dockerfile + pipeline) |

---

## Integration Examples

### Docker + GitHub Actions Pipeline

For complete containerization workflows, use both agents:

1. **`general-docker-expert`**: Create optimized Dockerfile and Docker Compose
2. **`github-actions-pipeline-expert`**: Create CI pipeline with Docker build and push

### Language-Specific Stacks

| Language/Framework | Docker Agent Focus | CI/CD Agent Focus |
|-------------------|-------------------|-------------------|
| Java/Spring Boot | Eclipse Temurin images, JVM tuning | Maven/Gradle caching, JaCoCo |
| Node.js/NestJS | Alpine variants, multi-stage builds | npm caching, multi-version testing |
| Python/FastAPI | Slim images, Gunicorn/Uvicorn | pip caching, dependency security |
| Go | Scratch/distroless, CGO handling | GoReleaser, multi-platform builds |
| React/Frontend | Nginx serving, build caching | npm caching, Lighthouse audits |

---

## Best Practices

### Docker

- Use specific version tags, never `latest`
- Implement multi-stage builds for compiled languages
- Run as non-root user in production images
- Include health checks for production containers
- Use `.dockerignore` to minimize build context

### GitHub Actions

- Set minimal permissions at workflow level
- Prefer OIDC over long-lived credentials
- Cache dependencies consistently
- Use concurrency control to cancel outdated runs
- Implement environment protection for production

---

## See Also

- [Core Plugin - Agent Overview](../../developer-kit-core/docs/guide-agents.md) - All Developer Kit agents
- [AWS Plugin Documentation](../../developer-kit-aws/docs/) - AWS-specific DevOps patterns
- [Java Plugin Documentation](../../developer-kit-java/docs/) - Java containerization
- [TypeScript Plugin Documentation](../../developer-kit-typescript/docs/) - Node.js CI/CD
