# Input Validation Patterns

## Zod Schema Validation

```typescript
import { z } from 'zod';

// Comprehensive user creation schema
const createUserSchema = z.object({
  name: z.string().min(1).max(100).trim(),
  email: z.string().email().max(254).toLowerCase(),
  password: z.string()
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[a-z]/, 'Must contain lowercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  role: z.enum(['user', 'editor']).default('user'),
});

// API endpoint with validation
app.post('/api/users', async (req, res) => {
  const result = createUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }
  const user = await createUser(result.data);
  res.status(201).json(user);
});
```

## NestJS Validation with class-validator

```typescript
import { IsEmail, IsString, MinLength, Matches, IsEnum } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(1)
  @MaxLength(100)
  name: string;

  @IsEmail()
  @MaxLength(254)
  email: string;

  @IsString()
  @MinLength(12)
  @Matches(/[A-Z]/, { message: 'Must contain uppercase letter' })
  @Matches(/[a-z]/, { message: 'Must contain lowercase letter' })
  @Matches(/[0-9]/, { message: 'Must contain a number' })
  password: string;

  @IsEnum(['user', 'editor'])
  role?: 'user' | 'editor';
}
```

## Validation Error Handling

```typescript
// Consistent error response format
interface ValidationError {
  field: string;
  message: string;
}

function handleValidation(errors: ZodError): ValidationError[] {
  return errors.errors.map(err => ({
    field: err.path.join('.'),
    message: err.message,
  }));
}

// Return structured 400 response
res.status(400).json({
  error: 'Validation failed',
  details: handleValidation(result.error),
});
```
