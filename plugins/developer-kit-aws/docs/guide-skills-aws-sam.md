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
- Migrate existing Lambda functions to SAM templates

## Trigger Phrases

- "Configure AWS SAM for this project"
- "Create a new SAM project"
- "Add template.yaml for SAM"
- "Initialize SAM for existing Lambda function"
- "Generate samconfig.toml"
- "Migrate Lambda to SAM"
- "Bootstrap serverless project"

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

```
.
├── template.yaml
├── samconfig.toml
└── events/
    └── event.json
```

### 4) SAM Command Coverage

| Command | Purpose |
|---------|---------|
| `sam init` | Initialize a new SAM project |
| `sam validate` | Validate template.yaml syntax |
| `sam build` | Build the project |
| `sam package` | Package for deployment |
| `sam deploy --guided` | Deploy with guided configuration |
| `sam local invoke` | Test function locally |

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

1. **Identify scenario**: new project or migration
2. **Select runtime**: Choose non-deprecated runtimes (Zip or Image package type)
3. **Generate/update `template.yaml`**: Define Lambda functions and related resources
4. **Generate/update `samconfig.toml`**: Configure deploy parameters
5. **Add `events/event.json`**: Create test payloads for local invocation
6. **Validate**: Run `sam validate`
7. **Build**: Run `sam build`
8. **Test locally**: Run `sam local invoke`
9. **Deploy**: Run `sam deploy --guided`

---

## Validation Checklist

Before deploying, verify:

- [ ] `sam validate` succeeds without errors
- [ ] `sam build` completes successfully
- [ ] `template.yaml` has correct logical IDs and handlers
- [ ] `samconfig.toml` contains deploy parameters for target environments
- [ ] IAM capabilities are correctly configured
- [ ] Test events are valid JSON

---

## Reference Materials

The skill includes comprehensive reference guides:

- `references/examples.md` - Complete SAM template examples
- `references/migration-checklist.md` - Step-by-step migration guide

---

## Related Skills

- **AWS CloudFormation Lambda** (`aws-cloudformation-lambda`) - Lambda infrastructure patterns in CloudFormation
- **AWS CLI Beast Mode** (`aws-cli-beast`) - Advanced AWS CLI operational workflows
- **AWS Cost Optimization** (`aws-cost-optimization`) - Cost controls for serverless workloads
