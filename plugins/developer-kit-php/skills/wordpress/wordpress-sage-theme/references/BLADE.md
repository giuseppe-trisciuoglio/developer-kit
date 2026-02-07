# Blade Templates Reference

Complete reference for Blade templating in Sage WordPress themes.

## Directives Reference

### Template Inheritance

**@extends**: Inherit from a layout
```blade
@extends('layouts.app')
```

**@section**: Define content section
```blade
@section('content')
  <h1>Page Content</h1>
@endsection
```

**@yield**: Display content section
```blade
@yield('content')
@yield('content', 'Default content if not provided')
```

### Conditionals

**@if/@else/@elseif/@endif**
```blade
@if (condition)
  <p>True</p>
@elseif (other_condition)
  <p>Other</p>
@else
  <p>False</p>
@endif
```

**@unless**: Negative if
```blade
@unless ($user->logged_in)
  <a href="/login">Login</a>
@endunless
```

**@isset/null**: Check variable existence
```blade
@isset($variable)
  {{ $variable }}
@endisset

@empty($collection)
  <p>No items</p>
@endempty
```

**@auth/@guest**: User authentication
```blade
@auth
  <a href="/dashboard">Dashboard</a>
@endauth

@guest
  <a href="/login">Login</a>
@endguest
```

### Loops

**@while**: WordPress loop
```blade
@while (have_posts())
  @php the_post() @endphp
  <h2>{{ the_title() }}</h2>
@endwhile
```

**@foreach**: Iterate arrays
```blade
@foreach ($items as $item)
  <li>{{ $item->name }}</li>
@endforeach
```

**@for**: Standard for loop
```blade
@for ($i = 0; $i < 10; $i++)
  <span>{{ $i }}</span>
@endfor
```

**@break/@continue**: Loop control
```blade
@foreach ($items as $item)
  @if ($item->skip)
    @continue
  @endif

  {{ $item->name }}

  @if ($item->last)
    @break
  @endif
@endforeach
```

### Includes

**@include**: Include template
```blade
@include('components.card')
```

**@includeIf**: Include if exists
```blade
@includeIf('components.optional')
```

**@includeWhen**: Include conditionally
```blade
@includeWhen($condition, 'components.featured')
```

**@includeIf**: With variables
```blade
@include('components.button', ['text' => 'Click', 'url' => '/page'])
```

### Components

**Anonymous Components** (`resources/views/components/alert.blade.php`):
```blade
@props(['type' => 'info', 'message' => ''])

<div class="alert alert-{{ $type }}">
  {{ $message }}
</div>
```

**Usage**:
```blade
<x-alert type="warning" message="Warning message" />
```

**Indexed Components** (`resources/views/components/button.blade.php`):
```blade
@props(['variant' => 'primary'])

<button class="btn btn-{{ $variant }}">
  {{ $slot }}
</button>
```

**Usage**:
```blade
<x-button variant="secondary">
  Click Me
</x-button>
```

**Dynamic Components**:
```blade
@php $component = 'button' @endphp
<x-dynamic-component :component="$component" :variant="'primary'" />
```

### Directives

**@php**: Execute PHP
```blade
@php
  $data = get_field('data');
  $formatted = format_data($data);
@endphp
```

**@verbatim**: Disable Blade parsing
```blade
@verbatim
  {{ This won't be parsed }}
@endverbatim
```

**@once**: Execute once per rendering
```blade
@once
  <script src="https://cdn.example.com/widget.js"></script>
@endonce
```

**@csrf**: CSRF token (rarely used in WP)
```blade
@csrf
```

**@method**: Form method spoofing
```blade
@method('PUT')
```

## WordPress Functions in Blade

### Common Functions

```blade
{{ the_title() }}              // Post title
{{ the_content() }}            // Post content
{{ the_excerpt() }}            // Post excerpt
{{ the_permalink() }}          // Post URL
{{ the_post_thumbnail_url() }} // Featured image URL
{{ the_date() }}               // Post date
{{ the_author() }}             // Author name
{{ the_category() }}           // Categories
{{ the_tags() }}               // Tags
```

### Conditional Tags

```blade
@if (is_front_page())     @endif
@if (is_home())           @endif
@if (is_single())         @endif
@if (is_page())           @endif
@if (is_category())       @endif
@if (is_archive())        @endif
@if (is_search())         @endif
@if (is_404())            @endif
```

### Helper Functions

```blade
{{ get_template_directory_uri() }}  // Theme URL
{{ get_stylesheet_directory_uri() }} // Child theme URL
{{ home_url('/') }}                 // Site URL
{{ site_url('/') }}                 // Site URL
{{ wp_get_attachment_url($id) }}    // Attachment URL
```

## Common Patterns

### Post Loop with Pagination

```blade
@extends('layouts.app')

@section('content')
  <div class="posts">
    @while (have_posts())
      @php the_post() @endphp

      @include('components.post-card')
    @endwhile
  </div>

  {{ the_posts_pagination() }}
@endsection
```

### Sidebar Conditional

```blade
@if (is_active_sidebar('sidebar'))
  <aside class="sidebar">
    {{ dynamic_sidebar('sidebar') }}
  </aside>
@endif
```

### Menu Rendering

```blade
@if (has_nav_menu('primary'))
  <nav class="primary-nav">
    {{ wp_nav_menu([
      'theme_location' => 'primary',
      'container' => false,
      'menu_class' => 'nav-menu'
    ]) }}
  </nav>
@endif
```

## Output Escaping

**{{ }}**: Auto-escaped (safe for user content)
```blade
{{ $user_input }}
```

**{!! !!}**: Unescaped (use with caution)
```blade
{!! $html_content !!}
```

**@verbatim**: Multiple unescaped lines
```blade
@verbatim
  <div class="example">
    {{ This won't be escaped }}
  </div>
@endverbatim
```
