# TechStore Accessibility Standards

## ♿ Accessibility Philosophy
Everyone should be able to use TechStore effectively, regardless of their abilities. Accessibility is not an afterthought—it's a core design principle.

## WCAG 2.1 Compliance

### Target Levels
- **Minimum**: AA compliance for all features
- **Goal**: AAA compliance where possible
- **Priority**: Critical business functions must exceed standards

## Color & Contrast

### Contrast Ratios
All text must meet WCAG contrast requirements:

#### Normal Text (< 18pt or < 14pt bold)
- **Minimum**: 4.5:1 contrast ratio
- **Large Text**: 3:1 contrast ratio

#### Our Palette Compliance
```
✅ Gray-900 on White: 17.9:1 (AAA)
✅ Gray-700 on White: 10.9:1 (AAA)
✅ Primary-500 on White: 4.7:1 (AA)
✅ Success-500 on White: 4.5:1 (AA)
✅ Error-500 on White: 4.5:1 (AA)
✅ White on Primary-500: 4.7:1 (AA)
```

### Color Independence
Never convey information through color alone:

```html
<!-- Bad: Only color indicates status -->
<span class="text-green-500">Active</span>

<!-- Good: Icon + color + text -->
<span class="text-green-500">
  <svg>✓</svg> Active
</span>
```

### Focus Indicators
All interactive elements must have visible focus states:

```css
/* Minimum focus indicator */
:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Enhanced focus for inputs */
.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}
```

## Keyboard Navigation

### Tab Order
- Logical flow matching visual layout
- Skip links for repetitive content
- No keyboard traps
- All interactive elements reachable

### Keyboard Shortcuts
```html
<!-- Skip to main content -->
<a href="#main" class="sr-only focus:not-sr-only">
  Skip to main content
</a>

<!-- Common shortcuts -->
/ : Focus search
Esc : Close modals
← → : Navigate tabs
Space : Toggle checkboxes
Enter : Activate buttons
```

### Focus Management
```javascript
// Return focus after modal close
const previousFocus = document.activeElement;
modal.close();
previousFocus.focus();

// Focus first error field
const firstError = form.querySelector('.error');
if (firstError) firstError.focus();
```

## Screen Reader Support

### Semantic HTML
Use proper HTML elements for their intended purpose:

```html
<!-- Navigation -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/">Dashboard</a></li>
    <li><a href="/products">Products</a></li>
  </ul>
</nav>

<!-- Main content -->
<main id="main">
  <h1>Page Title</h1>
  <!-- Content -->
</main>

<!-- Form structure -->
<form>
  <fieldset>
    <legend>Personal Information</legend>
    <!-- Fields -->
  </fieldset>
</form>
```

### ARIA Labels & Descriptions
Provide context when visual cues aren't enough:

```html
<!-- Icon buttons -->
<button aria-label="Edit product">
  <svg><!-- Edit icon --></svg>
</button>

<!-- Form fields -->
<label for="email">Email Address</label>
<input 
  id="email" 
  type="email"
  aria-describedby="email-help email-error"
  aria-invalid="true"
>
<p id="email-help">We'll never share your email</p>
<p id="email-error" role="alert">Please enter a valid email</p>

<!-- Status messages -->
<div role="status" aria-live="polite">
  3 items added to cart
</div>

<!-- Loading states -->
<div aria-busy="true" aria-label="Loading products">
  <div class="spinner"></div>
</div>
```

### Live Regions
Announce dynamic changes:

```html
<!-- Success messages -->
<div role="status" aria-live="polite">
  Product saved successfully
</div>

<!-- Error messages -->
<div role="alert" aria-live="assertive">
  Error: Invalid input
</div>

<!-- Progress updates -->
<div role="progressbar" 
     aria-valuenow="60" 
     aria-valuemin="0" 
     aria-valuemax="100">
  60% complete
</div>
```

## Form Accessibility

### Label Association
Every input needs a label:

```html
<!-- Visible label -->
<label for="name">Full Name</label>
<input id="name" type="text">

<!-- Hidden label -->
<label for="search" class="sr-only">Search products</label>
<input id="search" type="search" placeholder="Search...">

<!-- Label wrapping -->
<label>
  <input type="checkbox"> Remember me
</label>
```

### Error Handling
Clear, accessible error messages:

```html
<div class="form-group">
  <label for="email">Email <span aria-label="required">*</span></label>
  <input 
    id="email" 
    type="email"
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <p id="email-error" role="alert" class="error-message">
    <svg aria-hidden="true">⚠️</svg>
    Please enter a valid email address
  </p>
</div>
```

### Form Instructions
```html
<form aria-labelledby="form-title" aria-describedby="form-instructions">
  <h2 id="form-title">Create New Client</h2>
  <p id="form-instructions">
    All fields marked with * are required
  </p>
  <!-- Form fields -->
</form>
```

## Table Accessibility

### Table Structure
```html
<table>
  <caption>Product Inventory - December 2024</caption>
  <thead>
    <tr>
      <th scope="col">Product</th>
      <th scope="col">SKU</th>
      <th scope="col">Stock</th>
      <th scope="col">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">MacBook Pro</th>
      <td>MBP-001</td>
      <td>12</td>
      <td>
        <button aria-label="Edit MacBook Pro">Edit</button>
      </td>
    </tr>
  </tbody>
</table>
```

