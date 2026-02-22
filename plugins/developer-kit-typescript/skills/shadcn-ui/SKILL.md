---
name: shadcn-ui
description: Provides complete shadcn/ui component library patterns including installation, configuration, and implementation of accessible React components. Use when setting up shadcn/ui, installing components, building forms with React Hook Form and Zod, customizing themes with Tailwind CSS, or implementing UI patterns like buttons, dialogs, dropdowns, tables, and complex form layouts.
allowed-tools: Read, Write, Bash, Edit, Glob
category: frontend
tags: [shadcn-ui, react, tailwind, radix-ui, forms, accessibility]
---

# shadcn/ui Component Patterns

## Overview

Expert guide for building accessible, customizable UI components with shadcn/ui, Radix UI, and Tailwind CSS. shadcn/ui is NOT an NPM package - it's a collection of reusable components copied into your project that you own and customize.

## When to Use

- Setting up a new project with shadcn/ui
- Installing or configuring individual components
- Building forms with React Hook Form and Zod validation
- Creating accessible UI components (buttons, dialogs, dropdowns, sheets)
- Customizing component styling with Tailwind CSS
- Implementing design systems with shadcn/ui
- Building Next.js applications with TypeScript

## Instructions

1. **Initialize Project**: Run `npx shadcn@latest init` to configure shadcn/ui
2. **Install Components**: Add components with `npx shadcn@latest add <component>`
3. **Configure Theme**: Customize CSS variables in globals.css for theming
4. **Import Components**: Use components from `@/components/ui/` directory
5. **Customize as Needed**: Modify component code directly in your project
6. **Add Form Validation**: Integrate React Hook Form with Zod schemas
7. **Test Accessibility**: Verify ARIA attributes and keyboard navigation

## Quick Start

```bash
# Create Next.js project with shadcn/ui
npx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app
npx shadcn@latest init

# Install essential components
npx shadcn@latest add button input form card dialog select

# For existing projects
npm install tailwindcss-animate class-variance-authority clsx tailwind-merge lucide-react
npx shadcn@latest init
```

## Examples

### Complete Form with Validation

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "" },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-4">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl><Input type="email" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="password" render={({ field }) => (
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl><Input type="password" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Login</Button>
      </form>
    </Form>
  )
}
```

## Constraints and Warnings

- **Not an NPM Package**: Components are copied to your project; you own the code
- **Client Components**: Most components require "use client" directive
- **Radix Dependencies**: Ensure all @radix-ui packages are installed
- **Tailwind Required**: Components rely on Tailwind CSS utilities
- **TypeScript**: Designed for TypeScript projects; type definitions included
- **Path Aliases**: Configure @ alias in tsconfig.json for imports
- **Dark Mode**: Set up dark mode with CSS variables or class strategy

## Best Practices

1. **Accessibility**: Components use Radix UI primitives for ARIA compliance
2. **Customization**: Modify components directly in your codebase
3. **Type Safety**: Use TypeScript for type-safe props and state
4. **Validation**: Use Zod schemas for form validation
5. **Styling**: Leverage Tailwind utilities and CSS variables
6. **Consistency**: Use the same component patterns across your app

## References

Consult these files for detailed patterns and examples:

- **[references/components.md](references/components.md)** - All component examples (Button, Input, Card, Dialog, Sheet, Select, Table, Toast, Menubar)
- **[references/charts.md](references/charts.md)** - Chart components with Recharts (Bar, Line, Area, Pie charts with ChartConfig)
- **[references/configuration.md](references/configuration.md)** - Project setup, Tailwind config, CSS variables, TSConfig, dependencies
- **[references/patterns.md](references/patterns.md)** - Next.js integration, Server/Client Components, forms with Server Actions, customization patterns
- **[references/learn.md](references/learn.md)** - Additional learning resources
- **[references/official-ui-reference.md](references/official-ui-reference.md)** - Official UI reference
- **[references/ui-reference.md](references/ui-reference.md)** - UI reference details

### External References

- Official Docs: https://ui.shadcn.com
- Radix UI: https://www.radix-ui.com
- React Hook Form: https://react-hook-form.com
- Zod: https://zod.dev
- Tailwind CSS: https://tailwindcss.com
