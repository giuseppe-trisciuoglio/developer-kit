# ACF Integration Reference

Complete reference for integrating Advanced Custom Fields (ACF) with Sage WordPress themes.

## Installation

```bash
# Install ACF Pro via Composer
composer require wp-premium/acf-pro

# Or install ACF Free
composer require advanced-custom-fields/advanced-custom-fields
```

## Field Types Reference

### Basic Fields

**Text**:
```blade
<h1>{{ get_field('heading') }}</h1>
```

**Textarea**:
```blade
<div class="description">
  {{ get_field('description') }}
</div>
```

**Number**:
```blade
@php($price = get_field('price'))
<span class="price">${{ number_format($price, 2) }}</span>
```

**Email/URL**:
```blade
<a href="mailto:{{ get_field('email') }}">{{ get_field('email') }}</a>
<a href="{{ get_field('website') }}">Visit Website</a>
```

### Media Fields

**Image** (Return Format: Image Array):
```blade
@php($image = get_field('hero_image'))
@if ($image)
  <img
    src="{{ $image['url'] }}"
    alt="{{ $image['alt'] }}"
    width="{{ $image['width'] }}"
    height="{{ $image['height'] }}"
  >
@endif
```

**Image** (Return Format: URL):
```blade
<img src="{{ get_field('logo') }}" alt="Logo">
```

**Gallery**:
```blade
@php($gallery = get_field('gallery'))
@if ($gallery)
  <div class="gallery">
    @foreach ($gallery as $image)
      <img src="{{ $image['url'] }}" alt="{{ $image['alt'] }}">
    @endforeach
  </div>
@endif
```

**File**:
```blade
@php($file = get_field('download'))
@if ($file)
  <a href="{{ $file['url'] }}" download>Download {{ $file['filename'] }}</a>
@endif
```

### Choice Fields

**Select**:
```blade
@php($status = get_field('status'))
<span class="status status-{{ $status }}">{{ $status }}</span>
```

**Checkbox** (Return Format: Value):
```blade
@php($services = get_field('services'))
@if ($services && is_array($services))
  <ul class="services">
    @foreach ($services as $service)
      <li>{{ $service }}</li>
    @endforeach
  </ul>
@endif
```

**Radio**:
```blade
@php($layout = get_field('layout'))
<div class="container container-{{ $layout }}">
  {{ the_content() }}
</div>
```

### Relational Fields

**Post Object** (Single):
```blade
@php($featured_post = get_field('featured_post'))
@if ($featured_post)
  @php(setup_postdata($GLOBALS['post'], $featured_post))
  <article>
    <h2>{{ the_title() }}</h2>
    {{ the_excerpt() }}
  </article>
  @php(wp_reset_postdata())
@endif
```

**Post Object** (Multiple):
```blade
@php($posts = get_field('related_posts'))
@if ($posts)
  <div class="related-posts">
    @foreach ($posts as $post)
      @php(setup_postdata($GLOBALS['post'], $post))
      <h3>{{ the_title() }}</h3>
      @endforeach
    @php(wp_reset_postdata())
  </div>
@endif
```

**Page Link**:
```blade
@php($link = get_field('cta_link'))
@if ($link)
  <a href="{{ $link['url'] }}"
     target="{{ $link['target'] ?: '_self' }}"
     class="btn">
    {{ $link['title'] ?: 'Learn More' }}
  </a>
@endif
```

**Relationship**:
```blade
@php($related = get_field('related_projects'))
@if ($related)
  @foreach ($related as $p)
    @php($project = get_post($p->ID))
    <h3>{{ $project->post_title }}</h3>
    <a href="{{ get_permalink($project->ID) }}">View Project</a>
  @endforeach
@endif
```

**Taxonomy**:
```blade
@php($categories = get_field('featured_categories'))
@if ($categories)
  <ul>
    @foreach ($categories as $category)
      <li>
        <a href="{{ get_term_link($category) }}">
          {{ $category->name }}
        </a>
      </li>
    @endforeach
  </ul>
@endif
```

**User**:
```blade
@php($author = get_field('author'))
@if ($author)
  <div class="author">
    <img src="{{ get_avatar_url($author['ID']) }}" alt="{{ $author['display_name'] }}">
    <span>{{ $author['display_name'] }}</span>
  </div>
@endif
```

## Complex Field Types

### Repeater

**Basic Repeater**:
```blade
@if (have_rows('testimonials'))
  <div class="testimonials">
    @while (have_rows('testimonials'))
      @php(the_row())
      <blockquote>
        <p>{{ get_sub_field('testimonial_text') }}</p>
        <cite>{{ get_sub_field('author_name') }}</cite>
      </blockquote>
    @endwhile
  </div>
@endif
```

**Repeater with Sub-fields**:
```blade
@if (have_rows('pricing_plans'))
  <div class="pricing">
    @while (have_rows('pricing_plans'))
      @php(the_row())
      <div class="plan">
        <h3>{{ get_sub_field('plan_name') }}</h3>
        <div class="price">{{ get_sub_field('price') }}/mo</div>
        <ul class="features">
          @while (have_rows('features'))
            @php(the_row())
            <li>{{ get_sub_field('feature_name') }}</li>
          @endwhile
        </ul>
      </div>
    @endwhile
  </div>
@endif
```

