# Advanced Zod v4 Patterns

Advanced validation patterns using Zod v4 for complex use cases.

## Discriminated Union with Metadata

```ts
import { z } from "zod";

const EventSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("user_created"),
    userId: z.string().uuid(),
    email: z.email(),
    createdAt: z.coerce.date(),
  }),
  z.object({
    type: z.literal("user_deleted"),
    userId: z.string().uuid(),
    reason: z.string().optional(),
  }),
  z.object({
    type: z.literal("subscription_upgraded"),
    userId: z.string().uuid(),
    previousPlan: z.enum(["free", "pro", "enterprise"]),
    newPlan: z.enum(["pro", "enterprise"]),
    effectiveAt: z.coerce.date(),
  }),
]);

type Event = z.infer<typeof EventSchema>;

function handleEvent(event: Event) {
  switch (event.type) {
    case "user_created":
      return sendWelcomeEmail(event.email);
    case "user_deleted":
      return cleanupUserData(event.userId);
    case "subscription_upgraded":
      return applyPlanFeatures(event.userId, event.newPlan);
  }
}
```

## Recursive Schema (Tree Structure)

```ts
import { z } from "zod";

export const TreeNodeSchema: z.ZodType<{ id: string; children: TreeNode[] }> = z
  .object({
    id: z.string(),
    children: z.lazy(() => z.array(TreeNodeSchema)).default([]),
  })
  .strict();

type TreeNode = z.infer<typeof TreeNodeSchema>;
```

## Map and Set Validation

```ts
import { z } from "zod";

export const StringRecordSchema = z.record(z.string());
export const UserMapSchema = z.map(z.string(), z.object({
  id: z.string(),
  name: z.string(),
}));

export const UniqueTagsSchema = z.set(z.string().min(1).max(20)).max(10);
```

## Conditional Schema (or and union)

```ts
import { z } from "zod";

export const PricingSchema = z.union([
  z.object({ type: z.literal("fixed"), amount: z.number().positive() }),
  z.object({ type: z.literal("tiered"), tiers: z.array(z.object({
    minQty: z.number().int().nonnegative(),
    pricePerUnit: z.number().positive(),
  })) }),
]);

export const AdvancedSearchSchema = z.object({
  query: z.string().optional(),
  filters: z.object({
    status: z.enum(["active", "archived", "all"]).default("all"),
    dateRange: z.object({
      from: z.coerce.date(),
      to: z.coerce.date(),
    }).optional(),
  }).optional(),
});
```

## Async Validation (for database checks)

```ts
import { z } from "zod";

export const UniqueUsernameSchema = z.string()
  .min(3)
  .max(20)
  .regex(/^[a-zA-Z0-9_]+$/)
  .refine(async (username) => {
    const exists = await db.user.findUnique({ where: { username } });
    return !exists;
  }, { error: "Username already taken" });
```

## Pipeline Schema (Zod v4 functional pipe)

```ts
import { z } from "zod";

export const UsernamePipelineSchema = z
  .string()
  .trim()
  .toLowerCase()
  .min(3)
  .max(20)
  .regex(/^[a-z0-9_]+$/);

export const SlugSchema = z
  .string()
  .transform((v) => v.toLowerCase().replace(/\s+/g, "-"))
  .pipe(z.string().regex(/^[a-z0-9-]+$/));
```
