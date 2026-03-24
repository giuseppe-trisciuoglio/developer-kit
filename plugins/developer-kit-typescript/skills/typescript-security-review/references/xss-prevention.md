# XSS Prevention Patterns

## React Components

### Vulnerable: dangerouslySetInnerHTML without sanitization

```tsx
function Comment({ content }: { content: string }) {
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
}
```

### Secure: DOMPurify sanitization

```tsx
import DOMPurify from 'isomorphic-dompurify';

function Comment({ content }: { content: string }) {
  const sanitized = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### Better: Markdown renderer instead of raw HTML

```tsx
import ReactMarkdown from 'react-markdown';

function Comment({ content }: { content: string }) {
  return <ReactMarkdown>{content}</ReactMarkdown>;
}
```

## Server-Side Template Engines

```typescript
// Vulnerable: Template injection
const template = `Hello ${userInput}`; // User input directly in template

// Secure: Use template engines with auto-escaping
import Handlebars from 'handlebars';

const safeTemplate = Handlebars.compile('Hello {{name}}');
const result = safeTemplate({ name: userInput }); // Auto-escaped
```
