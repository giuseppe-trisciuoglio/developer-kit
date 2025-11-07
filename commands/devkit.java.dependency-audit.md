---
allowed-tools: Read, Bash, Grep, Glob, Write
argument-hint: [scope] [focus] [format]
description: Comprehensive dependency audit for Java projects with vulnerability scanning, license compliance, and supply chain security analysis
---

# Java Dependency Audit and Security Analysis

Perform comprehensive dependency analysis for Java/Maven/Gradle projects to identify security vulnerabilities, licensing issues, outdated packages, and supply chain risks with actionable remediation strategies.

## Context

- Build system: !`ls -la | grep -E "(pom\.xml|build\.gradle|build\.gradle\.kts)"`
- Current dependencies: !`if [ -f pom.xml ]; then mvn dependency:list 2>/dev/null | head -30; elif [ -f build.gradle ]; then ./gradlew dependencies 2>/dev/null | head -30; fi`
- Dependency tree depth: !`if [ -f pom.xml ]; then mvn dependency:tree 2>/dev/null | wc -l; elif [ -f build.gradle ]; then ./gradlew dependencies 2>/dev/null | wc -l; fi`

## Arguments

$1 specifies the scope (optional - defaults to `all`):
- `all` - Complete dependency audit (vulnerabilities, licenses, outdated)
- `security` - Focus on CVEs and security vulnerabilities only
- `licenses` - License compliance and compatibility analysis
- `outdated` - Identify outdated dependencies with update recommendations
- `supply-chain` - Supply chain security risks (typosquatting, maintainer changes)
- `transitive` - Focus on transitive (indirect) dependencies
- `<groupId:artifactId>` - Analyze specific dependency (e.g., `org.springframework.boot:spring-boot-starter`)

$2 specifies the focus area (optional - defaults to `comprehensive`):
- `comprehensive` - All analysis categories
- `critical-only` - Only critical and high severity issues
- `production` - Focus on production runtime dependencies
- `direct` - Only direct dependencies (exclude transitive)
- `cve` - CVE database cross-reference
- `compliance` - License and regulatory compliance

$3 specifies the output format (optional - defaults to `report`):
- `report` - Detailed markdown report
- `summary` - Executive summary with metrics
- `json` - Machine-readable JSON format
- `sarif` - SARIF format for CI/CD integration
- `remediation` - Actionable fix commands and PRs

## Audit Analysis Process

### 1. Dependency Discovery and Inventory

Comprehensive dependency scanning:

**Maven Dependency Analysis**
```bash
# List all dependencies with scope
mvn dependency:list -DoutputFile=dependencies.txt

# Full dependency tree
mvn dependency:tree -Dverbose -DoutputFile=dependency-tree.txt

# Dependency convergence check
mvn dependency:analyze -DignoreNonCompile=true

# Dependency resolution analysis
mvn dependency:resolve -Dclassifier=sources
```

**Gradle Dependency Analysis**
```bash
# All configurations
./gradlew dependencies > gradle-dependencies.txt

# Specific configuration
./gradlew dependencies --configuration compileClasspath

# Dependency insight for specific library
./gradlew dependencyInsight --dependency org.springframework.boot:spring-boot-starter

# Build scan for analysis
./gradlew build --scan
```

**Dependency Classification**
- **Direct dependencies**: Explicitly declared in POM/build.gradle
- **Transitive dependencies**: Required by direct dependencies
- **Provided/Compile**: Runtime classpath dependencies
- **Test dependencies**: Test scope only
- **Optional dependencies**: Conditional dependencies

### 2. Vulnerability Scanning (CVE Detection)

Check against multiple vulnerability databases:

**OWASP Dependency-Check (Maven)**
```bash
# Install and run OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# Generate report with specific format
mvn org.owasp:dependency-check-maven:check \
  -Dformat=HTML,JSON,XML \
  -DfailBuildOnCVSS=7 \
  -DsuppressionFile=owasp-suppressions.xml

# Check specific artifact
mvn org.owasp:dependency-check-maven:check \
  -Dartifact=org.springframework.boot:spring-boot-starter-web:3.2.0
```

