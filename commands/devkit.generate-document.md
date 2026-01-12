---
description: Generate professional documents (assessments, features, analysis, process, custom) with language support and specialized sub-agents
argument-hint: --lang=en|it|es|fr|de --type=assessment|feature|analysis|process|custom [objective/description]
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Document Generation Command

Generate professional technical and business documents with multi-language support. This command analyzes your codebase and produces comprehensive, well-structured documentation based on the specified type and objective.

## Current Context

- **Current Directory**: !`pwd`
- **Git Branch**: !`git branch --show-current`
- **Project Structure**: !`ls -la`

## Arguments

**Input received**: $ARGUMENTS

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `en`, `it`, `es`, `fr`, `de`, `pt` | `en` | Document language |
| `--type` | `assessment`, `feature`, `analysis`, `process`, `custom` | `assessment` | Document type |
| `--format` | `markdown`, `html`, `pdf` | `markdown` | Output format |

### Document Types

| Type | Description | Use Case |
|------|-------------|----------|
| `assessment` | Evaluation and audit documents | Technical debt, security review, performance analysis |
| `feature` | Feature specifications and proposals | New features, enhancements, requirements |
| `analysis` | Deep-dive technical analysis | Gap analysis, impact analysis, comparative studies |
| `process` | Process and workflow documentation | SOPs, runbooks, procedures |
| `custom` | Custom document format | Any specific documentation need |

### Languages

| Code | Language | Full Code |
|------|----------|-----------|
| `en` | English | `en-US` |
| `it` | Italian | `it-IT` |
| `es` | Spanish | `es-ES` |
| `fr` | French | `fr-FR` |
| `de` | German | `de-DE` |
| `pt` | Portuguese | `pt-BR` |

## Core Principles

- **Codebase-Driven**: Analyze actual code to generate accurate documentation
- **Multi-Language**: Full support for multiple languages with proper terminology
- **Structured Output**: Follow professional document templates and standards
- **Actionable Content**: Include concrete recommendations and next steps
- **Stakeholder-Ready**: Produce documents ready for review and distribution

---

## Phase 1: Discovery

**Goal**: Understand what document needs to be generated

**Actions**:
1. Parse $ARGUMENTS to extract:
   - `--lang` parameter (default: `en`)
   - `--type` parameter (default: `assessment`)
   - `--format` parameter (default: `markdown`)
   - Remaining text as the document objective/description
2. Create todo list with all phases
3. If document objective is unclear, ask user for:
   - What is the purpose of this document?
   - Who is the target audience?
   - What specific areas should be covered?
   - Any constraints or requirements?
4. Summarize understanding and confirm with user

---

## Phase 2: Codebase Analysis

**Goal**: Gather relevant information from the codebase

**Actions**:
1. Use the Task tool to launch an explorer agent to analyze the codebase

   **Agent Selection by Project Type**:
   - Java/Spring Boot: `developer-kit:spring-boot-backend-development-expert`
   - TypeScript/NestJS: `developer-kit:nestjs-backend-development-expert`
   - TypeScript/General: `developer-kit:general-code-explorer`
   - React: `developer-kit:react-frontend-development-expert`
   - General: `developer-kit:general-code-explorer`

   **Example Task Tool Usage**:
   ```
   Task(
     description: "Analyze codebase for document generation",
     prompt: "Analyze the codebase structure, architecture, patterns, and relevant details for generating a [document-type] document about [objective]. Return a comprehensive summary with file references.",
     subagent_type: "developer-kit:general-code-explorer"
   )
   ```

2. Based on document type, gather specific information:

   **For Assessment Documents**:
   - Code quality metrics
   - Architecture patterns
   - Security configurations
   - Performance characteristics
   - Test coverage
   - Dependencies and versions

   **For Feature Documents**:
   - Existing similar features
   - Technical constraints
   - Integration points
   - Current architecture

   **For Analysis Documents**:
   - Relevant code sections
   - Configuration files
   - Documentation gaps
   - Patterns and anti-patterns

   **For Process Documents**:
   - Existing workflows
   - Automation scripts
   - CI/CD configurations
   - Deployment procedures

3. Read all identified key files to build deep understanding
4. Document findings and patterns discovered

---

## Phase 3: Content Planning

**Goal**: Define document structure and content outline

**Actions**:
1. Select appropriate template based on `--type`:
   - `assessment`: Assessment Document Template
   - `feature`: Feature Specification Template
   - `analysis`: Analysis Document Template
   - `process`: Process Document Template
   - `custom`: User-defined or hybrid template

2. Create detailed outline with:
   - Main sections and subsections
   - Key points for each section
   - Required diagrams and visuals
   - Code examples to include

3. **Use AskUserQuestion tool** to present outline and get approval:
   - Show proposed document structure
   - Highlight key sections
   - Ask if any sections should be added/removed
   - Confirm target audience and depth

---

## Phase 4: Document Generation

**Goal**: Generate the complete document

**Actions**:
1. Use the Task tool to launch the document generator agent:

   ```
   Task(
     description: "Generate [document-type] document",
     prompt: "Generate a comprehensive [document-type] document in [language] about [objective]. 
     
     Context gathered:
     [Include codebase analysis findings]
     
     Document outline:
     [Include approved outline]
     
     Requirements:
     - Language: [--lang value]
     - Format: [--format value]
     - Audience: [identified audience]
     
     Generate the complete document following the template structure.",
     subagent_type: "developer-kit:document-generator-expert"
   )
   ```

