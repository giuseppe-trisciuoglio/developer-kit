# Sage Framework Reference

Complete reference for the Sage WordPress theme framework.

## Installation Methods

### Method 1: WP CLI

```bash
wp scaffold sage-theme my-theme --theme_name="My Theme" --author="Name" --activate
```

### Method 2: Composer

```bash
composer create-project roots/sage my-theme
cd my-theme
composer install
```

## Theme Structure

```
theme/
├── app/
│   ├── controllers/      # Custom controllers
│   ├── helpers.php       # Helper functions
│   ├── filters.php       # WordPress filters
│   └── setup.php         # Theme setup
├── resources/
│   ├── views/            # Blade templates
│   ├── styles/           # CSS/SASS
│   └── scripts/          # JavaScript
├── public/               # Built assets (generated)
├── composer.json
├── package.json
└── bud.config.js         # Build configuration
```

## Key Files

### app/setup.php

Theme configuration and WordPress setup:

```php
add_action('after_setup_theme', function () {
    // Enable features
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', [
        'caption',
        'comment-form',
        'comment-list',
        'gallery',
        'search-form'
    ]);
});
```

### app/helpers.php

Custom helper functions available in Blade templates:

```php
function custom_helper() {
    return 'value';
}
```

## Controllers

Organize data logic in controllers:

```php
// app/controllers/PageController.php
namespace App\Controllers;

class PageController extends \App\Controllers\Controller
{
    public function page()
    {
        return $this->view->make('page', [
            'title' => get_the_title(),
            'content' => apply_filters('the_content', get_the_content()),
        ]);
    }
}
```

## Filters

Modify WordPress behavior:

```php
// Remove emoji scripts
remove_action('wp_head', 'print_emoji_detection_script', 7);

// Custom excerpt length
add_filter('excerpt_length', function ($length) {
    return 20;
});
```

## Common Issues

### HMR Not Working

Check `bud.config.js` proxy settings:

```js
.proxy('http://localhost:3000') // WordPress URL
```

### Images Not Loading

Use `@asset()` directive in Blade:

```blade
<img src="@asset('images/logo.png')" alt="Logo">
```

### Styles Not Applying

Ensure `@styles` directive in layout:

```blade
{{ wp_head() }}
{{-- Bud automatically injects styles --}}
```
