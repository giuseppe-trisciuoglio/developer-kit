{{-- Starter Page Template
     Copy this to resources/views/page.blade.php as a starting point --}}
@extends('layouts.app')

@section('content')
  <main class="page-content">
    @while(have_posts())
      @php the_post() @endphp

      <article class="{{ get_post_type() }}-single">
        @php($title = get_field('page_title') ?: get_the_title())
        <h1 class="entry-title">{{ $title }}</h1>

        @if (get_field('page_subtitle'))
          <p class="entry-subtitle">{{ get_field('page_subtitle') }}</p>
        @endif

        <div class="entry-content">
          @if (have_rows('flexible_content'))
            @while (have_rows('flexible_content'))
              @php the_row() @endphp

              @switch(get_row_layout())
                @case('hero_section')
                  @include('components.sections.hero')
                  @break

                @case('text_section')
                  @include('components.sections.text')
                  @break

                @case('image_gallery')
                  @include('components.sections.gallery')
                  @break

                @default
                  <div class="default-content">
                    {{ the_content() }}
                  </div>
              @endswitch
            @endwhile
          @else
            {{ the_content() }}
          @endif
        </div>
      </article>

      @if (comments_open() || get_comments_number())
        <div class="comments-wrapper">
          {{ comments_template() }}
        </div>
      @endif
    @endwhile

    {{ the_posts_pagination() }}
  </main>
@endsection