**OWASP Dependency-Check (Gradle)**
```bash
# Apply plugin and run
./gradlew dependencyCheckAnalyze

# With custom configuration
./gradlew dependencyCheckAnalyze \
  --info \
  -PfailBuildOnCVSS=7
```

**Snyk Security Scanning**
```bash
# Test for vulnerabilities
snyk test --all-projects

# Test with Maven
snyk test --file=pom.xml

# Test with Gradle
snyk test --file=build.gradle

# Generate JSON report
snyk test --json > snyk-report.json

# Monitor project continuously
snyk monitor
```

**GitHub Advisory Database**
```bash
# Using GitHub CLI
gh api graphql -f query='
{
  securityVulnerabilities(first: 100, ecosystem: MAVEN, package: "org.springframework.boot") {
    nodes {
      advisory {
        summary
        severity
        cvss { score }
        references { url }
      }
      vulnerableVersionRange
      firstPatchedVersion { identifier }
    }
  }
}'
```

**Severity Analysis**

Categorize vulnerabilities by severity:
- **CRITICAL** (CVSS 9.0-10.0): Immediate action required
  - Remote code execution vulnerabilities
  - Authentication bypass
  - Data exposure without authentication
  
- **HIGH** (CVSS 7.0-8.9): Priority fix within days
  - Privilege escalation
  - SQL/NoSQL injection
  - Cross-site scripting (XSS)
  
- **MEDIUM** (CVSS 4.0-6.9): Fix within weeks
  - Information disclosure
  - Denial of service
  - CSRF vulnerabilities
  
- **LOW** (CVSS 0.1-3.9): Fix in regular updates
  - Minor information leakage
  - Low-impact vulnerabilities

### 3. License Compliance Analysis

Verify license compatibility and legal risks:

**License Detection (Maven)**
```bash
# Generate license report
mvn license:aggregate-third-party-report

# Download licenses
mvn license:download-licenses

# Check for specific licenses
mvn license:add-third-party \
  -Dlicense.excludedLicenses="GPL-3.0,AGPL-3.0"

# License overview
mvn project-info-reports:dependencies
```

**License Detection (Gradle)**
```bash
# Using license plugin
./gradlew downloadLicenses

# Generate license report
./gradlew generateLicenseReport

# Check license compatibility
./gradlew checkLicense
```

**License Compatibility Matrix**

Common Java dependency licenses:
- **Apache-2.0**: Permissive, compatible with most licenses
- **MIT**: Highly permissive, wide compatibility
- **BSD-3-Clause**: Permissive with attribution requirement
- **EPL-2.0**: Eclipse Public License, moderate restrictions
- **LGPL-3.0**: Lesser GPL, linking allowed
- **GPL-3.0**: Strong copyleft, requires source disclosure
- **AGPL-3.0**: Network copyleft, strongest restrictions
- **Proprietary**: Commercial license required

**Compliance Rules**
```java
// Example compatibility check
License projectLicense = License.APACHE_2_0;

Map<License, Boolean> compatibility = Map.of(
    License.MIT, true,              // ✅ Compatible
    License.APACHE_2_0, true,       // ✅ Compatible
    License.BSD_3_CLAUSE, true,     // ✅ Compatible
    License.EPL_2_0, true,          // ✅ Compatible with conditions
    License.LGPL_3_0, true,         // ✅ For linking only
    License.GPL_3_0, false,         // ❌ Incompatible (copyleft)
    License.AGPL_3_0, false,        // ❌ Incompatible (strong copyleft)
    License.UNKNOWN, false          // ⚠️ Requires review
);
```

### 4. Outdated Dependencies Analysis

Identify dependencies requiring updates:

**Maven Versions Plugin**
```bash
# Display dependency updates
mvn versions:display-dependency-updates

# Display plugin updates
mvn versions:display-plugin-updates

# Display property updates
mvn versions:display-property-updates

# Check for latest versions
mvn versions:use-latest-versions -DallowMajorUpdates=false

# Dependency updates report
mvn versions:dependency-updates-report
```

