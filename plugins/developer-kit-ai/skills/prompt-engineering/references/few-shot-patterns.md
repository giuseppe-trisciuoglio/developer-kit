# Few-Shot Learning Patterns

This reference provides comprehensive frameworks for implementing effective few-shot learning strategies that maximize model performance within context window constraints.

## Core Principles

### Example Selection Strategy

#### Semantic Similarity Selection
- Use embedding similarity to find examples closest to target input
- Cluster similar examples to avoid redundancy
- Select diverse representatives from different semantic regions
- Prioritize examples that cover key variations in problem space

#### Diversity Sampling Approach
- Ensure coverage of different input types and patterns
- Include boundary cases and edge conditions
- Balance simple and complex examples
- Select examples that demonstrate different solution strategies

#### Progressive Complexity Ordering
- Start with simplest, most straightforward examples
- Progress to increasingly complex scenarios
- Include challenging edge cases last
- Use this ordering to build understanding incrementally

## Example Templates

### Classification Tasks

#### Binary Classification Template
```
Classify if the text expresses positive or negative sentiment.

Example 1:
Text: "I love this product! It works exactly as advertised and exceeded my expectations."
Sentiment: Positive
Reasoning: Contains enthusiastic language, positive adjectives, and satisfaction indicators

Example 2:
Text: "The customer service was terrible and the product broke after one day of use."
Sentiment: Negative
Reasoning: Contains negative adjectives, complaint language, and dissatisfaction indicators

Example 3:
Text: "It's okay, nothing special but does the basic job."
Sentiment: Negative
Reasoning: Contains lukewarm language, lack of enthusiasm, minimal positive elements

Now classify:
Text: {input_text}
Sentiment:
Reasoning:
```

#### Multi-Class Classification Template
```
Categorize the customer inquiry into one of: Technical Support, Billing, Sales, or General.

Example 1:
Inquiry: "My account was charged twice for the same subscription this month"
Category: Billing
Key indicators: "charged twice", "subscription", "account", financial terms

Example 2:
Inquiry: "The app keeps crashing when I try to upload files larger than 10MB"
Category: Technical Support
Key indicators: "crashing", "upload files", "technical issue", "error report"

Example 3:
Inquiry: "What are your pricing plans for enterprise customers?"
Category: Sales
Key indicators: "pricing plans", "enterprise", business inquiry, sales question

Now categorize:
Inquiry: {inquiry_text}
Category:
Key indicators:
```

### Transformation Tasks

#### Text Transformation Template
```
Convert formal business text into casual, friendly language.

Example 1:
Formal: "We regret to inform you that your request cannot be processed at this time due to insufficient documentation."
Casual: "Sorry, but we can't process your request right now because some documents are missing."

Example 2:
Formal: "The aforementioned individual has demonstrated exceptional proficiency in the designated responsibilities."
Casual: "They've done a great job with their tasks and really know what they're doing."

Example 3:
Formal: "Please be advised that the scheduled meeting has been postponed pending further notice."
Casual: "Hey, just letting you know that we've put off the meeting for now and will let you know when it's rescheduled."

Now convert:
Formal: {formal_text}
Casual:
```

#### Data Extraction Template
```
Extract key information from the job posting into structured format.

Example 1:
Job Posting: "We are seeking a Senior Software Engineer with 5+ years of experience in Python and cloud technologies. This is a remote position offering $120k-$150k salary plus equity."

Extracted:
- Position: Senior Software Engineer
- Experience Required: 5+ years
- Skills: Python, cloud technologies
- Location: Remote
- Salary: $120k-$150k plus equity

Example 2:
Job Posting: "Marketing Manager needed for growing startup. Must have 3 years experience in digital marketing, social media management, and content creation. San Francisco office, competitive compensation."

Extracted:
- Position: Marketing Manager
- Experience Required: 3 years
- Skills: Digital marketing, social media management, content creation
- Location: San Francisco
- Salary: Competitive compensation

Now extract:
Job Posting: {job_posting_text}
Extracted:
```

### Generation Tasks

