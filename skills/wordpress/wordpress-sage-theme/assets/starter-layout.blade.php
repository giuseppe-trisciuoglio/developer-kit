{{-- Starter Layout Template
     Copy this to resources/views/layouts/app.blade.php as a starting point --}}
<!DOCTYPE html>
<html {{ site_html_language_attributes() }} class="no-js">
  <head>
    <meta charset="{{ site_bloginfo('charset') }}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {{ wp_head() }}
  </head>
  <body {{ body_class() }}>
    @do_action('get_header')
    <div class="wrap" role="document">
      @yield('content')
    </div>
    @do_action('get_footer')
    {{ wp_footer() }}
  </body>
</html>
