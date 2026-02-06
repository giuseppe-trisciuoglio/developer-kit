# Security Policy

## Supported Versions

The Developer Kit for Claude Code currently supports the versions indicated in the "Versioning" section of [CHANGELOG.md](CHANGELOG.md).

Only versions within the active support period will receive security updates.

## Reporting Vulnerabilities

The Developer Kit for Claude Code team takes security very seriously. If you discover a vulnerability, we thank you for contacting us responsibly.

### How to Report

To report a security vulnerability:

1. **Do not open a public issue** - This would expose the vulnerability before it can be fixed
2. **Send an email** to: `giuseppe.trisciuoglio@gmail.com` (replace with the actual team address)
3. **Include in your report**:
   - Detailed description of the vulnerability
   - Steps to reproduce (proof of concept if possible)
   - Potential impact of the vulnerability
   - Affected project version
   - Any suggestions for the fix

### What to Expect

- You will receive a response within **48 hours** to confirm receipt of your report
- We will provide regular updates on the fix status
- We leave it to you to decide whether and when to be publicly credited for the discovery
- We will publish a security advisory as soon as the fix is available

### Coordinated Disclosure

We follow a **coordinated disclosure** approach:
- Critical vulnerabilities are fixed within 7 days
- Important vulnerabilities are fixed within 14 days
- The public advisory is published after the fix is available

## Security Model for Skills, Commands, and Agents

This project implements specific security measures for Claude components (Skills, Slash Commands, and Subagents).

### Skills Security

Skills in this project follow Anthropic's security best practices:

#### Tool Access Control
Each SKILL.md explicitly specifies permissions through the `allowed-tools` field:

```yaml
---
allowed-tools: Read, Grep, Glob
---
```

**Implemented Best Practices:**
- Read-only Skills: limited to `Read`, `Grep`, `Glob`
- Code analysis Skills: `allowed-tools: Read, Bash, Grep`
- Data processing Skills: `allowed-tools: Read, Write, Bash`
- No Skill has unrestricted access to all tools by default

#### Preventing Prompt Injection
- Skills use third-person descriptions to prevent contextual confusion
- Instructions avoid ambiguous language that could be manipulated
- File references are specific and do not use dynamic patterns

#### Data Protection
- No Skill stores or transmits hardcoded credentials
- Skills with Bash access explicitly document executable commands
- Explicit validation for all user input

### Slash Commands Security

Custom slash commands implement:

#### Permission Constraints
```yaml
---
allowed-tools: Bash(git add:*, git status:*), Read, Write
---
```

**Best Practices:**
- Granular limitations for bash commands (e.g., `git add:*` not `git:*`)
- No command has access to system modification tools without restrictions
- Clear argument hints to prevent malicious input

#### Command Isolation
- Commands are executed in the context of the current repository
- No command accesses files outside the working directory without explicit authorization
- Commands that modify files require user confirmation

### Subagents Security

Subagents in `.claude/agents/` follow:

#### Tool Restrictions
```yaml
---
tools: Read, Bash, Edit
model: inherit
---
```

**Implemented Principles:**
- Each subagent has specific permissions for its domain
- No subagent has access to all MCP tools by default
- The `model: inherit` field maintains consistency with the main session's security settings

#### Agent Scope
- Subagents are focused on a single domain (single responsibility)
- Instructions include explicit constraints and limitations
- Clear documentation on when to escalate to the main conversation

## Threat Model

### Identified Risks

The project addresses the following risks identified in the AI security community:

#### 1. Unauthorized Code Execution
**Mitigation:**
- Restrictive `allowed-tools` in all SKILL.md files
- No Skill executes code from unvalidated external sources
- Bash commands are explicitly documented and limited

#### 2. Data Exfiltration
**Mitigation:**
- No Skill accesses sensitive data without explicit permission
- Skills document the data they process
- Transparent logging of operations

#### 3. Permission Bypass
**Mitigation:**
- Multi-level permission validation
- Hooks are configured to prevent unauthorized modifications
- Skills cannot modify their own permissions

#### 4. Confused Deputy Problem
**Mitigation:**
- Skills do not act on behalf of users without verifying context
- Sensitive operations require explicit confirmation
- Skills document assumptions about execution context

### Supply Chain Security

To protect the supply chain:

1. **Origin Verification**
   - All Skills are versioned in this repository
   - Users can verify provenance through git history
   - Release signing with GPG keys (planned implementation)

2. **Integrity Checks**
   - SKILL.md file hash comparison
   - YAML frontmatter syntax validation
   - Automated tests to verify Skills comply with declared constraints

3. **Dependency Management**
   - Skills have no undocumented external dependencies
   - Utility scripts are included in the repository
   - No external package dependencies without review

## Security Best Practices for Contributors

When contributing to the project, follow these guidelines:

### For Skills
1. **Always limit `allowed-tools`** to the minimum necessary
2. **Never include**:
   - Hardcoded credentials
   - API keys
   - Authentication tokens
3. **Validate all user input**
4. **Use relative paths** instead of absolute when possible
5. **Explicitly document** any file-modifying operations

### For Slash Commands
1. **Specify granular permissions** for bash commands
2. **Do not use unrestricted wildcards** in `allowed-tools`
3. **Validate arguments** before using them
4. **Avoid destructive commands** without explicit confirmation

### For Subagents
1. **Limit tools** to the specific domain
2. **Always include**:
   - Explicit constraints
   - Clear limitations
   - When to escalate
3. **Test with all models** you intend to support

## Auditing Skills

Before installing a Skill from an unverified source, perform an audit:

### Checklist
- [ ] Read `SKILL.md` to understand the purpose
- [ ] Verify `allowed-tools` - are they appropriate?
- [ ] Look for suspicious file or path references
- [ ] Check scripts in `scripts/` for insecure operations
- [ ] Verify the description contains no XML tags (frontmatter violation)
- [ ] Test the Skill in an isolated environment before using it on real data

### Red Flags
- Vague descriptions like "does everything" or "universal helper"
- `allowed-tools` omitted (all tools permitted)
- References to sensitive system paths
- Bash commands with broad wildcards
- Requests for credentials or tokens

## Responsible AI Principles

The project aligns with Anthropic's framework for trustworthy agents:

### 1. Human Control
- Destructive operations require explicit confirmation
- Users can interrupt any operation
- Skills do not operate completely autonomously without oversight

### 2. Transparency
- Each Skill clearly documents:
  - What it does
  - When it is used
  - Which tools it uses
- Operations are visible to the user
- Skill decisions are tracked

### 3. Alignment
- Skills have specific and limited objectives
- Instructions prevent out-of-scope behaviors
- Skills do not interpret commands creatively in ways that could violate intentions

### 4. Privacy
- No Skill shares data between different contexts without permission
- Skills do not store sensitive information
- Data is treated according to the minimization principle

### Environment Isolation

For production environments:
1. Use enterprise accounts with additional controls
2. Run Claude Code in sandboxed environments
3. Limit file system access
4. Monitor operation logs

## Related Resources

- [GitHub Security Advisories](https://github.com/giuseppe-trisciuoglio/developer-kit/security/advisories)
- [Anthropic's Responsible Scaling Policy](https://www.anthropic.com/responsible-scaling-policy)
- [Claude Skills Security Guidance](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Framework for Safe and Trustworthy Agents](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)

## License

This security policy is licensed under the same terms as the main project.

## Contact

For general security questions that are not vulnerabilities:
- Open a GitHub discussion with the `security` tag
- Contact: `giuseppe.trisciuoglio@gmail.com