**Nested Repeater**:
```blade
@if (have_rows('teams'))
  @while (have_rows('teams'))
    @php(the_row())
    <div class="team">
      <h2>{{ get_sub_field('team_name') }}</h2>

      @if (have_rows('team_members'))
        <ul class="members">
          @while (have_rows('team_members'))
            @php(the_row())
            <li>{{ get_sub_field('member_name') }}</li>
          @endwhile
        </ul>
      @endif
    </div>
  @endwhile
@endif
```

### Flexible Content

**Basic Flexible Content**:
```blade
@if (have_rows('page_sections'))
  @while (have_rows('page_sections'))
    @php(the_row())
    @switch(get_row_layout())
      @case('hero_section')
        @include('components.sections.hero')
        @break

      @case('features_grid')
        @include('components.sections.features')
        @break

      @case('cta_banner')
        @include('components.sections.cta')
        @break
    @endswitch
  @endwhile
@endif
```

**Hero Section Component** (`resources/views/components/sections/hero.blade.php`):
```blade
@php
  $title = get_sub_field('hero_title');
  $subtitle = get_sub_field('hero_subtitle');
  $background = get_sub_field('background_image');
@endphp

<section class="hero">
  @if ($background)
    <div class="hero-bg" style="background-image: url({{ $background['url'] }})"></div>
  @endif

  <div class="hero-content">
    <h1>{{ $title }}</h1>
    <p>{{ $subtitle }}</p>
  </div>
</section>
```

### Group

**Basic Group**:
```blade
@php($hero = get_field('hero_group'))
@if ($hero)
  <section class="hero">
    <h1>{{ $hero['title'] }}</h1>
    <p>{{ $hero['description'] }}</p>
    @if ($hero['background_image'])
      <img src="{{ $hero['background_image']['url'] }}" alt="">
    @endif
  </section>
@endif
```

**Group with Conditional**:
```blade
@php($settings = get_field('display_settings'))
@if ($settings && $settings['show_section'])
  <div class="custom-section {{ $settings['css_class'] }}">
    {{ the_content() }}
  </div>
@endif
```

### Clone

**Cloned Field Display**:
```blade
@php($cloned_fields = get_field('cloned_content'))
@if ($cloned_fields)
  <div class="cloned-content">
    <h2>{{ $cloned_fields['headline'] }}</h2>
    <p>{{ $cloned_fields['description'] }}</p>

    @if ($cloned_fields['show_button'])
      <a href="{{ $cloned_fields['button_link'] }}" class="btn">
        {{ $cloned_fields['button_text'] }}
      </a>
    @endif
  </div>
@endif
```

## Options Page

### Register Options Page

**In `app/setup.php`**:
```php
add_action('acf/init', function () {
    if (function_exists('acf_add_options_page')) {
        acf_add_options_page([
            'page_title' => 'Theme Settings',
            'menu_title' => 'Theme Settings',
            'menu_slug' => 'theme-settings',
            'capability' => 'edit_posts',
        ]);

        acf_add_options_sub_page([
            'page_title' => 'Header Settings',
            'menu_title' => 'Header',
            'parent_slug' => 'theme-settings',
        ]);
    }
});
```

### Display Options

```blade
@php($company_name = get_field('company_name', 'option'))
@if ($company_name)
  <footer>
    <p>&copy; {{ date('Y') }} {{ $company_name }}</p>
  </footer>
@endif
```

**Options with Repeater**:
```blade
@if (have_rows('social_links', 'option'))
  <div class="social-links">
    @while (have_rows('social_links', 'option'))
      @php(the_row())
      <a href="{{ get_sub_field('url', 'option') }}" class="social-icon">
        {{ get_sub_field('icon', 'option') }}
      </a>
    @endwhile
  </div>
@endif
```

## Conditional Logic in Blade

**Field Has Value**:
```blade
@if (get_field('featured_image'))
  {{-- Display section --}}
@endif
```

**Field Equals Value**:
```blade
@if (get_field('layout_type') === 'full-width')
  <div class="container-full">
@else
  <div class="container">
@endif
  {{ the_content() }}
  </div>
```

**Multiple Conditions**:
```blade
@php($type = get_field('content_type'))
@if ($type === 'video')
  @include('components.video')
@elseif ($type === 'gallery')
  @include('components.gallery')
@else
  @include('components.default')
@endif
```

## Helper Functions

**Format ACF Image**:
```php
// In app/helpers.php
function format_acf_image($image, $size = 'large') {
    if (!$image) return null;

    if (is_array($image)) {
        return [
            'url' => $image['url'],
            'alt' => $image['alt'] ?? '',
            'title' => $image['title'] ?? '',
        ];
    }

    return [
        'url' => $image,
        'alt' => '',
        'title' => '',
    ];
}
```

## Performance Tips

1. **Load fields efficiently**: Use `get_fields()` to load all fields at once
   ```blade
   @php($fields = get_fields(get_the_ID()))
   <h1>{{ $fields['title'] }}</h1>
   <p>{{ $fields['description'] }}</p>
   ```

2. **Cache repeater counts**:
   ```blade
   @if (have_rows('items') && count(get_field('items')) > 0)
   ```

3. **Use formatted values**: ACF returns formatted values by default for better performance

4. **Disable loading on specific posts**:
   ```php
   add_filter('acf/load_value', '__return_false');
   ```
