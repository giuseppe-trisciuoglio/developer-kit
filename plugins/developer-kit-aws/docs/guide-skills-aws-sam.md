# AWS SAM Bootstrap Skill Guide

## Overview

The **AWS SAM Bootstrap** skill helps initialize and migrate serverless projects using AWS Serverless Application Model (SAM). It supports both greenfield projects and existing Lambda/CloudFormation codebases, and standardizes `template.yaml`, `samconfig.toml`, and local test event artifacts.

## Skill Details

| Property | Value |
|----------|-------|
| **Name** | aws-sam-bootstrap |
| **Category** | General AWS |
| **Tools** | Read, Write, Bash |

## When to Use This Skill

Use this skill when you need to:
- Configure AWS SAM for an existing Lambda or CloudFormation project
- Create a new SAM project with production-ready defaults
- Generate or update `template.yaml` and `samconfig.toml`
- Add local test payloads in `events/` for `sam local invoke`
- Standardize build/package/deploy workflow for `sam deploy`

## Trigger Phrases

- "Configure AWS SAM for this project"
- "Create a new SAM project"
- "Add template.yaml for SAM"
- "Initialize SAM for existing Lambda function"
- "Generate samconfig.toml"

---

## Core Capabilities

### 1) New Project Bootstrap

- Guide usage of `sam init` with runtime and package type selection
- Set baseline build/deploy parameters in `samconfig.toml`
- Add sample local invocation events

### 2) Existing Project Migration

- Analyze current handler/runtime/dependency layout
- Map existing Lambda resources into SAM templates
- Preserve deployment-critical settings (timeout, memory, environment, triggers)

### 3) Required Artifacts

The skill ensures these files exist:

```text
.
├── template.yaml
├── samconfig.toml
└── events/
    └── event.json
```

### 4) SAM Command Coverage

- `sam init`
- `sam validate`
- `sam build`
- `sam package`
- `sam deploy --guided`
- `sam local invoke`

---

## Default `samconfig.toml` Pattern

```toml
version = 0.1

[default.global.parameters]
stack_name = "my-sam-app"

[default.build.parameters]
cached = true
parallel = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = true
resolve_s3 = true

[prod.deploy.parameters]
confirm_changeset = false
```

---

## Recommended Workflow

1. Identify scenario: new project or migration
2. Select runtime and package type (Zip or Image)
3. Generate/update `template.yaml`
4. Generate/update `samconfig.toml`
5. Add `events/event.json`
6. Run `sam validate`
7. Run `sam build`
8. Run `sam local invoke` and then `sam deploy --guided`

---

## Related Skills

- **AWS CloudFormation Lambda** (`aws-cloudformation-lambda`) - Lambda infrastructure patterns in CloudFormation
- **AWS CLI Beast Mode** (`aws-cli-beast`) - Advanced AWS CLI operational workflows
- **AWS Cost Optimization** (`aws-cost-optimization`) - Cost controls for serverless and other AWS workloads