### Sortable Columns
```html
<th scope="col" aria-sort="ascending">
  <button aria-label="Sort by price, descending">
    Price <svg aria-hidden="true">↑</svg>
  </button>
</th>
```

## Modal & Dialog Accessibility

### Focus Management
```html
<div role="dialog" 
     aria-labelledby="modal-title" 
     aria-describedby="modal-description"
     aria-modal="true">
  <h2 id="modal-title">Confirm Delete</h2>
  <p id="modal-description">
    Are you sure you want to delete this product?
  </p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

### Keyboard Handling
- Tab cycles within modal
- Escape closes modal
- Focus returns to trigger element

## Images & Media

### Alt Text Guidelines
```html
<!-- Informative image -->
<img src="macbook.jpg" alt="MacBook Pro 14-inch in Space Gray">

<!-- Decorative image -->
<img src="decoration.png" alt="" role="presentation">

<!-- Complex image -->
<img src="chart.png" 
     alt="Sales chart showing 25% growth"
     aria-describedby="chart-description">
<p id="chart-description" class="sr-only">
  Detailed chart description...
</p>
```

### Icons
```html
<!-- Decorative icon -->
<svg aria-hidden="true">...</svg>

<!-- Functional icon -->
<svg role="img" aria-label="Success">...</svg>

<!-- Icon with text -->
<button>
  <svg aria-hidden="true">...</svg>
  Save Changes
</button>
```

## Motion & Animation

### Respecting User Preferences
```css
/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Safe animations */
@media (prefers-reduced-motion: no-preference) {
  .card {
    transition: transform 0.2s ease;
  }
}
```

### Pause Controls
```html
<!-- Auto-playing content -->
<div class="carousel">
  <button aria-label="Pause carousel">⏸</button>
  <!-- Slides -->
</div>
```

## Touch Targets

### Minimum Sizes
- **Touch targets**: 44×44px minimum
- **Spacing**: 8px between targets
- **Exceptions**: Inline text links

```css
/* Ensure minimum touch target */
.btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1rem;
}

/* Small buttons need larger hit areas */
.btn-icon {
  position: relative;
  padding: 0.75rem;
}

.btn-icon::before {
  content: '';
  position: absolute;
  inset: -8px;
}
```

## Testing Checklist

### Manual Testing
- [ ] Keyboard-only navigation
- [ ] Screen reader testing (NVDA/JAWS/VoiceOver)
- [ ] 200% zoom functionality
- [ ] Color contrast analyzer
- [ ] Focus indicator visibility
- [ ] Motion settings respected

### Automated Testing
```javascript
// axe-core integration
import axe from '@axe-core/react';

if (process.env.NODE_ENV !== 'production') {
  axe(React, ReactDOM, 1000);
}
```

### Browser Extensions
- axe DevTools
- WAVE
- Lighthouse
- Color Contrast Analyzer

## Common Patterns

### Loading States
```html
<button aria-busy="true" aria-disabled="true">
  <span class="spinner" aria-label="Loading"></span>
  Saving...
</button>
```

### Notifications
```html
<div role="region" aria-label="Notifications">
  <div role="alert" aria-live="assertive">
    <h3>Error</h3>
    <p>Failed to save changes</p>
  </div>
</div>
```

### Data Updates
```html
<div aria-live="polite" aria-atomic="true">
  <p>Showing <span>10</span> of <span>50</span> products</p>
</div>
```

## Developer Guidelines

### Component Templates
```html
<!-- Accessible button component -->
<button
  type="button"
  class="btn btn-primary"
  aria-label={ariaLabel}
  aria-busy={loading}
  aria-disabled={disabled}
  onClick={handleClick}
>
  {loading && <Spinner aria-label="Loading" />}
  {children}
</button>

<!-- Accessible input component -->
<div class="form-group">
  <label htmlFor={id} className={required && 'required'}>
    {label}
  </label>
  <input
    id={id}
    type={type}
    aria-invalid={error ? 'true' : 'false'}
    aria-describedby={`${id}-help ${id}-error`}
    {...props}
  />
  {help && <p id={`${id}-help`}>{help}</p>}
  {error && <p id={`${id}-error`} role="alert">{error}</p>}
</div>
```

### Testing Code
```javascript
// Test keyboard navigation
fireEvent.keyDown(element, { key: 'Tab' });
expect(nextElement).toHaveFocus();

// Test screen reader announcements
expect(screen.getByRole('alert')).toHaveTextContent('Error message');

// Test ARIA attributes
expect(button).toHaveAttribute('aria-expanded', 'true');
```

## Resources

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

### Tools
- [Pa11y](https://pa11y.org/) - Automated testing
- [Stark](https://www.getstark.co/) - Design plugin
- [Screen readers](https://www.nvaccess.org/) - NVDA (free)

### Remember
- Accessibility benefits everyone
- Test early and often
- When in doubt, use semantic HTML
- Real users > compliance scores