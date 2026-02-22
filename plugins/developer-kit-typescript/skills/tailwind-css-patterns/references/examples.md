# Tailwind CSS Component Patterns & Examples

## Layout Utilities

### Flexbox Layouts

```html
<!-- Basic flex -->
<div class="flex items-center justify-between">
  <div>Left</div>
  <div>Right</div>
</div>

<!-- Responsive flex direction -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="flex-1">Item 1</div>
  <div class="flex-1">Item 2</div>
</div>

<!-- Center content -->
<div class="flex items-center justify-center min-h-screen">
  <div>Centered Content</div>
</div>

<!-- Vertical stack with gap -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### Grid Layouts

```html
<!-- Basic grid -->
<div class="grid grid-cols-3 gap-4">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <div>Item 4</div>
</div>

<!-- Auto-fit columns -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  <!-- Automatically fits columns -->
</div>
```

### Container & Max Width

```html
<div class="container mx-auto px-4 max-w-7xl">Centered content</div>
<div class="w-full max-w-md mx-auto">Max 448px, centered</div>
```

## Spacing

```html
<!-- Uniform -->
<div class="p-4">Padding all sides</div>
<div class="px-4 py-8">Horizontal 1rem, Vertical 2rem</div>

<!-- Responsive -->
<div class="p-4 md:p-8 lg:p-12">Increases at breakpoints</div>

<!-- Space between children -->
<div class="space-y-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

## Typography

```html
<h1 class="text-4xl font-bold">Large Heading</h1>
<h2 class="text-2xl font-semibold">Subheading</h2>
<p class="text-base font-normal">Body text</p>

<!-- Responsive typography -->
<h1 class="text-2xl md:text-4xl lg:text-6xl font-bold">Responsive Heading</h1>

<p class="leading-relaxed tracking-wide">Relaxed line height, wide letter spacing</p>
```

## Colors

```html
<div class="bg-blue-500">Blue background</div>
<div class="bg-gradient-to-r from-blue-500 to-purple-600">Gradient</div>
<p class="text-gray-900">Dark text</p>
<div class="bg-blue-500 bg-opacity-50">Semi-transparent</div>
```

## Interactive States

```html
<!-- Hover -->
<button class="bg-blue-500 hover:bg-blue-700 transition">Hover me</button>

<!-- Focus -->
<input class="border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none">

<!-- Active & Disabled -->
<button class="bg-blue-500 active:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed">Button</button>

<!-- Group Hover -->
<div class="group">
  <img class="group-hover:opacity-75" src="image.jpg" />
  <p class="group-hover:text-blue-600">Hover the parent</p>
</div>
```

## Component Patterns

### Card Component

```html
<div class="bg-white rounded-lg shadow-lg overflow-hidden">
  <img class="w-full h-48 object-cover" src="image.jpg" alt="Card image" />
  <div class="p-6">
    <h3 class="text-xl font-bold mb-2">Card Title</h3>
    <p class="text-gray-700 mb-4">Card description text goes here.</p>
    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Action</button>
  </div>
</div>
```

### Navigation Bar

```html
<nav class="bg-white shadow-lg">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center h-16">
      <a href="#" class="text-xl font-bold text-gray-800">Logo</a>
      <div class="hidden md:flex space-x-8">
        <a href="#" class="text-gray-700 hover:text-blue-600 transition">Home</a>
        <a href="#" class="text-gray-700 hover:text-blue-600 transition">About</a>
      </div>
      <button class="md:hidden">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
      </button>
    </div>
  </div>
</nav>
```

### Form Elements

```html
<form class="space-y-6 max-w-md mx-auto">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
    <input type="email"
      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      placeholder="you@example.com" />
  </div>
  <button type="submit"
    class="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition">
    Sign In
  </button>
</form>
```

### Modal/Dialog

```html
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-bold">Modal Title</h3>
      <button class="text-gray-500 hover:text-gray-700">X</button>
    </div>
    <p class="text-gray-700 mb-6">Modal content goes here.</p>
    <div class="flex justify-end space-x-4">
      <button class="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
      <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Confirm</button>
    </div>
  </div>
</div>
```

## Responsive Design Patterns

### Mobile-First Hero

```html
<div class="flex flex-col md:flex-row items-center gap-8 py-12">
  <div class="flex-1">
    <h1 class="text-3xl md:text-5xl font-bold mb-4">Welcome</h1>
    <p class="text-lg text-gray-600 mb-6">Build amazing things</p>
    <button class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">Get Started</button>
  </div>
  <div class="flex-1">
    <img src="hero.jpg" class="w-full rounded-lg shadow-lg" />
  </div>
</div>
```

### Responsive Grid Gallery

```html
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
  <div class="aspect-square bg-gray-200 rounded-lg overflow-hidden">
    <img src="image1.jpg" class="w-full h-full object-cover hover:scale-105 transition" />
  </div>
</div>
```

## Dark Mode

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-400">Description</p>
</div>
```

## Animations & Transitions

```html
<button class="bg-blue-500 hover:bg-blue-700 transition duration-300">Smooth</button>
<div class="transform hover:scale-110 transition duration-300">Scale on hover</div>
<div class="animate-spin">Spinning</div>
<div class="animate-pulse">Pulsing</div>
<div class="animate-bounce">Bouncing</div>
```

## React/JSX Pattern with Variants

```tsx
function Button({ variant = 'primary', size = 'md', children }: {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}) {
  const baseClasses = 'font-semibold rounded transition';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  };
  const sizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  return (
    <button className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}>
      {children}
    </button>
  );
}
```

## Accessibility

```html
<!-- Focus styles -->
<button class="focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-offset-2">Accessible</button>

<!-- Skip links -->
<a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4">Skip to main</a>

<!-- Motion preferences -->
<div class="transform transition-transform motion-reduce:transition-none">Respects reduced motion</div>
```
