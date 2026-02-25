# AWS Cost Optimization Skill Guide

## Overview

The **AWS Cost Optimization** skill provides structured guidance for reducing AWS spending through five optimization pillars and twelve actionable best practices. This skill leverages AWS native tools to identify savings opportunities and establish ongoing cost governance.

## Skill Details

| Property | Value |
|----------|-------|
| **Name** | aws-cost-optimization |
| **Category** | General AWS |
| **Tools** | Read, Write, Bash |

## When to Use This Skill

Use this skill when you need to:
- Optimize AWS costs or review AWS spending
- Find unused or under-utilized AWS resources
- Implement FinOps practices for cloud cost governance
- Reduce EC2, EBS, S3, or load balancer bills
- Choose between On-Demand, Spot, Reserved Instances, and Savings Plans
- Configure AWS Budgets, Cost Explorer, or Cost Anomaly Detection
- Perform an AWS Well-Architected Framework cost pillar review

## Trigger Phrases

- "Optimize my AWS costs"
- "Review AWS spending"
- "Find unused AWS resources"
- "Help me with FinOps"
- "How can I reduce my EC2 bill?"
- "Clean up unused EBS volumes"
- "Set up AWS Budgets"

---

## Five Optimization Pillars

### Pillar 1 — Right-Size

Match provisioned resources to actual workload needs.

- Pull 14-day average CPU/memory metrics from CloudWatch for every EC2 instance
- Cross-reference with AWS Compute Optimizer recommendations
- Flag instances where peak utilization stays below 40%
- Recommend downsizing to the next smaller instance family/size
- For RDS, check read/write IOPS vs. provisioned capacity

### Pillar 2 — Increase Elasticity

Schedule instance stop/start and leverage Auto Scaling Groups.

- Identify non-production instances running 24/7 (dev, staging, QA)
- Propose stop/start schedules using AWS Instance Scheduler or EventBridge rules
- Review Auto Scaling Group policies for over-provisioned min/desired counts
- Recommend target-tracking scaling policies tied to actual demand metrics
- Consider Lambda or Fargate for bursty, event-driven workloads

### Pillar 3 — Leverage the Right Pricing Model

Choose the optimal mix of On-Demand, Spot, Reserved Instances, and Savings Plans.

- Analyze steady-state baseline using Cost Explorer "RI Coverage" and "Savings Plans Coverage" reports
- Recommend Compute Savings Plans for consistent baseline compute
- Suggest Spot Instances for fault-tolerant, stateless workloads (batch, CI/CD runners)
- Evaluate existing Reserved Instances for utilization; resell unused RIs on the RI Marketplace
- Use the AWS Pricing Calculator to model total cost under each pricing option

### Pillar 4 — Optimize Storage

Eliminate waste in EBS, S3, and snapshots.

- List unattached EBS volumes (`available` state) and recommend deletion after backup review
- Identify orphaned EBS snapshots no longer linked to an active AMI or volume
- Review S3 bucket metrics; recommend Intelligent-Tiering or lifecycle rules for infrequent access data
- Enable Amazon Data Lifecycle Manager (DLM) for automated snapshot retention
- Check for gp2 volumes that should be migrated to gp3 for cost and performance gains

### Pillar 5 — Measure, Monitor, and Improve

Establish continuous cost governance.

- Implement a cost allocation tagging strategy (e.g., `Environment`, `Team`, `Project`, `CostCenter`)
- Configure AWS Budgets with threshold alerts (50%, 80%, 100%, forecasted)
- Enable AWS Cost Anomaly Detection for automatic spend anomaly alerts
- Set up a monthly Cost Explorer saved report for leadership review
- Create a Trusted Advisor check schedule for cost optimization recommendations

---

## Twelve Actionable Best Practices

| # | Best Practice | Pillar | AWS Tool |
|---|---|---|---|
| 1 | Choose appropriate AWS region (cost, latency, data sovereignty) | Right-Size | AWS Pricing Calculator |
| 2 | Schedule start/stop for non-production instances | Elasticity | Instance Scheduler / EventBridge |
| 3 | Identify under-utilized EC2 instances | Right-Size | Cost Explorer / Compute Optimizer |
| 4 | Reduce EC2 costs with Spot Instances | Pricing Model | EC2 Spot / Spot Fleet |
| 5 | Optimize Auto Scaling Group policies | Elasticity | Auto Scaling / CloudWatch |
| 6 | Use or resell under-utilized Reserved Instances | Pricing Model | RI Marketplace / Cost Explorer |
| 7 | Leverage Compute Savings Plans | Pricing Model | Savings Plans Console |
| 8 | Monitor and delete unused EBS volumes | Storage | EC2 Console / Trusted Advisor |
| 9 | Identify and clean up orphaned EBS snapshots | Storage | Data Lifecycle Manager |
| 10 | Remove idle load balancers; use CloudFront | Right-Size | Trusted Advisor / CloudFront |
| 11 | Implement cost allocation tagging | Monitoring | AWS Tag Editor / Cost Allocation Tags |
| 12 | Automate anomaly detection | Monitoring | AWS Cost Anomaly Detection |

---

## AWS Native Tools Reference

| Tool | Purpose |
|---|---|
| AWS Cost Explorer | Visualize, filter, and forecast AWS spend by service, account, or tag |
| AWS Budgets | Set custom spend/usage budgets with threshold alerts |
| AWS Pricing Calculator | Model and compare pricing for new or changed workloads |
| AWS Compute Optimizer | ML-driven right-sizing recommendations for EC2, EBS, Lambda |
| AWS Trusted Advisor | Automated checks for cost optimization, security, performance |
| Amazon Data Lifecycle Manager | Automate EBS snapshot creation and retention policies |
| AWS Cost Anomaly Detection | ML-powered anomaly detection with root-cause analysis |

---

## Review Process

Follow this structured flow when the user asks for a cost review:

1. **Scope** — Ask which AWS accounts, regions, and services to review
2. **Data Gathering** — Pull Cost Explorer data for the last 30–90 days; identify top-5 cost drivers
3. **Pillar Walk-Through** — Evaluate each of the five pillars in order
4. **Checklist** — Present the twelve best practices as a scored checklist (done / not done / partial)
5. **Quick Wins** — Highlight the three highest-impact, lowest-effort actions
6. **Roadmap** — Propose a 30/60/90-day optimization plan with estimated savings

---

## Related Skills

- **AWS Architecture Diagrams** (`aws-drawio-architecture-diagrams`) - Create visual representations of AWS architectures
- **CloudFormation VPC** (`aws-cloudformation-vpc`) - Design cost-effective VPC architectures
- **CloudFormation EC2** (`aws-cloudformation-ec2`) - Optimize EC2 cost configurations
- **CloudFormation S3** (`aws-cloudformation-s3`) - Implement S3 lifecycle policies for cost savings

---

## See Also

- [AWS Well-Architected Framework - Cost Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/)
- [AWS Cost Optimization Hub](https://aws.amazon.com/aws-cost-management/cost-optimization/)
- [AWS Pricing Calculator](https://calculator.aws/)
- [AWS Compute Optimizer](https://aws.amazon.com/compute-optimizer/)
