---
allowed-tools: Read, Write, Edit, Grep, Glob
argument-hint: "[language] [output-format]"
description: Generates comprehensive security assessment document after security audit completion. Use when you need to create a structured security report.
---

## Overview

Generates comprehensive security assessment document after security audit completion. Use when you need to create a structured security report.

## Arguments

| Argument | Description |
|----------|-------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Usage

```
/devkit.generate-security-assessment $ARGUMENTS
```


## Examples

```bash
- `/developer-kit:devkit.generate-security-assessment en-US markdown` - Generate English assessment in Markdown
- `/developer-kit:devkit.generate-security-assessment it-IT pdf` - Generate Italian assessment in PDF
- `/developer-kit:devkit.generate-security-assessment docx` - Generate English assessment in DOCX
```

## Security Assessment Document Generation

**Target Project**: $ARGUMENTS

### Document Analysis Setup

First, I'll analyze the project structure and security audit findings:

1. **Project Analysis**: Examine codebase structure and technologies
2. **Security Review**: Check recent security audit results
3. **Risk Assessment**: Identify critical security areas
4. **Compliance Check**: Verify regulatory requirements

### Document Structure Generation

Based on security audit analysis, generating comprehensive assessment document with the following structure:

---

# Security Assessment Document

**Language**: Language detection from arguments...
**Format**: Output format configuration...
**Generation Date**: Current timestamp...

### 1. Project Overview and Security Scope

#### Project Description
[Auto-generated based on codebase analysis]

**Identified Technologies**: [Framework detection from package.json/pom.xml]
**Application Size**: [Lines of code, number of files]
**Application Type**: [Web, API, Desktop, Mobile]

#### Security Scope
**Assessment Perimeter**:
- Authentication and Authorization
- Data Protection
- Security Architecture
- Incident Management

**Exclusions**: [Components not in scope]

### 2. Identity and Access Management

#### Authentication
[Analysis of authentication mechanisms]
- **Identified Methods**: JWT, OAuth2, Session-based
- **Security Configurations**: Spring Security, Passport.js, NextAuth
- **Two-Factor Authentication**: Implementation status
- **Password Policies**: Current password strength requirements

#### Authorization
[Access control analysis]
- **Role-Based Access Control (RBAC)**: Implementation status
- **Method-Level Security**: @PreAuthorize, @Secured annotations
- **API Protection**: Endpoint security configuration
- **Resource Access Control**: File and data access policies

#### Session Management
[Session security evaluation]
- **Session Timeout**: Current timeout configurations
- **Session Fixation Protection**: Security measures implemented
- **Concurrent Session Control**: Multiple session policies
- **Secure Cookie Configuration**: HttpOnly, Secure, SameSite settings

### 3. Data Protection

#### Encryption
[Cryptography implementation analysis]
- **Data in Transit**: TLS/SSL configurations
- **Data at Rest**: Database encryption, file system encryption
- **Algorithms Used**: AES, RSA, bcrypt for passwords
- **Key Management**: Secret storage and rotation policies

#### Data Masking
[Sensitive data handling]
- **PII Protection**: Personal identifiable information masking
- **Credit Card Data**: PCI-DSS compliance measures
- **Log Sanitization**: Sensitive data removal from logs
- **Database Field Encryption**: Column-level encryption

#### Backup and Recovery
[Data backup strategies]
- **Backup Schedule**: Automated backup frequency
- **Backup Encryption**: Encrypted backup storage
- **Recovery Testing**: Regular restore procedure validation
- **Disaster Recovery**: Business continuity planning

### 4. Threat Protection

#### Firewall and WAF
[Network security configuration]
- **Web Application Firewall**: Implementation status
- **Ingress/Egress Filtering**: Network traffic controls
- **DDoS Protection**: Rate limiting and traffic monitoring
- **API Gateway Security**: Request validation and filtering

#### Common Attack Protection
[Attack prevention measures]
- **SQL Injection**: Parameterized queries, ORMs usage
- **XSS Protection**: Input sanitization, CSP headers
- **CSRF Protection**: Anti-CSRF tokens
- **File Upload Security**: File type validation, virus scanning

#### Vulnerability Monitoring
[Security monitoring setup]
- **Dependency Scanning**: npm audit, OWASP Dependency Check
- **Static Analysis**: Code quality security tools
- **Dynamic Testing**: Security testing automation
- **Security Headers**: HSTS, X-Frame-Options, CSP