2. For specialized document types, also invoke domain experts:

   **Security Assessment**:
   - Primary: `developer-kit:document-generator-expert`
   - Support: `developer-kit:java-security-expert` or `developer-kit:typescript-security-expert`

   **Architecture Analysis**:
   - Primary: `developer-kit:document-generator-expert`
   - Support: `developer-kit:java-software-architect-review` or `developer-kit:typescript-software-architect-review`

   **Feature Specification**:
   - Primary: `developer-kit:document-generator-expert`
   - Support: `developer-kit:general-software-architect`

3. Generate document content section by section
4. Include diagrams using Mermaid format
5. Add code examples with proper syntax highlighting
6. Apply language-specific terminology consistently

---

## Phase 5: Review and Refinement

**Goal**: Ensure document quality and completeness

**Actions**:
1. Review generated document for:
   - Completeness of all required sections
   - Accuracy of technical content
   - Consistency in terminology and style
   - Appropriate depth for target audience
   - Language correctness

2. **Use AskUserQuestion tool** to present draft:
   - Show complete document
   - Ask for feedback on each major section
   - Confirm technical accuracy
   - Request any additions or modifications

3. Apply requested changes
4. Add cross-references and links
5. Generate table of contents if needed

---

## Phase 6: Output and Summary

**Goal**: Deliver final document and summary

**Actions**:
1. Save document to appropriate location:
   - Default: `docs/[document-type]-[timestamp].md`
   - Or user-specified location

2. Generate summary:
   - Document type and purpose
   - Key findings/content highlights
   - Sections included
   - Next steps or recommendations

3. Mark all todos complete

---

## Usage Examples

```bash
# Generate technical assessment in English (default)
/devkit.generate-document --type=assessment List all application features and their current status

# Generate feature specification in Italian
/devkit.generate-document --lang=it --type=feature User authentication with OAuth2 integration

# Generate security analysis in Spanish
/devkit.generate-document --lang=es --type=analysis Security vulnerabilities and compliance gaps

# Generate deployment process documentation in French
/devkit.generate-document --lang=fr --type=process CI/CD pipeline and deployment procedures

# Generate custom report in German
/devkit.generate-document --lang=de --type=custom API design patterns and best practices used in the project

# Generate feature proposal with HTML output
/devkit.generate-document --type=feature --format=html Real-time notification system proposal

# Generate gap analysis in Portuguese
/devkit.generate-document --lang=pt --type=analysis Current vs. target architecture comparison

# Quick assessment (all defaults)
/devkit.generate-document Technical debt and improvement opportunities
```

## Document Type Details

### Assessment Documents
Generate comprehensive evaluation documents including:
- Executive summary with key findings
- Current state analysis
- Strengths and areas for improvement
- Risk assessment matrix
- Prioritized recommendations
- Implementation roadmap

**Common Assessment Types**:
- Technical Debt Assessment
- Security Assessment
- Performance Assessment
- Code Quality Assessment
- Architecture Assessment
- DevOps Maturity Assessment

### Feature Documents
Generate detailed feature specifications including:
- Feature overview and value proposition
- Functional requirements
- Technical requirements
- Design and architecture
- Implementation plan
- Testing strategy
- Risks and mitigations

### Analysis Documents
Generate in-depth analysis documents including:
- Analysis methodology
- Data and evidence
- Key observations
- Findings with supporting evidence
- Conclusions and insights
- Actionable recommendations

**Common Analysis Types**:
- Gap Analysis
- Impact Analysis
- Comparative Analysis
- Root Cause Analysis
- Dependency Analysis

### Process Documents
Generate structured process documentation including:
- Process overview and objectives
- Roles and responsibilities
- Prerequisites and requirements
- Step-by-step procedures
- Decision points and exceptions
- Metrics and KPIs

### Custom Documents
Generate tailored documents based on user requirements:
- Combine elements from multiple templates
- Follow user-specified structure
- Adapt to specific industry or domain requirements

---

## Integration with Sub-agents

This command leverages specialized sub-agents for different aspects:

| Phase | Agent | Purpose |
|-------|-------|---------|
| Analysis | `developer-kit:general-code-explorer` | Codebase exploration |
| Analysis | `developer-kit:spring-boot-backend-development-expert` | Java/Spring analysis |
| Analysis | `developer-kit:nestjs-backend-development-expert` | NestJS analysis |
| Generation | `developer-kit:document-generator-expert` | Primary document generation |
| Support | `developer-kit:java-security-expert` | Security domain expertise |
| Support | `developer-kit:typescript-security-expert` | TypeScript security |
| Support | `developer-kit:general-software-architect` | Architecture insights |

---

## Todo Management

Throughout the process, maintain a todo list:

```
[ ] Phase 1: Discovery - Parse arguments and understand requirements
[ ] Phase 2: Codebase Analysis - Gather relevant information
[ ] Phase 3: Content Planning - Define structure and outline
[ ] Phase 4: Document Generation - Create complete document
[ ] Phase 5: Review and Refinement - Quality assurance
[ ] Phase 6: Output and Summary - Deliver final document
```

Update status as you progress through each phase.

---

## Output Format

The generated document will be saved as:
- **Markdown** (default): `docs/[type]-[objective-slug]-[YYYYMMDD].md`
- **HTML**: `docs/[type]-[objective-slug]-[YYYYMMDD].html`
- **PDF**: Requires additional processing (pandoc or similar)

---

**Note**: This command follows a systematic approach to ensure high-quality, professional documentation that accurately reflects your codebase and meets stakeholder requirements.
