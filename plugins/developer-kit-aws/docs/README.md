# Developer Kit AWS Plugin Documentation

Welcome to the Developer Kit AWS Plugin documentation. This plugin provides comprehensive tools for AWS cloud architecture, CloudFormation infrastructure as code, and DevOps automation.

---

## Available Documentation

### Skills Guides

- **[CloudFormation Skills](./guide-skills-cloudformation.md)** - AWS CloudFormation IaC skills (15 skills)
- **[AWS SAM Bootstrap](./guide-skills-aws-sam.md)** - AWS SAM project bootstrap and migration patterns
- **[AWS Cost Optimization](./guide-skills-cost-optimization.md)** - AWS cost optimization strategies
- **[AWS CLI Guide](./guide-skills-aws-cli.md)** - Advanced AWS CLI operations and automation
- **[AWS Architecture Diagrams](./guide-skills-drawio.md)** - Professional AWS diagrams in draw.io format

### Component Guides

- **[Agent Guide](./guide-agents.md)** - AWS specialized agents

---

## About AWS Plugin

The Developer Kit AWS Plugin provides:

- **AWS Agents**: 3 specialized agents for AWS architecture, CloudFormation, and DevOps
- **AWS Skills**: 19 skills covering AWS CloudFormation templates, AWS SAM bootstrap, architecture diagrams, and cost optimization

### General AWS Skills

- **AWS SAM Bootstrap**: AWS Serverless Application Model (SAM) bootstrap patterns for new and existing projects
  - Supports `sam init`, migration from existing Lambda/CloudFormation, and `samconfig.toml` configuration
  - Includes reference templates for common serverless patterns
- **AWS CLI Beast Mode**: Advanced AWS CLI patterns for power users
  - Bulk operations, JMESPath querying, waiters and polling, security-first patterns
  - Helper scripts: `aws-blast.sh` (30+ aliases) and `jmespath-templates.json`
- **AWS Architecture Diagrams**: Professional AWS architecture diagram creation in draw.io format
  - AWS shape reference and architecture templates included
- **AWS Cost Optimization**: Structured cost optimization guidance
  - Five pillars: Right-Sizing, Elasticity, Pricing Models, Storage, Monitoring
  - Twelve actionable best practices with AWS native tool references

---

## Plugin Structure

```
developer-kit-aws/
├── .claude-plugin/plugin.json   # Plugin manifest
├── agents/                      # AWS architecture and DevOps agents (3)
├── skills/
│   ├── aws-cloudformation/     # CloudFormation template skills (15)
│   │   ├── aws-cloudformation-vpc/
│   │   ├── aws-cloudformation-ec2/
│   │   ├── aws-cloudformation-lambda/
│   │   ├── aws-cloudformation-iam/
│   │   ├── aws-cloudformation-s3/
│   │   ├── aws-cloudformation-rds/
│   │   ├── aws-cloudformation-dynamodb/
│   │   ├── aws-cloudformation-ecs/
│   │   ├── aws-cloudformation-auto-scaling/
│   │   ├── aws-cloudformation-cloudwatch/
│   │   ├── aws-cloudformation-cloudfront/
│   │   ├── aws-cloudformation-security/
│   │   ├── aws-cloudformation-elasticache/
│   │   ├── aws-cloudformation-bedrock/
│   │   └── aws-cloudformation-task-ecs-deploy-gh/
│   └── aws/                    # General AWS skills (4)
│       ├── aws-cli-beast/
│       ├── aws-sam-bootstrap/
│       ├── aws-drawio-architecture-diagrams/
│       └── aws-cost-optimization/
└── docs/                       # This documentation
```

---

## Quick Start

1. **Explore available agents**: See [Agent Guide](./guide-agents.md)
2. **Learn CloudFormation patterns**: See [CloudFormation Skills](./guide-skills-cloudformation.md)
3. **Design AWS architecture**: Use `aws-solution-architect-expert` agent
4. **Create IaC templates**: Use `aws-cloudformation-devops-expert` agent
5. **Optimize costs**: Use the [Cost Optimization Guide](./guide-skills-cost-optimization.md)

---

## Key Features

### AWS Architecture Design
- Solution architecture design
- Well-Architected Framework application
- Multi-region and high availability design
- Serverless architecture patterns
- Cloud migration planning

### CloudFormation Infrastructure as Code
- Template design for 15+ AWS services
- IaC best practices implementation
- Stack deployment and management
- Resource orchestration
- CI/CD pipeline integration with GitHub Actions

### AWS Best Practices
- Security and compliance
- Cost optimization (5 pillars, 12 best practices)
- Performance optimization
- Operational excellence
- Reliability and resilience

---

## Skills Coverage

### CloudFormation Skills (15)

| Category | Skills |
|----------|--------|
| **Networking** | VPC, CloudFront |
| **Compute** | EC2, Lambda, ECS, Auto Scaling |
| **Storage** | S3 |
| **Database** | RDS, DynamoDB, ElastiCache |
| **Security** | IAM, Security (KMS, Secrets Manager) |
| **Monitoring** | CloudWatch |
| **AI/ML** | Bedrock |
| **CI/CD** | ECS GitHub Actions Deploy |

### General AWS Skills (4)

| Skill | Purpose |
|-------|---------|
| `aws-cli-beast` | Advanced CLI operations and automation |
| `aws-sam-bootstrap` | Serverless project initialization and migration |
| `aws-drawio-architecture-diagrams` | Visual architecture diagrams |
| `aws-cost-optimization` | Cost management and optimization |

---

## Dependencies

- `developer-kit-core` (required) - Core functionality and shared patterns

---

## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) - Core guides and installation
- [Java Plugin Documentation](../../developer-kit-java/docs/) - Java AWS SDK integration
- [DevOps Plugin Documentation](../../developer-kit-devops/) - Docker and GitHub Actions guides

---

## Cross-Plugin References

The AWS plugin focuses on CloudFormation infrastructure as code. For AWS SDK integration from applications, see:

- **[Java Plugin](../../developer-kit-java/docs/)** - AWS SDK for Java integration (S3, DynamoDB, Lambda, SNS/SQS, Bedrock, KMS, Secrets Manager, RDS, Messaging)
- The Java plugin contains 10 AWS Java SDK skills for programmatic AWS access from Java applications