**Gradle Versions Plugin**
```bash
# Check for dependency updates
./gradlew dependencyUpdates

# Show only latest versions
./gradlew dependencyUpdates -Drevision=release

# JSON report
./gradlew dependencyUpdates -DoutputFormatter=json

# Check specific configuration
./gradlew dependencyUpdates --configuration compileClasspath
```

**Update Priority Scoring**

Calculate priority for each outdated dependency:
```
Priority Score = (Severity × 10) + (Age Factor × 5) + (Releases Behind × 2)

Where:
- Severity: Has security fix (10), Major (3), Minor (2), Patch (1)
- Age Factor: >365 days (10), >180 days (7), >90 days (4), <90 days (1)
- Releases Behind: Number of versions behind latest
```

**Maintenance Status**
- **Active**: Regular updates, active community
- **Maintenance**: Bug fixes only, no new features
- **Deprecated**: No longer maintained, find alternatives
- **Archived**: Completely abandoned, must replace
- **Unknown**: Unable to determine status

### 5. Supply Chain Security

Detect supply chain attacks and risks:

**Typosquatting Detection**
```bash
# Check for common typos of popular packages
# Example suspicious patterns:
# - org.springframework -> org.springframework-boot (legitimate)
# - org.springfranework (typo - suspicious)
# - com.google.guava -> com.google.guava-beta (check legitimacy)
```

**Common Typosquatting Patterns**
- Character substitution: `spring` → `sprimg`, `springg`
- Missing/extra characters: `commons-io` → `common-io`, `commons-ioo`
- Domain confusion: `org.apache` → `org.apachi`, `io.apache`
- Hyphen manipulation: `spring-boot` → `springboot`, `spring_boot`

**Maintainer Change Analysis**
```bash
# Check recent maintainer changes (Maven Central)
curl -s "https://search.maven.org/solrsearch/select?q=g:${GROUP_ID}+AND+a:${ARTIFACT_ID}&rows=1&wt=json" | \
  jq '.response.docs[0]'

# Verify artifact signatures
mvn verify -Dgpg.skip=false

# Check PGP signatures
gpg --verify artifact.jar.asc artifact.jar
```

**Red Flags**
- Recent ownership transfer
- Sudden version spike (e.g., 1.0.0 → 99.0.0)
- Changed artifact coordinates
- Missing or invalid signatures
- Unusual download patterns
- No source repository link
- Obfuscated or minified code

**Package Health Metrics**
```bash
# Check Maven Central metadata
curl "https://repo1.maven.org/maven2/${GROUP_PATH}/${ARTIFACT}/maven-metadata.xml"

# Verify checksums
sha1sum -c artifact.jar.sha1
md5sum -c artifact.jar.md5

# Check repository activity
gh api repos/${OWNER}/${REPO}/commits --jq 'length'
gh api repos/${OWNER}/${REPO}/issues --jq 'length'
```

### 6. Dependency Size and Performance

Analyze impact on build and runtime:

**JAR Size Analysis**
```bash
# List all JARs with sizes
find ~/.m2/repository -name "*.jar" -exec du -sh {} \; | sort -rh | head -20

# Gradle build scan
./gradlew build --scan
# Check "Dependencies" section for size breakdown

# Analyze specific dependency size
mvn dependency:tree -Dincludes=${GROUP_ID}:${ARTIFACT_ID} -Dverbose
```

**Classpath Analysis**
```bash
# Duplicate class detection
mvn dependency:analyze-duplicate

# Unused dependencies
mvn dependency:analyze

# Dependency convergence
mvn dependency:tree -Dverbose | grep "conflict"
```

### 7. Framework-Specific Audits

#### Spring Boot Dependency Audit
```bash
# Spring Boot dependency report
mvn spring-boot:build-info

# Effective POM with Spring Boot parent
mvn help:effective-pom > effective-pom.xml

# Spring Boot Actuator dependency endpoints
curl http://localhost:8080/actuator/conditions
curl http://localhost:8080/actuator/configprops
```

**Spring Boot Starters Audit**
- Verify official Spring starters (io.spring.platform)
- Check for deprecated starters
- Validate starter version compatibility
- Review auto-configuration imports

