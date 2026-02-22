# shadcn/ui Charts Component

Installation:

```bash
npx shadcn@latest add chart
```

The charts component is built on **Recharts** - providing direct access to all Recharts capabilities with consistent theming.

## ChartContainer and ChartConfig

```tsx
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "var(--chart-1)",
  },
  mobile: {
    label: "Mobile",
    color: "var(--chart-2)",
  },
} satisfies import("@/components/ui/chart").ChartConfig

const chartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  { month: "March", desktop: 237, mobile: 120 },
]

export function BarChartDemo() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="month"
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => value.slice(0, 3)}
        />
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
        <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
        <ChartTooltip content={<ChartTooltipContent />} />
      </BarChart>
    </ChartContainer>
  )
}
```

## ChartConfig with Custom Colors

```tsx
const chartConfig = {
  visitors: {
    label: "Visitors",
    color: "#2563eb",
    theme: {
      light: "#2563eb",
      dark: "#60a5fa",
    },
  },
  sales: {
    label: "Sales",
    color: "var(--chart-1)",
    theme: {
      light: "oklch(0.646 0.222 41.116)",
      dark: "oklch(0.696 0.182 281.41)",
    },
  },
} satisfies import("@/components/ui/chart").ChartConfig
```

## CSS Variables for Charts

Add chart color variables to `globals.css`:

```css
@layer base {
  :root {
    --chart-1: oklch(0.646 0.222 41.116);
    --chart-2: oklch(0.6 0.118 184.704);
    --chart-3: oklch(0.546 0.198 38.228);
    --chart-4: oklch(0.596 0.151 343.253);
    --chart-5: oklch(0.546 0.158 49.157);
  }

  .dark {
    --chart-1: oklch(0.488 0.243 264.376);
    --chart-2: oklch(0.696 0.17 162.48);
    --chart-3: oklch(0.698 0.141 24.311);
    --chart-4: oklch(0.676 0.172 171.196);
    --chart-5: oklch(0.578 0.192 302.85);
  }
}
```

## Line Chart Example

```tsx
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const chartConfig = {
  price: { label: "Price", color: "var(--chart-1)" },
} satisfies import("@/components/ui/chart").ChartConfig

export function LineChartDemo() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px]">
      <LineChart data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey="month" tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
        <Line dataKey="price" stroke="var(--color-price)" strokeWidth={2} dot={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
      </LineChart>
    </ChartContainer>
  )
}
```

## Area Chart Example

```tsx
import { Area, AreaChart, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartLegend, ChartLegendContent, ChartTooltipContent } from "@/components/ui/chart"

const chartConfig = {
  desktop: { label: "Desktop", color: "var(--chart-1)" },
  mobile: { label: "Mobile", color: "var(--chart-2)" },
} satisfies import("@/components/ui/chart").ChartConfig

export function AreaChartDemo() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px]">
      <AreaChart data={chartData}>
        <XAxis dataKey="month" tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} />
        <Area dataKey="desktop" fill="var(--color-desktop)" stroke="var(--color-desktop)" fillOpacity={0.3} />
        <Area dataKey="mobile" fill="var(--color-mobile)" stroke="var(--color-mobile)" fillOpacity={0.3} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
      </AreaChart>
    </ChartContainer>
  )
}
```

## Pie Chart Example

```tsx
import { Pie, PieChart } from "recharts"
import { ChartContainer, ChartLegend, ChartLegendContent, ChartTooltipContent } from "@/components/ui/chart"

const chartConfig = {
  chrome: { label: "Chrome", color: "var(--chart-1)" },
  safari: { label: "Safari", color: "var(--chart-2)" },
  firefox: { label: "Firefox", color: "var(--chart-3)" },
} satisfies import("@/components/ui/chart").ChartConfig

const pieData = [
  { browser: "Chrome", visitors: 275, fill: "var(--color-chrome)" },
  { browser: "Safari", visitors: 200, fill: "var(--color-safari)" },
  { browser: "Firefox", visitors: 187, fill: "var(--color-firefox)" },
]

export function PieChartDemo() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px]">
      <PieChart>
        <Pie data={pieData} dataKey="visitors" nameKey="browser" cx="50%" cy="50%" outerRadius={80} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
      </PieChart>
    </ChartContainer>
  )
}
```

## ChartTooltipContent Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `labelKey` | string | "label" | Key for tooltip label |
| `nameKey` | string | "name" | Key for tooltip name |
| `indicator` | "dot" \| "line" \| "dashed" | "dot" | Indicator style |
| `hideLabel` | boolean | false | Hide label |
| `hideIndicator` | boolean | false | Hide indicator |

## Accessibility

Enable keyboard navigation and screen reader support:

```tsx
<BarChart accessibilityLayer data={chartData}>...</BarChart>
```

This adds:
- Keyboard arrow key navigation
- ARIA labels for chart elements
- Screen reader announcements for data values
