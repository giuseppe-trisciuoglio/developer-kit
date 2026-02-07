# Template Systems Architecture

This reference provides comprehensive frameworks for building modular, reusable prompt templates with variable interpolation, conditional sections, and hierarchical composition.

## Template Design Principles

### Modularity and Reusability
- **Single Responsibility**: Each template handles one specific type of task
- **Composability**: Templates can be combined to create complex prompts
- **Parameterization**: Variables allow customization without core changes
- **Inheritance**: Base templates can be extended for specific use cases

### Clear Variable Naming Conventions
```
{user_input}           - Direct input from user
{context}             - Background information
{examples}            - Few-shot learning examples
{constraints}         - Task limitations and requirements
{output_format}       - Desired output structure
{role}                - AI role or persona
{expertise_level}     - Level of expertise for the role
{domain}              - Specific domain or field
{difficulty}          - Task complexity level
{language}            - Output language specification
```

## Core Template Components

### 1. Base Template Structure
```
# Template: Universal Task Framework
# Purpose: Base template for most task types
# Variables: {role}, {task_description}, {context}, {examples}, {output_format}

## System Instructions
You are a {role} with {expertise_level} expertise in {domain}.

## Context Information
{if context}
Background and relevant context:
{context}
{endif}

## Task Description
{task_description}

## Examples
{if examples}
Here are some examples to guide your response:

{examples}
{endif}

## Output Requirements
{output_format}

## Constraints and Guidelines
{constraints}

## User Input
{user_input}
```

### 2. Conditional Sections Framework
```python
def process_conditional_template(template, variables):
    """
    Process template with conditional sections.
    """
    # Process if/endif blocks
    while '{if ' in template:
        start = template.find('{if ')
        end_condition = template.find('}', start)
        condition = template[start+4:end_condition].strip()

        start_endif = template.find('{endif}', end_condition)
        if_content = template[end_condition+1:start_endif].strip()

        # Evaluate condition
        if evaluate_condition(condition, variables):
            template = template[:start] + if_content + template[start_endif+6:]
        else:
            template = template[:start] + template[start_endif+6:]

    # Replace variables
    for key, value in variables.items():
        template = template.replace(f'{{{key}}}', str(value))

    return template
```

### 3. Variable Interpolation System
```python
class TemplateEngine:
    def __init__(self):
        self.variables = {}
        self.functions = {
            'upper': str.upper,
            'lower': str.lower,
            'capitalize': str.capitalize,
            'pluralize': self.pluralize,
            'format_date': self.format_date,
            'truncate': self.truncate
        }

    def set_variable(self, name, value):
        """Set a template variable."""
        self.variables[name] = value

    def render(self, template):
        """Render template with variable substitution."""
        # Process function calls {variable|function}
        template = self.process_functions(template)

        # Replace variables
        for key, value in self.variables.items():
            template = template.replace(f'{{{key}}}', str(value))

        return template

    def process_functions(self, template):
        """Process template functions."""
        import re
        pattern = r'\{(\w+)\|(\w+)\}'

        def replace_function(match):
            var_name, func_name = match.groups()
            value = self.variables.get(var_name, '')
            if func_name in self.functions:
                return self.functions[func_name](str(value))
            return value

        return re.sub(pattern, replace_function, template)
```

## Specialized Template Types

### 1. Classification Template
```
# Template: Multi-Class Classification
# Purpose: Classify inputs into predefined categories
# Required Variables: {input_text}, {categories}, {role}

## Classification Framework
You are a {role} specializing in accurate text classification.

## Classification Categories
{categories}

## Classification Process
1. Analyze the input text carefully
2. Identify key indicators and features
3. Match against category definitions
4. Select the most appropriate category
5. Provide confidence score

## Input to Classify
{input_text}

## Output Format
```json
{{
  "category": "selected_category",
  "confidence": 0.95,
  "reasoning": "Brief explanation of classification logic",
  "key_indicators": ["indicator1", "indicator2"]
}}
```
```

### 2. Transformation Template
```
# Template: Text Transformation
# Purpose: Transform text from one format/style to another
# Required Variables: {source_text}, {target_format}, {transformation_rules}

## Transformation Task
Transform the given {source_format} text into {target_format} following these rules:
{transformation_rules}

## Source Text
{source_text}

## Transformation Process
1. Analyze the structure and content of the source text
2. Apply the specified transformation rules
3. Maintain the core meaning and intent
4. Ensure proper {target_format} formatting
5. Verify completeness and accuracy

## Transformed Output
```

