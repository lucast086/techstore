# TechStore Interactive States & Feedback

## 🎯 Interaction Philosophy
Every interaction should feel responsive, smooth, and purposeful. Users should always know what's clickable and receive immediate feedback.

## Interactive States

### Hover States
Subtle changes that indicate interactivity without being distracting.

```css
/* Default → Hover transitions */
.transition-all { transition: all 0.2s ease; }
.transition-colors { transition: background-color 0.2s, border-color 0.2s, color 0.2s; }
.transition-shadow { transition: box-shadow 0.2s; }
.transition-transform { transition: transform 0.2s; }
```

### Focus States
Clear, accessible focus indicators for keyboard navigation.

```css
/* Primary focus style */
.focus-ring {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

/* Secondary focus style */
.focus-ring-secondary {
  outline: none;
  border-color: var(--gray-500);
  box-shadow: 0 0 0 3px var(--gray-200);
}
```

### Active/Pressed States
Immediate feedback when elements are clicked.

```css
/* Buttons */
.active-press {
  transform: translateY(1px);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}
```

### Disabled States
Clear visual indication that an element is not interactive.

```css
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

## Component-Specific States

### Buttons

#### Primary Button States
```css
/* Default */
.btn-primary {
  background: var(--primary-500);
  color: white;
  transition: all 0.2s;
}

/* Hover */
.btn-primary:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Active */
.btn-primary:active {
  background: var(--primary-700);
  transform: translateY(0);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Focus */
.btn-primary:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--primary-100);
}

/* Disabled */
.btn-primary:disabled {
  background: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
  transform: none;
}
```

#### Secondary Button States
```css
/* Hover */
.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
}

/* Active */
.btn-secondary:active {
  background: var(--gray-100);
}
```

### Form Inputs

#### Input States
```css
/* Default */
.form-input {
  border: 1px solid var(--gray-300);
  transition: all 0.2s;
}

/* Hover */
.form-input:hover:not(:focus) {
  border-color: var(--gray-400);
}

/* Focus */
.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

/* Invalid */
.form-input:invalid {
  border-color: var(--error-500);
}

.form-input:invalid:focus {
  box-shadow: 0 0 0 3px var(--error-100);
}

/* Disabled */
.form-input:disabled {
  background: var(--gray-100);
  color: var(--gray-500);
  cursor: not-allowed;
}
```

### Links

```css
/* Default */
.link {
  color: var(--primary-500);
  text-decoration: none;
  transition: all 0.2s;
}

/* Hover */
.link:hover {
  color: var(--primary-600);
  text-decoration: underline;
}

/* Active */
.link:active {
  color: var(--primary-700);
}

/* Focus */
.link:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Cards & Clickable Containers

```css
/* Hoverable Card */
.card-hover {
  transition: all 0.2s;
  cursor: pointer;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-hover:active {
  transform: translateY(0);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

### Table Rows

```css
/* Hover */
tr:hover {
  background: var(--gray-50);
}

/* Selected */
tr.selected {
  background: var(--primary-50);
  border-left: 3px solid var(--primary-500);
}
```

## Loading States

### Skeleton Screens
Show placeholder content while data loads.

```css
.skeleton {
  background: linear-gradient(90deg, 
    var(--gray-200) 25%, 
    var(--gray-100) 50%, 
    var(--gray-200) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Spinners
For actions that take time.

```css
.spinner {
  border: 2px solid var(--gray-300);
  border-top-color: var(--primary-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Progress Indicators
For multi-step processes.

```css
.progress-bar {
  background: var(--gray-200);
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  background: var(--primary-500);
  height: 100%;
  transition: width 0.3s ease;
}
```

## Feedback Messages

### Toast Notifications
Brief, non-blocking feedback.

```css
.toast {
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

### Alert States
Contextual feedback within the interface.

```css
/* Success */
.alert-success {
  background: var(--success-100);
  border: 1px solid var(--success-500);
  color: var(--success-700);
}

/* Warning */
.alert-warning {
  background: var(--warning-100);
  border: 1px solid var(--warning-500);
  color: var(--warning-700);
}

/* Error */
.alert-error {
  background: var(--error-100);
  border: 1px solid var(--error-500);
  color: var(--error-700);
}

/* Info */
.alert-info {
  background: var(--primary-100);
  border: 1px solid var(--primary-500);
  color: var(--primary-700);
}
```

## Micro-interactions

### Checkbox/Radio Animations
```css
input[type="checkbox"]:checked {
  animation: check-bounce 0.3s ease;
}

@keyframes check-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
```

### Toggle Switches
```css
.toggle-switch {
  transition: background-color 0.2s;
}

.toggle-switch.on {
  background: var(--primary-500);
}

.toggle-thumb {
  transition: transform 0.2s;
}

.toggle-switch.on .toggle-thumb {
  transform: translateX(20px);
}
```

### Dropdown Animations
```css
.dropdown-menu {
  transform-origin: top;
  animation: dropdown-open 0.2s ease-out;
}

@keyframes dropdown-open {
  from {
    opacity: 0;
    transform: scaleY(0.8);
  }
  to {
    opacity: 1;
    transform: scaleY(1);
  }
}
```

## Error Handling

### Form Validation
Real-time feedback as users type.

```css
/* Field turns red on error */
.form-input.error {
  border-color: var(--error-500);
  animation: shake 0.3s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
```

### Error Messages
Clear, helpful error communication.

```css
.error-message {
  color: var(--error-600);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## Transition Timing

### Duration Guidelines
- **Instant**: 0ms - State changes (active states)
- **Fast**: 100-200ms - Hover effects, focus states
- **Normal**: 200-300ms - Most transitions
- **Slow**: 300-500ms - Complex animations
- **Very Slow**: 500ms+ - Page transitions

### Easing Functions
```css
/* Standard easing */
.ease-out { transition-timing-function: cubic-bezier(0, 0, 0.2, 1); }
.ease-in-out { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }

/* Spring effect */
.ease-spring { transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1); }
```

## Performance Considerations

### Best Practices
1. Use `transform` and `opacity` for smooth animations
2. Avoid animating `width`, `height`, or `top/left`
3. Use `will-change` sparingly for complex animations
4. Respect `prefers-reduced-motion` setting
5. Keep animations under 300ms for responsiveness

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Implementation Examples

### Complete Button Example
```html
<button class="px-4 py-2 bg-primary-500 text-white rounded-md 
               hover:bg-primary-600 hover:-translate-y-0.5 hover:shadow-lg
               active:bg-primary-700 active:translate-y-0 active:shadow-inner
               focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
               disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed
               transition-all duration-200">
  Click Me
</button>
```

### Complete Form Field Example
```html
<div class="form-group">
  <label class="block text-sm font-medium text-gray-700 mb-2">
    Email
  </label>
  <input type="email" 
         class="w-full px-3 py-2 border border-gray-300 rounded-md
                hover:border-gray-400
                focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-100
                invalid:border-error-500 invalid:focus:ring-error-100
                disabled:bg-gray-100 disabled:text-gray-500
                transition-all duration-200"
         placeholder="you@example.com">
  <p class="mt-1 text-sm text-error-600 hidden">
    Please enter a valid email
  </p>
</div>
```