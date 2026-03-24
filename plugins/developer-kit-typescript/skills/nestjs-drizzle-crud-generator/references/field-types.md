# Supported Field Types

## Field Type Mapping

| Type | Drizzle Column | Zod Schema |
|------|---------------|------------|
| string | text | z.string() |
| text | text | z.string() |
| number | real | z.number() |
| integer | integer | z.number().int() |
| boolean | boolean | z.boolean() |
| date | timestamp | z.date() |
| uuid | uuid | z.string().uuid() |
| email | text | z.string().email() |

## Field Options

Each field definition supports these properties:

| Property | Type | Description |
|----------|------|-------------|
| name | string | Field name (camelCase recommended) |
| type | string | Data type from the table above |
| required | boolean | Whether the field is mandatory |
| default | any | Default value for optional fields |
| maxLength | number | Maximum length for string/text fields |
| minLength | number | Minimum length for string/text fields |

## Example Field Definitions

```json
[
  {"name": "name", "type": "string", "required": true},
  {"name": "email", "type": "email", "required": true},
  {"name": "age", "type": "integer", "required": false},
  {"name": "isActive", "type": "boolean", "required": false, "default": true},
  {"name": "price", "type": "number", "required": true},
  {"name": "bio", "type": "text", "required": false},
  {"name": "userId", "type": "uuid", "required": false}
]
```
