# Developer Kit AWS Plugin Documentation

Welcome to the Developer Kit AWS Plugin documentation. This plugin provides comprehensive tools for AWS cloud architecture, CloudFormation infrastructure as code, and DevOps automation.

---

## Available Documentation

### Skills Guides

- **[CloudFormation Skills](./guide-skills-cloudformation.md)** - AWS CloudFormation IaC skills (15 skills)
- **[AWS Cost Optimization](./guide-skills-cost-optimization.md)** - AWS cost optimization strategies

### Component Guides

- **[Agent Guide](./guide-agents.md)** - AWS specialized agents

---

## About AWS Plugin

The Developer Kit AWS Plugin provides:

- **AWS Agents**: 3 specialized agents for AWS architecture, CloudFormation, and DevOps
- **AWS Skills**: 17 skills covering AWS CloudFormation templates, AWS architecture diagrams, and cost optimization

---

## Plugin Structure

```
developer-kit-aws/
├── agents/                    # AWS architecture and DevOps agents
├── skills/
│   ├── aws-cloudformation/    # CloudFormation template skills (15 skills)
│   └── aws/                   # General AWS skills (architecture diagrams, cost optimization)
└── docs/                      # This documentation
```

---

## Quick Start

1. **Explore available agents**: See [Agent Guide](./guide-agents.md)
2. **Learn CloudFormation patterns**: See [CloudFormation Skills](./guide-skills-cloudformation.md)
3. **Design AWS architecture**: Use `aws-solution-architect-expert` agent
4. **Create IaC templates**: Use `aws-cloudformation-devops-expert` agent

---

## Key Features

### AWS Architecture Design
- Solution architecture design
- Well-Architected Framework application
- Multi-region and high availability design
- Serverless architecture patterns
- Cloud migration planning

### CloudFormation Infrastructure as Code
- Template design for various AWS services
- IaC best practices implementation
- Stack deployment and management
- Resource orchestration
- CI/CD pipeline integration

### AWS Best Practices
- Security and compliance
- Cost optimization
- Performance optimization
- Operational excellence
- Reliability and resilience

---

## Skills Coverage

### CloudFormation Skills

The AWS plugin includes CloudFormation skills for:

- **VPC**: Networking foundations
- **EC2**: Compute resources
- **S3**: Storage
- **RDS**: Databases
- **Lambda**: Serverless computing
- **ECS/Fargate**: Container orchestration
- **DynamoDB**: NoSQL databases
- **CloudFront**: CDN
- **SNS/SQS**: Messaging
- **IAM**: Security and access management
- **CloudWatch**: Monitoring
- **Bedrock**: AI/ML services
- **ElastiCache**: Caching
- **Security**: Security best practices
- **Task ECS Deploy GH**: ECS deployment with GitHub Actions

### General AWS Skills

- **AWS Architecture Diagrams**: Professional AWS architecture diagram creation in draw.io format
- **AWS Cost Optimization**: Structured cost optimization guidance using five pillars (right-sizing, elasticity, pricing models, storage optimization, monitoring) and twelve actionable best practices

---

## See Also

- [Core Plugin Documentation](../developer-kit-core/docs/) - Core guides and installation
- [Java Plugin Documentation](../developer-kit-java/docs/) - Java AWS SDK integration
- [DevOps Plugin Documentation](../developer-kit-devops/docs/) - Docker and GitHub Actions guides

---

## Cross-Plugin References

The AWS plugin focuses on CloudFormation infrastructure as code. For AWS SDK integration from applications, see:

- **[Java Plugin](../developer-kit-java/docs/)** - AWS SDK for Java integration (S3, DynamoDB, RDS, Lambda, SNS/SQS, Bedrock, KMS, Secrets Manager, RDS, Messaging)
- The Java plugin contains 10 AWS Java SDK skills for programmatic AWS access from Java applications
