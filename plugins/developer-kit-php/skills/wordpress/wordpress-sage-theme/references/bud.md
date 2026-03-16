# Bud Build Configuration Reference

Complete reference for configuring Bud (Sage's build tool based on Vite).

## Configuration File

**bud.config.js** - Main configuration file in theme root.

## Basic Configuration

```js
import config from '@roots/bud'

export default async (app) => {
  app
    .entry({
      app: ['./resources/scripts/main.js', './resources/styles/main.scss'],
      editor: ['./resources/scripts/editor.js', './resources/styles/editor.scss'],
    })
    .publicPath('/wp-content/themes/my-theme/public/')
}
```

## Entry Points

Define multiple entry points for different contexts:

```js
app.entry({
  // Frontend
  app: ['@scripts/main', '@styles/main'],

  // Editor (Gutenberg)
  editor: ['@scripts/editor', '@styles/editor'],

  // Custom admin
  admin: ['@scripts/admin', '@styles/admin'],
})
```

## Asset Management

### Copy Assets

```js
app.assets('images', 'fonts')
```

Copy files from `resources/` to `public/`:

```
resources/images/logo.png → public/images/logo.png
resources/fonts/inter.woff2 → public/fonts/inter.woff2
```

### Custom Paths

```js
app.assets(['images', 'fonts', 'icons'])
```

## Runtime

Enable runtime manifest for dynamic asset loading:

```js
app.runtime()
```

Creates `public/manifest.json` with asset mappings.

## Tailwind CSS

### Enable Tailwind

```js
import tailwindcss from '@roots/bud-tailwindcss'

app.use(tailwindcss)
```

### Configuration

**tailwind.config.js**:

```js
export default {
  content: [
    './resources/views/**/*.blade.php',
    './resources/scripts/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e40af',
        secondary: '#7c3aed',
      },
    },
  },
}
```

## Sass Configuration

### Options

```js
app.tailwind({
  options: {
    includePaths: ['node_modules'],
  },
})
```

## Aliases

Create import aliases:

```js
app.alias({
  '@': 'resources',
  '@scripts': 'resources/scripts',
  '@styles': 'resources/styles',
  '@components': 'resources/views/components',
})
```

Usage in JavaScript:

```js
import Button from '@/components/button'
```

## Minification

Control minification per environment:

```js
app.minimize(true) // Always minimize
app.minimize(false) // Never minimize
app.minimize(!app.isDevelopment) // Only in production
```

## Source Maps

```js
app.js({ sourcemaps: true })
```

## Dev Server

### Proxy Configuration

```js
app.proxy('http://localhost:3000')
```

### Watch Paths

```js
app.watch([
  'resources/views/**/*.blade.php',
  'app/**/*.php',
])
```

### Server Options

```js
app.server({
  host: 'localhost',
  port: 3000,
  hmr: true,
})
```

## PostCSS

### Plugins

```js
import postcssPresetEnv from 'postcss-preset-env'

app.postcss.set('plugins', [
  postcssPresetEnv({ stage: 1 }),
])
```

## Dependencies

### External Dependencies

```js
app.provide({
  $: 'jquery',
  jQuery: 'jquery',
  'window.jQuery': 'jquery',
})
```

### Vendor Splitting

```js
app.vendor('jquery', 'lodash')
```

## Optimization

### Split Chunks

```js
app.splitChunks(false) // Disable
app.splitChunks({
  strategy: 'default', // or 'single', 'all'
})
```

### Lazy Loading

```js
app.optimization.moduleChunks(true)
```

## Environment

### Detection

```js
app.isDevelopment // true in dev mode
app.isProduction  // true in production
```

### Conditional Config

```js
if (app.isProduction) {
  app.minimize()
}

if (app.isDevelopment) {
  app.devtool('eval-cheap-module-source-map')
}
```

## Commands Reference

```bash
# Development
npm run dev           # Start dev server with HMR
npm run dev -- --watch  # Watch mode without server

# Production
npm run build         # Build for production
npm run build -- --minify  # Build with extra minification

# Utilities
npm run clean         # Clean build directory
npm run check         # Check configuration
```

## Complete Example

```js
import config from '@roots/bud'
import tailwindcss from '@roots/bud-tailwindcss'

export default async (app) => {
  app
    // Entry points
    .entry({
      app: ['@scripts/main', '@styles/main'],
      editor: ['@scripts/editor', '@styles/editor'],
    })
    // Public path
    .publicPath('/wp-content/themes/my-theme/public')
    // Runtime manifest
    .runtime()
    // Asset copying
    .assets('images', 'fonts')
    // Tailwind
    .use(tailwindcss)
    // Aliases
    .alias({
      '@': 'resources',
      '@scripts': 'resources/scripts',
      '@styles': 'resources/styles',
    })
    // Minification
    .minimize(!app.isDevelopment)
    // Source maps
    .js({ sourcemaps: app.isDevelopment })
    // Dev server
    .proxy('http://localhost:3000')
    .watch([
      'resources/views/**/*.blade.php',
      'app/**/*.php',
    ])
}
```

## Troubleshooting

### HMR Not Working

Check proxy URL matches WordPress URL:

```js
app.proxy('http://localhost:3000') // Must match WP_URL
```

### Assets 404

Ensure public path is correct:

```js
app.publicPath('/wp-content/themes/my-theme/public/')
```

### Tailwind Classes Not Generated

Check content paths in `tailwind.config.js`:

```js
content: [
  './resources/views/**/*.blade.php', // Include Blade files
]
```
