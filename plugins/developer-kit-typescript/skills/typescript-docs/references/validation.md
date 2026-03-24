# Documentation Validation

## TypeDoc Plugin for Validation

```typescript
// typedoc-plugin-validation.js
export function load(app) {
  app.converter.on(
    Converter.EVENT_CREATE_SIGNATURE,
    (context, reflection, node?) => {
      // Check if method has JSDoc
      if (reflection.kind === ReflectionKind.Method) {
        const comment = reflection.comment;
        if (!comment) {
          app.logger.warn(
            `Method ${reflection.name} lacks documentation in ${reflection.parent.name}`
          );
        }
      }
    }
  );
}
```

## ESLint Rules for Documentation

```json
{
  "rules": {
    "jsdoc/require-description": "error",
    "jsdoc/require-param-description": "error",
    "jsdoc/require-returns-description": "error",
    "jsdoc/require-example": "warn",
    "jsdoc/check-alignment": "error",
    "jsdoc/check-indentation": "error",
    "jsdoc/tag-lines": ["error", "any", { "startLines": 1 }]
  }
}
```

## Validation Checklist

- [ ] All public methods have JSDoc comments
- [ ] All parameters have `@param` descriptions
- [ ] All return values have `@returns` descriptions
- [ ] Complex functions have `@example` blocks
- [ ] All `@throws` documented for error scenarios
- [ ] Cross-references use `@see` tags
- [ ] ESLint JSDoc rules pass