### 3. Generation Template
```
# Template: Creative Generation
# Purpose: Generate creative content based on specifications
# Required Variables: {content_type}, {specifications}, {style_guidelines}

## Creative Generation Task
Generate {content_type} that meets the following specifications:

## Content Specifications
{specifications}

## Style Guidelines
{style_guidelines}

## Quality Requirements
- Originality and creativity
- Adherence to specifications
- Appropriate tone and style
- Clear structure and coherence
- Audience-appropriate language

## Generated Content
```

### 4. Analysis Template
```
# Template: Comprehensive Analysis
# Purpose: Perform detailed analysis of given input
# Required Variables: {input_data}, {analysis_framework}, {focus_areas}

## Analysis Framework
You are an expert analyst with deep expertise in {domain}.

## Analysis Scope
Focus on these key areas:
{focus_areas}

## Analysis Methodology
{analysis_framework}

## Input Data for Analysis
{input_data}

## Analysis Process
1. Initial assessment and context understanding
2. Detailed examination of each focus area
3. Pattern and trend identification
4. Comparative analysis with benchmarks
5. Insight generation and recommendation formulation

## Analysis Output Structure
```yaml
executive_summary:
  key_findings: []
  overall_assessment: ""

detailed_analysis:
  {focus_area_1}:
    observations: []
    patterns: []
    insights: []
  {focus_area_2}:
    observations: []
    patterns: []
    insights: []

recommendations:
  immediate: []
  short_term: []
  long_term: []
```

## Advanced Template Patterns

### 1. Hierarchical Template Composition
```python
class HierarchicalTemplate:
    def __init__(self, name, content, parent=None):
        self.name = name
        self.content = content
        self.parent = parent
        self.children = []
        self.variables = {}

    def add_child(self, child_template):
        """Add a child template."""
        child_template.parent = self
        self.children.append(child_template)

    def render(self, variables=None):
        """Render template with inherited variables."""
        # Combine variables from parent hierarchy
        combined_vars = {}

        # Collect variables from parents
        current = self.parent
        while current:
            combined_vars.update(current.variables)
            current = current.parent

        # Add current variables
        combined_vars.update(self.variables)

        # Override with provided variables
        if variables:
            combined_vars.update(variables)

        # Render content
        rendered_content = self.render_content(self.content, combined_vars)

        # Render children
        for child in self.children:
            child_rendered = child.render(combined_vars)
            rendered_content = rendered_content.replace(
                f'{{child:{child.name}}}', child_rendered
            )

        return rendered_content
```

### 2. Role-Based Template System
```python
class RoleBasedTemplate:
    def __init__(self):
        self.roles = {
            'analyst': {
                'persona': 'You are a professional analyst with expertise in data interpretation and pattern recognition.',
                'approach': 'systematic',
                'output_style': 'detailed and evidence-based',
                'verification': 'Always cross-check findings and cite sources'
            },
            'creative_writer': {
                'persona': 'You are a creative writer with a talent for engaging storytelling and vivid descriptions.',
                'approach': 'imaginative',
                'output_style': 'descriptive and engaging',
                'verification': 'Ensure narrative consistency and flow'
            },
            'technical_expert': {
                'persona': 'You are a technical expert with deep knowledge of {domain} and practical implementation experience.',
                'approach': 'methodical',
                'output_style': 'precise and technical',
                'verification': 'Include technical accuracy and best practices'
            }
        }

    def create_prompt(self, role, task, domain=None):
        """Create role-specific prompt template."""
        role_config = self.roles.get(role, self.roles['analyst'])

        template = f"""
## Role Definition
{role_config['persona']}

## Approach
Use a {role_config['approach']} approach to this task.

## Task
{task}

## Output Style
{role_config['output_style']}

## Verification
{role_config['verification']}
"""

        if domain and '{domain}' in role_config['persona']:
            template = template.replace('{domain}', domain)

        return template
```

### 3. Dynamic Template Selection
```python
class DynamicTemplateSelector:
    def __init__(self):
        self.templates = {}
        self.selection_rules = {}

    def register_template(self, name, template, selection_criteria):
        """Register a template with selection criteria."""
        self.templates[name] = template
        self.selection_rules[name] = selection_criteria

    def select_template(self, task_characteristics):
        """Select the most appropriate template based on task characteristics."""
        best_template = None
        best_score = 0

        for name, criteria in self.selection_rules.items():
            score = self.calculate_match_score(task_characteristics, criteria)
            if score > best_score:
                best_score = score
                best_template = name

        return self.templates[best_template] if best_template else None

    def calculate_match_score(self, task_characteristics, criteria):
        """Calculate how well task matches template criteria."""
        score = 0
        total_weight = 0

        for characteristic, weight in criteria.items():
            if characteristic in task_characteristics:
                if task_characteristics[characteristic] == weight['value']:
                    score += weight['weight']
                total_weight += weight['weight']

        return score / total_weight if total_weight > 0 else 0
