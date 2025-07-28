# TechStore Icons & Visual Assets

## 🎯 Icon Philosophy
Simple, geometric icons that communicate clearly and align with our minimal, tech-savvy brand.

## Icon System

### Icon Library Choice
**Heroicons** - Modern, clean, open-source icons that match our aesthetic
- Regular weight for most uses
- Solid variants for emphasis
- Consistent 24x24px base size
- Perfect geometric construction

### Icon Categories

#### Navigation Icons
```
├── Dashboard     → HomeIcon
├── Customers     → UserGroupIcon
├── Products      → CubeIcon / ShoppingBagIcon
├── Sales         → ShoppingCartIcon
├── Repairs       → WrenchScrewdriverIcon
├── Reports       → ChartBarIcon
├── Settings      → CogIcon
└── Logout        → ArrowRightOnRectangleIcon
```

#### Action Icons
```
├── Add/Create    → PlusIcon / PlusCircleIcon
├── Edit          → PencilIcon / PencilSquareIcon
├── Delete        → TrashIcon
├── View          → EyeIcon
├── Search        → MagnifyingGlassIcon
├── Filter        → FunnelIcon
├── Sort          → ArrowsUpDownIcon
├── Download      → ArrowDownTrayIcon
├── Upload        → ArrowUpTrayIcon
└── Print         → PrinterIcon
```

#### Status Icons
```
├── Success       → CheckCircleIcon (green)
├── Error         → XCircleIcon (red)
├── Warning       → ExclamationTriangleIcon (amber)
├── Info          → InformationCircleIcon (blue)
├── Loading       → ArrowPathIcon (animated spin)
└── AI/Smart      → SparklesIcon (purple)
```

#### Form Icons
```
├── Calendar      → CalendarIcon
├── Clock         → ClockIcon
├── Location      → MapPinIcon
├── Phone         → PhoneIcon
├── Email         → EnvelopeIcon
├── Lock          → LockClosedIcon
├── User          → UserIcon
└── Document      → DocumentTextIcon
```

### Icon Sizes
```css
/* Icon size scale */
.icon-xs { width: 16px; height: 16px; }  /* Inline text */
.icon-sm { width: 20px; height: 20px; }  /* Buttons, inputs */
.icon-md { width: 24px; height: 24px; }  /* Default */
.icon-lg { width: 32px; height: 32px; }  /* Emphasis */
.icon-xl { width: 48px; height: 48px; }  /* Headers */
```

### Icon Colors
```css
/* Inherit text color by default */
.icon { color: currentColor; }

/* Specific colors for meaning */
.icon-success { color: var(--success-500); }
.icon-error { color: var(--error-500); }
.icon-warning { color: var(--warning-500); }
.icon-info { color: var(--primary-500); }
.icon-muted { color: var(--gray-400); }
```

### Implementation Examples

#### SVG Sprite Method
```html
<!-- Define sprite -->
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="icon-home" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
  </symbol>
  <!-- More icons... -->
</svg>

<!-- Use icon -->
<svg class="icon icon-md">
  <use href="#icon-home"></use>
</svg>
```

#### Inline SVG Method
```html
<svg class="icon icon-md" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
</svg>
```

#### React Component Method
```jsx
import { HomeIcon, UserGroupIcon, CubeIcon } from '@heroicons/react/24/outline';

<HomeIcon className="h-6 w-6 text-gray-500" />
```

## Logo & Brand Assets

### TechStore Logo
```
Primary Logo:
┌─────────────────────────┐
│   [T]  TechStore       │
│   Modern Tech Retail   │
└─────────────────────────┘

Icon Mark:
┌─────┐
│ [T] │  - Geometric T in primary blue
└─────┘  - Can be used alone for small spaces
```

### Logo Variations
```css
/* Logo sizing */
.logo-sm { height: 32px; }  /* Mobile header */
.logo-md { height: 40px; }  /* Desktop header */
.logo-lg { height: 64px; }  /* Login page */

/* Logo colors */
.logo-primary { color: var(--primary-500); }
.logo-white { color: white; }  /* Dark backgrounds */
.logo-black { color: var(--gray-900); }  /* Print */
```

## Illustrations & Graphics

### Empty States
Simple, friendly illustrations for empty screens:

