# AWS Lambda PHP Examples

Complete examples for implementing AWS Lambda with PHP and Symfony.

## Example 1: Create a Symfony Lambda API

**Input:**
```
Create a Symfony Lambda REST API using Bref for a todo application
```

**Process:**
1. Initialize Symfony project with `composer create-project`
2. Install Bref: `composer require bref/bref`
3. Configure serverless.yml
4. Set up routes in config/routes.yaml
5. Configure deployment with `vendor/bin/bref deploy`

**Output:**
- Complete Symfony project structure
- REST API with CRUD endpoints
- DynamoDB integration
- Deployment configuration

## Example 2: Optimize Cold Start for Symfony

**Input:**
```
My Symfony Lambda has 5 second cold start, how do I optimize it?
```

**Process:**
1. Analyze services loaded at startup
2. Disable unused Symfony features (validation, annotations)
3. Use lazy loading for heavy services
4. Optimize composer autoload
5. Consider using raw PHP if full framework not needed

**Output:**
- Refactored Symfony configuration
- Optimized cold start < 2s
- Service analysis report

## Example 3: Deploy with GitHub Actions

**Input:**
```
Configure CI/CD for Symfony Lambda with Serverless Framework
```

**Process:**
1. Create GitHub Actions workflow
2. Set up PHP environment with composer
3. Run PHPUnit tests
4. Deploy with Serverless Framework
5. Configure environment protection for prod

**Output:**
- Complete .github/workflows/deploy.yml
- Multi-stage pipeline
- Integrated test automation
