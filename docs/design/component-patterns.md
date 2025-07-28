# TechStore Component Design Patterns

## 🎨 Component Philosophy
Clean, functional components that prioritize usability and efficiency for daily business operations.

## Data Tables

### Structure
Tables are the backbone of inventory and order management. They must be scannable and actionable.

```html
<table class="w-full">
  <thead>
    <tr>
      <th class="text-left px-4 py-3 text-sm font-medium text-gray-700 bg-gray-50 
                 uppercase tracking-wider">Column Name</th>
    </tr>
  </thead>
  <tbody class="bg-white divide-y divide-gray-100">
    <tr class="hover:bg-gray-50">
      <td class="px-4 py-4">Content</td>
    </tr>
  </tbody>
</table>
```

### Design Principles
- **Header**: Gray-50 background, uppercase labels, 12px padding
- **Rows**: White background with hover state (gray-50)
- **Borders**: Subtle gray-100 dividers between rows
- **Typography**: Regular weight for data, mono font for codes/prices

### Special Cases
- **Multi-line cells**: Primary info in medium weight, secondary in small/muted
- **Status indicators**: Colored badges with semantic colors
- **Actions**: Icon buttons grouped at row end
- **Numeric data**: Right-aligned, monospace font

### Stock Indicators
```css
.stock-low { color: var(--error-500); }    /* < 5 items */
.stock-medium { color: var(--warning-500); } /* 5-20 items */
.stock-high { color: var(--success-500); }   /* > 20 items */
```

## Forms

### Layout Patterns
Forms use a grid system for responsive layouts:

```html
<!-- Single column for mobile, 2 columns for desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div class="form-group">...</div>
  <div class="form-group">...</div>
</div>
```

### Form Groups
Standard spacing between form elements:

```html
<div class="mb-6"> <!-- 24px margin between groups -->
  <label class="block text-sm font-medium text-gray-700 mb-2">
    Label Text
  </label>
  <input class="w-full px-3 py-2 border border-gray-300 rounded-md 
                focus:ring-primary-500 focus:border-primary-500">
  <p class="mt-1 text-sm text-gray-500">Help text</p>
</div>
```

### Input States
- **Default**: 1px gray-300 border
- **Focus**: Primary-500 border + 3px primary-100 ring
- **Error**: Error-500 border + error message below
- **Disabled**: Gray-100 background, gray-400 text

### Required Fields
```html
<label class="form-label">
  Field Name <span class="text-error-500">*</span>
</label>
```

## Buttons

### Primary Actions
```html
<button class="px-4 py-2 bg-primary-500 text-white rounded-md 
               hover:bg-primary-600 active:bg-primary-700 
               font-medium transition-colors">
  Primary Action
</button>
```

### Button Variants
- **Primary**: Blue background, white text
- **Secondary**: White background, gray border
- **Success**: Green for save/create actions
- **Danger**: Red for destructive actions

### Button Sizes
```css
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.btn { padding: 0.5rem 1rem; font-size: 1rem; }
.btn-lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }
```

### Icon Buttons
```html
<button class="p-1.5 text-gray-500 hover:text-gray-700 
               hover:bg-gray-100 rounded transition-colors">
  <svg>...</svg>
</button>
```

## Cards

### Basic Card
```html
<div class="bg-white rounded-lg shadow-sm border border-gray-200">
  <div class="px-6 py-4 border-b border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
  </div>
  <div class="p-6">
    <!-- Content -->
  </div>
</div>
```

### Card Variants
- **Default**: 24px padding, subtle shadow
- **Compact**: 16px padding for dense layouts
- **Spacious**: 32px padding for important content

## Status Badges

### Design Pattern
```html
<span class="inline-flex items-center px-3 py-1 rounded-full 
             text-xs font-medium uppercase tracking-wide">
  Status
</span>
```

