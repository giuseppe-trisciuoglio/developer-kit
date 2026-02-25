# Wrapping shadcn/ui Components as Design System Primitives

This guide shows how to wrap shadcn/ui components into design system primitives that enforce token usage and provide consistent API.

## Button Component

```tsx
// components/ds/Button.tsx
import { Button as ShadcnButton, type ButtonProps } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type DSButtonVariant = "primary" | "secondary" | "destructive" | "ghost" | "outline";
type DSButtonSize = "sm" | "md" | "lg";

interface DSButtonProps extends Omit<ButtonProps, "variant" | "size"> {
  variant?: DSButtonVariant;
  size?: DSButtonSize;
}

const variantMap: Record<DSButtonVariant, ButtonProps["variant"]> = {
  primary: "default",
  secondary: "secondary",
  destructive: "destructive",
  ghost: "ghost",
  outline: "outline",
};

const sizeMap: Record<DSButtonSize, ButtonProps["size"]> = {
  sm: "sm",
  md: "default",
  lg: "lg",
};

export function Button({ variant = "primary", size = "md", className, ...props }: DSButtonProps) {
  return (
    <ShadcnButton
      variant={variantMap[variant]}
      size={sizeMap[size]}
      className={cn("font-medium transition-colors", className)}
      {...props}
    />
  );
}
```

## Typography Component

```tsx
// components/ds/Text.tsx
import { cn } from "@/lib/utils";

type TextVariant = "h1" | "h2" | "h3" | "h4" | "body" | "body-sm" | "caption" | "overline";

interface TextProps {
  variant?: TextVariant;
  as?: keyof JSX.IntrinsicElements;
  className?: string;
  children: React.ReactNode;
}

const variantStyles: Record<TextVariant, string> = {
  h1: "text-4xl font-bold tracking-tight",
  h2: "text-3xl font-semibold tracking-tight",
  h3: "text-2xl font-semibold",
  h4: "text-xl font-medium",
  body: "text-base leading-relaxed",
  "body-sm": "text-sm leading-relaxed",
  caption: "text-xs text-muted-foreground",
  overline: "text-xs font-semibold uppercase tracking-widest text-muted-foreground",
};

const defaultElements: Record<TextVariant, keyof JSX.IntrinsicElements> = {
  h1: "h1",
  h2: "h2",
  h3: "h3",
  h4: "h4",
  body: "p",
  "body-sm": "p",
  caption: "span",
  overline: "span",
};

export function Text({ variant = "body", as, className, children }: TextProps) {
  const Component = as || defaultElements[variant];
  return <Component className={cn(variantStyles[variant], className)}>{children}</Component>;
}
```

## Stack Layout Component

```tsx
// components/ds/Stack.tsx
import { cn } from "@/lib/utils";

type StackSpacing = "xs" | "sm" | "md" | "lg" | "xl";

interface StackProps {
  direction?: "row" | "column";
  spacing?: StackSpacing;
  align?: "start" | "center" | "end" | "stretch";
  justify?: "start" | "center" | "end" | "between" | "around";
  className?: string;
  children: React.ReactNode;
}

const spacingMap: Record<StackSpacing, string> = {
  xs: "gap-1",
  sm: "gap-2",
  md: "gap-4",
  lg: "gap-6",
  xl: "gap-8",
};

export function Stack({
  direction = "column",
  spacing = "md",
  align = "stretch",
  justify = "start",
  className,
  children,
}: StackProps) {
  return (
    <div
      className={cn(
        "flex",
        direction === "row" ? "flex-row" : "flex-col",
        spacingMap[spacing],
        `items-${align}`,
        `justify-${justify}`,
        className
      )}
    >
      {children}
    </div>
  );
}
```

## Barrel Export

```tsx
// components/ds/index.ts
export { Button } from "./Button";
export { Text } from "./Text";
export { Stack } from "./Stack";
```

## Design System Directory Structure

```
src/
├── components/
│   ├── ui/                    # Raw shadcn/ui components (auto-generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   └── ds/                    # Design system primitives (manually curated)
│       ├── Button.tsx         # Wrapped button with DS constraints
│       ├── Text.tsx           # Typography component
│       ├── Stack.tsx          # Layout primitive
│       └── index.ts           # Barrel export
├── styles/
│   └── globals.css            # Design tokens + theme configuration
└── lib/
    └── utils.ts               # cn() helper
```

## Usage Example

```tsx
import { Button, Text, Stack } from "@/components/ds";

function Hero() {
  return (
    <Stack spacing="lg" align="center" className="py-20">
      <Text variant="h1">Welcome to our Design System</Text>
      <Text variant="body">Consistent, accessible, beautiful UI</Text>
      <Stack direction="row" spacing="md">
        <Button variant="primary" size="lg">Get Started</Button>
        <Button variant="secondary" size="lg">Learn More</Button>
      </Stack>
    </Stack>
  );
}
```