```

## Template Implementation Examples

### Example 1: Customer Service Template
```python
customer_service_template = """
# Customer Service Response Template

## Role Definition
You are a {customer_service_role} with {experience_level} of customer service experience in {industry}.

## Context
{if customer_history}
Customer History:
{customer_history}
{endif}

{if issue_context}
Issue Context:
{issue_context}
{endif}

## Response Guidelines
- Maintain {tone} tone throughout
- Address all aspects of the customer's inquiry
- Provide {level_of_detail} explanation
- Include {additional_elements}
- Follow company {communication_style} style

## Customer Inquiry
{customer_inquiry}

## Response Structure
1. Greeting and acknowledgment
2. Understanding and empathy
3. Solution or explanation
4. Additional assistance offered
5. Professional closing

## Response
"""
```

### Example 2: Technical Documentation Template
```python
documentation_template = """
# Technical Documentation Generator

## Role Definition
You are a {technical_writer_role} specializing in {technology} documentation with {experience_level} of experience.

## Documentation Standards
- Target audience: {audience_level}
- Technical depth: {technical_depth}
- Include examples: {include_examples}
- Add troubleshooting: {add_troubleshooting}
- Version: {version}

## Content to Document
{content_to_document}

## Documentation Structure
```markdown
# {title}

## Overview
{overview}

## Prerequisites
{prerequisites}

## {main_sections}

## Examples
{if include_examples}
{examples}
{endif}

## Troubleshooting
{if add_troubleshooting}
{troubleshooting}
{endif}

## Additional Resources
{additional_resources}
```

## Generated Documentation
"""
```

## Template Management System

### Version Control Integration
```python
class TemplateVersionManager:
    def __init__(self):
        self.versions = {}
        self.current_versions = {}

    def create_version(self, template_name, template_content, author, description):
        """Create a new version of a template."""
        import datetime
        import hashlib

        version_id = hashlib.md5(template_content.encode()).hexdigest()[:8]
        timestamp = datetime.datetime.now().isoformat()

        version_info = {
            'version_id': version_id,
            'content': template_content,
            'author': author,
            'description': description,
            'timestamp': timestamp,
            'parent_version': self.current_versions.get(template_name)
        }

        if template_name not in self.versions:
            self.versions[template_name] = []

        self.versions[template_name].append(version_info)
        self.current_versions[template_name] = version_id

        return version_id

    def rollback(self, template_name, version_id):
        """Rollback to a specific version."""
        if template_name in self.versions:
            for version in self.versions[template_name]:
                if version['version_id'] == version_id:
                    self.current_versions[template_name] = version_id
                    return version['content']
        return None
```

### Performance Monitoring
```python
class TemplatePerformanceMonitor:
    def __init__(self):
        self.usage_stats = {}
        self.performance_metrics = {}

    def track_usage(self, template_name, execution_time, success):
        """Track template usage and performance."""
        if template_name not in self.usage_stats:
            self.usage_stats[template_name] = {
                'usage_count': 0,
                'total_time': 0,
                'success_count': 0,
                'failure_count': 0
            }

        stats = self.usage_stats[template_name]
        stats['usage_count'] += 1
        stats['total_time'] += execution_time

        if success:
            stats['success_count'] += 1
        else:
            stats['failure_count'] += 1

    def get_performance_report(self, template_name):
        """Generate performance report for a template."""
        if template_name not in self.usage_stats:
            return None

        stats = self.usage_stats[template_name]
        avg_time = stats['total_time'] / stats['usage_count']
        success_rate = stats['success_count'] / stats['usage_count']

        return {
            'template_name': template_name,
            'total_usage': stats['usage_count'],
            'average_execution_time': avg_time,
            'success_rate': success_rate,
            'failure_rate': 1 - success_rate
        }
```

## Best Practices

### Template Quality Guidelines
- **Clear Documentation**: Include purpose, variables, and usage examples
- **Consistent Naming**: Use standardized variable naming conventions
- **Error Handling**: Include fallback mechanisms for missing variables
- **Performance Optimization**: Minimize template complexity and rendering time
- **Testing**: Implement comprehensive template testing frameworks

### Security Considerations
- **Input Validation**: Sanitize all template variables
- **Injection Prevention**: Prevent code injection in template rendering
- **Access Control**: Implement proper authorization for template modifications
- **Audit Trail**: Track template changes and usage

This comprehensive template system architecture provides the foundation for building scalable, maintainable prompt templates that can be efficiently managed and optimized across diverse use cases.