#### Hibernate/JPA Audit
```bash
# Check Hibernate version compatibility
mvn dependency:tree -Dincludes=org.hibernate:*

# JPA provider conflicts
mvn dependency:tree -Dincludes=javax.persistence:*,jakarta.persistence:*
```

#### Logging Framework Audit
```bash
# Detect logging framework conflicts
mvn dependency:tree -Dincludes=org.slf4j:*,ch.qos.logback:*,log4j:*

# Check for Log4Shell vulnerable versions
mvn dependency:tree -Dincludes=org.apache.logging.log4j:log4j-core | grep -E "2\.(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16)"
```

### 8. Automated Remediation

Generate fix scripts and pull requests:

**Maven Auto-Fix Script**
```bash
#!/bin/bash
# maven-dependency-fix.sh

echo "🔧 Maven Dependency Auto-Remediation"
echo "======================================"

# Backup current POM
cp pom.xml pom.xml.backup.$(date +%Y%m%d_%H%M%S)

# Fix critical security vulnerabilities
echo "🔒 Fixing critical vulnerabilities..."
mvn versions:use-latest-releases \
  -Dincludes=org.springframework.boot:*,org.springframework:* \
  -DallowMajorUpdates=false

# Update patch versions only (safe)
echo "📦 Updating patch versions..."
mvn versions:use-latest-releases \
  -DallowMinorUpdates=false \
  -DallowMajorUpdates=false

# Check for build success
mvn clean verify -DskipTests
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    
    # Generate dependency report
    mvn dependency:analyze-report
    mvn versions:dependency-updates-report
    
    # Commit changes
    git add pom.xml
    git commit -m "chore(deps): Security fixes and patch updates"
else
    echo "❌ Build failed, reverting changes..."
    mv pom.xml.backup.* pom.xml
fi
```

**Gradle Auto-Fix Script**
```bash
#!/bin/bash
# gradle-dependency-fix.sh

echo "🔧 Gradle Dependency Auto-Remediation"
echo "======================================"

# Backup build files
cp build.gradle build.gradle.backup.$(date +%Y%m%d_%H%M%S)
[ -f gradle/libs.versions.toml ] && cp gradle/libs.versions.toml gradle/libs.versions.toml.backup

# Update dependencies
./gradlew useLatestVersions --update-dependency-locks

# Verify build
./gradlew clean build -x test
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    
    # Generate reports
    ./gradlew dependencyUpdates
    ./gradlew dependencyCheckAnalyze
    
    # Commit changes
    git add build.gradle gradle/
    git commit -m "chore(deps): Security fixes and dependency updates"
else
    echo "❌ Build failed, reverting..."
    mv build.gradle.backup.* build.gradle
    [ -f gradle/libs.versions.toml.backup ] && mv gradle/libs.versions.toml.backup gradle/libs.versions.toml
fi
```

**Pull Request Template**
```markdown
## 🔒 Dependency Security Audit Fixes

### Summary
This PR addresses [X] security vulnerabilities and [Y] outdated dependencies identified by automated dependency audit.

### Vulnerabilities Fixed
| Dependency | CVE | Severity | Old Version | New Version |
|------------|-----|----------|-------------|-------------|
| spring-core | CVE-2024-XXXX | CRITICAL | 5.3.20 | 5.3.31 |
| jackson-databind | CVE-2024-YYYY | HIGH | 2.13.0 | 2.15.3 |

### License Compliance
- ✅ All dependencies maintain Apache-2.0 compatibility
- ✅ No new GPL/AGPL dependencies introduced
- ⚠️ Review required for: [dependency-name] (LGPL-3.0)

### Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Security scan shows no critical/high vulnerabilities
- [x] Build successful
- [x] No breaking changes detected

### Dependency Changes
```diff
- org.springframework.boot:spring-boot-starter-web:3.1.0
+ org.springframework.boot:spring-boot-starter-web:3.2.1

- com.fasterxml.jackson.core:jackson-databind:2.13.0
+ com.fasterxml.jackson.core:jackson-databind:2.15.3
```

### Risk Assessment
- **Risk Level**: LOW
- **Breaking Changes**: None identified
- **Rollback Plan**: Revert commit or merge

### Recommendations
1. Merge and deploy to staging first
2. Monitor application logs for 24h
3. Run smoke tests post-deployment
4. Schedule production deployment in maintenance window
```