### 5. Code Security

#### Secure Development Guidelines
[Coding standards analysis]
- **Input Validation**: Validation frameworks usage
- **Error Handling**: Secure error response patterns
- **Security Libraries**: Cryptography, authentication libraries
- **Code Quality**: Static analysis tools integration

#### Code Review Process
[Security review practices]
- **Security Code Review**: Peer review for security
- **Automated Security Testing**: CI/CD security gates
- **Security Standards**: OWASP ASVS compliance
- **Documentation**: Security requirements documentation

#### Security Testing
[Security testing strategy]
- **Unit Tests Security**: Security-focused unit tests
- **Integration Tests**: End-to-end security validation
- **Penetration Testing**: Regular security assessments
- **Security Monitoring**: Runtime security monitoring

### 6. Incident Management

#### Incident Response Plan
[Incident response procedures]
- **Detection**: Security incident identification
- **Response**: Immediate response actions
- **Containment**: Incident containment strategies
- **Recovery**: Service restoration procedures

#### Reporting
[Incident reporting structure]
- **Logging Strategy**: Comprehensive logging setup
- **Audit Trails**: User action tracking
- **Security Metrics**: Key security indicators
- **Compliance Reporting**: Regulatory reporting requirements

#### Communication
[Stakeholder communication]
- **Internal Notification**: Team alerting mechanisms
- **External Communication**: Customer notification procedures
- **Regulatory Reporting**: Legal requirement compliance
- **Public Relations**: Crisis communication plan

### 7. Training and Awareness

#### Staff Training
[Security education programs]
- **Developer Security**: Secure coding practices training
- **Security Awareness**: Phishing awareness programs
- **Compliance Training**: Regulatory requirement education
- **Regular Updates**: Ongoing security education

#### Attack Simulations
[Security validation exercises]
- **Phishing Simulations**: Employee security awareness testing
- **Penetration Testing**: Regular security assessments
- **Red Team Exercises**: Adversarial simulation testing
- **Security Drills**: Incident response practice

### 8. Compliance and Regulations

#### Regulatory Compliance
[Compliance framework analysis]
- **GDPR**: General Data Protection Regulation compliance
- **SOX**: Sarbanes-Oxley Act requirements
- **PCI-DSS**: Payment Card Industry Data Security Standard
- **ISO 27001**: Information Security Management

#### Security Audits
[Audit procedures and results]
- **Internal Audits**: Regular security assessments
- **External Audits**: Third-party security evaluations
- **Compliance Checks**: Automated compliance validation
- **Audit Findings**: Security improvement recommendations

### 9. Maintenance and Updates

#### Patch Management
[Update and patch procedures]
- **Vulnerability Scanning**: Regular security scans
- **Patch Schedule**: Automated update procedures
- **Testing Protocol**: Pre-deployment testing
- **Rollback Procedures**: Update failure recovery

#### Continuous Monitoring
[Ongoing security monitoring]
- **SIEM Integration**: Security information and event management
- **Real-time Alerting**: Immediate threat notification
- **Performance Monitoring**: Security impact on performance
- **Anomaly Detection**: Behavioral analysis systems

### 10. Appendices

#### Glossary
- **RBAC**: Role-Based Access Control
- **OWASP**: Open Web Application Security Project
- **TLS**: Transport Layer Security
- **PII**: Personal Identifiable Information

#### Useful Resources
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Security Guidelines**: Internal security documentation
- **Tools**: Security assessment tools used
- **Contacts**: Security team contact information

---

## Document Generation Process

1. **Analyze Codebase Structure**: Detect technologies, frameworks, and security implementations
2. **Review Security Audit Results**: Parse findings from recent security assessments
3. **Generate Risk Assessment**: Create project-specific security risk evaluation
4. **Format Document**: Apply requested language and output format
5. **Include Recommendations**: Provide actionable security improvement suggestions
6. **Add Compliance Mapping**: Map to relevant security standards and regulations

**Output**: Complete security assessment document ready for stakeholder review and security planning.

Language: $ARGUMENTS
Format: Based on user preference (Markdown default)

## Execution Instructions

**Agent Selection**: To execute this generation task, use the following approach:
- Primary: Use `general-purpose` agent with specialized knowledge of the task domain
- Or use appropriate specialized agent if available for the specific generation task