```
No Products:
┌─────────────────┐
│    📦           │
│  No products    │
│  Add your first │
└─────────────────┘

No Results:
┌─────────────────┐
│    🔍           │
│  No results     │
│  Try different  │
│  filters        │
└─────────────────┘
```

### Loading States
```css
/* Animated loading icon */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-icon {
  animation: spin 1s linear infinite;
}

/* Skeleton screens for content */
.skeleton {
  background: linear-gradient(90deg, 
    var(--gray-200) 25%, 
    var(--gray-100) 50%, 
    var(--gray-200) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}
```

## Visual Hierarchy

### Icon Usage Guidelines

#### Do's
- ✅ Use icons to reinforce meaning
- ✅ Maintain consistent sizing
- ✅ Include text labels for clarity
- ✅ Use appropriate colors for context
- ✅ Ensure sufficient contrast

#### Don'ts
- ❌ Use icons alone for critical actions
- ❌ Mix icon styles (outline vs solid)
- ❌ Make icons too small (< 16px)
- ❌ Use decorative icons that confuse
- ❌ Forget accessibility labels

### Button Icon Patterns
```html
<!-- Icon + Text -->
<button class="btn btn-primary">
  <svg class="icon icon-sm mr-2">...</svg>
  Add Product
</button>

<!-- Icon Only (with aria-label) -->
<button class="btn-icon" aria-label="Edit product">
  <svg class="icon icon-sm">...</svg>
</button>

<!-- Text + Icon (trailing) -->
<button class="btn btn-secondary">
  Download Report
  <svg class="icon icon-sm ml-2">...</svg>
</button>
```

## Custom Icons

### Product Categories
Create simple, recognizable icons for categories:

```
Computers:    [💻] - Laptop outline
Phones:       [📱] - Phone outline
Tablets:      [⬜] - Tablet outline
Accessories:  [🎧] - Headphones outline
Components:   [🔧] - CPU/chip outline
Software:     [💿] - Disc outline
```

### Business Metrics
Dashboard and reporting icons:

```
Revenue:      [📈] - Trending up
Customers:    [👥] - People group
Orders:       [📦] - Package
Repairs:      [🔧] - Wrench
Time:         [⏱️] - Clock
Performance:  [⚡] - Lightning bolt
```

## File Formats & Optimization

### SVG Guidelines
```xml
<!-- Optimized SVG -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <!-- Simple paths, no unnecessary attributes -->
  <path d="..." />
</svg>
```

### Optimization Tips
1. Remove unnecessary attributes
2. Use `currentColor` for flexibility
3. Simplify paths when possible
4. Consistent viewBox (0 0 24 24)
5. No embedded styles

### Favicon
```html
<!-- Multiple sizes for different contexts -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

## Implementation Resources

### Heroicons Integration
```bash
# Install Heroicons
npm install @heroicons/react
# or
npm install heroicons
```

### Icon Component Template
```jsx
// Icon wrapper component
const Icon = ({ name, size = 'md', color, className, ...props }) => {
  const sizeClasses = {
    xs: 'w-4 h-4',
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };
  
  return (
    <svg 
      className={`${sizeClasses[size]} ${color} ${className}`}
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
      aria-hidden="true"
      {...props}
    >
      {/* Icon paths */}
    </svg>
  );
};
```

### CSS Utilities
```css
/* Icon utilities */
.icon {
  flex-shrink: 0;
  user-select: none;
}

.icon-inline {
  display: inline-block;
  vertical-align: middle;
  margin-top: -0.125em;
}

.icon-button {
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.icon-button:hover {
  background-color: var(--gray-100);
}
```

## Accessibility

### Icon Labels
```html
<!-- Decorative icon -->
<svg aria-hidden="true">...</svg>

<!-- Meaningful icon -->
<svg role="img" aria-label="Success">...</svg>

<!-- Icon button -->
<button aria-label="Delete item">
  <svg aria-hidden="true">...</svg>
</button>
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
  .icon {
    stroke-width: 2.5;
  }
}
```

## Asset Management

### Directory Structure
```
/assets
├── /icons
│   ├── /navigation
│   ├── /actions
│   ├── /status
│   └── sprite.svg
├── /logos
│   ├── logo.svg
│   ├── logo-icon.svg
│   └── favicon.svg
└── /illustrations
    ├── empty-states/
    └── errors/
```

### Version Control
- Use semantic versioning for icon updates
- Document icon additions/changes
- Maintain backwards compatibility
- Provide migration guides for major changes