### 9. Continuous Monitoring

Set up automated dependency monitoring:

**GitHub Actions Workflow**
```yaml
name: Dependency Audit

on:
  schedule:
    - cron: '0 8 * * 1'  # Weekly Monday 8 AM
  push:
    paths:
      - 'pom.xml'
      - 'build.gradle'
      - 'gradle/libs.versions.toml'
  pull_request:
  workflow_dispatch:

jobs:
  dependency-audit:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: 'maven'
    
    - name: OWASP Dependency Check
      run: |
        if [ -f pom.xml ]; then
          mvn org.owasp:dependency-check-maven:check \
            -Dformat=HTML,JSON \
            -DfailBuildOnCVSS=7
        elif [ -f build.gradle ]; then
          ./gradlew dependencyCheckAnalyze
        fi
    
    - name: Snyk Security Scan
      uses: snyk/actions/maven@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    - name: License Compliance Check
      run: |
        if [ -f pom.xml ]; then
          mvn license:aggregate-third-party-report
        fi
    
    - name: Upload Reports
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: dependency-audit-reports
        path: |
          target/dependency-check-report.html
          target/site/third-party-report.html
    
    - name: Create Issue for Critical Vulnerabilities
      if: failure()
      uses: actions/github-script@v7
      with:
        script: |
          const issue = await github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: '🚨 Critical Security Vulnerabilities Detected',
            body: 'Automated dependency audit found critical vulnerabilities. See workflow run for details.',
            labels: ['security', 'dependencies', 'critical']
          });
```

### 10. Reporting Format

Generate comprehensive audit reports:

**Executive Summary**
```markdown
# Dependency Audit Report
**Project**: [Project Name]
**Date**: 2024-01-15
**Build System**: Maven 3.9.5
**Total Dependencies**: 247 (direct: 32, transitive: 215)

## Risk Assessment
- **Overall Risk**: ⚠️ MEDIUM
- **Critical Issues**: 0
- **High Severity**: 3
- **Medium Severity**: 12
- **Low Severity**: 8

## Key Findings
1. ✅ No critical vulnerabilities
2. ⚠️ 3 high-severity CVEs requiring immediate attention
3. ✅ License compliance: All compatible with Apache-2.0
4. ⚠️ 15 dependencies outdated by >1 year
5. ⚠️ 1 dependency with maintainer change in last 30 days

## Immediate Actions Required
1. Update `jackson-databind` to 2.15.3 (CVE-2024-XXXX - HIGH)
2. Replace `commons-collections` 3.2.1 (CVE-2015-YYYY - HIGH)
3. Review `suspicious-lib` 1.0.0 (supply chain risk)
```

## Your Task

Based on the specified scope and focus, provide:

1. **Dependency Inventory Report**
   - Complete dependency tree
   - Direct vs transitive breakdown
   - Dependency classification by scope
   - Size and performance metrics

2. **Security Vulnerability Analysis**
   - CVE database cross-reference
   - Severity categorization (Critical/High/Medium/Low)
   - Exploitability assessment
   - Remediation recommendations with version updates

3. **License Compliance Report**
   - License distribution across dependencies
   - Compatibility matrix with project license
   - Legal risk assessment
   - Incompatible licenses requiring action

4. **Outdated Dependencies Report**
   - Age analysis for each dependency
   - Update priority scoring
   - Maintenance status evaluation
   - Breaking change assessment

5. **Supply Chain Security Analysis**
   - Typosquatting detection
   - Maintainer change alerts
   - Package health metrics
   - Red flag identification

6. **Automated Remediation Plan**
   - Fix scripts for Maven/Gradle
   - Pull request generation
   - Rollback procedures
   - Testing strategy

7. **Continuous Monitoring Setup**
   - CI/CD integration workflows
   - Automated alert configuration
   - Scheduled audit frequency
   - Notification channels

Focus on **actionable insights** that enable teams to maintain secure, compliant, and efficient dependency management for Java enterprise applications.