#### Creative Writing Template
```
Generate compelling product descriptions following the shown patterns.

Example 1:
Product: Wireless headphones with noise cancellation
Description: "Immerse yourself in crystal-clear audio with our premium wireless headphones. Advanced noise cancellation technology blocks out distractions while 30-hour battery life keeps you connected all day long."

Example 2:
Product: Smart home security camera
Description: "Protect what matters most with intelligent monitoring that alerts you to activity instantly. AI-powered detection distinguishes between people, pets, and vehicles for truly smart security."

Example 3:
Product: Portable espresso maker
Description: "Barista-quality espresso anywhere, anytime. Compact design meets professional-grade extraction in this revolutionary portable machine that delivers perfect shots in under 30 seconds."

Now generate:
Product: {product_description}
Description:
```

### Error Correction Patterns

#### Error Detection and Correction Template
```
Identify and correct errors in the given text.

Example 1:
Text with errors: "Their going to the park to play there new game with they're friends."
Correction: "They're going to the park to play their new game with their friends."
Errors fixed: "Their → They're", "there → their", "they're → their"

Example 2:
Text with errors: "The company's new policy effects every employee and there morale."
Correction: "The company's new policy affects every employee and their morale."
Errors fixed: "effects → affects", "there → their"

Example 3:
Text with errors: "Its important to review you're work carefully before submiting."
Correction: "It's important to review your work carefully before submitting."
Errors fixed: "Its → It's", "you're → your", "submiting → submitting"

Now correct:
Text with errors: {text_with_errors}
Correction:
Errors fixed:
```

## Advanced Strategies

### Dynamic Example Selection

#### Context-Aware Selection
```python
def select_examples(input_text, example_database, max_examples=3):
    """
    Select most relevant examples based on semantic similarity and diversity.
    """
    # 1. Calculate similarity scores
    similarities = calculate_similarity(input_text, example_database)

    # 2. Sort by similarity
    sorted_examples = sort_by_similarity(similarities)

    # 3. Apply diversity sampling
    diverse_examples = diversity_sampling(sorted_examples, max_examples)

    # 4. Order by complexity
    final_examples = order_by_complexity(diverse_examples)

    return final_examples
```

#### Adaptive Example Count
```python
def determine_example_count(input_complexity, context_limit):
    """
    Adjust example count based on input complexity and available context.
    """
    base_count = 3

    # Complex inputs benefit from more examples
    if input_complexity > 0.8:
        return min(base_count + 2, context_limit)
    elif input_complexity > 0.5:
        return base_count + 1
    else:
        return max(base_count - 1, 2)
```

### Quality Metrics for Examples

#### Example Effectiveness Scoring
```python
def score_example_effectiveness(example, test_cases):
    """
    Score how effectively an example teaches the desired pattern.
    """
    metrics = {
        'coverage': measure_pattern_coverage(example),
        'clarity': measure_instructional_clarity(example),
        'uniqueness': measure_uniqueness_from_other_examples(example),
        'difficulty': measure_appropriateness_difficulty(example)
    }

    return weighted_average(metrics, weights=[0.3, 0.3, 0.2, 0.2])
```

## Best Practices

### Example Quality Guidelines
- **Clarity**: Examples should clearly demonstrate the desired pattern
- **Accuracy**: Input-output pairs must be correct and consistent
- **Relevance**: Examples should be representative of target task
- **Diversity**: Include variation in input types and complexity levels
- **Completeness**: Cover edge cases and boundary conditions

### Context Management
- **Token Efficiency**: Optimize example length while maintaining clarity
- **Progressive Disclosure**: Start simple, increase complexity gradually
- **Redundancy Elimination**: Remove overlapping or duplicate examples
- **Compression**: Use concise representations where possible

### Common Pitfalls to Avoid
- **Overfitting**: Don't include too many examples from same pattern
- **Under-representation**: Ensure coverage of important variations
- **Ambiguity**: Examples should have clear, unambiguous solutions
- **Context Overflow**: Balance example count with window limitations
- **Poor Ordering**: Place examples in logical progression order

## Integration with Other Patterns

Few-shot learning combines effectively with:
- **Chain-of-Thought**: Add reasoning steps to examples
- **Template Systems**: Use few-shot within structured templates
- **Prompt Optimization**: Test different example selections
- **System Prompts**: Establish few-shot learning expectations in system prompts

This framework provides the foundation for implementing effective few-shot learning across diverse tasks and model types.