### Status Colors
- **Active**: Green background (success-100), green text (success-600)
- **Inactive**: Gray background (gray-100), gray text (gray-600)
- **Warning**: Amber background (warning-100), amber text (warning-600)
- **Error**: Red background (error-100), red text (error-600)

## Navigation

### Page Headers
```html
<div class="bg-white px-8 py-6 border-b border-gray-200">
  <div class="flex justify-between items-center">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Page Title</h1>
      <p class="mt-1 text-gray-500">Page description</p>
    </div>
    <div class="flex gap-4">
      <!-- Actions -->
    </div>
  </div>
</div>
```

### Toolbars
```html
<div class="flex justify-between items-center mb-6 flex-wrap gap-4">
  <div class="flex gap-4">
    <!-- Left side: Search, filters -->
  </div>
  <div class="flex gap-4">
    <!-- Right side: Actions, stats -->
  </div>
</div>
```

## Search & Filters

### Search Input
```html
<div class="relative">
  <input type="text" 
         class="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md"
         placeholder="Search...">
  <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400">
    <!-- Search icon -->
  </svg>
</div>
```

### Filter Dropdowns
```html
<select class="px-4 py-2 border border-gray-300 rounded-md 
               text-gray-700 bg-white">
  <option>All Categories</option>
  <option>Computers</option>
  <option>Phones</option>
</select>
```

## Data Display

### Key-Value Pairs
```html
<dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
  <div>
    <dt class="text-sm font-medium text-gray-500">Label</dt>
    <dd class="mt-1 text-sm text-gray-900">Value</dd>
  </div>
</dl>
```

### Stats Cards
```html
<div class="bg-primary-50 rounded-lg p-4 border border-primary-100">
  <p class="text-sm text-gray-600">Metric Label</p>
  <p class="text-2xl font-semibold mt-1">156</p>
  <p class="text-sm text-success-500 mt-1">↑ 12% increase</p>
</div>
```

## Loading & Empty States

### Loading Spinner
```html
<div class="flex justify-center py-12">
  <div class="animate-spin rounded-full h-12 w-12 
              border-b-2 border-primary-500"></div>
</div>
```

### Empty State
```html
<div class="text-center py-12">
  <svg class="mx-auto h-12 w-12 text-gray-400">...</svg>
  <h3 class="mt-2 text-sm font-medium text-gray-900">No results found</h3>
  <p class="mt-1 text-sm text-gray-500">Try adjusting your filters</p>
</div>
```

## Responsive Patterns

### Mobile-First Tables
On mobile, consider:
- Horizontal scroll for wide tables
- Card-based layout for key data
- Collapsible rows for details
- Priority columns (hide less important on mobile)

### Form Adaptations
- Stack form fields on mobile
- Full-width inputs on small screens
- Larger touch targets (min 44x44px)
- Bottom-aligned action buttons on mobile

## AI-Powered Elements

### AI Badge
```html
<span class="inline-flex items-center gap-1 px-3 py-1 
             bg-purple-100 text-purple-500 rounded-full 
             text-xs font-medium">
  ✨ AI Powered
</span>
```

### AI Suggestions
```html
<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
  <div class="flex gap-3">
    <span class="text-purple-500">💡</span>
    <div>
      <p class="font-medium text-purple-900">AI Recommendation</p>
      <p class="text-sm text-purple-700 mt-1">Suggestion content...</p>
    </div>
  </div>
</div>
```

## Implementation Guidelines

### Component Hierarchy
1. **Container**: Card or section wrapper
2. **Header**: Title, description, actions
3. **Body**: Main content area
4. **Footer**: Secondary actions, metadata

### Consistency Rules
- Always use design system colors
- Maintain 4px spacing grid
- Use consistent border radius (rounded-md = 6px default)
- Apply hover states to all interactive elements
- Include focus states for accessibility

### Performance Tips
- Use Tailwind's purge to minimize CSS
- Lazy load heavy components
- Virtualize long lists/tables
- Debounce search inputs
- Cache filter states