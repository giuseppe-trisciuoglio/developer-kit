# React Accessibility Checklist and ARIA Patterns

## Semantic HTML First

Always use the correct semantic element before reaching for ARIA attributes.

| Need | Use | Not |
|------|-----|-----|
| Button | `<button>` | `<div onClick>` |
| Link/navigation | `<a href>` | `<span onClick>` |
| List | `<ul>` / `<ol>` | `<div>` with items |
| Heading | `<h1>`–`<h6>` | `<div className="title">` |
| Navigation | `<nav>` | `<div className="nav">` |
| Main content | `<main>` | `<div className="content">` |
| Form input label | `<label htmlFor>` | Placeholder text only |
| Table data | `<table>` | `<div>` grid layout |

## Interactive Elements

### Buttons vs Links
- **Button**: Triggers an action (submit, toggle, open modal)
- **Link**: Navigates to a URL or page section

```tsx
// ✅ Correct: Button for action
<button onClick={handleSave} type="button">Save</button>

// ✅ Correct: Link for navigation
<a href="/settings">Go to Settings</a>

// ❌ Wrong: Div as button
<div onClick={handleSave} className="btn">Save</div>

// ❌ Wrong: Button for navigation
<button onClick={() => router.push('/settings')}>Go to Settings</button>
```

### Keyboard Navigation
All interactive elements must be keyboard accessible.

```tsx
// ✅ Custom interactive element with keyboard support
function ToggleSwitch({ checked, onChange }: ToggleSwitchProps) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      onKeyDown={(e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          onChange(!checked);
        }
      }}
    >
      {checked ? 'On' : 'Off'}
    </button>
  );
}
```

## Focus Management

### Modal Focus Trap

```tsx
'use client';

import { useEffect, useRef } from 'react';

function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={modalRef}
      tabIndex={-1}
      onKeyDown={(e) => {
        if (e.key === 'Escape') onClose();
      }}
    >
      <h2 id="modal-title">Modal Title</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

### Skip Navigation Link
Allow keyboard users to skip repetitive navigation.

```tsx
function SkipToMain() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:p-4 focus:bg-white"
    >
      Skip to main content
    </a>
  );
}

function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <SkipToMain />
      <Header />
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
    </>
  );
}
```

## ARIA Patterns

### Live Regions
Announce dynamic content changes to screen readers.

```tsx
// ✅ Announce form submission status
function ContactForm() {
  const [status, setStatus] = useState('');

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit">Send</button>
      <div role="status" aria-live="polite" aria-atomic="true">
        {status}
      </div>
    </form>
  );
}
```

### Expandable Sections

```tsx
function Accordion({ title, children }: AccordionProps) {
  const [expanded, setExpanded] = useState(false);
  const contentId = useId();

  return (
    <div>
      <button
        aria-expanded={expanded}
        aria-controls={contentId}
        onClick={() => setExpanded(!expanded)}
      >
        {title}
      </button>
      <div
        id={contentId}
        role="region"
        hidden={!expanded}
      >
        {children}
      </div>
    </div>
  );
}
```

### Tabs Pattern

```tsx
function Tabs({ tabs }: { tabs: TabData[] }) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === index}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === index ? 0 : -1}
            onClick={() => setActiveTab(index)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowRight') setActiveTab((activeTab + 1) % tabs.length);
              if (e.key === 'ArrowLeft') setActiveTab((activeTab - 1 + tabs.length) % tabs.length);
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== index}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

## Forms Accessibility

### Label Association
Every form input must have an associated label.

```tsx
// ✅ Explicit label with htmlFor
<label htmlFor="email">Email address</label>
<input id="email" type="email" aria-required="true" />

// ✅ Wrapping label
<label>
  Email address
  <input type="email" aria-required="true" />
</label>

// ❌ No label — only placeholder
<input type="email" placeholder="Email" />
```

### Error Messages

```tsx
function FormField({ label, error, ...props }: FormFieldProps) {
  const id = useId();
  const errorId = `${id}-error`;

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : undefined}
        {...props}
      />
      {error && (
        <p id={errorId} role="alert" className="text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}
```

## Color and Contrast

- Minimum contrast ratio: **4.5:1** for normal text, **3:1** for large text (WCAG AA)
- Don't convey information through color alone — use icons, patterns, or text
- Support `prefers-color-scheme` for dark mode
- Test with color blindness simulators

## Motion and Animation

```tsx
// Respect user motion preferences
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// In Tailwind CSS
<div className="transition-transform motion-reduce:transition-none">
  Animated content
</div>

// In CSS
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Review Checklist

### Structure
- [ ] Semantic HTML elements used (nav, main, article, section, aside)
- [ ] Heading hierarchy is logical (h1 → h2 → h3, no skipping)
- [ ] Landmarks present (header, nav, main, footer)
- [ ] Skip navigation link provided
- [ ] Page has a descriptive `<title>`

### Interactive Elements
- [ ] All interactive elements are keyboard accessible
- [ ] Focus order is logical (follows visual order)
- [ ] Focus indicators are visible
- [ ] No keyboard traps
- [ ] Custom interactive elements have proper ARIA roles

### Forms
- [ ] All inputs have associated labels
- [ ] Required fields indicated with `aria-required`
- [ ] Error messages linked with `aria-describedby`
- [ ] Error states use `aria-invalid`
- [ ] Form groups use `fieldset` and `legend`

### Images and Media
- [ ] All images have `alt` text (empty `alt=""` for decorative)
- [ ] Complex images have extended descriptions
- [ ] Videos have captions and transcripts
- [ ] Audio has transcripts

### Dynamic Content
- [ ] Live regions announce important changes
- [ ] Loading states communicated to screen readers
- [ ] Modals trap focus and restore on close
- [ ] Toast notifications use `role="status"` or `role="alert"`
